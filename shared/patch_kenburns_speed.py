#!/usr/bin/env python3
"""
patch_kenburns_speed.py — tune the Ken Burns zoom faster (cap ~1.3x).

WHY
  The producer is smooth but too sleepy: over 9s it crept ~1.0->1.13x. Peter wants
  it to reach ~1.3x. This raises the per-frame zoom increment (0.0006 -> 0.0016) and
  the cap (1.25 -> 1.30). At 24fps over 9s (216 frames) that's ~0.0016*216 ≈ 0.35 of
  zoom, so it hits the 1.30 cap with room to spare — a clear, cinematic push-in.
  Producer logic, file paths, and duration math are otherwise unchanged.

DISCIPLINE
  Idempotent (sentinel: the new zoom expression). Single anchor verified once;
  backs up to .pre_kbspeed; re-compiles + rolls back on failure. Run from the repo
  root on the LAPTOP, then commit/push, then pull on the box. (No service restart.)
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")

OLD = "        f\"zoompan=z='min(zoom+0.0006,1.25)':d={total_frames}:\""
NEW = "        f\"zoompan=z='min(zoom+0.0016,1.30)':d={total_frames}:\""

MARKER = "zoom+0.0016,1.30"


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
        die("zoompan anchor NOT FOUND — confirm the kenburns producer patch is applied; nothing written.")
    if n > 1:
        die(f"zoompan anchor found {n}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(OLD, NEW)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_kbspeed")
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
    print("   zoom: increment 0.0006 -> 0.0016, cap 1.25 -> 1.30")
    print("Re-test on the box after pull:")
    print("   python shared/recreation_pipeline.py kenburns \\")
    print("     --still sacred-dawn/projects/figures-test-2/modea/stills/shot_001.png \\")
    print("     --out  sacred-dawn/projects/figures-test-2/modea/clips/kbtest.mp4 --duration 9")


if __name__ == "__main__":
    main()
