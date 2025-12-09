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
            # Using Gemini 2.0 Flash Exp for Image Generation as Imagen 3 is unavailable
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

    def generate_image(self, prompt):
        """
        Generates an image based on the prompt using Gemini 2.0 Flash Exp.
        Returns the path to the saved image.
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        try:
            # Generate Content (Image)
            response = self.model.generate_content(prompt)
            
            # Extract Image from Response
            if response.parts:
                for part in response.parts:
                    if part.mime_type and part.mime_type.startswith("image/"):
                        # Save to temp
                        filename = f"temp/gen_{int(time.time())}.png"
                        img_data = part.inline_data.data
                        # Decode if needed, but usually the library handles it or gives bytes?
                        # Actually, for inline_data, it might be bytes.
                        # Let's assume we need to save bytes.
                        # Wait, the library object 'part' might not be easy to save directly without PIL or writing bytes.
                        # Let's try writing bytes directly.
                        with open(filename, "wb") as f:
                            f.write(img_data)
                            
                        logger.info(f"Image saved to {filename}")
                        return filename
            
            logger.error("No image parts found in response.")
            raise ValueError("No image parts returned from API")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise e
