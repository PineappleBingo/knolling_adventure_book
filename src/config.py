"""
Configuration settings for Knolling Adventures.
Handles dynamic rate limiting based on deployment tier.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Deployment Tier: 'FREE' or 'PAID'
DEPLOYMENT_TIER = os.getenv("DEPLOYMENT_TIER", "FREE").upper()

# Quality Mode: 'DRAFT' (cheap iteration) or 'FINAL' (shipping quality)
# DRAFT  -> gemini-2.5-flash-image  (~1K output, up to 5 reference images)
# FINAL  -> gemini-3-pro-image      (up to 4K output, up to 14 reference images)
QUALITY_MODE = os.getenv("QUALITY_MODE", "DRAFT").upper()

# When false (default), missing reference assets abort the run instead of
# silently degrading to text-only generation (the historic "style drift" cause).
ALLOW_DEGRADED_ASSETS = os.getenv("ALLOW_DEGRADED_ASSETS", "false").lower() == "true"

# Asset key roster: every page key needs 3 reference PNGs in assets/
ASSET_KEYS = ["cover", "page1", "page2", "page3", "page4", "page5", "page50"]
ASSET_ROLES = ["01", "layout_wireframe_kdp", "structure_example"]

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

# Target Pages Configuration (Specific Pages/Ranges)
# Format: "1,3,5-7" -> [1, 3, 5, 6, 7]
TARGET_PAGES_LIST = []
target_pages_env = os.getenv("TARGET_PAGES")
if target_pages_env:
    try:
        for part in target_pages_env.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                TARGET_PAGES_LIST.extend(range(start, end + 1))
            else:
                TARGET_PAGES_LIST.append(int(part))
        # Remove duplicates and sort
        TARGET_PAGES_LIST = sorted(list(set(TARGET_PAGES_LIST)))
    except ValueError:
        print(f"Warning: Invalid TARGET_PAGES format: {target_pages_env}")
        pass

# Typography Assets (Google Fonts)
FONT_TITLE_MAIN = "TitanOne-Regular.ttf"
FONT_SUBTITLE = "Fredoka-Regular.ttf" # Note: Bible says FredokaOne, but file is Fredoka
FONT_BODY_TEXT = "Quicksand-Bold.ttf"
FONT_HANDWRITING = "PatrickHand-Regular.ttf"
FONT_LEGAL = "Sniglet-Regular.ttf"

PATH_FONTS = "assets/fonts/"

# Image Model Configuration (Agent Alpha Logic)
if DEPLOYMENT_TIER == "PAID":
    GEN_MODEL_ID = "imagen-4.0-generate-001"
else:
    # FREE Tier: Use Gemini 2.5 Flash Image (replaces deprecated gemini-2.0-flash-exp)
    GEN_MODEL_ID = "gemini-2.5-flash-image"

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
