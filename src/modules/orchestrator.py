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
        
    def start_job(self, theme):
        """
        Starts the book generation process for a given theme.
        """
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting job {run_id} for theme: {theme}")
        
        # 1. Initialize Tracking
        self.golf.start_job(run_id, theme)
        
        try:
            # 2. Generate Prompts
            logger.info("Agent Bravo: Generating prompts...")
            # For this MVP, we'll generate a small set of prompts
            # In production, this would generate all 50 pages
            prompts = []
            
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
            
            # 3. Generation Loop
            for i, p in enumerate(prompts):
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
                        # Retry generation (in real logic, maybe tweak prompt?)
                        image_path = self.charlie.generate_image(p['prompt'])
                
                if passed:
                    generated_images.append(image_path)
                    self.golf.update_progress(run_id, f"Image {i+1} Generated", len(generated_images))
                else:
                    logger.error(f"Image {i+1} failed QA after retries. Skipping.")
            
            # 4. Assembly
            if generated_images:
                logger.info("Agent Echo: Assembling PDF...")
                pdf_path = self.echo.assemble_pdf(generated_images)
                
                # 5. Finish
                # In real app, upload to Drive and get link
                drive_link = f"file://{pdf_path}" 
                self.golf.finish_job(run_id, drive_link)
                logger.info(f"Job {run_id} completed successfully.")
            else:
                logger.error("No images generated. Job failed.")
                self.golf.update_progress(run_id, "FAILED: No images")
                
        except Exception as e:
            logger.error(f"Job {run_id} failed: {e}")
            self.golf.update_progress(run_id, f"FAILED: {e}")
            raise e
