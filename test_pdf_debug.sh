#!/bin/bash
# Quick Test Script for PDF_DEBUG_MODE
# This script automates the testing process

echo "🔬 PDF_DEBUG_MODE Quick Test Script"
echo "===================================="
echo ""

# Step 1: Enable Debug Mode
echo "Step 1: Enabling PDF_DEBUG_MODE..."
if grep -q "PDF_DEBUG_MODE" .env; then
    sed -i 's/PDF_DEBUG_MODE=.*/PDF_DEBUG_MODE=true/' .env
    echo "✅ Updated PDF_DEBUG_MODE=true"
else
    echo "PDF_DEBUG_MODE=true" >> .env
    echo "✅ Added PDF_DEBUG_MODE=true to .env"
fi
echo ""

# Step 2: Backup Original Modules
echo "Step 2: Creating backups..."
if [ ! -f "src/modules/pdf_assembler_v1_backup.py" ]; then
    cp src/modules/pdf_assembler.py src/modules/pdf_assembler_v1_backup.py
    echo "✅ Backed up pdf_assembler.py"
else
    echo "ℹ️  Backup already exists"
fi
echo ""

# Step 3: Deploy v2 PDF Assembler
echo "Step 3: Deploying v2 PDF Assembler..."
if [ -f "src/modules/pdf_assembler_v2.py" ]; then
    cp src/modules/pdf_assembler_v2.py src/modules/pdf_assembler.py
    echo "✅ Deployed pdf_assembler_v2.py"
else
    echo "❌ ERROR: pdf_assembler_v2.py not found!"
    echo "   Please ensure v2 modules are created first."
    exit 1
fi
echo ""

# Step 4: Create Quick Test Script
echo "Step 4: Creating test script..."
cat > test_pdf_debug_quick.py << 'EOF'
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
EOF

echo "✅ Created test_pdf_debug_quick.py"
echo ""

# Step 5: Run Test
echo "Step 5: Running test..."
echo "========================================"
python test_pdf_debug_quick.py
echo "========================================"
echo ""

# Step 6: Show Results
echo "📊 Test Complete!"
echo ""
echo "Next Steps:"
echo "1. Open the generated PDF (should have MAGENTA text)"
echo "2. If text is visible and magenta → SUCCESS! ✅"
echo "3. If no text visible → Check logs/system.log"
echo ""
echo "To disable debug mode:"
echo "  sed -i 's/PDF_DEBUG_MODE=true/PDF_DEBUG_MODE=false/' .env"
echo ""
echo "To rollback to v1:"
echo "  cp src/modules/pdf_assembler_v1_backup.py src/modules/pdf_assembler.py"
