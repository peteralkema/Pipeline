#!/usr/bin/env python3
"""
diagnose_drift.py — locate the Mode A audio/video DRIFT, with numbers, not playback.

READ-ONLY. Probes artifacts and prints a per-beat table + verdict. Changes nothing.

It compares THREE timelines beat-by-beat so we can tell WHICH END the drift lives at:
  INTENDED  — durations.json (duration + audio_start; Whisper-measured from the voice)
  SPOKEN    — voiceover.json word timestamps (when the beat's words were ACTUALLY spoken)
  RENDERED  — ffprobe of the pooled conformed clip (what the assembled VIDEO actually plays)

Three deltas expose the bug's location:
  A) INTENDED.duration  vs  RENDERED.duration   -> is the VIDEO CONFORM faithful to the plan?
  B) INTENDED.duration  vs  SPOKEN.span          -> are the INTENDED durations faithful to the VOICE?
  C) cumulative RENDERED position vs INTENDED.audio_start -> the DRIFT itself, made visible.

Reading the result:
  - Delta A systematic + one-signed  -> conform (slow-fill/trim) is imprecise -> fix assemble_episode.
  - Delta B non-zero                 -> durations-building (Whisper align) is wrong; video renders wrong plan.
  - C grows then snaps back near end -> accumulate-then-pin (voice-wins masks it); confirms drift mechanism.

Usage (from repo root):
  python3 shared/diagnose_drift.py --project final-hours/projects/troy
  python3 shared/diagnose_drift.py --project final-hours/projects/troy --csv /tmp/troy_drift.csv
"""
import os, sys, json, argparse, subprocess
from pathlib import Path


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def build_word_timeline(whisper_json):
    """Flatten Whisper segments -> a single ordered list of (word, start, end)."""
    w = json.load(open(whisper_json, encoding="utf-8"))
    words = []
    for seg in w.get("segments", []):
        for wd in (seg.get("words") or []):
            words.append((wd.get("word", "").strip(), wd.get("start"), wd.get("end")))
    return words


