#!/usr/bin/env python3
"""
patch_shot_grammar.py — Option A variety fix for build_storyboard.

Adds a shot-grammar block to the storyboard-generation prompt in
recreation_pipeline.py so consecutive shots vary in framing/angle/distance
instead of defaulting to the same eye-level medium shot (the eyam samey-stills
problem). Cooperates with face-never-resolved discipline: close framings prefer
hands/objects/backs, never resolved faces.

SAFE: edits only the prompt string inside build_storyboard. Idempotent — running
twice is a no-op (checks for the marker first). Backs up the file before editing.

Run on the box, from anywhere:
    cd ~/Pipeline
    python shared/patch_shot_grammar.py
    # then verify with the grep it prints
"""

import shutil
from pathlib import Path

PIPE = Path(__file__).resolve().parent / "recreation_pipeline.py"

SHOT_GRAMMAR = '''
SHOT GRAMMAR — VARY THE CAMERA (this is critical for visual interest):
Each shot must specify a deliberate framing. Draw from this vocabulary and
VARY IT AGGRESSIVELY across consecutive shots — never two adjacent shots with
the same distance-and-angle:
- ESTABLISHING / EXTREME WIDE: the subject tiny in a vast landscape; drone-height looking down over terrain
- WIDE: full scene, figure and surroundings together
- MEDIUM: a figure from the waist, or two elements in frame
- CLOSE DETAIL: hands at work, an object, turned earth, a tool, a texture — NOT a face
- EXTREME CLOSE-UP: a single object or texture filling the frame (grain of wood, weave of cloth, a single coin)
- LOW ANGLE: camera low, looking up (the sky, a ridge above, a doorway towering)
- HIGH ANGLE / DRONE: camera high, looking down (a lone figure on a slope, graves from above, a roof, a path)
- FROM BEHIND / OVER-THE-SHOULDER: looking where the subject looks (the channel's face-never-resolved default)

HARD RULES:
- When several consecutive shots occur in the same location, DELIBERATELY cycle the framing: establish wide, then cut to a close detail of hands or an object, then a low or high angle, then a from-behind medium. Treat repetition as a failure.
- Never produce two adjacent shots that would look like the same photograph. Vary camera height, distance, and angle as much as the scene allows.
- For CLOSE and MEDIUM framings of people, frame on HANDS, OBJECTS, BACKS, and SILHOUETTES rather than faces. A close-up is an opportunity for a detail of hands at work or a meaningful object — NEVER a resolved face. This keeps variety and face-never-resolved discipline working together.
- Put the chosen framing explicitly at the START of each image_prompt (e.g. "High aerial drone view of...", "Extreme close-up of hands gripping...", "Low angle looking up at...").

'''

def main():
    src = PIPE.read_text()

    if "SHOT GRAMMAR — VARY THE CAMERA" in src:
        print("Already patched (marker present). No change.")
        return

    # Anchor: insert the shot-grammar block right before the "CRITICAL RULES
    # learned from past production" line in the storyboard prompt, so it sits
    # alongside the existing motion rules.
    anchor = "CRITICAL RULES learned from past production"
    if anchor not in src:
        print("ERROR: anchor text not found — build_storyboard prompt may have changed.")
        print("       Aborting WITHOUT editing. Inspect recreation_pipeline.py manually.")
        return

    backup = PIPE.with_suffix(".py.pre_shotgrammar")
    shutil.copy2(PIPE, backup)
    print(f"Backed up -> {backup.name}")

    # The block goes into the f-string prompt. The anchor line is inside the
    # f-string already, so plain text (no f-string braces) is safe to inject.
    patched = src.replace(anchor, SHOT_GRAMMAR.strip() + "\n\n" + anchor, 1)
    PIPE.write_text(patched)

    ok = "SHOT GRAMMAR — VARY THE CAMERA" in PIPE.read_text()
    print(f"Patched: {ok}")
    print("\nVerify with:")
    print('  grep -c "SHOT GRAMMAR — VARY THE CAMERA" ~/Pipeline/shared/recreation_pipeline.py')
    print("  (expect 1)")
    print("\nIf anything looks wrong, restore with:")
    print(f"  cp {backup} {PIPE}")


if __name__ == "__main__":
    main()
