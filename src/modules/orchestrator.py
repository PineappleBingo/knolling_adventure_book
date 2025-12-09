"""
Agent Omega: Senior Project Manager (Orchestrator)
Mission: Coordinate the entire lifecycle of a book generation.
"""

import logging
import uuid
import time
from src import config
from src.modules.tracking import AgentGolf
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
        
        # 1. Initialize Tracking
        self.golf.start_job(run_id, theme)
        
        try:
            if progress_callback:
                await progress_callback(f"⚙️ Phase: Agent Bravo\n📊 Progress: 0/4\n📝 Status: Generating prompts...")

            # 2. Generate Prompts
            logger.info("Agent Bravo: Generating prompts...")
            prompts = []
            
            # Page 0: Cover
            prompts.append({
                "type": "cover",
                "prompt": self.bravo.generate_cover(theme)
            })

            # Page 1: Mission Briefing
            prompts.append({
                "type": "mission",
                "prompt": self.bravo.generate_mission_briefing(theme)
            })
            
            # Demo: Just 1 Spread (Page 4 & 5)
            items = ["Helmet", "Hose", "Ladder", "Axe", "Boots"] # Placeholder items
            prompts.append({
                "type": "knolling",
                "prompt": self.bravo.generate_knolling_prompt(theme, items)
            })
            prompts.append({
                "type": "action",
                "prompt": self.bravo.generate_action_prompt(theme, "fighting fire", items, "burning building")
            })
            
            generated_images = []
            preview_images = {} # Store paths by type for preview
            
            # 3. Generation Loop
            total_steps = len(prompts)
            for i, p in enumerate(prompts):
                if progress_callback:
                    await progress_callback(f"⚙️ Phase: Agent Charlie & Delta\n📊 Progress: {i}/{total_steps}\n📝 Status: Generating {p['type']} image...")

                logger.info(f"Processing Image {i+1}/{len(prompts)} ({p['type']})...")
                
                # Generate
                image_path = self.charlie.generate_image(p['prompt'])
                
                # QA Check (Retry Loop)
                passed = False
                retries = 0
                while not passed and retries < 3:
                    passed = self.delta.quality_check(image_path)
                    if not passed:
                        logger.warning(f"Image {i+1} failed QA. Retrying ({retries+1}/3)...")
                        retries += 1
                        # Retry generation
                        image_path = self.charlie.generate_image(p['prompt'])
                
                if passed:
                    generated_images.append(image_path)
                    preview_images[p['type']] = image_path
                    self.golf.update_progress(run_id, f"Image {i+1} Generated", len(generated_images))
                else:
                    logger.error(f"Image {i+1} failed QA after retries. Skipping.")
            
            # 4. Assembly
            if generated_images:
                if progress_callback:
                    await progress_callback(f"⚙️ Phase: Agent Echo\n📊 Progress: {len(generated_images)}/{total_steps}\n📝 Status: Assembling PDF...")

                logger.info("Agent Echo: Assembling PDF...")
                pdf_path = self.echo.assemble_pdf(generated_images)
                
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
