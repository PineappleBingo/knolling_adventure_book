# Knolling Adventures - KDP Automation System

## Project Overview
- **SSOT:** `Series Master Bible v5.22.md` (root directory)
- **Platform:** Amazon KDP (Paperback), 8.5" x 8.5" trim
- **Target Audience:** Ages 4-8
- **Purpose:** Automated generation of children's coloring books via AI image generation + PDF assembly
- **Interface:** Telegram Bot (`/generate [Theme]`)
- **Status:** Pipeline verified end-to-end with synthetic art (2026-08). BLOCKED on restoring the 21 reference PNGs into `assets/` (see `assets/MANIFEST.md`) and a live API smoke run.

## Build & Run

### Prerequisites
- Python 3.11
- Google API Key (Gemini/Imagen access)
- Telegram Bot Token
- Google Sheets service account (`credentials.json`)

### Setup
```bash
pip install pipenv
pipenv install
# OR
pip install -r <(pipenv requirements)
```

### Environment Variables (.env)
```
GOOGLE_API_KEY=<required>
TELEGRAM_TOKEN=<required>
DEPLOYMENT_TIER=FREE|PAID        # Rate limits only (model selection moved to QUALITY_MODE)
QUALITY_MODE=DRAFT|FINAL          # DRAFT=gemini-2.5-flash-image, FINAL=gemini-3-pro-image
IMAGE_SIZE=2K                     # FINAL mode interior resolution (1K/2K/4K)
COVER_IMAGE_SIZE=4K               # FINAL mode cover resolution
ALLOW_DEGRADED_ASSETS=false       # true = permit runs with missing reference assets (debug only)
PAGE_COUNT=50                     # Default page count (drives spine width)
TARGET_PAGES=1,50                 # Optional: specific pages to generate
PDF_DEBUG_MODE=false              # Set true for magenta text overlay debugging
```

### Run
```bash
python src/main.py
```

### Run Tests
```bash
python -m pytest tests/
```

## Code Style & Standards (Bible Section 1.2, 1.5)
- Visual style: "Heroic Cute & Chunky" -- thick vector lines, rounded corners, toy-like proportions
- Output: Pure black & white line art for interior pages, vibrant color for covers
- Typography: Google Fonts only (OFL licensed) -- see `assets/fonts/`
- All critical art/text must stay within 0.375" safe margin from trim edges
- Wireframes with color guides (Red/Green/Blue) must be de-colorized in final output
- NO Vertex AI imports (`vertexai`, `google.cloud.aiplatform`) -- strictly forbidden

## Agent Topology

### Workflow
```
Telegram UI (Foxtrot) -> Golf (Log) -> Bravo (Prompts) 
  -> Loop: [Charlie (Generate) -> Delta (QA)] 
  -> Echo (PDF Assembly + Text Overlay) -> Foxtrot (Proof) -> Upload
```

### Agent-to-Module Map

| Agent | Role | Module | Key Responsibility |
|-------|------|--------|--------------------|
| Omega | Orchestrator | `src/modules/orchestrator.py` | Lifecycle coordination, error handling |
| Alpha | Infrastructure | `src/config.py` | Deployment tiers, rate limits, font/model config |
| Bravo | Prompt Logic | `src/modules/prompt_generator.py` | Triangulation Strategy, Negative DNA injection |
| Charlie | Image Generation | `src/modules/image_generator.py` | REST API (Imagen 4.0 / Gemini), dual-tier |
| Delta | QA Guard | `src/modules/qa_agent.py` | Gemini vision QA, retry logic |
| Echo | PDF Assembly | `src/modules/pdf_assembler.py` | ReportLab compositing, text overlay, color masking |
| Foxtrot | Telegram UI | `src/modules/bot_interface.py` | Live dashboard, proof delivery |
| Golf | Tracking | `src/modules/tracking.py` | Google Sheets "Mission Control" |

### API Configuration (Verified August 2026)

