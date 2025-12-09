"""
Agent Delta: Senior Pre-Press Quality Manager (QA Guard)
Mission: Build the "Guard" logic (Gemini 1.5 Pro Vision).
"""

import logging
import time
import os
import google.generativeai as genai
from PIL import Image
from src import config

logger = logging.getLogger("AgentDelta")

class AgentDelta:
    def __init__(self):
        logger.info("AgentDelta initialized.")
        # Configure API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found.")
        else:
            genai.configure(api_key=api_key)
            # Using gemini-1.5-pro for strict visual reasoning as requested
            self.model = genai.GenerativeModel('gemini-1.5-pro')

    def quality_check(self, image_path):
        """
        Checks the quality of the generated image using Gemini 1.5 Pro Vision.
        Returns True if passed, False otherwise.
        """
        logger.info(f"Performing QA check on {image_path}...")
        
        try:
            # Rate Limiting Delay (Before API call)
            logger.info(f"Sleeping for {config.QA_DELAY}s (Rate Limit)...")
            time.sleep(config.QA_DELAY)

            # Load Image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False
                
            img = Image.open(image_path)
            
            # QA Prompt
            prompt = (
                "Act as a Senior Pre-Press Quality Manager. "
                "Analyze this image for a children's coloring book. "
                "Strict Criteria:\n"
                "1. Must be black and white line art ONLY.\n"
                "2. No grayscale shading or colors.\n"
                "3. Lines must be unbroken and clear.\n"
                "4. No distorted text or gibberish.\n"
                "5. Must match the requested subject.\n"
                "Reply with 'PASS' if it meets all criteria. "
                "Reply with 'FAIL: [Reason]' if it fails."
            )
            
            response = self.model.generate_content([prompt, img])
            result = response.text.strip()
            
            logger.info(f"QA Result: {result}")
            
            if result.startswith("PASS"):
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"QA check failed: {e}")
            # Fail safe: If QA fails technically, we might want to flag it for human review
            # For now, return False to trigger retry
            return False
