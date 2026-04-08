"""
Tests to verify the google-generativeai -> google-genai SDK migration.
"""

import os
import sys
import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

PROMPT_GEN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "modules", "prompt_generator.py"
)
QA_AGENT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "modules", "qa_agent.py"
)


def read_source(path):
    with open(path, "r") as f:
        return f.read()


class TestPromptGeneratorMigration:
    """Verify prompt_generator.py no longer uses the deprecated SDK."""

    def test_no_old_import(self):
        source = read_source(PROMPT_GEN_PATH)
        assert "import google.generativeai" not in source, (
            "prompt_generator.py still uses the deprecated 'import google.generativeai'"
        )

    def test_no_genai_configure(self):
        source = read_source(PROMPT_GEN_PATH)
        assert "genai.configure" not in source, (
            "prompt_generator.py still calls deprecated genai.configure()"
        )

    def test_uses_new_import(self):
        source = read_source(PROMPT_GEN_PATH)
        assert "from google import genai" in source, (
            "prompt_generator.py should use 'from google import genai'"
        )

    def test_uses_client_pattern(self):
        source = read_source(PROMPT_GEN_PATH)
        assert "genai.Client(" in source, (
            "prompt_generator.py should use genai.Client() pattern"
        )


class TestQaAgentMigration:
    """Verify qa_agent.py no longer uses the deprecated SDK."""

    def test_no_old_import(self):
        source = read_source(QA_AGENT_PATH)
        assert "import google.generativeai" not in source, (
            "qa_agent.py still uses the deprecated 'import google.generativeai'"
        )

    def test_no_genai_configure(self):
        source = read_source(QA_AGENT_PATH)
        assert "genai.configure" not in source, (
            "qa_agent.py still calls deprecated genai.configure()"
        )

    def test_uses_new_import(self):
        source = read_source(QA_AGENT_PATH)
        assert "from google import genai" in source, (
            "qa_agent.py should use 'from google import genai'"
        )

    def test_uses_client_pattern(self):
        source = read_source(QA_AGENT_PATH)
        assert "genai.Client(" in source, (
            "qa_agent.py should use genai.Client() pattern"
        )


class TestAgentInitialization:
    """Verify the agents can be instantiated without error using a placeholder API key."""

    def setup_method(self):
        os.environ["GOOGLE_API_KEY"] = "test-placeholder-key"

    def teardown_method(self):
        os.environ.pop("GOOGLE_API_KEY", None)

    def test_agent_bravo_init(self):
        from src.modules.prompt_generator import AgentBravo
        agent = AgentBravo()
        assert agent is not None
        assert agent.genai_client is not None
        assert agent.vision_model_name is not None

    def test_agent_delta_init(self):
        from src.modules.qa_agent import AgentDelta
        agent = AgentDelta()
        assert agent is not None
        assert agent.genai_client is not None
        assert agent.model_name is not None
