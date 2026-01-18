# MASTER PAGE BLUEPRINT: Page 5 (Action Scene)
**Version:** 2.1 (Full Bleed / Safety Masking)
**Date:** January 13, 2026
**Trim Size:** 8.5" x 8.5" (215.9mm x 215.9mm)
**Bleed Settings:** 0.125" (3.175mm) added to outer edges.
**Total Canvas Dimensions:** 8.625" (W) x 8.75" (H)
**Resolution:** 300 DPI (Grayscale/Black & White Output)

---

## 1. GLOBAL STYLE GUIDE
* **Line Art:** Thick, uniform mono-weight lines (approx 3pt-5pt).
* **Style:** "Heroic Cute & Chunky". Friendly, safe, toy-like proportions.
* **Composition Strategy:** **"Centralized Island"**. Keep the main action in the center to prevent binding issues.
* **Logic:** "Match the Tools". The character MUST use the tools displayed on Page 4.

---

## 2. ZONE LEGEND (Layout Map)
*Refer to `ref_page5_structure_example.png` for Visual QA.*

### 🟩 ZONE 1: SAFE ZONE (Fixed Mask)
* **[Layout ID Color]:** **GREEN** (#00FF00) / **Source:** `ref_page5_layout_wireframe_kdp.png`
* **Type:** Safety Boundary & Production Mask.
* **Position:** 0.375" (9.5mm) from all trim edges.
* **Role:**
    1.  **Visual QA:** Any critical element (Face, Tool) touching this green line is a FAIL.
    2.  **Production:** Python script uses this green box to locate the center coordinates.

### ⬜ ZONE 2: ACTION STAGE (Dynamic Content)
* **[Layout ID Color]:** **WHITE (Void)**
* **Type:** Dynamic Illustration Area.
* **Content:** [THEME] Character in "Action in Motion".
* **Generation Rule:**
    * Input: `[THEME]`, `[TOOL_LIST_FROM_PAGE_4]`
    * Output: Dynamic pose using the tools.
    * Constraint: "Zoom Out" slightly to ensure white padding around the character.

---

## 3. ASSET MANIFEST
1.  **`ref_page5_01.png`**: Master Visual Target (Style/Line Weight Reference).
2.  **`ref_page5_structure_example.png`**: Visual QA Guide (With Character + Border).
3.  **`ref_page5_layout_wireframe_kdp.png`**: Production Mask (Empty Center + Border).

---

## 4. QUALITY CHECKLIST (Pre-Export)
1.  [ ] **Safety Check:** Is the Main Character fully inside the Green Zone?
2.  [ ] **Gutter Check:** Is the left side (Spine) clear of critical details?
3.  [ ] **Logic Check:** Is the character holding the correct tool from Page 4?
4.  [ ] **Style Check:** Are the lines thick and uniform (No sketch lines)?