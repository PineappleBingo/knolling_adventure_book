"""
Agent Bravo: Executive Creative Director (Prompt Logic)
Mission: Ensure the "Director" logic strictly adheres to the visual style guidelines.
"""

import logging
import time
import glob
import os
from google import genai
from PIL import Image
from src import config

MAX_RETRIES = 3
BACKOFF_BASE = 10  # seconds

logger = logging.getLogger("AgentBravo")

# ── Bible Section 5.0: Fixed DNA Macros (deterministic style anchors) ──
DNA_MACROS = {
    "mission": 'High-contrast coloring page. Layout: Center Magnifying Glass (empty glass), Bottom 3-step icon strip (Crayon/Eye/Lightbulb). Background: "Sticker Cloud" of [THEME] items. Style: Die-cut stickers, thick double outlines, no shading.',
    "parents": 'Visual instruction page. Border: Single thick rounded rectangular border. Icon: Bottom center "Marker Pen" inside "Prohibition Circle". Center: Pure white void. Style: Safety signage, heavy strokes, minimal.',
    "intro": 'Hero Prop. Subject: Cute chunky [THEME] Gear Bag, open with tools visible. Add-on: Large chunky arrow pointing right. Layout: Center zone. Style: Heroic cute, detailed textures.',
    "knolling": 'Knolling Photography Style. 90-degree flat lay. Distinct [THEME] parts in a grid. Spacing: White space separation (no overlap). Style: Technical vector line art.',
    "action": 'Full-page action. Subject: Hero character utilizing [THEME] tools. Pose: Dynamic, eye contact. Background: Immersive [THEME] environment. Style: Full-bleed scene, Centralized Composition, Wide White Margin. No double tools.',
    "certificate": 'Official Award. Border: Patterned icons of [THEME]. Center: Empty for text. Details: Ribbon/Seal at bottom. Style: Formal/Playful mix.',
    "cover": 'Wide seamless spread. Front: Hero Character + Title. Back: Flat-lay gear + Mockups. Style: Vibrant colors, thick clean outlines, high commercial quality.',
}

# ── Bible Section 5 [A]-[G]: Fixed Prompt Templates ──
PROMPT_TEMPLATES = {
    "mission": (
        '[TECH_ENVELOPE], [DNA]. '
        'Variable Zone (Zone 4): A "Sticker Cloud" filling the negative space. '
        'Content: 10-15 distinct [THEME] items. '
        'Style: "Die-cut Sticker" effect with thick double outlines and white gaps.'
    ),
    "parents": (
        '[TECH_ENVELOPE], [DNA], a coloring book instruction page. A clean white background. '
        'A single thick black rectangular border with rounded corners near the edges. '
        'A large empty white space in the center. At the bottom center, a cute thick-line vector icon '
        'of a "Marker Pen" inside a "Prohibition Sign" (Circle with a diagonal line). '
        'No text, no letters, no words. High contrast line art.'
    ),
    "intro": (
        '[TECH_ENVELOPE], [DNA], black and white line art coloring page. '
        'Layout: A thick black rectangular border with rounded corners. '
        'Center: A large, detailed [THEME] gear bag or backpack (chunky and friendly style) overflowing with theme-specific tools. '
        'Action: A bold arrow pointing to the right. '
        'Constraint: All elements are fixed; no character art on this page. Focus on the tools and the bag.'
    ),
    "knolling": (
        '[TECH_ENVELOPE], [DNA], black and white line art, knolling photography layout, flat lay, '
        '[SUBJECT] parts, organized grid of [OBJECT LIST], top 75% filled, bottom 25% empty white space, no shading.'
    ),
    "action": (
        '[TECH_ENVELOPE], [DNA], black and white line art, [SUBJECT] in action pose, wearing [OBJECT LIST], '
        'dynamic composition, thick uniform lines, [MAIN CHARACTER DESCRIPTION].'
    ),
    "certificate": (
        '[TECH_ENVELOPE], [DNA], certificate of completion design. '
        'Structure: Single line borders (inner and outer). '
        'Frame Content (Zone 1): A rectangular frame composed of diverse [THEME] items arranged in a neat knolling style between the borders. '
        'Center (Zone 3): Large empty white space for text injection. '
        'Corner (Zone 2): Space for "Official Explore" badge.'
    ),
    "cover": (
        '[TECH_ENVELOPE]. A seamless panoramic book cover design for kids, wide aspect ratio, [THEME] theme. '
        'Right Side: Title area (Zone 1), Subtitle area (Zone 9), Hero Character (Zone 11). Leave Zone 8 empty for Logo Asset. '
        'Left Side: Text area (Zone 10 - Context: "Match Tools"), Mockup display of internal pages (Zone 4), Mini Character (Zone 5). '
        'Style: Flat vector illustration, vibrant colors, thick clean outlines, high energy, 300 dpi.'
    ),
}

