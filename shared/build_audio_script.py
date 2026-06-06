#!/usr/bin/env python3
"""
build_audio_script.py — Step 4c / Piece 2a: assemble the full-episode narration.

The audio leg's foundation. Walks beats.json IN ORDER and produces:
  1. <out>.txt   — the exact words the narrator speaks across the whole episode,
                   in beat order, for feeding to Inworld (Victor) as ONE read.
  2. <out>.manifest.json — per-beat spoken text + a `spoken` flag, so the
                   Whisper alignment step (2c) can map measured word-timestamps
                   back onto beat boundaries, AND so silent/visual-only beats are
                   explicitly marked (they get no words and need a duration from a
                   different source — see notes).

The rule for a beat's spoken text (decided by inspecting real beats):
  - narration if present (on QuoteCard beats the parser already folds the
    found-line into narration — same text, no duplication).
  - else: SILENT beat (cold-open black, ChapterCards, most NumberCounters,
    DocumentReveals). No words. Marked spoken=false.

Silent beats are real time on the timeline (a ChapterCard holds; the cold-open
black breathes) but have no audio to measure. Their durations come from a
default-hold policy, NOT from Whisper. The manifest marks them so 2c/2d know.

Usage:
    python3 build_audio_script.py beats.json --out ep1_audio
"""
import json, argparse, re

# Default hold (seconds) for silent / visual-only beats, by component or situation.
# These are the ONLY durations not measured from audio; tune by eye in review.
SILENT_HOLDS = {
    "ChapterCard": 2.5,      # a chapter title breathes
    "NumberCounter": 3.0,    # the count animates over this
    "DocumentReveal": 4.0,   # time to read the revealed line
    "HighlightedHeadline": 2.5,
    "LowerThird": 2.5,
    "QuoteCard": 2.5,        # only if it somehow has no spoken line
    "_cold_open_black": 2.0, # beat 0 style silent A beats
    "_default_A_silent": 2.5,
}

def spoken_text(beat):
    nr = (beat.get("narration") or "").strip()
    return nr  # narration already contains the found-line on QuoteCard beats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--out", default="ep1_audio")
    args = ap.parse_args()
    beats = json.load(open(args.beats_json, encoding="utf-8"))

    manifest = []
    spoken_chunks = []
    for b in beats:
        txt = spoken_text(b)
        entry = {
            "index": b["index"],
            "mode": b["mode"],
            "component": b.get("component"),
            "spoken": bool(txt),
            "text": txt,
        }
        if txt:
            spoken_chunks.append(txt)
            entry["char_len"] = len(txt)
        else:
            # assign a default hold so this beat still has a duration downstream
            if b["mode"] == "B":
                hold = SILENT_HOLDS.get(b.get("component"), 2.5)
            else:
                hold = SILENT_HOLDS["_cold_open_black"] if b["index"] == 0 else SILENT_HOLDS["_default_A_silent"]
            entry["default_hold"] = hold
        manifest.append(entry)

    # The full read: one continuous narration, beats joined by a space.
    # (Whisper will re-segment by its own word timing; the manifest preserves
    #  per-beat boundaries so we can re-map.)
    full_text = " ".join(spoken_chunks)

    txt_path = f"{args.out}.txt"
    man_path = f"{args.out}.manifest.json"
    open(txt_path, "w", encoding="utf-8").write(full_text + "\n")
    json.dump(manifest, open(man_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    n_spoken = sum(1 for m in manifest if m["spoken"])
    n_silent = len(manifest) - n_spoken
    words = len(full_text.split())
    est_min = words / 135  # documentary pace, ROUGH — real number comes from Whisper
    print(f"\n=== full-episode audio script ===")
    print(f"{len(beats)} beats: {n_spoken} spoken, {n_silent} silent/visual-only")
    print(f"{words} words across spoken beats (~{est_min:.1f} min at 135wpm — ROUGH)")
    print(f"\nwrote {txt_path}  (the read, for Inworld)")
    print(f"wrote {man_path}  (per-beat boundaries + silent-beat holds, for Whisper align)")
    print(f"\nfirst 8 beats:")
    for m in manifest[:8]:
        tag = m["mode"] if m["mode"]=="A" else f"B:{m['component']}"
        if m["spoken"]:
            print(f"  [{m['index']:02d}] ({tag}) spoken: {m['text'][:64]}{'...' if len(m['text'])>64 else ''}")
        else:
            print(f"  [{m['index']:02d}] ({tag}) SILENT, hold {m['default_hold']}s")
    print(f"\nsilent beats and their holds:")
    for m in manifest:
        if not m["spoken"]:
            tag = m["mode"] if m["mode"]=="A" else f"B:{m['component']}"
            print(f"  [{m['index']:02d}] {tag}: {m['default_hold']}s")

if __name__ == "__main__":
    main()
