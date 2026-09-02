# Sankalan

## Humanizer (branch: shobit-humanizer)

A free AI-text humanizer tuned for research papers. Runs in the cloud (OpenRouter free
model + Google Translate) — no local GPU or heavy RAM needed. Full docs and code are in
the [`humanizer/`](humanizer/) folder.

### Quick start
```bash
cd humanizer
pip install -r requirements.txt
cp .env.example .env        # then add your OpenRouter key
python api.py               # serves POST http://localhost:8000/humanize
```

Send text, get humanized text back:
```
POST /humanize   {"text": "...", "formal": true, "launder": true}
->               {"humanizedText": "...", "mode": "formal", "laundered": true}
```

See [`humanizer/README.md`](humanizer/README.md) for full usage, modes, and limits.
