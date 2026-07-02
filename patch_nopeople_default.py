#!/usr/bin/env python3
"""
patch_nopeople_default.py (v2, anchored to live box code with the NB2 guard present)

Widens the existing NB2 phrase-guard into an architectural default. The phrase-list
("no people/figures/crew/person") missed person-free beats worded "no face" (a hand
lifting a burning branch) or "no clear animal" (predator eyes in grass), so the
people_directive was appended and NB2-text summoned a cartoon human onto a clean
plate. QQrew Fire beats 9, 26, 45, 52.

FIX: on a reference-mode channel, a beat reaching the TEXT path has NO reference
images, so by Rule 1 (a human in frame is a crew member carrying a {token} -> ref
-> the /edit path, or does not exist) it is person-free BY DEFINITION. Strip the
people_directive unconditionally in that case. Keeps the existing phrase-guard for
non-reference channels (Final Hours etc. legitimately want crowds). Cannot be beaten
by wording.

Two edits in shared/recreation_pipeline.py:
  1. generate_still(): after the phrase-guard, add
     `if render_mode=="reference" and not reference_images: people=""`.
  2. _flux_fallback_still(): mirror it (no reference_images param there; strip on any
     reference-mode channel).

Idempotent (sentinel PATCH_NOPEOPLE_DEFAULT), anchor-verified against the LIVE code
(which already carries PATCH_NB2_TEXT), backup .pre_nopeople, py_compiles first.
Relaunch/Regenerate renders after pulling. No storyboard rebuild -- this is render-time
prompt assembly, so Regenerating the affected text beats picks it up.

    python3 patch_nopeople_default.py --file shared/recreation_pipeline.py
"""
from __future__ import annotations
import argparse, py_compile, shutil, sys, tempfile
from pathlib import Path

SENTINEL = "PATCH_NOPEOPLE_DEFAULT"
EDITS = [['generate_still no-people default', '    people = rb.get("people_directive", "")\n    # PATCH_NB2_TEXT: the people_directive is a face/people enhancer appended to\n    # EVERY text prompt -- on beats that declare themselves people-free ("no\n    # people/figures/crew") it actively summons humans onto clean plates\n    # (graphics, maps, empty wides). Skip it on those beats.\n    _lp = image_prompt.lower()\n    if people and any(t in _lp for t in ("no people", "no figures", "no crew", "no person")):\n        people = ""\n    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"', '    people = rb.get("people_directive", "")\n    # PATCH_NB2_TEXT: the people_directive is a face/people enhancer appended to\n    # EVERY text prompt -- on beats that declare themselves people-free ("no\n    # people/figures/crew") it actively summons humans onto clean plates\n    # (graphics, maps, empty wides). Skip it on those beats.\n    _lp = image_prompt.lower()\n    if people and any(t in _lp for t in ("no people", "no figures", "no crew", "no person")):\n        people = ""\n    # PATCH_NOPEOPLE_DEFAULT: the phrase-list above missed person-free beats worded\n    # "no face" / "no clear animal" (a hand lifting a branch, predator eyes) -> a\n    # cartoon human got summoned onto a clean plate. On a reference-mode channel a\n    # beat reaching the TEXT path has NO refs, so by Rule 1 (human = crew {token}\n    # -> /edit, or nobody) it is person-free BY DEFINITION. Strip unconditionally.\n    if config.get("render_mode") == "reference" and not reference_images:\n        people = ""\n    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"'], ['flux fallback no-people default', '    people = rb.get("people_directive", "")\n    _lp = image_prompt.lower()  # PATCH_NB2_TEXT: same no-people guard as generate_still\n    if people and any(t in _lp for t in ("no people", "no figures", "no crew", "no person")):\n        people = ""\n    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people\n                   else f"{style_suffix}. {image_prompt}")', '    people = rb.get("people_directive", "")\n    _lp = image_prompt.lower()  # PATCH_NB2_TEXT: same no-people guard as generate_still\n    if people and any(t in _lp for t in ("no people", "no figures", "no crew", "no person")):\n        people = ""\n    # PATCH_NOPEOPLE_DEFAULT: mirror generate_still. On a reference-mode channel the\n    # flux fallback should never inject anonymous people either.\n    if config.get("render_mode") == "reference":\n        people = ""\n    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people\n                   else f"{style_suffix}. {image_prompt}")']]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="shared/recreation_pipeline.py")
    a = ap.parse_args()
    t = Path(a.file)
    if not t.is_file():
        print(f"ERROR: not found: {t}", file=sys.stderr); return 2
    src = t.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {t}"); return 0
    for label, old, _new in EDITS:
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor {label!r} found {c}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src
    for _l, old, new in EDITS:
        out = out.replace(old, new, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: result does not compile:\n{e}", file=sys.stderr); tmp.unlink(missing_ok=True); return 4
    tmp.unlink(missing_ok=True)
    b = t.with_suffix(t.suffix + ".pre_nopeople")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name}, {len(EDITS)} edits)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
