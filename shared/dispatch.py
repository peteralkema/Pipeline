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

import os
import sys
import json
import argparse
import tempfile
import subprocess

KNOWN_COMPONENTS = {
    "HighlightedHeadline", "LowerThird", "NumberCounter",
    "ChapterCard", "QuoteCard", "DocumentReveal",
}

FPS = 30  # Remotion frame rate; durations (once measured) become frame counts.

# Where the Remotion project lives. Override with env REMOTION_DIR so moving the
# folder into the repo later is a one-line change, not a code edit.
REMOTION_DIR = os.environ.get("REMOTION_DIR", os.path.expanduser("~/Projects/remotion-learning"))
ACCENT = "#3b5bdb"   # Synthetic channel accent; every prototype takes accentColor
COMPOSITION_ID = {c: c for c in KNOWN_COMPONENTS}  # parsed name -> Remotion composition id (1:1)


# --------------------------------------------------------------------------
# Mode B: payload -> props.  This is the registry boundary. The parser already
# gave us the payload; here we shape it into the exact props each component
# expects, and apply per-component defaults. When the real Remotion renderer
# arrives, ONLY render_mode_b() changes - everything else stays.
# --------------------------------------------------------------------------

def shape_props(component: str, payload: dict, beat: dict):
    """Translate a parsed B payload into REAL prototype props (per Root.tsx schemas).
    Returns (props, notes). notes = component-feature gaps to upgrade later."""
    p = dict(payload)
    notes = []

    if component == "QuoteCard":
        # Prototype: {quote, attribution, accentColor} — it RENDERS the quote.
        # Doctrine wants spoken line in VO only + card shows attribution. Prototype
        # has no attribution-only mode yet, so render the found-line as quote for now.
        quote = beat.get("found_line", "") or p.get("text", "")
        notes.append("QuoteCard renders spoken line (karaoke) — needs attribution-only/highlight variant later")
        return {"quote": quote, "attribution": p.get("text", ""), "accentColor": ACCENT}, notes

    if component == "NumberCounter":
        # Prototype: {endValue, prefix, suffix, label, accentColor}; always 0->endValue.
        props = {"endValue": p.get("to", 0), "prefix": p.get("prefix", ""),
                 "suffix": "", "label": p.get("label", ""), "accentColor": ACCENT}
        if p.get("countdown"):
            notes.append(f"COUNTDOWN ({p.get('from')}->{p.get('to')}) unsupported — renders 0->{p.get('to')}; add startValue+countdown later")
        if p.get("plain_year"):
            notes.append("PLAIN-YEAR unsupported — renders with commas; add plainYear prop later")
        return props, notes

    if component == "HighlightedHeadline":
        return {"text": p.get("text", ""), "highlightPhrase": p.get("highlight", ""),
                "highlightColor": ACCENT, "sweepStart": 30}, notes

    if component == "ChapterCard":
        text = p.get("text", ""); eyebrow, title = "", text
        for sep in ["\u2014", "\u2013", " - ", ":"]:
            if sep in text:
                a, b = text.split(sep, 1); eyebrow, title = a.strip(), b.strip(); break
        return {"eyebrow": eyebrow, "title": title, "accentColor": ACCENT}, notes

    if component == "LowerThird":
        text = p.get("text", ""); primary, secondary = text, ""
        for sep in ["\u2014", "\u2013", " - ", ":"]:
            if sep in text:
                a, b = text.split(sep, 1); primary, secondary = a.strip(), b.strip(); break
        return {"primary": primary, "secondary": secondary, "accentColor": ACCENT}, notes

    if component == "DocumentReveal":
        return {"source": p.get("source", "") or p.get("text", ""),
                "body": p.get("show_line", ""), "highlight": p.get("highlight", ""),
                "accentColor": ACCENT}, notes

    return p, notes

# --------------------------------------------------------------------------
# Renderers (STUBBED). Each returns a clip path it "produced".
# --------------------------------------------------------------------------

def render_mode_a(beat: dict, frames: int, render: bool = False) -> str:
    clip = f"clips/beat_{beat['index']:02d}_A.mp4"
    face = "  [FACE-HOLD]" if beat.get("face_hold") else ""
    sil = "  [+silence]" if beat.get("silence_after") else ""
    print(f"  -> MODE A  stills->clip   ({frames} frames){face}{sil}")
    print(f"     visual : {beat.get('visual','')[:70]}")
    if beat.get("narration"):
        print(f"     vo     : {beat['narration'][:70]}...")
    print(f"     => {clip}")
    return clip


