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
            files = glob.glob(f"assets/ref_{asset_type}_*.png")
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

    def generate_cover(self, theme, main_character, gear_objects):
        """
        Generates the prompt for the Cover Art using Blueprint + Wireframe + DNA.
        """
        logger.info("Generating Cover Prompt via Blueprint...")
        self._rate_limit()
        
        # 1. Load Blueprint Text
        # 1. Load Blueprint Text
        blueprint_path = "docs/MASTER_COVER_BLUEPRINT_v1.0.md"
        blueprint_text = ""
        if os.path.exists(blueprint_path):
            with open(blueprint_path, "r") as f:
                blueprint_text = f.read()
        else:
            logger.warning("Blueprint file not found!")
            
        # 2. Load Wireframe Image (Geometry)
        wireframe_path = "assets/ref_cover_layout_wireframe_kdp.png"
        wireframe_img = None
        if os.path.exists(wireframe_path):
            wireframe_img = Image.open(wireframe_path)
        else:
            logger.warning("Wireframe image not found!")

        # 3. Load Structure Example Image (Context)
        structure_path = "assets/ref_cover_structure_example.png"
        structure_img = None
        if os.path.exists(structure_path):
            structure_img = Image.open(structure_path)
        else:
            logger.warning("Structure example image not found!")

        # 4. Construct Meta-Prompt for Gemini
        dna_cover = self.style_library.get("dna_cover", "")
        
        meta_prompt = (
            "Act as an Expert Art Director. Construct a highly detailed image generation prompt for Imagen 4.0.\n\n"
            f"THEME: {theme}\n"
            f"MAIN CHARACTER: {main_character}\n"
            f"GEAR: {gear_objects}\n"
            f"STYLE DNA: {dna_cover}\n\n"
            "REFERENCE DOCUMENTS:\n"
            f"1. BLUEPRINT TEXT:\n{blueprint_text}\n\n"
            "2. WIREFRAME IMAGE (First Image): This defines the STRICT GEOMETRY (X/Y Coordinates). "
            "Red=Title, Yellow=Marketing, Green=Stickers, Blue=Mini-Char, White=Main-Char, Black=Logo Zone.\n\n"
            "3. STRUCTURE EXAMPLE (Second Image): This defines the CONTEXT (Layering & Density). "
            "Observe how the Character overlaps the background. Observe how Stickers float in negative space.\n\n"
            "INSTRUCTION:\n"
            "Write a single, seamless panoramic image prompt. "
            "1. GEOMETRY: Follow the Wireframe for placement.\n"
            "2. CONTEXT: Follow the Structure Example for layering/density.\n"
            "3. STYLE: Follow the Style DNA for rendering.\n"
            "Explicitly instruct the generator to leave the 'Black Zone' (Zone 8) empty or reserved for the 'assets/logo.png' overlay. "
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
            return final_prompt
            
        except Exception as e:
            logger.error(f"Failed to generate cover prompt: {e}")
            return f"A seamless panoramic book cover for {theme}, {dna_cover}"

    def generate_prompts(self, theme):
        """
        Generates all interior prompts using Multi-Shot DNA.
        """
        # 1. Analyze Assets first
        self.analyze_assets()
        
        # Define Context
        items = ["Helmet", "Hose", "Ladder", "Axe", "Boots"] 
        main_character = f"Heroic {theme}"
        gear_objects = ", ".join(items)
        
        prompts = []
        
        # Helper to get DNA
        def get_dna(key):
            return self.style_library.get(key, "black and white line art")

        # Page 1: Mission Briefing
        self._rate_limit()
        prompts.append({
            "type": "mission",
            "prompt": f"{get_dna('dna_page_01')}, title page design for {theme}, magnifying glass outline, central area clean, border of {theme} icons."
        })
        
        # Page 2: Note to Parents
        self._rate_limit()
        prompts.append({
            "type": "parents",
            "prompt": f"{get_dna('dna_page_02')}, instructional page layout, {theme} theme, cute border frame, large empty central area for text, 'Note to Parents' header style."
        })

        # Page 3: Intro
        self._rate_limit()
        prompts.append({
            "type": "intro",
            "prompt": f"{get_dna('dna_page_03')}, 'Are you ready to explore?' theme, {main_character} waving hello, minimal background, space for dedication text."
        })
        
        # Demo: Just 1 Spread (Page 4 & 5)
        self._rate_limit()
        prompts.append({
            "type": "knolling",
            "prompt": f"{get_dna('dna_knolling')}, knolling photography layout, flat lay, {theme} parts, organized grid of {gear_objects}, top 75% filled, bottom 25% empty white space."
        })
        
        self._rate_limit()
        prompts.append({
            "type": "action",
            "prompt": f"{get_dna('dna_action')}, {theme} in action pose, wearing {gear_objects}, dynamic composition, {main_character} description."
        })
        
        # Certificate
        self._rate_limit()
        prompts.append({
            "type": "certificate",
            "prompt": f"{get_dna('dna_certificate')}, certificate of completion design for {theme}, rectangular border of diverse items, empty center, official document style."
        })
        
        return {
            "prompts": prompts,
            "main_character": main_character,
            "gear_objects": gear_objects
        }
