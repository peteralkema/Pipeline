#!/usr/bin/env python3
"""
align_with_whisper.py — Frame-accurate per-shot audio alignment.

Reads:
  - projects/<project>/voiceover.json    (Whisper output with word timestamps)
  - projects/<project>/storyboard.json   (shot list with narration text)

Writes audio_start and audio_duration back into each shot in storyboard.json
based on real measured timestamps from the rendered voiceover audio.

Usage (from channel root, e.g. final-hours/):
    python ../shared/align_with_whisper.py --project mary_celeste

  OR point it at named files directly (used by the Synthetic dual-mode spine,
  whose 62-beat scaffold is deliberately NOT called storyboard.json so it can't
  collide with the engine's own 41-shot storyboard.json):
    python ../shared/align_with_whisper.py \
        --storyboard ep1_beats_storyboard.json \
        --whisper projects/ep1-the-promise/voiceover.json

The pipeline's assemble() step then reads audio_duration from storyboard.json
and uses it instead of the word-count proxy that caused drift on Mary Celeste.

Banked as the permanent fix for sync drift. Capability serves Lazarus Films
dialogue-driven scripts as well — same mechanism, different application.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def normalize(s: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace — for word matching."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def words_in(text: str) -> list:
    """Return a list of normalized word tokens from text."""
    return [w for w in normalize(text).split() if w]


def main():
    parser = argparse.ArgumentParser(description="Align storyboard shots to Whisper-measured audio timestamps.")
    parser.add_argument("--project", required=False, default=None, help="Project name (looks in projects/<name>/)")
    parser.add_argument("--storyboard", default=None,
                        help="explicit path to the shot/beat list JSON (overrides --project; pass with --whisper)")
    parser.add_argument("--whisper", default=None,
                        help="explicit path to the Whisper voiceover.json (overrides --project; pass with --storyboard)")
    parser.add_argument("--verbose", action="store_true", help="Print per-shot timing details")
    args = parser.parse_args()

    # Path resolution: explicit file overrides take precedence; otherwise the
    # original --project-based resolution runs UNCHANGED (Final Hours path).
    if args.storyboard or args.whisper:
        if not (args.storyboard and args.whisper):
            print("ERROR: pass BOTH --storyboard and --whisper, or use --project instead", file=sys.stderr)
            sys.exit(1)
        storyboard_path = Path(args.storyboard)
        whisper_path = Path(args.whisper)
    else:
        if not args.project:
            print("ERROR: --project is required (or pass --storyboard and --whisper)", file=sys.stderr)
            sys.exit(1)
        project_arg = Path(args.project)
        if not project_arg.is_absolute() and len(project_arg.parts) == 1 and Path("projects").is_dir():
            project_dir = Path("projects") / project_arg
        else:
            project_dir = project_arg
        whisper_path = project_dir / "voiceover.json"
        storyboard_path = project_dir / "storyboard.json"

    if not whisper_path.exists():
        print(f"ERROR: Whisper output not found at {whisper_path}", file=sys.stderr)
        print(f"Run Whisper first:", file=sys.stderr)
        print(f"  whisper {whisper_path.parent}/voiceover.mp3 --model small --output_format json \\", file=sys.stderr)
        print(f"    --output_dir {whisper_path.parent}/ --word_timestamps True", file=sys.stderr)
        sys.exit(1)

    if not storyboard_path.exists():
        print(f"ERROR: storyboard not found at {storyboard_path}", file=sys.stderr)
        sys.exit(1)

    # Load Whisper output and flatten to a single word list
    whisper_data = json.load(open(whisper_path))
    all_words = []
    for seg in whisper_data.get("segments", []):
        if "words" in seg and seg["words"]:
            for w in seg["words"]:
                token = normalize(w.get("word", ""))
                if not token:
                    continue
                # A whisper "word" may contain multiple tokens after normalization
                for t in token.split():
                    all_words.append({"word": t, "start": w["start"], "end": w["end"]})
        else:
            # Fallback: distribute segment time evenly across words
            tokens = words_in(seg.get("text", ""))
            if not tokens:
                continue
            dur = seg["end"] - seg["start"]
            per = dur / len(tokens)
            for i, t in enumerate(tokens):
                all_words.append({"word": t, "start": seg["start"] + i * per, "end": seg["start"] + (i + 1) * per})

    print(f"Whisper detected {len(all_words)} words across {len(whisper_data.get('segments', []))} segments")

    # Load storyboard
    storyboard = json.load(open(storyboard_path))
    if isinstance(storyboard, list):
        shots = storyboard
        storyboard_key = None
    else:
        if "beats" in storyboard:
            storyboard_key = "beats"
        elif "shots" in storyboard:
            storyboard_key = "shots"
        else:
            print(f"ERROR: storyboard has no 'beats' or 'shots' key", file=sys.stderr)
            sys.exit(1)
        shots = storyboard[storyboard_key]

    # Build a flat list of (shot_idx, narration_word_index_in_shot) for every word in narration
    storyboard_words = []
    for shot_idx, shot in enumerate(shots):
        narration = shot.get("narration", "")
        for word in words_in(narration):
            storyboard_words.append((shot_idx, word))

    print(f"Storyboard contains {len(storyboard_words)} narration words across {len(shots)} shots")

    if len(storyboard_words) == 0:
        print("ERROR: no narration words found in storyboard", file=sys.stderr)
        sys.exit(1)

    # Sanity check
    diff = len(all_words) - len(storyboard_words)
    if abs(diff) > len(storyboard_words) * 0.05:
        print(f"WARNING: Whisper word count ({len(all_words)}) differs from storyboard word count ({len(storyboard_words)}) by {diff}", flush=True)
        print(f"This may indicate transcription errors. Alignment may drift slightly.", flush=True)

    # For each shot, find its starting word index in the full storyboard word list
    # then look up that index in the Whisper word list to get the actual audio time
    shot_start_indices = {}
    cursor = 0
    for shot_idx, shot in enumerate(shots):
        shot_start_indices[shot_idx] = cursor
        n_narration_words = len(words_in(shot.get("narration", "")))
        cursor += n_narration_words

    # Now look up the audio start time for each shot
    for shot_idx, shot in enumerate(shots):
        start_word_index = shot_start_indices[shot_idx]

        # Clamp to bounds
        if start_word_index >= len(all_words):
            shot["audio_start"] = all_words[-1]["end"] if all_words else 0.0
        else:
            shot["audio_start"] = all_words[start_word_index]["start"]

    # Compute audio_duration for each shot from consecutive starts
    last_audio_end = all_words[-1]["end"] if all_words else 0.0
    for i, shot in enumerate(shots):
        if i + 1 < len(shots):
            shot["audio_duration"] = shots[i + 1]["audio_start"] - shot["audio_start"]
        else:
            shot["audio_duration"] = last_audio_end - shot["audio_start"]

        # Floor to a reasonable minimum (avoid zero-duration shots)
        if shot["audio_duration"] < 0.3:
            shot["audio_duration"] = 0.3

    # Save updated storyboard
    if storyboard_key is None:
        with open(storyboard_path, "w") as f:
            json.dump(shots, f, indent=2, ensure_ascii=False)
    else:
        storyboard[storyboard_key] = shots
        with open(storyboard_path, "w") as f:
            json.dump(storyboard, f, indent=2, ensure_ascii=False)

    # Summary
    total = sum(s["audio_duration"] for s in shots)
    durations = [s["audio_duration"] for s in shots]
    print(f"\nAlignment complete:")
    print(f"  Total measured audio time:  {total:.1f}s ({total/60:.2f} min)")
    print(f"  Whisper audio length:       {last_audio_end:.1f}s")
    print(f"  Shortest shot:              {min(durations):.2f}s")
    print(f"  Longest shot:               {max(durations):.2f}s")
    print(f"  Mean shot:                  {total/len(shots):.2f}s")

    if args.verbose:
        print(f"\nPer-shot timing (first 10 + last 5):")
        for i in list(range(min(10, len(shots)))) + list(range(max(10, len(shots)-5), len(shots))):
            s = shots[i]
            narration_preview = s.get("narration", "")[:60]
            print(f"  Shot {i+1:3d}: start={s['audio_start']:7.2f}s  dur={s['audio_duration']:5.2f}s  | {narration_preview!r}")

    print(f"\nNow patch the pipeline assemble() to use audio_duration when present, then run --assemble-only")


if __name__ == "__main__":
    main()
