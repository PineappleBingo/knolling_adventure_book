"""
Agent Delta: Senior Pre-Press Quality Manager (QA Guard)
Mission: Build the "Guard" logic (Gemini 1.5 Pro Vision).
"""

import json
import logging
import re
import time
import os
from google import genai
from google.genai import types as genai_types
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

    VERDICT_INSTRUCTIONS = (
        'Respond with ONLY a JSON object: {"verdict": "PASS" or "FAIL", '
        '"reasons": ["specific issue 1", "specific issue 2"]}. '
        'reasons must be an empty list on PASS, and concrete, actionable '
        'descriptions of each failed criterion on FAIL.'
    )

    def _parse_verdict(self, raw_text):
        """Parses the model's verdict. Returns (passed: bool, reasons: list[str])."""
        text = raw_text.strip()
        try:
            # Strip accidental markdown fences before parsing
            fenced = re.search(r"\{.*\}", text, re.DOTALL)
            data = json.loads(fenced.group(0) if fenced else text)
            passed = str(data.get("verdict", "")).upper() == "PASS"
            reasons = [str(r) for r in data.get("reasons", [])]
            return passed, reasons
        except (json.JSONDecodeError, AttributeError):
            # Fallback for non-JSON replies: tolerate "**PASS**", "PASS.", preambles
            upper = text.upper()
            if "PASS" in upper[:40] and "FAIL" not in upper[:40]:
                return True, []
            return False, [text[:500]]

    def quality_check(self, image_path, reference_image_path=None):
        """
        Checks the quality of the generated image using Gemini 2.5 Pro Vision.
        Optionally compares against a reference image for layout/style accuracy.
        Returns (passed: bool, reasons: list[str]) — reasons feed the retry prompt.
        """
        logger.info(f"Performing QA check on {image_path}...")

        try:
            # Rate Limiting Delay (Before API call)
            logger.info(f"Sleeping for {config.QA_DELAY}s (Rate Limit)...")
            time.sleep(config.QA_DELAY)

            # Load Image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False, [f"Image file not found: {image_path}"]

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
                    f"{self.VERDICT_INSTRUCTIONS}"
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
                    f"{self.VERDICT_INSTRUCTIONS}"
                )
                contents.append(prompt)

            # Call with exponential backoff on transient errors (503 + 429)
            response = None
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.genai_client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=genai_types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                    break
                except Exception as api_err:
                    error_str = str(api_err)
                    transient = any(t in error_str for t in
                                    ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))
                    if transient and attempt < MAX_RETRIES - 1:
                        wait = BACKOFF_BASE * (2 ** attempt)
                        logger.warning(f"Transient API error (attempt {attempt+1}/{MAX_RETRIES}): "
                                       f"{error_str[:120]}. Retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
            result = response.text.strip()

            passed, reasons = self._parse_verdict(result)
            logger.info(f"QA Result: {'PASS' if passed else 'FAIL'} {reasons if reasons else ''}")
            return passed, reasons

        except Exception as e:
            logger.error(f"QA check failed: {e}")
            # Fail safe: technical QA failure triggers a retry rather than a false PASS
            return False, [f"QA technical error: {e}"]
