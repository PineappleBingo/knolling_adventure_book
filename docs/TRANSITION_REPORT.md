# Transition Report: KDP Automation System
**From:** Antigravity IDE  
**To:** Claude Code  
**Date:** 2026-04-08  
**SSOT:** Series Master Bible v5.22  
**Status:** ~80% Functional  

---

## 1. Directory Reconnaissance

### 1.1 Project Structure
```
knolling_adventure_book/
├── assets/
│   ├── fonts/          (5 .ttf files)
│   ├── logo.png
│   ├── ref_*_01.png    (7 style reference images)
│   ├── ref_*_layout_wireframe_kdp.png  (7 wireframes)
│   └── ref_*_structure_example.png     (7 structure examples)
├── docs/               (7 blueprint .md files)
├── src/
│   ├── config.py       (Agent Alpha config)
│   ├── main.py         (Entry point)
│   └── modules/
│       ├── orchestrator.py       (Agent Omega)
│       ├── prompt_generator.py   (Agent Bravo)
│       ├── image_generator.py    (Agent Charlie v1)
│       ├── image_generator_v2.py (Agent Charlie v2)
│       ├── qa_agent.py           (Agent Delta)
│       ├── pdf_assembler.py      (Agent Echo)
│       ├── bot_interface.py      (Agent Foxtrot)
│       ├── tracking.py           (Agent Golf)
│       └── system_architect.py   (Agent Alpha - STUB)
├── tests/              (4 test files)
├── tools/              (2 model listing utilities)
├── temp/               (generated outputs + PDFs)
└── Series Master Bible v5.22.md
```

### 1.2 Asset Verification (Bible Sections 0.0 & 1.6)

| Asset Category | Expected | Found | Status |
|---------------|----------|-------|--------|
| Font: TitanOne-Regular.ttf | FONT_TITLE_MAIN | `assets/fonts/` | PRESENT |
| Font: Fredoka-Regular.ttf | FONT_SUBTITLE | `assets/fonts/` | PRESENT |
| Font: Quicksand-Bold.ttf | FONT_BODY_TEXT | `assets/fonts/` | PRESENT |
| Font: PatrickHand-Regular.ttf | FONT_HANDWRITING | `assets/fonts/` | PRESENT |
| Font: Sniglet-Regular.ttf | FONT_LEGAL | `assets/fonts/` | PRESENT |
| logo.png | Author branding | `assets/` | PRESENT |
| MASTER_REF_IMG | Bible: `ref_pag2_01.png` | `ref_page2_01.png` | **BIBLE TYPO** |
| Style refs (*_01.png) | cover, page1-5, page50 | All 7 | PRESENT |
| Wireframes (*_wireframe_kdp.png) | cover, page1-5, page50 | All 7 | PRESENT |
| Structure examples (*_structure_example.png) | cover, page1-5, page50 | All 7 | PRESENT |

### 1.3 Installed Packages

| Package | Version | Status |
|---------|---------|--------|
| google-generativeai | 0.8.6 | **DEPRECATED** (deadline: Aug 31, 2025) |
| requests | 2.32.5 | Current |
| pillow | 12.1.0 | Current |
| reportlab | 4.4.9 | Current |
| python-telegram-bot | 22.6 | Current |
| gspread | 6.2.1 | Current |
| oauth2client | 4.1.3 | **DEPRECATED** |
| python-dotenv | 1.2.1 | Current |

---

## 2. Codebase Logic Extraction

### 2.1 Agent-to-Code Mapping

| Bible Agent | Role | Module | Class | Implementation Status |
|-------------|------|--------|-------|-----------------------|
| Omega | Orchestrator | `orchestrator.py` | `AgentOmega` | Complete |
| Alpha | Config/Infrastructure | `config.py` + `system_architect.py` | module + `AgentAlpha` | **Partial** (stub) |
| Bravo | Prompt Logic | `prompt_generator.py` | `AgentBravo` | Complete |
| Charlie | Image Generation | `image_generator.py` (v1) / `image_generator_v2.py` (v2) | `AgentCharlie` | Complete (2 versions) |
| Delta | QA Guard | `qa_agent.py` | `AgentDelta` | Complete |
| Echo | PDF Assembly | `pdf_assembler.py` | `AgentEcho` | Complete |
| Foxtrot | Telegram UI | `bot_interface.py` | `AgentFoxtrot` | Complete |
| Golf | Tracking | `tracking.py` | `AgentGolf` | Complete |

### 2.2 Triangulation Strategy (Agent Bravo)

**Bible spec:** Anchor (DNA macros) + Constraint (Layout wireframe) + Nuance (Image analysis)

**Code implementation** (`prompt_generator.py:128-225`):
1. Loads wireframe image (Geometry) -- maps to Constraint
2. Loads structure example image (Context) -- **undocumented addition**
3. Extracts DNA via Gemini vision analysis -- maps to Anchor but uses **dynamic extraction** instead of fixed `[DNA_*]` macros from Section 5.0
4. Constructs meta-prompt via Gemini -- maps to Nuance

