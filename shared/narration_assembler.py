#!/usr/bin/env python3
"""
narration_assembler.py - Piece 2, step 1 of Synthetic 4c (the free scaffolding).

Reads beats.json (from parse_script.py) and emits the two artifacts the audio
spine needs. Both are PURE, FREE, INSTANT transforms of beats.json - no network,
no cost. Run this (and prove timing) before spending a cent on stills or Kling.

  1. <narration-out>  - the FULL spoken script in beat order, one continuous
     text, ready to feed Inworld via recreation_pipeline.generate_voiceover.
     This is exactly what the narrator (Victor scratch, then Peter's human read)
     actually says, top to bottom.

  2. <storyboard-out> - a one-entry-per-beat scaffold JSON (all 62, A and B),
     each carrying its narration. This is the object the Whisper aligner consumes
     to write per-BEAT audio_duration back (SPEC Piece 2, option a: reuse the
     proven alignment code). Kept under a DISTINCT filename so it never collides
     with the engine's own 41-shot storyboard.json (the Mode-A-only one the
     recreation pipeline writes and its assemble reads).

WHY narration ONLY (deviating from the SPEC's literal wording):
    parse_script.flush_into() folds every buffered found-line INTO the beat's
    `narration` field AND also stores it in `found_line`. So for a QuoteCard,
    narration already contains the spoken line. The SPEC says "narration plus
    found_line"; taken literally that DOUBLES every QuoteCard line in the VO.
    We therefore use narration alone and VERIFY: every QuoteCard's spoken line
    must appear exactly once in the assembled text, and no beat may have a
    found_line that isn't already inside its narration. If either check fires,
    the parser's behaviour changed and this assumption must be revisited.

THE SILENT-BEAT TELL (surfaced here so it doesn't bite in Piece 3):
    Beats with empty narration carry no spoken words, so Whisper cannot time
    them - they won't appear in the transcript at all. Expected: beat 00 (the
    cold-open black frame, whose words live on beat 01's QuoteCard) and any
    held cards (ChapterCards, etc.). These need DEFAULT HOLD durations assigned
    in the alignment/assemble step, not measured. This script lists them so you
    know the count before you build the aligner.

Usage:
    python3 narration_assembler.py beats.json
    python3 narration_assembler.py beats.json \
        --narration-out ep1_narration.txt \
        --storyboard-out ep1_beats_storyboard.json
"""

import os
import sys
import json
import argparse

WPM = 135  # documentary pace; matches the proxy in dispatch.py / the engine


# --------------------------------------------------------------------------
# Load + normalise
# --------------------------------------------------------------------------

def load_beats(path):
    with open(path, encoding="utf-8") as f:
        beats = json.load(f)
    if not isinstance(beats, list):
        sys.exit(f"{path} is not a JSON list of beats (got {type(beats).__name__}). "
                 f"Did you run parse_script.py with --json?")
    beats = sorted(beats, key=lambda b: b["index"])
    got = [b["index"] for b in beats]
    expected = list(range(len(beats)))
    if got != expected:
        print(f"  !! WARNING: beat indices are not contiguous 0..{len(beats) - 1}")
        print(f"     got: {got}")
    return beats


def spoken_text(beat):
    """The spoken words for one beat. narration already includes any found-line
    (parse_script folds it in), so narration alone is the source of truth."""
    return (beat.get("narration") or "").strip()


# --------------------------------------------------------------------------
# Build the two artifacts
# --------------------------------------------------------------------------

def build_narration(beats):
    """Full spoken script, beat order, blank line between beats.

    Blank lines are human-readable (so the human-read true-up can see beat
    boundaries) and are plain whitespace to both Inworld's sentence chunker
    and Whisper, so they don't affect the spoken words or the alignment."""
    parts = [spoken_text(b) for b in beats if spoken_text(b)]
    return "\n\n".join(parts)


def build_storyboard(beats):
    """One entry per beat (A and B), in order, in the flat-list shape the
    existing _auto_align_with_whisper() accepts. The aligner writes
    audio_duration onto each entry; silent beats (no narration) get a default
    hold assigned in the alignment step instead."""
    out = []
    for b in beats:
        out.append({
            "index": b["index"],
            "mode": b["mode"],
            "component": b.get("component"),
            "narration": spoken_text(b),
            "found_line": (b.get("found_line") or "").strip(),
            "silence_after": bool(b.get("silence_after")),
        })
    return out


# --------------------------------------------------------------------------
# Verification (the whole point of running this before spending)
# --------------------------------------------------------------------------

