#!/usr/bin/env python3
"""
patch_generate_still_style_first.py

PROBLEM: generate_still builds the flux prompt as
    f"{image_prompt}, {people}, {style_suffix}"
i.e. STYLE LAST. The stored image_prompt for QQrew is canon-first (a ~57-word
person description), so the cel-shaded style directive lands ~70+ tokens deep,
after flux has already been primed to render a realistic person. flux-pro
weights early tokens hardest, so busy/long beats drift 3D-glossy while only
short beats stay flat. The probe showed exactly this 1-to-6 style spread.

FIX: STYLE FIRST. Lead the prompt with style_suffix so the medium is locked
before the subject is described:
    f"{style_suffix}. {image_prompt}, {people}"
Channel-agnostic: every channel's own style_suffix simply leads its own prompts.
Final Hours leads with its cinematic suffix, QQrew with its flat-cel suffix --
each channel gets its medium pinned first. No per-channel branching.

IDEMPOTENT: sentinel on the new f-string. Backs up to .pre_stylefirst.
ASCII-only. Anchor must appear exactly once. py_compile-gated with auto-revert.
"""
import sys, shutil, py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")

OLD = (
    '    full_prompt = f"{image_prompt}, {people}, {style_suffix}" if people else f"{image_prompt}, {style_suffix}"\n'
)
NEW = (
    '    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"\n'
)
SENTINEL = 'f"{style_suffix}. {image_prompt}'


def main():
    if not TARGET.exists():
        sys.exit("ERROR: run from repo root (shared/recreation_pipeline.py not found).")

    src = TARGET.read_text()

    if SENTINEL in src:
        print("Already patched (style-first f-string present). No-op.")
        return

    c = src.count(OLD)
    if c == 0:
        sys.exit("ERROR: full_prompt assembly line not found / changed. Aborting (no write).")
    if c != 1:
        sys.exit(f"ERROR: full_prompt line found {c} times, expected 1. Aborting (no write).")

    backup = TARGET.with_suffix(".py.pre_stylefirst")
    shutil.copy2(TARGET, backup)
    print(f"Backup: {backup}")

    TARGET.write_text(src.replace(OLD, NEW, 1))

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        sys.exit(f"ERROR: py_compile failed, reverted from backup.\n{e}")

    print("Patched generate_still: prompt is now STYLE-FIRST.")
    print("py_compile OK.")


if __name__ == "__main__":
    main()
