#!/usr/bin/env python3
"""
patch_serve_review_public.py — let serve_review.py bind public with token auth,
so the stills page is reachable at http://<box-ip>:<port>/?key=<secret> with NO
SSH tunnel. Idempotent.

Backward-compatible: with no --host/--key flags it binds 127.0.0.1 and requires
no key — EXACTLY today's behaviour. The public bind is strictly opt-in, and when
you opt in you MUST pass --key (the patch enforces it) so the spend-capable
/api/restill and /api/aifix endpoints are never exposed unauthenticated.

Three edits to shared/serve_review.py:
  1. add a module-level _require_key(handler) helper + AUTH check
  2. gate do_GET and do_POST on the key
  3. add --host / --key args, bind to args.host, refuse public bind without a key,
     and print the full keyed URL.

Run:  python shared/patch_serve_review_public.py
Then once on the box:  sudo ufw allow 8001/tcp   (or scope to your home IP)
"""

import sys, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SR = REPO / "shared" / "serve_review.py"

# ---- edit 1: insert an auth helper + a module constant, before class Handler ----
ANCHOR1 = "class Handler(BaseHTTPRequestHandler):"
INSERT1 = '''# Optional shared secret for public-bind mode. Set by main() from --key.
SERVER_KEY = None


def _key_ok(handler) -> bool:
    """True if auth is satisfied: no key configured (localhost mode), or the
    request carries ?key=<SERVER_KEY>."""
    if not SERVER_KEY:
        return True
    from urllib.parse import urlparse, parse_qs
    q = parse_qs(urlparse(handler.path).query)
    return q.get("key", [""])[0] == SERVER_KEY


'''

# ---- edit 2a: gate do_GET ----
ANCHOR2 = '''    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        srv: ReviewServer = self.server  # type: ignore
'''
INSERT2 = '''    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        srv: ReviewServer = self.server  # type: ignore
        if not _key_ok(self):
            self.send_response(403); self.end_headers()
            self.wfile.write(b"403 - missing or bad ?key"); return
'''

# ---- edit 2b: gate do_POST ----
ANCHOR3 = '''    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
'''
INSERT3 = '''    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not _key_ok(self):
            self.send_response(403); self.end_headers(); return
'''

# ---- edit 3a: argparse — add --host and --key ----
ANCHOR4 = '''    parser.add_argument("--port", type=int, default=8000)'''
INSERT4 = '''    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind address; use 0.0.0.0 for tunnel-free public access")
    parser.add_argument("--key", default=None,
                        help="shared secret required as ?key=... (MANDATORY when --host is public)")'''

# ---- edit 3b: bind to args.host, enforce key on public bind, set SERVER_KEY, print URL ----
ANCHOR5 = '''    addr = ("127.0.0.1", args.port)
    server = ReviewServer(addr, Handler, project_dir, beats, canon, negatives, args.model)'''
INSERT5 = '''    global SERVER_KEY
    if args.host not in ("127.0.0.1", "localhost") and not args.key:
        sys.exit("ERROR: refusing to bind public without --key. "
                 "This server can spend fal/Claude credits; pass --key <secret>.")
    SERVER_KEY = args.key
    addr = (args.host, args.port)
    server = ReviewServer(addr, Handler, project_dir, beats, canon, negatives, args.model)'''

# ---- edit 3c: the printed URL line ----
ANCHOR6 = '''    print(f"Server running at http://localhost:{args.port}/")'''
INSERT6 = '''    if args.host in ("127.0.0.1", "localhost"):
        print(f"Server running at http://localhost:{args.port}/")
    else:
        _q = f"?key={args.key}" if args.key else ""
        print(f"Server running at http://{args.host}:{args.port}/{_q}")
        print("  (open that exact URL — the key is required on every request)")'''

EDITS = [
    ("auth helper", ANCHOR1, INSERT1 + ANCHOR1),
    ("do_GET gate", ANCHOR2, INSERT2),
    ("do_POST gate", ANCHOR3, INSERT3),
    ("argparse --host/--key", ANCHOR4, INSERT4),
    ("bind + key enforce", ANCHOR5, INSERT5),
    ("printed URL", ANCHOR6, INSERT6),
]


def main():
    if not SR.exists():
        sys.exit(f"ERROR: {SR} not found. Run from repo root.")
    src = SR.read_text(encoding="utf-8")

    if "_key_ok" in src and "--key" in src:
        print("  [skip] serve_review.py: public-bind auth already present.")
        return

    # verify ALL anchors before writing anything
    for label, anchor, _new in EDITS:
        if anchor not in src:
            sys.exit(f"  [FAIL] anchor not found: {label}. Aborting (no write).")
        if src.count(anchor) != 1:
            sys.exit(f"  [FAIL] anchor for {label} found {src.count(anchor)}x (expected 1). Aborting.")

    bak = SR.with_suffix(".py.pre_public_auth")
    shutil.copy2(SR, bak)
    for label, anchor, new in EDITS:
        src = src.replace(anchor, new, 1)
        print(f"  [ok] {label}")
    SR.write_text(src, encoding="utf-8")

    print(f"\nDONE (backup -> {bak.name}). Verify:")
    print('  grep -n "_key_ok\\|--key\\|--host" shared/serve_review.py')
    print("\nThen, ONCE on the box, open the firewall port:")
    print("  sudo ufw allow 8001/tcp        # or: sudo ufw allow from <home-ip> to any port 8001")
    print("\nRun tunnel-free, e.g.:")
    print("  python shared/serve_review.py --project <proj>/modea --port 8001 \\")
    print("    --host 0.0.0.0 --key choose-a-long-random-secret")


if __name__ == "__main__":
    main()
