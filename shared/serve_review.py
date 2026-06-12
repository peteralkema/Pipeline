# httpx TLS for fal_client is handled in shared/ssl_compat (no verify=False).
import sys as _sys
from ssl_compat import trust_zscaler_if_present
trust_zscaler_if_present()
import warnings as _w
_w.filterwarnings("ignore")

"""
serve_review.py — local HTTP server: regenerate + override prompt + AI fix.

POST /api/restill accepts {shot, note, override}.
  Override non-empty → raw user prompt to fal, no canon/beat/note/rulebook.
  Override empty → normal mode: canon-resolved beat prompt + REGENERATION FEEDBACK note.

POST /api/aifix accepts {shot}.
  Sends the current rendered still + the shot's intended (canon-resolved) prompt +
  the brand rules to Claude vision. Claude judges the image against the rules,
  returns a short diagnosis + a corrected prompt, which is then run through the
  SAME fal path as Override mode. Returns the diagnosis so the reviewer sees what
  changed. Vision calls happen only on shots the reviewer clicks — no batch pass.
"""
import argparse
import base64
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

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

# Anthropic client for the AI-fix vision diagnosis. Imported lazily so the
# server still starts (NORMAL/OVERRIDE regen still work) if anthropic is absent.
try:
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

VISION_MODEL = "claude-sonnet-4-6"

# The brand rules Claude judges each rendered still against. Mirrors the
# discipline-auditor's system prompt, extended to vision: it is now looking at
# the IMAGE, not just the prompt text, and must catch what actually rendered.
AIFIX_SYSTEM_PROMPT = """You are the quality reviewer for a YouTube channel called Final Hours: dignified, atmospheric, photoreal cinematic recreations of historical final hours.

You are shown a generated still image and the prompt that was intended to produce it. Judge the IMAGE against these brand rules and find what actually rendered wrong:

FACE-NEVER-RESOLVED (the most important rule):
- No human may have a clearly resolved face. Faces must be obscured by shadow, profile, distance, framing, back-of-head, or silhouette.
- A visible face, resolved eyes, or a clear facial expression is a violation.

PERIOD ACCURACY:
- No modern objects, clothing, hairstyles, materials, or architecture out of period.
- Famous structures must be the correct historical version (e.g. medieval cathedral not modern dome; Victorian wrought-iron lattice bridge not a modern suspension bridge with cables/towers).

ANATOMY & RENDER QUALITY:
- No broken anatomy, extra or malformed hands/limbs, phantom disembodied hands, fused figures.
- No gibberish or illegible text rendered in the image.

COMPOSITION:
- Group compositions of multiple resolved figures are weak; prefer object-substitution or anonymised framing.
- Fire/storm should read as environment and lighting, not a literal close-up subject.

Your job:
1. Look at the image. Decide if it violates any rule above, OR has an obvious quality problem (black/empty frame, nonsense, off-topic).
2. If it is FINE, say so — do not invent problems.
3. If it is WRONG, write a corrected image prompt that fixes the specific problem while preserving the intended location, period, lighting, atmosphere, and framing. Apply the channel rules (obscure the face, correct the period detail, substitute objects for groups, etc.). Restate the era anchor and the face-never-resolved framing explicitly in the corrected prompt.

Respond with STRICT JSON only, no preamble, no markdown:
{"verdict": "fine" | "fix", "diagnosis": "<one short sentence naming what is wrong, or why it is fine>", "corrected_prompt": "<the full corrected prompt if verdict is fix, else empty string>"}"""


