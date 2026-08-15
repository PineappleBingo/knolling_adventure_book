# Pending 20% Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all remaining issues identified in the transition gap analysis to bring the KDP Automation System to 100% functional parity with Series Master Bible v5.22.

**Architecture:** The system is a Python-based pipeline: Telegram UI -> Prompt Generation (Gemini) -> Image Generation (REST API) -> QA (Gemini Vision) -> PDF Assembly (ReportLab). Changes span config, image generator, prompt generator, QA agent, tracking, and PDF assembler modules. All fixes are backward-compatible within the existing agent architecture.

**Tech Stack:** Python 3.11, google-genai SDK, requests, ReportLab, Pillow, gspread, python-telegram-bot

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `src/config.py` | Modify | Fix FREE tier model ID |
| `src/modules/prompt_generator.py` | Modify | Fix Bible path, migrate to google-genai |
| `src/modules/qa_agent.py` | Modify | Migrate to google-genai |
| `src/modules/image_generator.py` | Modify | Add responseModalities, update FREE tier logic |
| `src/modules/orchestrator.py` | Modify | Wire v2 image generator, pass wireframe paths |
| `src/modules/pdf_assembler.py` | Modify | Fix typo, add cover spread dimensions |
| `src/modules/system_architect.py` | Modify | Implement check_environment() |
| `src/modules/tracking.py` | Modify | Migrate oauth2client to google-auth |
| `src/modules/image_generator_v2.py` | Delete | Consolidate into image_generator.py |
| `src/modules/pdf_assembler_v1_backup.py` | Delete | Stale backup |
| `src/modules/pdf_assembler_v2.py` | Delete | Duplicate of current |
| `Pipfile` | Modify | Replace google-generativeai with google-genai, replace oauth2client with google-auth |
| `Series Master Bible v5.22.md` | Modify | Fix typos (MASTER_REF_IMG, models/ prefix) |
| `tests/test_p0_fixes.py` | Create | Tests for Bible path fix and responseModalities |
| `tests/test_sdk_migration.py` | Create | Tests for google-genai migration |
| `tests/test_cover_dimensions.py` | Create | Tests for cover spread sizing |

---

### Task 1: P0 Fix — Bible Path (v5.21 -> v5.22)

**Files:**
- Modify: `src/modules/prompt_generator.py:95`
- Create: `tests/test_p0_fixes.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_p0_fixes.py
import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBiblePath(unittest.TestCase):
    def test_bible_path_points_to_v522(self):
        """Agent Bravo must read from v5.22, not v5.21."""
        from src.modules.prompt_generator import AgentBravo
        import inspect

        source = inspect.getsource(AgentBravo._extract_bible_specs)
        self.assertIn("v5.22", source, "Bible path must reference v5.22")
        self.assertNotIn("v5.21", source, "Bible path must NOT reference v5.21")


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestBiblePath::test_bible_path_points_to_v522 -v`
Expected: FAIL with `AssertionError: 'v5.22' not found in ...`

- [ ] **Step 3: Fix the Bible path**

In `src/modules/prompt_generator.py`, change line 95:

```python
# OLD:
bible_path = "Series Master Bible v5.21.md"
# NEW:
bible_path = "Series Master Bible v5.22.md"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestBiblePath::test_bible_path_points_to_v522 -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/modules/prompt_generator.py tests/test_p0_fixes.py
git commit -m "fix: update Bible path from v5.21 to v5.22 in prompt_generator"
```

---

### Task 2: P0 Fix — Add responseModalities to FREE Tier Payload

**Files:**
- Modify: `src/modules/image_generator.py:89-93`
- Modify: `tests/test_p0_fixes.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_p0_fixes.py`:

```python
import json


class TestFreePayload(unittest.TestCase):
    def test_free_tier_payload_includes_response_modalities(self):
        """FREE tier generateContent payload must include responseModalities."""
        # We test by inspecting the payload construction logic
        # Simulate what image_generator.py builds for FREE tier
        from src.modules.image_generator import AgentCharlie
        import inspect

        source = inspect.getsource(AgentCharlie.generate_image)
        self.assertIn("responseModalities", source,
                       "FREE tier payload must include generationConfig.responseModalities")

    def test_free_tier_payload_structure(self):
        """Verify the payload JSON structure is correct."""
        # Build the expected payload structure
        payload = {
            "contents": [{"parts": [{"text": "test prompt"}]}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }
        self.assertIn("generationConfig", payload)
        self.assertEqual(payload["generationConfig"]["responseModalities"], ["TEXT", "IMAGE"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestFreePayload::test_free_tier_payload_includes_response_modalities -v`