Imagen is RETIRED: `imagen-4.0-generate-001:predict` accepts no image input, so it
silently dropped every reference image (a root cause of style drift). Both quality
modes now share one multimodal path:

**DRAFT mode:** `gemini-2.5-flash-image` (~1K output, up to 5 reference images)
**FINAL mode:** `gemini-3-pro-image` / Nano Banana Pro (up to 14 refs, 1K/2K/4K)

- Endpoint: `POST .../models/{model}:generateContent`
- **Required:** `generationConfig.responseModalities: ["TEXT", "IMAGE"]`
- `generationConfig.imageConfig`: `aspectRatio` (+ `imageSize` on gemini-3 only)
- Parts order: role-labeled reference images (style ref, structure example,
  wireframe) first, operative prompt LAST
- Response: `candidates[].content.parts[].inlineData.data`

**Cover:** front + back generated as separate 1:1 art; Agent Echo composites the
KDP spread (spine width = PAGE_COUNT x 0.002252") and draws title/subtitle/logo
in real fonts. Typography is never AI-rendered.

## Key Technical Constraints
- Image generation MUST use REST API via `requests` (Agent Charlie), NOT the deprecated `google-generativeai` SDK
- NOTE: `.agent/*.md` role docs predate 2026-04-08 and list already-fixed bugs as open -- trust CLAUDE.md + code over them
- Text overlay is programmatic via ReportLab (Agent Echo), NOT AI-generated
- All text content/coordinates sourced from Bible Section 1.6 GLOBAL_BLUEPRINT_SPECS
- Page 50 requires `[PROTOCOL_COLOR_MASKING]` -- detect and remove Red/Green/Blue wireframe artifacts

## Progress Tracker

### Session 2026-08 (Claude Code handoff continuation)
- P0: assets tracked + manifest, fonts restored, hard preflight gate (assert_ready_for_generation)
- P1: zero-text bug fixed (metadata page classification), fail-fast fonts, HTTP retry/timeouts, JSON QA verdicts, QA-feedback retries, test suite repaired (51 passing + reproduce_e2e SUCCESS)
- P2: QUALITY_MODE re-tiering, Imagen retired, single-round-trip deterministic prompts, all 3 reference types reach the image model, theme-driven gear, composited cover spread
- P3: numpy saturation masking (incl. blue), lossless PNG line art, Bible-correct 8.625"x8.75" interior canvas, KDP validator gate wired into the orchestrator
- REMAINING: restore 21 reference PNGs (assets/MANIFEST.md), live API smoke run, gemini-3-pro-image access probe, page scale-out decision, .agent/*.md roster refresh

### Complete (100% as of 2026-04-08)
- Orchestration workflow (Omega)
- Prompt generation with triangulation + negative DNA (Bravo)
- Dual-tier image generation via REST with wireframe/ref support (Charlie)
- QA guard with retry logic (Delta)
- PDF assembly with text overlay, color masking, cover spread dimensions (Echo)
- Telegram bot with live dashboard (Foxtrot)
- Google Sheets tracking with google-auth (Golf)
- Deployment tier config + rate limiting (Alpha/config)
- Agent Alpha environment validation (check_environment)
- TARGET_PAGES selective generation
- All assets (fonts, wireframes, structure examples)
- Bible path updated to v5.22
- FREE tier: responseModalities + gemini-2.5-flash-image model
- SDK migration: google-generativeai -> google-genai
- SDK migration: oauth2client -> google-auth
- Cover spread dimensions (17.365" x 8.75")
- Bible typos corrected (MASTER_REF_IMG, models/ prefix)
- v1/v2 file duplication cleaned up

## Reference Documents
- `Series Master Bible v5.22.md` -- SSOT for all design/technical specs
- `docs/MASTER_*_BLUEPRINT_*.md` -- Per-page layout blueprints
- `docs/TRANSITION_REPORT.md` -- Full gap analysis with API verification
- `AGENT_DELTA_V2_GUIDE.md` -- QA agent reference
