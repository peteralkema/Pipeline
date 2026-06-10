#!/usr/bin/env python3
"""
patch_modea_gate_oneurl.py — replace the Mode A gate's broken 3-step tunnel block
with a single call to shared/review.py, which prints ONE clickable URL.

Before: STEP 1 (box: activate + make_review_page + serve_review), STEP 2 (laptop:
lsof kill + ssh -L tunnel), STEP 3 (browser localhost) — fragile, wrong paths, dies
on window close.

After: the gate runs `review.py --project <engine_project>` for the user (builds the
page, repoints the always-on user service, prints the URL) and tells them to click it.

Idempotent. Verifies the anchor block exists verbatim, backs up to .pre_oneurl,
refuses to half-apply. Run from repo root (laptop):
    python3 shared/patch_modea_gate_oneurl.py
"""
import sys
from pathlib import Path

TARGET = Path("shared/modea_leg.py")
MARKER = "review.py')} --project"

# The exact block to replace (the three STEP panels through the browser line).
# Anchored on stable substrings; we replace from 'STEP 1' panel start to the
# 'http://localhost' browser line inclusive.
OLD = '''  │  STEP 1 ▸ In your BOX window (prompt: peter@pipeline-prod), paste:     │
  │                                                                        │
        source ~/venvs/pipeline/bin/activate
        python {os.path.join(shared, 'make_review_page.py')} --project {engine_project}
        python {os.path.join(shared, 'serve_review.py')} --project {engine_project} --port {port}
  │                                                                        │
  │  STEP 2 ▸ In your LAPTOP window (prompt: your-name@laptop), paste:     │
  │                                                                        │
        lsof -ti :{port} | xargs kill 2>/dev/null; true
        ssh -p 443 -L {port}:localhost:{port} {box}
  │                                                                        │
  │  STEP 3 ▸ Open this in your browser:                                   │
  │                                                                        │
        http://localhost:{port}'''

NEW = '''  │  ONE STEP ▸ the server is always on. Get your review URL:              │
  │                                                                        │
        python {os.path.join(shared, 'review.py')} --project {engine_project}
  │                                                                        │
  │  That prints a URL like:  http://116.202.18.68:8001/?key=fh2026        │
  │  Click it. No tunnel, no localhost, no login.                         │'''


def fail(m):
    print(f"ABORT: {m}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found — run from repo root.")
    src = TARGET.read_text(encoding="utf-8")
    if MARKER in src:
        print("already patched (review.py call present) — no change. \u2713")
        return
    if src.count(OLD) != 1:
        fail(f"the 3-step block was not found verbatim (found {src.count(OLD)}). "
             "modea_leg.py may have changed — inspect lines ~191-215 before patching.")
    patched = src.replace(OLD, NEW, 1)
    if MARKER not in patched:
        fail("post-write verification failed — not writing.")
    TARGET.with_suffix(".py.pre_oneurl").write_text(src, encoding="utf-8")
    TARGET.write_text(patched, encoding="utf-8")
    print(f"patched {TARGET} (backup .pre_oneurl) \u2713")
    print("verify:  grep -n \"review.py')} --project\" shared/modea_leg.py")


if __name__ == "__main__":
    main()
