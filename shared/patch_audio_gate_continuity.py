#!/usr/bin/env python3
"""
patch_audio_gate_continuity.py — bake the gap-scan into the AUDIO GATE.

Idempotent. Inserts a continuity check into audio_gate() in shared/audio_leg.py,
printed right before the gate prompt, so a silent 44-second-hole can never again
slip past unnoticed. The check is read-only and fails soft.

PREREQUISITE: copy audio_qc.py into shared/ first.

Run:  python shared/patch_audio_gate_continuity.py
"""

import sys
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AL = REPO / "shared" / "audio_leg.py"

# Anchor: the line that opens the gate display. We insert the QC block before it.
ANCHOR = '    t.gate("AUDIO GATE")'

INSERT = '''    # --- audio continuity QC (read-only; fails soft) -------------------
    if not dry:
        try:
            from audio_qc import audio_continuity_check
            _ok, _msg = audio_continuity_check(artifacts["whisper"])
            if _ok:
                t.ok(_msg)
            else:
                # loud, unmissable — a detected hole means re-run audio, not swap
                t.gate("AUDIO CONTINUITY WARNING")
                print("  !! " + _msg)
        except Exception as _e:
            t.info(f"continuity check unavailable ({_e}) — proceeding without it.")
    # -------------------------------------------------------------------
'''


def main():
    if not AL.exists():
        print(f"ERROR: {AL} not found. Run from repo root.")
        sys.exit(1)

    src = AL.read_text(encoding="utf-8")

    if "audio_continuity_check" in src:
        print("  [skip] audio_leg.py: continuity check already present.")
        # still verify the helper is deployed
        if not (REPO / "shared" / "audio_qc.py").exists():
            print("  [WARN] shared/audio_qc.py not found — copy it into shared/.")
        return

    if ANCHOR not in src:
        print("  [FAIL] anchor not found in audio_leg.py:")
        print(f"         {ANCHOR!r}")
        print("         (gate display line may have changed — aborting, no write.)")
        sys.exit(2)

    if src.count(ANCHOR) != 1:
        print(f"  [FAIL] anchor found {src.count(ANCHOR)}x (expected 1). Aborting.")
        sys.exit(2)

    bak = AL.with_suffix(".py.pre_continuity_qc")
    shutil.copy2(AL, bak)
    AL.write_text(src.replace(ANCHOR, INSERT + ANCHOR, 1), encoding="utf-8")
    print(f"  [ok] audio_leg.py: continuity check inserted (backup -> {bak.name}).")

    if not (REPO / "shared" / "audio_qc.py").exists():
        print("  [WARN] shared/audio_qc.py not found — copy it into shared/ before running.")

    print()
    print("DONE. Verify:")
    print('  grep -n "audio_continuity_check" shared/audio_leg.py')
    print('  python shared/audio_qc.py you-had-to-be-there/projects/gaming-series/voiceover.json')


if __name__ == "__main__":
    main()
