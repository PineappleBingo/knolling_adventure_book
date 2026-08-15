import unittest, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from reportlab.lib.units import inch
from src import config

class TestCoverDimensions(unittest.TestCase):
    def test_cover_spread_width_computed_from_page_count(self):
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        expected_w, _ = config.get_cover_spread_size()
        self.assertAlmostEqual(echo.cover_width, expected_w * inch, places=2)
        # For the Bible's 50-page reference case the spread is ~17.36"
        w50, _ = config.get_cover_spread_size(50)
        self.assertAlmostEqual(w50, 17.3626, places=3)

    def test_spine_width_formula(self):
        # KDP B&W paper: 0.002252" per page
        self.assertAlmostEqual(config.get_spine_width(50), 0.1126, places=4)

    def test_cover_spread_height(self):
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        _, expected_h = config.get_cover_spread_size()
        self.assertAlmostEqual(echo.cover_height, expected_h * inch, places=2)

    def test_internal_page_dimensions_unchanged(self):
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        self.assertAlmostEqual(echo.width, 8.75 * inch, places=1)
        self.assertAlmostEqual(echo.height, 8.75 * inch, places=1)

if __name__ == '__main__':
    unittest.main()