def _sniff_media_type(data: bytes) -> str:
    """Detect image format from magic bytes; filenames lie (fal often returns JPEG as .png)."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


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
        # Build the Anthropic client once if available + keyed.
        self.anthropic = None
        if _ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            self.anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# Optional shared secret for public-bind mode. Set by main() from --key.
SERVER_KEY = None


def _key_ok(handler) -> bool:
    """True if auth is satisfied. No key configured (localhost mode) -> always ok.
    Static images (/stills/) and the health check are EXEMPT: they are not
    spend-capable and the page loads images via <img> tags that carry no key.
    Everything else (the page, /api/restill, /api/aifix) requires ?key=<SERVER_KEY>."""
    if not SERVER_KEY:
        return True
    from urllib.parse import urlparse, parse_qs, unquote as _unq
    parsed = urlparse(handler.path)
    p = _unq(parsed.path)
    if p.startswith("/stills/") or p == "/api/health":
        return True
    q = parse_qs(parsed.query)
    if q.get("key", [""])[0] == SERVER_KEY:
        return True
    # POST buttons (aifix / regenerate / restill) can't put the key in the URL;
    # accept it from the X-Review-Key request header instead.
    return handler.headers.get("X-Review-Key", "") == SERVER_KEY


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
        if not _key_ok(self):
            self.send_response(403); self.end_headers()
            self.wfile.write(b"403 - missing or bad ?key"); return

        if path == "/" or path == "/index.html" or path == "/review.html":
            html_path = srv.project_dir / "review.html"
            if not html_path.exists():
                self.send_response(500); self.end_headers()
                self.wfile.write(b"review.html not found"); return
            self._send_file(html_path, "text/html; charset=utf-8"); return

        if path == "/api/health":
            self._send_json(200, {
                "ok": True,
                "project": srv.project_dir.name,
                "aifix": srv.anthropic is not None,
            }); return

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
        if not _key_ok(self):
            self.send_response(403); self.end_headers(); return
        if path == "/api/restill":
            self._handle_restill(); return
        if path == "/api/aifix":
            self._handle_aifix(); return
        self.send_response(404); self.end_headers()

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(length).decode("utf-8")), None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return None, f"bad JSON: {e}"

    # ── Existing regenerate (Notes / Override) ──────────────────────────────

    def _handle_restill(self):
        body, err = self._read_body()
        if err:
            self._send_json(400, {"ok": False, "error": err}); return

        shot_idx = body.get("shot")
        note = (body.get("note") or "").strip()
        override = (body.get("override") or "").strip()

        if not isinstance(shot_idx, int):
            self._send_json(400, {"ok": False, "error": "shot must be an integer"}); return

        srv: ReviewServer = self.server  # type: ignore
        if shot_idx not in srv.beats_by_idx:
            self._send_json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return

        if override:
            final_prompt = override
            mode = "OVERRIDE"
            negatives_to_use = []
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

    # ── AI fix (vision diagnose → corrected prompt → regenerate) ────────────

    def _handle_aifix(self):
        body, err = self._read_body()
        if err:
            self._send_json(400, {"ok": False, "error": err}); return

        shot_idx = body.get("shot")
        if not isinstance(shot_idx, int):
            self._send_json(400, {"ok": False, "error": "shot must be an integer"}); return

        srv: ReviewServer = self.server  # type: ignore
        if srv.anthropic is None:
            self._send_json(503, {"ok": False, "error":
                "AI fix unavailable: anthropic not installed or ANTHROPIC_API_KEY not set"}); return
        if shot_idx not in srv.beats_by_idx:
            self._send_json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return

        still_path = srv.stills_dir / f"shot_{shot_idx:03d}.png"
        if not still_path.exists():
            self._send_json(404, {"ok": False, "error": f"still not found: {still_path.name}"}); return

        beat = srv.beats_by_idx[shot_idx]
        intended_prompt = resolve_canon_tokens(beat.get("image_prompt", ""), srv.canon)

        print(f"\n[AI fix] Shot {shot_idx:03d} — diagnosing image against brand rules...")

        # 1) Vision diagnosis
        try:
            img_bytes = still_path.read_bytes()
            media_type = _sniff_media_type(img_bytes)
            img_b64 = base64.standard_b64encode(img_bytes).decode("ascii")
            user_content = [
                {"type": "image", "source": {
                    "type": "base64", "media_type": media_type, "data": img_b64}},
                {"type": "text", "text":
                    f"Intended prompt for this shot:\n\n{intended_prompt}\n\n"
                    f"Judge the image against the brand rules and respond with the JSON object."},
            ]
            resp = srv.anthropic.messages.create(
                model=VISION_MODEL,
                max_tokens=1024,
                system=AIFIX_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_content}],
            )
            raw = resp.content[0].text.strip()
            # tolerate accidental ```json fences
            if raw.startswith("```"):
                raw = raw.strip("`")
                raw = raw[raw.find("{"):raw.rfind("}") + 1]
            verdict = json.loads(raw)
        except Exception as e:
            print(f"  diagnosis failed: {e}")
            self._send_json(500, {"ok": False, "error": f"vision diagnosis failed: {e}"}); return

        diagnosis = (verdict.get("diagnosis") or "").strip()
        corrected = (verdict.get("corrected_prompt") or "").strip()
        is_fix = verdict.get("verdict") == "fix" and bool(corrected)

        print(f"  Verdict:    {verdict.get('verdict')}")
        print(f"  Diagnosis:  {diagnosis}")

        # 2) If the model says the shot is fine, report back and regenerate nothing.
        if not is_fix:
            self._send_json(200, {
                "ok": True, "shot": shot_idx, "changed": False,
                "diagnosis": diagnosis or "Image looks consistent with the brand rules.",
            }); return

        # 3) Run the corrected prompt through the SAME fal path as Override mode
        #    (raw prompt, no canon/rulebook negatives — the corrected prompt is self-contained).
        print(f"  Corrected:  {corrected[:220]}{'...' if len(corrected) > 220 else ''}")
        backup = backup_existing_still(srv.stills_dir, shot_idx)
        if backup:
            print(f"  Backed up:  {backup.name}")

        success = generate_still(corrected, [], still_path, srv.model)
        if success:
            print(f"  OK -> {still_path.name}")
            self._send_json(200, {
                "ok": True, "shot": shot_idx, "changed": True,
                "diagnosis": diagnosis, "corrected_prompt": corrected,
            })
        else:
            print(f"  FAILED (fal generation)")
            self._send_json(500, {"ok": False, "error": "fal generation failed after diagnosis",
                                   "diagnosis": diagnosis})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--beats")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind address; use 0.0.0.0 for tunnel-free public access")
    parser.add_argument("--key", default=None,
                        help="shared secret required as ?key=... (MANDATORY when --host is public)")
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

    global SERVER_KEY
    if args.host not in ("127.0.0.1", "localhost") and not args.key:
        sys.exit("ERROR: refusing to bind public without --key. "
                 "This server can spend fal/Claude credits; pass --key <secret>.")
    SERVER_KEY = args.key
    addr = (args.host, args.port)
    server = ReviewServer(addr, Handler, project_dir, beats, canon, negatives, args.model)

    if server.anthropic is not None:
        print(f"AI fix: enabled ({VISION_MODEL})")
    else:
        print("AI fix: DISABLED (anthropic not installed or ANTHROPIC_API_KEY not set)")

    print()
    if args.host in ("127.0.0.1", "localhost"):
        print(f"Server running at http://localhost:{args.port}/")
    else:
        _q = f"?key={args.key}" if args.key else ""
        print(f"Server running at http://{args.host}:{args.port}/{_q}")
        print("  (open that exact URL — the key is required on every request)")
    print(f"Press Ctrl+C to stop.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
