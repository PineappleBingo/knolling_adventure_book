"""
Agent Charlie: Lead Technical Artist (Image Generation)
Mission: Manage the "Artist" loop (Imagen 3 API).
"""

import logging
import time
import os
import google.generativeai as genai
from PIL import Image
from src import config

logger = logging.getLogger("AgentCharlie")

class AgentCharlie:
    def __init__(self):
        logger.info("Agent Charlie initialized.")
        # Configure API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found.")
        else:
            genai.configure(api_key=api_key)
            # Assuming 'imagen-3.0-generate-001' or similar model name
            # You might need to adjust the model name based on availability
            self.model = genai.ImageGenerationModel("imagen-3.0-generate-001")

    def generate_image(self, prompt):
        """
        Generates an image based on the prompt using Imagen 3.
        Returns the path to the saved image.
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        try:
            # Rate Limiting Delay
            logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
            time.sleep(config.IMG_GEN_DELAY)

            # Generate
            # Note: The exact API call might vary slightly depending on the lib version
            # This is a standard pattern for the new genai lib
            response = self.model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1", # Square as per Bible
                safety_filter_level="block_only_high",
                person_generation="allow_adult"
            )
            
            if response.images:
                image = response.images[0]
                
                # Save to temp
                filename = f"temp/gen_{int(time.time())}.png"
                image.save(filename)
                logger.info(f"Image saved to {filename}")
                return filename
            else:
                logger.error("No images returned from API.")
                return None

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # For testing without API access, we might want to return a placeholder
            # return "assets/logo.png" 
            return None
