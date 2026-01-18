# 📘 MASTER BLUEPRINT: Page 50 (Certificate of Completion)

## 1. METADATA
* **Page ID:** `PAGE_50`
* **Type:** Variable Frame & Text Page (Dynamic Certificate)
* **Target Audience:** Kids (4-8 years)
* **Theme:** Firefighter (Default) / Variable for other themes
* **Canvas Size:** 8.625" x 8.75" (Square with Bleed)

## 2. ASSET MANIFEST
| Asset ID | Filename | Description | Usage |
| :--- | :--- | :--- | :--- |
| **Reference Art** | `ref_page50_01.png` | Original Visual Target | Style & Layout Reference |
| **Structure Map** | `ref_page50_structure_example.png` | Zone Guide (Human View) | Coordinate Planning |
| **Production Wireframe** | `ref_page50_layout_wireframe_kdp.png` | **Colorized Skeleton** | **Base Canvas for Python Script** |

---

## 3. LAYOUT SPECIFICATIONS (The Zones)

### 🟥 ZONE 1: THEME FRAME (Variable)
* **Location:** The track between the Outer Red Line and Inner Red Line.
* **Content:** **[THEME] Objects** (e.g., Firefighter tools, Space gear, Dinosaur bones).
* **Generation Rule:**
    * Items must be **Knolled** (neatly arranged).
    * Items must be **Upright** (not rotated randomly).
    * **Density:** High (fill the track but allow small white gaps).
* **Production Note:** The Red Lines are for detection only. **They must be removed or recolored to BLACK in the final output.**

### 🟦 ZONE 2: BADGE (Fixed)
* **Location:** Bottom Left Corner (Blue Circle).
* **Content:** "OFFICIAL EXPLORE" Ribbon Badge.
* **Status:** **Pre-rendered** in the wireframe. Do not overwrite unless changing the badge text.

### 🟩 ZONE 3: TEXT AREA (Variable)
* **Location:** Inside the Inner Green Line (Center Panel).
* **Content:** Dynamic Text Injection.
* **Typography Rules:**
    * **Header:** "CONGRATULATIONS!" (Font: Titan One, Size: 60pt, Style: Outline/Hollow).
    * **Body:** "This certifies that" (Sans-Serif, Small).
    * **Name Line:** "_____________________" (Line).
    * **Theme Title:** "[THEME] ADVENTURES" (Font: Chunky Bold, Size: 45pt, Uppercase).
    * **Signature:** "Parent/Guardian Signature: ___________ Date: ____".
* **Production Note:** The Green Line indicates the text boundary. **It must be removed or recolored to BLACK in the final output.**

---

## 4. PROMPT ENGINEERING (For Dynamic Content)

### 🎨 Generation Prompt (Zone 1 - Frame Filling)
> **Role:** Technical Illustrator
> **Task:** Draw a set of **[Current Theme]** objects arranged in a neat frame.
> **Style:** Heroic Cute, Chunky Line Art, Black & White.
> **Layout:** Generate items ONLY inside the detected mask area (Zone 1).
> **Items:** [List of Theme Items, e.g., Helmet, Axe, Hose].

---

## 5. TECHNICAL PRODUCTION RULES (Critical)

### ⚠️ The "Colorized Wireframe" Protocol
Since the base wireframe (`ref_page50_layout_wireframe_kdp.png`) contains **colored guide lines (Red/Green/Blue)**, the Production Script (Python) must perform the following **Post-Processing Steps**:

1.  **Load Wireframe:** Load `ref_page50_layout_wireframe_kdp.png`.
2.  **Detect Zones:** Use the Red/Green colors to define the masking areas for Inpainting (Zone 1) and Text placement (Zone 3).
3.  **Generate Content:** Fill Zone 1 with art and Zone 3 with text.
4.  **Final Polish (The "De-Colorize" Step):**
    * **Convert Red/Green Lines to BLACK:** If the lines are intended to be the final border.
    * **OR Remove Colors:** Apply a `Grayscale` or `Threshold` filter to ensure the final PDF is 100% Black & White (KDP Requirement). **Do NOT print Red/Green lines in the final book.**

---

## 6. STRATEGY NOTE: "Schematic Reconstruction"
* **Issue:** AI struggled to "erase" complex objects inside the frame while keeping the frame intact.
* **Solution:** We used a **"Schematic Reconstruction"** prompt strategy.
    * *Instead of asking to "edit/erase", we asked to "redraw the diagram as an empty schematic".*
* **Usage:** Use this strategy for any future page where "erasing" fails.