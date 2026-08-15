"""
Agent Bravo: Executive Creative Director (Prompt Logic)
Mission: Ensure the "Director" logic strictly adheres to the visual style guidelines.
"""

import json
import logging
import re
import time
import glob
import os
from google import genai
from google.genai import types as genai_types
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

    def _call_with_backoff(self, model, contents, gen_config=None):
        """Calls Gemini API with exponential backoff on transient errors (503/429)."""
        for attempt in range(MAX_RETRIES):
            try:
                self._rate_limit()
                kwargs = {"model": model, "contents": contents}
                if gen_config is not None:
                    kwargs["config"] = gen_config
                response = self.genai_client.models.generate_content(**kwargs)
                return response
            except Exception as e:
                error_str = str(e)
                transient = any(t in error_str for t in
                                ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))
                if transient and attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning(f"Transient API error (attempt {attempt+1}/{MAX_RETRIES}). Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        raise Exception(f"API still unavailable after {MAX_RETRIES} retries")

    def _get_theme_content(self, theme):
        """
        One structured LLM call for theme-specific CONTENT (never visual style):
        main character description + gear list. Replaces the hardcoded
        firefighter gear that shipped with every theme.
        """
        defaults = {
            "main_character": f"Heroic {theme} character, chunky toy-like proportions",
            "gear": ["Helmet", "Gloves", "Boots", "Tool Belt", "Backpack"],
        }
        if not self.genai_client:
            return defaults

        prompt = (
            f'Theme: "{theme}" (children\'s coloring book, ages 4-8).\n'
            'Return JSON: {"main_character": "<one-line hero description>", '
            '"gear": ["<5 distinct, theme-authentic tools/equipment items>"]}.\n'
            "Items must be instantly recognizable, simple shapes, kid-safe."
        )
        try:
            response = self._call_with_backoff(
                self.vision_model_name, [prompt],
                gen_config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            fenced = re.search(r"\{.*\}", response.text, re.DOTALL)
            data = json.loads(fenced.group(0) if fenced else response.text)
            if data.get("main_character") and isinstance(data.get("gear"), list) and data["gear"]:
                return {
                    "main_character": str(data["main_character"]),
                    "gear": [str(g) for g in data["gear"]][:5],
                }
        except Exception as e:
            logger.warning(f"Theme content call failed ({e}); using defaults.")
        return defaults

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
        Builds the final image prompt DETERMINISTICALLY from the Bible templates.
        Returns 4-tuple: (prompt, wireframe_path, reference_images, negative_dna).

        Single round-trip architecture: the raw reference images (style ref +
        structure example + wireframe) travel to the IMAGE model as pixels via
        Agent Charlie. The old flow paraphrased them into text twice through
        Gemini Vision before generation — visual DNA does not survive that.
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
        logger.info(f"Building deterministic prompt for {page_type} (Asset Key: {asset_key})...")

        # 1. Resolve reference assets (style ref first, then structure example —
        #    Charlie labels them by role in that order; wireframe rides separately)
        wireframe_path = f"assets/ref_{asset_key}_layout_wireframe_kdp.png"
        if not os.path.exists(wireframe_path):
            logger.warning(f"Wireframe not found for {asset_key}: {wireframe_path}")
            wireframe_path = None

        reference_images = []
        style_ref_path = f"assets/ref_{asset_key}_01.png"
        if os.path.exists(style_ref_path):
            reference_images.append(style_ref_path)
        else:
            logger.warning(f"Style reference not found for {asset_key}: {style_ref_path}")
        structure_path = f"assets/ref_{asset_key}_structure_example.png"
        if os.path.exists(structure_path):
            reference_images.append(structure_path)
        else:
            logger.warning(f"Structure example not found for {asset_key}: {structure_path}")

        # 2. Fixed DNA + Tech Envelope + Bible template (deterministic)
        fixed_dna = DNA_MACROS.get(page_type, "black and white line art")
        tech_envelope = TECH_ENVELOPE_COVER if page_type == "cover" else TECH_ENVELOPE_INTERNAL
        bible_prompt = self._build_bible_prompt(
            page_type, theme, subject=subject,
            object_list=object_list, main_character=main_character
        )

        # 3. Negative DNA (separate field — never appended as '--negative_prompt')
        negative_dna = self.NEGATIVE_GLOBAL
        if page_type == "knolling":
            negative_dna += f", {self.NEGATIVE_KNOLLING}"
        elif page_type == "action":
            negative_dna += f", {self.NEGATIVE_ACTION}"
        elif page_type == "cover":
            negative_dna += f", {self.NEGATIVE_COVER}"

        # 4. Color instruction
        if page_type != "cover":
            color_instruction = (
                "CRITICAL: The Wireframe contains COLORED ZONES (Red/Green/Blue) for reference only. "
                "The final output must be pure BLACK & WHITE line art. "
                "Do NOT draw the colored zone lines. Do NOT draw the text labels found in the wireframe. "
                "Only draw the ILLUSTRATION content inside the zones."
            )
        else:
            color_instruction = "Follow the Wireframe zones for placement. Output full color for the Cover."

        # 5. Assemble the final prompt — no LLM in the loop
        sections = [bible_prompt or f"{tech_envelope}. Style: {fixed_dna}. Theme: {theme}."]
        if specific_context:
            sections.append(f"PAGE SPECIFICATIONS (Series Master Bible):\n{specific_context}")
        sections.append(color_instruction)
        prompt = "\n\n".join(sections)

        return prompt, wireframe_path, reference_images, negative_dna

    def generate_cover(self, theme, main_character, gear_objects):
        """
        Generates FRONT and BACK cover art prompts as two separate square (1:1)
        generations. The full 17.365"x8.75" spread is composited programmatically
        by Agent Echo (back + spine + front), which also draws title/subtitle/logo
        in real fonts — no image model can hit the exact ~2:1 spread ratio, and
        AI-rendered title text is unreliable.

        Returns dict: {"front": 4-tuple, "back": 4-tuple} matching
        (_prompt, wireframe_path, reference_images, negative_dna).
        """
        # Shared cover assets (style ref / structure / wireframe)
        _, wireframe_path, reference_images, negative_dna = \
            self._generate_smart_prompt("cover", theme, "")

        common_style = (
            "Flat vector illustration, vibrant colors, thick clean black outlines, "
            "heroic cute chunky style for ages 4-8, high energy, white background, "
            "high commercial print quality."
        )
        # Art must stay text-free: title/subtitle/logo are composited in ReportLab.
        no_text = ("Do NOT render any text, letters, words, logos or watermarks — "
                   "all typography is added later in postproduction.")

        front_prompt = (
            f"Square front cover artwork for a children's coloring book, theme: {theme}. "
            f"Hero: {main_character}, full body, dynamic friendly pose, direct eye contact, "
            f"surrounded by floating {gear_objects}. "
            "Composition: hero centered in the lower two-thirds; keep the top third "
            "visually calm (soft background shapes only) as clear space for the title. "
            f"{common_style} {no_text}"
        )
        back_prompt = (
            f"Square back cover artwork for a children's coloring book, theme: {theme}. "
            f"Neat knolling flat-lay of {gear_objects} arranged in a grid on the upper half, "
            "with a small cheerful mini mascot character in the middle area. "
            "Keep the bottom-right quadrant completely empty white space (reserved area). "
            f"{common_style} {no_text}"
        )

        return {
            "front": (front_prompt, wireframe_path, reference_images, negative_dna),
            "back": (back_prompt, wireframe_path, reference_images, negative_dna),
        }

    def generate_prompts(self, theme):
        """
        Generates all interior prompts deterministically from Bible templates.
        Each prompt dict includes negative_dna as a separate field.
        (analyze_assets() is no longer in the loop: raw reference images now go
        to the image model directly, so an LLM paraphrase of them adds nothing.)
        """
        # Theme-specific content (character + gear) via one structured LLM call
        theme_content = self._get_theme_content(theme)
        items = theme_content["gear"]
        main_character = theme_content["main_character"]
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
