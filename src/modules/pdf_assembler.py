"""
Agent Echo v2.0: Senior Publishing Engineer (Assembly) - FIXED
Mission: Handle PDF assembly with VERIFIED text overlay compositing.
"""

import logging
import os
import time
from datetime import datetime
import numpy as np
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
        # Bible Specs (§1.4): 8.5" x 8.5" trim. KDP bleed extends TOP/BOTTOM/OUTER
        # edges only — never the binding edge — so the interior page canvas is
        # 8.625" x 8.75" (w: 8.5 + 0.125 outer; h: 8.5 + 0.125 top + 0.125 bottom).
        # The old square 8.75 x 8.75 canvas was a spec violation.
        self.width = (config.TRIM_WIDTH + config.BLEED_SIZE) * inch
        self.height = (config.TRIM_HEIGHT + 2 * config.BLEED_SIZE) * inch
        # Cover Spread: Back + Spine + Front + Bleeds — spine width depends on
        # PAGE_COUNT, so the spread is computed, not hardcoded (17.365" was only
        # correct for exactly 50 pages).
        cover_w_in, cover_h_in = config.get_cover_spread_size()
        self.cover_width = cover_w_in * inch
        self.cover_height = cover_h_in * inch
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
        
    # Saturation above this marks a pixel as a colored wireframe guide.
    # Black line art and white paper both have ~0 channel spread.
    MASK_SATURATION_THRESHOLD = 60

    def apply_color_masking(self, image_path):
        """
        [PROTOCOL_COLOR_MASKING]
        Whites out ANY saturated pixel (Red/Green/Blue wireframe guides — the old
        per-pixel loop only caught R and G, letting blue guides print as gray),
        then converts to grayscale. Vectorized with numpy: a 300-DPI page is
        ~6.9M pixels, which the previous pure-Python loop handled one at a time.
        Saves lossless PNG — JPEG ringing on 1-bit line art is a classic KDP
        print-QA rejection.
        """
        try:
            with Image.open(image_path) as img:
                arr = np.asarray(img.convert("RGB"), dtype=np.int16)

            saturation = arr.max(axis=2) - arr.min(axis=2)
            arr[saturation > self.MASK_SATURATION_THRESHOLD] = 255

            gray_img = Image.fromarray(arr.astype(np.uint8)).convert("L")

            base, _ = os.path.splitext(image_path)
            temp_masked = f"{base}_masked.png"
            gray_img.save(temp_masked)
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

    COMPOSE_DPI = 300  # KDP minimum print resolution

    def _compose_cover_spread(self, front_path=None, back_path=None):
        """
        Composites the full KDP cover spread (back panel | spine | front panel)
        from two square art generations at 300 DPI. The KDP barcode zone
        (2.0" x 1.2", bottom-right of the back panel) is cleared to white.
        Returns the path of the composed PNG.
        """
        dpi = self.COMPOSE_DPI
        w_in, h_in = config.get_cover_spread_size()
        W, H = int(round(w_in * dpi)), int(round(h_in * dpi))
        panel_w = int(round((config.TRIM_WIDTH + config.BLEED_SIZE) * dpi))

        canvas_img = Image.new("RGB", (W, H), "white")

        def paste_panel(art_path, x0):
            if not art_path or not os.path.exists(art_path):
                return
            with Image.open(art_path) as art:
                art = art.convert("RGB")
                # cover-fit into the panel (center-crop the overflow)
                target_ratio = panel_w / H
                aw, ah = art.size
                if aw / ah > target_ratio:
                    crop_w = int(ah * target_ratio)
                    x = (aw - crop_w) // 2
                    art = art.crop((x, 0, x + crop_w, ah))
                else:
                    crop_h = int(aw / target_ratio)
                    y = (ah - crop_h) // 2
                    art = art.crop((0, y, aw, y + crop_h))
                art = art.resize((panel_w, H), Image.LANCZOS)
                canvas_img.paste(art, (x0, 0))

        paste_panel(back_path, 0)                 # back panel: left
        paste_panel(front_path, W - panel_w)      # front panel: right
        # spine stays white (spine text disallowed under 79 pages)

        # Clear the KDP barcode restricted area (Bible Zone 7): 2.0" x 1.2" at
        # the bottom-right of the BACK panel (KDP prints its barcode there)
        bc_w, bc_h = int(2.0 * dpi), int(1.2 * dpi)
        margin = int((config.BLEED_SIZE + 0.25) * dpi)
        x1 = panel_w - margin - bc_w
        y1 = H - margin - bc_h
        canvas_img.paste((255, 255, 255), (x1, y1, x1 + bc_w, y1 + bc_h))

        out_path = f"temp/cover_spread_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        canvas_img.save(out_path)
        logger.info(f"✅ Cover spread composed: {out_path} ({W}x{H}px @ {dpi} DPI)")
        return out_path

    def _draw_cover_text(self, c, cover_text):
        """
        Draws title/subtitle on the FRONT panel and the series logo (Zone 8,
        1.2" tall per Bible) in real fonts. Typography is never AI-rendered.
        """
        title = cover_text.get("title", "KNOLLING ADVENTURES")
        subtitle = cover_text.get("subtitle", "")

        # Front panel geometry (right side of the spread)
        panel_w = (config.TRIM_WIDTH + config.BLEED_SIZE) * inch
        front_cx = self.cover_width - (config.BLEED_SIZE + config.TRIM_WIDTH / 2) * inch
        safe_top = self.cover_height - (config.BLEED_SIZE + config.SAFE_MARGIN) * inch

        c.setFillColor(black)
        c.setFont("TitanOne", 64)
        c.drawCentredString(front_cx, safe_top - 0.9 * inch, title)
        if subtitle:
            c.setFont("FredokaOne", 32)
            c.drawCentredString(front_cx, safe_top - 1.6 * inch, subtitle)

        # Logo: Zone 8, height exactly 1.2" (Bible), bottom-center of front panel
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            with Image.open(logo_path) as logo:
                lw, lh = logo.size
            logo_h = 1.2 * inch
            logo_w = logo_h * (lw / lh)
            c.drawImage(
                logo_path,
                front_cx - logo_w / 2,
                (config.BLEED_SIZE + config.SAFE_MARGIN) * inch,
                width=logo_w, height=logo_h,
                mask='auto'
            )
        else:
            logger.warning("assets/logo.png not found — cover logo skipped")

    def assemble_pdf(self, pages, cover_text=None):
        """
        Assembles the PDF from generated pages.

        Args:
            pages: list of dicts with explicit metadata (single source of truth is
                   the orchestrator's prompt data — NO filename sniffing):
                   {"path": str, "page_type": str, "page_number": int}
                   Cover art arrives as page_type "cover_front"/"cover_back"
                   (composited into one spread) or legacy "cover" (pre-made spread).
            cover_text: optional {"title": ..., "subtitle": ...} drawn on the
                   front panel in real fonts.

        Returns the path to the generated PDF. Raises on assembly failure —
        a silent None return previously masked total failures.
        """
        if not pages:
            raise ValueError("No pages to assemble.")

        output_filename = f"temp/Knolling_Adventure_{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        logger.info(f"📄 Assembling PDF: {output_filename}")

        cover_front = next((p for p in pages if p.get("page_type") == "cover_front"), None)
        cover_back = next((p for p in pages if p.get("page_type") == "cover_back"), None)
        legacy_cover = next((p for p in pages if p.get("page_type") == "cover"), None)
        interiors = sorted(
            (p for p in pages if p.get("page_type") not in ("cover", "cover_front", "cover_back")),
            key=lambda p: p.get("page_number", 0)
        )

        c = canvas.Canvas(output_filename, pagesize=(self.width, self.height))

        # ── Cover spread first ──
        if cover_front or cover_back:
            spread_path = self._compose_cover_spread(
                front_path=cover_front["path"] if cover_front else None,
                back_path=cover_back["path"] if cover_back else None,
            )
            c.setPageSize((self.cover_width, self.cover_height))
            c.drawImage(spread_path, 0, 0, width=self.cover_width, height=self.cover_height)
            self._draw_cover_text(c, cover_text or {})
            c.showPage()
            os.remove(spread_path)
            logger.info("  ✅ Cover spread page complete")
        elif legacy_cover:
            c.setPageSize((self.cover_width, self.cover_height))
            drawn = self._draw_image_fitted(c, legacy_cover["path"], self.cover_width, self.cover_height)
            self._draw_cover_text(c, cover_text or {})
            c.showPage()
            if drawn != legacy_cover["path"] and os.path.exists(drawn):
                os.remove(drawn)

        # ── Interior pages in reading order ──
        for page in interiors:
            img_path = page["path"]
            page_type = page.get("page_type", "unknown")

            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Generated image missing during assembly: {img_path}")

            logger.info(f"\n📄 Processing: {img_path} (type={page_type}, page={page.get('page_number')})")

            # Color masking / grayscale applies to interiors only
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
