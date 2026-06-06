#!/usr/bin/env python3
"""
match_beats.py - compute Mode B beat timings from Whisper word-timestamps.

Reads:
  - a Whisper JSON with word-level timestamps (the voiceover.json your
    true-up step already produces: {"segments":[{"words":[{"word","start","end"}]}]})
  - a beats spec: for each beat, the component, its props, and the phrase to emphasize

Writes:
  - beats.json: each beat with computed `from` (frame the beat's words begin)
    and `sweepStart` (frame, RELATIVE to the beat, where the emphasis phrase is spoken)

Matching is fuzzy + normalized to survive spoken-vs-written drift
("$13 billion" spoken as "thirteen billion dollars", lowercasing, punctuation).
Every match prints a confidence score; low-confidence ones are flagged for your review.
"""

import argparse
import json
import re
import sys
from difflib import SequenceMatcher

FPS = 30


def normalize(s: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace - so written and spoken compare."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def load_words(whisper_path):
    """Flatten Whisper JSON into a list of {word, start, end} with normalized tokens."""
    with open(whisper_path) as f:
        data = json.load(f)
    words = []
    # support both {"segments":[{"words":[...]}]} and a flat {"words":[...]}
    segments = data.get("segments")
    raw = []
    if segments:
        for seg in segments:
            raw.extend(seg.get("words", []))
    else:
        raw = data.get("words", [])
    for w in raw:
        token = normalize(w.get("word", ""))
        if not token:
            continue
        words.append({"token": token, "start": float(w["start"]), "end": float(w["end"])})
    return words


def find_phrase(words, phrase):
    """
    Slide a window over the spoken words, find the span whose joined tokens best
    match the normalized phrase. Returns (start_sec, end_sec, confidence) or None.
    """
    target = normalize(phrase)
    target_len = len(target.split())
    if target_len == 0 or not words:
        return None

    best = (0.0, None)  # (ratio, (start_idx, end_idx))
    # try windows from a bit shorter to a bit longer than the target,
    # because spoken length differs from written ("$13b" -> 4 spoken words)
    for win in range(max(1, target_len - 1), target_len + 4):
        for i in range(0, len(words) - win + 1):
            span = " ".join(w["token"] for w in words[i : i + win])
            ratio = SequenceMatcher(None, target, span).ratio()
            if ratio > best[0]:
                best = (ratio, (i, i + win))

    ratio, idx = best
    if idx is None:
        return None
    i, j = idx
    return words[i]["start"], words[j - 1]["end"], ratio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--whisper", required=True, help="path to Whisper voiceover.json")
    ap.add_argument("--spec", required=True, help="path to beat spec JSON (input)")
    ap.add_argument("--out", default="beats.json", help="output beats.json")
    ap.add_argument("--min-confidence", type=float, default=0.6)
    args = ap.parse_args()

    words = load_words(args.whisper)
    with open(args.spec) as f:
        spec = json.load(f)

    out_beats = []
    print(f"\nMatching {len(spec['beats'])} beats against {len(words)} spoken words:\n")

    for n, beat in enumerate(spec["beats"]):
        # the beat's words begin when its first script word is spoken.
        # we anchor `from` on the beat's full text, and sweepStart on the highlight phrase.
        full = find_phrase(words, beat["text"])
        emph = find_phrase(words, beat["highlightPhrase"]) if beat.get("highlightPhrase") else None

        if not full:
            print(f"  beat {n}: !! could not place beat text at all - REVIEW")
            from_frame = beat.get("from", 0)
            sweep_start = beat.get("sweepStart", 30)
        else:
            beat_start_sec, beat_end_sec, full_conf = full
            from_frame = round(beat_start_sec * FPS)

            if emph:
                emph_start_sec, _, emph_conf = emph
                # sweepStart is RELATIVE to the beat's own clock
                sweep_start = max(0, round((emph_start_sec - beat_start_sec) * FPS))
                flag = "" if emph_conf >= args.min_confidence else "  <-- LOW CONFIDENCE, REVIEW"
                print(f"  beat {n}: from={from_frame}  sweepStart={sweep_start}  "
                      f"(text {full_conf:.2f}, phrase {emph_conf:.2f}){flag}")
            else:
                sweep_start = beat.get("sweepStart", 30)
                print(f"  beat {n}: from={from_frame}  (no highlight phrase)")

        out = dict(beat)
        out["from"] = from_frame
        out["sweepStart"] = sweep_start
        out_beats.append(out)

    with open(args.out, "w") as f:
        json.dump({"fps": FPS, "beats": out_beats}, f, indent=2)
    print(f"\nWrote {args.out}. Review any flagged beats and hand-edit frames if needed.\n")


if __name__ == "__main__":
    main()
