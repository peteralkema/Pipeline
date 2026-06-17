#!/usr/bin/env python3
"""
patch_inworld_speaking_rate.py — add per-channel voice speed to the Inworld TTS call.

WHY (17 June): Victor read a touch rushed on Prehistoric Disasters' slow deep-time
register. Inworld's REST API supports `speakingRate` inside audioConfig (range
0.5-1.5, default 1.0; confirmed working at 0.9 via a standalone curl test on the
box). The pipeline payload had NO speed key at all, so every channel ran at 1.0.

WHAT: read a `speaking_rate` float from the resolved channel config and pass it as
`speakingRate` inside the audioConfig dict. Absent key => 1.0 => byte-identical to
today's behaviour, so Final Hours / Sacred Dawn / Synthetic are unchanged. Only a
channel that sets `speaking_rate` in its channel.json changes pace.

The payload currently reads (around line 680):
    payload = {
        "text": ...,
        "voiceId": voice_id,
        "modelId": INWORLD_MODEL,
        "audioConfig": {"audioEncoding": "MP3"},
    }
`config` (the resolved channel dict) is in scope here (voice_id = config["voice_id"]
just above), so config.get("speaking_rate", 1.0) is the per-channel value.

Sentinel: 'speakingRate'. Backs up to .pre_speakingrate. Idempotent. ASCII.

Run on LAPTOP:  python3 shared/patch_inworld_speaking_rate.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "recreation_pipeline.py"
SENTINEL = "speakingRate"

OLD = '        "audioConfig": {"audioEncoding": "MP3"},'
NEW = ('        "audioConfig": {"audioEncoding": "MP3",\n'
       '                        "speakingRate": float(config.get("speaking_rate", 1.0))},')


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return
    if text.count(OLD) != 1:
        sys.exit(f"FAIL: audioConfig anchor found {text.count(OLD)} times (expected 1) -- "
                 "paste the payload block (around line 680) and I'll re-cut.")
    new = text.replace(OLD, NEW, 1)
    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change -- aborting.")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_speakingrate")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n 'speakingRate' shared/recreation_pipeline.py")
    print("    Then set Prehistoric to 0.9:")
    print("      python -c \"import json; p='prehistoric-disasters/channel.json'; "
          "d=json.load(open(p)); d['speaking_rate']=0.9; "
          "json.dump(d,open(p,'w'),indent=2,ensure_ascii=False); print('speaking_rate=0.9')\"")


if __name__ == "__main__":
    main()
