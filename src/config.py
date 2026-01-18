"""
Configuration settings for Knolling Adventures.
Handles dynamic rate limiting based on deployment tier.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Deployment Tier: 'FREE' or 'PAID'
DEPLOYMENT_TIER = os.getenv("DEPLOYMENT_TIER", "FREE").upper()

# 0.0 SYSTEM CONFIGURATION (Physical Specs)
TRIM_WIDTH = 8.5
TRIM_HEIGHT = 8.5
BLEED_SIZE = 0.125
SAFE_MARGIN = 0.375
PAGE_COUNT = 50

# Page Count Configuration (Override from Env)
try:
    if os.getenv("PAGE_COUNT"):
        PAGE_COUNT = int(os.getenv("PAGE_COUNT"))
except ValueError:
    pass

# Image Model Configuration (Agent Alpha Logic)
if DEPLOYMENT_TIER == "PAID":
    GEN_MODEL_ID = "imagen-4.0-generate-001"
else:
    # FREE Tier: Use Gemini 2.0 Flash Exp (Image Generation)
    GEN_MODEL_ID = "models/gemini-2.0-flash-exp-image-generation"

# QA Model Configuration (Same for both tiers)
QA_MODEL_NAME = "models/gemini-2.5-pro"

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
        return f"🚀 Running in PAID mode ({GEN_MODEL_ID}) - Max Speed"
    else:
        return f"🐢 Running in FREE mode ({GEN_MODEL_ID}) - Safe Limits Active"
