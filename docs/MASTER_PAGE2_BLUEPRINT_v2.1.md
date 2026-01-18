# MASTER PAGE BLUEPRINT: Page 2 (Note to Parents)
**Version:** 2.1 (Hybrid Layout / KDP Compliant)
**Date:** December 27, 2025
**Trim Size:** 8.5" x 8.5" (215.9mm x 215.9mm)
**Bleed Settings:** 0.125" (3.175mm) added to outer edges.
**Total Canvas Dimensions:** 8.625" (W) x 8.75" (H)
**Resolution:** 300 DPI (Grayscale/Black & White Output)

---

## 1. GLOBAL STYLE GUIDE
* **Line Art:** Thick, uniform mono-weight lines (approx 3pt-5pt).
* **Composition:** Minimalist. High readability.
* **Hybrid Model:** This page uses a **"Visuals First, Text Second"** approach. The AI generates the frame and icon; Python overlays the text.

---

## 2. ZONE LEGEND (Layout Map)
*Refer to `ref_page2_structure_example.png` for visual confirmation.*

### 🟥 ZONE 1: FIXED FRAME (Outer Border)
* **[Layout ID Color]:** **RED**
* **Type:** Visual Element (AI Generated / Fixed Asset)
* **Description:** Single thick black rectangular border with **Rounded Corners**.
* **Position:** Fixed margin (approx 0.5" from edge).

### 🟩 ZONE 3: TITLE AREA (Header)
* **[Layout ID Color]:** **GREEN**
* **Type:** **TEXT OVERLAY (Agent Echo)**
* **Content:** "A NOTE TO PARENTS:"
* **Font:** Titan One (Regular), ~40pt.
* **Rule:** The AI must leave this area **PURE WHITE**.

### 🟨 ZONE 4: BODY TEXT AREA (Center)
* **[Layout ID Color]:** **YELLOW**
* **Type:** **TEXT OVERLAY (Agent Echo)**
* **Content:** Instructions regarding crayon usage and marker warnings.
* **Font:** Quicksand (Bold), ~18pt.
* **Rule:** The AI must leave this area **PURE WHITE**.

### 🟦 ZONE 5: MARKER ICON (Visual Anchor)
* **[Layout ID Color]:** **BLUE**
* **Type:** Visual Element (AI Generated)
* **Content:** "No Markers" Icon (Marker pen inside a prohibition circle).
* **Style:** Thick vector lines, matching the border style.
* **Position:** Bottom Center, anchored below the text.

### 🟪 ZONE 6: COPYRIGHT AREA (Footer)
* **[Layout ID Color]:** **PURPLE**
* **Type:** **TEXT OVERLAY (Agent Echo)**
* **Content:** "Copyright © 2025 by PapaBingo. All rights reserved."
* **Font:** Sniglet (Regular), ~10pt.
* **Position:** Inside the border, bottom centered.

---

## 3. ASSET MANIFEST
1.  **`ref_page2_01.png`**: Original Approved Design (Visual Target).
2.  **`ref_page2_structure_example.png`**: Layout Guide with Color Zones.
3.  **`ref_page2_layout_wireframe_kdp.png`**: Production Mask (Clean White Background).

---

## 4. GENERATION RULES (For Agent Charlie)
* **Prompt Strategy:** "Draw a clean white page with a thick black rounded rectangular border (Zone 1) and a bold 'No Markers' icon (Zone 5) at the bottom center. **LEAVE THE CENTER COMPLETELY EMPTY.** No text, no scribbles."
* **Inpainting:** Not required for this page (Static Layout).