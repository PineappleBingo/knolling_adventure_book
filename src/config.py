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
# QUALITY_MODE selects the model; both use the same :generateContent multimodal
# path so reference images ALWAYS reach the image model. The old Imagen
# :predict path was removed: imagen-4.0-generate-001 cannot accept image input,
# so the "premium" tier silently dropped every reference (root cause of drift).
if QUALITY_MODE == "FINAL":
    GEN_MODEL_ID = "gemini-3-pro-image"   # Nano Banana Pro: <=14 refs, up to 4K
    # imageSize is only supported on gemini-3-pro-image: "1K" | "2K" | "4K"
    IMAGE_SIZE = os.getenv("IMAGE_SIZE", "2K").upper()
    COVER_IMAGE_SIZE = os.getenv("COVER_IMAGE_SIZE", "4K").upper()
else:
    GEN_MODEL_ID = "gemini-2.5-flash-image"  # draft iteration: <=5 refs, ~1K
    IMAGE_SIZE = None
    COVER_IMAGE_SIZE = None

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

# Cover geometry (KDP): spread width is a FUNCTION of page count.
# Spine width for B&W paper: page_count * 0.002252". The historic hardcoded
# 17.365" is only correct for exactly 50 pages.
SPINE_INCHES_PER_PAGE = 0.002252

def get_spine_width(page_count=None):
    return (page_count or PAGE_COUNT) * SPINE_INCHES_PER_PAGE

def get_cover_spread_size(page_count=None):
    """Returns (width_in, height_in) of the full cover spread incl. bleed."""
    spine = get_spine_width(page_count)
    width = TRIM_WIDTH * 2 + spine + BLEED_SIZE * 2
    height = TRIM_HEIGHT + BLEED_SIZE * 2
    return width, height

def get_status_message():
    speed = "Max Speed" if DEPLOYMENT_TIER == "PAID" else "Safe Limits Active"
    return f"🎨 QUALITY_MODE={QUALITY_MODE} ({GEN_MODEL_ID}) | Tier={DEPLOYMENT_TIER} - {speed}"
