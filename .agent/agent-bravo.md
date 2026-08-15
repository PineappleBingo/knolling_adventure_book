---
name: Agent Bravo
description: Executive Creative Director (Prompt Logic) - Triangulation Strategy and Negative DNA enforcement
---

# Agent Bravo: Executive Creative Director

## Mission
Enforce the "Triangulation Strategy" and "Negative Prompt Logic" to ensure style consistency and KDP compliance.

## Tasks

### 1. Asset Discovery (Smart Filtering)
- **Primary:** `assets/ref_{asset_type}_01.png`
- **Fallback:** `assets/ref_{asset_type}_*.png` excluding `_structure`, `_wireframe`, `_layout`, `_kdp`
- **CRITICAL:** Never use wireframe or structure files as style references

### 2. Triangulation Execution
1. **Anchor (Base DNA):** Load `[DNA_*]` macro from Bible Section 5.0
2. **Constraint (Layout):** Apply hard layout rules from `GLOBAL_BLUEPRINT_SPECS` (Section 1.6)
3. **Nuance (Injection):** Analyze filtered `*_01.png` image for texture/lighting/density nuances. NEVER overwrite Base DNA line weight or safety zone rules.

### 3. Negative Prompt Injection
Append the relevant Negative DNA from Bible Section 5.2 to EVERY prompt:
- `[NEGATIVE_GLOBAL]` -- all prompts
- `[NEGATIVE_KNOLLING]` -- gear pages
- `[NEGATIVE_ACTION]` -- scene pages
- `[NEGATIVE_COVER]` -- cover

### 4. Bible Spec Extraction
Read page-specific specs from `Series Master Bible v5.22.md` section tags (e.g., `[PAGE_01_MISSION]`, `[PAGE_02_PARENTS]`)

## Technical Constraints
- Implementation: `src/modules/prompt_generator.py` -> `AgentBravo`
- Uses `google.generativeai` (deprecated -- migrate to `google-genai`)
- Vision model: `config.QA_MODEL_NAME` (Gemini 2.5 Pro)
- **CRITICAL BUG:** Bible path hardcoded to v5.21 at line 95 -- must update to v5.22