def beat_spoken_spans(durations, words):
    """Estimate each beat's actual spoken span from the word timeline.

    durations.json gives each beat an intended audio_start. We assign words to the
    beat whose [audio_start, next audio_start) window they fall into, then the beat's
    spoken span = (first word start, last word end) of its words. This is an INDEPENDENT
    measure of when the beat's audio actually happened, to compare against intended."""
    keys = sorted(durations, key=lambda x: int(x))
    starts = [(int(k), float(durations[k].get("audio_start", 0.0))) for k in keys]
    # window boundaries: beat i owns [start_i, start_{i+1})
    spans = {}
    for n, (idx, st) in enumerate(starts):
        nxt = starts[n + 1][1] if n + 1 < len(starts) else float("inf")
        ws = [w for w in words if w[1] is not None and st <= w[1] < nxt]
        if ws:
            spans[idx] = (ws[0][1], ws[-1][2])  # first word start, last word end
        else:
            spans[idx] = None
    return spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="project dir, e.g. final-hours/projects/troy")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--csv", default=None, help="optional: also write the per-beat table to CSV")
    ap.add_argument("--show", type=int, default=0,
                    help="print every Nth beat to console (0 = print a smart subset)")
    args = ap.parse_args()

    proj = Path(args.project)
    durations = json.load(open(proj / "durations.json", encoding="utf-8"))
    index = json.load(open(proj / "_index.json", encoding="utf-8"))   # {shot_str: beat_idx}
    rev = {int(b): int(s) for s, b in index.items()}                  # beat_idx -> shot number
    pooled_dir = proj / "clips"
    source_dir = proj / "modea" / "clips"
    vo_mp3 = proj / "voiceover.mp3"
    vo_json = proj / "voiceover.json"

    voice_len = probe(vo_mp3)
    words = build_word_timeline(vo_json) if vo_json.exists() else []
    spans = beat_spoken_spans(durations, words) if words else {}

    keys = sorted(durations, key=lambda x: int(x))
    rows = []
    cum_rendered = 0.0   # running start position of the video, summing rendered durations
    sum_intended = 0.0
    sum_rendered = 0.0
    sum_abs_A = 0.0
    signed_A = 0.0
    nA = 0

    for k in keys:
        idx = int(k)
        d = durations[k]
        intended = float(d.get("duration", 0.0))
        a_start = float(d.get("audio_start", 0.0))
        shot = rev.get(idx)
        pooled = source = 0.0
        if shot is not None:
            p = pooled_dir / f"shot_{shot:03d}.mp4"
            s = source_dir / f"shot_{shot:03d}.mp4"
            pooled = probe(p) if p.exists() else 0.0
            source = probe(s) if s.exists() else 0.0

        deltaA = pooled - intended                       # video conform faithfulness
        # spoken span (independent voice measure)
        sp = spans.get(idx)
        spoken_span = (sp[1] - sp[0]) if sp else None
        deltaB = (intended - spoken_span) if spoken_span is not None else None
        # drift: where the video THINKS this beat starts (cum_rendered) vs where the
        # audio actually starts (a_start)
        drift_at_start = cum_rendered - a_start

        rows.append({
            "beat": idx, "shot": shot,
            "intended": round(intended, 3),
            "spoken_span": round(spoken_span, 3) if spoken_span is not None else None,
            "source_clip": round(source, 3),
            "rendered": round(pooled, 3),
            "deltaA_render_minus_intended": round(deltaA, 3),
            "deltaB_intended_minus_spoken": round(deltaB, 3) if deltaB is not None else None,
            "audio_start": round(a_start, 3),
            "video_start_cum": round(cum_rendered, 3),
            "drift_at_start": round(drift_at_start, 3),
        })

        cum_rendered += pooled
        sum_intended += intended
        sum_rendered += pooled
        sum_abs_A += abs(deltaA)
        signed_A += deltaA
        nA += 1

    # ---- console output ----
    print(f"\n=== drift diagnosis: {proj} ===")
    print(f"beats: {len(keys)}   voiceover.mp3: {voice_len:.2f}s   words: {len(words)}\n")
    hdr = (f"{'beat':>4} {'shot':>4} {'intend':>7} {'spoken':>7} {'srcClip':>7} "
           f"{'render':>7} {'dA':>7} {'dB':>7} {'aStart':>8} {'vStart':>8} {'DRIFT':>8}")
    print(hdr); print("-" * len(hdr))

    def fmt(r):
        def g(x): return f"{x:>7}" if x is not None else f"{'-':>7}"
        return (f"{r['beat']:>4} {str(r['shot']):>4} {r['intended']:>7} "
                f"{g(r['spoken_span'])} {r['source_clip']:>7} {r['rendered']:>7} "
                f"{r['deltaA_render_minus_intended']:>7} {g(r['deltaB_intended_minus_spoken'])} "
                f"{r['audio_start']:>8} {r['video_start_cum']:>8} {r['drift_at_start']:>8}")

    # print a smart subset: first 5, every ~15th, last 5, and the worst-drift beat
    show_idx = set(range(5)) | set(range(len(rows) - 5, len(rows)))
    show_idx |= set(range(0, len(rows), max(1, len(rows) // 10)))
    worst = max(rows, key=lambda r: abs(r["drift_at_start"]))
    show_idx.add(worst["beat"])
    if args.show:
        show_idx |= set(range(0, len(rows), args.show))
    for r in rows:
        if r["beat"] in show_idx:
            print(fmt(r))

    # ---- summary / verdict ----
    final_drift = rows[-1]["video_start_cum"] + rows[-1]["rendered"] - voice_len
    print("\n--- summary ---")
    print(f"sum(intended)  = {sum_intended:.2f}s   vs voice {voice_len:.2f}s   "
          f"(diff {sum_intended - voice_len:+.2f}s)   <- are INTENDED durations faithful to the voice?")
    print(f"sum(rendered)  = {sum_rendered:.2f}s   vs voice {voice_len:.2f}s   "
          f"(diff {sum_rendered - voice_len:+.2f}s)   <- does the assembled VIDEO match the voice?")
    print(f"mean deltaA (rendered - intended) = {signed_A / nA:+.4f}s   "
          f"mean |deltaA| = {sum_abs_A / nA:.4f}s")
    print(f"worst cumulative drift = {worst['drift_at_start']:+.2f}s at beat {worst['beat']}")
    print(f"final-beat end vs voice = {final_drift:+.2f}s")

    one_signed = abs(signed_A) > 0.6 * sum_abs_A and sum_abs_A > 0
    print("\n--- verdict ---")
    if sum_abs_A / nA < 0.01:
        print("  deltaA ~ 0: the VIDEO conform faithfully matches intended durations.")
        print("  -> If desync still observed, suspect the INTENDED durations (check deltaB column /")
        print("     sum(intended) vs voice) -> bug is UPSTREAM in build_beat_durations/align_with_whisper.")
    elif one_signed:
        sign = "LONGER" if signed_A > 0 else "SHORTER"
        print(f"  deltaA is SYSTEMATIC and one-signed: rendered clips are consistently {sign} than intended")
        print(f"  (mean {signed_A/nA:+.4f}s/beat x {nA} beats ~= {signed_A:+.1f}s accumulated).")
        print("  -> CONFORM precision bug in assemble_episode.make_video_segment (slow-fill/trim).")
        print("     FIX: build each segment to an exact integer FRAME count, not a float -t seconds.")
    else:
        print("  deltaA is mixed-sign (rounding noise) but accumulates. Likely concat/frame-rounding.")
        print("  -> Ensure every segment is frame-exact at constant FPS before concat.")
    print("  (deltaB column isolates whether INTENDED durations themselves drift from the spoken voice.)")

    if args.csv:
        import csv
        with open(args.csv, "w", newline="") as f:
            wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            wtr.writeheader(); wtr.writerows(rows)
        print(f"\nwrote full 154-row table -> {args.csv}")


if __name__ == "__main__":
    main()
