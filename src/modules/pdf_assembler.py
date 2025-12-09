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

logger = logging.getLogger("AgentEcho")

class AgentEcho:
    def __init__(self):
        logger.info("Agent Echo initialized.")
        # Bible Specs: 8.5" x 8.5" Trim Size
        # Bleed: 0.125" on all sides
        # Total Size: 8.75" x 8.75"
        self.width = 8.75 * inch
        self.height = 8.75 * inch
        
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
                    # Convert to Grayscale (L) as per Bible
                    try:
                        with Image.open(img_path) as img:
                            gray_img = img.convert("L")
                            # Save temp grayscale version
                            temp_gray = img_path.replace(".png", "_gray.jpg")
                            gray_img.save(temp_gray, quality=95)
                            
                            # Draw on Canvas (Full Bleed)
                            # In a real app, we'd handle left/right page positioning specifically
                            # For now, we just center/fill
                            c.drawImage(temp_gray, 0, 0, width=self.width, height=self.height)
                            c.showPage()
                            
                            # Cleanup temp gray
                            os.remove(temp_gray)
                    except Exception as e:
                        logger.error(f"Failed to process image {img_path}: {e}")
                else:
                    logger.warning(f"Image not found: {img_path}")
            
            c.save()
            logger.info("PDF Assembly complete.")
            return output_filename
            
        except Exception as e:
            logger.error(f"PDF Assembly failed: {e}")
            return None
