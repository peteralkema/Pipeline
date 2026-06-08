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

ALIGNMENT METHOD (the Troy-drift fix, 8 Jun 2026)
-------------------------------------------------
Earlier versions located each shot's start by COUNTING storyboard narration
words and indexing that running count straight into the Whisper word list. That
silently assumed the two token streams were 1:1 in length and order. They are
not: spelled-out numbers in the script ("eleven eighty-four") are transcribed by
Whisper as digits ("1184"), dropped fillers and merges add more divergence. Each
mismatch nudged the cursor permanently ahead of the Whisper stream, so audio_start
ran progressively further ahead of the spoken word (Troy: +9s by beat 32, +46s by
beat 141), and the tail beats collapsed to claw the total back. A ~3% token
divergence — under the old 5% warning — produced 46s of drift.

The fix aligns the storyboard token stream to the Whisper token stream with a
real sequence alignment (difflib, autojunk disabled), anchors each storyboard
word to its MATCHED Whisper word's timestamp, and interpolates across the
mismatch gaps. Errors stay local instead of accumulating. This is the original
"audio_start = Whisper start-time of the beat's first spoken word" intent, with
the word->word matching made robust rather than positional.
"""

import argparse
import difflib
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


def build_sb_time_map(sb_tokens, wh_tokens, wh_times, last_audio_end):
    """
    Map every storyboard token index -> an audio time (seconds).

    sb_tokens / wh_tokens : parallel normalized token lists.
    wh_times              : wh_times[j] is the start time of wh_tokens[j].
    Returns a list sb_time of len(sb_tokens), non-decreasing.

    Matched tokens take the exact Whisper start time. Unmatched storyboard
    tokens (e.g. number words Whisper rendered as digits) are linearly
    interpolated between their surrounding matched anchors, so a local
    transcription mismatch never propagates into later beats.
    """
    m = len(sb_tokens)
    if m == 0:
        return []

    # Collect anchors: (sb_index, time) for every element-wise 'equal' match.
    anchors = []
    sm = difflib.SequenceMatcher(None, sb_tokens, wh_tokens, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                anchors.append((i1 + k, wh_times[j1 + k]))

    sb_time = [0.0] * m

    if not anchors:
        # Degenerate: nothing matched. Spread the audio evenly so we still
        # produce a monotonic timeline rather than crashing.
        for i in range(m):
            sb_time[i] = last_audio_end * (i / m)
        return sb_time

    # Head: indices before the first anchor interpolate from 0.0 at index 0
    # up to the first anchor time.
    first_idx, first_t = anchors[0]
    for i in range(0, first_idx + 1):
        sb_time[i] = first_t * (i / first_idx) if first_idx > 0 else first_t

    # Interior: linear interpolation between consecutive anchors.
    for (i_a, t_a), (i_b, t_b) in zip(anchors, anchors[1:]):
        sb_time[i_a] = t_a
        span = i_b - i_a
        if span <= 0:
            continue
        for i in range(i_a + 1, i_b):
            frac = (i - i_a) / span
            sb_time[i] = t_a + (t_b - t_a) * frac
    last_idx, last_t = anchors[-1]
    sb_time[last_idx] = last_t

    # Tail: indices after the last anchor interpolate toward last_audio_end.
    tail_span = (m - 1) - last_idx
    for i in range(last_idx + 1, m):
        if tail_span > 0:
            frac = (i - last_idx) / tail_span
            sb_time[i] = last_t + (last_audio_end - last_t) * frac
        else:
            sb_time[i] = last_t

    # Enforce non-decreasing (interpolation already is, but guard against
    # any pathological anchor ordering from a noisy transcript).
    for i in range(1, m):
        if sb_time[i] < sb_time[i - 1]:
            sb_time[i] = sb_time[i - 1]

    return sb_time


def main():
    parser = argparse.ArgumentParser(description="Align storyboard shots to Whisper-measured audio timestamps.")
    parser.add_argument("--project", required=False, default=None, help="Project name (looks in projects/<name>/)")
    parser.add_argument("--storyboard", default=None,
                        help="explicit path to the shot/beat list JSON (overrides --project; pass with --whisper)")
    parser.add_argument("--whisper", default=None,
                        help="explicit path to the Whisper voiceover.json (overrides --project; pass with --storyboard)")
    parser.add_argument("--verbose", action="store_true", help="Print per-shot timing details")
    parser.add_argument("--min-duration", type=float, default=0.3,
                        help="Safety floor for a shot duration in seconds. With correct alignment this should "
                             "essentially never fire; if it does, Whisper likely dropped a whole beat's words.")
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

    # Flatten storyboard narration to a token stream, recording which shot each
    # token belongs to and the index of each shot's FIRST token in that stream.
    sb_tokens = []
    shot_first_token_idx = {}
    for shot_idx, shot in enumerate(shots):
        shot_first_token_idx[shot_idx] = len(sb_tokens)
        for word in words_in(shot.get("narration", "")):
            sb_tokens.append(word)

    print(f"Storyboard contains {len(sb_tokens)} narration words across {len(shots)} shots")

    if len(sb_tokens) == 0:
        print("ERROR: no narration words found in storyboard", file=sys.stderr)
        sys.exit(1)

    last_audio_end = all_words[-1]["end"] if all_words else 0.0
    wh_tokens = [w["word"] for w in all_words]
    wh_times = [w["start"] for w in all_words]

    # Sequence-align the two token streams and resolve a time for every
    # storyboard token. This replaces the old cursor-count indexing that let
    # number/transcription mismatches accumulate into multi-second drift.
    sb_time = build_sb_time_map(sb_tokens, wh_tokens, wh_times, last_audio_end)

    # Coverage = fraction of storyboard tokens that matched a Whisper token.
    # This is the real health metric (the old 5% length-diff check missed the
    # Troy drift entirely because the drift came from in-order substitutions,
    # not a length mismatch).
    sm = difflib.SequenceMatcher(None, sb_tokens, wh_tokens, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    coverage = matched / len(sb_tokens) if sb_tokens else 0.0

    # Assign each shot its start from the resolved time of its first token.
    for shot_idx, shot in enumerate(shots):
        idx = shot_first_token_idx[shot_idx]
        if idx >= len(sb_tokens):
            # Shot with no narration words sitting at the very end.
            shot["audio_start"] = last_audio_end
        else:
            shot["audio_start"] = round(sb_time[idx], 3)

    # The episode's audio is one continuous track from t=0; the first shot must
    # start at 0.0 regardless of any lead-in silence before the first word.
    if shots:
        shots[0]["audio_start"] = 0.0

    # Keep starts non-decreasing across shots (a shot with no narration inherits
    # the next spoken shot's start, which can equal its neighbour's).
    for i in range(1, len(shots)):
        if shots[i]["audio_start"] < shots[i - 1]["audio_start"]:
            shots[i]["audio_start"] = shots[i - 1]["audio_start"]

    # Compute audio_duration for each shot from consecutive starts.
    n_floored = 0
    for i, shot in enumerate(shots):
        if i + 1 < len(shots):
            shot["audio_duration"] = round(shots[i + 1]["audio_start"] - shot["audio_start"], 3)
        else:
            shot["audio_duration"] = round(last_audio_end - shot["audio_start"], 3)

        if shot["audio_duration"] < args.min_duration:
            shot["audio_duration"] = args.min_duration
            n_floored += 1

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
    print(f"  Word-match coverage:        {coverage*100:.1f}%  ({matched}/{len(sb_tokens)} storyboard words)")
    print(f"  Shortest shot:              {min(durations):.2f}s")
    print(f"  Longest shot:               {max(durations):.2f}s")
    print(f"  Mean shot:                  {total/len(shots):.2f}s")

    if coverage < 0.85:
        print(f"\n!! LOW COVERAGE ({coverage*100:.1f}%). Many storyboard words did not match the "
              f"transcript. Check that the Whisper voiceover.json is for THIS script, and that the "
              f"narration text matches what was spoken. Alignment may be approximate.")
    if n_floored:
        print(f"\n!! {n_floored} shot(s) hit the {args.min_duration}s duration floor. With correct alignment "
              f"this should not happen — it usually means Whisper dropped an entire beat's words, so two "
              f"beats resolved to nearly the same start. Inspect those beats.")

    if args.verbose:
        print(f"\nPer-shot timing (first 10 + last 5):")
        for i in list(range(min(10, len(shots)))) + list(range(max(10, len(shots) - 5), len(shots))):
            s = shots[i]
            narration_preview = s.get("narration", "")[:60]
            print(f"  Shot {i+1:3d}: start={s['audio_start']:8.2f}s  dur={s['audio_duration']:5.2f}s  | {narration_preview!r}")

    print(f"\nNow patch the pipeline assemble() to use audio_duration when present, then run --assemble-only")


if __name__ == "__main__":
    main()
