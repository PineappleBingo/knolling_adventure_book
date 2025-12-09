# SERIES MASTER BIBLE: Knolling Adventures
**Version:** 5.2 (Full Stack Production)
**Last Updated:** December 08, 2025
**Platform:** Amazon KDP (Paperback)
**Target Audience:** Ages 4–8
**Trim Size:** 8.5" x 8.5" Square
**Page Count:** 50 Pages (Standard)

---

## 0. THE AGENT MANIFEST (Engineering Architecture)
*Use this manifest to instruct the AI IDE on how to build the Python application. Each Agent represents a specialized module with Senior-Level expertise.*

### 0.1 TECHNICAL SPECIFICATIONS (The Stack)
* **Core Python Libs:**
    * `python-telegram-bot` (Async interface for UI)
    * `google-generativeai` (Gemini & Imagen access)
    * `pillow` (Image processing & Grayscale conversion)
    * `reportlab` (PDF assembly & high-res canvas control)
    * `pydrive2` (Google Drive uploads)
    * `gspread` (Google Sheets tracking)
    * `oauth2client` (Auth for Drive/Sheets)
* **Project Structure:**
    * `/src/main.py` - Entry point (Initializes Omega & Foxtrot).
    * `/src/modules/` - Modular logic for each agent.
    * `/temp/` - Temporary storage for raw images (cleared after run).

### 👑 Agent Omega: Senior Project Manager (Orchestrator)
* **Experience:** 20+ Years in Agile Project Management & Systems Integration.
* **Mission:** Coordinate the entire lifecycle of a book generation.
* **Tasks:**
    * **The Controller:** The *only* agent that calls other agents.
    * **Workflow Logic:**
        1. Receive trigger from Agent Foxtrot (UI).
        2. Call **Agent Golf** to initialize tracking row.
        3. Call **Agent Bravo** to get prompts.
        4. Loop: Call **Agent Charlie** (Gen) -> Call **Agent Delta** (QA) -> Retry if needed.
        5. Call **Agent Echo** to stitch PDF.
        6. Call **Agent Golf** to mark "Done".
        7. Return final file to Agent Foxtrot.
    * **Error Handling:** If any agent fails, Omega catches the error and logs it via Agent Golf.

### 👨‍💻 Agent Alpha: Senior Systems Architect (Infrastructure)
* **Mission:** Build the rock-solid foundation.
* **Tasks:**
    * Initialize Python environment.
    * Manage secure credential handling (`credentials.json`) for Google Service Accounts.
    * Create `requirements.txt` with conflict-free versions of libraries listed above.

### 🎨 Agent Bravo: Executive Creative Director (Prompt Logic)
* **Mission:** Ensure the "Director" logic (Gemini 1.5 Flash) strictly adheres to the visual style guidelines.
* **Tasks:**
    * Write `prompt_generator.py`.
    * **Constraint:** Must enforce the "Left Page (Gear) / Right Page (Action)" logic without exception.
    * **Constraint:** Must inject the "Heroic Cute" style tags into every single prompt.

### 🖌️ Agent Charlie: Lead Technical Artist (Image Generation)
* **Mission:** Manage the "Artist" loop (Imagen 3 API).
* **Tasks:**
    * Write `image_generator.py`.
    * Implement robust error handling for API timeouts.
    * Manage file naming conventions (`page_04_firefighter_knolling.png`) to ensure sequencing.

### 🔍 Agent Delta: Senior Pre-Press Quality Manager (QA Guard)
* **Mission:** Build the "Guard" logic (Gemini 1.5 Pro Vision).
* **Tasks:**
    * Write `qa_agent.py`.
    * **Strict Directive:** "If an image contains grayscale shading, color (other than B&W), or broken lines, reject it immediately."
    * Implement the "Auto-Retry" loop (max 3 retries) before flagging a human.

### 📐 Agent Echo: Senior Publishing Engineer (Assembly)
* **Mission:** Handle the "Publisher" logic (Image Processing).
* **Tasks:**
    * Write `pdf_assembler.py`.
    * **The Math:** Enforce exactly **2625 x 2588 pixels** (8.75" x 8.625" @ 300 DPI) for bleed compliance.
    * Convert all images to **Grayscale Mode (L)** to prevent "Color Ink" billing on Amazon KDP.

