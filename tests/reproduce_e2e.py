
import os
import sys
import asyncio
import logging
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock missing dependencies
sys.modules["gspread"] = MagicMock()
sys.modules["oauth2client.service_account"] = MagicMock()

from src.modules.orchestrator import AgentOmega
from src import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestE2E")

async def run_test():
    # 1. Setup Environment
    os.environ["TARGET_PAGES"] = "1,50"
    # Reload config to pick up env var
    import importlib
    importlib.reload(config)
    
    logger.info(f"TARGET_PAGES_LIST: {config.TARGET_PAGES_LIST}")
    
    # 2. Mock Agents
    omega = AgentOmega()

    # Mock Agent Alpha preflight (test env has no assets/API keys)
    omega.alpha.assert_ready_for_generation = MagicMock()

    # Mock Agent Charlie (Image Generator) — accepts multimodal kwargs
    omega.charlie.generate_image = MagicMock(
        side_effect=lambda prompt, theme, page_num, **kwargs: f"temp/test_{page_num}.png"
    )

    # Mock Agent Bravo (Prompt Generator)
    # We need to return the structure expected by AgentOmega
    omega.bravo.generate_prompts = MagicMock(return_value={
        "prompts": [
            {"type": "mission", "page_number": 2, "prompt": "p1"},
            {"type": "parents", "page_number": 3, "prompt": "p2"},
            {"type": "intro", "page_number": 4, "prompt": "p3"},
            {"type": "knolling", "page_number": 5, "prompt": "p4"},
            {"type": "action", "page_number": 6, "prompt": "p5"},
            {"type": "certificate", "page_number": 50, "prompt": "p50"}
        ],
        "main_character": "Hero",
        "gear_objects": "Gear"
    })
    # generate_cover returns front/back 4-tuples (composited spread architecture)
    omega.bravo.generate_cover = MagicMock(return_value={
        "front": ("front_prompt", None, [], "neg"),
        "back": ("back_prompt", None, [], "neg"),
    })

    # Mock Agent Delta (QA) — returns (passed, reasons) tuple
    omega.delta.quality_check = MagicMock(return_value=(True, []))
    
    # Mock Agent Echo (PDF Assembler)
    omega.echo.assemble_pdf = MagicMock(return_value="temp/test_output.pdf")
    
    # Mock Agent Golf (Tracking) - optional, but good to avoid errors
    omega.golf.start_job = MagicMock()
    omega.golf.update_progress = MagicMock()
    omega.golf.finish_job = MagicMock()
    
    # 3. Run Job
    logger.info("Starting Job...")
    result = await omega.start_job("TestTheme")
    
    # 4. Verify Results
    logger.info("Job Finished. Verifying results...")
    
    # Check generated images
    # TARGET_PAGES=1,50 → cover front + cover back (both page_number 1) + certificate
    calls = omega.charlie.generate_image.call_args_list
    logger.info(f"Agent Charlie called {len(calls)} times.")

    page_nums = [call[0][2] for call in calls]
    expected = ["CoverFront", "CoverBack", "50"]
    if page_nums != expected:
        logger.error(f"FAILED: Expected page ids {expected}, got {page_nums}")
        for i, call in enumerate(calls):
            logger.error(f"Call {i}: {call}")
        sys.exit(1)

    # Verify the assembler received explicit page metadata (not bare paths)
    (assemble_args, assemble_kwargs) = omega.echo.assemble_pdf.call_args
    pages = assemble_args[0]
    assert all(isinstance(pg, dict) for pg in pages), f"Expected page dicts, got: {pages}"
    types = {pg["page_type"] for pg in pages}
    if types != {"cover_front", "cover_back", "certificate"}:
        logger.error(f"FAILED: Expected cover_front+cover_back+certificate, got {types}")
        sys.exit(1)
    if "cover_text" not in assemble_kwargs:
        logger.error("FAILED: assemble_pdf not given cover_text")
        sys.exit(1)

    logger.info("SUCCESS: Verified Cover (front+back) and Page 50 were generated.")

if __name__ == "__main__":
    asyncio.run(run_test())
