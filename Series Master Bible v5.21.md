# SERIES MASTER BIBLE: Knolling Adventures
**Version:** 5.21
**Last Updated:** January 16, 2026
**Platform:** Amazon KDP (Paperback)
**Target Audience:** Ages 4–8

---

## 0.0 SYSTEM CONFIGURATION (Central Control)
*All Agents must reference these variables. Note: `GEN_MODEL_ID` and Delays may be overridden by Agent Alpha's Deployment Tier logic.*

### [SYSTEM_CONFIG_VARS]
* **Physical Specs (Amazon KDP):**
    * `TRIM_WIDTH`: **8.5"**
    * `TRIM_HEIGHT`: **8.5"**
    * `BLEED_SIZE`: **0.125"**
    * `SAFE_MARGIN`: **0.375"** (Critical Art/Text Safety Zone)
    * `PAGE_COUNT`: **50 Pages** (Default)
* **Typography Assets (Google Fonts):**
    * `FONT_TITLE_MAIN`: **"TitanOne-Regular.ttf"**
    * `FONT_SUBTITLE`: **"FredokaOne-Regular.ttf"**
    * `FONT_BODY_TEXT`: **"Quicksand-Bold.ttf"**
    * `FONT_HANDWRITING`: **"PatrickHand-Regular.ttf"**
    * `FONT_LEGAL`: **"Sniglet-Regular.ttf"**
* **File Paths:**
    * `PATH_ASSETS`: "assets/"
    * `PATH_FONTS`: "assets/fonts/"
    * `MASTER_REF_IMG`: "assets/ref_pag2_01.png"
* **AI Models & Settings (Defaults):**
    * `GEN_MODEL_ID`: "models/imagen-4.0-generate-001" (See Agent Alpha for Tier Logic)
    * `QA_MODEL_ID`: "models/gemini-2.0-flash-exp" (or latest stable)
    * `MAX_RETRIES`: 3
    * `GEN_DELAY`: 2.0 (seconds)

---

## 0. THE AGENT MANIFEST (Engineering Architecture)
*Use this manifest to instruct the AI IDE on how to build the Python application.*

### 0.1 TECHNICAL SPECIFICATIONS (The Stack)
* **Core Python Libs:**
    * `python-telegram-bot` (Async interface for UI)
    * `google-generativeai` (Strictly for Text/QA/Vision Analysis via Gemini)
    * `requests` (**CRITICAL:** Used for Image Generation via Direct REST API)
    * `pillow` (Image processing & Grayscale conversion)
    * `reportlab` (PDF assembly & **Text Compositing**)
    * `pydrive2` & `gspread` (Cloud Storage/Tracking)
    * `python-dotenv` (Env variables)
    * `glob` (File pattern matching)
* **Assets Structure:**
    * `{PATH_FONTS}` (**REQUIRED:** Store Google Fonts .ttf files defined in **0.0 SYSTEM_CONFIG**)
    * `{MASTER_REF_IMG}` (**MASTER REFERENCE:** The fixed layout source for Page 2)
    * `assets/logo.png` (Author Branding)
* **Constraint - NO VERTEX AI:**
    * Agents must **NEVER** import `vertexai` or `google.cloud.aiplatform`.
* **Constraint - IMAGE GENERATION STRATEGY:**
    * **Agent Charlie** must use the **Direct REST API** via `requests`.
    * **Model ID:** `{GEN_MODEL_ID}` (Refer to Section 0.0 and Agent Alpha).
    * **Protocol:** `requests.post()` with `x-goog-api-key`.
    * **Payload Protocol (JSON Structure):**
        ```json
        {
          "instances": [ { "prompt": "YOUR PROMPT HERE" } ],
          "parameters": { "sampleCount": 1, "aspectRatio": "1:1" }
        }
        ```

### 👑 Agent Omega: Senior Project Manager (Orchestrator)
* **Mission:** Coordinate the lifecycle and handle errors.
* **Tasks:**
    * **Workflow:** UI Trigger -> Golf Log -> Bravo (Prompts) -> Loop [Charlie (Gen) -> Delta (QA)] -> **Echo (Compositing & PDF)** -> Foxtrot (Proof) -> Upload.
    * **Conflict Check:** Ensure Bravo DOES NOT request text in prompts for Page 2, so Echo can overlay text safely without collision.
    * **Safety Net:** Wrap `run_job()` in a global `try/except`.

