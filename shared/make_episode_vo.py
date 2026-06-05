#!/usr/bin/env python3
"""
make_episode_vo.py - Synthetic 4c, Piece 2 step 2: the audio spine's voice.

Takes the assembled narration (ep1_narration.txt from narration_assembler.py) and
produces the ONE continuous whole-episode voiceover - all 62 beats' spoken words,
top to bottom, in Synthetic's Victor scratch voice. This is the source of truth the
whole timeline hangs off; the human-read true-up later just swaps this file and
re-aligns, regenerating nothing visual.

It reuses the engine's proven generate_voiceover (sentence-boundary chunking under
Inworld's 1800-char limit + concat), so there's no second TTS implementation to keep
honest. Run it from INSIDE the synthetic/ channel folder so load_channel_config walks
up to synthetic/channel.json and picks Victor (not Final Hours' Ashley/default).

With --whisper it then runs Whisper using the IDENTICAL invocation the engine's
_auto_align_with_whisper uses (model=small, word timestamps, JSON), writing
voiceover.json next to the mp3 - exactly where the aligner will look, so when the
per-beat aligner gets wired in the next rung, Whisper won't have to re-run.

This is still cheap: Inworld TTS for ~1800 words is a few cents; Whisper is free
(local), ~3-5 min on an M-series, longer on the box CPU. No fal, no Kling.

Usage (from inside synthetic/, in ~/venvs/pipeline):
    python3 ../shared/make_episode_vo.py
    python3 ../shared/make_episode_vo.py --whisper
    python3 ../shared/make_episode_vo.py --narration ep1_narration.txt \
        --out projects/ep1-the-promise/voiceover.mp3 --whisper --force
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

WPM = 135  # documentary proxy, only used to compare against the REAL measured length


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def run_whisper(voice_path: Path, model: str) -> Path:
    """Mirror the engine's _auto_align_with_whisper invocation exactly, so the
    voiceover.json produced here is byte-compatible with what the aligner expects."""
    if not shutil.which("whisper"):
        print("   whisper not installed; skipping. (pip install openai-whisper --break-system-packages)")
        return None
    out_json = voice_path.parent / (voice_path.stem + ".json")
    if out_json.exists():
        print(f"   whisper: {out_json.name} already exists, leaving it (delete to re-measure)")
        return out_json
    print(f"   whisper: measuring {voice_path.name} with model='{model}' (this takes a few minutes)...")
    try:
        subprocess.run(
            ["whisper", str(voice_path),
             "--model", model,
             "--output_format", "json",
             "--output_dir", str(voice_path.parent),
             "--word_timestamps", "True",
             "--verbose", "False"],
            check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        tail = (e.stderr or "")[-300:]
        sys.exit(f"   whisper failed:\n{tail}")
    if not out_json.exists():
        sys.exit(f"   whisper ran but {out_json} was not written — check the output dir.")
    return out_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--narration", default="ep1_narration.txt",
                    help="the assembled VO text (from narration_assembler.py)")
    ap.add_argument("--out", default="projects/ep1-the-promise/voiceover.mp3",
                    help="where to write the episode mp3 (default: the project folder)")
    ap.add_argument("--whisper", action="store_true",
                    help="after generating the VO, run Whisper to write voiceover.json (raw word timestamps)")
    ap.add_argument("--whisper-model", default="small")
    ap.add_argument("--force", action="store_true", help="regenerate the VO even if the mp3 exists")
    args = ap.parse_args()

    narr_path = Path(args.narration)
    if not narr_path.exists():
        sys.exit(f"narration not found: {narr_path}\n"
                 f"Run narration_assembler.py first, from this same folder.")
    text = narr_path.read_text(encoding="utf-8").strip()
    words = len(text.split())
    proxy_min = words / WPM

    # Import the engine's VO path. Running this as `python3 ../shared/make_episode_vo.py`
    # puts shared/ on sys.path[0], so this import resolves to shared/recreation_pipeline.py.
    try:
        import recreation_pipeline as rp
    except Exception as e:
        sys.exit(f"could not import recreation_pipeline ({e}).\n"
                 f"Run this from inside the synthetic/ channel folder, inside ~/venvs/pipeline "
                 f"(bare python3 lacks the deps).")

    # Verify channel + voice before spending a single TTS credit (playbook discipline).
    cfg = rp.load_channel_config(strict=True)
    voice_id = cfg.get("voice_id")
    print(f"\n=== episode VO ===")
    print(f"channel   : {cfg.get('name')}  (marker: {cfg.get('_marker_path')})")
    print(f"voice_id  : {voice_id}")
    if voice_id != "Victor":
        print(f"  !! expected Victor for Synthetic — you're standing in the wrong channel folder?")
        print(f"     (cd into synthetic/ and re-run; not generating against the wrong voice.)")
        sys.exit(1)
    if not rp.INWORLD_API_KEY:
        sys.exit("  !! INWORLD_API_KEY not set — check the .env symlink in this channel folder.")
    print(f"narration : {narr_path}  ({words} words, ~{proxy_min:.1f} min proxy)")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not args.force:
        print(f"\nVO already exists: {out_path}  (use --force to regenerate)")
    else:
        print(f"\nGenerating VO -> {out_path} ...")
        rp.generate_voiceover(text, out_path)

    dur = probe_duration(out_path)
    print(f"\nmeasured VO length: {dur:.1f}s = {dur / 60:.1f} min")
    if dur:
        delta = (dur / 60) - proxy_min
        print(f"  vs {WPM}-wpm proxy {proxy_min:.1f} min  ->  {delta:+.1f} min "
              f"({'Victor reads slower' if delta > 0 else 'Victor reads faster'} than the proxy)")
        print(f"  NOTE: this whole-episode length is REAL; per-beat durations still need Whisper.")

    if args.whisper:
        print()
        wj = run_whisper(out_path, args.whisper_model)
        if wj:
            print(f"   whisper: wrote {wj}  (raw word timestamps — the aligner consumes this next)")

    print(f"\nnext rung: wire the per-beat aligner against ep1_beats_storyboard.json")
    print(f"           (needs align_with_whisper.py to map these timestamps onto all 62 beats)")


if __name__ == "__main__":
    main()
