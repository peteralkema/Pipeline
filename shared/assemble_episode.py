#!/usr/bin/env python3
"""
assemble_episode.py — dual-mode assemble (continuous-narration model).

Walks every beat IN ORDER and builds one episode:
  - VIDEO: each beat's clip, conformed to its MEASURED duration (durations.json).
    Mode A via the reversed index map -> shot_NNN.mp4; Mode B via
    beat_NN_B_<Component>.mp4. Short clips: Mode A SLOW-fills (cinematic), Mode B
    FREEZE-tails (graphics must not warp). Long clips trim. Missing clips (or
    --placeholders) become solid colour blocks so the cut still assembles.
  - AUDIO: the ONE continuous voiceover.mp3, laid over the video UNTOUCHED.
    No slicing, no silence, no reconstruction. The voice track is sacred.

THE INVARIANT (script-craft Part II): the narration is one continuous, protected
voice track and the sole source of timing. Every beat's clip duration == its
spoken-words duration (Whisper-measured, in durations.json). The video conforms to
the voice; the voice is never touched. VOICE WINS: the output is pinned to the
voiceover's length, so the voice always plays in full; trailing video is trimmed
if there's any sub-second rounding mismatch.

There is NO codified silence anywhere. A beat with no narration is an authoring
error (duration 0, source "no_narration" in durations.json) — it is WARNED and
SKIPPED here, never held.

Inputs:
  --durations  projects/ep1-the-promise/durations.json   (timing + mode + component + order;
                                                           from the audio leg / build_beat_durations.py)
  --index      synthetic_modeA_beats_index.json           (Mode A beat -> shot number; from modea_beats.py)
  --voiceover  projects/ep1-the-promise/voiceover.mp3     (the protected continuous track)
  --project    projects/ep1-the-promise                   (clips/ + output live here)

Usage:
  # free pacing cut — colour blocks, real VO + real timing:
  python3 ../shared/assemble_episode.py --placeholders \
      --durations projects/ep1-the-promise/durations.json \
      --index synthetic_modeA_beats_index.json \
      --voiceover projects/ep1-the-promise/voiceover.mp3 \
      --project projects/ep1-the-promise

  # real cut — uses real clips/shot_NNN.mp4 and clips/beat_NN_B_*.mp4:
  python3 ../shared/assemble_episode.py  <same flags, no --placeholders>

Banked ffmpeg lessons applied: duration via d= INSIDE the lavfi filter, hex
colours (0xRRGGBB), -r after the input, every emitted command printed before it runs.
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path

FPS = 30
A_COLOR = "0x222222"   # grey placeholder for recreated (Mode A) beats
B_COLOR = "0x0a1628"   # Synthetic navy placeholder for graphic (Mode B) beats
COLDOPEN_COLOR = "0x000000"
VOICE_LEVEL = 1.15   # VO full (calibrated)
MUSIC_LEVEL = 0.07   # music bed sits low under narration (Jamendo-calibrated)


def run(cmd, desc, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join((r.stderr or "").strip().splitlines()[-6:])
        print(f"\n!! ffmpeg failed during {desc}:")
        print("   cmd:", " ".join(cmd))
        print("   err:", tail)
        sys.exit(1)
    return r


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def reverse_index(index_path):
    """index.json maps engine_shot_index (str) -> beat_index. Reverse to
    beat_index -> shot_index (int)."""
    raw = json.load(open(index_path, encoding="utf-8"))
    rev = {}
    for shot_str, beat_idx in raw.items():
        rev[int(beat_idx)] = int(shot_str)
    return rev


def load_beats_from_durations(durations_path):
    """durations.json is the single timing+structure source: {str(idx): {duration,
    frames, source, mode, component}}. Return an ordered list of beat dicts
    [{index, mode, component, duration, source}, ...] sorted by index."""
    durs = json.load(open(durations_path, encoding="utf-8"))
    beats = []
    for k in sorted(durs, key=lambda x: int(x)):
        d = durs[k]
        beats.append({
            "index": int(k),
            "mode": d.get("mode"),
            "component": d.get("component"),
            "duration": float(d.get("duration", 0.0)),
            "source": d.get("source"),
        })
    return beats


def clip_for(beat, rev_map, clips_dir, force_placeholders):
    """Return (path_or_None, is_placeholder). None path means make a placeholder."""
    idx, mode = beat["index"], beat["mode"]
    if force_placeholders:
        return None, True
    if mode == "B":
        comp = beat.get("component")
        p = clips_dir / f"beat_{idx:02d}_B_{comp}.mp4"
        return (p, False) if p.exists() else (None, True)
    # Mode A
    shot = rev_map.get(idx)
    if shot is None:
        return None, True
    p = clips_dir / f"shot_{shot:03d}.mp4"
    return (p, False) if p.exists() else (None, True)


def make_video_segment(beat, src, is_ph, dur, W, H, work, i):
    """Build a video segment of EXACTLY `dur` seconds at WxH/FPS.
    Short clips: Mode A SLOW-fills (cinematic), Mode B FREEZE-tails (graphics must
    not warp/slow). Long clips trim. native<=0 (probe failed) -> freeze-tail."""
    dst = work / f"v_{i:03d}.mp4"
    if is_ph:
        color = COLDOPEN_COLOR if (beat["index"] == 0) else (B_COLOR if beat["mode"] == "B" else A_COLOR)
        run(["ffmpeg", "-y", "-f", "lavfi",
             "-i", f"color=c={color}:s={W}x{H}:d={dur:.3f}",
             "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst)],
            f"placeholder video beat {beat['index']}")
        return dst
    native = probe(src)
    scale_pad = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}")
    if native >= dur:
        vf = scale_pad
        run(["ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}",
             "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-an", str(dst)], f"trim video beat {beat['index']}")
    else:
        # clip shorter than the slot
        if native <= 0:
            # probe failed — hold a frame to fill so the cut still assembles
            vf = f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur:.3f}"
            label = "hold(probe-fail)"
        elif beat["mode"] == "B":
            # Mode B: FREEZE the tail. A graphic must never be slowed/warped. This is
            # the FAILSAFE for a Mode B phrase that overflowed its component (dispatch
            # rendered at the component max; we freeze the last frame for the remainder).
            # Avoid by good script design (keep promoted phrases within component capacity).
            vf = f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur - native:.3f}"
            label = "freeze-tail(B)"
        else:
            # Mode A: slow-to-fill (cinematic). setpts factor > 1 slows; fps resamples.
            factor = dur / native
            if factor > 2.5:
                print(f"     beat {beat['index']}: slow-fill {native:.1f}s -> {dur:.1f}s "
                      f"({factor:.1f}x — heavy stretch; candidate for more/shorter beats)")
            vf = f"setpts=PTS*{factor:.6f},{scale_pad}"
            label = "slow-fill(A)"
        run(["ffmpeg", "-y", "-i", str(src),
             "-vf", vf, "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-an", str(dst)], f"{label} video beat {beat['index']}")
    return dst


def concat_video(segments, out, work):
    listfile = work / "concat_v.txt"
    listfile.write_text("".join(f"file '{s.resolve()}'\n" for s in segments))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", str(FPS), str(out)], "concat video")
    return out



def _build_music_bed(music_dir, voice_dur, work, n_tracks, crossfade_s, run_fn, probe_fn):
    """Pick n random tracks from music_dir, crossfade the joins, loop to >= voice_dur.
    Returns a Path to the bed (m4a) or None if the dir has no usable tracks.
    run_fn/probe_fn are the module's existing run() and probe() helpers."""
    import random as _random, math as _math
    md = Path(music_dir).expanduser()
    tracks = sorted([p for p in md.glob("*.mp3")] + [p for p in md.glob("*.m4a")]
                    + [p for p in md.glob("*.wav")])
    if not tracks:
        print(f"  !! --music-dir {md} has no audio files; assembling without music")
        return None
    # pick n (or all, if fewer than n exist), in random order
    n = max(1, min(n_tracks, len(tracks)))
    picked = _random.sample(tracks, n)
    print(f"  music-dir: {md.name}/  picked {n} of {len(tracks)} -> "
          + ", ".join(p.name for p in picked))

    # 1) crossfade-chain the picked tracks into one sequence
    if len(picked) == 1:
        seq = picked[0]
    else:
        seq = work / "music_seq.m4a"
        cur = picked[0]
        for k, nxt in enumerate(picked[1:], start=1):
            out = work / f"music_xf_{k}.m4a"
            run_fn(["ffmpeg", "-y", "-i", str(cur), "-i", str(nxt),
                    "-filter_complex",
                    f"[0][1]acrossfade=d={crossfade_s}:c1=tri:c2=tri[a]",
                    "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out)],
                   f"crossfade music {k}")
            cur = out
        seq = cur

    seq_dur = probe_fn(seq)
    if seq_dur <= 0:
        print("  !! music sequence has zero duration; assembling without music")
        return None

    # 2) loop the crossfaded sequence to cover the voiceover
    if seq_dur >= voice_dur:
        return seq
    reps = _math.ceil(voice_dur / seq_dur)
    mlist = work / "music_seq_list.txt"
    mlist.write_text("".join(f"file '{Path(seq).resolve()}'\n" for _ in range(reps)))
    looped = work / "music_bed.m4a"
    run_fn(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
            "-c", "copy", str(looped)], "loop music bed")
    return looped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--durations", default="projects/ep1-the-promise/durations.json",
                    help="durations.json — per-beat measured duration + mode + component + order")
    ap.add_argument("--index", default="synthetic_modeA_beats_index.json",
                    help="Mode A beat -> shot-number map (from modea_beats.py)")
    ap.add_argument("--voiceover", default="projects/ep1-the-promise/voiceover.mp3",
                    help="the ONE continuous protected voice track")
    ap.add_argument("--project", default="projects/ep1-the-promise")
    ap.add_argument("--clips", default=None, help="clips dir (default: <project>/clips)")
    ap.add_argument("--music", default=None, help="music bed mp3 (default: <project>/music.mp3 if present)")
    ap.add_argument("--no-music", action="store_true", help="assemble without any music bed")
    ap.add_argument("--music-dir", default=None,
                    help="folder of tracks: pick N random, crossfade, loop to fill (overrides --music)")
    ap.add_argument("--music-tracks", type=int, default=3, help="how many random tracks to cycle (default 3)")
    ap.add_argument("--music-crossfade", type=float, default=2.0, help="crossfade seconds between tracks (default 2)")
    ap.add_argument("--out", default=None, help="output mp4 (default: pacing_cut.mp4 or final_video.mp4)")
    ap.add_argument("--placeholders", action="store_true",
                    help="force colour-block placeholders for ALL beats (free pacing cut)")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    args = ap.parse_args()

    durations = Path(args.durations); index = Path(args.index)
    voiceover = Path(args.voiceover); project = Path(args.project)
    clips_dir = Path(args.clips) if args.clips else project / "clips"
    W, H = args.width, args.height

    for p, label in [(durations, "durations.json"), (index, "index map"), (voiceover, "voiceover")]:
        if not p.exists():
            sys.exit(f"missing {label}: {p}")

    out = Path(args.out) if args.out else project / ("pacing_cut.mp4" if args.placeholders else "final_video.mp4")

    beats = load_beats_from_durations(durations)
    rev_map = reverse_index(index)
    voice_dur = probe(voiceover)

    print(f"\n=== dual-mode assemble: {len(beats)} beats -> {out} ===")
    print(f"mode: {'PLACEHOLDERS (free pacing cut)' if args.placeholders else 'real clips where present'}")
    print(f"resolution: {W}x{H} @ {FPS}fps   voiceover: {voiceover} ({voice_dur:.1f}s) [VOICE WINS]\n")

    # Surface any no-narration authoring errors (0-duration beats) and drop them.
    bad = [b for b in beats if b["source"] == "no_narration" or b["duration"] <= 0.0]
    if bad:
        idxs = [b["index"] for b in bad]
        print(f"  !! {len(bad)} beat(s) have NO narration (0s) — authoring errors, SKIPPED: {idxs}")
        print(f"     Every beat must carry spoken words (continuous-narration model). Fix the script.")
        beats = [b for b in beats if b not in bad]

    work = Path(tempfile.mkdtemp(prefix="assemble_ep_", dir=str(project)))
    n_real, n_ph = 0, 0
    try:
        v_segs = []
        for i, b in enumerate(beats):
            dur = float(b["duration"])
            src, is_ph = clip_for(b, rev_map, clips_dir, args.placeholders)
            if is_ph: n_ph += 1
            else: n_real += 1
            v_segs.append(make_video_segment(b, src, is_ph, dur, W, H, work, i))
            tag = b["mode"] if b["mode"] == "A" else f"B:{b.get('component')}"
            kind = "ph" if is_ph else "real"
            if i % 10 == 0 or i == len(beats) - 1:
                print(f"  [{b['index']:02d}] {tag:18s} {dur:5.2f}s  {kind}")

        print("\n  concatenating video...")
        silent_v = concat_video(v_segs, work / "video.mp4", work)
        vid_dur = probe(silent_v)
        print(f"  video track: {vid_dur:.1f}s   voice track: {voice_dur:.1f}s   "
              f"(diff {abs(vid_dur - voice_dur):.2f}s)")

        # ── AUDIO: the WHOLE voiceover, untouched. VOICE WINS — output pinned to the
        # voice length so the voice always plays in full; trailing video trimmed if any
        # sub-second mismatch. No per-beat audio, no silence, no reconstruction.
        print("  muxing (whole voiceover over conformed video; voice untouched)...")
        music_path = None
        if not args.no_music:
            if args.music_dir:
                music_path = _build_music_bed(
                    args.music_dir, voice_dur, work,
                    args.music_tracks, args.music_crossfade, run, probe)
            else:
                cand = Path(args.music).expanduser() if args.music else (project / "music.mp3")
                if cand.exists():
                    music_path = cand
                elif args.music:
                    print(f"  !! --music {cand} not found; assembling without music")

        if music_path:
            import math as _math
            print(f"  music bed: {music_path.name} (VOICE {VOICE_LEVEL} / MUSIC {MUSIC_LEVEL})")
            md = probe(music_path)
            music_src = music_path
            if md > 0 and md < voice_dur:
                reps = _math.ceil(voice_dur / md)
                mlist = work / "mlist.txt"
                mlist.write_text("".join(f"file '{music_path.resolve()}'\n" for _ in range(reps)))
                looped = work / "music_looped.m4a"
                run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
                     "-c", "copy", str(looped)], "loop music")
                music_src = looped
            run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(voiceover), "-i", str(music_src),
                 "-filter_complex",
                 f"[1:a]volume={VOICE_LEVEL}[v];[2:a]volume={MUSIC_LEVEL}[m];"
                 f"[v][m]amix=inputs=2:normalize=0:duration=first:dropout_transition=0[a]",
                 "-map", "0:v:0", "-map", "[a]",
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-t", f"{voice_dur:.3f}", str(out)],
                "mux video+voice+music")
        else:
            run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(voiceover),
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-map", "0:v:0", "-map", "1:a:0",
                 "-t", f"{voice_dur:.3f}", str(out)],
                "mux video+voice")

        fd = probe(out)
        print(f"\n  final: {fd:.1f}s ({fd/60:.2f} min)  [pinned to voice {voice_dur:.1f}s]")
        print(f"\nDONE -> {out}")
        print(f"  {n_real} real clips, {n_ph} placeholders")
        if args.placeholders:
            print("\n  This is the PACING CUT: watch it to judge runtime/rhythm before any spend.")
            print("  When the real clips exist, re-run WITHOUT --placeholders for the real episode.")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
