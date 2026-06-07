#!/usr/bin/env python3
"""
assemble_episode.py - Synthetic 4c, Piece 3: the dual-mode assemble.

Walks all 62 beats IN TRUE ORDER and builds one episode:
  - video: each beat's clip laid end-to-end, conformed to its timing-table
    duration (Mode A via the reversed index map -> shot_NNN.mp4; Mode B via
    beat_NN_B_<Component>.mp4). Missing clips (or --placeholders) become solid
    colour blocks so the cut still assembles.
  - audio: for each beat, the real VO sliced at [vo_start, vo_start+vo_span]
    then padded with silence to the beat's full duration; silent beats are pure
    silence. Concatenated, this is the VO with the holds' silence INSERTED at the
    right places — so audio length == video length, perfectly synced, and the
    silent holds are real pauses, not drift.

THE KEY IDEA: build it once, run it on placeholders FIRST (free), watch the cut
to settle pacing/runtime, then run the SAME command without --placeholders once
the real Mode A clips exist. Nothing else changes.

Inputs (defaults assume you're in the synthetic/ channel folder):
  --timed      ep1_beats_timed.json                       (from align_episode.py)
  --index      synthetic_modeA_beats_index.json           (from modea_beats.py)
  --voiceover  projects/ep1-the-promise/voiceover.mp3     (from make_episode_vo.py)
  --project    projects/ep1-the-promise                   (clips/ + output live here)

Usage:
  # free pacing cut — grey A blocks, navy B blocks, real VO + real timing:
  python3 ../shared/assemble_episode.py --placeholders

  # final cut — uses real clips/shot_NNN.mp4 and clips/beat_NN_B_*.mp4 if present:
  python3 ../shared/assemble_episode.py

Banked ffmpeg lessons applied: duration via d= INSIDE the lavfi filter, hex
colours (0xRRGGBB), -r after the input, and every emitted command is printed
before it runs so a failure shows exactly what was attempted.
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
    """Build a video segment of EXACTLY `dur` seconds at WxH/FPS."""
    dst = work / f"v_{i:03d}.mp4"
    if is_ph:
        color = COLDOPEN_COLOR if (beat["index"] == 0) else (B_COLOR if beat["mode"] == "B" else A_COLOR)
        # d= INSIDE the filter; -r after; hex colour. (banked lesson)
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
        # clip shorter than the slot -> SLOW it to fill (slow-to-fill, not freeze).
        # setpts factor > 1 slows playback; the fps filter (in scale_pad) resamples
        # to constant FPS so it stays smooth. Guard native<=0 (probe failed).
        if native <= 0:
            vf = f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur:.3f}"
        else:
            factor = dur / native
            if factor > 2.5:
                print(f"     beat {beat['index']}: slow-fill {native:.1f}s -> {dur:.1f}s "
                      f"({factor:.1f}x — heavy stretch; candidate for more/shorter beats)")
            vf = f"setpts=PTS*{factor:.6f},{scale_pad}"
        run(["ffmpeg", "-y", "-i", str(src),
             "-vf", vf, "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-an", str(dst)], f"slow-fill video beat {beat['index']}")
    return dst


def make_audio_segment(beat, dur, voiceover, work, i):
    """Build an audio segment of EXACTLY `dur` seconds: VO slice + silence pad,
    or pure silence for silent beats. 48k stereo AAC-friendly PCM."""
    dst = work / f"a_{i:03d}.m4a"
    span = float(beat.get("vo_span") or 0.0)
    if beat.get("vo_start") is not None and span > 0:
        start = float(beat["vo_start"])
        # take the VO window, then pad with silence out to the full beat duration
        run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-t", f"{span:.3f}", "-i", str(voiceover),
             "-af", f"apad=whole_dur={dur:.3f},aformat=sample_rates=48000:channel_layouts=stereo",
             "-t", f"{dur:.3f}", "-c:a", "aac", "-b:a", "192k", str(dst)],
            f"vo+pad audio beat {beat['index']}")
    else:
        run(["ffmpeg", "-y", "-f", "lavfi",
             "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000",
             "-t", f"{dur:.3f}", "-c:a", "aac", "-b:a", "192k", str(dst)],
            f"silence audio beat {beat['index']}")
    return dst


def build_audio_track(beats, voiceover, work):
    """Build ONE continuous audio track in a single ffmpeg pass. Replaces the
    per-beat make_audio_segment + AAC-concat, which left encoder-delay gaps at
    every beat boundary ('audio cuts then resumes'). For each beat in order:
      - spoken (vo_span>0): atrim the real VO at [vo_start, vo_start+vo_span].
        These slices are contiguous across spoken beats, so they reconstruct the
        continuous voiceover exactly, sample-accurate (atrim is on decoded samples,
        unlike -ss). Any remainder (audio_duration - vo_span = silence_after bonus)
        becomes trailing silence.
      - fully silent beat (hold): anullsrc of audio_duration.
    Joined with the concat FILTER (single decode+encode) so there are NO inter-
    segment gaps. Total == sum(audio_duration) == the video track."""
    SR = 48000
    AFMT = f"aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo"
    parts, labels, k = [], [], 0
    for b in sorted(beats, key=lambda x: x["index"]):
        a_dur = float(b["audio_duration"])
        vo_span = float(b.get("vo_span") or 0.0)
        vo_start = b.get("vo_start")
        if vo_span > 0 and vo_start is not None:
            lbl = f"s{k}"; k += 1
            parts.append(f"[0:a]atrim=start={float(vo_start):.3f}:duration={vo_span:.3f},"
                         f"asetpts=PTS-STARTPTS,{AFMT}[{lbl}]")
            labels.append(lbl)
            gap = a_dur - vo_span
            if gap > 0.001:
                lbl = f"s{k}"; k += 1
                parts.append(f"anullsrc=r={SR}:cl=stereo,atrim=duration={gap:.3f},{AFMT}[{lbl}]")
                labels.append(lbl)
        else:
            if a_dur > 0.001:
                lbl = f"s{k}"; k += 1
                parts.append(f"anullsrc=r={SR}:cl=stereo,atrim=duration={a_dur:.3f},{AFMT}[{lbl}]")
                labels.append(lbl)
    if not labels:
        raise SystemExit("build_audio_track: no audio segments produced (empty/invalid timing table).")
    parts.append("".join(f"[{l}]" for l in labels) + f"concat=n={len(labels)}:v=0:a=1[aout]")
    graph = ";\n".join(parts)
    script = work / "audio_filter.txt"
    script.write_text(graph)
    out = work / "audio.m4a"
    run(["ffmpeg", "-y", "-i", str(voiceover),
         "-filter_complex_script", str(script),
         "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", str(out)], "build continuous audio")
    return out


def concat(segments, out, work, kind):
    listfile = work / f"concat_{kind}.txt"
    listfile.write_text("".join(f"file '{s.resolve()}'\n" for s in segments))
    if kind == "v":
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-r", str(FPS), str(out)], "concat video")
    else:
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
             "-c:a", "aac", "-b:a", "192k", str(out)], "concat audio")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timed", default="ep1_beats_timed.json")
    ap.add_argument("--index", default="synthetic_modeA_beats_index.json")
    ap.add_argument("--voiceover", default="projects/ep1-the-promise/voiceover.mp3")
    ap.add_argument("--project", default="projects/ep1-the-promise")
    ap.add_argument("--clips", default=None, help="clips dir (default: <project>/clips)")
    ap.add_argument("--music", default=None, help="music bed mp3 (default: <project>/music.mp3 if present)")
    ap.add_argument("--no-music", action="store_true", help="assemble without any music bed")
    ap.add_argument("--out", default=None, help="output mp4 (default: pacing_cut.mp4 or final_video.mp4)")
    ap.add_argument("--placeholders", action="store_true",
                    help="force colour-block placeholders for ALL beats (free pacing cut)")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    args = ap.parse_args()

    timed = Path(args.timed); index = Path(args.index)
    voiceover = Path(args.voiceover); project = Path(args.project)
    clips_dir = Path(args.clips) if args.clips else project / "clips"
    W, H = args.width, args.height

    for p, label in [(timed, "timed table"), (index, "index map"), (voiceover, "voiceover")]:
        if not p.exists():
            sys.exit(f"missing {label}: {p}")

    out = Path(args.out) if args.out else project / ("pacing_cut.mp4" if args.placeholders else "final_video.mp4")

    beats = json.load(open(timed, encoding="utf-8"))
    beats.sort(key=lambda b: b["index"])
    rev_map = reverse_index(index)

    print(f"\n=== dual-mode assemble: {len(beats)} beats -> {out} ===")
    print(f"mode: {'PLACEHOLDERS (free pacing cut)' if args.placeholders else 'real clips where present'}")
    print(f"resolution: {W}x{H} @ {FPS}fps   voiceover: {voiceover} ({probe(voiceover):.1f}s)\n")

    work = Path(tempfile.mkdtemp(prefix="assemble_ep_", dir=str(project)))
    n_real, n_ph = 0, 0
    try:
        v_segs, a_segs = [], []
        for i, b in enumerate(beats):
            dur = float(b["audio_duration"])
            src, is_ph = clip_for(b, rev_map, clips_dir, args.placeholders)
            if is_ph: n_ph += 1
            else: n_real += 1
            v_segs.append(make_video_segment(b, src, is_ph, dur, W, H, work, i))
            tag = b["mode"] if b["mode"] == "A" else f"B:{b.get('component')}"
            kind = "ph" if is_ph else "real"
            if i % 10 == 0 or i == len(beats) - 1:
                print(f"  [{b['index']:02d}] {tag:18s} {dur:5.2f}s  {kind}")

        print("\n  concatenating video + audio tracks...")
        silent_v = concat(v_segs, work / "video.mp4", work, "v")
        full_a = build_audio_track(beats, voiceover, work)

        print("  muxing...")
        # music bed: <project>/music.mp3 by default, or --music FILE; --no-music skips.
        # Defensive: no music file present -> behaves exactly as the VO-only mux below.
        music_path = None
        if not args.no_music:
            cand = Path(args.music).expanduser() if args.music else (project / "music.mp3")
            if cand.exists():
                music_path = cand
            elif args.music:
                print(f"  !! --music {cand} not found; assembling without music")
        if music_path:
            import math as _math
            print(f"  music bed: {music_path.name} (VOICE {VOICE_LEVEL} / MUSIC {MUSIC_LEVEL})")
            ad = probe(full_a); md = probe(music_path)
            music_src = music_path
            if md > 0 and md < ad:
                reps = _math.ceil(ad / md)
                mlist = work / "mlist.txt"
                mlist.write_text("".join(f"file '{music_path.resolve()}'\n" for _ in range(reps)))
                looped = work / "music_looped.m4a"
                run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
                     "-c", "copy", str(looped)], "loop music")
                music_src = looped
            run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(full_a), "-i", str(music_src),
                 "-filter_complex",
                 f"[1:a]volume={VOICE_LEVEL}[v];[2:a]volume={MUSIC_LEVEL}[m];"
                 f"[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                 "-map", "0:v:0", "-map", "[a]",
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],
                "mux video+vo+music")
        else:
            run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(full_a),
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out)], "final mux")

        vd, ad, fd = probe(silent_v), probe(full_a), probe(out)
        print(f"\n  video track: {vd:.1f}s   audio track: {ad:.1f}s   final: {fd:.1f}s ({fd/60:.2f} min)")
        if abs(vd - ad) > 1.0:
            print(f"  !! video/audio length differ by {abs(vd-ad):.1f}s — investigate before trusting sync")
        print(f"\nDONE -> {out}")
        print(f"  {n_real} real clips, {n_ph} placeholders")
        if args.placeholders:
            print("\n  This is the PACING CUT: watch it to judge runtime/rhythm before any spend.")
            print("  When the real Mode A clips exist, re-run WITHOUT --placeholders for the real episode.")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
