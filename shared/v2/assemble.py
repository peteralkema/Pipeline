"""shared/v2/assemble.py -- stages 4+5: attach (concat) + music + mux.

Extraction provenance (assemble_episode.py organ donor, decommission map):
  concat_video      -> verbatim (concat demuxer, re-encode, FPS pin)
  _build_music_bed  -> verbatim (random pick from folder, crossfade, loop)
  the sidechain mux -> verbatim (VOICE 1.15 / MUSIC 0.11 ducked baseline,
                       sidechaincompress threshold=0.03:ratio=8:attack=15:
                       release=350, voice-pinned -t, VOICE WINS)

What v2 deletes from the donor BY CONSTRUCTION: durations.json, the index
reverse-map, placeholder plumbing, and the whole make_video_segment fitting
apparatus -- clips arrive from stage 3 already born at their exact measured
length, so stage 4 is a pure concat of the 'main' EDL. The kb-tail logic the
donor grew lives in visuals.py now, where it belongs.

Music: <project_dir>/music/ is the curated folder (rsync'd, gitignored --
curate the folder so random is safe). Empty or absent -> voice-only mux,
which is valid. Idempotent: final_video.mp4 present + project row set -> no-op.
"""
from __future__ import annotations
import json
import math
import random
import shutil
import subprocess
from pathlib import Path

import db as v2db

FPS = 24
VOICE_LEVEL = 1.15
MUSIC_LEVEL = 0.11
MUSIC_TRACKS = 3
MUSIC_CROSSFADE = 2.0


def _run(cmd, desc):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True)
    if res.returncode != 0:
        tail = " | ".join(res.stderr.strip().splitlines()[-6:])
        raise RuntimeError(f"{desc} failed: {tail}")


def _probe(path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


BT709_FLAGS = ["-colorspace", "bt709", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-color_range", "tv"]


def _concat_video(segments, out: Path, work: Path) -> Path:
    listfile = work / "concat_v.txt"
    listfile.write_text("".join(f"file '{Path(s).resolve()}'\n" for s in segments))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
          "-c:v", "libx264", "-preset", "medium", "-crf", "18",
          "-pix_fmt", "yuv420p", "-r", str(FPS), *BT709_FLAGS,
          str(out)], "concat video")
    return out


def _build_music_bed(music_dir: Path, voice_dur: float, work: Path,
                     n_tracks: int = MUSIC_TRACKS,
                     crossfade_s: float = MUSIC_CROSSFADE):
    md = Path(music_dir).expanduser()
    tracks = sorted([p for p in md.glob("*.mp3")] + [p for p in md.glob("*.m4a")]
                    + [p for p in md.glob("*.wav")])
    if not tracks:
        print(f"   music: {md} has no audio files -- assembling without music")
        return None
    n = max(1, min(n_tracks, len(tracks)))
    picked = random.sample(tracks, n)
    print(f"   music: picked {n} of {len(tracks)} -> "
          + ", ".join(p.name for p in picked))
    if len(picked) == 1:
        seq = picked[0]
    else:
        cur = picked[0]
        for k, nxt in enumerate(picked[1:], start=1):
            out = work / f"music_xf_{k}.m4a"
            _run(["ffmpeg", "-y", "-i", str(cur), "-i", str(nxt),
                  "-filter_complex",
                  f"[0][1]acrossfade=d={crossfade_s}:c1=tri:c2=tri[a]",
                  "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out)],
                 f"crossfade music {k}")
            cur = out
        seq = cur
    seq_dur = _probe(seq)
    if seq_dur <= 0:
        print("   music: sequence has zero duration -- assembling without music")
        return None
    if seq_dur >= voice_dur:
        return seq
    reps = math.ceil(voice_dur / seq_dur)
    mlist = work / "music_seq_list.txt"
    mlist.write_text("".join(f"file '{Path(seq).resolve()}'\n"
                             for _ in range(reps)))
    looped = work / "music_bed.m4a"
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
          "-c:a", "aac", "-b:a", "192k", str(looped)], "loop music bed")
    return looped