### 👨‍💻 Agent Alpha: Senior Systems Architect (Infrastructure)
* **Mission:** Configuration & Resource Loading.
* **Tasks:**
    * **Config.py:** Load `{PAGE_COUNT}` and `DEPLOYMENT_TIER`.
    * **Deployment Tiers Logic (Environment Control):**
        * **IF FREE (Gemini Tier):**
            * `IMG_MODEL` = `models/gemini-2.0-flash-exp` (Fallback)
            * `QA_MODEL` = `models/gemini-2.5-pro` (Smartest Available)
            * `QA_DELAY` = 35 seconds (Strict Rate Limit)
            * `GEN_DELAY` = 20 seconds
        * **IF PAID (Imagen Tier):**
            * `IMG_MODEL` = `models/imagen-4.0-generate-001` (High Fidelity)
            * `QA_MODEL` = `models/gemini-2.5-pro` (Smartest Available)
            * `QA_DELAY` = 0.5 seconds
            * `GEN_DELAY` = 0.5 seconds
    * **Font Loader:** Ensure all `.ttf` files defined in **Section 0.0** are registered with `reportlab` at startup. If missing, raise `FileNotFoundError`.

### 🎨 Agent Bravo: Executive Creative Director (Prompt Logic)
* **Mission:** Enforce the **"Triangulation Strategy"** and **"Negative Prompt Logic"** to ensure style consistency and KDP compliance.
* **Tasks:**
    * **Discovery (Smart Filtering):**
        * Target **ONLY** pure visual references using the pattern: `assets/ref_*_01.png`.
        * **CRITICAL SAFETY PROTOCOL:** Explicitly **IGNORE** and **EXCLUDE** any files containing terms like `_structure`, `_wireframe`, `_layout`, or `_kdp`. These are technical guides, NOT style references.
    * **Triangulation Execution:**
        1.  **Anchor (Base DNA):** Load the strictly defined `[DNA_*]` macro from **Section 5.0**.
        2.  **Constraint (Layout):** Apply hard layout rules from the corresponding `GLOBAL_BLUEPRINT_SPECS` in **Section 1.6**.
        3.  **Nuance (Injection):** Analyze the filtered `*_01.png` image. Extract *only* texture/lighting/density nuances and inject them into the prompt. **NEVER** overwrite the Base DNA's line weight or safety zone rules.
    * **Negative Prompt Injection:**
        * Explicitly append the relevant **Negative DNA** from **Section 5.2** to every prompt generated.

### 🖌️ Agent Charlie: Lead Technical Artist (Image Generation)
* **Mission:** Manage the API Loop via REST (Imagen 4.0).
* **Tasks:**
    * **Output:** Pure visual assets (Backgrounds, Borders, Icons) without text artifacts.
    * **Rate Limiting:** Apply `time.sleep({GEN_DELAY})` after every call (Value determined by Agent Alpha).

### 🔍 Agent Delta: Senior Pre-Press Quality Manager (QA Guard)
* **Mission:** Enforce Quality Control (No Shading/Color).
* **Tasks:**
    * **Model:** Use **Gemini 2.5 Pro** (or `{QA_MODEL_ID}`).
    * **Retry Logic:** Max `{MAX_RETRIES}` Retries.

### 📐 Agent Echo: Senior Publishing Engineer (Compositing & Assembly)
* **Mission:** PDF Assembly & **Text Overlay Engine**.
* **CRITICAL TASK - HYBRID TEXT COMPOSITING:**
    * Instead of relying on AI to generate text, Agent Echo must **programmatically draw text** onto the images using `reportlab`.
    * **Source of Truth:** **Refer strictly to Section 1.6 (GLOBAL_BLUEPRINT_SPECS)** for all text content, fonts, sizes, and coordinate positioning. Do NOT hardcode text strings here.
    * **Safety Zone Check:** Ensure all text is within the `{SAFE_MARGIN}` safe margin.
    * **[PROTOCOL_COLOR_MASKING] (Page 50 & Complex Layouts):**
        * **Trigger:** When processing Page 50 or pages with `_wireframe_kdp.png` containing Color (Red/Green/Blue).
        * **Action:**
            1.  **Load Wireframe:** Load the specific wireframe defined in Section 1.6.
            2.  **Detect Zones:** Use Red/Green/Blue channels to define masking coordinates.
            3.  **De-Colorize:** After content generation and text overlay, apply a **Grayscale** or **Threshold** filter to the final output.
            4.  **Final Polish:** Ensure NO Red/Green lines remain in the printable PDF. The final output must be 100% Black & White.

