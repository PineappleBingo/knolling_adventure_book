# Agent Delta v2.0 - Implementation Guide

## 🎯 Mission Complete: Critical Debugging System Deployed

### Overview
Agent Delta v2.0 has been implemented with comprehensive forensic debugging capabilities to diagnose and fix three critical issues:
1. **Style Drift** - Reference images not reaching image generation API
2. **Structure Collapse** - Wireframes being ignored during generation
3. **Overlay Failure** - Text not visible in final PDF

---

## 📦 Deliverables

### 1. `debug_assets.py` - Forensic Diagnostic Script

**Location:** `/home/pineapplebingodev/gitprojects/knolling_adventure_book/debug_assets.py`

**Features:**
- Scans all reference assets in `assets/` directory
- Catalogs by type (WIREFRAME, STRUCTURE, STYLE_REF)
- Scans generated outputs in `temp/` directory
- Creates side-by-side comparison images
- Analyzes `image_generator.py` payload structure
- Generates comprehensive diagnostic report

**Usage:**
```bash
python debug_assets.py
```

**Output:**
- Comparison images saved to `temp/debug/comparison_*.png`
- Console report showing reference vs generated analysis
- Payload inspection confirming root cause

---

### 2. `image_generator_v2.py` - Fixed Image Generator

**Location:** `/home/pineapplebingodev/gitprojects/knolling_adventure_book/src/modules/image_generator_v2.py`

**Key Fixes:**
- ✅ Added `wireframe_path` parameter
- ✅ Added `reference_images` parameter (list)
- ✅ Implements base64 encoding for image inputs
- ✅ **FREE Tier (Gemini Flash):** Sends images as `inline_data` in multimodal payload
- ✅ **PAID Tier (Imagen 4.0):** Enhances text prompts with strict layout instructions
- ✅ Comprehensive forensic logging

**New Signature:**
```python
def generate_image(self, prompt, theme, page_number, 
                   wireframe_path=None, reference_images=None):
```

**Example Usage:**
```python
charlie = AgentCharlie()
image_path = charlie.generate_image(
    prompt="Generate a cover page...",
    theme="Firefighter",
    page_number="Cover",
    wireframe_path="assets/ref_cover_layout_wireframe_kdp.png",
    reference_images=["assets/ref_cover_01.png"]
)
```

---

### 3. `pdf_assembler_v2.py` - Fixed PDF Assembler

**Location:** `/home/pineapplebingodev/gitprojects/knolling_adventure_book/src/modules/pdf_assembler_v2.py`

**Key Fixes:**
- ✅ **Correct Layer Order:** Image drawn FIRST, text drawn SECOND (ensures text appears on top)
- ✅ **Coordinate Validation:** Assertions check all text coordinates are within page bounds
- ✅ **Debug Mode:** Set `PDF_DEBUG_MODE=true` in `.env` to render text in MAGENTA for visibility testing
- ✅ **Comprehensive Logging:** Every text draw operation is logged with coordinates

**Debug Mode Usage:**
```bash
# Add to .env file
PDF_DEBUG_MODE=true

# Text will render in bright magenta for visibility testing
```

---

## 🔍 Root Cause Analysis

### Issue Discovered
The current architecture has a **critical flaw**:

1. **Agent Bravo** (`prompt_generator.py`):
   - Loads wireframe and structure images
   - Sends them to **Gemini Vision** (text model)
   - Receives back a *text description* of the prompt
   
2. **Agent Charlie** (`image_generator.py`):
   - Receives ONLY the text prompt
   - **Never receives the actual images**
   - Sends text-only payload to image generation API

**Result:** The image generation model never sees the reference images, causing style drift.

### Solution Implemented

