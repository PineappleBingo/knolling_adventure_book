"""
Agent Bravo: Executive Creative Director (Prompt Logic)
Mission: Ensure the "Director" logic strictly adheres to the visual style guidelines.
"""

import logging
import time
import glob
import os
import google.generativeai as genai
from PIL import Image
from src import config

logger = logging.getLogger("AgentBravo")

class AgentBravo:
    def __init__(self):
        logger.info("Agent Bravo initialized.")
        # Initialize Gemini Vision for analysis
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.vision_model = genai.GenerativeModel(config.QA_MODEL_NAME) # Use the smart model (Gemini 2.5 Pro)
        else:
            logger.error("GOOGLE_API_KEY not found.")
            
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

    def analyze_assets(self):
        """
        Analyzes reference assets to extract Shared Visual DNA.
        """
        logger.info("Agent Bravo: Analyzing assets for Visual DNA...")
        
        asset_types = [
            "cover", "page_01", "page_02", "page_03", 
            "knolling", "action", "certificate"
        ]
        
        for asset_type in asset_types:
            # Find all matching files
            # Strict filtering: Only use *_01.png as the Master Style Reference
            # This avoids picking up _wireframe or _structure files
            files = glob.glob(f"assets/ref_{asset_type}_01.png")
            
            if not files:
                # Fallback to broader search but exclude keywords
                all_files = glob.glob(f"assets/ref_{asset_type}_*.png")
                files = [f for f in all_files if "_wireframe" not in f and "_structure" not in f]
            
            if not files:
                logger.warning(f"No reference images found for {asset_type}. Using default style.")
                self.style_library[f"dna_{asset_type}"] = "[Default Style: Black and white line art, coloring book style]"
                continue
                
            logger.info(f"Analyzing {len(files)} images for {asset_type}...")
            
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
                
                self._rate_limit()
                response = self.vision_model.generate_content([prompt, *images])
                dna = response.text.strip()
                self.style_library[f"dna_{asset_type}"] = dna
                logger.info(f"Extracted DNA for {asset_type}: {dna[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to analyze assets for {asset_type}: {e}")
                self.style_library[f"dna_{asset_type}"] = "[Fallback Style: Black and white line art]"

    def _extract_bible_specs(self, section_tag):
        """
        Extracts the specific text block for a given tag from the Series Master Bible.
        """
        bible_path = "Series Master Bible v5.21.md"
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

    def _generate_smart_prompt(self, page_type, theme, specific_context):
        """
        Generates a smart prompt using Wireframe + Structure + DNA.
        Handles mapping from logical page type to asset filename.
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
        self._rate_limit()

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

        # 3. Get DNA
        dna_key = f"dna_{asset_key}"
        dna = self.style_library.get(dna_key, self.style_library.get("dna_cover", "black and white line art"))

        # 4. Construct Meta-Prompt
        # CRITICAL: Explicit instruction to ignore colored lines in output
        color_instruction = ""
        if page_type != "cover":
            color_instruction = (
                "CRITICAL: The Wireframe contains COLORED ZONES (Red/Green/Blue) for reference only. "
                "The final output must be pure BLACK & WHITE line art. "
                "Do NOT draw the colored zone lines. Do NOT draw the text labels found in the wireframe. "
                "Only draw the ILLUSTRATION content inside the zones."
            )
        else:
            color_instruction = "Follow the Wireframe zones for placement. Output full color for the Cover."

        meta_prompt = (
            "Act as an Expert Art Director. Construct a highly detailed image generation prompt for Imagen 4.0.\n\n"
            f"THEME: {theme}\n"
            f"CONTEXT (BIBLE SPECS): {specific_context}\n"
            f"STYLE DNA: {dna}\n\n"
            "REFERENCE DOCUMENTS:\n"
            "1. WIREFRAME IMAGE (First Image): This defines the STRICT GEOMETRY (X/Y Coordinates). "
            "Follow the layout lines exactly.\n\n"
            "2. STRUCTURE EXAMPLE (Second Image): This defines the CONTEXT (Layering & Density). "
            "Observe how elements overlap and fill the space.\n\n"
            "INSTRUCTION:\n"
            "Write a single, detailed image prompt.\n"
            "1. GEOMETRY: Follow the Wireframe for placement.\n"
            "2. CONTEXT: Follow the Structure Example for layering/density.\n"
            "3. STYLE: Follow the Style DNA for rendering.\n"
            f"{color_instruction}\n"
            "Output ONLY the raw prompt string, no markdown."
        )

        try:
            inputs = [meta_prompt]
            if wireframe_img:
                inputs.append(wireframe_img)
            if structure_img:
                inputs.append(structure_img)
                
            response = self.vision_model.generate_content(inputs)
            final_prompt = response.text.strip()
            
            # Append Negative DNA
            negative_dna = self.NEGATIVE_GLOBAL
            if page_type == "knolling":
                negative_dna += f", {self.NEGATIVE_KNOLLING}"
            elif page_type == "action":
                negative_dna += f", {self.NEGATIVE_ACTION}"
            elif page_type == "cover":
                negative_dna += f", {self.NEGATIVE_COVER}"
                
            final_prompt += f" --negative_prompt: {negative_dna}"
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"Failed to generate smart prompt for {page_type}: {e}")
            return f"{specific_context}, {dna} --negative_prompt: {self.NEGATIVE_GLOBAL}"

    def generate_cover(self, theme, main_character, gear_objects):
        """
        Generates the prompt for the Cover Art using Blueprint + Wireframe + DNA.
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
        Generates all interior prompts using Multi-Shot DNA and Smart Prompt Logic.
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
        prompts.append({
            "type": "mission",
            "page_number": 2,
            "prompt": self._generate_smart_prompt("mission", theme, spec_mission or "Title page design, magnifying glass outline.")
        })
        
        # Page 2: Note to Parents (System Page 3)
        spec_parents = self._extract_bible_specs("[PAGE_02_PARENTS]")
        prompts.append({
            "type": "parents",
            "page_number": 3,
            "prompt": self._generate_smart_prompt("parents", theme, spec_parents or "Instructional page layout, cute border frame.")
        })

        # Page 3: Intro (System Page 4)
        spec_intro = self._extract_bible_specs("[PAGE_03_START]")
        prompts.append({
            "type": "intro",
            "page_number": 4,
            "prompt": self._generate_smart_prompt("intro", theme, spec_intro or f"'Are you ready to explore?' theme, {main_character}.")
        })
        
        # Demo: Just 1 Spread (Page 4 & 5) -> System Page 5 & 6
        spec_knolling = self._extract_bible_specs("[PAGE_04_KNOLLING]")
        prompts.append({
            "type": "knolling",
            "page_number": 5,
            "prompt": self._generate_smart_prompt("knolling", theme, spec_knolling or f"Knolling photography layout, {gear_objects}.")
        })
        
        spec_action = self._extract_bible_specs("[PAGE_05_ACTION]")
        prompts.append({
            "type": "action",
            "page_number": 6,
            "prompt": self._generate_smart_prompt("action", theme, spec_action or f"{theme} in action pose, wearing {gear_objects}.")
        })
        
        # Certificate (Page 50)
        spec_cert = self._extract_bible_specs("[PAGE_50_CERTIFICATE]")
        prompts.append({
            "type": "certificate",
            "page_number": 50,
            "prompt": self._generate_smart_prompt("certificate", theme, spec_cert or "Certificate of completion design.")
        })
        
        return {
            "prompts": prompts,
            "main_character": main_character,
            "gear_objects": gear_objects
        }
