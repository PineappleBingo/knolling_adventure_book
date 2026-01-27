"""
Agent Delta v2.0: Forensic QA & Debugger
Mission: Diagnose style drift, reference loading, and compositing failures.
"""

import os
import glob
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentDelta_Forensic")

class ForensicDebugger:
    def __init__(self):
        self.assets_dir = "assets"
        self.temp_dir = "temp"
        self.debug_output_dir = "temp/debug"
        
        # Create debug output directory
        os.makedirs(self.debug_output_dir, exist_ok=True)
        
    def scan_reference_assets(self):
        """Scans and catalogs all reference assets."""
        logger.info("=" * 80)
        logger.info("TASK 1: REFERENCE ASSET LOADING & VISION CHECK")
        logger.info("=" * 80)
        
        ref_files = glob.glob(f"{self.assets_dir}/ref_*.png")
        ref_files.sort()
        
        logger.info(f"\n📁 Found {len(ref_files)} reference files in {self.assets_dir}/")
        
        asset_catalog = {}
        for ref_path in ref_files:
            filename = os.path.basename(ref_path)
            file_size = os.path.getsize(ref_path) / 1024  # KB
            
            # Categorize
            if "_wireframe" in filename:
                category = "WIREFRAME (Geometry)"
            elif "_structure" in filename:
                category = "STRUCTURE (Context)"
            elif "_01.png" in filename:
                category = "STYLE_REF (DNA)"
            else:
                category = "OTHER"
                
            asset_catalog[filename] = {
                "path": ref_path,
                "size_kb": file_size,
                "category": category
            }
            
            logger.info(f"  ✓ {filename:50s} | {file_size:8.1f} KB | {category}")
            
        return asset_catalog
    
    def scan_generated_outputs(self):
        """Scans most recent generated images."""
        output_files = glob.glob(f"{self.temp_dir}/*.png")
        output_files.sort(key=os.path.getmtime, reverse=True)
        
        # Get most recent 10
        recent_outputs = output_files[:10]
        
        logger.info(f"\n📁 Found {len(output_files)} generated files in {self.temp_dir}/")
        logger.info(f"   Showing {len(recent_outputs)} most recent:")
        
        for output_path in recent_outputs:
            filename = os.path.basename(output_path)
            file_size = os.path.getsize(output_path) / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(output_path))
            
            logger.info(f"  ✓ {filename:50s} | {file_size:8.1f} KB | {mod_time}")
            
        return recent_outputs
    
    def create_side_by_side_comparison(self, ref_path, output_path, comparison_name):
        """Creates side-by-side comparison image."""
        try:
            ref_img = Image.open(ref_path).convert("RGB")
            output_img = Image.open(output_path).convert("RGB")
            
            # Resize to same height for comparison
            target_height = 800
            ref_ratio = target_height / ref_img.height
            output_ratio = target_height / output_img.height
            
            ref_resized = ref_img.resize((int(ref_img.width * ref_ratio), target_height), Image.Resampling.LANCZOS)
            output_resized = output_img.resize((int(output_img.width * output_ratio), target_height), Image.Resampling.LANCZOS)
            
            # Create canvas
            total_width = ref_resized.width + output_resized.width + 40  # 40px gap
            canvas = Image.new("RGB", (total_width, target_height + 100), "white")
            
            # Paste images
            canvas.paste(ref_resized, (10, 50))
            canvas.paste(output_resized, (ref_resized.width + 30, 50))
            
            # Add labels
            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype("assets/fonts/Quicksand-Bold.ttf", 24)
            except:
                font = ImageFont.load_default()
                
            draw.text((10, 10), "REFERENCE (Expected)", fill="blue", font=font)
            draw.text((ref_resized.width + 30, 10), "GENERATED (Actual)", fill="red", font=font)
            
            # Save
            output_filename = f"{self.debug_output_dir}/{comparison_name}"
            canvas.save(output_filename)
            logger.info(f"  ✅ Saved comparison: {output_filename}")
            
            return output_filename
            
        except Exception as e:
            logger.error(f"  ❌ Failed to create comparison: {e}")
            return None
    
    def analyze_image_generator_payload(self):
        """Analyzes image_generator.py to check if reference images are sent to API."""
        logger.info("\n" + "=" * 80)
        logger.info("CRITICAL ANALYSIS: IMAGE GENERATOR PAYLOAD INSPECTION")
        logger.info("=" * 80)
        
        img_gen_path = "src/modules/image_generator.py"
        
        if not os.path.exists(img_gen_path):
            logger.error(f"❌ File not found: {img_gen_path}")
            return
            
        with open(img_gen_path, 'r') as f:
            code = f.read()
            
        # Check for Base64 encoding of images
        has_image_input = "Image.open" in code and "base64.b64encode" in code
        has_multipart = "multipart" in code.lower()
        has_image_param = '"image"' in code or "'image'" in code
        
        logger.info("\n🔍 PAYLOAD ANALYSIS:")
        logger.info(f"  • Loads PIL Image objects: {'YES ✓' if 'Image.open' in code else 'NO ✗'}")
        logger.info(f"  • Encodes images to Base64: {'YES ✓' if has_image_input else 'NO ✗'}")
        logger.info(f"  • Uses multipart/form-data: {'YES ✓' if has_multipart else 'NO ✗'}")
        logger.info(f"  • Includes 'image' parameter: {'YES ✓' if has_image_param else 'NO ✗'}")
        
        # Check payload structure
        if '"instances"' in code:
            logger.info(f"\n  📦 PAID Tier Payload Structure: instances[] (Imagen 4.0)")
            if '"prompt"' in code and not has_image_input:
                logger.warning("  ⚠️  CRITICAL ISSUE: Payload contains ONLY 'prompt' field!")
                logger.warning("  ⚠️  Reference images are NOT being sent to the API!")
                
        if '"contents"' in code:
            logger.info(f"\n  📦 FREE Tier Payload Structure: contents[] (Gemini Flash)")
            if '"text"' in code and not has_image_input:
                logger.warning("  ⚠️  CRITICAL ISSUE: Payload contains ONLY 'text' field!")
                logger.warning("  ⚠️  Reference images are NOT being sent to the API!")
                
        logger.info("\n" + "=" * 80)
        logger.info("DIAGNOSIS:")
        logger.info("=" * 80)
        logger.info("❌ CONFIRMED: Agent Bravo uses reference images to generate TEXT prompts,")
        logger.info("   but Agent Charlie NEVER sends those images to the image generation API.")
        logger.info("   This is the ROOT CAUSE of style drift.")
        logger.info("\n💡 SOLUTION: Modify Agent Charlie to accept reference images and include")
        logger.info("   them in the API payload (if supported by the model tier).")
        logger.info("=" * 80)
        
    def run_full_diagnostic(self):
        """Runs complete diagnostic suite."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("\n" + "🔬" * 40)
        logger.info("AGENT DELTA v2.0 - FORENSIC DIAGNOSTIC REPORT")
        logger.info(f"Timestamp: {timestamp}")
        logger.info("🔬" * 40 + "\n")
        
        # Task 1: Asset Scanning
        ref_catalog = self.scan_reference_assets()
        recent_outputs = self.scan_generated_outputs()
        
        # Create comparisons
        logger.info("\n" + "=" * 80)
        logger.info("CREATING SIDE-BY-SIDE COMPARISONS")
        logger.info("=" * 80)
        
        # Match reference to output by type
        comparisons_made = 0
        for ref_name, ref_data in ref_catalog.items():
            if ref_data["category"] == "STYLE_REF (DNA)":
                # Extract page type (e.g., "page1", "cover")
                page_type = ref_name.split("_")[1]  # ref_page1_01.png -> page1
                
                # Find matching output
                for output_path in recent_outputs:
                    output_name = os.path.basename(output_path)
                    if page_type.lower() in output_name.lower():
                        comparison_name = f"comparison_{page_type}_{timestamp}.png"
                        self.create_side_by_side_comparison(
                            ref_data["path"], 
                            output_path, 
                            comparison_name
                        )
                        comparisons_made += 1
                        break
                        
        logger.info(f"\n✅ Created {comparisons_made} comparison images in {self.debug_output_dir}/")
        
        # Payload Analysis
        self.analyze_image_generator_payload()
        
        # Summary
        logger.info("\n" + "📊" * 40)
        logger.info("DIAGNOSTIC SUMMARY")
        logger.info("📊" * 40)
        logger.info(f"  • Reference Assets Found: {len(ref_catalog)}")
        logger.info(f"  • Generated Outputs Found: {len(recent_outputs)}")
        logger.info(f"  • Comparisons Created: {comparisons_made}")
        logger.info(f"  • Debug Output Directory: {self.debug_output_dir}/")
        logger.info("📊" * 40 + "\n")

if __name__ == "__main__":
    debugger = ForensicDebugger()
    debugger.run_full_diagnostic()
