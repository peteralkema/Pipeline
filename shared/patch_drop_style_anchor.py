#!/usr/bin/env python3
"""Drop the reference_style_anchor fallback for crew-absent beats.

Crew-absent beats have no character to hold consistent, so they should render
via text-to-image + style_suffix (like every other channel's wides), NOT via
the NB2 /edit endpoint conditioned on a people-free "style plate". The plate
caused setting-leak and hard 422 no_media_generated refusals (e.g. an ocean
wide conditioned on a palace-wall photo). This removes the fallback only;
crew-present character beats are unaffected.

Idempotent: verifies the exact anchor block exists once, backs up the target,
parses the patched source before writing, and no-ops if already patched.
"""
import ast
import shutil
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "recreation_pipeline.py"

ANCHOR = (
    "                if not _refs and _ref_anchor:\n"
    "                    _refs.append(str(_ref_chdir / _ref_anchor))\n"
)
REPLACEMENT = (
    "                # crew-absent beats intentionally get NO reference: they\n"
    "                # render via text-to-image + style_suffix, not the /edit path\n"
)


def main() -> int:
    src = TARGET.read_text()

    if ANCHOR not in src:
        if REPLACEMENT.strip() in src:
            print("Already patched (anchor fallback already removed). No-op.")
            return 0
        print("ERROR: anchor block not found and not already patched. Aborting.")
        print("Expected to find:\n" + ANCHOR)
        return 1

    if src.count(ANCHOR) != 1:
        print(f"ERROR: expected exactly 1 anchor match, found {src.count(ANCHOR)}. Aborting.")
        return 1

    new_src = src.replace(ANCHOR, REPLACEMENT)

    # Verify it still parses before touching anything on disk.
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        print(f"ERROR: patched source fails to parse: {e}. Aborting, no changes made.")
        return 1

    backup = TARGET.with_suffix(".py.bak_style_anchor")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new_src)
    print(f"OK patched {TARGET.name} (backup: {backup.name})")
    print("Crew-absent beats now route to text-to-image; anchor fallback removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
