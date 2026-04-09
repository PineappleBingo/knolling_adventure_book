"""
Agent Delta: Senior Pre-Press Quality Manager (QA Guard)
Mission: Build the "Guard" logic (Gemini 1.5 Pro Vision).
"""

import logging
import time
import os
from google import genai
from PIL import Image
from src import config

MAX_RETRIES = 3
BACKOFF_BASE = 10  # seconds

logger = logging.getLogger("AgentDelta")

class AgentDelta:
    def __init__(self):
        logger.info("AgentDelta initialized.")
        # Configure API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found.")
            self.genai_client = None
        else:
            # Using Gemini 2.5 Pro for strict visual reasoning
            self.genai_client = genai.Client(api_key=api_key)
        self.model_name = config.QA_MODEL_NAME

    def quality_check(self, image_path, reference_image_path=None):
        """
        Checks the quality of the generated image using Gemini 2.5 Pro Vision.
        Optionally compares against a reference image for layout/style accuracy.
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

            # Build QA prompt — enhanced when reference image is available
            contents = []

            if reference_image_path and os.path.exists(reference_image_path):
                ref_img = Image.open(reference_image_path)
                contents.append("REFERENCE IMAGE (this is the target style and layout):")
                contents.append(ref_img)
                contents.append("GENERATED IMAGE (evaluate this against the reference):")
                contents.append(img)
                prompt = (
                    "Act as a Senior Pre-Press Quality Manager. "
                    "Compare the GENERATED IMAGE against the REFERENCE IMAGE. "
                    "Strict Criteria:\n"
                    "1. Must be black and white line art ONLY (no color, no grayscale shading).\n"
                    "2. Lines must be unbroken, thick, and clear.\n"
                    "3. No distorted text or gibberish text.\n"
                    "4. Overall layout and composition must be similar to the reference.\n"
                    "5. Art style must match: chunky, rounded, toy-like proportions.\n"
                    "Reply with 'PASS' if it meets all criteria. "
                    "Reply with 'FAIL: [Reason]' if it fails."
                )
                contents.append(prompt)
            else:
                contents.append(img)
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
                contents.append(prompt)

            # Call with exponential backoff on 503
            response = None
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.genai_client.models.generate_content(
                        model=self.model_name,
                        contents=contents
                    )
                    break
                except Exception as api_err:
                    error_str = str(api_err)
                    if ("503" in error_str or "UNAVAILABLE" in error_str) and attempt < MAX_RETRIES - 1:
                        wait = BACKOFF_BASE * (2 ** attempt)
                        logger.warning(f"503 UNAVAILABLE (attempt {attempt+1}/{MAX_RETRIES}). Retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
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
