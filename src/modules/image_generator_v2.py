"""
Agent Charlie v2.0: Lead Technical Artist (Image Generation) - FIXED
Mission: Manage the "Artist" loop with REFERENCE IMAGE SUPPORT.
"""

import logging
import time
import os
import requests
import json
import base64
from PIL import Image
from src import config

logger = logging.getLogger("AgentCharlie")

class AgentCharlie:
    def __init__(self):
        logger.info("Agent Charlie v2.0 initialized (with Reference Image Support).")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found.")
        
        logger.info(f"Using Image Model: {config.GEN_MODEL_ID}")

    def _encode_image_to_base64(self, image_path):
        """Encodes an image file to base64 string."""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    def generate_image(self, prompt, theme, page_number, wireframe_path=None, reference_images=None):
        """
        Generates an image based on the prompt using REST API.
        
        Args:
            prompt: Text prompt for generation
            theme: Theme name for filename
            page_number: Page number for filename
            wireframe_path: Optional path to wireframe image for layout enforcement
            reference_images: Optional list of reference image paths for style guidance
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        # FORENSIC LOGGING
        logger.info("=" * 80)
        logger.info("🔍 AGENT CHARLIE PAYLOAD DEBUG")
        logger.info(f"  • Wireframe provided: {wireframe_path is not None}")
        logger.info(f"  • Reference images provided: {reference_images is not None}")
        if wireframe_path:
            logger.info(f"    - Wireframe path: {wireframe_path}")
            logger.info(f"    - Wireframe exists: {os.path.exists(wireframe_path) if wireframe_path else False}")
        if reference_images:
            logger.info(f"    - Reference count: {len(reference_images)}")
            for i, ref in enumerate(reference_images):
                logger.info(f"    - Ref {i+1}: {ref} (exists: {os.path.exists(ref)})")
        logger.info("=" * 80)
        
        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        # Clean theme for filename
        safe_theme = "".join(x for x in theme if x.isalnum() or x in " _-").strip().replace(" ", "_")
        
        try:
            if config.DEPLOYMENT_TIER == "PAID":
                # PAID Tier: Imagen 4.0 (:predict endpoint)
                # NOTE: Imagen 4.0 currently does NOT support image input for conditioning
                # We must rely on enhanced text prompts
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEN_MODEL_ID}:predict"
                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }
                
                # TASK 2 FIX: Enhance prompt with wireframe description if provided
                enhanced_prompt = prompt
                if wireframe_path and os.path.exists(wireframe_path):
                    logger.warning("⚠️  PAID Tier: Imagen 4.0 does not support image input.")
                    logger.warning("    Injecting STRICT LAYOUT ENFORCEMENT into text prompt.")
                    enhanced_prompt = (
                        f"CRITICAL INSTRUCTION: Follow the structural layout EXACTLY as described. "
                        f"This is a wireframe-guided generation. Maintain precise zone positioning. "
                        f"{prompt}"
                    )
                
                payload = {
                    "instances": [
                        { "prompt": enhanced_prompt }
                    ],
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": "1:1"
                    }
                }
                
                logger.info(f"📤 PAID Tier Payload (Text-Only): {json.dumps(payload, indent=2)[:200]}...")
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Parse Imagen Response
                if 'predictions' in result and len(result['predictions']) > 0:
                    b64_data = result['predictions'][0]['bytesBase64Encoded']
                    img_data = base64.b64decode(b64_data)
                    
                    filename = f"temp/{safe_theme}_Page{page_number}_{int(time.time())}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    logger.info(f"✅ Image saved to {filename}")
                    return filename
                else:
                    raise ValueError(f"Invalid response from Imagen API: {result}")

            else:
                # FREE Tier: Gemini 2.0 Flash Exp (:generateContent endpoint)
                # Gemini Flash DOES support multimodal input (text + images)
                
                model_id = config.GEN_MODEL_ID
                if model_id.startswith("models/"):
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent"
                else:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"

                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }
                
                # TASK 2 FIX: Build multimodal payload with images
                parts = [{"text": prompt}]
                
                # Add wireframe as reference image
                if wireframe_path and os.path.exists(wireframe_path):
                    logger.info("✅ FREE Tier: Adding wireframe as inline image data")
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
                
                # Add style reference images
                if reference_images:
                    for ref_path in reference_images:
                        if os.path.exists(ref_path):
                            logger.info(f"✅ FREE Tier: Adding style reference: {ref_path}")
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
                    }]
                }
                
                logger.info(f"📤 FREE Tier Payload: {len(parts)} parts (text + {len([p for p in parts if 'inline_data' in p])} images)")
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Parse Gemini Response
                if 'candidates' in result and result['candidates']:
                    for candidate in result['candidates']:
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'inlineData' in part:
                                    b64_data = part['inlineData']['data']
                                    img_data = base64.b64decode(b64_data)
                                    
                                    filename = f"temp/{safe_theme}_Page{page_number}_{int(time.time())}.png"
                                    with open(filename, "wb") as f:
                                        f.write(img_data)
                                    logger.info(f"✅ Image saved to {filename}")
                                    return filename
                            
                raise ValueError(f"No image found in Gemini Flash response: {result}")

        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"API Response: {response.text}")
            raise e
