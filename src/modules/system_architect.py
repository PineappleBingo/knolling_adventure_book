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

        # Full reference-asset manifest: 3 PNGs per page key (see assets/MANIFEST.md)
        missing_refs = []
        for key in config.ASSET_KEYS:
            for role in config.ASSET_ROLES:
                path = f"assets/ref_{key}_{role}.png"
                if not os.path.exists(path):
                    missing_refs.append(path)
        results["reference_assets"] = {
            "all_present": len(missing_refs) == 0,
            "missing": missing_refs,
        }

        for key, val in results.items():
            if isinstance(val, dict):
                if val["all_present"]:
                    logger.info(f"  {key}: OK")
                else:
                    logger.error(f"  {key}: MISSING {len(val['missing'])} file(s): {val['missing']}")
            elif isinstance(val, bool):
                logger.info(f"  {key}: {'OK' if val else 'MISSING'}")
        return results

    def assert_ready_for_generation(self):
        """
        Hard gate before any generation run. Raises EnvironmentError listing every
        missing prerequisite unless ALLOW_DEGRADED_ASSETS permits reference gaps.
        """
        results = self.check_environment()
        problems = []

        if not results["google_api_key"]:
            problems.append("GOOGLE_API_KEY is not set")
        if not results["bible"]:
            problems.append("Series Master Bible v5.22.md not found")
        if not results["fonts"]["all_present"]:
            problems.append(f"Missing fonts: {results['fonts']['missing']}")

        ref = results["reference_assets"]
        if not ref["all_present"]:
            msg = (f"Missing {len(ref['missing'])} reference asset(s) "
                   f"(see assets/MANIFEST.md): {ref['missing'][:5]}"
                   f"{' ...' if len(ref['missing']) > 5 else ''}")
            if config.ALLOW_DEGRADED_ASSETS:
                logger.warning(f"DEGRADED RUN PERMITTED (ALLOW_DEGRADED_ASSETS=true): {msg}")
            else:
                problems.append(msg + " — set ALLOW_DEGRADED_ASSETS=true to run anyway (debug only)")

        if problems:
            summary = "Environment not ready for generation:\n  - " + "\n  - ".join(problems)
            logger.error(summary)
            raise EnvironmentError(summary)

        logger.info("Environment preflight passed.")
        return results
