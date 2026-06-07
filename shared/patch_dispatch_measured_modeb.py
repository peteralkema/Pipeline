#!/usr/bin/env python3
"""
patch_dispatch_measured_modeb.py — make Mode B render at its beat's MEASURED spoken
duration, per the continuous-narration model. Run from repo root:
    python shared/patch_dispatch_measured_modeb.py

WHAT CHANGES:
  1. render_mode_b: a Mode B clip's duration = its beat's measured spoken duration
     (the `frames` passed in), exactly like Mode A — NOT the component's own fixed
     length. The component duration becomes a FAILSAFE CAP only: if a promoted phrase
     overflows the component's max frames (a script that ignored the eligibility
     filter), render at the cap and let the assembler freeze-tail the remainder, so
     Remotion is never asked for more frames than the component has. Avoid by design
     (script-stage word limit); failsafe if needed.
  2. estimate_frames: remove the `silence_after` +1.5s bonus — the continuous-narration
     model codifies nothing about silence.

Idempotent + self-verifying (ast-parse). Backs up to dispatch.py.pre_measured_modeb.
"""
import sys, ast, shutil
from pathlib import Path

TARGET = Path(__file__).parent / "dispatch.py"

# ── Edit 1: render_mode_b duration logic ───────────────────────────────────
RENDER_ANCHOR = '''    # FIRST PRINCIPLE: a Mode B element renders at ITS OWN declared length. The audio-
    # derived `frames` is IGNORED here — Remotion enforces the component's durationInFrames
    # and refuses anything longer, so we render exactly what the component declares. The
    # gap between this clip's length and the beat's measured audio slot is filled by the
    # ASSEMBLER (freeze-fill), not here. This makes Mode B render unbreakable: it can never
    # ask for more frames than the component has.
    comp_frames = component_durations().get(comp_id)
    if comp_frames is None:
        comp_frames = frames  # query unavailable (e.g. dry-run/no-node): fall back, render still attempts component length
        note_dur = f"{comp_frames} frames (audio-fallback; component duration unqueried)"
    else:
        note_dur = f"{comp_frames} frames (component's own duration)"
    frames = comp_frames
'''
RENDER_REPLACE = '''    # CONTINUOUS-NARRATION MODEL: a Mode B clip's duration = its beat's MEASURED spoken
    # duration (the `frames` passed in), exactly like Mode A. The script-stage eligibility
    # filter keeps a promoted phrase within the component's capacity, so this normally fits.
    # FAILSAFE ONLY (avoid by good script design): if a phrase overflows the component's max
    # frames, render at the component max and let the ASSEMBLER freeze-tail the remainder —
    # never ask Remotion for more frames than the component has (that would error mid-batch).
    target = frames                                  # measured spoken duration for this beat
    cap = component_durations().get(comp_id)
    if cap is not None and target > cap:
        print(f"     !! OVERFLOW: measured {target}f > component max {cap}f — rendering {cap}f; "
              f"assembler will freeze-tail {target - cap}f. SHORTEN this Mode B phrase in the script.")
        frames = cap
        note_dur = f"{cap} frames (component max — measured {target}f OVERFLOWED; failsafe)"
    else:
        frames = target
        note_dur = f"{target} frames (measured spoken duration)"
'''

# ── Edit 2: remove the silence_after bonus in estimate_frames ──────────────
SILENCE_ANCHOR = '''    if words:
        seconds = max(1.5, words / 135 * 60)
    else:
        seconds = 3.0 if beat["mode"] == "B" else 2.5
    if beat.get("silence_after"):
        seconds += 1.5
    return round(seconds * FPS)
'''
SILENCE_REPLACE = '''    if words:
        seconds = max(1.5, words / 135 * 60)
    else:
        seconds = 3.0 if beat["mode"] == "B" else 2.5
    # (no silence_after bonus — the continuous-narration model codifies nothing about silence)
    return round(seconds * FPS)
'''

EDITS = [
    ("measured spoken duration for this beat", RENDER_ANCHOR, RENDER_REPLACE, "render_mode_b measured duration"),
    ("no silence_after bonus", SILENCE_ANCHOR, SILENCE_REPLACE, "remove silence_after bonus"),
]


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found. Run from repo root: python shared/patch_dispatch_measured_modeb.py")
    src = TARGET.read_text()
    original = src
    applied = []
    for marker, anchor, replacement, label in EDITS:
        if marker in src:
            print(f"skip: {label} already present.")
            continue
        if anchor not in src:
            sys.exit(f"FAIL: anchor for '{label}' not found — dispatch.py changed. Nothing written.")
        if src.count(anchor) != 1:
            sys.exit(f"FAIL: anchor for '{label}' not unique ({src.count(anchor)}). Nothing written.")
        src = src.replace(anchor, replacement, 1)
        applied.append(label)

    if src == original:
        print("Already fully patched — no changes. No-op.")
        return

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"FAIL: patched source does not parse ({e}). Nothing written.")

    backup = TARGET.with_suffix(".py.pre_measured_modeb")
    if not backup.exists():
        shutil.copy2(TARGET, backup)
        print(f"Backed up original -> {backup.name}")
    TARGET.write_text(src)
    print(f"OK wrote {TARGET.name} (compiles). Applied: {', '.join(applied)}")


if __name__ == "__main__":
    main()