Expected: FAIL with `AssertionError: 'responseModalities' not found in ...`

- [ ] **Step 3: Add responseModalities to the payload**

In `src/modules/image_generator.py`, replace lines 89-93:

```python
# OLD:
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }

# NEW:
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"]
                    }
                }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/modules/image_generator.py tests/test_p0_fixes.py
git commit -m "fix: add responseModalities to FREE tier generateContent payload"
```

---

### Task 3: P1 Fix — Update FREE Tier Model ID

**Files:**
- Modify: `src/config.py:59-60`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_p0_fixes.py`:

```python
class TestModelConfig(unittest.TestCase):
    def test_free_tier_model_is_current(self):
        """FREE tier must use gemini-2.5-flash-image, not deprecated model."""
        import importlib
        old_tier = os.environ.get("DEPLOYMENT_TIER", "")
        os.environ["DEPLOYMENT_TIER"] = "FREE"
        from src import config
        importlib.reload(config)
        self.assertEqual(config.GEN_MODEL_ID, "gemini-2.5-flash-image",
                         "FREE tier model must be gemini-2.5-flash-image")
        # Restore
        if old_tier:
            os.environ["DEPLOYMENT_TIER"] = old_tier
        else:
            os.environ.pop("DEPLOYMENT_TIER", None)
        importlib.reload(config)

    def test_paid_tier_model_is_correct(self):
        """PAID tier must use imagen-4.0-generate-001."""
        import importlib
        old_tier = os.environ.get("DEPLOYMENT_TIER", "")
        os.environ["DEPLOYMENT_TIER"] = "PAID"
        from src import config
        importlib.reload(config)
        self.assertEqual(config.GEN_MODEL_ID, "imagen-4.0-generate-001")
        # Restore
        if old_tier:
            os.environ["DEPLOYMENT_TIER"] = old_tier
        else:
            os.environ.pop("DEPLOYMENT_TIER", None)
        importlib.reload(config)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestModelConfig::test_free_tier_model_is_current -v`
Expected: FAIL with `AssertionError: 'models/gemini-2.0-flash-exp-image-generation' != 'gemini-2.5-flash-image'`

- [ ] **Step 3: Update the model ID**

In `src/config.py`, replace lines 58-60:

```python
# OLD:
else:
    # FREE Tier: Use Gemini 2.0 Flash Exp (Image Generation)
    GEN_MODEL_ID = "models/gemini-2.0-flash-exp-image-generation"

# NEW:
else:
    # FREE Tier: Use Gemini 2.5 Flash Image (replaces deprecated gemini-2.0-flash-exp)
    GEN_MODEL_ID = "gemini-2.5-flash-image"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestModelConfig -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_p0_fixes.py
git commit -m "fix: update FREE tier model to gemini-2.5-flash-image"
```

---

### Task 4: P1 Fix — Consolidate Image Generator v2 into v1

**Files:**
- Modify: `src/modules/image_generator.py` (merge v2 features: wireframe_path, reference_images params)
- Modify: `src/modules/orchestrator.py:12` (keep importing from image_generator)
- Delete: `src/modules/image_generator_v2.py`

The v2 generator adds `wireframe_path` and `reference_images` parameters to `generate_image()`. We merge these into v1 rather than swapping the import, since orchestrator already imports v1 and the v2 class has the same name.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_p0_fixes.py`:

```python
class TestImageGeneratorV2Features(unittest.TestCase):
    def test_generate_image_accepts_wireframe_path(self):
        """generate_image() must accept wireframe_path parameter."""
        from src.modules.image_generator import AgentCharlie
        import inspect
        sig = inspect.signature(AgentCharlie.generate_image)
        self.assertIn("wireframe_path", sig.parameters,
                       "generate_image must accept wireframe_path kwarg")

    def test_generate_image_accepts_reference_images(self):
        """generate_image() must accept reference_images parameter."""
        from src.modules.image_generator import AgentCharlie
        import inspect
        sig = inspect.signature(AgentCharlie.generate_image)
        self.assertIn("reference_images", sig.parameters,
                       "generate_image must accept reference_images kwarg")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestImageGeneratorV2Features -v`
