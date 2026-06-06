#!/usr/bin/env python3
"""
patch_animate_only.py — add the `--animate-only` seam to recreation_pipeline.py.

Same in-place, idempotent style as patch_assemble_ffmpeg.py / patch_channel_resolution.py.
Run from the repo root:  python shared/patch_animate_only.py

Two edits, both mirroring the existing --assemble-only flag:
  1. register --animate-only on the finish subparser (next to --assemble-only)
  2. in cmd_finish, return right after the animate loop when --animate-only is set,
     before narrate/score/assemble.

Idempotent: re-running is a no-op once patched. Verifies the result compiles.
Backs up the original to recreation_pipeline.py.pre_animate_only before writing.
"""
import sys, ast, shutil
from pathlib import Path

TARGET = Path(__file__).parent / "recreation_pipeline.py"

# ── Edit 1: the argparse flag ──────────────────────────────────────────────
ARG_ANCHOR = (
    '    c.add_argument("--assemble-only", action="store_true",\n'
    '                   help="re-stitch from existing clips/voice/music only (no rendering, no cost)")\n'
)
ARG_INSERT = (
    '    c.add_argument("--animate-only", action="store_true",\n'
    '                   help="animate stills to clips, then STOP (no narrate/score/assemble)")\n'
)

# ── Edit 2: the early return in cmd_finish ─────────────────────────────────
RET_ANCHOR = '    print("\\nNarrating script (Victor)...")\n'
RET_INSERT = (
    '    if getattr(args, "animate_only", False):\n'
    '        print(f"\\nAnimate-only: {len(clip_paths)} clips in {p[\'clips\']}, "\n'
    '              f"stopping before narrate/score/assemble (audio + assembly are separate legs).")\n'
    '        return\n\n'
)


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found. Run from the repo root: python shared/patch_animate_only.py")

    src = TARGET.read_text()

    already_flag = '"--animate-only"' in src
    already_ret = 'getattr(args, "animate_only"' in src
    if already_flag and already_ret:
        print("Already patched — --animate-only flag and cmd_finish early-return both present. No-op.")
        return

    # Edit 1
    if not already_flag:
        if ARG_ANCHOR not in src:
            sys.exit("FAIL: could not find the --assemble-only argparse block to anchor Edit 1. "
                     "The finish subparser may have changed — patch not applied.")
        src = src.replace(ARG_ANCHOR, ARG_INSERT + ARG_ANCHOR, 1)
        print("Edit 1 applied: registered --animate-only on the finish subparser.")
    else:
        print("Edit 1 skipped: --animate-only flag already present.")

    # Edit 2
    if not already_ret:
        if src.count(RET_ANCHOR) != 1:
            sys.exit(f"FAIL: expected exactly one 'Narrating script (Victor)' line to anchor Edit 2, "
                     f"found {src.count(RET_ANCHOR)}. Patch not applied.")
        src = src.replace(RET_ANCHOR, RET_INSERT + RET_ANCHOR, 1)
        print("Edit 2 applied: cmd_finish returns after animate when --animate-only is set.")
    else:
        print("Edit 2 skipped: early-return already present.")

    # Verify it still parses BEFORE writing anything.
    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"FAIL: patched source does not parse ({e}). Nothing written.")

    backup = TARGET.with_suffix(".py.pre_animate_only")
    if not backup.exists():
        shutil.copy2(TARGET, backup)
        print(f"Backed up original -> {backup.name}")
    TARGET.write_text(src)
    print(f"OK wrote {TARGET.name} (compiles).")
    print("Verify the flag parses:  python shared/recreation_pipeline.py finish --project _nope --animate-only")


if __name__ == "__main__":
    main()
