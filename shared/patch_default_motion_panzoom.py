#!/usr/bin/env python3
"""
patch_default_motion_panzoom.py — update Sacred Dawn's default_motion string.

WHY
  Peter refined the dramatic default: "zoom in" -> "pan and zoom in".

WHAT THIS DOES (one file: sacred-dawn/channel.json)
  Sets default_motion to the new string. Idempotent: no-op if already set to it.
  (Only the channel.json data file — no code, no service restart needed; the engine
  and the once-off button read default_motion fresh at runtime.)

DISCIPLINE
  Backs up to .pre_panzoom; revalidates JSON; rolls back on failure. Run from the
  repo root on the LAPTOP, then commit/push, then pull on the box.
"""
import sys
import json
import shutil
from pathlib import Path

CJ = Path("sacred-dawn/channel.json")
NEW = ("dramatic motion, maximise elements of movement and interplay on scene, "
       "dramatic lighting effects. pan and zoom in")


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not CJ.exists():
        die(f"{CJ} not found — run this from the repo root on the laptop.")
    try:
        cfg = json.loads(CJ.read_text())
    except Exception as e:
        die(f"{CJ} did not parse as JSON: {e}")

    if cfg.get("default_motion") == NEW:
        print("Already set to the pan-and-zoom string — no changes made.")
        return

    bak = CJ.with_suffix(CJ.suffix + ".pre_panzoom")
    shutil.copy2(CJ, bak)
    cfg["default_motion"] = NEW
    CJ.write_text(json.dumps(cfg, indent=2) + "\n")

    try:
        check = json.loads(CJ.read_text())
        assert check.get("default_motion") == NEW
    except Exception as e:
        shutil.copy2(bak, CJ)
        die(f"verification failed — restored from backup ({e}).")

    print(f"OK updated {CJ}")
    print(f"   backup: {bak.name}")
    print(f"   default_motion = {NEW}")


if __name__ == "__main__":
    main()
