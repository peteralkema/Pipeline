#!/usr/bin/env python3
"""Add a --music-level CLI flag to assemble_episode.py, replacing the hardcoded
MUSIC_LEVEL constant as the default. Idempotent; anchor-verified; .pre backup.

Run from the repo root on the LAPTOP:
    python3 shared/patch_music_level_flag.py
Then: git add shared/assemble_episode.py shared/patch_music_level_flag.py
      git commit -m "assemble_episode: --music-level flag"
      git push
On the BOX: git pull --no-edit   (no need to re-run the patch; the patched
file arrives via git).

Usage after patching:
    assemble_episode.py ... --music-dir <dir> --music-level 0.065
Omit --music-level to keep the 0.040 default (unchanged for all other channels).
"""
import sys
import py_compile
import shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "assemble_episode.py"
SENTINEL = "# patched: --music-level flag"


def main():
    if not TARGET.exists():
        sys.exit(f"TARGET not found: {TARGET}. Run from the repo root "
                 f"(expected shared/assemble_episode.py beside this script).")

    src = TARGET.read_text()

    if SENTINEL in src:
        print("Already patched (sentinel present). No-op.")
        return

    # --- Anchor 1: argparse block. Insert the new arg after --music-crossfade. ---
    anchor_arg = ('ap.add_argument("--music-crossfade", type=float, default=2.0, '
                  'help="crossfade seconds between tracks (default 2)")')
    if anchor_arg not in src:
        sys.exit("ANCHOR 1 NOT FOUND (--music-crossfade add_argument). "
                 "Aborting, no changes written.")

    new_arg = (anchor_arg
               + '\n    ap.add_argument("--music-level", type=float, default=None, '
               + 'help="music bed gain (linear; default = MUSIC_LEVEL constant). '
               + 'Higher = louder under the voice.")  ' + SENTINEL)
    src = src.replace(anchor_arg, new_arg, 1)

    # --- Anchor 2: after args = ap.parse_args(), bind the effective level. ---
    anchor_parse = "args = ap.parse_args()"
    if anchor_parse not in src:
        sys.exit("ANCHOR 2 NOT FOUND (args = ap.parse_args()). Aborting.")

    inject = (anchor_parse
              + "\n    global MUSIC_LEVEL\n"
              + "    if args.music_level is not None:\n"
              + "        MUSIC_LEVEL = args.music_level\n"
              + "        print(f'  music-level override: MUSIC {MUSIC_LEVEL}')")
    src = src.replace(anchor_parse, inject, 1)

    # verify both edits applied before writing
    if SENTINEL not in src or "global MUSIC_LEVEL" not in src:
        sys.exit("POST-EDIT VERIFY FAILED. Aborting without write.")

    shutil.copy(TARGET, TARGET.with_suffix(".py.pre_music_level"))
    TARGET.write_text(src)
    py_compile.compile(str(TARGET), doraise=True)
    print(f"OK patched {TARGET.name}; backup at {TARGET.name}.pre_music_level")
    print("Use: --music-level 0.065 (or 0.08). Omit to keep the 0.040 default.")


if __name__ == "__main__":
    main()