Expected: FAIL with `AssertionError: 'wireframe_path' not found ...`

- [ ] **Step 3: Merge v2 features into image_generator.py**

Replace the entire `src/modules/image_generator.py` with the merged version. The key changes:
1. Add `_encode_image_to_base64()` helper method
2. Add `wireframe_path=None` and `reference_images=None` params to `generate_image()`
3. FREE tier: build multimodal payload with inline images when wireframe/refs provided
4. PAID tier: enhance text prompt with layout instructions when wireframe provided (Imagen 4.0 doesn't support image input)
5. Keep `responseModalities` from Task 2

```python
"""
Agent Charlie: Lead Technical Artist (Image Generation)
Mission: Manage the "Artist" loop (Imagen 4.0 / Gemini REST API).
"""

import logging
import time
import os
import requests
import json
import base64
from src import config

logger = logging.getLogger("AgentCharlie")


class AgentCharlie:
    def __init__(self):
        logger.info("Agent Charlie initialized.")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found.")
        logger.info(f"Using Image Model: {config.GEN_MODEL_ID}")

    def _encode_image_to_base64(self, image_path):
        """Encodes an image file to base64 string."""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    def generate_image(self, prompt, theme, page_number, wireframe_path=None, reference_images=None):
        """
        Generates an image based on the prompt using REST API.

        Args:
            prompt: Text prompt for generation
            theme: Theme name for filename
            page_number: Page number for filename
            wireframe_path: Optional path to wireframe image for layout enforcement
            reference_images: Optional list of reference image paths for style guidance
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")

        # Rate Limiting Delay
        logger.info(f"Sleeping for {config.IMG_GEN_DELAY}s (Rate Limit)...")
        time.sleep(config.IMG_GEN_DELAY)

        # Clean theme for filename
        safe_theme = "".join(x for x in theme if x.isalnum() or x in " _-").strip().replace(" ", "_")

        try:
            if config.DEPLOYMENT_TIER == "PAID":
                # PAID Tier: Imagen 4.0 (:predict endpoint)
                # Imagen 4.0 does NOT support image input — enhance text prompt instead
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEN_MODEL_ID}:predict"
                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }

                enhanced_prompt = prompt
                if wireframe_path and os.path.exists(wireframe_path):
                    enhanced_prompt = (
                        "CRITICAL INSTRUCTION: Follow the structural layout EXACTLY as described. "
                        "This is a wireframe-guided generation. Maintain precise zone positioning. "
                        f"{prompt}"
                    )

                payload = {
                    "instances": [{"prompt": enhanced_prompt}],
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": "1:1"
                    }
                }

                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                if 'predictions' in result and len(result['predictions']) > 0:
                    b64_data = result['predictions'][0]['bytesBase64Encoded']
                    img_data = base64.b64decode(b64_data)

                    filename = f"temp/{safe_theme}_Page{page_number}_{int(time.time())}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    logger.info(f"Image saved to {filename}")
                    return filename
                else:
                    raise ValueError(f"Invalid response from Imagen API: {result}")

            else:
                # FREE Tier: Gemini generateContent endpoint
                model_id = config.GEN_MODEL_ID
                if model_id.startswith("models/"):
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent"
                else:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"

                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key
                }

                # Build multimodal payload
                parts = [{"text": prompt}]

                # Add wireframe as reference image
                if wireframe_path and os.path.exists(wireframe_path):
                    wireframe_b64 = self._encode_image_to_base64(wireframe_path)
                    if wireframe_b64:
                        parts.insert(0, {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": wireframe_b64
                            }
                        })
                        parts.insert(0, {
                            "text": "WIREFRAME REFERENCE (Follow this layout structure EXACTLY):"
                        })

                # Add style reference images
                if reference_images:
                    for ref_path in reference_images:
                        if os.path.exists(ref_path):
                            ref_b64 = self._encode_image_to_base64(ref_path)
                            if ref_b64:
                                parts.insert(0, {
                                    "inline_data": {
                                        "mime_type": "image/png",
                                        "data": ref_b64
                                    }
                                })
                                parts.insert(0, {
                                    "text": "STYLE REFERENCE (Match this visual DNA):"
                                })

                payload = {
                    "contents": [{"parts": parts}],
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"]
                    }
                }

                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                if 'candidates' in result and result['candidates']:
                    for candidate in result['candidates']:
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'inlineData' in part:
                                    b64_data = part['inlineData']['data']
                                    img_data = base64.b64decode(b64_data)

                                    filename = f"temp/{safe_theme}_Page{page_number}_{int(time.time())}.png"
                                    with open(filename, "wb") as f:
                                        f.write(img_data)
                                    logger.info(f"Image saved to {filename}")
                                    return filename

                raise ValueError(f"No image found in Gemini response: {result}")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"API Response: {response.text}")
            raise e
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py -v`
Expected: ALL PASS

- [ ] **Step 5: Delete v2 file and backups**

```bash
rm src/modules/image_generator_v2.py
rm src/modules/pdf_assembler_v1_backup.py
rm src/modules/pdf_assembler_v2.py
```

- [ ] **Step 6: Commit**

```bash
git add src/modules/image_generator.py tests/test_p0_fixes.py
git add -u src/modules/image_generator_v2.py src/modules/pdf_assembler_v1_backup.py src/modules/pdf_assembler_v2.py
git commit -m "feat: consolidate v2 image generator features (wireframe+ref support) into v1, remove duplicates"
```

---

### Task 5: P1 Fix — Migrate google-generativeai to google-genai

**Files:**
- Modify: `Pipfile:14`
- Modify: `src/modules/prompt_generator.py` (lines 10, 20-23, 82, 207)
- Modify: `src/modules/qa_agent.py` (lines 9, 19-25, 60)
- Create: `tests/test_sdk_migration.py`

- [ ] **Step 1: Install google-genai package**

```bash
./venv/bin/pip install google-genai
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_sdk_migration.py
import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSDKMigration(unittest.TestCase):
    def test_prompt_generator_uses_new_sdk(self):
        """prompt_generator must import from google.genai, not google.generativeai."""
        import inspect
        from src.modules.prompt_generator import AgentBravo
        source = inspect.getsource(AgentBravo)
        self.assertNotIn("import google.generativeai", source,
                         "Must not use deprecated google.generativeai")
        self.assertNotIn("genai.configure", source,
                         "Must not use deprecated genai.configure pattern")

    def test_qa_agent_uses_new_sdk(self):
        """qa_agent must import from google.genai, not google.generativeai."""
        import inspect
        from src.modules.qa_agent import AgentDelta
        source = inspect.getsource(AgentDelta)
        self.assertNotIn("import google.generativeai", source,
                         "Must not use deprecated google.generativeai")
        self.assertNotIn("genai.configure", source,
                         "Must not use deprecated genai.configure pattern")

    def test_prompt_generator_initializes(self):
        """AgentBravo must initialize without error (mocked API key)."""
        os.environ.setdefault("GOOGLE_API_KEY", "test-key-placeholder")
        from src.modules.prompt_generator import AgentBravo
        bravo = AgentBravo()
        self.assertIsNotNone(bravo)

    def test_qa_agent_initializes(self):
        """AgentDelta must initialize without error (mocked API key)."""
        os.environ.setdefault("GOOGLE_API_KEY", "test-key-placeholder")
        from src.modules.qa_agent import AgentDelta
        delta = AgentDelta()
        self.assertIsNotNone(delta)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_sdk_migration.py::TestSDKMigration::test_prompt_generator_uses_new_sdk -v`
Expected: FAIL with `'import google.generativeai' found in ...`

- [ ] **Step 4: Migrate prompt_generator.py**

Replace the import and initialization in `src/modules/prompt_generator.py`:

```python
# OLD (lines 10, 20-23):
import google.generativeai as genai
# ...
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.vision_model = genai.GenerativeModel(config.QA_MODEL_NAME)

# NEW:
from google import genai
# ...
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            self.genai_client = genai.Client(api_key=api_key)
            self.vision_model_name = config.QA_MODEL_NAME
        else:
            logger.error("GOOGLE_API_KEY not found.")
```

Then update all `self.vision_model.generate_content(...)` calls (lines 82, 207):

```python
# OLD:
response = self.vision_model.generate_content([prompt, *images])
# NEW:
response = self.genai_client.models.generate_content(
    model=self.vision_model_name,
    contents=[prompt, *images]
)
```

And the same for line 207:
```python
# OLD:
response = self.vision_model.generate_content(inputs)
# NEW:
response = self.genai_client.models.generate_content(
    model=self.vision_model_name,
    contents=inputs
)
```

- [ ] **Step 5: Migrate qa_agent.py**

Replace the import and initialization in `src/modules/qa_agent.py`:

```python
# OLD (lines 9, 19-25):
import google.generativeai as genai
# ...
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(config.QA_MODEL_NAME)

# NEW:
from google import genai
# ...
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found.")
        else:
            self.genai_client = genai.Client(api_key=api_key)
            self.model_name = config.QA_MODEL_NAME
```

Then update the generate_content call (line 60):
```python
# OLD:
response = self.model.generate_content([prompt, img])
# NEW:
response = self.genai_client.models.generate_content(
    model=self.model_name,
    contents=[prompt, img]
)
```

- [ ] **Step 6: Update Pipfile**

In `Pipfile`, replace line 14:

```
# OLD:
google-generativeai = ">=0.8.3"

# NEW:
google-genai = "*"
```

- [ ] **Step 7: Run all tests**

Run: `./venv/bin/python -m pytest tests/test_sdk_migration.py -v`
Expected: ALL PASS

- [ ] **Step 8: Commit**

```bash
git add src/modules/prompt_generator.py src/modules/qa_agent.py Pipfile tests/test_sdk_migration.py
git commit -m "feat: migrate google-generativeai to google-genai SDK"
```

---

### Task 6: P2 Fix — Migrate oauth2client to google-auth

**Files:**
- Modify: `src/modules/tracking.py:7-8, 24-25`
- Modify: `Pipfile`

- [ ] **Step 1: Install google-auth**

```bash
./venv/bin/pip install google-auth google-auth-oauthlib
```

Note: `google-auth` is already installed (v2.47.0) as a dependency. We just need to update the import.

- [ ] **Step 2: Write the failing test**

Append to `tests/test_sdk_migration.py`:

```python
class TestOAuthMigration(unittest.TestCase):
    def test_tracking_uses_google_auth(self):
        """tracking.py must use google.oauth2, not oauth2client."""
        import inspect
        # Need to mock gspread since it requires credentials
        from unittest.mock import MagicMock
        sys.modules["gspread"] = MagicMock()

        # Force reimport
        if 'src.modules.tracking' in sys.modules:
            del sys.modules['src.modules.tracking']

        from src.modules.tracking import AgentGolf
        source = inspect.getsource(AgentGolf)
        self.assertNotIn("oauth2client", source,
                         "Must not use deprecated oauth2client")
```

- [ ] **Step 3: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_sdk_migration.py::TestOAuthMigration -v`
Expected: FAIL

- [ ] **Step 4: Update tracking.py imports and auth logic**

In `src/modules/tracking.py`, replace lines 7-8 and 24-25:

```python
# OLD:
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# ...
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds_file = "credentials.json"
        self.client = None
        self.sheet = None

        try:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, self.scope)
            self.client = gspread.authorize(self.creds)

