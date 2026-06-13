#!/usr/bin/env python3
"""
patch_kenburns_15x.py — push the Ken Burns zoom to ~1.5x.

WHY
  1.3x still reads short for Peter; wants ~1.5x. Raise the cap 1.30 -> 1.50 and the
  per-frame increment 0.0016 -> 0.0024 so a normal beat clearly reaches the cap.
  At 24fps over 9s (216 frames): 0.0024*216 ≈ 0.52 of zoom, so it hits 1.50 with
  margin. Even a short ~5s beat (120 frames) gains ~0.29 -> ~1.29x, a strong push.
  Producer logic, paths, duration math unchanged.

DISCIPLINE
  Idempotent (sentinel: the new zoom expression). Single anchor verified once;
  backs up to .pre_kb15; re-compiles + rolls back on failure. Run from the repo root
  on the LAPTOP, then commit/push, then pull on the box. (No service restart.)
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")

OLD = "        f\"zoompan=z='min(zoom+0.0016,1.30)':d={total_frames}:\""
NEW = "        f\"zoompan=z='min(zoom+0.0024,1.50)':d={total_frames}:\""

MARKER = "zoom+0.0024,1.50"


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    n = src.count(OLD)
    if n == 0:
        die("zoompan anchor NOT FOUND — confirm the 1.3x speed patch is applied; nothing written.")
    if n > 1:
        die(f"zoompan anchor found {n}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(OLD, NEW)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_kb15")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    if MARKER not in check:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   zoom: increment 0.0016 -> 0.0024, cap 1.30 -> 1.50")
    print("Re-test on the box after pull:")
    print("   python shared/recreation_pipeline.py kenburns \\")
    print("     --still sacred-dawn/projects/figures-test-2/modea/stills/shot_001.png \\")
    print("     --out  sacred-dawn/projects/figures-test-2/modea/clips/kbtest.mp4 --duration 9")


if __name__ == "__main__":
    main()
