# My Humanizer

A free AI-text humanizer tuned for research papers. Runs in the cloud (OpenRouter free
model + Google Translate), so it needs no local GPU or heavy RAM.

## Files
- `power_humanizer.py` — the humanizer engine (formal + casual modes, laundering, auto-fixes).
- `api.py` — HTTP route: send text, get humanized text back.
- `humanize_paper_doc.py` — humanize a whole paper's body prose from a text file, keeping headers/references intact.
- `.env` — your API keys (OpenRouter, and optional Gemini/Groq).
- `requirements.txt` — Python dependency.

## Setup (once)
```bash
pip install -r requirements.txt
```

## Use it as a route (send text, get text)
Start the server:
```bash
python api.py
```
Call it:
```
POST http://localhost:8000/humanize
  JSON body:  {"text": "...", "formal": true, "launder": true}
  or raw:     Content-Type: text/plain, body = the text
  response:   {"humanizedText": "...", "mode": "formal", "laundered": true}
GET http://localhost:8000/health  ->  {"ok": true}
```
- `formal`  (default true): research register. Set false for casual.
- `launder` (default true): translation laundering (lowest scores). Set false for a faithful pass.

## Use it from the command line
```bash
python power_humanizer.py -f input.txt -o output.txt
```
Flags: `--casual`, `--no-launder`, `--rudra`, `--model NAME`.

## Engine & limits
- OpenRouter free model `minimax/minimax-m3:free` + Google Translate. All free.
- OpenRouter free tier: ~20 requests/min, ~50 requests/day (no credits). Buying $10 of
  OpenRouter credits once raises the daily cap to ~1000, enough for a full paper in one run.
- ~5s per call; a paragraph uses 1-6 calls depending on mode.

## Notes
- Keys live in `.env`: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, optional `GEMINI_API_KEY`, `GROQ_API_KEY`.
- Laundering lowers detector scores most but can reword specifics. For real papers, proofread
  the output against your original before submitting.
