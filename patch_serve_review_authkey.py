#!/usr/bin/env python3
"""
patch_serve_review_authkey.py  —  idempotent

Fixes: review-page AI Fix / Regenerate / Restill buttons return HTTP 403
(empty body -> browser "Unexpected end of JSON input").

Root cause: _key_ok() in serve_review.py reads the shared key ONLY from the
URL query string. The page + <img> GETs carry ?key=... so they pass, but the
button fetch() POSTs to /api/aifix, /api/regenerate, /api/restill send no key
at all -> blocked before the handler runs -> 403 with no JSON body.

Two coordinated, backward-compatible edits:
  1) serve_review.py  : _key_ok() also accepts an "X-Review-Key" request header
                        (query-string path is preserved unchanged).
  2) make_review_page.py : the generated page learns the key from its own URL
                        and sends it as the X-Review-Key header on every POST.
                        (Belt + braces: backend tolerates either source;
                        frontend always sends the header.)

Run on the LAPTOP against ~/Projects/Pipeline. Verifies each anchor before
writing and refuses to double-apply. Then commit -> push -> pull on box ->
restart the review server -> regenerate this project's review.html from the
fixed generator.

Usage:
    python3 patch_serve_review_authkey.py            # patches ./shared/...
    python3 patch_serve_review_authkey.py --root ~/Projects/Pipeline
"""

import argparse
import sys
from pathlib import Path

PATCH_TAG = "X-Review-Key"  # presence of this marker == already patched


# ─────────────────────────────────────────────────────────────────────────────
# Edit 1 — serve_review.py : _key_ok() accepts the header as well as ?key=
# ─────────────────────────────────────────────────────────────────────────────

SERVE_ANCHOR = '''    q = parse_qs(parsed.query)
    return q.get("key", [""])[0] == SERVER_KEY'''

SERVE_REPLACEMENT = '''    q = parse_qs(parsed.query)
    if q.get("key", [""])[0] == SERVER_KEY:
        return True
    # POST buttons (aifix / regenerate / restill) can't put the key in the URL;
    # accept it from the X-Review-Key request header instead.
    return handler.headers.get("X-Review-Key", "") == SERVER_KEY'''


# ─────────────────────────────────────────────────────────────────────────────
# Edit 2 — make_review_page.py : emit a KEY const + send the header on POSTs
#
# The generator writes the page JS via an f-string, so literal braces in the
# emitted JS are doubled ({{ }}). We therefore match the DOUBLED forms here.
# The page reads its own ?key=... and attaches it as X-Review-Key on each POST.
# ─────────────────────────────────────────────────────────────────────────────

# Anchor: the existing IS_SERVED line in the generator (doubled-brace context).
GEN_KEY_ANCHOR = (
    'const IS_SERVED = window.location.protocol === "http:" '
    '|| window.location.protocol === "https:";'
)

GEN_KEY_INSERT = (
    'const IS_SERVED = window.location.protocol === "http:" '
    '|| window.location.protocol === "https:";\n'
    '    const REVIEW_KEY = new URLSearchParams(window.location.search).get("key") || "";'
)

# The two POST header lines in the GENERATOR are doubled-brace f-string literals.
GEN_HEADER_ANCHOR = 'headers: {{"Content-Type": "application/json"}},'
GEN_HEADER_REPLACEMENT = (
    'headers: {{"Content-Type": "application/json", "X-Review-Key": REVIEW_KEY}},'
)


def _read(p: Path) -> str:
    if not p.exists():
        sys.exit(f"ERROR: not found: {p}")
    return p.read_text()


def patch_serve(root: Path) -> bool:
    p = root / "shared" / "serve_review.py"
    src = _read(p)

    if "X-Review-Key" in src:
        print(f"  ✓ serve_review.py already patched (X-Review-Key present) — skipping")
        return False
    if SERVE_ANCHOR not in src:
        sys.exit(
            "ERROR: serve_review.py anchor not found.\n"
            "Expected the _key_ok() tail:\n"
            f"{SERVE_ANCHOR}\n"
            "Refusing to guess. Re-grep the file and update the patch."
        )
    if src.count(SERVE_ANCHOR) != 1:
        sys.exit(f"ERROR: serve_review.py anchor appears {src.count(SERVE_ANCHOR)}x "
                 "(want exactly 1). Refusing to patch ambiguously.")

    p.write_text(src.replace(SERVE_ANCHOR, SERVE_REPLACEMENT))
    print(f"  ✓ patched {p}  (_key_ok now accepts X-Review-Key header)")
    return True


def patch_generator(root: Path) -> bool:
    p = root / "shared" / "make_review_page.py"
    src = _read(p)

    if "X-Review-Key" in src or "REVIEW_KEY" in src:
        print(f"  ✓ make_review_page.py already patched — skipping")
        return False

    if GEN_KEY_ANCHOR not in src:
        sys.exit(
            "ERROR: make_review_page.py IS_SERVED anchor not found.\n"
            f"Expected: {GEN_KEY_ANCHOR}\n"
            "Refusing to guess."
        )
    n_headers = src.count(GEN_HEADER_ANCHOR)
    if n_headers < 1:
        sys.exit(
            "ERROR: make_review_page.py header anchor not found.\n"
            f"Expected (doubled-brace f-string form): {GEN_HEADER_ANCHOR}\n"
            "If the generator uses single braces, the page isn't an f-string — re-check."
        )

    # 1) inject the REVIEW_KEY const right after IS_SERVED (once)
    src = src.replace(GEN_KEY_ANCHOR, GEN_KEY_INSERT, 1)
    # 2) add the header to every POST (aifix + restill, and regenerate if present)
    src = src.replace(GEN_HEADER_ANCHOR, GEN_HEADER_REPLACEMENT)

    p.write_text(src)
    print(f"  ✓ patched {p}  (emits REVIEW_KEY + sends X-Review-Key on {n_headers} POST call(s))")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".",
                    help="repo root (default: current dir). On laptop: ~/Projects/Pipeline")
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    print(f"patch_serve_review_authkey.py — root={root}")

    changed = False
    changed |= patch_serve(root)
    changed |= patch_generator(root)

    print()
    if changed:
        print("DONE. Next:")
        print("  1) eyeball the diff:  git diff shared/serve_review.py shared/make_review_page.py")
        print("  2) commit + push from laptop")
        print("  3) box: git pull --no-edit")
        print("  4) box: regenerate this project's page from the fixed generator:")
        print("       python shared/make_review_page.py --project sacred-dawn/projects/the-daughters/modea")
        print("  5) box: restart the review server:")
        print("       lsof -ti :8001 | xargs kill -9")
        print("       python shared/review.py --project sacred-dawn/projects/the-daughters/modea")
        print("  6) hard-refresh page (Cmd-Shift-R), click AI Fix, watch journalctl for 200 not 403")
    else:
        print("No changes (already fully patched).")


if __name__ == "__main__":
    main()
