#!/usr/bin/env python3
"""
audio_qc.py — audio continuity quality check for the AUDIO GATE.

Scans the Whisper segments in voiceover.json for silence gaps larger than a
threshold. A large mid-read gap almost always means a failed/empty Inworld TTS
chunk got concatenated as dead air (the "44-second hole" failure mode) — Whisper
finds speech on either side but nothing in the gap.

Design:
  - READ ONLY. Never mutates anything.
  - FAILS SOFT. If the JSON is missing/malformed, returns a "couldn't check"
    result rather than raising — a quality check must never break the pipeline.
  - Returns (ok: bool, message: str). ok=True means "no problem found OR couldn't
    check"; the message carries the detail. The caller decides how loud to be.

A detected gap is NOT a swap situation — swap replaces audio with a human read.
A hole means a failed render: abort and re-run the audio leg. The message says so.
"""

import json
from pathlib import Path

DEFAULT_THRESHOLD_S = 3.0


def _fmt_ts(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    return f"{m}:{s:02d}"


def audio_continuity_check(voiceover_json_path, threshold=DEFAULT_THRESHOLD_S):
    """Return (ok, message).

    ok=False ONLY when a real gap over `threshold` is found. Missing/unreadable
    JSON returns ok=True with a 'could not run' note (fail soft — don't block the
    gate on the checker's own failure).
    """
    p = Path(voiceover_json_path)
    if not p.exists():
        return True, f"continuity check skipped — {p.name} not found (could not run)."

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return True, f"continuity check skipped — could not read {p.name} ({e})."

    segs = data.get("segments", data) if isinstance(data, dict) else data
    if not isinstance(segs, list) or len(segs) < 2:
        return True, "continuity check skipped — not enough segments to analyze."

    # find the largest gap between the end of one segment and the start of the next
    worst_gap = 0.0
    worst_at = 0.0
    gaps = []
    try:
        for i in range(len(segs) - 1):
            end_i = float(segs[i]["end"])
            start_next = float(segs[i + 1]["start"])
            gap = start_next - end_i
            if gap > threshold:
                gaps.append((end_i, gap))
            if gap > worst_gap:
                worst_gap = gap
                worst_at = end_i
    except (KeyError, TypeError, ValueError):
        return True, "continuity check skipped — segment format unexpected."

    if not gaps:
        return True, f"continuity check: clean — no silence gaps over {threshold:.0f}s."

    # at least one real gap — this is the failure we care about
    total_flagged = len(gaps)
    msg = (
        f"AUDIO GAP DETECTED — {worst_gap:.0f}s of silence at {_fmt_ts(worst_at)} "
        f"({total_flagged} gap{'s' if total_flagged > 1 else ''} over {threshold:.0f}s). "
        f"This almost always means a failed TTS chunk shipped as dead air. "
        f"SWAP will NOT fix it — abort (Ctrl-C) and re-run the audio leg instead."
    )
    return False, msg


if __name__ == "__main__":
    import sys
    ok, message = audio_continuity_check(sys.argv[1] if len(sys.argv) > 1 else "voiceover.json")
    print(("OK: " if ok else "FAIL: ") + message)
    sys.exit(0 if ok else 1)
