"""
Agent Alpha: Senior Systems Architect (Infrastructure)
Mission: Build the rock-solid foundation.
"""

import logging
import os
from src import config

logger = logging.getLogger("AgentAlpha")


class AgentAlpha:
    def __init__(self):
        logger.info("Agent Alpha initialized.")

    def check_environment(self):
        """
        Checks if the environment is correctly set up.
        Returns a dict of check results.
        """
        results = {}
        results["google_api_key"] = bool(os.getenv("GOOGLE_API_KEY"))
        results["telegram_token"] = bool(os.getenv("TELEGRAM_TOKEN"))
        results["credentials_json"] = os.path.exists("credentials.json")

        font_files = [
            config.FONT_TITLE_MAIN, config.FONT_SUBTITLE,
            config.FONT_BODY_TEXT, config.FONT_HANDWRITING, config.FONT_LEGAL,
        ]
        missing_fonts = [f for f in font_files if not os.path.exists(os.path.join(config.PATH_FONTS, f))]
        results["fonts"] = {"all_present": len(missing_fonts) == 0, "missing": missing_fonts}
        results["assets_dir"] = os.path.isdir("assets")
        results["bible"] = os.path.exists("Series Master Bible v5.22.md")

        for key, val in results.items():
            if key == "fonts":
                logger.info(f"  {key}: {'OK' if val['all_present'] else 'MISSING ' + str(val['missing'])}")
            elif isinstance(val, bool):
                logger.info(f"  {key}: {'OK' if val else 'MISSING'}")
        return results
