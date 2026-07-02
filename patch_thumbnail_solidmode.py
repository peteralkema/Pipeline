#!/usr/bin/env python3
"""
patch_thumbnail_solidmode.py -- add the `solid_color_character` composition mode
to make_thumbnail.py (the B-variant: character cutout on a flat colour + subject
shadow + the existing text block).

The pose-picker generates a character render already on a solid colour (via
make_character_ref.py). This mode takes that PNG, rembg-cuts the character, drops
it right-of-frame on a clean flat fill of the SAME palette colour with a soft
drop-shadow behind the cutout (the ICE-AGE 'lift'), then hands off to the existing
_draw_block text renderer. Reuses _segment_foreground, _fit_text, _anchor_x, _draw_block.

Two edits:
  1. DEFAULTS: add solid_color_character-relevant keys (bg_color default, subject
     shadow params) so a channel with no overrides still renders sanely.
  2. make_thumbnail(): add the mode branch BEFORE the centered_subject Layer-4 block.
     When cfg['composition']=='solid_color_character', build a flat-colour base +
     shadowed cutout instead of the darkened-still base, then let the shared text
     path run as normal.

Idempotent (PATCH_SOLIDMODE), anchor-verified, backup .pre_solidmode, py_compiles.
    python3 patch_thumbnail_solidmode.py --file shared/make_thumbnail.py
"""
from __future__ import annotations
import argparse, py_compile, shutil, sys, tempfile
from pathlib import Path

SENTINEL = "PATCH_SOLIDMODE"

# --- Edit 1: DEFAULTS additions (anchor on the shadow_color default line) ---
OLD_DEF = '''    "shadow_color":         [0, 0, 0, 220],'''
NEW_DEF = '''    "shadow_color":         [0, 0, 0, 220],
    # PATCH_SOLIDMODE: solid_color_character mode (B-variant thumbnails)
    "bg_color":             [237, 106, 34],   # flat fill when no per-render colour given
    "subject_shadow":       True,             # soft drop-shadow behind the cutout (ICE-AGE lift)
    "subject_shadow_offset":[18, 18],
    "subject_shadow_blur":  22,
    "subject_shadow_color": [0, 0, 0, 150],
    "subject_scale":        0.92,             # cutout height as frac of canvas height
    "subject_x_frac":       0.52,             # left edge of cutout as frac of width (pushes right)'''

# --- Edit 2: the mode branch in make_thumbnail(), anchored on the Layer-4 comment ---
OLD_BRANCH = '''    # Layer 4 — poke-through subject (centered_subject mode only)
    if cfg["composition"] == "centered_subject" and cfg.get("segment_foreground", True):'''
NEW_BRANCH = '''    # PATCH_SOLIDMODE: solid_color_character mode -- flat colour + shadowed cutout.
    # Rebuilds `bg` from scratch (ignores the darkened-still base above) so the
    # character render (already on a solid bg) becomes a clean cutout on a flat fill.
    if cfg["composition"] == "solid_color_character":
        _bgc = tuple(cfg.get("bg_color", [237, 106, 34]))[:3]
        flat = Image.new("RGB", (target_w, target_h), _bgc)
        cut = _segment_foreground(base)   # rembg RGBA of the character
        if cut is not None:
            # scale the cutout to subject_scale of canvas height, keep aspect
            sh = int(target_h * float(cfg.get("subject_scale", 0.92)))
            ratio = sh / cut.height
            sw = int(cut.width * ratio)
            cut = cut.resize((sw, sh), Image.LANCZOS)
            px = int(target_w * float(cfg.get("subject_x_frac", 0.52)))
            py = target_h - sh   # sit on the bottom edge
            flat = flat.convert("RGBA")
            if cfg.get("subject_shadow", True):
                sox, soy = cfg.get("subject_shadow_offset", [18, 18])
                scol = tuple(cfg.get("subject_shadow_color", [0, 0, 0, 150]))
                # shadow = the cutout's alpha, filled dark, blurred, offset
                shadow = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                sil = Image.new("RGBA", (sw, sh), scol)
                shadow.paste(sil, (px + sox, py + soy), cut)
                shadow = shadow.filter(ImageFilter.GaussianBlur(
                    radius=cfg.get("subject_shadow_blur", 22)))
                flat = Image.alpha_composite(flat, shadow)
            flat.alpha_composite(cut, (px, py))
            bg = flat.convert("RGB")
        else:
            bg = flat  # no rembg -> flat colour, headline still lands
        # the shared text block below renders as normal (uses the same cfg keys)

    # Layer 4 — poke-through subject (centered_subject mode only)
    if cfg["composition"] == "centered_subject" and cfg.get("segment_foreground", True):'''


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
    for label, old in (("DEFAULTS", OLD_DEF), ("make_thumbnail branch", OLD_BRANCH)):
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor {label!r} found {c}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src.replace(OLD_DEF, NEW_DEF, 1).replace(OLD_BRANCH, NEW_BRANCH, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: result does not compile:\\n{e}", file=sys.stderr); tmp.unlink(missing_ok=True); return 4
    tmp.unlink(missing_ok=True)
    b = t.with_suffix(t.suffix + ".pre_solidmode")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
