"""
Agent Echo: Senior Publishing Engineer (Assembly)
Mission: Handle the "Publisher" logic (Image Processing).
"""

import logging
import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from src import config

logger = logging.getLogger("AgentEcho")

class AgentEcho:
    def __init__(self):
        logger.info("Agent Echo initialized.")
        # Bible Specs: 8.5" x 8.5" Trim Size
        # Bleed: 0.125" on all sides
        # Total Size: 8.75" x 8.75"
        self.width = 8.75 * inch
        self.height = 8.75 * inch
        self._register_fonts()

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
                    logger.info(f"Registered font: {name}")
                else:
                    logger.warning(f"Font file not found: {path}")
            except Exception as e:
                logger.error(f"Failed to register font {name}: {e}")
        
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
                return temp_masked
                
        except Exception as e:
            logger.error(f"Color masking failed for {image_path}: {e}")
            return None

    def draw_text_overlay(self, c, page_type):
        """
        Draws text overlay based on Series Master Bible v5.21 specs.
        """
        width, height = self.width, self.height
        
        try:
            if page_type == "mission": # Page 1
                # Header (Red)
                c.setFont("TitanOne", 30)
                c.drawCentredString(width/2, height - 1.0*inch, "KNOLLING ADVENTURES")
                
                # Center (Yellow)
                c.setFont("FredokaOne", 20)
                c.drawCentredString(width/2, height/2 + 0.5*inch, "THIS BOOK BELONGS TO:")
                
                # Instruction (Blue) - Simplified for MVP
                c.setFont("Quicksand", 12)
                c.drawCentredString(width/2, 1.5*inch, "1. COLOR  2. OBSERVE  3. LEARN")

            elif page_type == "parents": # Page 2
                # Header
                c.setFont("TitanOne", 40)
                c.drawCentredString(width/2, height * 0.85, "A NOTE TO PARENTS:")
                
                # Body
                c.setFont("Quicksand", 18)
                text = "This book is best used with crayons or colored pencils. If using MARKERS, please place a protective sheet behind the page!"
                # Simple text wrap logic (MVP)
                c.drawCentredString(width/2, height * 0.60, "This book is best used with crayons or colored pencils.")
                c.drawCentredString(width/2, height * 0.60 - 25, "If using MARKERS, please place a protective sheet behind the page!")
                
                # Footer
                c.setFont("Sniglet", 10)
                c.drawCentredString(width/2, 0.5*inch, "Copyright © 2025 by PapaBingo. All rights reserved.")

            elif page_type == "intro": # Page 3
                # Top
                c.setFont("TitanOne", 30)
                c.setFillColorRGB(1, 1, 1) # White Fill
                c.setStrokeColorRGB(0, 0, 0) # Black Stroke
                c.setLineWidth(2)
                # Note: ReportLab text render mode for outline is complex, simplifying to black text for MVP
                c.setFillColorRGB(0, 0, 0) 
                c.drawCentredString(width/2, height - 1.5*inch, "ARE YOU READY TO EXPLORE?")
                
                # Bottom
                c.drawCentredString(width/2, 1.5*inch, "TURN THE PAGE TO START YOUR FIRST MISSION!")

            elif page_type == "knolling": # Page 4
                # Theme Title (Blue Zone)
                c.setFont("TitanOne", 24)
                # Assuming Theme is passed or generic. Using generic for now.
                c.drawCentredString(width/2, 1.0*inch, "THEME GEAR")

            elif page_type == "certificate": # Page 50
                c.setFont("TitanOne", 60)
                c.drawCentredString(width/2, height - 2*inch, "CONGRATULATIONS!")
                
                c.setFont("TitanOne", 45)
                c.drawCentredString(width/2, height/2, "OFFICIAL EXPLORER")

        except Exception as e:
            logger.error(f"Text overlay failed for {page_type}: {e}")

    def assemble_pdf(self, image_paths):
        """
        Assembles the PDF from the generated images.
        Returns the path to the generated PDF.
        """
        if not image_paths:
            logger.error("No images to assemble.")
            return None
            
        output_filename = f"temp/Knolling_Adventure_{int(time.time())}.pdf"
        logger.info(f"Assembling PDF: {output_filename}")
        
        try:
            c = canvas.Canvas(output_filename, pagesize=(self.width, self.height))
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    # Apply Color Masking & Grayscale Conversion
                    processed_img_path = self.apply_color_masking(img_path)
                    
                    if processed_img_path:
                        # Draw on Canvas (Full Bleed)
                        c.drawImage(processed_img_path, 0, 0, width=self.width, height=self.height)
                        
                        # Determine Page Type from filename (MVP heuristic)
                        page_type = "unknown"
                        if "mission" in img_path or "page1" in img_path: page_type = "mission"
                        elif "parents" in img_path or "page2" in img_path: page_type = "parents"
                        elif "intro" in img_path or "page3" in img_path: page_type = "intro"
                        elif "knolling" in img_path or "page4" in img_path: page_type = "knolling"
                        elif "certificate" in img_path or "page50" in img_path: page_type = "certificate"
                        
                        # Apply Text Overlay
                        self.draw_text_overlay(c, page_type)
                        
                        c.showPage()
                        
                        # Cleanup temp file
                        os.remove(processed_img_path)
                    else:
                        logger.warning(f"Failed to process image: {img_path}")
                else:
                    logger.warning(f"Image not found: {img_path}")
            
            c.save()
            logger.info("PDF Assembly complete.")
            return output_filename
            
        except Exception as e:
            logger.error(f"PDF Assembly failed: {e}")
            return None
