"""
Agent Charlie: Lead Technical Artist (Image Generation)
Mission: Manage the "Artist" loop (Imagen 3 API).
"""

import logging
import time
import os
import requests
import json
import base64
from datetime import datetime
from src import config

logger = logging.getLogger("AgentCharlie")

MAX_RETRIES = 3
BACKOFF_BASE = 10  # seconds
# (connect timeout, read timeout) — image generation can legitimately take minutes
REQUEST_TIMEOUT = (10, 300)
TRANSIENT_STATUS = {429, 500, 502, 503, 504}

class AgentCharlie:
    def __init__(self):
        logger.info("Agent Charlie initialized.")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found.")
        
        logger.info(f"Using Image Model: {config.GEN_MODEL_ID}")

    def _post_with_backoff(self, url, headers, payload):
        """
        POSTs with timeouts and exponential backoff on transient failures
        (429/5xx/timeouts). Honors Retry-After when the server provides it.
        Previously a single bare requests.post with no timeout could hang or
        let one transient 429 kill an entire page.
        """
        last_err = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = requests.post(url, headers=headers, json=payload,
                                         timeout=REQUEST_TIMEOUT)
                if response.status_code in TRANSIENT_STATUS and attempt < MAX_RETRIES:
                    retry_after = response.headers.get("Retry-After")
                    wait = int(retry_after) if (retry_after and retry_after.isdigit()) \
                        else BACKOFF_BASE * (2 ** attempt)
                    logger.warning(f"HTTP {response.status_code} (attempt {attempt+1}/"
                                   f"{MAX_RETRIES+1}). Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except (requests.Timeout, requests.ConnectionError) as e:
                last_err = e
                if attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning(f"Network error (attempt {attempt+1}/{MAX_RETRIES+1}): "
                                   f"{e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        raise last_err or RuntimeError("Exhausted retries")

    def _encode_image_to_base64(self, image_path):
        """Encodes an image file to base64 string."""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    def generate_image(self, prompt, theme, page_number, wireframe_path=None, reference_images=None, negative_dna=None):
        """
        Generates an image based on the prompt using REST API.

        Args:
            prompt: Text prompt for generation
            theme: Theme name for filename
            page_number: Page number for filename
            wireframe_path: Optional path to wireframe image for layout enforcement
            reference_images: Optional list of reference image paths for style guidance
            negative_dna: Optional negative prompt text (exclusion list)
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")

        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        # Clean theme for filename
        safe_theme = "".join(x for x in theme if x.isalnum() or x in " _-").strip().replace(" ", "_")

        try:
            if config.DEPLOYMENT_TIER == "PAID":
                # PAID Tier: Imagen 4.0 (:predict endpoint)
                # NOTE: Imagen 4.0 does not support image input; use enhanced text prompt instead.
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEN_MODEL_ID}:predict"
                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }

                # When a wireframe is provided, prepend a layout enforcement instruction.
                enhanced_prompt = prompt
                if wireframe_path and os.path.exists(wireframe_path):
                    logger.warning("PAID Tier: Imagen 4.0 does not support image input. Injecting layout enforcement into text prompt.")
                    enhanced_prompt = (
                        f"CRITICAL INSTRUCTION: Follow the structural layout EXACTLY as described. "
                        f"This is a wireframe-guided generation. Maintain precise zone positioning. "
                        f"{prompt}"
                    )

                # v5.22 Payload Protocol
                parameters = {
                    "sampleCount": 1,
                    "aspectRatio": "1:1"
                }
                if negative_dna:
                    parameters["negativePrompt"] = negative_dna

                payload = {
                    "instances": [
                        { "prompt": enhanced_prompt }
                    ],
                    "parameters": parameters
                }

                response = self._post_with_backoff(url, headers, payload)
                result = response.json()

                # Parse Imagen Response
                # Expected: {'predictions': [{'bytesBase64Encoded': '...', 'mimeType': 'image/png'}]}
                if 'predictions' in result and len(result['predictions']) > 0:
                    b64_data = result['predictions'][0]['bytesBase64Encoded']
                    img_data = base64.b64decode(b64_data)

                    filename = f"temp/{safe_theme}_Page{page_number}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    logger.info(f"Image saved to {filename}")
                    return filename
                else:
                    raise ValueError(f"Invalid response from Imagen API: {result}")

            else:
                # FREE Tier: Gemini Flash (:generateContent endpoint)
                # Gemini Flash supports multimodal input (text + images).
                # Handle 'models/' prefix if present in config
                model_id = config.GEN_MODEL_ID
                if model_id.startswith("models/"):
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent"
                else:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"

                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }

                # Build multimodal parts list; add wireframe and reference images if provided.
                parts = []

                # Prepend negative DNA as explicit exclusion instruction
                if negative_dna:
                    parts.append({"text": f"IMPORTANT: Do NOT include any of the following in the generated image: {negative_dna}"})

                parts.append({"text": prompt})

                if wireframe_path and os.path.exists(wireframe_path):
                    wireframe_b64 = self._encode_image_to_base64(wireframe_path)
                    if wireframe_b64:
                        parts.insert(0, {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": wireframe_b64
                            }
                        })
                        parts.insert(0, {
                            "text": "WIREFRAME REFERENCE (Follow this layout structure EXACTLY):"
                        })

                if reference_images:
                    for ref_path in reference_images:
                        if os.path.exists(ref_path):
                            ref_b64 = self._encode_image_to_base64(ref_path)
                            if ref_b64:
                                parts.insert(0, {
                                    "inline_data": {
                                        "mime_type": "image/png",
                                        "data": ref_b64
                                    }
                                })
                                parts.insert(0, {
                                    "text": "STYLE REFERENCE (Match this visual DNA):"
                                })

                payload = {
                    "contents": [{
                        "parts": parts
                    }],
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"]
                    }
                }

                response = self._post_with_backoff(url, headers, payload)
                result = response.json()

                # Parse Gemini Response
                # Look for inline data in candidates
                if 'candidates' in result and result['candidates']:
                    for candidate in result['candidates']:
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'inlineData' in part:
                                    b64_data = part['inlineData']['data']
                                    img_data = base64.b64decode(b64_data)

                                    filename = f"temp/{safe_theme}_Page{page_number}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
                                    with open(filename, "wb") as f:
                                        f.write(img_data)
                                    logger.info(f"Image saved to {filename}")
                                    return filename

                raise ValueError(f"No image found in Gemini Flash response: {result}")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"API Response: {response.text}")
            raise e
