#!/usr/bin/env python3
"""
patch_parse_script_motion.py  (idempotent)

Teach parse_script.py to recognize a per-beat `MOTION:` line and store it on a
new Beat.motion field, exactly the way `VISUAL:` is handled. Without this, a
MOTION: line falls through the Mode-A block loop into the narration string and
gets READ ALOUD by the TTS (confirmed on the Tell-Tale Heart launch script:
beat 33 narration ended with "MOTION: TIGHTEN - an insistent push...").

This patch ONLY changes parse_script.py. It makes the authored motion available
as beat.motion in the JSON. The consumer side (modea_beats.translate reading
beat.motion and falling through to channel default_motion) is a SEPARATE patch.
Until that lands, motion still resolves to the channel default at storyboard
time, but narration is clean.

Run from repo root:  python shared/patch_parse_script_motion.py
Re-running is a no-op.
"""

import io
import os
import sys
import py_compile

TARGET = os.path.join(os.path.dirname(__file__), "parse_script.py")
SENTINEL = "MOTION_RE"

# --- the three edits, each (anchor, replacement, label) ---------------------

# 1) Add MOTION_RE next to VISUAL_RE.
ANCHOR_1 = (
    'VISUAL_RE    = re.compile(r"\\*?\\s*VISUAL:\\s*(.*?)\\*?\\s*$", re.IGNORECASE)'
)
REPLACE_1 = (
    'VISUAL_RE    = re.compile(r"\\*?\\s*VISUAL:\\s*(.*?)\\*?\\s*$", re.IGNORECASE)\n'
    'MOTION_RE    = re.compile(r"\\*?\\s*MOTION:\\s*(.*?)\\*?\\s*$", re.IGNORECASE)'
)

# 2) Add the motion field to the Beat dataclass (right after `visual`).
ANCHOR_2 = (
    '    visual: str = ""                            # A only: the VISUAL: direction'
)
REPLACE_2 = (
    '    visual: str = ""                            # A only: the VISUAL: direction\n'
    '    motion: str = ""                            # A only: the MOTION: direction (per-beat override; blank => channel default_motion)'
)

# 3) In the Mode-A block loop, catch MOTION: before the narration fallback.
#    The anchor is the exact VISUAL/else block; we insert a MOTION branch.
ANCHOR_3 = (
    "            for seg in block:\n"
    "                vm = VISUAL_RE.search(seg)\n"
    "                if vm and not beat.visual:\n"
    "                    beat.visual = _strip_md(vm.group(1))\n"
    '                    if "\\u2b50" in seg:\n'
    "                        beat.face_hold = True\n"
    "                else:\n"
    "                    clean = _strip_md(seg)\n"
    '                    if clean and not clean.upper().startswith("VISUAL:"):\n'
    "                        beat.narration = (beat.narration + \" \" + clean).strip()"
)
REPLACE_3 = (
    "            for seg in block:\n"
    "                vm = VISUAL_RE.search(seg)\n"
    "                mm = MOTION_RE.search(seg)\n"
    "                if vm and not beat.visual:\n"
    "                    beat.visual = _strip_md(vm.group(1))\n"
    '                    if "\\u2b50" in seg:\n'
    "                        beat.face_hold = True\n"
    "                elif mm and not beat.motion:\n"
    "                    beat.motion = _strip_md(mm.group(1))\n"
    "                else:\n"
    "                    clean = _strip_md(seg)\n"
    '                    if clean and not clean.upper().startswith("VISUAL:") \\\n'
    '                            and not clean.upper().startswith("MOTION:"):\n'
    "                        beat.narration = (beat.narration + \" \" + clean).strip()"
)

EDITS = [
    (ANCHOR_1, REPLACE_1, "MOTION_RE regex"),
    (ANCHOR_2, REPLACE_2, "Beat.motion field"),
    (ANCHOR_3, REPLACE_3, "Mode-A MOTION branch"),
]


def main():
    if not os.path.exists(TARGET):
        sys.exit(f"ERROR: {TARGET} not found - run from the repo root.")

    with io.open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if SENTINEL in src:
        print("Already patched (MOTION_RE present) - no-op.")
        return

    # verify every anchor exists exactly once BEFORE writing anything
    for anchor, _repl, label in EDITS:
        n = src.count(anchor)
        if n != 1:
            sys.exit(
                f"ERROR: anchor for '{label}' found {n} times (expected 1). "
                "Refusing to patch - parse_script.py is not the expected version."
            )

    backup = TARGET + ".pre_motion"
    if not os.path.exists(backup):
        with io.open(backup, "w", encoding="utf-8") as f:
            f.write(src)
        print(f"Backed up -> {backup}")

    new = src
    for anchor, repl, label in EDITS:
        new = new.replace(anchor, repl, 1)
        print(f"Applied: {label}")

    with io.open(TARGET, "w", encoding="utf-8") as f:
        f.write(new)

    # py_compile verification
    try:
        py_compile.compile(TARGET, doraise=True)
    except py_compile.PyCompileError as e:
        with io.open(backup, "r", encoding="utf-8") as f:
            f.write  # noqa
        with io.open(TARGET, "w", encoding="utf-8") as f:
            f.write(src)
        sys.exit(f"ERROR: patched file failed to compile, reverted.\n{e}")

    print("OK: parse_script.py now reads MOTION: into beat.motion. py_compile passed.")


if __name__ == "__main__":
    main()