def run(con, project_dir: Path) -> None:
    proj = con.execute("SELECT * FROM project WHERE id=1").fetchone()
    out = project_dir / "final_video.mp4"
    if proj["final_video_path"] and Path(proj["final_video_path"]).exists():
        print(f"   assemble already done: {proj['final_video_path']} -- no-op")
        return

    missing = v2db.pending(con, "clip_path")
    if missing:
        raise SystemExit(f"stage 'assemble': {len(missing)} beat(s) lack "
                         f"clip_path -- run stage visuals first.")
    voiceover = Path(proj["voiceover_path"] or (project_dir / "voiceover.mp3"))
    if not voiceover.exists():
        raise SystemExit("stage 'assemble': no voiceover.mp3 -- run stage audio.")

    rows = con.execute(
        "SELECT b.clip_path FROM edl e JOIN beats b ON b.id = e.beat_id "
        "WHERE e.edit_name='main' ORDER BY e.position").fetchall()
    segments = [r["clip_path"] for r in rows]
    for s in segments:
        if not Path(s).exists():
            raise SystemExit(f"stage 'assemble': missing clip {s}")

    work = project_dir / "work_assemble"
    work.mkdir(exist_ok=True)
    try:
        print(f"   concatenating {len(segments)} clips (edl 'main')...")
        silent_v = _concat_video(segments, work / "video.mp4", work)
        vid_dur = _probe(silent_v)
        voice_dur = _probe(voiceover)
        print(f"   video {vid_dur:.1f}s | voice {voice_dur:.1f}s | "
              f"diff {abs(vid_dur - voice_dur):.2f}s")

        music_src = _build_music_bed(project_dir / "music", voice_dur, work)

        if music_src:
            md = _probe(music_src)
            if md > 0 and md < voice_dur:
                reps = math.ceil(voice_dur / md)
                mlist = work / "mlist.txt"
                mlist.write_text("".join(f"file '{Path(music_src).resolve()}'\n"
                                         for _ in range(reps)))
                looped = work / "music_looped.m4a"
                _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                      str(mlist), "-c", "copy", str(looped)], "loop music")
                music_src = looped
            print(f"   mux with sidechain duck (VOICE {VOICE_LEVEL} / "
                  f"MUSIC {MUSIC_LEVEL})")
            _run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(voiceover),
                  "-i", str(music_src), "-filter_complex",
                  f"[1:a]volume={VOICE_LEVEL},asplit=2[vmix][vkey];"
                  f"[2:a]volume={MUSIC_LEVEL}[m];"
                  f"[m][vkey]sidechaincompress=threshold=0.03:ratio=8:"
                  f"attack=15:release=350:makeup=1[mduck];"
                  f"[vmix][mduck]amix=inputs=2:normalize=0:duration=first:"
                  f"dropout_transition=0[a]",
                  "-map", "0:v:0", "-map", "[a]",
                  "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                  "-t", f"{voice_dur:.3f}", str(out)], "mux video+voice+music")
        else:
            _run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(voiceover),
                  "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                  "-map", "0:v:0", "-map", "1:a:0",
                  "-t", f"{voice_dur:.3f}", str(out)], "mux video+voice")

        fd = _probe(out)
        con.execute("UPDATE project SET final_video_path=?, "
                    "publish_status='rendered' WHERE id=1", (str(out),))
        v2db.log_generation(con, stage="assemble", model="ffmpeg",
                            result_path=str(out),
                            params_json=json.dumps(
                                {"clips": len(segments),
                                 "final_s": round(fd, 2),
                                 "voice_s": round(voice_dur, 2),
                                 "music": bool(music_src)}))
        con.commit()
        print(f"   final: {fd:.1f}s ({fd/60:.2f} min) -> {out} "
              f"[pinned to voice {voice_dur:.1f}s]")
    finally:
        shutil.rmtree(work, ignore_errors=True)
