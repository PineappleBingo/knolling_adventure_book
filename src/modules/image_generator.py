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

    def generate_image(self, prompt, theme, page_number, wireframe_path=None,
                       reference_images=None, negative_dna=None,
                       aspect_ratio=None, image_size=None):
        """
        Generates an image based on the prompt using REST API.

        Args:
            prompt: Text prompt for generation
            theme: Theme name for filename
            page_number: Page number for filename
            wireframe_path: Optional path to wireframe image for layout enforcement
            reference_images: Optional list of reference image paths (style refs,
                structure examples) sent as ordered multimodal parts
            negative_dna: Optional negative prompt text (exclusion list)
            aspect_ratio: Optional aspect ratio string (e.g. "1:1", "2:1"); default 1:1
            image_size: Optional "1K"/"2K"/"4K" override (gemini-3-pro-image only)
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")

        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        # Clean theme for filename
        safe_theme = "".join(x for x in theme if x.isalnum() or x in " _-").strip().replace(" ", "_")

        try:
            # Single :generateContent multimodal path for BOTH quality modes
            # (gemini-2.5-flash-image drafts / gemini-3-pro-image finals), so
            # reference images always reach the image model. The old Imagen
            # :predict branch dropped them 100% of the time.
            model_id = config.GEN_MODEL_ID
            if model_id.startswith("models/"):
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent"
            else:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"

            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }

            # Ordered, role-labeled multimodal parts. Image order and the index
            # references inside the prompt must stay in sync:
            #   Image 1 = style reference(s), Image N = wireframe (if present).
            parts = []
            image_roles = []

            if reference_images:
                for ref_path in reference_images:
                    if not os.path.exists(ref_path):
                        logger.warning(f"Reference image missing, skipped: {ref_path}")
                        continue
                    ref_b64 = self._encode_image_to_base64(ref_path)
                    if ref_b64:
                        idx = len(image_roles) + 1
                        role = ("STRUCTURE EXAMPLE (layering & density guide)"
                                if "_structure" in ref_path
                                else "STYLE REFERENCE (match this visual DNA: line weight, corner rounding, composition)")
                        parts.append({"text": f"Image {idx} — {role}:"})
                        parts.append({"inline_data": {"mime_type": "image/png", "data": ref_b64}})
                        image_roles.append(role)

            if wireframe_path and os.path.exists(wireframe_path):
                wireframe_b64 = self._encode_image_to_base64(wireframe_path)
                if wireframe_b64:
                    idx = len(image_roles) + 1
                    parts.append({"text": (
                        f"Image {idx} — LAYOUT WIREFRAME: follow its zone geometry EXACTLY, "
                        "but do NOT draw its colored guide lines or text labels."
                    )})
                    parts.append({"inline_data": {"mime_type": "image/png", "data": wireframe_b64}})
                    image_roles.append("WIREFRAME")

            # Operative instruction goes LAST so it is the freshest context
            instruction = prompt
            if negative_dna:
                instruction += f"\n\nSTRICTLY EXCLUDE from the image: {negative_dna}"
            if image_roles:
                instruction += (
                    f"\n\nYou were given {len(image_roles)} reference image(s) above. "
                    "Match their art style and follow the wireframe layout precisely."
                )
            parts.append({"text": instruction})

            generation_config = {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {"aspectRatio": aspect_ratio or "1:1"}
            }
            # imageSize ("1K"/"2K"/"4K") is only supported on gemini-3-pro-image
            size = image_size or config.IMAGE_SIZE
            if size and model_id.startswith("gemini-3"):
                generation_config["imageConfig"]["imageSize"] = size

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": generation_config
            }

            logger.info(f"Payload: {len(image_roles)} image part(s) "
                        f"[{', '.join(r.split(' ')[0] for r in image_roles) or 'none'}], "
                        f"aspect={generation_config['imageConfig'].get('aspectRatio')}, "
                        f"size={generation_config['imageConfig'].get('imageSize', 'default')}")

            response = self._post_with_backoff(url, headers, payload)
            result = response.json()

            # Parse Gemini response — first inline image part wins
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

            raise ValueError(f"No image found in Gemini response: {result}")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"API Response: {response.text[:2000]}")
            raise e
