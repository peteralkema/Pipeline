#!/usr/bin/env python3
"""
stitch_book.py -- v1 multi-hour compilation stitcher (Sacred Soak).

Joins already-rendered final_video.mp4 segments, in the order given, into one
long "book" cut for the browse/all-night lane. It does NOT re-render segments
and it does NOT upload. It exits at the compiled mp4 for manual packaging,
per the batch exit-gate rule.

What it does (v1 doctrine):
  * concatenate segments in the exact order of the manifest (text order, not
    volume order -- you control the order in the manifest)
  * defensively normalise each segment's video (scale/fps/pixfmt/sar) to the
    first segment so xfade cannot fail on a minor mismatch late in a long render
  * crossfade (dissolve) video and audio at every seam so a sleeping listener
    never hears a hard cut / re-greet
  * run ONE loudnorm pass over the whole joined audio track (not per segment)
    so there is no volume step at any seam
  * compute the true stitched runtime and round it DOWN to the nearest half
    hour for the title token ("3 Hours" over a 3h07m cut, never up)
  * emit YouTube chapter timestamps computed on the CROSSFADED timeline
    (naive sums drift once crossfades overlap), first chapter pinned to 0:00
  * write the compiled mp4 + a .chapters.txt sidecar, then stop

Not in v1 (these are re-render jobs, deliberately deferred to v2):
  * omitting each segment's internal settle-open / rest-close
  * volume trending gently downward across the runtime
  * two-pass loudnorm

Manifest format (UTF-8, one segment per line, in final play order):
    /abs/path/to/volI/final_video.mp4 | The Watchers
    /abs/path/to/volII/final_video.mp4 | The Parables
  - text after the first ' | ' is the chapter title
  - if no ' | Title' is given, the chapter title is the parent folder name
  - blank lines and lines starting with '#' are ignored

Usage:
    python3 stitch_book.py --manifest book_enoch.txt --title "The Book of Enoch"
    python3 stitch_book.py --manifest book_enoch.txt --title "The Book of Enoch" \
        --out /path/enoch_complete.mp4 --crossfade 2.5 --workdir /tmp/stitch_enoch

Laptop uses python3; box uses python in the venv. ffmpeg + ffprobe must be on PATH.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def die(msg):
    sys.stderr.write("ERROR: " + msg + "\n")
    sys.exit(1)


def run(cmd):
    """Run a command, streaming nothing; return (rc, stdout, stderr)."""
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def need_tool(name):
    rc, _, _ = run([name, "-version"])
    if rc != 0:
        die("required tool not found on PATH: " + name)


def parse_manifest(path):
    if not os.path.isfile(path):
        die("manifest not found: " + path)
    segments = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if " | " in line:
                seg_path, title = line.split(" | ", 1)
                seg_path = seg_path.strip()
                title = title.strip()
            else:
                seg_path = line
                title = os.path.basename(os.path.dirname(os.path.abspath(seg_path)))
            if not os.path.isfile(seg_path):
                die("segment file not found: " + seg_path)
            segments.append({"path": seg_path, "title": title})
    if len(segments) < 2:
        die("need at least 2 segments to stitch; got %d" % len(segments))
    return segments


def probe(path):
    """Return dict with duration(float sec), width, height, fps(float), has_audio(bool)."""
    rc, out, err = run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ])
    if rc != 0:
        die("ffprobe failed on %s:\n%s" % (path, err))
    data = json.loads(out)
    dur = None
    if "format" in data and data["format"].get("duration"):
        dur = float(data["format"]["duration"])
    width = height = None
    fps = None
    has_audio = False
    for st in data.get("streams", []):
        if st.get("codec_type") == "video" and width is None:
            width = int(st["width"])
            height = int(st["height"])
            rate = st.get("avg_frame_rate") or st.get("r_frame_rate") or "0/1"
            num, _, den = rate.partition("/")
            try:
                den = float(den) if den else 1.0
                fps = float(num) / den if den else 0.0
            except ValueError:
                fps = 0.0
            if dur is None and st.get("duration"):
                dur = float(st["duration"])
        elif st.get("codec_type") == "audio":
            has_audio = True
    if dur is None or width is None:
        die("could not determine duration/video for %s" % path)
    if not fps or fps <= 0:
        fps = 30.0
    return {"duration": dur, "width": width, "height": height, "fps": fps, "has_audio": has_audio}


def fmt_ts(seconds):
    """YouTube chapter timestamp: H:MM:SS if >=1h else M:SS."""
    seconds = int(round(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return "%d:%02d:%02d" % (h, m, s)
    return "%d:%02d" % (m, s)


def fmt_hms(seconds):
    seconds = int(round(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return "%d:%02d:%02d" % (h, m, s)


def round_down_half_hour(seconds):
    """Round total runtime DOWN to nearest 0.5h; return a display token."""
    half_hours = int(seconds // 1800)  # number of whole 30-min blocks
    hours = half_hours / 2.0
    if hours < 1:
        # under an hour: express in minutes, rounded down to 5 min
        mins = int(seconds // 300) * 5
        return "%d Minutes" % mins
    if hours == int(hours):
        n = int(hours)
        return "%d Hour%s" % (n, "" if n == 1 else "s")
    return "%.1f Hours" % hours


def main():
    ap = argparse.ArgumentParser(description="Stitch published final_video.mp4 segments into one multi-hour cut.")
    ap.add_argument("--manifest", required=True, help="path to manifest file (see header for format)")
    ap.add_argument("--title", required=True, help="book/topic title, used for output filename and title-token line")
    ap.add_argument("--out", default=None, help="output mp4 path (default: <slug>_complete.mp4 next to manifest)")
    ap.add_argument("--crossfade", type=float, default=2.5, help="crossfade seconds at each seam (default 2.5)")
    ap.add_argument("--loudnorm-i", type=float, default=-18.0, help="loudnorm integrated target LUFS (sleep-friendly default -18)")
    ap.add_argument("--workdir", default=None, help="scratch dir (default: system temp)")
    ap.add_argument("--force", action="store_true", help="overwrite output if it exists")
    ap.add_argument("--dry-run", action="store_true", help="probe + compute plan/chapters, do NOT encode")
    ap.add_argument("--crf", type=int, default=18, help="x264 CRF (default 18)")
    ap.add_argument("--preset", default="veryfast", help="x264 preset (default veryfast)")
    args = ap.parse_args()

    need_tool("ffmpeg")
    need_tool("ffprobe")

    c = args.crossfade
    if c <= 0:
        die("--crossfade must be > 0 for v1 (hard-cut concat is a separate path)")

    segments = parse_manifest(args.manifest)

    # Probe all segments up front; fail loud before any encode.
    for seg in segments:
        info = probe(seg["path"])
        seg.update(info)
        if not seg["has_audio"]:
            die("segment has no audio track: %s" % seg["path"])
        if seg["duration"] <= c + 0.5:
            die("segment shorter than crossfade (%.1fs <= %.1fs): %s" % (seg["duration"], c, seg["path"]))

    target_w = segments[0]["width"]
    target_h = segments[0]["height"]
    target_fps = segments[0]["fps"]

    # --- timeline math on the CROSSFADED timeline ---
    # total = sum(durations) - c*(N-1)
    # chapter k start (k>=1) begins overlapping at offset_k = sum(d[0..k-1]) - k*c
    #   we mark the chapter at the midpoint of the transition (offset_k + c/2)
    # chapter 0 is pinned to 0:00
    durs = [s["duration"] for s in segments]
    n = len(segments)
    total = sum(durs) - c * (n - 1)

    xfade_offsets = []   # offset arg for each xfade filter (k = 1..n-1)
    chapter_times = [0.0]
    cum = 0.0
    for k in range(1, n):
        cum_before = sum(durs[:k]) - (k - 1) * c   # length of accumulated output before this xfade
        off = cum_before - c
        xfade_offsets.append(off)
        chapter_times.append(off + c / 2.0)

    # enforce strictly increasing, first pinned to 0
    chapter_times[0] = 0.0
    for i in range(1, len(chapter_times)):
        if chapter_times[i] <= chapter_times[i - 1]:
            chapter_times[i] = chapter_times[i - 1] + 1.0

    token = round_down_half_hour(total)

    # output paths
    def slugify(t):
        keep = "abcdefghijklmnopqrstuvwxyz0123456789"
        s = "".join(ch if ch in keep else "-" for ch in t.lower())
        while "--" in s:
            s = s.replace("--", "-")
        return s.strip("-")[:60] or "book"

    slug = slugify(args.title)
    if args.out:
        out_path = os.path.abspath(args.out)
    else:
        out_path = os.path.join(os.path.dirname(os.path.abspath(args.manifest)), slug + "_complete.mp4")
    chapters_path = os.path.splitext(out_path)[0] + ".chapters.txt"

    if os.path.exists(out_path) and not args.force and not args.dry_run:
        die("output exists (use --force to overwrite): " + out_path)

    # --- plan report ---
    print("=" * 68)
    print("STITCH PLAN: %s" % args.title)
    print("=" * 68)
    print("segments        : %d" % n)
    print("crossfade        : %.2fs at each of %d seams" % (c, n - 1))
    print("target video     : %dx%d @ %.3f fps (from segment 1)" % (target_w, target_h, target_fps))
    print("true runtime     : %s (%.1f min)" % (fmt_hms(total), total / 60.0))
    print("title token      : %s   <- round DOWN to half hour" % token)
    print("output mp4       : %s" % out_path)
    print("chapters sidecar : %s" % chapters_path)
    print("-" * 68)
    print("CHAPTERS (paste into description; first is 0:00):")
    chapter_lines = []
    for seg, t in zip(segments, chapter_times):
        line = "%s %s" % (fmt_ts(t), seg["title"])
        chapter_lines.append(line)
        print("  " + line)
    print("-" * 68)
    title_line = "%s \u2014 Scripture to Fall Asleep To | %s (No Adverts)" % (args.title, token)
    print("SUGGESTED TITLE  : %s" % title_line)
    print("=" * 68)

    # write chapters sidecar regardless (useful even on dry-run)
    with open(chapters_path, "w", encoding="utf-8") as fh:
        fh.write(title_line + "\n\n")
        fh.write("\n".join(chapter_lines) + "\n")

    if args.dry_run:
        print("DRY RUN: probe + plan complete, no encode performed.")
        print("chapters written to: %s" % chapters_path)
        return

    # --- build filter_complex ---
    # per-segment video normalisation to the target, then xfade chain
    parts = []
    for i, seg in enumerate(segments):
        parts.append(
            "[%d:v]scale=%d:%d:force_original_aspect_ratio=decrease,"
            "pad=%d:%d:(ow-iw)/2:(oh-ih)/2,fps=%.5f,format=yuv420p,setsar=1[v%d]"
            % (i, target_w, target_h, target_w, target_h, target_fps, i)
        )

    # video xfade chain
    vprev = "[v0]"
    for k in range(1, n):
        vout = "[vx%d]" % k if k < n - 1 else "[vout]"
        parts.append(
            "%s[v%d]xfade=transition=fade:duration=%.3f:offset=%.3f%s"
            % (vprev, k, c, xfade_offsets[k - 1], vout)
        )
        vprev = vout

    # audio acrossfade chain (acrossfade aligns at the join; no offset needed)
    aprev = "[0:a]"
    for k in range(1, n):
        aout = "[ax%d]" % k if k < n - 1 else "[amix]"
        parts.append(
            "%s[%d:a]acrossfade=d=%.3f:c1=tri:c2=tri%s"
            % (aprev, k, c, aout)
        )
        aprev = aout

    # single whole-track loudnorm as the final audio pass
    parts.append("[amix]loudnorm=I=%.1f:TP=-2.0:LRA=11[aout]" % args.loudnorm_i)

    filter_complex = ";".join(parts)

    workdir = args.workdir or tempfile.mkdtemp(prefix="stitch_")
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    fc_path = os.path.join(workdir, "filter_complex.txt")
    with open(fc_path, "w", encoding="utf-8") as fh:
        fh.write(filter_complex)

    cmd = ["ffmpeg", "-y"]
    for seg in segments:
        cmd += ["-i", seg["path"]]
    cmd += [
        "-filter_complex_script", fc_path,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", str(args.crf), "-preset", args.preset, "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        out_path,
    ]

    print("encoding (this is a long offline render for multi-hour cuts)...")
    rc, out, err = run(cmd)
    if rc != 0:
        sys.stderr.write(err[-4000:] + "\n")
        die("ffmpeg encode failed (rc=%d)" % rc)

    # verify output
    got = probe(out_path)
    print("=" * 68)
    print("DONE.")
    print("output           : %s" % out_path)
    print("verified runtime : %s (planned %s)" % (fmt_hms(got["duration"]), fmt_hms(total)))
    print("chapters         : %s" % chapters_path)
    print("title token      : %s" % token)
    print("NEXT: manual package + upload (batch exit-gate: this script does not upload).")
    print("=" * 68)


if __name__ == "__main__":
    main()