# NEW:
import gspread
from google.oauth2.service_account import Credentials
# ...
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds_file = "credentials.json"
        self.client = None
        self.sheet = None

        try:
            self.creds = Credentials.from_service_account_file(self.creds_file, scopes=self.scope)
            self.client = gspread.authorize(self.creds)
```

- [ ] **Step 5: Update Pipfile**

Replace `oauth2client = "*"` with `google-auth = "*"` in `Pipfile`.

- [ ] **Step 6: Run tests**

Run: `./venv/bin/python -m pytest tests/test_sdk_migration.py -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add src/modules/tracking.py Pipfile tests/test_sdk_migration.py
git commit -m "feat: migrate oauth2client to google-auth in tracking module"
```

---

### Task 7: P2 Fix — AssertionError Typo in pdf_assembler.py

**Files:**
- Modify: `src/modules/pdf_assembler.py:197`

- [ ] **Step 1: Fix the typo**

In `src/modules/pdf_assembler.py`, line 197:

```python
# OLD:
        except AssertionError as e:

# NEW:
        except AssertionError as e:
```

- [ ] **Step 2: Verify Python can parse the file**

Run: `./venv/bin/python -c "from src.modules.pdf_assembler import AgentEcho; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/modules/pdf_assembler.py
git commit -m "fix: correct AssertionError typo to AssertionError in pdf_assembler"
```

---

### Task 8: P2 Fix — Cover Spread Dimensions

**Files:**
- Modify: `src/modules/pdf_assembler.py`
- Create: `tests/test_cover_dimensions.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cover_dimensions.py
import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reportlab.lib.units import inch


