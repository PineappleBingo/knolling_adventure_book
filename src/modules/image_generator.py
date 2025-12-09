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
            # Initialize the model
            # Note: We try to use ImageGenerationModel as requested.
            # If it doesn't exist in the library, this will raise an AttributeError, causing a crash as desired.
            try:
                self.model = genai.ImageGenerationModel("imagen-3.0-generate-001")
            except AttributeError:
                # If ImageGenerationModel is missing, we try to import it directly or fail
                # In newer versions, it might be under a different module, but we stick to the user's instruction.
                logger.error("genai.ImageGenerationModel not found. Please upgrade google-generativeai.")
                raise

    def generate_image(self, prompt):
        """
        Generates an image based on the prompt using Imagen 3.
        Returns the path to the saved image.
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        try:
            # Try generating with the main model
            response = self.model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_only_high",
                person_generation="allow_adult"
            )
        except Exception as e:
            logger.warning(f"Imagen 3.0 failed: {e}. Trying fallback to Imagen 3.0 Fast...")
            try:
                # Fallback to Fast model
                fast_model = genai.ImageGenerationModel("imagen-3.0-fast-generate-001")
                response = fast_model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult"
                )
            except Exception as e2:
                logger.error(f"Imagen 3.0 Fast also failed: {e2}")
                raise e2 # Crash as requested

        if response.images:
            image = response.images[0]
            
            # Save to temp
            filename = f"temp/gen_{int(time.time())}.png"
            image.save(filename)
            logger.info(f"Image saved to {filename}")
            return filename
        else:
            logger.error("No images returned from API.")
            raise ValueError("No images returned from API")
