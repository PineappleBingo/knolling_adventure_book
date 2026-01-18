# SERIES MASTER BIBLE: Knolling Adventures
**Version:** 5.12.1 (Multi-Shot, Cover Blueprint & Logo Integration)
**Last Updated:** December 11, 2025
**Platform:** Amazon KDP (Paperback)
**Target Audience:** Ages 4–8
**Trim Size:** 8.5" x 8.5" Square
**Page Count:** 50 Pages (Standard) or defined by `PAGE_COUNT`

---

## 0. THE AGENT MANIFEST (Engineering Architecture)
*Use this manifest to instruct the AI IDE on how to build the Python application.*

### 0.1 TECHNICAL SPECIFICATIONS (The Stack)
* **Core Python Libs:**
    * `python-telegram-bot` (Async interface for UI)
    * `google-generativeai` (Strictly for Text/QA/Vision Analysis via Gemini)
    * `requests` (**CRITICAL:** Used for Image Generation via Direct REST API)
    * `pillow` (Image processing & Grayscale conversion)
    * `reportlab` (PDF assembly)
    * `pydrive2` & `gspread` (Cloud Storage/Tracking)
    * `python-dotenv` (Env variables)
    * `glob` (File pattern matching for Multi-Shot references)
* **Dependency Management:** Use **Pipenv** (`Pipfile` / `Pipfile.lock`).
* **Secrets (.env):**
    * `TELEGRAM_TOKEN`
    * `GOOGLE_API_KEY`
    * `DEPLOYMENT_TIER` (Values: `FREE` or `PAID`)
    * `PAGE_COUNT` (Integer; e.g., `5` for testing, `50` for production)
* **Constraint - NO VERTEX AI:**
    * Agents must **NEVER** import `vertexai` or `google.cloud.aiplatform`.
    * Agents must **NEVER** try to import `ImageGenerationModel` from `google.generativeai`.