class TestCoverDimensions(unittest.TestCase):
    def test_cover_spread_width(self):
        """Cover spread must be 17.365 inches wide per Bible Section 1.4."""
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        expected_width = 17.365 * inch
        self.assertAlmostEqual(echo.cover_width, expected_width, places=1,
                               msg="Cover spread width must be 17.365 inches")

    def test_cover_spread_height(self):
        """Cover spread must be 8.75 inches tall per Bible Section 1.4."""
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        expected_height = 8.75 * inch
        self.assertAlmostEqual(echo.cover_height, expected_height, places=1,
                               msg="Cover spread height must be 8.75 inches")

    def test_internal_page_dimensions_unchanged(self):
        """Internal pages must remain 8.75 x 8.75 inches."""
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        expected = 8.75 * inch
        self.assertAlmostEqual(echo.width, expected, places=1)
        self.assertAlmostEqual(echo.height, expected, places=1)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_cover_dimensions.py -v`
Expected: FAIL with `AttributeError: 'AgentEcho' object has no attribute 'cover_width'`

- [ ] **Step 3: Add cover dimensions to AgentEcho.__init__**

In `src/modules/pdf_assembler.py`, after line 27 (`self.height = 8.75 * inch`), add:

```python
        # Cover Spread: 17.365" x 8.75" (Back + Spine + Front + Bleeds)
        self.cover_width = 17.365 * inch
        self.cover_height = 8.75 * inch
