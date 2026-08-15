"""
Tests for the P3 print-quality gate: saturation-based color masking
(including the previously-missed BLUE wireframe guides) and the KDP validator.
"""

import os
import shutil
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas

from src import config
from src.modules.kdp_validator import KDPValidator
from src.modules.pdf_assembler import AgentEcho

TMP = "temp_test_kdp"


def make_echo():
    with patch.object(AgentEcho, "_register_fonts"):
        return AgentEcho()


class TestColorMasking(unittest.TestCase):
    def setUp(self):
        os.makedirs(TMP, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(TMP, ignore_errors=True)

    def test_all_three_guide_colors_masked_and_png_output(self):
        img_path = f"{TMP}/guides.png"
        img = Image.new("RGB", (60, 60), "white")
        px = img.load()
        for i in range(10, 50):
            px[i, 10] = (255, 0, 0)    # red guide
            px[i, 20] = (0, 255, 0)    # green guide
            px[i, 30] = (0, 0, 255)    # blue guide (old loop missed this)
            px[i, 40] = (0, 0, 0)      # real black line art — must survive
        img.save(img_path)

        echo = make_echo()
        out = echo.apply_color_masking(img_path)

        self.assertTrue(out.endswith("_masked.png"), "line art must be lossless PNG, not JPEG")
        with Image.open(out) as result:
            self.assertEqual(result.mode, "L")
            self.assertGreater(result.getpixel((20, 10)), 250)  # red gone
            self.assertGreater(result.getpixel((20, 20)), 250)  # green gone
            self.assertGreater(result.getpixel((20, 30)), 250)  # blue gone
            self.assertLess(result.getpixel((20, 40)), 5)       # black line kept


class TestKDPValidator(unittest.TestCase):
    def setUp(self):
        os.makedirs(TMP, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(TMP, ignore_errors=True)

    def _build_pdf(self, path, page_w_in, page_h_in, img_px):
        img_path = f"{TMP}/art.png"
        Image.new("RGB", (img_px, img_px), "white").save(img_path)
        c = rl_canvas.Canvas(path, pagesize=(page_w_in * inch, page_h_in * inch))
        c.drawImage(img_path, 0, 0, width=page_w_in * inch, height=page_h_in * inch)
        c.showPage()
        c.save()

    def test_correct_geometry_and_dpi_passes(self):
        pdf = f"{TMP}/good.pdf"
        # 8.625" wide at >=300 DPI needs >=2588px
        self._build_pdf(pdf, 8.625, 8.75, 2700)
        report = KDPValidator().validate(pdf)
        self.assertTrue(report["passed"], report["errors"])
        # short book is a warning, not an error
        self.assertTrue(any("page count" in w for w in report["warnings"]))

    def test_low_dpi_fails(self):
        pdf = f"{TMP}/lowdpi.pdf"
        self._build_pdf(pdf, 8.625, 8.75, 1024)  # ~119 DPI
        report = KDPValidator().validate(pdf)
        self.assertFalse(report["passed"])
        self.assertTrue(any("DPI" in e for e in report["errors"]))

    def test_wrong_page_size_fails(self):
        pdf = f"{TMP}/square.pdf"
        self._build_pdf(pdf, 8.75, 8.75, 2700)  # the old (wrong) square canvas
        report = KDPValidator().validate(pdf)
        self.assertFalse(report["passed"])
        self.assertTrue(any("size" in e for e in report["errors"]))

    def test_missing_pdf_fails(self):
        report = KDPValidator().validate(f"{TMP}/nope.pdf")
        self.assertFalse(report["passed"])


if __name__ == "__main__":
    unittest.main()
