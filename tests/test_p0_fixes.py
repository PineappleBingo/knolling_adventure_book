"""
Tests for P0/P1 quick fixes:
  1. Bible path in prompt_generator.py references v5.22
  2. image_generator.py FREE tier payload includes responseModalities
  3. FREE tier config produces model ID "gemini-2.5-flash-image"
  4. PAID tier config produces model ID "imagen-4.0-generate-001"
"""

import importlib
import inspect
import os
import sys
import types


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_source(module_path: str) -> str:
    """Return the raw source text of a module given its file path."""
    with open(module_path, "r", encoding="utf-8") as f:
        return f.read()


# Absolute paths to the source files under test
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROMPT_GENERATOR_PATH = os.path.join(REPO_ROOT, "src", "modules", "prompt_generator.py")
IMAGE_GENERATOR_PATH  = os.path.join(REPO_ROOT, "src", "modules", "image_generator.py")
CONFIG_PATH           = os.path.join(REPO_ROOT, "src", "config.py")


# ---------------------------------------------------------------------------
# Task 1: Bible path references v5.22
# ---------------------------------------------------------------------------

class TestBiblePath:
    def test_bible_path_is_v522(self):
        """prompt_generator.py must reference Series Master Bible v5.22, not v5.21."""
        source = _get_source(PROMPT_GENERATOR_PATH)
        assert "Series Master Bible v5.22.md" in source, (
            "Expected 'Series Master Bible v5.22.md' in prompt_generator.py"
        )

    def test_bible_path_not_v521(self):
        """prompt_generator.py must NOT reference the outdated v5.21 bible."""
        source = _get_source(PROMPT_GENERATOR_PATH)
        assert "Series Master Bible v5.21.md" not in source, (
            "Found stale 'Series Master Bible v5.21.md' reference in prompt_generator.py"
        )

    def test_bible_path_via_inspect(self):
        """Cross-check using inspect.getsource on the _extract_bible_specs method."""
        # Add src to path so we can import the module
        src_path = os.path.join(REPO_ROOT, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        # Import without triggering heavy side-effects if possible
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "prompt_generator", PROMPT_GENERATOR_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        # Provide a minimal stub so the module can be loaded in isolation
        sys.modules.setdefault("prompt_generator", mod)
        try:
            spec.loader.exec_module(mod)
        except Exception:
            pass  # tolerate import errors from missing deps; source is what we need

        # Use inspect.getsource on the class method if available
        klass = getattr(mod, "PromptGenerator", None)
        if klass is not None:
            method = getattr(klass, "_extract_bible_specs", None)
            if method is not None:
                src = inspect.getsource(method)
                assert "v5.22" in src, (
                    "inspect.getsource(_extract_bible_specs) does not contain 'v5.22'"
                )
                return
        # Fallback: source-file check already passed in previous tests
        source = _get_source(PROMPT_GENERATOR_PATH)
        assert "v5.22" in source


# ---------------------------------------------------------------------------
# Task 2: responseModalities present in image_generator.py
# ---------------------------------------------------------------------------

class TestResponseModalities:
    def test_response_modalities_present(self):
        """FREE tier payload in image_generator.py must include responseModalities."""
        source = _get_source(IMAGE_GENERATOR_PATH)
        assert "responseModalities" in source, (
            "Expected 'responseModalities' key in image_generator.py FREE tier payload"
        )

    def test_response_modalities_values(self):
        """responseModalities must include both TEXT and IMAGE."""
        source = _get_source(IMAGE_GENERATOR_PATH)
        assert '"TEXT"' in source or "'TEXT'" in source, (
            "Expected 'TEXT' in responseModalities list"
        )
        assert '"IMAGE"' in source or "'IMAGE'" in source, (
            "Expected 'IMAGE' in responseModalities list"
        )

    def test_generation_config_present(self):
        """The payload must include a generationConfig wrapper."""
        source = _get_source(IMAGE_GENERATOR_PATH)
        assert "generationConfig" in source, (
            "Expected 'generationConfig' block in image_generator.py FREE tier payload"
        )


# ---------------------------------------------------------------------------
# Task 3: Model IDs in config.py
# ---------------------------------------------------------------------------

class TestModelIDs:
    def _load_config(self, tier: str) -> types.ModuleType:
        """Load src/config.py with DEPLOYMENT_TIER forced to *tier*."""
        old_tier = os.environ.get("DEPLOYMENT_TIER")
        os.environ["DEPLOYMENT_TIER"] = tier
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("_config_under_test", CONFIG_PATH)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            if old_tier is None:
                os.environ.pop("DEPLOYMENT_TIER", None)
            else:
                os.environ["DEPLOYMENT_TIER"] = old_tier
        return mod

    def test_free_tier_model_id(self):
        """FREE tier config must produce model ID 'gemini-2.5-flash-image'."""
        config = self._load_config("FREE")
        assert config.GEN_MODEL_ID == "gemini-2.5-flash-image", (
            f"FREE tier GEN_MODEL_ID is '{config.GEN_MODEL_ID}', "
            "expected 'gemini-2.5-flash-image'"
        )

    def test_free_tier_model_not_deprecated(self):
        """FREE tier must NOT use the deprecated gemini-2.0-flash-exp model."""
        config = self._load_config("FREE")
        assert "gemini-2.0-flash-exp" not in config.GEN_MODEL_ID, (
            "FREE tier is still using the deprecated gemini-2.0-flash-exp model"
        )

    def test_paid_tier_model_id(self):
        """PAID tier config must produce model ID 'imagen-4.0-generate-001'."""
        config = self._load_config("PAID")
        assert config.GEN_MODEL_ID == "imagen-4.0-generate-001", (
            f"PAID tier GEN_MODEL_ID is '{config.GEN_MODEL_ID}', "
            "expected 'imagen-4.0-generate-001'"
        )


# ---------------------------------------------------------------------------
# Task 4: AgentCharlie v2 features merged into image_generator.py
# ---------------------------------------------------------------------------

class TestAgentCharlieV2Features:
    """Verify that v2 features (wireframe_path, reference_images, _encode_image_to_base64)
    have been merged into the main image_generator.py (AgentCharlie v1)."""

    def _load_agent_charlie(self):
        """Load AgentCharlie from image_generator.py without triggering API calls."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_agent_charlie_under_test", IMAGE_GENERATOR_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception:
            pass  # tolerate missing env vars at import time
        return getattr(mod, "AgentCharlie", None)

    def test_generate_image_accepts_wireframe_path(self):
        """AgentCharlie.generate_image must accept a wireframe_path keyword argument."""
        klass = self._load_agent_charlie()
        assert klass is not None, "AgentCharlie class not found in image_generator.py"
        sig = inspect.signature(klass.generate_image)
        assert "wireframe_path" in sig.parameters, (
            "generate_image() is missing 'wireframe_path' parameter"
        )
        param = sig.parameters["wireframe_path"]
        assert param.default is None, (
            "wireframe_path default must be None"
        )

    def test_generate_image_accepts_reference_images(self):
        """AgentCharlie.generate_image must accept a reference_images keyword argument."""
        klass = self._load_agent_charlie()
        assert klass is not None, "AgentCharlie class not found in image_generator.py"
        sig = inspect.signature(klass.generate_image)
        assert "reference_images" in sig.parameters, (
            "generate_image() is missing 'reference_images' parameter"
        )
        param = sig.parameters["reference_images"]
        assert param.default is None, (
            "reference_images default must be None"
        )

    def test_encode_image_to_base64_method_exists(self):
        """AgentCharlie must have a _encode_image_to_base64 helper method."""
        klass = self._load_agent_charlie()
        assert klass is not None, "AgentCharlie class not found in image_generator.py"
        assert hasattr(klass, "_encode_image_to_base64"), (
            "AgentCharlie is missing the '_encode_image_to_base64' method"
        )
