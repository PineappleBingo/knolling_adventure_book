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
from src import config

logger = logging.getLogger("AgentCharlie")

class AgentCharlie:
    def __init__(self):
        logger.info("Agent Charlie initialized.")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found.")
        
        logger.info(f"Using Image Model: {config.GEN_MODEL_ID}")

    def generate_image(self, prompt, theme, page_number):
        """
        Generates an image based on the prompt using REST API.
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
                # Model ID is now config.GEN_MODEL_ID (e.g., imagen-4.0-generate-001)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEN_MODEL_ID}:predict"
                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }
                # v5.21 Payload Protocol
                payload = {
                    "instances": [
                        { "prompt": prompt }
                    ],
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": "1:1"
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Parse Imagen Response
                # Expected: {'predictions': [{'bytesBase64Encoded': '...', 'mimeType': 'image/png'}]}
                if 'predictions' in result and len(result['predictions']) > 0:
                    b64_data = result['predictions'][0]['bytesBase64Encoded']
                    img_data = base64.b64decode(b64_data)
                    
                    filename = f"temp/{safe_theme}_Page{page_number}_{int(time.time())}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    logger.info(f"Image saved to {filename}")
                    return filename
                else:
                    raise ValueError(f"Invalid response from Imagen API: {result}")

            else:
                # FREE Tier: Gemini 2.0 Flash Exp (:generateContent endpoint)
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
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
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
                                    
                                    filename = f"temp/{safe_theme}_Page{page_number}_{int(time.time())}.png"
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
