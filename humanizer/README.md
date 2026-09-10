# My Humanizer

A free AI-text humanizer tuned for research papers. Runs in the cloud (Google Gemini for
the rewrite + Google Translate for laundering), so it needs no local GPU or heavy RAM.

## Files
- `power_humanizer.py` — the humanizer engine (formal + casual modes, laundering, auto-fixes).
- `api.py` — HTTP route: send text, get humanized text back.
- `humanize_paper_doc.py` — humanize a whole paper's body prose from a text file, keeping headers/references intact.
- `.env` — your API keys (Gemini + OpenRouter).
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
- **Formal rewrite: Google Gemini `gemini-flash-lite-latest`** — fast (~1-4s/paragraph) and
  faithful (keeps length and facts). This is the default and does the main work.
- **Laundering + fallback: OpenRouter** `nvidia/nemotron-3-super-120b-a12b:free` + Google Translate.
- Free to run. Gemini's free tier (~15 req/min) is the practical ceiling; large papers just pace out.
- Per HTTP request: **max 20,000 characters** (larger inputs must be chunked). Each paragraph
  rewrite is capped at ~3,000 words output (never an issue for real paragraphs).

## Notes
- Keys live in `.env`: `GEMINI_API_KEY`, `GEMINI_MODEL`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`.
- Free model IDs change often. If a call returns 404, the model was retired — swap the id in `.env`.
- Laundering lowers detector scores most but can reword specifics. For real papers, proofread
  the output against your original before submitting.
