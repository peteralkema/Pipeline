#!/usr/bin/env python3
"""
dispatch.py - Step 2 of the Synthetic dual-mode pipeline.

Walks the parsed beats (from parse_script.py) IN ORDER and routes each one to
its renderer based on `mode`:
    A          -> the existing stills->clips path (recreation_pipeline)
    B:Component -> the Remotion path (payload -> props -> remotion render)

Both paths are STUBBED here. The job of Step 2 is to prove routing + ordering +
prop-shaping are correct before any real renderer is wired. Each stub prints
exactly what it WOULD do and "returns" a clip path, so we can confirm the whole
timeline assembles in the right order with the right inputs.

Run it after parse_script.py:
    python3 parse_script.py <script.md> --json beats.json
    python3 dispatch.py beats.json
"""

import sys
import json
import argparse

KNOWN_COMPONENTS = {
    "HighlightedHeadline", "LowerThird", "NumberCounter",
    "ChapterCard", "QuoteCard", "DocumentReveal",
}

FPS = 30  # Remotion frame rate; durations (once measured) become frame counts.


# --------------------------------------------------------------------------
# Mode B: payload -> props.  This is the registry boundary. The parser already
# gave us the payload; here we shape it into the exact props each component
# expects, and apply per-component defaults. When the real Remotion renderer
# arrives, ONLY render_mode_b() changes - everything else stays.
# --------------------------------------------------------------------------

def shape_props(component: str, payload: dict) -> dict:
    """Translate a parsed B payload into Remotion component props."""
    p = dict(payload)  # copy

    if component == "NumberCounter":
        props = {
            "to": p.get("to", 0),
            "from": p.get("from", 0),
            "prefix": p.get("prefix", ""),
            "label": p.get("label", ""),
            "plainYear": bool(p.get("plain_year", False)),
            "countdown": bool(p.get("countdown", False)),
        }
        # plain-year mode: no separators, no prefix
        if props["plainYear"]:
            props["prefix"] = ""
            props["separator"] = ""
        return props

    if component == "QuoteCard":
        return {
            "attribution": p.get("text", ""),   # name/source/date - the receipt
            "highlight": p.get("highlight", ""), # stressed phrase, voice-synced
            # NB: the spoken line is NOT a prop - it lives in the voiceover.
            # The card never duplicates the full sentence (no-karaoke rule).
        }

    if component == "HighlightedHeadline":
        return {"text": p.get("text", ""), "highlight": p.get("highlight", "")}

    if component == "ChapterCard":
        return {"text": p.get("text", "")}

    if component == "LowerThird":
        return {"text": p.get("text", "")}

    if component == "DocumentReveal":
        return {
            "title": p.get("text", ""),
            "showLine": p.get("show_line", ""),
            "source": p.get("source", ""),
        }

    # unknown component - shouldn't reach here if parser flagged it
    return p


# --------------------------------------------------------------------------
# Renderers (STUBBED). Each returns a clip path it "produced".
# --------------------------------------------------------------------------

def render_mode_a(beat: dict, frames: int) -> str:
    clip = f"clips/beat_{beat['index']:02d}_A.mp4"
    face = "  [FACE-HOLD]" if beat.get("face_hold") else ""
    sil = "  [+silence]" if beat.get("silence_after") else ""
    print(f"  -> MODE A  stills->clip   ({frames} frames){face}{sil}")
    print(f"     visual : {beat.get('visual','')[:70]}")
    if beat.get("narration"):
        print(f"     vo     : {beat['narration'][:70]}...")
    print(f"     => {clip}")
    return clip


def render_mode_b(beat: dict, frames: int) -> str:
    comp = beat["component"]
    props = shape_props(comp, beat.get("payload", {}))
    clip = f"clips/beat_{beat['index']:02d}_B_{comp}.mp4"
    sil = "  [+silence]" if beat.get("silence_after") else ""
    print(f"  -> MODE B  remotion render {comp}   ({frames} frames){sil}")
    print(f"     props  : {props}")
    if beat.get("found_line"):
        print(f"     vo     : \"{beat['found_line']}\"  (spoken; card shows attribution only)")
    print(f"     => would run: npx remotion render {comp} --props='{json.dumps(props)}' --frames={frames}")
    print(f"     => {clip}")
    return clip


# --------------------------------------------------------------------------
# Duration: until the audio spine exists, estimate frames from narration length
# (words / 135 wpm * fps). Mode B beats with no narration get a sensible default.
# When Whisper timing arrives, this single function is what gets replaced - the
# measured duration per beat flows straight into `frames` for BOTH renderers.
# --------------------------------------------------------------------------

def estimate_frames(beat: dict) -> int:
    text = beat.get("narration") or beat.get("found_line") or ""
    words = len(text.split())
    if words:
        seconds = max(1.5, words / 135 * 60)
    else:
        # silent / card-only beat defaults by type
        seconds = 3.0 if beat["mode"] == "B" else 2.5
    if beat.get("silence_after"):
        seconds += 1.5
    return round(seconds * FPS)


def dispatch(beats: list) -> list:
    timeline = []
    warnings = []
    for beat in beats:
        frames = estimate_frames(beat)
        idx = beat["index"]
        mode = beat["mode"]

        if mode == "A":
            print(f"[{idx:02d}] A")
            clip = render_mode_a(beat, frames)
        elif mode == "B":
            comp = beat.get("component")
            if comp not in KNOWN_COMPONENTS:
                warnings.append(f"beat {idx}: unknown component '{comp}' - not routed")
                print(f"[{idx:02d}] B:{comp}  !! UNKNOWN - skipped")
                continue
            print(f"[{idx:02d}] B:{comp}")
            clip = render_mode_b(beat, frames)
        else:
            warnings.append(f"beat {idx}: unknown mode '{mode}'")
            continue

        timeline.append({"index": idx, "mode": mode, "clip": clip, "frames": frames})
        print()

    return timeline, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    args = ap.parse_args()

    with open(args.beats_json, encoding="utf-8") as f:
        beats = json.load(f)

    print(f"\n=== dispatch: {args.beats_json} ({len(beats)} beats) ===\n")
    timeline, warnings = dispatch(beats)

    a = sum(1 for t in timeline if t["mode"] == "A")
    b = sum(1 for t in timeline if t["mode"] == "B")
    total_frames = sum(t["frames"] for t in timeline)
    print("=" * 60)
    print(f"timeline: {len(timeline)} clips in order  |  A: {a}  B: {b}")
    print(f"est. runtime: {total_frames} frames @ {FPS}fps = "
          f"{total_frames/FPS/60:.1f} min  (rough; real timing comes from Whisper)")
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print("  " + w)
    # the timeline (ordered clip list) is what Step 4 (assemble) will consume
    print("\nfirst 6 timeline slots:")
    for t in timeline[:6]:
        print(f"  {t['index']:02d}  {t['mode']}  {t['frames']:>3}f  {t['clip']}")


if __name__ == "__main__":
    main()
