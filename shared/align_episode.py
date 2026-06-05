#!/usr/bin/env python3
"""
align_episode.py - Synthetic 4c, Piece 2 step 3: the complete per-beat timing table.

Closes the audio spine. Runs the proven align_with_whisper against the 62-beat
scaffold to MEASURE the spoken beats from real Whisper timestamps, then ASSIGNS
deliberate holds to the silent beats (which Whisper cannot time - there are no
words to transcribe). Output: ep1_beats_timed.json, the single timing table both
the dispatcher (rendering Mode B clips) and the dual-mode assemble consume. That
is principle 3 made real: one measurement, two consumers.

THE THING THE SPEC GLOSSED - read this before tuning:
    The VO contains NO silence for the silent beats. We fed Inworld only the
    spoken words, so Victor reads beat 19 then immediately beat 21 - there is no
    audio gap where beat 20's hold lives. Therefore:
      * the finished episode is LONGER than the voiceover, by the total of all
        assigned holds;
      * Piece 3 must INSERT silence into the audio at each silent beat's position
        (its audio_start, which the aligner already gives us), NOT just trim the
        VO to length. "Mux VO over the concatenated video" is not enough.
    This script reports the runtime split (spoken vs inserted) so the real episode
    length is visible now, before any fal/Kling spend.

Hold policy is DIRECTOR'S CHOICE - the constants below are a sane first pass.
Tune them by eye after watching, then re-run (free, instant). The mechanism is
fixed; the numbers are yours.

Prereqs (from inside synthetic/, in ~/venvs/pipeline):
    python3 ../shared/narration_assembler.py /tmp/ep1_beats.json   # -> scaffold
    python3 ../shared/make_episode_vo.py --whisper                 # -> voiceover.json

Then:
    python3 ../shared/align_episode.py
    python3 ../shared/align_episode.py \
        --scaffold ep1_beats_storyboard.json \
        --whisper projects/ep1-the-promise/voiceover.json \
        --out ep1_beats_timed.json
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# ── Hold policy (TUNE BY EYE) ────────────────────────────────────────────────
# Deliberate on-screen durations for beats with no spoken words. These are the
# pauses the script is asking for; the VO doesn't contain them, so they get
# inserted into the timeline (and the audio gets matching silence in Piece 3).
HOLD_COLD_OPEN = 2.0   # beat 00, the black frame before "We have a verdict."
HOLD_CARD      = 2.5   # any held Mode B graphic (ChapterCard, Headline, Counter, ...)
HOLD_SILENT_A  = 3.0   # Mode A decision-point pause (empty chair, closing door)
SILENCE_AFTER_BONUS = 1.5  # extra inserted silence for any beat flagged silence_after


def categorise(beat):
    """Return (category, base_hold) for a silent beat."""
    idx, mode = beat["index"], beat["mode"]
    if idx == 0 and mode == "A":
        return "cold_open", HOLD_COLD_OPEN
    if mode == "B":
        return "card", HOLD_CARD
    if mode == "A":
        return "silent_a", HOLD_SILENT_A
    return "other", HOLD_CARD


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scaffold", default="ep1_beats_storyboard.json",
                    help="the 62-beat scaffold from narration_assembler.py")
    ap.add_argument("--whisper", default="projects/ep1-the-promise/voiceover.json",
                    help="Whisper voiceover.json (from make_episode_vo.py --whisper)")
    ap.add_argument("--out", default="ep1_beats_timed.json",
                    help="the complete 62-beat timing table to write")
    ap.add_argument("--skip-align", action="store_true",
                    help="don't re-run the aligner; the scaffold already has audio_start/audio_duration")
    args = ap.parse_args()

    scaffold = Path(args.scaffold)
    whisper = Path(args.whisper)
    if not scaffold.exists():
        sys.exit(f"scaffold not found: {scaffold}  (run narration_assembler.py first)")
    if not whisper.exists():
        sys.exit(f"whisper json not found: {whisper}  (run make_episode_vo.py --whisper first)")

    # 1) MEASURE: run the proven aligner against our named scaffold (writes
    #    audio_start/audio_duration back into it in place).
    if not args.skip_align:
        aligner = Path(__file__).parent / "align_with_whisper.py"
        cmd = [sys.executable, str(aligner),
               "--storyboard", str(scaffold), "--whisper", str(whisper)]
        print(f"$ {' '.join(cmd)}\n")
        r = subprocess.run(cmd, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            sys.exit(f"\naligner failed (exit {r.returncode}) — see above")

    beats = json.load(open(scaffold, encoding="utf-8"))
    beats.sort(key=lambda b: b["index"])

    # 2) ASSIGN: override silent beats with deliberate holds; add silence_after
    #    bonus to ANY beat that carries it (spoken beats keep their measured time
    #    and gain only the inserted trailing pause).
    spoken_measured = 0.0     # real word time (Whisper), before any inserted silence
    inserted_silence = 0.0    # holds + silence_after bonuses (timeline the VO lacks)
    by_cat = {}

    for b in beats:
        spoken = bool((b.get("narration") or "").strip())
        measured = float(b.get("audio_duration", 0.0))
        if spoken:
            spoken_measured += measured
            b["hold_assigned"] = False
            b["hold_category"] = "spoken"
            dur = measured
            if b.get("silence_after"):
                dur += SILENCE_AFTER_BONUS
                inserted_silence += SILENCE_AFTER_BONUS
        else:
            cat, base = categorise(b)
            dur = base
            if b.get("silence_after"):
                dur += SILENCE_AFTER_BONUS
            inserted_silence += dur
            by_cat[cat] = by_cat.get(cat, 0) + 1
            b["hold_assigned"] = True
            b["hold_category"] = cat
        b["audio_duration"] = round(dur, 3)

    runtime = spoken_measured + inserted_silence

    # 3) WRITE the complete timing table.
    json.dump(beats, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    # ── Summary ──────────────────────────────────────────────────────────────
    n = len(beats)
    n_spoken = sum(1 for b in beats if not b["hold_assigned"])
    n_silent = n - n_spoken
    print("\n=== episode timing table ===")
    print(f"beats           : {n}  ({n_spoken} spoken, {n_silent} silent/assigned)")
    print(f"spoken word time: {spoken_measured:6.1f}s  ({spoken_measured/60:.2f} min)  [Whisper-measured]")
    print(f"inserted silence: {inserted_silence:6.1f}s  ({inserted_silence/60:.2f} min)  [holds + silence_after]")
    print(f"EPISODE RUNTIME : {runtime:6.1f}s  ({runtime/60:.2f} min)  <-- the real length")
    print(f"  (the VO itself is ~{spoken_measured:.0f}s; the episode is longer by the inserted silence)")

    print("\nassigned holds by category:")
    for cat in ("cold_open", "card", "silent_a", "other"):
        if by_cat.get(cat):
            print(f"  {cat:10s} x{by_cat[cat]}")

    print("\nsilent beats (index: category -> assigned hold):")
    for b in beats:
        if b["hold_assigned"]:
            sa = "  +silence_after" if b.get("silence_after") else ""
            comp = f" {b.get('component')}" if b.get("component") else ""
            print(f"  [{b['index']:02d}] {b['hold_category']:9s}{comp:16s} -> {b['audio_duration']:.1f}s{sa}")

    print(f"\nwrote {args.out}")
    print("\nNEXT: this table is the one source of truth for timing. Two consumers:")
    print("  - dispatch.py: render each Mode B clip at its beat's audio_duration (replaces estimate_frames)")
    print("  - the dual-mode assemble (Piece 3): trim/hold A clips, place B clips, and")
    print("    INSERT silence into the audio at each silent beat's audio_start.")


if __name__ == "__main__":
    main()