### 📊 Agent Golf: Production Analyst (Tracking)
* **Mission:** Google Sheet "Mission Control".
* **Tasks:** Update status rows asynchronously.

### 🤖 Agent Foxtrot: Lead UX Engineer (Interface)
* **Mission:** Telegram Dashboard.
* **Tasks:** Live Dashboard updates and Proofing Album delivery.

---

## 1. Core Design Rules (The Constants)

### 1.1 The "Game Mechanic" (Spread Logic)
* **Left Page (Even):** **THE GEAR (Knolling).** A neat, flat-lay grid of the items/parts.
* **Right Page (Odd):** **THE ACTION (Scene).** Full Bleed with Centralized Island Strategy. The character/creature using those items in a full background.
    * **Regulation:** Action pages do NOT use a fixed border (Full Bleed). Instead, to ensure safety during Binding and Trimming, the Character and Key Tools must be strictly clustered in the center (inside the Safe Zone), creating a 'Visual Island' composition that prevents any critical art from touching the trim edges.
* **Goal:** "Match the Item to the Action."

### 1.2 Visual Style (Age 4-8)
* **Definition:** **"Heroic Cute & Chunky"**
* **Concept:** Bold, safe, toy-like.
* **Line Quality:** Thick, uniform vector lines (Chunky). No sketching, no grayscale.
* **Shape:** Rounded corners (Safety), Toy-like proportions, but maintains **Functional Recognizability** (An axe must look like an axe).
* **Avoid:** Babyish distortion or wobble.
* **Master Reference (Page 2):** Use `{MASTER_REF_IMG}` to ensure the border thickness and icon position are identical across all books.
* **Composition:**
    * *Left:* Clean white background, distinct object separation.
    * *Right:* Immersive, full-bleed background.
* **Character Style:** Modern cartoon style (like PAW Patrol/PJ Masks). Heroic proportions (not babyish), expressive eyes with pupils, detailed gear textures.

### 1.3 Typography (Google Fonts)
*All fonts must be open-source (OFL) via Google Fonts. Refer to `0.0 SYSTEM_CONFIG` for filenames.*
* **Titles:** **`{FONT_TITLE_MAIN}`** (Thick, Display).
* **Subtitles:** **`{FONT_SUBTITLE}`** (Rounded).
* **Body:** **`{FONT_BODY_TEXT}`** (Bold/Medium).
* **Handwriting:** **`{FONT_HANDWRITING}`**.
* **Legal/Copyright:** **`{FONT_LEGAL}`**.

### 1.4 KDP Technical Specifications (MANDATORY)
* **Trim Size:** `{TRIM_WIDTH}` x `{TRIM_HEIGHT}` (Final Book Size).
* **Internal Page Canvas:** **8.625" x 8.75"**
    * *Bleed:* Includes `{BLEED_SIZE}` bleed on top, bottom, and outer edge.
