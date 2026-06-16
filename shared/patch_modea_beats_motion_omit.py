#!/usr/bin/env python3
"""
patch_modea_beats_motion_omit.py - stop modea_beats.py stamping a placeholder
motion on every normal beat, so the channel's default_motion can fire.

WHY
  patch_default_motion.py (a prior session) already fixed the CONSUMER:
  cmd_stills in recreation_pipeline.py resolves the channel's default_motion
  and falls through with `b.get("motion_prompt") or _default_motion`. It also
  fixed the Mission Control typed-motion-box fallback. But the PRODUCER,
  modea_beats.py translate(), still writes DEFAULT_MOTION (the slow string)
  onto every non-face-hold beat. So by the time beats reach cmd_stills, the
  motion_prompt is already truthy, the `or` short-circuits, and the channel
  default never gets a turn. Result: every Sacred Dawn project shipped slow
  unless hand-hot-fixed per project (the-watchers/the-daughters shipped slow;
  enoch1/book-of-giants hot-fixed to dramatic). This fixes the third and
  first-in-chain layer the prior patch left untouched.

WHAT THIS DOES (one file, shared/modea_beats.py)
  translate():
    - face-hold beats keep FACEHOLD_MOTION (a real, intentional override that
      must still win over the channel default).
    - normal beats get NO motion_prompt key at all (omit it), instead of the
      slow DEFAULT_MOTION placeholder. cmd_stills then resolves them to the
      channel's default_motion (dramatic for Sacred Dawn).
  main() summary prints:
    - the two `s["motion_prompt"]` reads (face label + fh sanity list) become
      `s.get("motion_prompt")` so a now-absent key doesn't KeyError.

  Default-only: an authored face_hold still wins; the channel default is the
  floor; CHANNEL_DEFAULTS["default_motion"] remains the global floor for a
  channel that sets none. DEFAULT_MOTION stays defined (now unused by translate,
  left as documentation of the historical Final-Hours register).

DISCIPLINE
  Idempotent (sentinel: `motion omitted when not face-hold`). Anchors verified
  x1 on the original source before any write; backs up to .pre_motionomit;
  re-compiles; rolls back on failure. Run from the repo root on the LAPTOP,
  then commit/push, then `git pull --no-edit` + verify on the box.
  (No service restart needed - modea_beats.py is run per-job by modea_leg.py,
  not the always-on Mission Control server.)
"""
import sys
import shutil
import py_compile
from pathlib import Path

MB = Path("shared/modea_beats.py")
SENTINEL = "motion omitted when not face-hold"

# ── translate(): the producer fix ───────────────────────────────────────────
TRANSLATE_OLD = '''        narration = (b.get("narration") or "").strip()
        motion = FACEHOLD_MOTION if b.get("face_hold") else DEFAULT_MOTION
        shot_beats.append({
            "narration": narration,
            "image_prompt": visual,
            "motion_prompt": motion,
        })
        index_map[engine_idx] = b["index"]'''

TRANSLATE_NEW = '''        narration = (b.get("narration") or "").strip()
        # motion omitted when not face-hold: leave normal beats with NO
        # motion_prompt so cmd_stills falls through to the channel's
        # default_motion (channel.json). Only a real override (face-hold) is
        # written here; the channel owns the default register otherwise.
        shot = {
            "narration": narration,
            "image_prompt": visual,
        }
        if b.get("face_hold"):
            shot["motion_prompt"] = FACEHOLD_MOTION
        shot_beats.append(shot)
        index_map[engine_idx] = b["index"]'''

# ── main() summary print: face label read ────────────────────────────────────
FACE_OLD = '''        face = "  [face-hold motion]" if s["motion_prompt"] == FACEHOLD_MOTION else ""'''
FACE_NEW = '''        face = "  [face-hold motion]" if s.get("motion_prompt") == FACEHOLD_MOTION else ""'''

# ── main() summary print: fh sanity list read ────────────────────────────────
FH_OLD = '''    fh = [index_map[i] for i,s in enumerate(beat_script['beats'],1) if s['motion_prompt']==FACEHOLD_MOTION]'''
FH_NEW = '''    fh = [index_map[i] for i,s in enumerate(beat_script['beats'],1) if s.get('motion_prompt')==FACEHOLD_MOTION]'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not MB.exists():
        die(f"{MB} not found - run this from the repo root on the laptop.")

    src = MB.read_text()

    if SENTINEL in src:
        print("Already applied (sentinel present) - no changes made.")
        return

    edits = [
        ("translate producer", TRANSLATE_OLD, TRANSLATE_NEW),
        ("main face label", FACE_OLD, FACE_NEW),
        ("main fh sanity", FH_OLD, FH_NEW),
    ]

    # Verify every anchor exactly once on the ORIGINAL source before writing.
    for label, old, _ in edits:
        c = src.count(old)
        if c != 1:
            die(f"{label} anchor found {c}x (expected 1) - nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    if SENTINEL not in new:
        die("sentinel not present after edits - aborting (anchor mismatch).")

    bak = MB.with_suffix(MB.suffix + ".pre_motionomit")
    shutil.copy2(MB, bak)
    MB.write_text(new)

    try:
        py_compile.compile(str(MB), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(bak, MB)
        die(f"{MB} does not compile - restored from backup.\n{e}")

    print("OK patched:")
    print(f"   {MB}   (backup: {bak.name})")
    print("translate() now omits motion_prompt on normal beats; face-hold beats keep FACEHOLD_MOTION.")
    print("cmd_stills resolves omitted-motion beats to the channel default_motion.")
    print()
    print("VERIFY after pull on the box (re-translate the-watchers and grep):")
    print("   git pull --no-edit && grep -n 'motion omitted when not face-hold' shared/modea_beats.py")


if __name__ == "__main__":
    main()
