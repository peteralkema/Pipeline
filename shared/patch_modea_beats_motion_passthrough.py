#!/usr/bin/env python3
"""
patch_modea_beats_motion_passthrough.py  (idempotent)

Teach modea_beats.translate() to carry an AUTHORED per-beat motion (beat.motion,
produced by parse_script.py's MOTION: line) through to the shot's motion_prompt.

Precedence (decided):
    1. authored beat.motion   -> use it verbatim   (the TIGHTEN/HOLD/SWING overrides)
    2. else face_hold         -> FACEHOLD_MOTION    (existing behaviour, unchanged)
    3. else (nothing)         -> omit motion_prompt -> cmd_stills falls through to
                                 channel.json default_motion (CREEP) — existing
                                 inheritance, unchanged.

This is the consumer half of the motion wiring. The producer half
(patch_parse_script_motion.py) must be applied first so beats carry `motion`.

Run from repo root:  python shared/patch_modea_beats_motion_passthrough.py
Re-running is a no-op.
"""

import io
import os
import sys
import py_compile

TARGET = os.path.join(os.path.dirname(__file__), "modea_beats.py")
SENTINEL = "authored_motion"

# Anchor: the exact shot-build + face_hold block inside translate().
ANCHOR = (
    '        shot = {\n'
    '            "narration": narration,\n'
    '            "image_prompt": visual,\n'
    '        }\n'
    '        if b.get("face_hold"):\n'
    '            shot["motion_prompt"] = FACEHOLD_MOTION\n'
    '        shot_beats.append(shot)'
)

REPLACE = (
    '        shot = {\n'
    '            "narration": narration,\n'
    '            "image_prompt": visual,\n'
    '        }\n'
    '        # Precedence: authored MOTION: line > face-hold default > blank (inherit\n'
    '        # channel default_motion). An authored motion is a deliberate per-beat\n'
    '        # override (TIGHTEN/HOLD/SWING); only when absent do we fall back to the\n'
    '        # face-hold default or leave it blank for the channel default to win.\n'
    '        authored_motion = (b.get("motion") or "").strip()\n'
    '        if authored_motion:\n'
    '            shot["motion_prompt"] = authored_motion\n'
    '        elif b.get("face_hold"):\n'
    '            shot["motion_prompt"] = FACEHOLD_MOTION\n'
    '        shot_beats.append(shot)'
)


def main():
    if not os.path.exists(TARGET):
        sys.exit(f"ERROR: {TARGET} not found - run from the repo root.")

    with io.open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if SENTINEL in src:
        print("Already patched (authored_motion present) - no-op.")
        return

    n = src.count(ANCHOR)
    if n != 1:
        sys.exit(
            f"ERROR: anchor found {n} times (expected 1). Refusing to patch - "
            "modea_beats.py is not the expected version."
        )

    backup = TARGET + ".pre_motion_passthrough"
    if not os.path.exists(backup):
        with io.open(backup, "w", encoding="utf-8") as f:
            f.write(src)
        print(f"Backed up -> {backup}")

    new = src.replace(ANCHOR, REPLACE, 1)

    with io.open(TARGET, "w", encoding="utf-8") as f:
        f.write(new)

    try:
        py_compile.compile(TARGET, doraise=True)
    except py_compile.PyCompileError as e:
        with io.open(TARGET, "w", encoding="utf-8") as f:
            f.write(src)
        sys.exit(f"ERROR: patched file failed to compile, reverted.\n{e}")

    print("OK: modea_beats.translate() now passes authored beat.motion -> motion_prompt.")
    print("    Precedence: authored > face-hold > channel default. py_compile passed.")


if __name__ == "__main__":
    main()
