import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.prompt_generator import AgentBravo

class TestSmartPrompts(unittest.TestCase):
    def setUp(self):
        self.bravo = AgentBravo()
        # Mock the API call layer to avoid network (post-google-genai migration:
        # AgentBravo calls _call_with_backoff(model_name, contents))
        self.bravo._call_with_backoff = MagicMock(
            return_value=MagicMock(text="Mocked Prompt")
        )

        # Mock rate limit to speed up tests
        self.bravo._rate_limit = MagicMock()

    def test_bible_spec_extraction(self):
        print("\nTesting Bible Spec Extraction...")
        
        # Mock reading the Bible file
        mock_bible_content = """
#### [PAGE_04_KNOLLING] (Miniature Gear Box)
* **Structure:** "Visual Island" (60% Scale).
* **Asset_Wireframe:** `assets/ref_page4_layout_wireframe_kdp.png`
* **Gap_Rule:** **0.5 inch (minimum)** vertical gap.

#### [PAGE_05_ACTION] (Action Scene)
* **Structure:** Full Bleed.
"""
        with patch('builtins.open', new_callable=MagicMock) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = mock_bible_content
            with patch('os.path.exists', return_value=True):
                
                # Test extraction
                spec = self.bravo._extract_bible_specs("[PAGE_04_KNOLLING]")
                print(f"Extracted Spec: {spec[:50]}...")
                
                self.assertIn("Visual Island", spec)
                self.assertIn("Gap_Rule", spec)
                self.assertNotIn("PAGE_05_ACTION", spec) # Should stop before next section
                
                print("Bible spec extraction successful.")

    def test_no_color_instruction(self):
        print("\nTesting 'No Color' Instruction Injection...")
        
        with patch('os.path.exists', return_value=True):
            # Prompts are now built deterministically — assert on the returned string
            prompt, wf, refs, neg = self.bravo._generate_smart_prompt("knolling", "Test", "Context")

            self.assertIn("CRITICAL: The Wireframe contains COLORED ZONES", prompt)
            self.assertIn("pure BLACK & WHITE line art", prompt)
            # Style ref + structure example both flow to the image model
            self.assertEqual(refs, ["assets/ref_page4_01.png",
                                    "assets/ref_page4_structure_example.png"])
            self.assertEqual(wf, "assets/ref_page4_layout_wireframe_kdp.png")
            self.assertIn(self.bravo.NEGATIVE_KNOLLING.split(",")[0], neg)

            print("Verified 'No Color' instruction for interior page.")

            # Test Cover (should NOT have the B/W restriction)
            prompt, wf, refs, neg = self.bravo._generate_smart_prompt("cover", "Test", "Context")

            self.assertNotIn("The final output must be pure BLACK & WHITE line art", prompt)
            self.assertIn("Output full color", prompt)

            print("Verified 'Full Color' instruction for cover.")

    def test_deterministic_no_llm_in_prompt_loop(self):
        """The prompt build must not round-trip through the text LLM anymore."""
        with patch('os.path.exists', return_value=True):
            self.bravo._generate_smart_prompt("action", "Test", "Context")
        self.bravo._call_with_backoff.assert_not_called()

if __name__ == '__main__':
    unittest.main()
