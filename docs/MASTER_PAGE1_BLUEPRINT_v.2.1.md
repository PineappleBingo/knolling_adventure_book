# MASTER PAGE BLUEPRINT: Internal Page Template
**Version:** 2.1 (Color-Coded Zones / KDP Compliant)
**Date:** December 22, 2025
**Trim Size:** 8.5" x 8.5" (215.9mm x 215.9mm)
**Bleed Settings:** 0.125" (3.175mm) added to outer edges.
**Total Canvas Dimensions:** 8.625" (W) x 8.75" (H) (Minimum required for bleed)
**Resolution:** 300 DPI (Grayscale/Black & White Output)

---

## 1. GLOBAL STYLE GUIDE (Critical for Consistency)
*All elements must strictly follow these rules to maintain the "Knolling Adventures" brand identity.*

### **A. Line Art Style**
* **Line Weight:** Thick, uniform mono-weight lines (approx 3pt-5pt).
* **Aesthetic:** "Clean Vector" style suitable for coloring. No sketching lines, no shading.
* **Closed Paths:** All shapes must be closed paths for easy coloring.

### **B. The "Sticker" Effect (Die-Cut Look)**
* **Outer Border:** Every object must have a **double outline** (Object Outline + White Gap + Outer Cut-Line).
* **Purpose:** Creates the illusion of physical die-cut stickers.

---

## 2. STATIC ZONES (Fixed Elements)
*These zones are PERMANENT. Use the specified colors for layout identification.*

### 🔴 ZONE 1: TITLE HEADER (Top Fixed)
* **[Layout ID Color]:** **RED**
* **Position:** Top Center (Inside Safe Margin).
* **Content:** Text "KNOLLING ADVENTURES".
* **Style:** "Titan One" font, heavy block style.
* **Layout Rule:** Must span 80% of page width. Fixed position.

### 🟡 ZONE 2: OWNERSHIP INTERACTION (Center Fixed)
* **[Layout ID Color]:** **YELLOW**
* **Position:** Visual Center of the Page.
* **Content:** Large Magnifying Glass illustration with text "THIS BOOK BELONGS TO:".
* **Layout Rule:** This is the central focal point. Zone 4 objects must flow *around* the Yellow zone.

### 🔵 ZONE 3: INSTRUCTION PANEL (Bottom Fixed)
* **[Layout ID Color]:** **BLUE**
* **Position:** Bottom Center anchor.
* **Content:** 3-Step Guide (Crayon/COLOR IT -> Eye/FIND IT -> Lightbulb/LEARN IT).
* **Layout Rule:** Defined by the Blue boundary at the bottom.

---

## 3. DYNAMIC ZONE (Variable Content)
*This zone is populated based on the input variable: `[THEME]`.*

### 🟢 ZONE 4: STICKER CLOUD ([THEME] Variable)
* **[Layout ID Color]:** **GREEN**
* **Input Variable:** `[THEME]` (e.g., Space, Magic, Construction)
* **Role:** Decor & Context.
* **Placement:** Fills the **Negative Space** surrounding the Red, Yellow, and Blue zones.

#### **Generation Rules for AI Agent:**
1.  **Scope:** Any object inside the **GREEN** boundary belongs to the Sticker Cloud.
2.  **Object Selection:** Generate 10-15 distinct items related to `[THEME]`.
3.  **No Duplicates:** **CRITICAL.** Do not repeat the exact same object file. (e.g., Use "Tall Potion" and "Round Potion" instead of two "Potions").
4.  **Knolling Layout:** Arrange items in an organized, "flat-lay" style without overlapping.
5.  **Separation:** Maintain a white space buffer between the Green zone stickers and the fixed Red/Yellow/Blue zones.
6.  **Boundaries:** Ensure all sticker art is drawn strictly **inside the Safe Zone margins**.

---

## 4. QUALITY CHECKLIST (Pre-Export)
1.  [ ] **Size Check:** Is canvas 8.625" x 8.75"?
2.  [ ] **Zone Identification:**
    * **RED:** Title is clear?
    * **YELLOW:** Center ownership panel is clear?
    * **BLUE:** Bottom instruction panel is clear?
    * **GREEN:** All theme stickers are distinct and non-overlapping?
3.  [ ] **Safety:** Are all critical elements inside the safe margin?