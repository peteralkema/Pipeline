#!/usr/bin/env python3
"""
patch_serve_review_key_exempt_stills.py — fix the public-bind auth so it stops
blocking the page's own image loads.

Problem: _key_ok() gated ALL GETs on ?key. The review page loads each still via
<img src="/stills/shot_NNN.png"> with no key, so every image 403'd and every tile
showed "Still not generated yet".

Fix: exempt static image GETs (/stills/) and the health check (/api/health) from
the key. These are not spend-capable, and /stills/ already has a path-traversal
guard. The key still protects the page itself and the POST spend endpoints
(/api/restill, /api/aifix).

Idempotent. Run:  python shared/patch_serve_review_key_exempt_stills.py
"""

import sys, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SR = REPO / "shared" / "serve_review.py"

OLD = '''def _key_ok(handler) -> bool:
    """True if auth is satisfied: no key configured (localhost mode), or the
    request carries ?key=<SERVER_KEY>."""
    if not SERVER_KEY:
        return True
    from urllib.parse import urlparse, parse_qs
    q = parse_qs(urlparse(handler.path).query)
    return q.get("key", [""])[0] == SERVER_KEY'''

NEW = '''def _key_ok(handler) -> bool:
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
    return q.get("key", [""])[0] == SERVER_KEY'''


def main():
    if not SR.exists():
        sys.exit(f"ERROR: {SR} not found. Run from repo root.")
    src = SR.read_text(encoding="utf-8")

    if 'p.startswith("/stills/")' in src:
        print("  [skip] /stills/ exemption already present.")
        return
    if OLD not in src:
        sys.exit("  [FAIL] could not find the _key_ok body to replace "
                 "(was the public-bind patch applied first?). No write.")
    if src.count(OLD) != 1:
        sys.exit(f"  [FAIL] _key_ok body found {src.count(OLD)}x (expected 1). No write.")

    bak = SR.with_suffix(".py.pre_stills_exempt")
    shutil.copy2(SR, bak)
    SR.write_text(src.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"  [ok] /stills/ + /api/health exempted from key (backup -> {bak.name}).")
    print("\nRestart the server, then reload the keyed page URL — tiles should fill in.")


if __name__ == "__main__":
    main()