### 📊 Agent Golf: Production Analyst (Tracking)
* **Mission:** Maintain the "Mission Control" Google Sheet.
* **Tasks:**
    * Initialize connection to Google Sheets using `gspread`.
    * Expose simple methods for Omega: `start_job()`, `update_progress()`, `finish_job()`.
    * **Row Structure:** `[RunID, Date, Theme, Status, Images_Passed, Drive_Link]`.

### 🤖 Agent Foxtrot: Lead UX Engineer (Interface)
* **Mission:** Build the Telegram Bot Wrapper.
* **Tasks:**
    * Write `bot_interface.py`.
    * Listen for command: `/generate [Theme]`.
    * **Handoff:** Pass request to Agent Omega.
    * **Feedback:** Report status updates ("Generating... 20/50").
    * **Approval:** Present the final PDF button for human sign-off before upload.

---

## 1. Core Design Rules (The Constants)

### 1.1 The "Game Mechanic" (Spread Logic)
* **Left Page (Even):** **THE GEAR (Knolling).** A neat, flat-lay grid of the items/parts.
* **Right Page (Odd):** **THE ACTION (Scene).** The character/creature using those items in a full background.
* **Goal:** "Match the Item to the Action."

### 1.2 Visual Style (Age 4-8)
* **Line Art:** **Thick, uniform vector lines.** No sketching, no grayscale, no shading. High contrast.
* **Composition:**
    * *Left:* Clean white background, distinct object separation (Top 75%).
    * *Right:* Immersive, full-bleed background.
* **Character Style:** **"Heroic Cute."** Modern cartoon style (like PAW Patrol/PJ Masks). Heroic proportions (not babyish), expressive eyes with pupils, detailed gear textures.

### 1.3 Quality Control
* **Resolution:** **300 DPI** minimum for all generations.
* **Bleed:** Images must extend **0.125"** (3.2mm) past the trim line.
* **Safe Zone:** Text must be **0.375"** (9.6mm) inside the trim line.

---

## 2. Page Sequencing Structure

* **Page 1 (Right):** **Title Page / Mission Briefing**
    * *Layout:* Central title/name-line, Border of `[EDITION THEME]` icons.
* **Page 2 (Left):** **Copyright & Note to Parents**
    * *Copyright Line:* "Copyright © 2025 by PapaBingo" (Standard Text).
    * *Warning:* "Use a protective sheet for markers."
* **Page 3 (Right):** **Dedication / Intro**
* **Page 4 (Left):** `[THEME 1]` Knolling
* **Page 5 (Right):** `[THEME 1]` Action
* *(...Repeat Pattern...)*
* **Page 50 (Left):** **Certificate of Completion**
    * *Layout:* `[EDITION THEME]` Border (Diverse Items), Parent Signature line, Website Marketing Link.

---

## 3. Cover Design (Seamless Spread)

### 3.1 Technical Layout
* **Format:** One single PDF (Back + Spine + Front).
* **Dimensions:** ~17.36" x 8.75" (Use KDP Calculator).
* **Resolution:** 300 DPI.

### 3.2 Visual Strategy
* **Concept:** Seamless panoramic wrap-around scene.
* **Front (Right):** High-energy action. Huge Title. Floating "Sticker-style" gear in top left. Hero character in bottom right (eye contact).
* **Back (Left):** Continuation of scene. More floating gear in top left. **Two "Mockup-style" Page Previews** (angled paper look with drop shadow) shown being presented by a mini-version of the main character.

### 3.3 Text & Elements
* **Front Title (The "King"):**
    * **Size:** **MAXIMUM VISIBILITY**, spanning width.
    * **Effect:** Bright gradient with **Thick Colored Outline** AND **Heavy Black Drop Shadow**.
* **Front Author Branding (The "Badge"):**
    * **Visual Hierarchy:** Visually smaller than the Title (approx **15-20%** of cover width).
    * **Style:** **STICKER / PATCH STYLE.** Use a **THIN** white bubble contour (not puffy) to create a clean seal.
    * **The Logo:** Place your **[AUTHOR LOGO FILE]** (PapaBingo Pineapple) at the bottom center.
    * **The "by" Line:** Place the word "by" to the left of the logo.
    * **Font for "by":** **Sniglet** (Google Font). Lowercase, Contrasting Color inside the white bubble.