def verify(beats, full_text):
    problems = 0

    # 1. found_line containment: every found_line must already be inside narration.
    for b in beats:
        fl = (b.get("found_line") or "").strip()
        if fl and fl not in spoken_text(b):
            print(f"  !! beat {b['index']:02d}: found_line NOT inside narration "
                  f"-> the fold assumption broke; this line would be LOST. \"{fl}\"")
            problems += 1

    # 2. duplication guard: each QuoteCard's spoken line appears exactly once.
    for b in beats:
        if b.get("component") == "QuoteCard":
            fl = (b.get("found_line") or "").strip()
            if fl:
                c = full_text.count(fl)
                if c != 1:
                    print(f"  !! QuoteCard beat {b['index']:02d}: spoken line appears "
                          f"{c}x in the VO text (expected exactly 1): \"{fl}\"")
                    problems += 1

    return problems


def categorise_empty(beats):
    """Split empty-narration beats into the legitimate categories vs genuine anomalies.

    All of these are untimable by Whisper (no words to transcribe) and need
    durations ASSIGNED in the alignment/assemble step rather than measured:
      - cold_open    : beat 00, the black frame whose words live on beat 01's card
      - held_cards   : Mode B graphics held over silence (ChapterCards, etc.)
      - silent_holds : Mode A recreated beats held in silence at decision-points
                       (the register's "generous silent beats"); they carry a
                       visual and almost always silence_after=True
      - other        : anything that fits none of the above -> investigate
    """
    cold_open, held_cards, silent_holds, other = [], [], [], []
    for b in beats:
        if spoken_text(b):
            continue
        if b["index"] == 0 and b["mode"] == "A":
            cold_open.append(b)
        elif b["mode"] == "B":
            held_cards.append(b)
        elif b["mode"] == "A" and (b.get("visual") or "").strip():
            silent_holds.append(b)
        else:
            other.append(b)
    return cold_open, held_cards, silent_holds, other


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--narration-out", default="ep1_narration.txt")
    ap.add_argument("--storyboard-out", default="ep1_beats_storyboard.json")
    args = ap.parse_args()

    beats = load_beats(args.beats_json)
    full_text = build_narration(beats)
    storyboard = build_storyboard(beats)

    n = len(beats)
    a = sum(1 for b in beats if b["mode"] == "A")
    bb = sum(1 for b in beats if b["mode"] == "B")
    words = len(full_text.split())
    est_sec = words / WPM * 60 if words else 0.0

    print(f"\n=== narration assembler: {args.beats_json} ===")
    print(f"{n} beats  |  A: {a}  B: {bb}")
    print(f"{words} spoken words  |  ~{est_sec / 60:.1f} min @ {WPM} wpm "
          f"(PROXY ONLY - real timing comes from Whisper next)\n")

    # Verification
    print("--- verification ---")
    problems = verify(beats, full_text)
    if problems == 0:
        print("  OK  found_line fold + QuoteCard-once checks pass.")

    # Silent beats (no words -> Whisper can't time them; durations get ASSIGNED)
    cold_open, held_cards, silent_holds, other = categorise_empty(beats)
    untimable = len(cold_open) + len(held_cards) + len(silent_holds) + len(other)
    print(f"\n--- silent beats: {untimable} of {n} carry no spoken words "
          f"(Whisper can't time these; durations get assigned, not measured) ---")
    if cold_open:
        print(f"  cold open (expected): beat(s) {[b['index'] for b in cold_open]}")
    if held_cards:
        comps = [f"{b['index']:02d}:{b.get('component')}" for b in held_cards]
        print(f"  held B cards ({len(held_cards)}): {comps}")
    if silent_holds:
        idxs = [b["index"] for b in silent_holds]
        print(f"  silent A holds ({len(silent_holds)}) -> decision-point pauses: {idxs}")
    if other:
        print(f"  !! UNEXPECTED empty beats (investigate): {[b['index'] for b in other]}")
    if untimable == 0:
        print("  (none - every beat has spoken words)")

    # Write artifacts
    with open(args.narration_out, "w", encoding="utf-8") as f:
        f.write(full_text + "\n")
    with open(args.storyboard_out, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)

    print(f"\nwrote {args.narration_out}  ({words} words, the VO script)")
    print(f"wrote {args.storyboard_out}  ({n} beats, the alignment scaffold)")

    # Show the head of the VO so the cold-open ordering is visible at a glance
    print("\n--- first lines of the VO (cold-open ordering check) ---")
    for line in full_text.splitlines()[:6]:
        if line.strip():
            print(f"  {line[:88]}{'...' if len(line) > 88 else ''}")

    if problems:
        print(f"\n!! {problems} verification problem(s) above - fix before generating VO.")
        sys.exit(1)


if __name__ == "__main__":
    main()
