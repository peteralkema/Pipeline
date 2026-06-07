#!/usr/bin/env python3
"""
build_audio_script.py — Piece 2a: assemble the full-episode narration.

The audio leg's foundation. Walks beats.json IN ORDER and produces:
  1. <out>.txt   — the exact words the narrator speaks across the WHOLE episode,
                   in beat order, as ONE continuous read for Inworld (Victor).
  2. <out>.manifest.json — per-beat spoken text + a `spoken` flag, so the Whisper
                   alignment step (2c) can map measured word-timestamps back onto
                   beat boundaries.

CONTINUOUS-NARRATION MODEL (script-craft Part II):
The narration is one continuous, unbroken track and the sole source of timing.
There is NO codified silence anywhere in this pipeline — no holds, no inserted
gaps, no "silent beat" category. EVERY beat carries spoken words; a Mode B beat is
a PROMOTED PHRASE (words stay spoken, only the on-screen visual changes).

Therefore a beat with no narration is an AUTHORING ERROR, not a silent beat. It is
flagged here (`spoken=false`) and surfaced LOUDLY; it is never handed a default
hold. The downstream duration step (build_beat_durations.py) measures every beat's
duration from Whisper; a wordless beat gets 0s + a `no_narration` warning there.
The manifest's `spoken` flag therefore means "has words / authoring-error", and is
the single signal 2c uses — there is no second silent-beat policy to keep in sync.

Usage:
    python3 build_audio_script.py beats.json --out ep1_audio
"""
import json, argparse


def spoken_text(beat):
    """A beat's spoken words = its narration. On QuoteCard beats the parser already
    folds the found-line into narration (same text, no duplication)."""
    return (beat.get("narration") or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--out", default="ep1_audio")
    args = ap.parse_args()
    beats = json.load(open(args.beats_json, encoding="utf-8"))

    manifest = []
    spoken_chunks = []
    wordless = []
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
            # No narration. NOT silence — an authoring error. Flag it; never hold it.
            wordless.append(b["index"])
        manifest.append(entry)

    # The full read: one continuous narration, beats joined by a single space.
    # Whisper re-segments by its own word timing; the manifest preserves per-beat
    # boundaries so 2c can re-map measured timestamps onto beats.
    full_text = " ".join(spoken_chunks)

    txt_path = f"{args.out}.txt"
    man_path = f"{args.out}.manifest.json"
    open(txt_path, "w", encoding="utf-8").write(full_text + "\n")
    json.dump(manifest, open(man_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    n_spoken = sum(1 for m in manifest if m["spoken"])
    words = len(full_text.split())
    est_min = words / 135  # documentary pace, ROUGH — real number comes from Whisper
    print(f"\n=== full-episode audio script ===")
    print(f"{len(beats)} beats: {n_spoken} spoken")
    print(f"{words} words (~{est_min:.1f} min at 135wpm — ROUGH; real number from Whisper)")
    print(f"\nwrote {txt_path}  (the continuous read, for Inworld)")
    print(f"wrote {man_path}  (per-beat boundaries, for Whisper align)")
    print(f"\nfirst 8 beats:")
    for m in manifest[:8]:
        tag = m["mode"] if m["mode"] == "A" else f"B:{m['component']}"
        if m["spoken"]:
            print(f"  [{m['index']:02d}] ({tag}) {m['text'][:64]}{'...' if len(m['text'])>64 else ''}")
        else:
            print(f"  [{m['index']:02d}] ({tag}) !! NO NARRATION")

    if wordless:
        print(f"\n  !! {len(wordless)} beat(s) have NO narration: {wordless}")
        print(f"     The continuous-narration model requires EVERY beat to carry spoken words")
        print(f"     (a Mode B beat is a promoted phrase — words stay spoken). These are")
        print(f"     authoring errors. Fix the script: give each beat words, or remove it.")
        print(f"     (They will be measured at 0s + warned by build_beat_durations.py, and")
        print(f"      skipped by the assembler — never held.)")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
