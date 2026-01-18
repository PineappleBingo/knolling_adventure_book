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
                        # In a real app, we'd handle left/right page positioning specifically
                        # For now, we just center/fill
                        c.drawImage(processed_img_path, 0, 0, width=self.width, height=self.height)
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
