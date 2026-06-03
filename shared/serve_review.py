# httpx TLS for fal_client is handled in shared/ssl_compat (no verify=False).
import sys as _sys
from ssl_compat import trust_zscaler_if_present
trust_zscaler_if_present()
import warnings as _w
_w.filterwarnings("ignore")

"""
serve_review.py — local HTTP server: regenerate + override prompt.

POST /api/restill accepts {shot, note, override}.

Override non-empty → raw user prompt to fal, no canon/beat/note/rulebook.
Override empty → normal mode: canon-resolved beat prompt + REGENERATION FEEDBACK note.
"""
import argparse
import json
import os
import ssl
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ssl._create_default_https_context = ssl._create_unverified_context
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

def _load_env():
    here = Path.cwd().resolve()
    for parent in [here] + list(here.parents):
        env = parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
            return
_load_env()

_SHARED_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SHARED_DIR))
try:
    from restill_from_feedback import (
        resolve_canon_tokens, find_beats_file, load_rulebook_negatives,
        backup_existing_still, generate_still,
    )
except ImportError as e:
    sys.exit(f"ERROR: could not import from restill_from_feedback.py: {e}")


class ReviewServer(HTTPServer):
    def __init__(self, addr, handler_cls, project_dir, beats_data, canon,
                 negatives, model):
        super().__init__(addr, handler_cls)
        self.project_dir = project_dir
        self.beats = beats_data
        self.beats_by_idx = {b["index"]: b for b in beats_data}
        self.canon = canon
        self.negatives = negatives
        self.model = model
        self.stills_dir = project_dir / "stills"


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        sys.stderr.write(f"  {self.address_string()} - {format % args}\n")

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str):
        try:
            data = path.read_bytes()
        except (OSError, FileNotFoundError):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        srv: ReviewServer = self.server  # type: ignore

        if path == "/" or path == "/index.html" or path == "/review.html":
            html_path = srv.project_dir / "review.html"
            if not html_path.exists():
                self.send_response(500); self.end_headers()
                self.wfile.write(b"review.html not found"); return
            self._send_file(html_path, "text/html; charset=utf-8"); return

        if path == "/api/health":
            self._send_json(200, {"ok": True, "project": srv.project_dir.name}); return

        if path.startswith("/stills/"):
            relative = path.lstrip("/")
            file_path = (srv.project_dir / relative).resolve()
            if not str(file_path).startswith(str(srv.project_dir.resolve())):
                self.send_response(403); self.end_headers(); return
            if not file_path.exists():
                self.send_response(404); self.end_headers()
                self.wfile.write(b"Still not found"); return
            self._send_file(file_path, "image/png"); return

        self.send_response(404); self.end_headers()
        self.wfile.write(b"Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path != "/api/restill":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._send_json(400, {"ok": False, "error": f"bad JSON: {e}"}); return

        shot_idx = body.get("shot")
        note = (body.get("note") or "").strip()
        override = (body.get("override") or "").strip()

        if not isinstance(shot_idx, int):
            self._send_json(400, {"ok": False, "error": "shot must be an integer"}); return

        srv: ReviewServer = self.server  # type: ignore
        if shot_idx not in srv.beats_by_idx:
            self._send_json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return

        if override:
            # OVERRIDE MODE: send exactly what the user typed, nothing else
            final_prompt = override
            mode = "OVERRIDE"
            negatives_to_use = []  # also bypass rulebook negatives
        else:
            beat = srv.beats_by_idx[shot_idx]
            raw_prompt = beat.get("image_prompt", "")
            resolved = resolve_canon_tokens(raw_prompt, srv.canon)
            if note:
                final_prompt = f"{resolved.rstrip(' .')}. REGENERATION FEEDBACK: {note}"
            else:
                final_prompt = resolved
            mode = "NORMAL"
            negatives_to_use = srv.negatives

        print(f"\n[Regenerate] Shot {shot_idx:03d} [{mode}]")
        if override:
            print(f"  Override:   {override[:200]}{'...' if len(override) > 200 else ''}")
        else:
            print(f"  Note:       {note or '(none)'}")
        print(f"  Final:      {final_prompt[:220]}{'...' if len(final_prompt) > 220 else ''}")

        backup = backup_existing_still(srv.stills_dir, shot_idx)
        if backup:
            print(f"  Backed up:  {backup.name}")

        output_path = srv.stills_dir / f"shot_{shot_idx:03d}.png"
        success = generate_still(final_prompt, negatives_to_use, output_path, srv.model)

        if success:
            print(f"  OK -> {output_path.name}")
            self._send_json(200, {"ok": True, "shot": shot_idx, "mode": mode})
        else:
            print(f"  FAILED")
            self._send_json(500, {"ok": False, "error": "fal generation failed"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--beats")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--model", default="fal-ai/flux-pro/v1.1")
    args = parser.parse_args()

    project_dir = Path(args.project).resolve()
    if not project_dir.is_dir():
        sys.exit(f"ERROR: project dir not found: {project_dir}")
    if not os.environ.get("FAL_KEY"):
        sys.exit("ERROR: FAL_KEY not set in environment or .env file")

    review_html = project_dir / "review.html"
    if not review_html.exists():
        sys.exit(f"ERROR: review.html not found. Generate first via make_review_page.py")

    beats_file = find_beats_file(project_dir, args.beats)
    print(f"Beats: {beats_file}")
    data = json.loads(beats_file.read_text())
    if isinstance(data, dict) and "beats" in data:
        canon = data.get("canon", {})
        beats = data["beats"]
    else:
        canon = {}
        beats = data

    negatives = load_rulebook_negatives(project_dir)
    print(f"Negatives loaded: {len(negatives)} (used in NORMAL mode only)")
    print(f"Model: {args.model}")

    addr = ("127.0.0.1", args.port)
    server = ReviewServer(addr, Handler, project_dir, beats, canon, negatives, args.model)

    print()
    print(f"Server running at http://localhost:{args.port}/")
    print(f"Press Ctrl+C to stop.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
