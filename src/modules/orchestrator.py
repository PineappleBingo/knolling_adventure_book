"""
Agent Omega: Senior Project Manager (Orchestrator)
Mission: Coordinate the entire lifecycle of a book generation.
"""

import logging
import uuid
import time
from src import config
from src.modules.tracking import AgentGolf
from src.modules.system_architect import AgentAlpha
from src.modules.prompt_generator import AgentBravo
from src.modules.image_generator import AgentCharlie
from src.modules.qa_agent import AgentDelta
from src.modules.pdf_assembler import AgentEcho

logger = logging.getLogger("AgentOmega")

class AgentOmega:
    def __init__(self):
        logger.info("Agent Omega initialized.")
        logger.info(config.get_status_message())

        # Initialize Sub-Agents
        self.alpha = AgentAlpha()
        self.golf = AgentGolf()
        self.bravo = AgentBravo()
        self.charlie = AgentCharlie()
        self.delta = AgentDelta()
        self.echo = AgentEcho()

    async def start_job(self, theme, progress_callback=None):
        """
        Starts the book generation process for a given theme.
        """
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting job {run_id} for theme: {theme}")

        # 0. Preflight — abort loudly before spending any API budget
        try:
            self.alpha.assert_ready_for_generation()
        except EnvironmentError as env_err:
            if progress_callback:
                await progress_callback(f"🛑 Preflight failed:\n{env_err}")
            raise

        # 1. Initialize Tracking
        self.golf.start_job(run_id, theme)
        
        try:
            if progress_callback:
                await progress_callback(f"⚙️ Phase: Agent Bravo\n📊 Progress: 0/4\n📝 Status: Generating prompts...")

            # 2. Generate Prompts
            logger.info("Agent Bravo: Generating prompts...")
            
            # Get Interior Prompts & Context
            prompt_data = self.bravo.generate_prompts(theme)
            prompts = prompt_data['prompts']
            
            # Generate Cover using the SAME context (4-tuple)
            cover_prompt, cover_wf, cover_refs, cover_neg = self.bravo.generate_cover(
                theme,
                prompt_data['main_character'],
                prompt_data['gear_objects']
            )

            # Insert Cover at the beginning
            prompts.insert(0, {
                "type": "cover",
                "page_number": 1,
                "prompt": cover_prompt,
                "wireframe_path": cover_wf,
                "reference_images": cover_refs,
                "negative_dna": cover_neg
            })
            
            generated_pages = []  # [{"path","page_type","page_number"}] — assembler's single source of truth
            preview_images = {} # Store paths by type for preview
            
            # Limit prompts based on TARGET_PAGES or PAGE_COUNT
            if config.TARGET_PAGES_LIST:
                logger.info(f"Filtering generation to pages: {config.TARGET_PAGES_LIST}")
                # Filter prompts where page_number is in TARGET_PAGES_LIST
                filtered_prompts = []
                for p in prompts:
                    # Default to 0 if no page_number (shouldn't happen with new logic)
                    pg = p.get('page_number', 0)
                    if pg in config.TARGET_PAGES_LIST:
                        filtered_prompts.append(p)
                prompts = filtered_prompts
            elif len(prompts) > config.PAGE_COUNT:
                logger.info(f"Limiting generation to {config.PAGE_COUNT} pages (PAGE_COUNT).")
                prompts = prompts[:config.PAGE_COUNT]

            # 3. Generation Loop
            total_steps = len(prompts)
            for i, p in enumerate(prompts):
                if progress_callback:
                    await progress_callback(f"⚙️ Phase: Agent Charlie & Delta\n📊 Progress: {i}/{total_steps}\n📝 Status: Generating {p['type']} image...")

                logger.info(f"Processing Image {i+1}/{len(prompts)} ({p['type']})...")
                
                # Generate
                # Use actual page number for naming
                pg_num = p.get('page_number', i+1)
                page_num_str = str(pg_num).zfill(2)
                if p['type'] == 'cover':
                    page_num_str = "Cover"
                
                # Resolve wireframe + reference image paths + negative DNA for multimodal input
                wireframe_path = p.get('wireframe_path')
                reference_images = p.get('reference_images')
                negative_dna = p.get('negative_dna')

                image_path = self.charlie.generate_image(
                    p['prompt'], theme, page_num_str,
                    wireframe_path=wireframe_path,
                    reference_images=reference_images,
                    negative_dna=negative_dna
                )

                # QA Check (Retry Loop) — pass first reference image for comparison.
                # On FAIL the specific reasons are fed back into the retry prompt:
                # resending a byte-identical request only re-rolls sampling noise.
                qa_ref = reference_images[0] if reference_images else None
                passed = False
                retries = 0
                while not passed and retries < 3:
                    passed, qa_reasons = self.delta.quality_check(image_path, reference_image_path=qa_ref)
                    if not passed:
                        logger.warning(f"Image {i+1} failed QA ({qa_reasons}). Retrying ({retries+1}/3)...")
                        retries += 1
                        retry_prompt = p['prompt']
                        if qa_reasons:
                            retry_prompt += (
                                "\n\nPREVIOUS ATTEMPT REJECTED by quality control for these "
                                "specific issues — correct every one of them:\n- "
                                + "\n- ".join(qa_reasons)
                            )
                        image_path = self.charlie.generate_image(
                            retry_prompt, theme, page_num_str,
                            wireframe_path=wireframe_path,
                            reference_images=reference_images,
                            negative_dna=negative_dna
                        )

                if passed:
                    generated_pages.append({
                        "path": image_path,
                        "page_type": p['type'],
                        "page_number": p.get('page_number', i + 1),
                    })
                    preview_images[p['type']] = image_path
                    self.golf.update_progress(run_id, f"Image {i+1} Generated", len(generated_pages))
                else:
                    logger.error(f"Image {i+1} failed QA after retries. Skipping.")
            
            # 4. Assembly
            if generated_pages:
                if progress_callback:
                    await progress_callback(f"⚙️ Phase: Agent Echo\n📊 Progress: {len(generated_pages)}/{total_steps}\n📝 Status: Assembling PDF...")

                logger.info("Agent Echo: Assembling PDF...")
                pdf_path = self.echo.assemble_pdf(generated_pages)
                
                # 5. Finish
                # In real app, upload to Drive and get link
                drive_link = f"file://{pdf_path}" 
                self.golf.finish_job(run_id, drive_link)
                logger.info(f"Job {run_id} completed successfully.")
                
                return {
                    "status": "SUCCESS",
                    "run_id": run_id,
                    "pdf_path": pdf_path,
                    "drive_link": drive_link,
                    "previews": preview_images
                }
            else:
                error_msg = "No images generated. Job failed."
                logger.error(error_msg)
                self.golf.log_error(run_id, error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Job {run_id} failed: {e}")
            self.golf.log_error(run_id, str(e))
            raise e