**Discrepancy:** Bible defines fixed deterministic DNA macros (`[DNA_PAGE_01]`, `[DNA_KNOLLING]`, etc.) but code uses non-deterministic vision-extracted DNA. This contributes to output variability.

### 2.3 Workflow (Agent Omega)

Verified workflow in `orchestrator.py:30-149`:
```
UI Trigger (Foxtrot) 
  -> Golf.start_job() 
  -> Bravo.generate_prompts() + Bravo.generate_cover()
  -> Loop: [Charlie.generate_image() -> Delta.quality_check()] (max 3 retries)
  -> Echo.assemble_pdf()
  -> Golf.finish_job()
```
This matches the Bible's Omega workflow: `UI -> Golf -> Bravo -> [Charlie -> Delta] -> Echo -> Foxtrot -> Upload`

---

## 3. API Verification (Web-Verified April 2026)

### 3.1 PAID Tier: Imagen 4.0

| Aspect | Bible v5.22 | Code | Verified (Google Docs) | Verdict |
|--------|------------|------|----------------------|---------|
| Model ID | `models/imagen-4.0-generate-001` | `imagen-4.0-generate-001` | `imagen-4.0-generate-001` | **CODE CORRECT** |
| Endpoint | `:predict` | `:predict` | `:predict` | Match |
| Payload | `instances[].prompt` + `parameters` | Same | Same | Match |
| Response | `predictions[].bytesBase64Encoded` | Same | Same | Match |
| Aspect Ratio | `1:1` | `1:1` | Options: 1:1, 3:4, 4:3, 9:16, 16:9 | Match |

**Analysis:** Code is correct. The Bible's `models/` prefix on the model ID would cause a double-prefix (`models/models/imagen-4.0-generate-001`) because the URL construction in `image_generator.py:42` already prepends `models/`.

**Source:** https://ai.google.dev/gemini-api/docs/imagen

### 3.2 FREE Tier: Gemini Image Generation

| Aspect | Bible v5.22 | Code | Verified (Google Docs) | Verdict |
|--------|------------|------|----------------------|---------|
| Model ID | `models/gemini-2.0-flash-exp` | `models/gemini-2.0-flash-exp-image-generation` | **Both deprecated.** Current: `gemini-2.5-flash-image` | **BOTH WRONG** |
| Endpoint | `:generateContent` | `:generateContent` | `:generateContent` | Match |
| Payload | `contents[].parts[]` | `contents[].parts[].text` | Requires `generationConfig.responseModalities: ["TEXT", "IMAGE"]` | **CODE MISSING CRITICAL FIELD** |
| Response | `candidates[].content.parts[].inlineData.data` | Same | Same | Match |

**Analysis:** 
- `gemini-2.0-flash-exp` is deprecated and shut down as of March 2026
- The code's `-image-generation` suffix variant is also deprecated
- **Critical:** The code does NOT include `generationConfig.responseModalities: ["TEXT", "IMAGE"]` in the payload. Without this, Gemini models return text only, not images. This is likely the **primary cause of FREE tier image generation failures**.

**Correct payload (April 2026):**
```json
{
  "contents": [{"parts": [{"text": "prompt"}]}],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"]
  }
}
```

**Source:** https://ai.google.dev/gemini-api/docs/image-generation

### 3.3 Library Deprecation Verification

**`google-generativeai` (v0.8.6):**
- Status: **DEPRECATED** -- deadline was August 31, 2025
- GitHub repo renamed to `deprecated-generative-ai-python`
- Migration target: `google-genai` package
- Migration pattern:
  - Old: `import google.generativeai as genai` / `genai.configure(api_key=...)` / `genai.GenerativeModel(name)`
  - New: `from google import genai` / `client = genai.Client(api_key=...)` / `client.models.generate_content(model=name, contents=...)`
- Affected files: `prompt_generator.py`, `qa_agent.py`

**Source:** https://ai.google.dev/gemini-api/docs/migrate

**`oauth2client` (v4.1.3):**
- Status: **DEPRECATED** (long ago)
- Migration target: `google-auth` + `google-auth-oauthlib`
- Affected files: `tracking.py`

---

## 4. Critical Issues (Prioritized)

### P0 - Blocking Production

| # | Issue | File:Line | Root Cause |
|---|-------|-----------|------------|
| 1 | Bible path hardcoded to v5.21 | `prompt_generator.py:95` | Reads `Series Master Bible v5.21.md` instead of v5.22 |
| 2 | Missing `responseModalities` in FREE tier | `image_generator.py:89-93` | Gemini models require this to return images |

### P1 - High Priority

