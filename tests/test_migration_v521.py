import unittest
import os
import sys
from PIL import Image
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import config
from src.modules.prompt_generator import AgentBravo
from src.modules.pdf_assembler import AgentEcho

class TestMigrationV521(unittest.TestCase):
    def setUp(self):
        self.bravo = AgentBravo()
        self.echo = AgentEcho()
        os.makedirs("temp_test", exist_ok=True)

    def tearDown(self):
        if os.path.exists("temp_test"):
            shutil.rmtree("temp_test")

    def test_config_model_id(self):
        print(f"\nTesting Config Model ID (Tier: {config.DEPLOYMENT_TIER})...")
        if config.DEPLOYMENT_TIER == "PAID":
            self.assertEqual(config.GEN_MODEL_ID, "imagen-4.0-generate-001")
        else:
            self.assertEqual(config.GEN_MODEL_ID, "models/gemini-2.0-flash-exp-image-generation")
            
    def test_negative_dna_injection(self):
        print("\nTesting Negative DNA Injection...")
        
        # Mock the vision model response
        class MockResponse:
            text = "Mock DNA Style"
            
        class MockModel:
            def generate_content(self, inputs):
                return MockResponse()
                
        self.bravo.vision_model = MockModel()
        
        # Mock analyze_assets to populate style library without API calls
        self.bravo.style_library['dna_page_01'] = "test_dna"
        self.bravo.style_library['dna_cover'] = "test_dna"
        
        prompts = self.bravo.generate_prompts("Firefighter")
        mission_prompt = prompts['prompts'][0]['prompt']
        
        self.assertIn("--negative_prompt", mission_prompt)
        self.assertIn(self.bravo.NEGATIVE_GLOBAL, mission_prompt)
        print("Negative DNA found in prompt.")

    def test_color_masking(self):
        print("\nTesting Color Masking...")
        # Create a dummy image with Red and Green lines
        img_path = "temp_test/test_masking.png"
        img = Image.new("RGB", (100, 100), "white")
        pixels = img.load()
        
        # Draw Red Line
        for i in range(10, 90):
            pixels[i, 50] = (255, 0, 0) # Red
            
        # Draw Green Line
        for i in range(10, 90):
            pixels[50, i] = (0, 255, 0) # Green
            
        img.save(img_path)
        
        # Apply Masking
        processed_path = self.echo.apply_color_masking(img_path)
        
        # Check result
        self.assertTrue(os.path.exists(processed_path))
        
        with Image.open(processed_path) as result:
            self.assertEqual(result.mode, "L") # Should be Grayscale
            # Check if Red line is gone (should be white/light gray)
            # Since we converted to Grayscale, White is 255.
            # If masking worked, the Red (255,0,0) became White (255,255,255) -> 255 in L
            # If masking failed, Red (255,0,0) -> ~76 in L (standard conversion)
            
            # Let's check the pixel where Red was
            val = result.getpixel((50, 50)) # Intersection of Red and Green
            print(f"Pixel Value at intersection: {val}")
            self.assertGreater(val, 250) # Should be near white

if __name__ == '__main__':
    unittest.main()