* **Constraint - IMAGE GENERATION STRATEGY:**
    * **Agent Charlie** must use the **Direct REST API** via `requests`.
    * **Model ID:** `models/imagen-4.0-generate-001` (Verified Available).
    * **Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/{model_name}:predict`
    * **Auth:** Use the `x-goog-api-key` header.
    * **Payload Protocol:**
        ```json
        {
          "instances": [ { "prompt": "YOUR PROMPT HERE" } ],
          "parameters": { "sampleCount": 1, "aspectRatio": "1:1" }
        }
        ```
* **Assets Structure (Multi-Shot & Blueprint):**
    * **Cover Layout Assets:**
        * `docs/MASTER_COVER_BLUEPRINT_v1.0.md` (Strict text rules for layout).
        * `assets/ref_cover_layout_wireframe_kdp.png` (Color-coded Zone Map).
        * `assets/ref_cover_structure_example.png` (Context Map: Real art with zones overlaid).
        * `assets/logo.png` (Author Branding for Zone 8).
    * **Style References (Upload 3-5 variants per type):**
        * `assets/ref_cover_*.png` (Style: Colored, Panoramic, Sticker aesthetic).
        * `assets/ref_page_01_*.png` (Style: Title/Magnifying Glass).
        * `assets/ref_page_02_*.png` (Style: Note to Parents layout).
        * `assets/ref_page_03_*.png` (Style: "Ready to Explore" layout).
        * `assets/ref_knolling_*.png` (Style: B&W Grid Layout).
        * `assets/ref_action_*.png` (Style: B&W Action Scene).
        * `assets/ref_certificate_*.png` (Style: Final Certificate).

### 👑 Agent Omega: Senior Project Manager (Orchestrator)
* **Mission:** Coordinate the lifecycle and handle errors.
* **Tasks:**
    * **Loop Control:** Use `config.PAGE_COUNT` to determine exactly how many pages to generate.
    * **Safety Net:** Wrap `run_job()` in a global `try/except`. If ANY crash occurs, call `AgentGolf.log_error(e)` immediately.
    * **Visual Consistency Handoff:**
        1. Call `Bravo.generate_prompts()`.
        2. **Capture Return Data:** Extract `main_character_prompt` and `gear_list_prompt`.
        3. **Pass Data:** Call `Bravo.generate_cover(...)` using those exact strings.
    * **Workflow:** UI Trigger -> Golf Log -> Bravo (Prompts) -> Loop [Charlie (Gen) -> Delta (QA)] -> Echo (PDF) -> Foxtrot (Proof) -> Upload.

### 👨‍💻 Agent Alpha: Senior Systems Architect (Infrastructure)
* **Mission:** Build the environment and Configuration logic.
* **Tasks:**
    * **Config.py:** Load `PAGE_COUNT` from `.env` (Default to 50 if missing).
    * **Deployment Tiers Logic:**
        * **IF FREE:**
            * `IMG_MODEL` = `models/gemini-2.0-flash-exp` (Fallback)
            * `QA_MODEL` = `models/gemini-2.5-pro` (Smartest Available)
            * `QA_DELAY` = 35 seconds (Strict Rate Limit)
            * `GEN_DELAY` = 20 seconds
        * **IF PAID:**
            * `IMG_MODEL` = `models/imagen-4.0-generate-001` (High Fidelity)
            * `QA_MODEL` = `models/gemini-2.5-pro` (Smartest Available)
            * `QA_DELAY` = 0.5 seconds
            * `GEN_DELAY` = 0.5 seconds
    * Manage `credentials.json` logic.

### 🎨 Agent Bravo: Executive Creative Director (Prompt Logic)
* **Mission:** Ensure visual consistency via **Multi-Shot & Blueprint Analysis**.
* **Tasks:**
    * **Discovery:** Use `glob` to find all `assets/ref_{type}_*.png`.
    * **Batch Analysis:** Send **BATCHES** of images to Gemini Vision. Extract "Shared Visual DNA" (line weight, layout rules) into `self.style_library`.
    * **Cover Logic (CRITICAL):**
        1. Read `docs/MASTER_COVER_BLUEPRINT_v1.0.md` for text/zone rules.
        2. Analyze `assets/ref_cover_layout_wireframe_kdp.png` to understand spatial Zones (Red=Title, Black=Logo, etc.).
        3. **Injection:** Explicitly instruct the generator to place `assets/logo.png` in the coordinates defined by Zone 8.
        4. Combine with "Visual DNA" from `ref_cover_*.png` to create the final prompt.
    * **Mapping Logic:**
        * **Page 1:** Inject `[DNA_PAGE_01]`
        * **Page 2:** Inject `[DNA_PAGE_02]`
        * **Page 3:** Inject `[DNA_PAGE_03]`
        * **Knolling:** Inject `[DNA_KNOLLING]`
        * **Action:** Inject `[DNA_ACTION]`
        * **Certificate:** Inject `[DNA_CERTIFICATE]`
        * **Cover:** Inject `[DNA_COVER]` + Blueprint Structure.

### 🖌️ Agent Charlie: Lead Technical Artist (Image Generation)
* **Mission:** Manage the API Loop via REST (Imagen 4.0).
* **Tasks:**
    * **Naming Convention:** Files must follow: `temp/{Theme}_Page{XX}_{Timestamp}.png`.
    * **Protocol:** Use `requests.post()` to hit the Google API directly.
    * **Aspect Ratio:**
        * Interior: `1:1`
        * Cover: `2:1` (or nearest wide equivalent for 17" spread).
    * **Rate Limiting:** Apply `time.sleep(config.GEN_DELAY)` after every call.
    * **No Placeholders:** If API fails, Raise Error. Do not save fake images.

### 🔍 Agent Delta: Senior Pre-Press Quality Manager (QA Guard)
* **Mission:** Enforce Quality Control (No Shading/Color).
* **Tasks:**
    * **Model:** Use **Gemini 2.5 Pro** (`models/gemini-2.5-pro`).
    * **Rate Limiting:** Apply `time.sleep(config.QA_DELAY)` *before* every check.
    * **Retry Logic:** Max 3 Retries.

### 📐 Agent Echo: Senior Publishing Engineer (Assembly)
* **Mission:** PDF Assembly.
* **Tasks:**
    * Enforce **2625 x 2588 pixels** (300 DPI) for pages.
    * Convert all images to **Grayscale Mode (L)** (Except Cover).

### 📊 Agent Golf: Production Analyst (Tracking)
* **Mission:** Google Sheet "Mission Control".
* **Tasks:**
    * Implement `log_error(error_msg)` to mark status as "❌ FAILED".
    * Update status rows asynchronously if possible.

### 🤖 Agent Foxtrot: Lead UX Engineer (Interface)
* **Mission:** Telegram Dashboard.
* **Tasks:**
    * **Live Dashboard:** Use `edit_message_text` to show real-time progress.
    * **Hyperlink:** Link "Mission Control" text to the Google Sheet URL.
    * **Proofing Album:** Before final PDF, send a **Media Group** of 3 images (Cover, Knolling Page, Action Page).
    * **Approval:** Show "Upload to Drive" button only after proof is sent.

---

## 1. Core Design Rules (The Constants)

### 1.1 The "Game Mechanic" (Spread Logic)
* **Left Page (Even):** **THE GEAR (Knolling).** A neat, flat-lay grid of the items/parts.
* **Right Page (Odd):** **THE ACTION (Scene).** The character/creature using those items in a full background.
* **Goal:** "Match the Item to the Action."

### 1.2 Visual Style (Age 4-8)
* **Reference System:** All visual styles are derived from the `assets/ref_*.png` files.
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

## 2. MASTER COVER BLUEPRINT (Structural Analysis)
*Refer to `docs/MASTER_COVER_BLUEPRINT_v1.0.md` and `assets/ref_cover_layout_wireframe_kdp.png` for strict positioning.*

* **Format:** Single Seamless Image (17.365" x 8.75").
* **ZONE 1 (Top Right):** Title "**KNOLLING ADVENTURES**" (Yellow Gradient, Thick Black Outline).
* **ZONE 9 (Below Title):** Subtitle "From Gear to Action: [THEME] Edition".
* **ZONE 11 (Bottom Right):** Main Character (Heroic Cute, Eye Contact).
* **ZONE 8 (Bottom Center-Right):** **AUTHOR LOGO** (`assets/logo.png`). *Do not generate text here; reserve space for logo asset.*
* **ZONE 10 (Top Left):** Marketing Text "**MATCH THE TOOLS TO THE JOB!**" (Yellow Sticker style).
* **ZONE 4 (Center Left):** Mockup Display (Angled Papers showing Page 4 & 5).
* **ZONE 5 (Bottom Left):** Mini Character (Pointing Up).
* **ZONE 6 (Below Mockups):** Text "20+ Professions to Explore! Ages 4-8."
* **ZONE 3 (Floating):** Sticker Cloud (Die-cut gear items).
* **ZONE 7 (Bottom Right Back):** **BARCODE ZONE (EMPTY)**.

---

## 3. Page Sequencing Structure

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
* **Source:** Structure from `docs/MASTER_PAGE_01_BLUEPRINT_v1.1.md` + Style DNA from `assets/ref_page_01_*.png`.
* **Reference Asset:** Use `assets/ref_5.png` specifically for the "How to Play" layout logic.
* **Prompt:** `[DNA_PAGE_01]`, black and white line art coloring page.
    * **Header:** Title "MISSION BRIEFING" in hollow coloring font.
    * **Center:** Large magnifying glass with "Agent Name: ____" inside.
    * **Character:** Cute `[MAIN CHARACTER]` holding the lens handle on the right.
    * **Bottom Banner (Mission Protocol):** A 3-step visual guide at the bottom.
        * Step 1: Crayon Icon with text "COLOR IT".
        * Step 2: Eye Icon with text "FIND IT".
        * Step 3: Lightbulb Icon with text "LEARN IT".
    * **Border:** `[EDITION THEME]` icons around the edges.

### [B] PAGE 2: Note to Parents
* **Source:** Average of `assets/ref_page_02_*.png`
* **Prompt:** `[DNA_PAGE_02]`, black and white line art, instructional page layout, cute border frame of `[EDITION THEME]` items, large empty central area for text, "Note to Parents" header style.

### [C] PAGE 3: Intro / Dedication
* **Source:** Average of `assets/ref_page_03_*.png`
* **Prompt:** `[DNA_PAGE_03]`, black and white line art, "Are you ready to explore?" theme, exciting introductory layout, `[MAIN CHARACTER]` waving hello, minimal background, space for dedication text.

### [D] INTERIOR: The Knolling Page (Left)
* **Source:** Average of `assets/ref_knolling_*.png`
* **Prompt:** `[DNA_KNOLLING]`, black and white line art, knolling photography layout, flat lay, **[SUBJECT]** parts, organized grid of **[OBJECT LIST]**, **top 75%** filled, **bottom 25%** empty white space, no shading.

### [E] INTERIOR: The Action Page (Right)
* **Source:** Average of `assets/ref_action_*.png`
* **Prompt:** `[DNA_ACTION]`, black and white line art, **[SUBJECT]** in action pose, wearing **[OBJECT LIST]**, dynamic composition, thick uniform lines, **[MAIN CHARACTER DESCRIPTION]**.

### [F] FINAL PAGE: Certificate
* **Source:** Average of `assets/ref_certificate_*.png`
* **Prompt:** `[DNA_CERTIFICATE]`, certificate of completion design, rectangular border of diverse items, empty center, official document style.

### [G] COVER ART (Seamless Spread)
* **Source:** `[DNA_COVER]` + Structure from `assets/ref_cover_layout_wireframe_kdp.png`.
* **Prompt:** *Refer to the Blueprint Wireframe for Zone placement.* A seamless panoramic book cover design for kids, wide aspect ratio, **[EDITION THEME]** theme.
    * **Right Side:** Title "KNOLLING ADVENTURES" (Zone 1), Subtitle (Zone 9), Hero Character (Zone 11). **Leave Zone 8 empty for Logo Asset.**
    * **Left Side:** Text "MATCH THE TOOLS..." (Zone 10), Mockup display of internal pages (Zone 4), Mini Character (Zone 5), Marketing text (Zone 6).
    * **Style:** Flat vector illustration, vibrant colors, thick clean outlines, high energy, 300 dpi.

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