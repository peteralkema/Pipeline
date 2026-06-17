#!/usr/bin/env python3
"""
patch_amix_normalize.py — stop the music bed from ducking under the voice.

THE BUG (found 17 June, chicxulub had intermittent music dips):
  The mux filter uses `amix=inputs=2:duration=first:dropout_transition=0` with no
  `normalize` option. ffmpeg's amix DEFAULTS to normalize=1, which dynamically
  scales the whole mix against its inputs to avoid clipping — so the music gets
  pumped DOWN whenever the voice is loud and rises in the pauses. Reads as
  intermittent music, dips tied to the narration rather than the music itself.

THE FIX:
  Add `normalize=0` so amix just SUMS the two pre-scaled streams at their fixed
  levels (voice volume=VOICE_LEVEL, music volume=MUSIC_LEVEL). The music then holds
  a constant level the whole way through; the voice still dominates because it is
  the louder pre-scaled stream. No level re-tuning needed — VOICE_LEVEL 1.15 and
  MUSIC_LEVEL 0.07 already sum cleanly with the voice on top.

Sentinel: 'amix=inputs=2:normalize=0'. Backs up to .pre_amixnorm. Idempotent. ASCII.

Run on LAPTOP:  python3 shared/patch_amix_normalize.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "assemble_episode.py"
SENTINEL = "amix=inputs=2:normalize=0"

OLD = "[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]"
NEW = "[v][m]amix=inputs=2:normalize=0:duration=first:dropout_transition=0[a]"


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return
    if text.count(OLD) != 1:
        sys.exit(f"FAIL: amix anchor found {text.count(OLD)} times (expected 1) -- "
                 "paste the amix line and I'll re-cut.")
    new = text.replace(OLD, NEW, 1)
    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change -- aborting.")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_amixnorm")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n 'amix=inputs=2:normalize=0' shared/assemble_episode.py")


if __name__ == "__main__":
    main()
