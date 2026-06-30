#!/usr/bin/env python3
"""
patch_generate_still_anchor.py

FAULT (canonical 2B code-leak, made literal):
  generate_still() calls load_channel_config(strict=False) with NO anchor.
  _find_channel_marker(None) walks up from Path.cwd() (= ~/Pipeline), finds no
  channel.json, and silently returns CHANNEL_DEFAULTS -- which carry the Final
  Hours cinematic/photoreal style_suffix and an empty base_canon. Result: EVERY
  channel that renders through this path with cwd above the channel folder gets
  the Final Hours look and loses its own style_suffix + base_canon. This is what
  rendered QQrew's Skeptic as photoreal beauty-portraits.

FIX:
  generate_still() already receives out_path (the real project still path, e.g.
  qqrew/projects/pregnancy1/modea/stills/shot_001.png). Anchor channel
  resolution on it: load_channel_config(strict=True, anchor=out_path). The
  cache is keyed by resolved channel dir, so the first correctly-anchored call
  populates qqrew and every subsequent still hits the cache. strict=True turns a
  future resolution miss into a loud crash instead of a silent Final Hours
  render -- nothing that cannot identify its own channel should spend on stills.

IDEMPOTENT: sentinel check; re-runs are no-ops. Backs up to .pre_anchor.
ASCII-only. Verifies the anchor exists exactly once before writing.
"""
import sys, shutil, py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")
SENTINEL = "anchor=out_path"

ANCHOR = "    config = load_channel_config(strict=False)\n"
REPLACEMENT = "    config = load_channel_config(strict=True, anchor=out_path)\n"


def main():
    if not TARGET.exists():
        sys.exit("ERROR: run from repo root (shared/recreation_pipeline.py not found).")

    src = TARGET.read_text()

    if SENTINEL in src:
        print("Already patched (sentinel present). No-op.")
        return

    count = src.count(ANCHOR)
    if count == 0:
        sys.exit("ERROR: anchor line not found -- generate_still's config call may have changed. Aborting (no write).")
    if count != 1:
        sys.exit(f"ERROR: anchor line found {count} times, expected exactly 1. Aborting (no write).")

    backup = TARGET.with_suffix(".py.pre_anchor")
    shutil.copy2(TARGET, backup)
    print(f"Backup: {backup}")

    TARGET.write_text(src.replace(ANCHOR, REPLACEMENT, 1))

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        sys.exit(f"ERROR: py_compile failed, reverted from backup.\n{e}")

    print("Patched generate_still: load_channel_config(strict=True, anchor=out_path)")
    print("py_compile OK.")


if __name__ == "__main__":
    main()