| # | Issue | File:Line | Root Cause |
|---|-------|-----------|------------|
| 3 | FREE tier model deprecated | `config.py:60` | `gemini-2.0-flash-exp-image-generation` shut down; use `gemini-2.5-flash-image` |
| 4 | Orchestrator uses v1 image generator | `orchestrator.py:13` | Imports `image_generator` not `image_generator_v2` (v2 has reference image support) |
| 5 | `google-generativeai` past deprecation | `prompt_generator.py`, `qa_agent.py` | Must migrate to `google-genai` |

### P2 - Medium Priority

| # | Issue | File:Line | Root Cause |
|---|-------|-----------|------------|
| 6 | `oauth2client` deprecated | `tracking.py:8` | Should use `google-auth` |
| 7 | Agent Alpha is a stub | `system_architect.py:18` | `check_environment()` body is `pass` |
| 8 | `AssertionError` typo | `pdf_assembler.py:197` | Should be `AssertionError` (Python built-in) |
| 9 | Cover uses internal page dimensions | `pdf_assembler.py` | Should be 17.365" x 8.75" per Bible Section 1.4 |

### P3 - Low Priority / Cleanup

| # | Issue | File | Root Cause |
|---|-------|------|------------|
| 10 | v1/v2 file duplication | `image_generator_v2.py`, `pdf_assembler_v1_backup.py`, `pdf_assembler_v2.py` | Cleanup needed |
| 11 | Bible `MASTER_REF_IMG` typo | Bible Section 0.0 | `ref_pag2_01.png` should be `ref_page2_01.png` |
| 12 | Bible `models/` prefix on Imagen ID | Bible Section 0.0 | Would cause double `models/models/` prefix |

---

## 5. Image Quality Root Cause Analysis

The image quality mismatch with `MASTER_REF_IMG` is attributed to these factors (ordered by impact):

1. **Missing `responseModalities` (FREE tier)** -- Without `generationConfig.responseModalities: ["TEXT", "IMAGE"]`, Gemini returns text instead of images. Any images produced are from fallback/error paths.

2. **Wrong Bible version read** -- Agent Bravo reads v5.21 specs (`prompt_generator.py:95`), not v5.22. Prompt specs may be outdated or mismatched.

3. **v1 image generator active** -- Orchestrator imports v1 (`image_generator.py`) which sends text-only prompts. v2 (`image_generator_v2.py`) supports wireframes as multimodal input for layout enforcement but is not wired in.

4. **Dynamic DNA vs Fixed DNA** -- Code extracts style via Gemini vision analysis (non-deterministic) instead of using the Bible's fixed `[DNA_*]` macros (deterministic). This causes output variability across runs.

5. **Deprecated model** -- `gemini-2.0-flash-exp` may have degraded capabilities or be entirely unavailable.

---

## 6. Progress Tracker

### Implemented (80%)
- [x] Agent Omega orchestration workflow with error handling
- [x] Agent Bravo prompt generation with triangulation + negative DNA injection
- [x] Agent Charlie dual-tier image generation (PAID: Imagen 4.0, FREE: Gemini)
- [x] Agent Delta QA guard with Gemini vision + retry logic
- [x] Agent Echo PDF assembly with text overlay, coordinate validation, color masking
- [x] Agent Foxtrot Telegram bot with live dashboard updates
- [x] Agent Golf Google Sheets tracking
- [x] Config with deployment tier logic + rate limiting
- [x] TARGET_PAGES selective generation
- [x] Font registration with graceful degradation
- [x] All reference assets present (fonts, wireframes, structure examples, style refs)
- [x] PAID tier Imagen 4.0 REST API integration (correct endpoint, payload, response parsing)
- [x] Negative DNA library (all 4 categories match Bible Section 5.2)

### Pending (20%)
- [ ] **P0:** Add `generationConfig.responseModalities` to FREE tier payload
- [ ] **P0:** Fix Bible path from v5.21 to v5.22 in prompt_generator.py
- [ ] **P1:** Update FREE tier model ID to `gemini-2.5-flash-image`
- [ ] **P1:** Switch orchestrator to use image_generator_v2
- [ ] **P1:** Migrate `google-generativeai` to `google-genai`
- [ ] **P2:** Migrate `oauth2client` to `google-auth`
- [ ] **P2:** Implement Agent Alpha `check_environment()`
- [ ] **P2:** Fix `AssertionError` typo in pdf_assembler.py
- [ ] **P2:** Implement cover spread dimensions (17.365" x 8.75")
- [ ] **P3:** Clean up v1/v2 file duplication
- [ ] **P3:** Fix Bible typos (MASTER_REF_IMG path, models/ prefix)

---

## 7. Recommended Next Steps

1. **Immediate (P0):** Fix the two blocking issues -- Bible path and responseModalities
2. **Short-term (P1):** Update model ID, wire in v2 image generator, begin SDK migration
3. **Medium-term (P2):** Complete library migrations, implement Alpha, fix cover dimensions
4. **Cleanup (P3):** Remove duplicate files, update Bible typos