# ── Bible Technical Envelopes ──
TECH_ENVELOPE_INTERNAL = "Canvas: 8.625x8.75 inches. Resolution: 300 DPI. Pure white background. Keep all text/art inside 7.75x7.75 inch safety zone. Thick uniform black vector lines."
TECH_ENVELOPE_COVER = "Canvas: 17.365x8.75 inches (Full Spread). Resolution: 300 DPI. Right side is Front, Left side is Back. Center 0.115 inch is Spine. Vibrant colors, thick outlines, heroic cute style."

class AgentBravo:
    def __init__(self):
        logger.info("Agent Bravo initialized.")
        # Initialize Gemini Vision for analysis
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            self.genai_client = genai.Client(api_key=api_key)
            self.vision_model_name = config.QA_MODEL_NAME  # Use the smart model (Gemini 2.5 Pro)
        else:
            logger.error("GOOGLE_API_KEY not found.")
            self.genai_client = None
            self.vision_model_name = config.QA_MODEL_NAME
            
        self.style_library = {} # Stores extracted DNA

        # 5.2 NEGATIVE DNA LIBRARY
        self.NEGATIVE_GLOBAL = "text, font, letters, words, watermark, signature, copyright info, barcode, qr code, shading, gradients, grayscale, colored, filled, 3d render, realistic photo, sketch lines, dithering, noise, blur, low quality, pixelated, jpeg artifacts, cropped, cut off, duplicate, deformed"
        self.NEGATIVE_KNOLLING = "perspective, angled view, isometric, human hands, holding items, messy, overlapping items, shadow, chaotic background, multiple angles, distorted shapes"
        self.NEGATIVE_ACTION = "knolling grid, static pose, floating objects, multiple horizons, text bubbles, speech balloons, frame border, cut off limbs, babyish proportions, scary"
        self.NEGATIVE_COVER = "barcode placeholder, price tag, low resolution, dull colors, messy sketch, cutoff character, internal page guides"

    def _rate_limit(self):
        """Applies rate limiting delay."""
        logger.info(f"Sleeping for {config.PROMPT_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.PROMPT_GEN_DELAY)

    def _call_with_backoff(self, model, contents):
        """Calls Gemini API with exponential backoff on 503 errors."""
        for attempt in range(MAX_RETRIES):
            try:
                self._rate_limit()
                response = self.genai_client.models.generate_content(
                    model=model,
                    contents=contents
                )
                return response
            except Exception as e:
                error_str = str(e)
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning(f"503 UNAVAILABLE (attempt {attempt+1}/{MAX_RETRIES}). Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        raise Exception(f"API still unavailable after {MAX_RETRIES} retries")

    def analyze_assets(self):
        """
        Analyzes reference assets to extract Shared Visual DNA.
        Uses the same asset key mapping as _generate_smart_prompt() to match actual filenames.
        """
        logger.info("Agent Bravo: Analyzing assets for Visual DNA...")

        # Maps logical name -> actual filename key (must match files in assets/)
        asset_types = {
            "cover": "cover",
            "page1": "page1",
            "page2": "page2",
            "page3": "page3",
            "page4": "page4",   # knolling spread
            "page5": "page5",   # action spread
            "page50": "page50", # certificate
        }

        for dna_key, file_key in asset_types.items():
            # Strict filtering: Only use *_01.png as the Master Style Reference
            files = glob.glob(f"assets/ref_{file_key}_01.png")

            if not files:
                # Fallback to broader search but exclude wireframe/structure files
                all_files = glob.glob(f"assets/ref_{file_key}_*.png")
                files = [f for f in all_files if "_wireframe" not in f and "_structure" not in f]

            if not files:
                logger.warning(f"No reference images found for {dna_key} (pattern: assets/ref_{file_key}_01.png). Using default style.")
                self.style_library[f"dna_{dna_key}"] = "[Default Style: Black and white line art, coloring book style]"
                continue

            logger.info(f"Analyzing {len(files)} images for {dna_key}...")
            
            try:
                # Load images
                images = [Image.open(f) for f in files[:5]] # Limit to 5 max
                
                prompt = (
                    f"Analyze these {len(images)} reference images collectively. "
                    "Ignore specific characters or objects. "
                    "Extract the 'Shared Visual DNA' (line weight, shading rules, composition layout, whitespace usage) "
                    "into a detailed, comma-separated style description string. "
                    "Focus on technical artistic attributes suitable for an image generation prompt."
                )
                
                response = self._call_with_backoff(
                    self.vision_model_name,
                    [prompt, *images]
                )
                dna = response.text.strip()
                self.style_library[f"dna_{dna_key}"] = dna
                logger.info(f"Extracted DNA for {dna_key}: {dna[:50]}...")

            except Exception as e:
                logger.error(f"Failed to analyze assets for {dna_key}: {e}")
                self.style_library[f"dna_{dna_key}"] = "[Fallback Style: Black and white line art]"

    def _extract_bible_specs(self, section_tag):
        """
        Extracts the specific text block for a given tag from the Series Master Bible.
        """
        bible_path = "Series Master Bible v5.22.md"
        if not os.path.exists(bible_path):
            logger.warning(f"Bible not found at {bible_path}")
            return ""
            
        try:
            with open(bible_path, "r") as f:
                content = f.read()
                
            # Find the section
            start_idx = content.find(section_tag)
            if start_idx == -1:
                logger.warning(f"Section {section_tag} not found in Bible.")
                return ""
                
            # Find the next section (starts with #### [) or end of file
            # We assume sections start with #### [TAG]
            # We want to capture everything until the next ####
            
            # Start after the tag line
            content_after_tag = content[start_idx:]
            # Find next header
            next_header_idx = content_after_tag.find("#### [", 1) 
            
            if next_header_idx != -1:
                return content_after_tag[:next_header_idx].strip()
            else:
                return content_after_tag.strip()
                
        except Exception as e:
            logger.error(f"Failed to extract Bible specs: {e}")
            return ""

    def _build_bible_prompt(self, page_type, theme, subject="", object_list="", main_character=""):
        """
        Builds a prompt from the Bible's fixed template (Section 5) with variable substitution.
        Returns the expanded prompt string.
        """
        template = PROMPT_TEMPLATES.get(page_type, "")
        if not template:
            return ""

        # Select tech envelope
        tech_envelope = TECH_ENVELOPE_COVER if page_type == "cover" else TECH_ENVELOPE_INTERNAL
        # Get fixed DNA
        fixed_dna = DNA_MACROS.get(page_type, "black and white line art")

        # Variable substitution
        expanded = template.replace("[TECH_ENVELOPE]", tech_envelope)
        expanded = expanded.replace("[DNA]", fixed_dna)
        expanded = expanded.replace("[THEME]", theme)
        expanded = expanded.replace("[SUBJECT]", subject or theme)
        expanded = expanded.replace("[OBJECT LIST]", object_list)
        expanded = expanded.replace("[MAIN CHARACTER DESCRIPTION]", main_character)
        expanded = expanded.replace("[EDITION THEME]", theme)

        return expanded

    def _generate_smart_prompt(self, page_type, theme, specific_context,
                               subject="", object_list="", main_character=""):
        """
        Generates a smart prompt using Bible Template + Wireframe + Structure + DNA.
        Returns 4-tuple: (prompt, wireframe_path, reference_images, negative_dna).
        """
        # Asset Mapping
        asset_map = {
            "mission": "page1",
            "parents": "page2",
            "intro": "page3",
            "knolling": "page4",
            "action": "page5",
            "certificate": "page50",
            "cover": "cover"
        }

        asset_key = asset_map.get(page_type, page_type)
        logger.info(f"Generating Smart Prompt for {page_type} (Asset Key: {asset_key})...")

        # 1. Load Wireframe (Geometry)
        wireframe_path = f"assets/ref_{asset_key}_layout_wireframe_kdp.png"
        wireframe_img = None
        if os.path.exists(wireframe_path):
            wireframe_img = Image.open(wireframe_path)
        else:
            logger.warning(f"Wireframe not found for {asset_key}: {wireframe_path}")

        # 2. Load Structure Example (Context)
        structure_path = f"assets/ref_{asset_key}_structure_example.png"
        structure_img = None
        if os.path.exists(structure_path):
            structure_img = Image.open(structure_path)
        else:
            logger.warning(f"Structure example not found for {asset_key}: {structure_path}")

        # 3. Get Dynamic DNA (supplementary nuance from reference analysis)
        dna_key = f"dna_{asset_key}"
        dynamic_dna = self.style_library.get(dna_key, self.style_library.get("dna_cover", "black and white line art"))

        # 4. Get Fixed DNA + Tech Envelope from Bible
        fixed_dna = DNA_MACROS.get(page_type, "black and white line art")
        tech_envelope = TECH_ENVELOPE_COVER if page_type == "cover" else TECH_ENVELOPE_INTERNAL

        # 5. Build Bible prompt template with variable substitution
        bible_prompt = self._build_bible_prompt(
            page_type, theme, subject=subject,
            object_list=object_list, main_character=main_character
        )

        # 6. Build Negative DNA (separate from prompt — NOT appended with --negative_prompt)
        negative_dna = self.NEGATIVE_GLOBAL
        if page_type == "knolling":
            negative_dna += f", {self.NEGATIVE_KNOLLING}"
        elif page_type == "action":
            negative_dna += f", {self.NEGATIVE_ACTION}"
        elif page_type == "cover":
            negative_dna += f", {self.NEGATIVE_COVER}"

        # 7. Color instruction
        if page_type != "cover":
            color_instruction = (
                "CRITICAL: The Wireframe contains COLORED ZONES (Red/Green/Blue) for reference only. "
                "The final output must be pure BLACK & WHITE line art. "
                "Do NOT draw the colored zone lines. Do NOT draw the text labels found in the wireframe. "
                "Only draw the ILLUSTRATION content inside the zones."
            )
        else:
            color_instruction = "Follow the Wireframe zones for placement. Output full color for the Cover."

        # 8. Construct Meta-Prompt with Bible anchors
        meta_prompt = (
            "Act as an Expert Art Director. Construct a highly detailed image generation prompt.\n\n"
            f"TECHNICAL ENVELOPE:\n{tech_envelope}\n\n"
            f"THEME: {theme}\n\n"
            f"FIXED STYLE DNA (MUST follow exactly):\n{fixed_dna}\n\n"
            f"BIBLE PROMPT TEMPLATE:\n{bible_prompt}\n\n"
            f"BIBLE SPECIFICATIONS:\n{specific_context}\n\n"
            f"SUPPLEMENTARY STYLE NUANCE (from reference analysis):\n{dynamic_dna}\n\n"
            "REFERENCE DOCUMENTS:\n"
            "1. WIREFRAME IMAGE: Defines STRICT GEOMETRY. Follow zone positions exactly.\n"
            "2. STRUCTURE EXAMPLE: Defines CONTEXT (layering & density).\n\n"
            f"{color_instruction}\n\n"
            "MANDATORY RULES:\n"
            "- Output must be pure BLACK & WHITE line art (except covers)\n"
            "- Thick uniform vector lines, no sketching, no grayscale\n"
            "- No text, no letters, no words in the image\n"
            "- All art must stay inside the safety zone\n"
            f"- EXCLUDE from output: {negative_dna}\n\n"
            "Output ONLY the raw prompt string, no markdown."
        )

        # Collect reference image paths to pass through to Charlie for multimodal input
        ref_img_path = f"assets/ref_{asset_key}_01.png"
        reference_images = [ref_img_path] if os.path.exists(ref_img_path) else []

        try:
            inputs = [meta_prompt]
            if wireframe_img:
                inputs.append(wireframe_img)
            if structure_img:
                inputs.append(structure_img)

            response = self._call_with_backoff(
                self.vision_model_name,
                inputs
            )
            final_prompt = response.text.strip()

            return final_prompt, wireframe_path if os.path.exists(wireframe_path) else None, reference_images, negative_dna

        except Exception as e:
            logger.error(f"Failed to generate smart prompt for {page_type}: {e}")
            # Fallback: use the Bible template directly as the prompt
            fallback = bible_prompt or (
                f"{tech_envelope}. Black and white line art coloring book page for children ages 4-8. "
                f"Pure black outlines on white background, no shading, no color, no gradients. "
                f"Thick clean vector lines, rounded corners, toy-like proportions. "
                f"Theme: {specific_context}. Style: {fixed_dna}"
            )
            return fallback, wireframe_path if os.path.exists(wireframe_path) else None, reference_images, negative_dna

    def generate_cover(self, theme, main_character, gear_objects):
        """
        Generates the prompt for the Cover Art using Blueprint + Wireframe + DNA.
        Returns 4-tuple: (prompt, wireframe_path, reference_images, negative_dna).
        """
        # Load Blueprint Text for Cover specifically
        blueprint_path = "docs/MASTER_COVER_BLUEPRINT_v1.0.md"
        blueprint_text = ""
        if os.path.exists(blueprint_path):
            with open(blueprint_path, "r") as f:
                blueprint_text = f.read()

        context = (
            f"MAIN CHARACTER: {main_character}\n"
            f"GEAR: {gear_objects}\n"
            f"BLUEPRINT: {blueprint_text}\n"
            "Explicitly instruct the generator to leave the 'Black Zone' (Zone 8) empty or reserved for the 'assets/logo.png' overlay."
        )

        return self._generate_smart_prompt("cover", theme, context)

    def generate_prompts(self, theme):
        """
        Generates all interior prompts using Bible Templates + Multi-Shot DNA + Smart Prompt Logic.
        Each prompt dict includes negative_dna as a separate field.
        """
        # 1. Analyze Assets first
        self.analyze_assets()

        # Define Context
        items = ["Helmet", "Hose", "Ladder", "Axe", "Boots"]
        main_character = f"Heroic {theme}"
        gear_objects = ", ".join(items)

        prompts = []

        # Page 1: Mission Briefing (System Page 2)
        spec_mission = self._extract_bible_specs("[PAGE_01_MISSION]")
        prompt_text, wf, refs, neg = self._generate_smart_prompt("mission", theme, spec_mission or "Title page design, magnifying glass outline.")
        prompts.append({"type": "mission", "page_number": 2, "prompt": prompt_text, "wireframe_path": wf, "reference_images": refs, "negative_dna": neg})

        # Page 2: Note to Parents (System Page 3)
        spec_parents = self._extract_bible_specs("[PAGE_02_PARENTS]")
        prompt_text, wf, refs, neg = self._generate_smart_prompt("parents", theme, spec_parents or "Instructional page layout, cute border frame.")
        prompts.append({"type": "parents", "page_number": 3, "prompt": prompt_text, "wireframe_path": wf, "reference_images": refs, "negative_dna": neg})

        # Page 3: Intro (System Page 4)
        spec_intro = self._extract_bible_specs("[PAGE_03_START]")
        prompt_text, wf, refs, neg = self._generate_smart_prompt("intro", theme, spec_intro or f"'Are you ready to explore?' theme, {main_character}.")
        prompts.append({"type": "intro", "page_number": 4, "prompt": prompt_text, "wireframe_path": wf, "reference_images": refs, "negative_dna": neg})

        # Demo: Just 1 Spread (Page 4 & 5) -> System Page 5 & 6
        spec_knolling = self._extract_bible_specs("[PAGE_04_KNOLLING]")
        prompt_text, wf, refs, neg = self._generate_smart_prompt(
            "knolling", theme, spec_knolling or f"Knolling photography layout, {gear_objects}.",
            subject=theme, object_list=gear_objects
        )
        prompts.append({"type": "knolling", "page_number": 5, "prompt": prompt_text, "wireframe_path": wf, "reference_images": refs, "negative_dna": neg})

        spec_action = self._extract_bible_specs("[PAGE_05_ACTION]")
        prompt_text, wf, refs, neg = self._generate_smart_prompt(
            "action", theme, spec_action or f"{theme} in action pose, wearing {gear_objects}.",
            subject=theme, object_list=gear_objects, main_character=main_character
        )
        prompts.append({"type": "action", "page_number": 6, "prompt": prompt_text, "wireframe_path": wf, "reference_images": refs, "negative_dna": neg})

        # Certificate (Page 50)
        spec_cert = self._extract_bible_specs("[PAGE_50_CERTIFICATE]")
        prompt_text, wf, refs, neg = self._generate_smart_prompt("certificate", theme, spec_cert or "Certificate of completion design.")
        prompts.append({"type": "certificate", "page_number": 50, "prompt": prompt_text, "wireframe_path": wf, "reference_images": refs, "negative_dna": neg})

        return {
            "prompts": prompts,
            "main_character": main_character,
            "gear_objects": gear_objects
        }