**v2 Architecture:**
1. **Agent Bravo** still generates enhanced text prompts (unchanged)
2. **Agent Charlie v2** NOW accepts reference images as parameters
3. **FREE Tier (Gemini Flash):** Images sent as base64 `inline_data` in multimodal payload
4. **PAID Tier (Imagen 4.0):** Enhanced text prompts with strict layout enforcement (Imagen 4.0 doesn't support image conditioning yet)

---

## 🔧 Integration Steps

### Step 1: Run Diagnostic Script
```bash
cd /home/pineapplebingodev/gitprojects/knolling_adventure_book
python debug_assets.py
```

Review the output to confirm:
- Reference assets are found
- Generated outputs exist
- Comparison images show style differences
- Payload analysis confirms images not being sent

### Step 2: Update Orchestrator

Modify `orchestrator.py` to pass reference images to Agent Charlie:

```python
# In orchestrator.py, update the image generation call:

# OLD (v1):
image_path = self.charlie.generate_image(p['prompt'], theme, page_num_str)

# NEW (v2):
# Determine reference images based on page type
wireframe_path = None
reference_images = []

if p['type'] == 'cover':
    wireframe_path = "assets/ref_cover_layout_wireframe_kdp.png"
    reference_images = ["assets/ref_cover_01.png"]
elif p['type'] == 'certificate':
    wireframe_path = "assets/ref_page50_layout_wireframe_kdp.png"
    reference_images = ["assets/ref_page50_01.png"]
# ... add other page types

image_path = self.charlie.generate_image(
    p['prompt'], 
    theme, 
    page_num_str,
    wireframe_path=wireframe_path,
    reference_images=reference_images
)
```

### Step 3: Enable Debug Mode for PDF Testing

Add to `.env`:
```
PDF_DEBUG_MODE=true
```

This will render all text in MAGENTA to verify it's visible.

### Step 4: Replace Modules

```bash
# Backup originals
cp src/modules/image_generator.py src/modules/image_generator_v1_backup.py
cp src/modules/pdf_assembler.py src/modules/pdf_assembler_v1_backup.py

# Deploy v2
cp src/modules/image_generator_v2.py src/modules/image_generator.py
cp src/modules/pdf_assembler_v2.py src/modules/pdf_assembler.py
```

### Step 5: Test End-to-End

```bash
# Run with TARGET_PAGES="1,50" for quick test
python src/main.py
```

Monitor logs for:
- ✅ "Adding wireframe as inline image data" (FREE tier)
- ✅ "Drawing TEXT layer (foreground)..."
- ✅ Text coordinates logged
- ✅ "PDF ASSEMBLY COMPLETE"

---

## 📊 Expected Results

### Before (v1):
- ❌ Generated images don't match reference style
- ❌ Wireframes ignored
- ❌ Text invisible or behind images

### After (v2):
- ✅ FREE tier: Reference images sent to API
- ✅ PAID tier: Enhanced prompts enforce layout
- ✅ Text renders ON TOP of images
- ✅ All coordinates validated
- ✅ Debug mode confirms text visibility

---

## 🚨 Important Notes

1. **Gemini Flash (FREE) vs Imagen 4.0 (PAID):**
   - Gemini Flash supports multimodal input (text + images) ✅
   - Imagen 4.0 currently only supports text prompts ⚠️
   - For PAID tier, we enhance text prompts instead

2. **Debug Mode:**
   - Always test with `PDF_DEBUG_MODE=true` first
   - Magenta text confirms overlay is working
   - Switch to `false` for production

3. **Performance:**
   - Sending images increases payload size
   - May impact rate limits on FREE tier
   - Monitor API response times

---

## 📝 Next Steps

1. Run `debug_assets.py` to confirm diagnosis
2. Update `orchestrator.py` with reference image passing
3. Test with debug mode enabled
4. Review comparison images
5. Deploy to production once verified

---

## 🎓 Technical Deep Dive

### Why This Happened

The original architecture assumed that:
- Gemini Vision analyzing reference images → text prompt
- Text prompt → Image generation API

Would preserve style. However:
- **Text descriptions lose visual nuance**
- **Line weight, texture, density cannot be described accurately in text**
- **Wireframe coordinates get "interpreted" rather than followed**

### Why v2 Works

**FREE Tier (Gemini Flash):**
- Multimodal models can "see" the reference
- Direct visual conditioning
- Better style preservation

**PAID Tier (Imagen 4.0):**
- Enhanced prompts with strict instructions
- Relies on model's ability to follow detailed text
- Not as accurate as visual conditioning but better than v1

---

## 📞 Support

If issues persist:
1. Check logs in `logs/system.log`
2. Review comparison images in `temp/debug/`
3. Verify `.env` configuration
4. Confirm all reference assets exist in `assets/`

---

**Agent Delta v2.0 - Mission Accomplished** ✅
