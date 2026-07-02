#!/usr/bin/env python3
"""
patch_thumbnail_composition_flag.py -- add a --composition CLI override to
make_thumbnail.py so a composition mode can be forced per-render, independent of
channel.json. Lets you test solid_color_character in isolation before the MC
pose-picker button depends on it (probe-before-spend), and is permanently useful
for one-off overrides.

Two edits (both in the argparse/main block near the bottom, ~line 474-502):
  1. add the --composition argument.
  2. after cfg is resolved, override cfg['composition'] if the flag was passed.

Anchored to the pasted live main() (ap.add_argument('--out'...) and the
`result = make_thumbnail(...)` call). Idempotent (PATCH_COMPFLAG), backup, compiles.
    python3 patch_thumbnail_composition_flag.py --file shared/make_thumbnail.py
"""
from __future__ import annotations
import argparse, py_compile, shutil, sys, tempfile
from pathlib import Path

SENTINEL = "PATCH_COMPFLAG"

# Edit 1: add the arg. Anchor on the --out argument line (unique, from pasted code).
OLD_ARG = '''    ap.add_argument("--out", default=None, help="output path (default: <project>/thumbnail.png)")'''
NEW_ARG = '''    ap.add_argument("--out", default=None, help="output path (default: <project>/thumbnail.png)")
    ap.add_argument("--composition", default=None,  # PATCH_COMPFLAG
                    help="override the channel's composition mode for this render "
                         "(e.g. solid_color_character). Omit to use channel.json.")
    ap.add_argument("--bg-color", default=None,  # PATCH_COMPFLAG
                    help="override bg_color as 'R,G,B' (solid_color_character mode).")'''

# Edit 2: apply the overrides after cfg is built, before make_thumbnail() is called.
# Anchor on the result = make_thumbnail(...) line (unique, from pasted code).
OLD_CALL = '''    out = Path(args.out) if args.out else project / "thumbnail.png"
    result = make_thumbnail(still, args.title, args.subtitle, out, cfg)'''
NEW_CALL = '''    out = Path(args.out) if args.out else project / "thumbnail.png"
    if args.composition:            # PATCH_COMPFLAG
        cfg["composition"] = args.composition
    if args.bg_color:               # PATCH_COMPFLAG
        try:
            cfg["bg_color"] = [int(x) for x in args.bg_color.split(",")][:3]
        except Exception:
            print(f"   (ignoring bad --bg-color {args.bg_color!r})")
    result = make_thumbnail(still, args.title, args.subtitle, out, cfg)'''


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
    for label, old in (("--out arg", OLD_ARG), ("make_thumbnail call", OLD_CALL)):
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor {label!r} found {c}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src.replace(OLD_ARG, NEW_ARG, 1).replace(OLD_CALL, NEW_CALL, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: result does not compile:\\n{e}", file=sys.stderr); tmp.unlink(missing_ok=True); return 4
    tmp.unlink(missing_ok=True)
    b = t.with_suffix(t.suffix + ".pre_compflag")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
