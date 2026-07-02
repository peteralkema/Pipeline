#!/usr/bin/env python3
"""
patch_nopeople_default.py -- stop the people_directive summoning cartoon humans
onto person-free beats (QQrew Fire, 02 Jul).

ROOT CAUSE: every text-path beat gets the rulebook people_directive appended
("...appealing realistic detailed faces where people are present..."). On the
reference-mode channel (QQrew) the earlier phrase-guard only stripped it when the
beat literally said "no people/figures/crew". Person-free beats worded "no face"
(a hand lifting a branch) or "no clear animal" (predator eyes in grass) slipped
the guard, kept the directive, and NB2-text rendered a smiling cartoon human onto
a plate that never asked for one. Beats 9, 26, 45, 52 in Fire.

THE FIX (architectural, not a bigger denylist): on a reference-mode channel a beat
that reaches the TEXT path has NO reference images, which -- by Rule 1 (a human in
frame is a crew member carrying a {token}->ref->/edit, or does not exist) -- means
it is person-free BY DEFINITION. So strip the people_directive unconditionally when
render_mode == "reference" and there are no reference_images. Cannot be defeated by
wording. Non-reference channels (Final Hours etc.) are untouched -- they still get
the directive, because they legitimately want anonymous crowds.

TWO EDITS in shared/recreation_pipeline.py:
  1. generate_still(): strip people when render_mode==reference and not reference_images.
  2. _flux_fallback_still(): mirror it (no reference_images param there; strip on any
     reference-mode channel, since the fallback fires after the primary path failed).

Idempotent (sentinel PATCH_NOPEOPLE_DEFAULT), anchor-verified, backup .pre_nopeople,
py_compiles before writing. Relaunch renders after pulling (running batch holds the
old module). No storyboard rebuild needed -- this changes prompt assembly at render
time, so re-rendering the affected text beats picks it up.

    python3 patch_nopeople_default.py --file shared/recreation_pipeline.py
"""
from __future__ import annotations
import argparse, py_compile, shutil, sys, tempfile
from pathlib import Path

SENTINEL = "PATCH_NOPEOPLE_DEFAULT"
EDITS = [['generate_still no-people default', '    from look_resolver import resolve_look\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"\n    negative = ", ".join(rb["negative"])\n    # Per-channel image model: channel.json may set "image_model"', '    from look_resolver import resolve_look\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    # PATCH_NOPEOPLE_DEFAULT: on a reference-mode channel (QQrew), a beat that\n    # arrives here on the TEXT path (no reference_images) is a person-free beat\n    # BY DEFINITION -- Rule 1: a human in frame is a crew member (which would have\n    # carried a {token} -> a ref -> the /edit path) or does not exist. The\n    # people_directive ("...detailed faces where people are present...") was\n    # summoning cartoon humans onto person-free plates (predator eyes, a hand, an\n    # empty wide) whenever their wording missed the old phrase-guard ("no face",\n    # "no clear animal" didn\'t match "no people"). Invert the default: no ref +\n    # reference channel = strip the directive unconditionally.\n    if config.get("render_mode") == "reference" and not reference_images:\n        people = ""\n    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"\n    negative = ", ".join(rb["negative"])\n    # Per-channel image model: channel.json may set "image_model"'], ['flux fallback no-people default', '    rb = load_rulebook()\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people\n                   else f"{style_suffix}. {image_prompt}")', '    rb = load_rulebook()\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    # PATCH_NOPEOPLE_DEFAULT: mirror generate_still. On a reference-mode channel the\n    # flux fallback should not inject anonymous people either.\n    if config.get("render_mode") == "reference":\n        people = ""\n    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people\n                   else f"{style_suffix}. {image_prompt}")']]

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
    shutil.copy2(t, b)
    t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name}, {len(EDITS)} edits)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