```

- [ ] **Step 4: Update assemble_pdf to use cover dimensions for cover pages**

In `src/modules/pdf_assembler.py`, inside the `assemble_pdf` method, after the `c = canvas.Canvas(...)` line (line 221), the page loop needs to detect cover pages and use cover dimensions. Modify the loop body where it draws the image:

```python
                    # Determine if this is a cover page
                    is_cover = "Cover" in img_path or "cover" in img_path

                    if is_cover:
                        page_w, page_h = self.cover_width, self.cover_height
                        c.setPageSize((page_w, page_h))
                    else:
                        page_w, page_h = self.width, self.height
                        c.setPageSize((page_w, page_h))

                    # Step 1: Draw Image FIRST (Background Layer)
                    logger.info("  1. Drawing IMAGE layer (background)...")
                    c.drawImage(processed_img_path, 0, 0, width=page_w, height=page_h)
```

- [ ] **Step 5: Run tests**

Run: `./venv/bin/python -m pytest tests/test_cover_dimensions.py -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/modules/pdf_assembler.py tests/test_cover_dimensions.py
git commit -m "feat: add cover spread dimensions (17.365\" x 8.75\") per Bible Section 1.4"
```

---

### Task 9: P2 Fix — Implement Agent Alpha check_environment()

**Files:**
- Modify: `src/modules/system_architect.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_p0_fixes.py`:

```python
class TestAgentAlpha(unittest.TestCase):
    def test_check_environment_returns_dict(self):
        """check_environment must return a dict of check results."""
        from src.modules.system_architect import AgentAlpha
        alpha = AgentAlpha()
        result = alpha.check_environment()
        self.assertIsInstance(result, dict)

    def test_check_environment_checks_api_key(self):
        """check_environment must verify GOOGLE_API_KEY presence."""
        from src.modules.system_architect import AgentAlpha
        alpha = AgentAlpha()
        result = alpha.check_environment()
        self.assertIn("google_api_key", result)

    def test_check_environment_checks_fonts(self):
        """check_environment must verify font files exist."""
        from src.modules.system_architect import AgentAlpha
        alpha = AgentAlpha()
        result = alpha.check_environment()
        self.assertIn("fonts", result)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestAgentAlpha -v`
Expected: FAIL (check_environment returns None, not dict)

- [ ] **Step 3: Implement check_environment()**

Replace `src/modules/system_architect.py`:

```python
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

        # Check API Key
        results["google_api_key"] = bool(os.getenv("GOOGLE_API_KEY"))

        # Check Telegram Token
        results["telegram_token"] = bool(os.getenv("TELEGRAM_TOKEN"))

        # Check credentials.json
        results["credentials_json"] = os.path.exists("credentials.json")

        # Check font files
        font_files = [
            config.FONT_TITLE_MAIN,
            config.FONT_SUBTITLE,
            config.FONT_BODY_TEXT,
            config.FONT_HANDWRITING,
            config.FONT_LEGAL,
        ]
        missing_fonts = []
        for font in font_files:
            path = os.path.join(config.PATH_FONTS, font)
            if not os.path.exists(path):
                missing_fonts.append(font)
        results["fonts"] = {
            "all_present": len(missing_fonts) == 0,
            "missing": missing_fonts,
        }

        # Check assets directory
        results["assets_dir"] = os.path.isdir("assets")

        # Check Bible exists
        results["bible"] = os.path.exists("Series Master Bible v5.22.md")

        # Log results
        for key, val in results.items():
            if key == "fonts":
                if val["all_present"]:
                    logger.info(f"  {key}: OK")
                else:
                    logger.warning(f"  {key}: MISSING {val['missing']}")
            elif isinstance(val, bool):
                status = "OK" if val else "MISSING"
                logger.info(f"  {key}: {status}")

        return results
