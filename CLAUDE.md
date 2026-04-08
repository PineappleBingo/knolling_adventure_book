# Knolling Adventures - KDP Automation System

## Project Overview
- **SSOT:** `Series Master Bible v5.22.md` (root directory)
- **Platform:** Amazon KDP (Paperback), 8.5" x 8.5" trim
- **Target Audience:** Ages 4-8
- **Purpose:** Automated generation of children's coloring books via AI image generation + PDF assembly
- **Interface:** Telegram Bot (`/generate [Theme]`)
- **Status:** ~80% functional (see Progress Tracker below)

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
DEPLOYMENT_TIER=FREE|PAID        # Controls model selection + rate limits
PAGE_COUNT=50                     # Default page count
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

### API Configuration (Verified April 2026)

**PAID Tier (Imagen 4.0):**
- Model: `imagen-4.0-generate-001`
- Endpoint: `POST .../models/{model}:predict`
- Payload: `instances[].prompt` + `parameters.sampleCount/aspectRatio`
- Response: `predictions[].bytesBase64Encoded`

**FREE Tier (Gemini Image Gen):**
- Model: `gemini-2.5-flash-image` (current -- replaces deprecated `gemini-2.0-flash-exp`)
- Endpoint: `POST .../models/{model}:generateContent`
- **Required:** `generationConfig.responseModalities: ["TEXT", "IMAGE"]`
- Response: `candidates[].content.parts[].inlineData.data`

## Key Technical Constraints
- Image generation MUST use REST API via `requests` (Agent Charlie), NOT the deprecated `google-generativeai` SDK
- Text overlay is programmatic via ReportLab (Agent Echo), NOT AI-generated
- All text content/coordinates sourced from Bible Section 1.6 GLOBAL_BLUEPRINT_SPECS
- Page 50 requires `[PROTOCOL_COLOR_MASKING]` -- detect and remove Red/Green/Blue wireframe artifacts

## Progress Tracker

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
