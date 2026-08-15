"""
Agent Echo v2.0: Senior Publishing Engineer (Assembly) - FIXED
Mission: Handle PDF assembly with VERIFIED text overlay compositing.
"""

import logging
import os
import time
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, magenta, black
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from src import config

logger = logging.getLogger("AgentEcho")

class AgentEcho:
    def __init__(self):
        logger.info("Agent Echo v2.0 initialized (with Text Overlay Debugging).")
        # Bible Specs: 8.5" x 8.5" Trim Size
        # Bleed: 0.125" on all sides
        # Total Size: 8.75" x 8.75"
        self.width = 8.75 * inch
        self.height = 8.75 * inch
        # Cover Spread: 17.365" x 8.75" (Back + Spine + Front + Bleeds)
        self.cover_width = 17.365 * inch
        self.cover_height = 8.75 * inch
        self._register_fonts()
        
        # Debug mode: Use magenta text for visibility testing
        self.debug_mode = os.getenv("PDF_DEBUG_MODE", "false").lower() == "true"
        if self.debug_mode:
            logger.warning("🔍 PDF DEBUG MODE ENABLED: Text will render in MAGENTA")

    def _register_fonts(self):
        """Registers Google Fonts from assets/fonts/. Fails fast on any missing font:
        an unregistered font would otherwise surface later as a KeyError inside
        draw_text_overlay and silently kill the whole PDF."""
        fonts = [
            ("TitanOne", config.FONT_TITLE_MAIN),
            ("FredokaOne", config.FONT_SUBTITLE),
            ("Quicksand", config.FONT_BODY_TEXT),
            ("PatrickHand", config.FONT_HANDWRITING),
            ("Sniglet", config.FONT_LEGAL)
        ]

        missing = []
        for name, filename in fonts:
            path = os.path.join(config.PATH_FONTS, filename)
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
                logger.info(f"✅ Registered font: {name}")
            else:
                missing.append(path)

        if missing:
            raise RuntimeError(
                f"Missing font files (see assets/MANIFEST.md): {missing}. "
                "Text overlay cannot render without them."
            )
        
    def apply_color_masking(self, image_path):
        """
        [PROTOCOL_COLOR_MASKING]
        Detects Red/Green pixels (Wireframe artifacts) and replaces them with White.
        Then converts to Grayscale.
        """
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                datas = img.getdata()
                
                new_data = []
                for item in datas:
                    # Detect Red (R>200, G<100, B<100) or Green (G>200, R<100, B<100)
                    if (item[0] > 200 and item[1] < 100 and item[2] < 100) or \
                       (item[1] > 200 and item[0] < 100 and item[2] < 100):
                        new_data.append((255, 255, 255)) # Replace with White
                    else:
                        new_data.append(item)
                        
                img.putdata(new_data)
                
                # Convert to Grayscale (L)
                gray_img = img.convert("L")
                
                # Save temp masked version
                temp_masked = image_path.replace(".png", "_masked.jpg")
                gray_img.save(temp_masked, quality=95)
                logger.info(f"✅ Color masking applied: {temp_masked}")
                return temp_masked
                
        except Exception as e:
            logger.error(f"❌ Color masking failed for {image_path}: {e}")
            return None

    def draw_text_overlay(self, c, page_type):
        """
        Draws text overlay based on Series Master Bible v5.22 specs.
        TASK 3 FIX: Ensures proper layering, coordinate validation, and color visibility.
        """
        width, height = self.width, self.height
        
        # TASK 3 FIX: Set text color (Magenta for debugging, Black for production)
        if self.debug_mode:
            c.setFillColor(magenta)
            c.setStrokeColor(magenta)
            logger.info("🔍 DEBUG: Text color set to MAGENTA for visibility testing")
        else:
            c.setFillColor(black)
            c.setStrokeColor(black)
        
        try:
            if page_type == "mission": # Page 1
                # Header (Red)
                c.setFont("TitanOne", 30)
                x, y = width/2, height - 1.0*inch
                
                # TASK 3 FIX: Coordinate validation
                assert 0 <= x <= width, f"X coordinate {x} out of bounds (0-{width})"
                assert 0 <= y <= height, f"Y coordinate {y} out of bounds (0-{height})"
                
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'KNOLLING ADVENTURES'")
                c.drawCentredString(x, y, "KNOLLING ADVENTURES")
                
                # Center (Yellow)
                c.setFont("FredokaOne", 20)
                x, y = width/2, height/2 + 0.5*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'THIS BOOK BELONGS TO:'")
                c.drawCentredString(x, y, "THIS BOOK BELONGS TO:")
                
                # Instruction (Blue) - Simplified for MVP
                c.setFont("Quicksand", 12)
                x, y = width/2, 1.5*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): '1. COLOR  2. OBSERVE  3. LEARN'")
                c.drawCentredString(x, y, "1. COLOR  2. OBSERVE  3. LEARN")

            elif page_type == "parents": # Page 2
                # Header
                c.setFont("TitanOne", 40)
                x, y = width/2, height * 0.85
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'A NOTE TO PARENTS:'")
                c.drawCentredString(x, y, "A NOTE TO PARENTS:")
                
                # Body
                c.setFont("Quicksand", 18)
                x, y1 = width/2, height * 0.60
                y2 = height * 0.60 - 25
                assert 0 <= x <= width and 0 <= y1 <= height and 0 <= y2 <= height
                
                logger.info(f"📝 Drawing text at ({x:.2f}, {y1:.2f})")
                c.drawCentredString(x, y1, "This book is best used with crayons or colored pencils.")
                logger.info(f"📝 Drawing text at ({x:.2f}, {y2:.2f})")
                c.drawCentredString(x, y2, "If using MARKERS, please place a protective sheet behind the page!")
                
                # Footer
                c.setFont("Sniglet", 10)
                x, y = width/2, 0.5*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): Copyright")
                c.drawCentredString(x, y, "Copyright © 2025 by PapaBingo. All rights reserved.")

            elif page_type == "intro": # Page 3
                # Top
                c.setFont("TitanOne", 30)
                c.setFillColor(black if not self.debug_mode else magenta)
                x, y = width/2, height - 1.5*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'ARE YOU READY TO EXPLORE?'")
                c.drawCentredString(x, y, "ARE YOU READY TO EXPLORE?")
                
                # Bottom
                x, y = width/2, 1.5*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'TURN THE PAGE...'")
                c.drawCentredString(x, y, "TURN THE PAGE TO START YOUR FIRST MISSION!")

            elif page_type == "knolling": # Page 4
                # Theme Title (Blue Zone)
                c.setFont("TitanOne", 24)
                x, y = width/2, 1.0*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'THEME GEAR'")
                c.drawCentredString(x, y, "THEME GEAR")

            elif page_type == "certificate": # Page 50
                c.setFont("TitanOne", 60)
                x, y = width/2, height - 2*inch
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'CONGRATULATIONS!'")
                c.drawCentredString(x, y, "CONGRATULATIONS!")
                
                c.setFont("TitanOne", 45)
                x, y = width/2, height/2
                assert 0 <= x <= width and 0 <= y <= height
                logger.info(f"📝 Drawing text at ({x:.2f}, {y:.2f}): 'OFFICIAL EXPLORER'")
                c.drawCentredString(x, y, "OFFICIAL EXPLORER")
                
            logger.info(f"✅ Text overlay completed for page type: {page_type}")

        except AssertionError as e:
            logger.error(f"❌ COORDINATE VALIDATION FAILED: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Text overlay failed for {page_type}: {e}")
            raise

    def _draw_image_fitted(self, c, img_path, page_w, page_h):
        """
        Draws the image preserving aspect ratio ("cover" fit: fill the page,
        center-crop the overflow) instead of stretching, and logs effective DPI.
        """
        with Image.open(img_path) as im:
            px_w, px_h = im.size
            page_aspect = page_w / page_h
            img_aspect = px_w / px_h

            if abs(img_aspect - page_aspect) / page_aspect > 0.02:
                logger.warning(
                    f"  ⚠️  Aspect mismatch (image {img_aspect:.3f} vs page {page_aspect:.3f}) "
                    f"— center-cropping instead of stretching"
                )
                if img_aspect > page_aspect:
                    crop_w = int(px_h * page_aspect)
                    x0 = (px_w - crop_w) // 2
                    im_c = im.crop((x0, 0, x0 + crop_w, px_h))
                else:
                    crop_h = int(px_w / page_aspect)
                    y0 = (px_h - crop_h) // 2
                    im_c = im.crop((0, y0, px_w, y0 + crop_h))
                base, ext = os.path.splitext(img_path)
                cropped_path = f"{base}_fit{ext}"
                im_c.save(cropped_path)
                img_path = cropped_path
                px_w, px_h = im_c.size

        page_w_in = page_w / inch
        effective_dpi = px_w / page_w_in
        if effective_dpi < 300:
            logger.warning(f"  ⚠️  Effective resolution {effective_dpi:.0f} DPI < KDP minimum 300 DPI "
                           f"({px_w}x{px_h}px on {page_w_in:.3f}\" page)")
        else:
            logger.info(f"  ✅ Effective resolution: {effective_dpi:.0f} DPI")

        c.drawImage(img_path, 0, 0, width=page_w, height=page_h)
        return img_path

    # Page types that receive a programmatic text overlay (Bible §1.6)
    TEXT_OVERLAY_TYPES = {"mission", "parents", "intro", "knolling", "certificate"}

    def assemble_pdf(self, pages):
        """
        Assembles the PDF from generated pages.

        Args:
            pages: list of dicts with explicit metadata (single source of truth is
                   the orchestrator's prompt data — NO filename sniffing):
                   {"path": str, "page_type": str, "page_number": int}

        Returns the path to the generated PDF. Raises on assembly failure —
        a silent None return previously masked total failures.
        """
        if not pages:
            raise ValueError("No pages to assemble.")

        output_filename = f"temp/Knolling_Adventure_{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        logger.info(f"📄 Assembling PDF: {output_filename}")

        # Interior pages in reading order, cover first if present
        ordered = sorted(pages, key=lambda p: (p.get("page_type") != "cover", p.get("page_number", 0)))

        c = canvas.Canvas(output_filename, pagesize=(self.width, self.height))

        for page in ordered:
            img_path = page["path"]
            page_type = page.get("page_type", "unknown")

            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Generated image missing during assembly: {img_path}")

            logger.info(f"\n📄 Processing: {img_path} (type={page_type}, page={page.get('page_number')})")

            # Color masking / grayscale applies to interiors only — covers stay full color
            if page_type == "cover":
                processed_img_path = img_path
                page_w, page_h = self.cover_width, self.cover_height
            else:
                processed_img_path = self.apply_color_masking(img_path)
                if not processed_img_path:
                    raise RuntimeError(f"Color masking failed for {img_path}")
                page_w, page_h = self.width, self.height

            # Layer 1: image (background), aspect-preserving
            c.setPageSize((page_w, page_h))
            drawn_path = self._draw_image_fitted(c, processed_img_path, page_w, page_h)

            # Layer 2: programmatic text (foreground)
            if page_type in self.TEXT_OVERLAY_TYPES:
                logger.info("  2️⃣  Drawing TEXT layer (foreground)...")
                self.draw_text_overlay(c, page_type)
            else:
                logger.info(f"  ⏭️  No text overlay for page type '{page_type}'")

            c.showPage()

            # Cleanup temp files
            for tmp in {processed_img_path, drawn_path} - {img_path}:
                if os.path.exists(tmp):
                    os.remove(tmp)
            logger.info("  ✅ Page complete")

        c.save()
        logger.info(f"✅ PDF ASSEMBLY COMPLETE: {output_filename}")
        return output_filename