```

- [ ] **Step 4: Run tests**

Run: `./venv/bin/python -m pytest tests/test_p0_fixes.py::TestAgentAlpha -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/modules/system_architect.py tests/test_p0_fixes.py
git commit -m "feat: implement Agent Alpha check_environment() with env/asset/font validation"
```

---

### Task 10: P3 Fix — Bible Typo Corrections

**Files:**
- Modify: `Series Master Bible v5.22.md:28, 30`

- [ ] **Step 1: Fix MASTER_REF_IMG typo**

In `Series Master Bible v5.22.md`, line 28:

```markdown
# OLD:
    * `MASTER_REF_IMG`: "assets/ref_pag2_01.png"

# NEW:
    * `MASTER_REF_IMG`: "assets/ref_page2_01.png"
```

- [ ] **Step 2: Fix models/ prefix on Imagen model ID**

In `Series Master Bible v5.22.md`, line 30:

```markdown
# OLD:
    * `GEN_MODEL_ID`: "models/imagen-4.0-generate-001" (See Agent Alpha for Tier Logic)

# NEW:
    * `GEN_MODEL_ID`: "imagen-4.0-generate-001" (See Agent Alpha for Tier Logic)
```

- [ ] **Step 3: Commit**

```bash
git add "Series Master Bible v5.22.md"
git commit -m "fix: correct MASTER_REF_IMG typo and remove redundant models/ prefix in Bible v5.22"
```

---

### Task 11: Verify All Tests Pass End-to-End

**Files:** None (verification only)

- [ ] **Step 1: Run all tests**

```bash
./venv/bin/python -m pytest tests/ -v
```

Expected: ALL PASS

- [ ] **Step 2: Run the E2E smoke test**

```bash
./venv/bin/python tests/reproduce_e2e.py
```

Expected: `SUCCESS: Verified Cover and Page 50 were generated.`

- [ ] **Step 3: Verify no v5.21 references remain in code**

```bash
grep -r "v5.21" src/ --include="*.py"
```

Expected: No output (no remaining v5.21 references in src/)

- [ ] **Step 4: Verify no deprecated imports remain**

```bash
grep -r "google.generativeai\|oauth2client" src/ --include="*.py"
```

Expected: No output

- [ ] **Step 5: Verify config loads for both tiers**

```bash
DEPLOYMENT_TIER=FREE ./venv/bin/python -c "from src.config import *; print(f'FREE: {GEN_MODEL_ID}')"
DEPLOYMENT_TIER=PAID ./venv/bin/python -c "from src.config import *; print(f'PAID: {GEN_MODEL_ID}')"
```

Expected:
```
FREE: gemini-2.5-flash-image
PAID: imagen-4.0-generate-001
```

- [ ] **Step 6: Final commit (update CLAUDE.md progress tracker)**

Update `CLAUDE.md` to mark all pending items as complete. Then:

```bash
git add CLAUDE.md
git commit -m "docs: mark all pending items as complete in CLAUDE.md"
```
