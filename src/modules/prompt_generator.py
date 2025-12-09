"""
Agent Bravo: Executive Creative Director (Prompt Logic)
Mission: Ensure the "Director" logic strictly adheres to the visual style guidelines.
"""

import logging
import google.generativeai as genai

logger = logging.getLogger("AgentBravo")

class AgentBravo:
    def __init__(self):
        logger.info("Agent Bravo initialized.")
        # Note: API Key should be set in environment variables or configured externally
        # genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    def _inject_style(self, base_prompt):
        """
        Injects the mandatory style tags into the prompt.
        """
        style_tags = (
            "black and white line art, coloring book style for kids ages 4-8, "
            "thick uniform vector lines, high contrast, clear outlines, "
            "modern cartoon style, expressive eyes, heroic proportions, "
            "cute but detailed, no shading, no gray, 300 dpi"
        )
        return f"{base_prompt}, {style_tags}"

    def generate_mission_briefing(self, theme):
        """
        Generates the prompt for Page 1: Mission Briefing.
        """
        prompt = (
            f"title page design, a large bold outline of a magnifying glass in the center (empty inside), "
            f"central area is clean white space, surrounded by a border frame composed of small cute {theme} icons "
            f"arranged along the edges, white background"
        )
        return self._inject_style(prompt)

    def generate_knolling_prompt(self, theme, items):
        """
        Generates the prompt for the Left Page (Knolling).
        """
        items_str = ", ".join(items)
        prompt = (
            f"knolling photography layout, flat lay, {theme} parts/gear, "
            f"organized grid arrangement of {items_str}, "
            f"objects are arranged in the top 75% of the image, "
            f"leaving empty white space at the bottom 25%, "
            f"simple shapes, no text"
        )
        return self._inject_style(prompt)

    def generate_action_prompt(self, theme, action, items, background):
        """
        Generates the prompt for the Right Page (Action).
        """
        items_str = ", ".join(items)
        prompt = (
            f"{theme} in an action pose, full body shot, wearing/using {items_str}, "
            f"interacting with {background}, dynamic composition, "
            f"dynamic pose, immersive background"
        )
        return self._inject_style(prompt)

    def generate_certificate(self, theme):
        """
        Generates the prompt for Page 50: Certificate.
        """
        prompt = (
            f"certificate of completion design, a rectangular border frame composed of neat rows of diverse unique {theme} items "
            f"arranged side-by-side, no repeating patterns, organized knolling style border, "
            f"empty center space for text, clean white background, official document style"
        )
        return self._inject_style(prompt)

    def generate_cover(self, theme, main_character, gear_objects):
        """
        Generates the prompt for the Cover Art.
        """
        prompt = (
            f"a seamless panoramic book cover design for kids, wide aspect ratio, {theme} theme. "
            f"Right Side (Front): Huge title text 'KNOLLING ADVENTURES' at top, subtitle below. "
            f"Top left area features bold, floating 'sticker-style' {gear_objects}. "
            f"Bottom right features cute heroic {main_character} in dynamic action, making eye contact, moving towards center. "
            f"Left Side (Back): Continuation of background. Top left features more floating {gear_objects}. "
            f"Below are two realistic 'paper mockup' style page previews (Left: Knolling, Right: Action) with white borders and drop shadows. "
            f"A mini {main_character} is pointing at the previews. Blurb text below. Bottom right corner is empty background space. "
            f"Style: Flat vector illustration, vibrant colors, thick clean outlines, high energy"
        )
        # Cover has specific style requirements different from interior (color, etc)
        # So we don't use _inject_style here, but append specific cover style
        return f"{prompt}, 300 dpi"
