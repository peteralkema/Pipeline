#!/usr/bin/env python3
"""
patch_solidmode_positioning.py -- fix the solid_color_character cutout positioning.

BUG (02 Jul): subject_x_frac=0.52 is used as the LEFT edge of the cutout, so a
waist-up figure runs PAST the right frame edge -- only a trailing hand stays in
view (95% flat colour, hand bottom-right). Fix: anchor the cutout's RIGHT edge
inside a right margin, and sit it on the bottom, so the BODY lands in the right
third and stays on-canvas. Also widen subject to fill the right portion.

Replaces the px/py computation in the solid_color_character branch (added by
PATCH_SOLIDMODE) with right-edge anchoring.

Idempotent (PATCH_SOLIDMODE_POS), anchored to the PATCH_SOLIDMODE px/py lines,
backup .pre_solidpos, compiles.
    python3 patch_solidmode_positioning.py --file shared/make_thumbnail.py
"""
from __future__ import annotations
import argparse, py_compile, shutil, sys, tempfile
from pathlib import Path

SENTINEL = "PATCH_SOLIDMODE_POS"

OLD = '''            sh = int(target_h * float(cfg.get("subject_scale", 0.92)))
            ratio = sh / cut.height
            sw = int(cut.width * ratio)
            cut = cut.resize((sw, sh), Image.LANCZOS)
            px = int(target_w * float(cfg.get("subject_x_frac", 0.52)))
            py = target_h - sh   # sit on the bottom edge'''
NEW = '''            # PATCH_SOLIDMODE_POS: scale to subject_scale of height, then anchor the
            # cutout's RIGHT edge inside a right margin (so the BODY sits in the
            # right third and never runs off-canvas -- the old left-edge frac at
            # 0.52 pushed a waist-up figure off the right edge, leaving only a hand).
            sh = int(target_h * float(cfg.get("subject_scale", 1.02)))
            ratio = sh / cut.height
            sw = int(cut.width * ratio)
            cut = cut.resize((sw, sh), Image.LANCZOS)
            _rmargin = int(target_w * float(cfg.get("subject_right_margin_frac", 0.02)))
            px = target_w - sw - _rmargin       # right-edge anchored
            # if the cutout is very wide, don't let its left edge cross the mid-line
            # (keeps the left half clear for the headline)
            _min_px = int(target_w * float(cfg.get("subject_min_left_frac", 0.46)))
            if px < _min_px:
                px = _min_px
            py = target_h - sh                  # sit on the bottom edge'''

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="shared/make_thumbnail.py")
    a = ap.parse_args()
    t = Path(a.file)
    if not t.is_file():
        print(f"ERROR: not found: {t}", file=sys.stderr); return 2
    src = t.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {t}"); return 0
    c = src.count(OLD)
    if c != 1:
        print(f"ERROR: anchor found {c}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src.replace(OLD, NEW, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: does not compile:\\n{e}", file=sys.stderr); tmp.unlink(missing_ok=True); return 4
    tmp.unlink(missing_ok=True)
    b = t.with_suffix(t.suffix + ".pre_solidpos")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
