#!/usr/bin/env python3
"""
patch_elevenlabs_min_duration.py — let the concat guard know how long an utterance
is *supposed* to be.

THE BUG
-------
generate_voiceover_elevenlabs() ends with:

    total_dur = _ffprobe_duration(out_path)
    if total_dur <= 1.0:
        raise ElevenLabsTTSError(f"Concatenated voiceover is ... hard fail.")

That guard is CORRECT for what it was written for: a full-episode narration. If a whole
episode's read comes back under a second, the API silently returned garbage and dead air
must never ship (reliability doctrine, banked 23 June).

But a wordless-spine channel renders ONE LINE AT A TIME. "Beautiful." is 0.91s of
perfectly good audio, and the guard hard-fails on it. The assumption ("this is always a
whole episode") is invisible in the signature, so it collides with a legitimate new use.

THE FIX
-------
Parameterize the floor. `generate_voiceover_elevenlabs(..., min_total_duration=1.0)`
keeps today's behaviour byte-for-byte for every existing caller; the per-line renderer
passes a smaller floor because a single spoken line legitimately runs under a second.

The guard keeps doing its real job — catching dead air and API garbage — it simply stops
assuming it is always looking at a full episode.

NOT TOUCHED: _validate_chunk's per-chunk `dur <= 0.2` dead-air check. A real utterance
always clears 0.2s; that guard is correct at every scale and stays exactly as it is.

Discipline: verifies its anchors, py_compiles the result before writing, keeps a .pre_*
backup, idempotent.

Run on the BOX from ~/Pipeline (after git pull):
    python shared/patch_elevenlabs_min_duration.py --dry-run
    python shared/patch_elevenlabs_min_duration.py
"""

from __future__ import annotations

import argparse
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TARGET = Path("shared/elevenlabs_tts.py")
MARKER = "min_total_duration"

# ── 1. signature: add the parameter, defaulted to today's value ───────────
ANCHOR_SIG = 'def generate_voiceover_elevenlabs(text: str, out_path, channel_config: dict) -> str:'
NEW_SIG = ('def generate_voiceover_elevenlabs(text: str, out_path, channel_config: dict,\n'
           '                                  min_total_duration: float = 1.0) -> str:')

# ── 2. the guard: use the parameter instead of the hardcoded 1.0 ──────────
ANCHOR_GUARD = '''    total_dur = _ffprobe_duration(out_path)
    if total_dur <= 1.0:
        raise ElevenLabsTTSError(
            f"Concatenated voiceover is {total_dur:.2f}s — something is wrong, hard fail."
        )'''

NEW_GUARD = '''    total_dur = _ffprobe_duration(out_path)
    # Dead air never ships. The FLOOR is caller-supplied because it depends on what is
    # being rendered: a full-episode narration under 1s means the API returned garbage;
    # a single VO line ("Beautiful.") is legitimately shorter than that. Default 1.0
    # preserves the original behaviour for every narration caller.
    if total_dur <= min_total_duration:
        raise ElevenLabsTTSError(
            f"Concatenated voiceover is {total_dur:.2f}s "
            f"(floor {min_total_duration:.2f}s) — something is wrong, hard fail."
        )'''


def fail(msg: str) -> int:
    print(f"!! {msg}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--target", default=str(TARGET))
    args = ap.parse_args()

    target = Path(args.target)
    if not target.is_file():
        return fail(f"{target} not found. Run from ~/Pipeline (repo root).")

    src = target.read_text(encoding="utf-8")

    if MARKER in src:
        print(f"OK  already applied (marker present in {target}); nothing to do.")
        return 0

    problems = []
    if ANCHOR_SIG not in src:
        problems.append("generate_voiceover_elevenlabs signature anchor not found")
    if ANCHOR_GUARD not in src:
        problems.append("concat-duration guard anchor not found (the `total_dur <= 1.0` block)")
    if problems:
        for p in problems:
            print(f"!! {p}", file=sys.stderr)
        return fail("anchors did not verify — elevenlabs_tts.py has moved. "
                    "Re-read it and update this patch. Nothing was written.")
    print("anchors verified: signature, concat guard")

    out = src.replace(ANCHOR_SIG, NEW_SIG, 1)
    out = out.replace(ANCHOR_GUARD, NEW_GUARD, 1)

    if out == src:
        return fail("no change produced — refusing to write.")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out)
        tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        tmp.unlink(missing_ok=True)
        return fail(f"patched source does not compile; nothing written.\n{e}")
    tmp.unlink(missing_ok=True)
    print("py_compile OK on the patched source")

    if args.dry_run:
        print("\n--dry-run: anchors verified, result compiles, nothing written.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f".pre_min_duration_{stamp}_{target.name}")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")

    print(f"backup -> {backup}")
    print(f"PATCHED -> {target}")
    print("\nVERIFY:")
    print("  grep -n 'min_total_duration' shared/elevenlabs_tts.py")
    print("\nExisting narration callers pass no floor and keep the 1.0s guard exactly. "
          "Only the per-line VO renderer lowers it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
