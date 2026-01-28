"""Quick PDF Debug Test"""
import os
import glob
from src.modules.pdf_assembler import AgentEcho

print("\n🔍 Testing PDF Debug Mode\n")

# Find existing images
test_images = sorted(glob.glob("temp/*Page*.png"), key=os.path.getmtime, reverse=True)[:2]

if not test_images:
    print("❌ No test images found in temp/")
    print("   Please run a generation first:")
    print("   python src/main.py")
    exit(1)

print(f"📄 Using {len(test_images)} test images:")
for img in test_images:
    print(f"   - {os.path.basename(img)}")

# Create PDF
echo = AgentEcho()
pdf_path = echo.assemble_pdf(test_images)

if pdf_path:
    print(f"\n✅ Test PDF created: {pdf_path}")
    print(f"🔍 Text should be MAGENTA for visibility testing")
    print(f"\n📖 Open the PDF to verify:")
    print(f"   xdg-open {pdf_path}")
else:
    print("\n❌ PDF creation failed - check logs")
