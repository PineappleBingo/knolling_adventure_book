---
name: Agent Golf
description: Production Analyst (Tracking) - Google Sheets "Mission Control" logging
---

# Agent Golf: Production Analyst

## Mission
Google Sheets "Mission Control" for production tracking.

## Tasks
1. **start_job:** Initialize new row `[RunID, Date, Theme, Status, Images_Passed, Drive_Link]`
2. **update_progress:** Update status and image count for a running job
3. **finish_job:** Mark as COMPLETED, add Drive link
4. **log_error:** Mark as FAILED with error message

## Technical Constraints
- Implementation: `src/modules/tracking.py` -> `AgentGolf`
- Uses `gspread` + `oauth2client` (deprecated -- migrate to `google-auth`)
- Requires `credentials.json` (service account)
- Sheet name: "Mission Control"
- Non-blocking: App starts even if Sheets connection fails
- Row lookup by RunID via `sheet.find()`

## Known Issues
- `oauth2client` is deprecated; should migrate to `google-auth` + `google-auth-oauthlib`
