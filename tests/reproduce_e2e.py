
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
    
    # Mock Agent Charlie (Image Generator)
    omega.charlie.generate_image = MagicMock(side_effect=lambda prompt, theme, page_num: f"temp/test_{page_num}.png")
    
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
    omega.bravo.generate_cover = MagicMock(return_value="cover_prompt")
    
    # Mock Agent Delta (QA)
    omega.delta.quality_check = MagicMock(return_value=True)
    
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
    # We expect 2 images: Cover (Page 1) and Certificate (Page 50)
    # Based on my code changes:
    # Cover -> page_number=1 -> "Cover" (handled in orchestrator) -> "temp/test_Cover.png"
    # Cert -> page_number=50 -> "50" -> "temp/test_50.png"
    
    expected_calls = [
        ("temp/test_Cover.png", "Cover"),
        ("temp/test_50.png", "50")
    ]
    
    # Check actual calls to generate_image
    # call_args_list is a list of calls. Each call is (args, kwargs).
    # args: (prompt, theme, page_num_str)
    
    calls = omega.charlie.generate_image.call_args_list
    logger.info(f"Agent Charlie called {len(calls)} times.")
    
    if len(calls) != 2:
        logger.error(f"FAILED: Expected 2 calls, got {len(calls)}")
        for i, call in enumerate(calls):
            logger.error(f"Call {i}: {call}")
        sys.exit(1)
        
    # Verify Call 1 (Cover)
    args1, _ = calls[0]
    # args1[2] is page_num_str
    if args1[2] != "Cover":
         logger.error(f"FAILED: Call 1 expected page_num='Cover', got '{args1[2]}'")
         sys.exit(1)
         
    # Verify Call 2 (Certificate)
    args2, _ = calls[1]
    if args2[2] != "50":
         logger.error(f"FAILED: Call 2 expected page_num='50', got '{args2[2]}'")
         sys.exit(1)

    logger.info("SUCCESS: Verified Cover and Page 50 were generated.")

if __name__ == "__main__":
    asyncio.run(run_test())
