import unittest, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from reportlab.lib.units import inch

class TestCoverDimensions(unittest.TestCase):
    def test_cover_spread_width(self):
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        self.assertAlmostEqual(echo.cover_width, 17.365 * inch, places=1)

    def test_cover_spread_height(self):
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        self.assertAlmostEqual(echo.cover_height, 8.75 * inch, places=1)

    def test_internal_page_dimensions_unchanged(self):
        from src.modules.pdf_assembler import AgentEcho
        echo = AgentEcho()
        self.assertAlmostEqual(echo.width, 8.75 * inch, places=1)
        self.assertAlmostEqual(echo.height, 8.75 * inch, places=1)

if __name__ == '__main__':
    unittest.main()
