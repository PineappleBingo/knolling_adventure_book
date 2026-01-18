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
        # Mock the vision model to avoid API calls
        self.bravo.vision_model = MagicMock()
        self.bravo.vision_model.generate_content.return_value.text = "Mocked Prompt"
        
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
            with patch('PIL.Image.open'):
                # Generate a prompt for a non-cover page
                self.bravo._generate_smart_prompt("knolling", "Test", "Context")
                
                # Check the arguments passed to generate_content
                call_args = self.bravo.vision_model.generate_content.call_args
                meta_prompt = call_args[0][0][0] # First arg, first element (list), first item (string)
                
                self.assertIn("CRITICAL: The Wireframe contains COLORED ZONES", meta_prompt)
                self.assertIn("pure BLACK & WHITE line art", meta_prompt)
                
                print("Verified 'No Color' instruction for interior page.")
                
                # Test Cover (should NOT have the restriction)
                self.bravo._generate_smart_prompt("cover", "Test", "Context")
                call_args = self.bravo.vision_model.generate_content.call_args
                meta_prompt = call_args[0][0][0]
                
                self.assertNotIn("pure BLACK & WHITE line art", meta_prompt)
                self.assertIn("Output full color", meta_prompt)
                
                print("Verified 'Full Color' instruction for cover.")

if __name__ == '__main__':
    unittest.main()
