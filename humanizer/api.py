"""
HTTP route for the humanizer. Send text, get humanized text back.
Uses power_humanizer (OpenRouter minimax + laundering + formal rewrite). No extra deps.

Run:
  python api.py            # serves on http://localhost:8000

Call it:
  POST /humanize
  body (JSON):  {"text": "...", "formal": true, "launder": true}
  or raw text:  Content-Type: text/plain  with the text as the body
  response:     {"humanizedText": "...", "mode": "formal", "laundered": true}

Health check:  GET /health  ->  {"ok": true}
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import power_humanizer as ph

PORT = 8000
MAX_CHARS = 20000


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": "use POST /humanize"})

    def do_POST(self):
        if self.path.rstrip("/") != "/humanize":
            return self._send(404, {"error": "use POST /humanize"})

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        ctype = (self.headers.get("Content-Type") or "").lower()

        text, formal, launder = "", True, True
        if "application/json" in ctype:
            try:
                d = json.loads(raw or "{}")
            except json.JSONDecodeError:
                return self._send(400, {"error": "invalid JSON"})
            text = d.get("text", "")
            formal = bool(d.get("formal", True))
            launder = bool(d.get("launder", True))
        else:
            text = raw  # raw text body

        if not text.strip():
            return self._send(400, {"error": "empty 'text'"})
        if len(text) > MAX_CHARS:
            return self._send(413, {"error": f"text too long: max {MAX_CHARS} chars"})

        try:
            out = ph.humanize(text.strip(), do_launder=launder, formal=formal)
            self._send(200, {"humanizedText": out, "mode": "formal" if formal else "casual",
                             "laundered": launder})
        except Exception as e:
            self._send(502, {"error": "humanization failed", "detail": str(e)})

    def log_message(self, *a):
        pass  # quiet


if __name__ == "__main__":
    print(f"Humanizer route running on http://localhost:{PORT}")
    print(f"  POST http://localhost:{PORT}/humanize")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
