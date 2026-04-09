# How to Run — Knolling Adventures KDP Factory

## 1. Environment Setup

Create `.env` in project root:

```env
# Required
GOOGLE_API_KEY=your-google-ai-api-key
TELEGRAM_TOKEN=your-telegram-bot-token

# Deployment Tier (controls model + rate limits)
DEPLOYMENT_TIER=FREE
# FREE: gemini-2.5-flash-image, 20s delay between image gen calls
# PAID: imagen-4.0-generate-001, 0.5s delay

# Optional
PAGE_COUNT=50                # Default page count
TARGET_PAGES=1,50            # Generate only specific pages (comma-separated, ranges ok: 1,3-5,50)
PDF_DEBUG_MODE=false          # Set true to render text overlay in magenta for debugging
```

## 2. Google Sheets (Optional)

Place `credentials.json` (service account key) in project root. Share the "Mission Control" sheet with the service account email.

If you skip this, the app still runs — tracking just logs warnings.

## 3. Install Dependencies

```bash
# Option A: Pipenv
pipenv install

# Option B: venv (already exists)
./venv/bin/pip install -r <(pipenv requirements)
```

## 4. Run the Server

```bash
# With pipenv
pipenv run python src/main.py

# With venv
./venv/bin/python src/main.py
```

The Telegram bot starts polling. You'll see:
```
Agent Omega initialized.
Agent Foxtrot initialized.
Starting Telegram Bot...
```

## 5. Use the Bot

In Telegram, message your bot:

| Command | Action |
|---------|--------|
| `/start` | Welcome message + Mission Control link |
| `/generate Firefighter` | Generate a full "Firefighter" themed coloring book |
| `/generate Dinosaur` | Generate a "Dinosaur" themed book |

The bot sends live progress updates, preview images, and the final PDF link.

## 6. Quick Test (No Telegram)

Run the E2E smoke test with mocked agents:

```bash
./venv/bin/python tests/reproduce_e2e.py
```

Run unit tests:

```bash
./venv/bin/python -m pytest tests/ -v
```

## 7. Output

Generated files go to `temp/`:
- `temp/{Theme}_Page{N}_{timestamp}.png` — individual page images
- `temp/Knolling_Adventure_{timestamp}.pdf` — assembled PDF

## Rate Limits (FREE Tier)

| Operation | Delay |
|-----------|-------|
| Image generation | 20s between calls |
| QA check | 35s between calls |
| Prompt generation | 5s between calls |

A full 50-page book on FREE tier takes ~45 min. Use `TARGET_PAGES=1,50` for quick 2-page test runs (~2 min).