* **Cover Spread Canvas:** **17.365" x 8.75"**
    * *Calculation:* (8.5" Back + 0.115" Spine + 8.5" Front) + 0.125" Bleed all around.
* **Safe Zone:** All critical text/art must be `{SAFE_MARGIN}` (9.6mm) inside the trim line.
* **Resolution:** 300 DPI minimum.

### 1.5 Wireframe Standards (Asset Pipeline)
* **Standard Mode:** Pure Black & White (B/W) Skeleton.
* **Complex Masking Mode (New):** Used for complex pages (like Page 50). Allows **Red/Green/Blue** guide lines in the wireframe (`_wireframe_kdp.png`) to assist Python detection.
* **CRITICAL PRODUCTION RULE:** If a wireframe contains color, the Production Script **MUST** apply a `Grayscale` or `Threshold` filter during final PDF assembly. The final print must be 100% Black & White.
* **Strict Technical Standards:**
    1.  **Label Style:** Standardization to **"Floating Bold Text"**. (Explicitly prohibit "Text Box" styles).
    2.  **Line Style:** Zone borders must be a **"Thick Single Line"**. (Double lines are strictly prohibited).
    3.  **Color Matching:** The Text Color of a label must **exactly match** the Zone Border color (e.g., Green Text for a Green Border) to assist Python color masking.

### 1.6 GLOBAL_BLUEPRINT_SPECS (The SSOT)
*All Agents (Bravo, Charlie, Echo) must reference these variables. Do not hardcode values.*

#### [PAGE_01_MISSION] (Internal Page Template)
* **Structure:** Fixed Layout (Red/Yellow/Blue Zones) + Variable Sticker Cloud (Green).
* **Asset_Wireframe:** `assets/ref_page1_wireframe.png`
* **Text_Header (Red):** "KNOLLING ADVENTURES" (Font: Titan One, Top Fixed).
* **Text_Center (Yellow):** "THIS BOOK BELONGS TO:" (Interaction Panel).
* **Text_Instruction (Blue):** 3-Step Guide (Crayon/Eye/Lightbulb).
* **Variable_Zone (Green):** [THEME] Sticker Cloud. 10-15 distinct items.

#### [PAGE_02_PARENTS] (Note to Parents)
* **Structure:** Hybrid (Visual Frame + Code Text).
* **Asset_Ref:** `{MASTER_REF_IMG}`
* **Text_Header (Green):** "A NOTE TO PARENTS:"
    * Font: `{FONT_TITLE_MAIN}` | Size: **40pt** | Align: Center | Y-Pos: Top 85%
* **Text_Body (Yellow):** "This book is best used with crayons or colored pencils. If using MARKERS, please place a protective sheet behind the page to prevent ink bleeding!"
    * Font: `{FONT_BODY_TEXT}` | Size: **18pt** | Align: Center | Wrap Width: 6 inches | Y-Pos: Center (approx 60%)
* **Text_Footer (Purple):** "Copyright © 2025 by PapaBingo. All rights reserved."
    * Font: `{FONT_LEGAL}` | Size: **10pt** | Align: Center | Y-Pos: 0.5 inch from bottom.
* **Visual_Constraint:** "No Markers" Icon at Bottom Center (Blue Zone).

#### [PAGE_03_START] (Mission Start)
* **Structure:** Static Frame + Variable Gear Bag.
* **Asset_Wireframe:** `assets/ref_page3_layout_wireframe_kdp.png`
* **Text_Top (Blue):** "ARE YOU READY TO EXPLORE?"
    * Font: `{FONT_TITLE_MAIN}` | Style: Outline (Stroke 2pt) | Fill: White.
* **Text_Bottom (Purple):** "TURN THE PAGE TO START YOUR FIRST MISSION!"
    * Font: `{FONT_TITLE_MAIN}` | Style: Outline (Stroke 2pt).
* **Visual_Element (Green):** [THEME] Backpack with 3-4 Tools.
* **Visual_Element (Yellow):** Fixed Action Arrow pointing Right.

#### [PAGE_04_KNOLLING] (Miniature Gear Box)
* **Structure:** "Visual Island" (60% Scale).
* **Asset_Wireframe:** `assets/ref_page4_layout_wireframe_kdp.png`
* **Gap_Rule:** **0.5 inch (minimum)** vertical gap between Box bottom and Text top.
* **Alignment:** Text Width <= Box Width.
* **Zone_Logic:**
    * **Red:** Fixed Frame (Rounded Square).
    * **Green:** Variable Objects (6 items).
    * **Blue:** Dynamic Text ("THEME GEAR").

#### [PAGE_05_ACTION] (Action Scene)
* **Structure:** Full Bleed with Center Safe Zone.
* **Asset_Wireframe:** `assets/ref_page5_layout_wireframe_kdp.png`
* **Safety_Zone (Green):** `{SAFE_MARGIN}` (9.5mm) from trim edges. Critical art must stay inside.
* **Logic:** Must use tools defined in Page 4. "Zoom Out" slightly for padding.

#### [PAGE_50_CERTIFICATE] (Completion)
* **Structure:** Variable Frame + Text Injection.
* **Asset_Wireframe:** `assets/ref_page50_layout_wireframe_kdp.png` (Colorized).
* **Protocol:** **[PROTOCOL_COLOR_MASKING]** applies. Red/Green lines must be removed.
* **Text_Header:** "CONGRATULATIONS!" (Titan One, 60pt, Outline).
* **Text_Body:** "This certifies that" (Sans-Serif) / Name Line / "[THEME] ADVENTURES" (Bold, 45pt).
* **Visual_Badge (Blue):** "OFFICIAL EXPLORE" (Fixed Asset).
* **Visual_Frame (Red):** [THEME] Objects, Knolled, Upright.

#### [COVER_SPREAD]
* **Dimensions:** 17.365" x 8.75" (Spine: 0.115").
* **Asset_Wireframe:** `assets/ref_cover_layout_wireframe_kdp.png`
* **Logo_Constraint:** `assets/logo.png` height must be **1.2 inches** (Zone 8).
* **Zone_Map:**
    * **Front (Right):** Title (Zone 1), Subtitle (Zone 9), Hero (Zone 11).
    * **Back (Left):** Marketing Text (Zone 10, 6), Mockups (Zone 4), Mini Char (Zone 5).
    * **Spine:** Keep clear.
    * **Barcode (Zone 7):** RESTRICTED AREA (2.0" x 1.2").

---

## 2. MASTER COVER BLUEPRINT (Structural Analysis)
*Refer to `1.6 GLOBAL_BLUEPRINT_SPECS` for Dimensions and Zones.*
* **Objective:** Single Seamless Image (17.365" x 8.75").
* **Key Logic:**
    * **Front:** High energy, clear branding.
    * **Back:** "Game Mechanic" explanation (Match Tools to Job).
    * **Safety:** All critical text/logos `{SAFE_MARGIN}` away from trim.

---

## 3. Page Sequencing Structure

* **Page 1 (Right):** **Title Page / Mission Briefing**
    * *Source Spec:* `[PAGE_01_MISSION]` in Section 1.6.
    * *Visuals:* Fixed Header/Footer + Sticker Cloud.
    * *Overlay:* **Agent Echo** must retrieve text strings from Section 1.6.

* **Page 2 (Left):** **Copyright & Note to Parents**
    * *Source Spec:* `[PAGE_02_PARENTS]` in Section 1.6.
    * *Visuals:* Fixed Border + "No Markers" Icon.
    * *Overlay:* **Agent Echo** must retrieve text strings/coords from Section 1.6.

* **Page 3 (Right):** **Intro / Mission Start**
    * *Source Spec:* `[PAGE_03_START]` in Section 1.6.
    * *Visuals:* Fixed Frame + Variable Gear Bag.
    * *Overlay:* **Agent Echo** must retrieve text strings/coords from Section 1.6.

* **Page 4 (Left):** **[THEME 1] Knolling**
    * *Source Spec:* `[PAGE_04_KNOLLING]` in Section 1.6.
    * *Logic:* Visual Island (60% Scale).
    * *Overlay:* Theme Title Text (Blue Zone).

* **Page 5 (Right):** **[THEME 1] Action**
    * *Source Spec:* `[PAGE_05_ACTION]` in Section 1.6.
    * *Logic:* Full Bleed, Safety Masking. Reference Page 4 Asset.

* **Page 50 (Left):** **Certificate of Completion**
    * *Source Spec:* `[PAGE_50_CERTIFICATE]` in Section 1.6.
    * *Logic:* Variable Frame. Apply **[PROTOCOL_COLOR_MASKING]**.
    * *Overlay:* Name, Theme Title, Date.

---

## 4. Typography (Standard Series Fonts)
*Keeping these consistent builds a recognizable brand. See Section 0.0 for filenames.*

* **Titles:** **Titan One** (Thick, Outline Effect).
* **Subtitles:** **Fredoka One** (Rounded).
* **Labels/Body:** **Quicksand Bold** (Clean).
* **Handwriting:** **Patrick Hand** (Personal).
* **"By" Line:** **Sniglet** (Rounded, playful).

---

## 5. Master Prompts (Series Template & Tech Envelopes)

*Every prompt generated must explicitly or implicitly use the following Technical Envelopes to ensure KDP compliance.*

### 5.0 DNA LIBRARY (Standard Style Macros)
**[DNA_PAGE_01] (Mission Briefing):**
"High-contrast coloring page. **Layout:** Center Magnifying Glass (empty glass), Bottom 3-step icon strip (Crayon/Eye/Lightbulb). **Background:** 'Sticker Cloud' of [THEME] items. **Style:** Die-cut stickers, thick double outlines, no shading."

**[DNA_PAGE_02] (Note to Parents):**
"Visual instruction page. **Border:** Single thick rounded rectangular border. **Icon:** Bottom center 'Marker Pen' inside 'Prohibition Circle'. **Center:** Pure white void. **Style:** Safety signage, heavy strokes, minimal."

**[DNA_PAGE_03] (Mission Start):**
"Hero Prop. **Subject:** Cute chunky **[THEME] Gear Bag**, open with tools visible. **Add-on:** Large chunky arrow pointing right. **Layout:** Center zone. **Style:** Heroic cute, detailed textures."

**[DNA_KNOLLING] (The Parts):**
"**Knolling Photography Style**. 90-degree flat lay. Distinct [SUBJECT] parts in a grid. **Spacing:** White space separation (no overlap). **Style:** Technical vector line art."

**[DNA_ACTION] (The Scene):**
"Full-page action. **Subject:** Hero character utilizing [SUBJECT] tools. **Pose:** Dynamic, eye contact. **Background:** Immersive [THEME] environment. **Style:** Full-bleed scene, Centralized Composition, Wide White Margin, **Use Page 4 Asset as Reference**, No double tools."

**[DNA_CERTIFICATE] (Completion):**
"Official Award. **Border:** Patterned icons of [THEME]. **Center:** Empty for text. **Details:** Ribbon/Seal at bottom. **Style:** Formal/Playful mix."

**[DNA_COVER] (Seamless Spread):**
"Wide seamless spread. **Front:** Hero Character + Title. **Back:** Flat-lay gear + Mockups. **Style:** Vibrant colors, thick clean outlines, high commercial quality."

### 5.1 Protocol: Schematic Reconstruction (Advanced)
* **Trigger:** When `Erase` commands fail to remove objects inside a frame (due to Visual Binding).
* **Concept:** Shift persona from "Image Editor" to **"Architect"**.
* **Instruction:** "Redraw this image as a Simplified Schematic. Draw the border lines exactly as seen, but treat internal content as 'noise'. Render the track as **SOLID WHITE**."

### 5.2 NEGATIVE DNA LIBRARY (Quality Control)
*Agent Bravo MUST append the appropriate Negative DNA to every prompt.*

#### [NEGATIVE_GLOBAL] (Apply to ALL Prompts)
"text, font, letters, words, watermark, signature, copyright info, barcode, qr code, shading, gradients, grayscale, colored, filled, 3d render, realistic photo, sketch lines, dithering, noise, blur, low quality, pixelated, jpeg artifacts, cropped, cut off, duplicate, deformed"

#### [NEGATIVE_KNOLLING] (Apply to Gear Pages)
"perspective, angled view, isometric, human hands, holding items, messy, overlapping items, shadow, chaotic background, multiple angles, distorted shapes"

#### [NEGATIVE_ACTION] (Apply to Scene Pages)
"knolling grid, static pose, floating objects, multiple horizons, text bubbles, speech balloons, frame border, cut off limbs, babyish proportions, scary"

#### [NEGATIVE_COVER] (Apply to Cover)
"barcode placeholder, price tag, low resolution, dull colors, messy sketch, cutoff character, internal page guides"

### [TECH_ENVELOPE_INTERNAL]
**"Canvas: 8.625x8.75 inches. Resolution: 300 DPI. Pure white background. Keep all text/art inside 7.75x7.75 inch safety zone. Thick uniform black vector lines."**

### [TECH_ENVELOPE_COVER]
**"Canvas: 17.365x8.75 inches (Full Spread). Resolution: 300 DPI. Right side is Front, Left side is Back. Center 0.115 inch is Spine. Vibrant colors, thick outlines, heroic cute style."**

---

### [A] PAGE 1: Mission Briefing (Hybrid Restore w/ Sticker Cloud)
* **Ref:** `[PAGE_01_MISSION]` in Section 1.6.
* **Prompt:** `[TECH_ENVELOPE_INTERNAL]`, `[DNA_PAGE_01]`. **Negative:** `[NEGATIVE_GLOBAL]`.
    * **Variable Zone (Zone 4):** A **"Sticker Cloud"** filling the negative space.
    * **Content:** 10-15 distinct `[THEME]` items.
    * **Style:** **"Die-cut Sticker" effect** with thick double outlines and white gaps.

### [B] PAGE 2: Note to Parents (VISUALS ONLY)
* **Ref:** `[PAGE_02_PARENTS]` in Section 1.6.
* **Strategy:** **Visuals Only.** The AI **MUST NOT** generate any text.
* **Prompt:** `[TECH_ENVELOPE_INTERNAL]`, `[DNA_PAGE_02]`, a coloring book instruction page. A clean white background. A **single thick black rectangular border with rounded corners** near the edges. A large empty white space in the center. At the bottom center, a cute thick-line vector icon of a **"Marker Pen" inside a "Prohibition Sign"** (Circle with a diagonal line). No text, no letters, no words. High contrast line art. **Negative:** `[NEGATIVE_GLOBAL]`.

### [C] PAGE 3: Intro / Mission Start (Static Gear Bag)
* **Ref:** `[PAGE_03_START]` in Section 1.6.
* **Prompt:** `[TECH_ENVELOPE_INTERNAL]`, `[DNA_PAGE_03]`, black and white line art coloring page.
    * **Layout:** A thick black rectangular border with rounded corners.
    * **Center:** A large, detailed **[THEME] gear bag or backpack** (chunky and friendly style) overflowing with theme-specific tools.
    * **Action:** A bold arrow pointing to the **right**.
    * **Constraint:** All elements are fixed; no character art on this page. Focus on the tools and the bag.
    * **Negative:** `[NEGATIVE_GLOBAL]`.

### [D] INTERIOR: The Knolling Page (Left)
* **Source:** Average of `assets/ref_knolling_*.png`
* **Prompt:** `[TECH_ENVELOPE_INTERNAL]`, `[DNA_KNOLLING]`, black and white line art, knolling photography layout, flat lay, **[SUBJECT]** parts, organized grid of **[OBJECT LIST]**, **top 75%** filled, **bottom 25%** empty white space, no shading.
* **Negative:** `[NEGATIVE_GLOBAL]`, `[NEGATIVE_KNOLLING]`.

### [E] INTERIOR: The Action Page (Right)
* **Source:** Average of `assets/ref_action_*.png`
* **Prompt:** `[TECH_ENVELOPE_INTERNAL]`, `[DNA_ACTION]`, black and white line art, **[SUBJECT]** in action pose, wearing **[OBJECT LIST]**, dynamic composition, thick uniform lines, **[MAIN CHARACTER DESCRIPTION]**.
* **Negative:** `[NEGATIVE_GLOBAL]`, `[NEGATIVE_ACTION]`.

### [F] FINAL PAGE: Certificate
* **Ref:** `[PAGE_50_CERTIFICATE]` in Section 1.6.
* **Prompt:** `[TECH_ENVELOPE_INTERNAL]`, `[DNA_CERTIFICATE]`, certificate of completion design.
    * **Structure:** Single line borders (inner and outer).
    * **Frame Content (Zone 1):** A rectangular frame composed of diverse **[THEME]** items arranged in a neat knolling style between the borders.
    * **Center (Zone 3):** Large empty white space for text injection.
    * **Corner (Zone 2):** Space for "Official Explore" badge.
    * **Negative:** `[NEGATIVE_GLOBAL]`.

### [G] COVER ART (Seamless Spread)
* **Ref:** `[COVER_SPREAD]` in Section 1.6.
* **Prompt:** `[TECH_ENVELOPE_COVER]`. *Refer to the Blueprint Wireframe for Zone placement.* A seamless panoramic book cover design for kids, wide aspect ratio, **[EDITION THEME]** theme.
    * **Right Side:** Title area (Zone 1), Subtitle area (Zone 9), Hero Character (Zone 11). **Leave Zone 8 empty for Logo Asset.**
    * **Left Side:** Text area (Zone 10 - Context: "Match Tools"), Mockup display of internal pages (Zone 4), Mini Character (Zone 5).
    * **Style:** Flat vector illustration, vibrant colors, thick clean outlines, high energy, 300 dpi.
    * **Negative:** `[NEGATIVE_GLOBAL]`, `[NEGATIVE_COVER]`.

---

## 6. Production Planner

**Series Volume:** __________________ (e.g., Vehicles)
**Theme/Unit:** __________________ (e.g., Fire Truck)

**Reference Image Found:** [ ] Yes (Source: _______________)

**Left Page (The Parts):**
1.  __________________ (e.g., Wheel)
2.  __________________ (e.g., Ladder)
3.  __________________ (e.g., Siren)
4.  __________________ (e.g., Hose)
5.  __________________ (e.g., Helmet)

**Right Page (The Action):**
* **Setting:** ___________________________________________________________
* **Action:** ___________________________________________________________

**Fun Fact Text:** ___________________________________________________________