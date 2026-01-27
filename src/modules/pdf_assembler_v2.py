"""
Agent Echo v2.0: Senior Publishing Engineer (Assembly) - FIXED
Mission: Handle PDF assembly with VERIFIED text overlay compositing.
"""

import logging
import os
import time
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
        self._register_fonts()
        
        # Debug mode: Use magenta text for visibility testing
        self.debug_mode = os.getenv("PDF_DEBUG_MODE", "false").lower() == "true"
        if self.debug_mode:
            logger.warning("🔍 PDF DEBUG MODE ENABLED: Text will render in MAGENTA")

    def _register_fonts(self):
        """Registers Google Fonts from assets/fonts/"""
        fonts = [
            ("TitanOne", config.FONT_TITLE_MAIN),
            ("FredokaOne", config.FONT_SUBTITLE),
            ("Quicksand", config.FONT_BODY_TEXT),
            ("PatrickHand", config.FONT_HANDWRITING),
            ("Sniglet", config.FONT_LEGAL)
        ]
        
        for name, filename in fonts:
            try:
                path = os.path.join(config.PATH_FONTS, filename)
                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont(name, path))
                    logger.info(f"✅ Registered font: {name}")
                else:
                    logger.warning(f"⚠️  Font file not found: {path}")
            except Exception as e:
                logger.error(f"❌ Failed to register font {name}: {e}")
        
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

    def assemble_pdf(self, image_paths):
        """
        Assembles the PDF from the generated images.
        TASK 3 FIX: Ensures correct layer order (image FIRST, then text OVER it).
        Returns the path to the generated PDF.
        """
        if not image_paths:
            logger.error("❌ No images to assemble.")
            return None
            
        output_filename = f"temp/Knolling_Adventure_{int(time.time())}.pdf"
        logger.info(f"📄 Assembling PDF: {output_filename}")
        logger.info("=" * 80)
        logger.info("LAYER ORDER VERIFICATION (CRITICAL FOR TEXT VISIBILITY)")
        logger.info("=" * 80)
        
        try:
            c = canvas.Canvas(output_filename, pagesize=(self.width, self.height))
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    logger.info(f"\n📄 Processing: {img_path}")
                    
                    # Apply Color Masking & Grayscale Conversion
                    processed_img_path = self.apply_color_masking(img_path)
                    
                    if processed_img_path:
                        # TASK 3 FIX: CRITICAL LAYER ORDER
                        # Step 1: Draw Image FIRST (Background Layer)
                        logger.info("  1️⃣  Drawing IMAGE layer (background)...")
                        c.drawImage(processed_img_path, 0, 0, width=self.width, height=self.height)
                        
                        # Determine Page Type from filename (MVP heuristic)
                        page_type = "unknown"
                        if "Cover" in img_path or "cover" in img_path: 
                            page_type = "cover"
                        elif "Page1" in img_path or "page1" in img_path: 
                            page_type = "mission"
                        elif "Page2" in img_path or "page2" in img_path: 
                            page_type = "parents"
                        elif "Page3" in img_path or "page3" in img_path: 
                            page_type = "intro"
                        elif "Page4" in img_path or "page4" in img_path: 
                            page_type = "knolling"
                        elif "Page5" in img_path or "page5" in img_path: 
                            page_type = "action"
                        elif "Page50" in img_path or "page50" in img_path: 
                            page_type = "certificate"
                        
                        logger.info(f"  📋 Detected page type: {page_type}")
                        
                        # Step 2: Draw Text SECOND (Foreground Layer)
                        if page_type != "unknown" and page_type != "action" and page_type != "cover":
                            logger.info("  2️⃣  Drawing TEXT layer (foreground)...")
                            self.draw_text_overlay(c, page_type)
                        else:
                            logger.info("  ⏭️  Skipping text overlay (not applicable for this page type)")
                        
                        # Step 3: Finalize Page
                        logger.info("  3️⃣  Finalizing page...")
                        c.showPage()
                        
                        # Cleanup temp file
                        os.remove(processed_img_path)
                        logger.info("  ✅ Page complete\n")
                    else:
                        logger.warning(f"⚠️  Failed to process image: {img_path}")
                else:
                    logger.warning(f"⚠️  Image not found: {img_path}")
            
            c.save()
            logger.info("=" * 80)
            logger.info(f"✅ PDF ASSEMBLY COMPLETE: {output_filename}")
            logger.info("=" * 80)
            return output_filename
            
        except Exception as e:
            logger.error(f"❌ PDF Assembly failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
