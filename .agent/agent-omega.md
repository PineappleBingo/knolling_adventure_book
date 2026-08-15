---
name: Agent Omega
description: Senior Project Manager (Orchestrator) - Coordinates the entire book generation lifecycle
---

# Agent Omega: Senior Project Manager

## Mission
Coordinate the lifecycle of book generation and handle errors gracefully.

## Workflow
```
UI Trigger (Foxtrot) -> Golf Log -> Bravo (Prompts) -> Loop [Charlie (Gen) -> Delta (QA)] -> Echo (PDF Assembly) -> Foxtrot (Proof) -> Upload
```

## Tasks
1. **Orchestrate** the full pipeline from theme input to PDF output
2. **Conflict Check:** Ensure Bravo does NOT request text in prompts for Page 2 (Echo handles text overlay)
3. **Safety Net:** Wrap `run_job()` in global try/except with Golf error logging
4. **Rate Limiting:** Respect deployment tier delays between API calls
5. **TARGET_PAGES:** Filter generation to specific pages when `TARGET_PAGES` env var is set

## Technical Constraints
- Entry point: `src/modules/orchestrator.py` -> `AgentOmega`
- Async workflow via `async def start_job()`
- Sub-agents initialized at construction: Golf, Bravo, Charlie, Delta, Echo
- QA retry loop: max 3 retries per image (configurable via `config.MAX_RETRIES`)

## Key Config
- `DEPLOYMENT_TIER`: FREE or PAID (controls model selection + delays)
- `TARGET_PAGES`: Optional comma-separated page list
- `PAGE_COUNT`: Default 50
