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
            logger.info(f"Using Image Model: {config.IMAGE_MODEL_NAME}")
            
            if config.DEPLOYMENT_TIER == "PAID":
                # PAID Tier: Imagen 3
                try:
                    from google.generativeai import ImageGenerationModel
                    self.model = ImageGenerationModel(config.IMAGE_MODEL_NAME)
                except ImportError:
                    logger.error("ImageGenerationModel not found. Please upgrade google-generativeai.")
                    raise
            else:
                # FREE Tier: Gemini 2.0 Flash Exp
                self.model = genai.GenerativeModel(config.IMAGE_MODEL_NAME)

    def generate_image(self, prompt):
        """
        Generates an image based on the prompt.
        Uses generate_images for PAID tier and generate_content for FREE tier.
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        try:
            if config.DEPLOYMENT_TIER == "PAID":
                # PAID Tier: generate_images
                response = self.model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult"
                )
                if response.images:
                    image = response.images[0]
                    filename = f"temp/gen_{int(time.time())}.png"
                    image.save(filename)
                    logger.info(f"Image saved to {filename}")
                    return filename
                else:
                    raise ValueError("No images returned from Imagen 3 API")
            else:
                # FREE Tier: generate_content
                response = self.model.generate_content(prompt)
                if response.parts:
                    for part in response.parts:
                        if part.mime_type and part.mime_type.startswith("image/"):
                            filename = f"temp/gen_{int(time.time())}.png"
                            with open(filename, "wb") as f:
                                f.write(part.inline_data.data)
                            logger.info(f"Image saved to {filename}")
                            return filename
                raise ValueError("No image parts returned from Gemini Flash API")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise e
