"""
Configuration settings for Knolling Adventures.
Handles dynamic rate limiting based on deployment tier.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Deployment Tier: 'FREE' or 'PAID'
DEPLOYMENT_TIER = os.getenv("DEPLOYMENT_TIER", "FREE").upper()

# Image Model Configuration
if DEPLOYMENT_TIER == "PAID":
    IMAGE_MODEL_NAME = "imagen-3.0-generate-002"
else:
    # FREE Tier: Use Gemini 2.0 Flash Exp (Image Generation)
    IMAGE_MODEL_NAME = "models/gemini-2.0-flash-exp-image-generation"

# Mission Control Sheet URL
MISSION_CONTROL_SHEET_URL = "https://docs.google.com/spreadsheets/d/1uNFeH89l96fbuB6olSHAWip-w_et-iqLDJLfBfuMvCo/edit?usp=sharing"

# Rate Limiting Delays (in seconds)
if DEPLOYMENT_TIER == "PAID":
    QA_DELAY = 0.5
    IMG_GEN_DELAY = 0.5
    PROMPT_GEN_DELAY = 0.5
else:
    # FREE Tier Limits
    QA_DELAY = 35        # Gemini 1.5 Pro: 2 RPM limit -> 30s+ buffer
    IMG_GEN_DELAY = 20   # Safe buffer for image generation
    PROMPT_GEN_DELAY = 5 # Buffer for prompt generation

def get_status_message():
    if DEPLOYMENT_TIER == "PAID":
        return "🚀 Running in PAID mode - Max Speed"
    else:
        return "🐢 Running in FREE mode - Safe Limits Active"