* **Back Blurb:** "Match the tools to the job! [Number]+ Professions to Explore."
* **Barcode Zone (CRITICAL):** Leave **2.0" x 1.2"** completely empty in the Bottom Right corner. **DO NOT place a white box or fake barcode graphic there.**

---

## 4. Typography (Standard Series Fonts)
*Keeping these consistent builds a recognizable brand.*

* **Titles:** **Titan One** (Thick, Outline Effect).
* **Subtitles:** **Fredoka One** (Rounded).
* **Labels/Body:** **Quicksand Bold** (Clean).
* **Handwriting:** **Patrick Hand** (Personal).
* **"By" Line:** **Sniglet** (Rounded, playful).

---

## 5. Master Prompts (Series Template)

### [A] PAGE 1: Mission Briefing
* **Reference Strategy:** Search for "Kids coloring book title page magnifying glass" to use as a composition guide.
* **Prompt:**
    > black and white line art, coloring book style, title page design, a large bold outline of a magnifying glass in the center (empty inside), **central area is clean white space**, surrounded by a **border frame composed of small cute [EDITION THEME] icons** arranged along the edges, white background, high contrast, thick vector lines, no shading, 300 dpi.

### [B] INTERIOR: The Knolling Page (Left)
* **Reference Strategy:** Search for "Knolling photography [SUBJECT]" or "Flat lay [SUBJECT] gear" to see exactly which tools belong in the grid. Upload this photo as a structure reference.
* **Prompt:**
    > black and white line art, coloring book style for kids ages 4-8, knolling photography layout, flat lay, **[SPECIFIC SUBJECT]** parts/gear, organized grid arrangement of **[OBJECT LIST]**, objects are arranged in the **top 75% of the image**, leaving **empty white space at the bottom 25%**, white background, high contrast, thick uniform vector lines, simple shapes, no shading, no gray, no text, 300 dpi.

### [C] INTERIOR: The Action Page (Right)
* **Reference Strategy:** Use your **Page 1 Character Generation** as an Image Reference (URL/Upload) to ensure facial consistency. Search for "[SUBJECT] action pose cartoon" for pose reference.
* **Prompt:**
    > black and white line art, coloring book style for kids ages 4-8, **[SPECIFIC SUBJECT]** in an action pose, full body shot, wearing/using **[OBJECT LIST]**, interacting with **[BACKGROUND ENVIRONMENT]**, dynamic composition, thick uniform vector lines, high contrast, clear outlines, **modern cartoon style, expressive eyes, heroic proportions, cute but detailed, dynamic pose**, immersive background, no shading, no gray, 300 dpi.

### [D] PAGE 50: The Certificate
* **Reference Strategy:** Search for "Official Certificate Border Vector" to guide the layout structure.
* **Prompt:**
    > black and white line art, coloring book style, certificate of completion design, **a rectangular border frame composed of neat rows of diverse unique [EDITION THEME] items** arranged side-by-side, **no repeating patterns**, organized knolling style border, empty center space for text, clean white background, thick vector lines, high contrast, official document style, high resolution.

### [E] COVER ART (Seamless Spread)
* **Reference Strategy:** Upload your **Interior Character Art** to match the character design. Search for "Kids Book Cover Action Scene" for color palette inspiration.
* **Prompt:**
    > a seamless panoramic book cover design for kids, wide aspect ratio, **[EDITION THEME]** theme.
    > **Right Side (Front):** Huge title text "**KNOLLING ADVENTURES**" at top, subtitle below. Top left area features bold, floating "sticker-style" **[GEAR/OBJECTS]**. Bottom right features cute heroic **[MAIN CHARACTER]** in dynamic action, making eye contact, moving towards center.
    > **Left Side (Back):** Continuation of background. Top left features more floating **[GEAR/OBJECTS]**. Below are two realistic "paper mockup" style page previews (Left: Knolling, Right: Action) with white borders and drop shadows. A mini **[MAIN CHARACTER]** is pointing at the previews. Blurb text below. Bottom right corner is empty background space.
    > **Style:** Flat vector illustration, vibrant colors, thick clean outlines, high energy, 300 dpi.

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