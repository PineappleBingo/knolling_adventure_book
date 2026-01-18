# MASTER PAGE BLUEPRINT: Page 3 (Mission Start)
**Version:** 2.0 (Production Ready / KDP Compliant)
**Date:** December 30, 2025
**Trim Size:** 8.5" x 8.5"
**Bleed Settings:** 0.125" (3.175mm) added to outer edges.
**Total Canvas Dimensions:** 8.625" (W) x 8.75" (H)
**Resolution:** 300 DPI (Grayscale)

---

## 1. GLOBAL STYLE GUIDE (Heroic Cute)
* **Visual Identity:** "Chunky, Rounded, Safe". No sharp/scary edges.
* **Line Art:** Thick, uniform vector lines (3pt-5pt).
* **Text Style:** **HOLLOW OUTLINE**. All text must be white inside with a black stroke so kids can color the letters.

---

## 2. ZONE LEGEND (Layout Map)
*Refer to `ref_page3_layout_wireframe_kdp.png` for zone coordinates.*

### 🟥 ZONE 1: FIXED FRAME (Red)
* **Type:** Static Asset (Preserved from Reference)
* **Description:** Thick black rounded rectangular border with 0.5" margin.

### 🟦 ZONE 2: TOP TITLE (Blue)
* **Type:** **TEXT OVERLAY (Agent Echo)**
* **Content:** "ARE YOU READY TO EXPLORE?"
* **Font:** `TitanOne-Regular.ttf`
* **Style:** **Outlined Text (Stroked)**. Stroke Width: 2pt. Fill: White.
* **Position:** Top Center, inside the frame.

### 🟩 ZONE 3: GEAR BAG (Green)
* **Type:** **VARIABLE GENERATION (Agent Charlie)**
* **Input Variable:** `[THEME]` (e.g., Firefighter, Space, Construction)
* **Role:** Inpainting Target.
* **Prompt:** "A cute, chunky **[THEME] Backpack** sitting on the ground. Inside the open bag, 3-4 distinct **[THEME] Tools** are sticking out. Thick vector lines, white background."
* **Constraint:** Must fit strictly inside the Green Box area.

### 🟨 ZONE 4: ACTION ARROW (Yellow)
* **Type:** Static Asset (Preserved from Reference)
* **Description:** Thick bubble-style arrow pointing right.
* **Rule:** Do NOT regenerate. Keep original.

### 🟪 ZONE 5: BOTTOM TEXT (Purple)
* **Type:** **TEXT OVERLAY (Agent Echo)**
* **Content:** "TURN THE PAGE TO START YOUR FIRST MISSION!"
* **Font:** `TitanOne-Regular.ttf`
* **Style:** **Outlined Text (Stroked)**. Stroke Width: 2pt. Fill: White.
* **Position:** Bottom Center, inside the frame.

---

## 3. ASSET MANIFEST
1.  **`ref_page3_01.png`**: Original Concept.
2.  **`ref_page3_structure_example.png`**: Structure Map with Labels.
3.  **`ref_page3_layout_wireframe_kdp.png`**: Production Mask (Clean White Background).