def render_mode_b(beat: dict, frames: int, render: bool = False) -> str:
    comp = beat["component"]
    comp_id = COMPOSITION_ID.get(comp, comp)
    props, notes = shape_props(comp, beat.get("payload", {}), beat)
    os.makedirs(os.path.join(os.getcwd(), "clips"), exist_ok=True)
    clip = os.path.abspath(f"clips/beat_{beat['index']:02d}_B_{comp}.mp4")

    print(f"  -> MODE B  {comp}   ({frames} frames)")
    print(f"     props  : {props}")
    if beat.get("found_line"):
        print(f"     vo     : \"{beat['found_line']}\"  (spoken; from voiceover)")
    for n in notes:
        print(f"     !! {n}")

    tf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(props, tf, ensure_ascii=False); tf.close()
    cmd = ["npx", "remotion", "render", comp_id, clip,
           f"--props={tf.name}", f"--frames=0-{max(1, frames - 1)}"]
    print(f"     run    : (cwd={REMOTION_DIR}) {' '.join(cmd)}")

    if not render:
        os.unlink(tf.name)
        return clip
    try:
        res = subprocess.run(cmd, cwd=REMOTION_DIR, capture_output=True, text=True, timeout=600)
        if res.returncode != 0:
            tail = res.stderr.strip().splitlines()[-1] if res.stderr.strip() else "no stderr"
            print(f"     !! FAILED (exit {res.returncode}): {tail}")
        else:
            print(f"     => {clip}")
    except FileNotFoundError:
        print("     !! 'npx' not found — is Node on PATH on this box?")
    except subprocess.TimeoutExpired:
        print("     !! timed out (>600s)")
    finally:
        if os.path.exists(tf.name): os.unlink(tf.name)
    return clip

# --------------------------------------------------------------------------
# Duration: until the audio spine exists, estimate frames from narration length
# (words / 135 wpm * fps). Mode B beats with no narration get a sensible default.
# When Whisper timing arrives, this single function is what gets replaced - the
# measured duration per beat flows straight into `frames` for BOTH renderers.
# --------------------------------------------------------------------------

# Real per-beat durations from the audio leg (build_beat_durations.py -> durations.json).
# Keyed by str(beat index) -> {"duration","frames","source",...}. Loaded once via
# load_durations(); when present, estimate_frames() uses MEASURED frames instead of
# the word-count guess. This is the seam where the audio spine replaces the proxy.
_DURATIONS = None

def load_durations(path):
    """Load durations.json (from the audio leg). Call before dispatch()."""
    global _DURATIONS
    import json as _json
    with open(path, encoding="utf-8") as f:
        _DURATIONS = _json.load(f)
    n = len(_DURATIONS)
    measured = sum(1 for d in _DURATIONS.values() if d.get("source") == "whisper")
    print(f"   durations: loaded {n} beats ({measured} whisper-measured) from {path}")
    return _DURATIONS


def estimate_frames(beat: dict) -> int:
    # 1. Real measured duration from the audio leg, if available.
    if _DURATIONS is not None:
        d = _DURATIONS.get(str(beat["index"]))
        if d and "frames" in d:
            return int(d["frames"])
        # durations file present but this beat missing -> fall through to proxy,
        # but make the gap visible rather than silently guessing.
        print(f"   !! beat {beat['index']} not in durations.json — using word-count proxy")
    # 2. Fallback: word-count proxy (pre-audio-leg behaviour; keeps script standalone).
    text = beat.get("narration") or beat.get("found_line") or ""
    words = len(text.split())
    if words:
        seconds = max(1.5, words / 135 * 60)
    else:
        seconds = 3.0 if beat["mode"] == "B" else 2.5
    if beat.get("silence_after"):
        seconds += 1.5
    return round(seconds * FPS)


def dispatch(beats, render=False, only=None):
    timeline = []
    warnings = []
    for beat in beats:
        if only is not None and beat['index'] not in only:
            continue
        frames = estimate_frames(beat)
        idx = beat["index"]
        mode = beat["mode"]

        if mode == "A":
            print(f"[{idx:02d}] A")
            clip = render_mode_a(beat, frames, render=render)
        elif mode == "B":
            comp = beat.get("component")
            if comp not in KNOWN_COMPONENTS:
                warnings.append(f"beat {idx}: unknown component '{comp}' - not routed")
                print(f"[{idx:02d}] B:{comp}  !! UNKNOWN - skipped")
                continue
            print(f"[{idx:02d}] B:{comp}")
            clip = render_mode_b(beat, frames, render=render)
        else:
            warnings.append(f"beat {idx}: unknown mode '{mode}'")
            continue

        timeline.append({"index": idx, "mode": mode, "clip": clip, "frames": frames})
        print()

    return timeline, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--render", action="store_true", help="actually run Remotion (default: dry-run, just print the command)")
    ap.add_argument("--only", help="comma-separated beat indices to process, e.g. 27,01")
    ap.add_argument("--durations", help="durations.json from the audio leg (real per-beat timing); if omitted, falls back to the word-count proxy")
    args = ap.parse_args()

    with open(args.beats_json, encoding="utf-8") as f:
        beats = json.load(f)

    print(f"\n=== dispatch: {args.beats_json} ({len(beats)} beats) ===\n")
    only = set(int(x) for x in args.only.split(',')) if args.only else None
    if args.durations:
        load_durations(args.durations)
    timeline, warnings = dispatch(beats, render=args.render, only=only)

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
