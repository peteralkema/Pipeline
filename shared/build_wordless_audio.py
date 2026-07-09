#!/usr/bin/env python3
"""
build_wordless_audio.py — timing + audio spine for WORDLESS-SPINE channels.

THE CONVERGENCE POINT
---------------------
This is the file that lets a wordless channel rejoin the ordinary pipeline. It emits the
two artifacts assemble_episode.py already consumes, and after this point NOTHING
downstream knows anything unusual happened:

    <project>/durations.json   per-beat {duration, mode, component, source}
    <project>/voiceover.mp3    ONE full-length track: silence with VO clips placed at
                               their beats' timecodes

assemble_episode.py then conforms video to durations.json, mixes its music bed under this
track (amix, MUSIC_LEVEL), and writes final_video.mp4. The assembler is UNTOUCHED. The
music bed is UNTOUCHED. Upload / thumbnails / harvest are UNTOUCHED.

WHY THIS DOES NOT VIOLATE SCRIPT-IS-KING
---------------------------------------
Script is still the sole source of truth and of timing. We have only changed WHERE in the
script the timing lives: for voice-led channels, timing is measured from the narration
(Whisper); for a wordless channel, timing is declared per beat in the beat-sheet. The
picture still conforms to the audio spine; the spine is simply authored rather than
measured. There is no second timing policy hiding anywhere — durations.json remains the
single timing+structure source.

SILENCE IS LEGAL HERE
---------------------
The continuous-narration doctrine (build_audio_script.py: "a beat with no narration is an
AUTHORING ERROR") is correct for voice-led channels and is NOT touched. On this path a
silent beat is a first-class citizen: it gets a real, positive duration from the
beat-sheet and `source: "beatsheet"`. Note assemble_episode.py drops a beat only when
`source == "no_narration"` or `duration <= 0` — we emit neither, so every beat assembles.

DURATION RULE
-------------
    silent beat  -> default_hold
    spoken beat  -> max(default_hold, vo_clip_duration + vo_tail)

A flat default hold is a deliberate v1 baseline: it produces a complete, watchable cut
fast, and its metronomic feel is a DIAGNOSTIC — the stills gate shows exactly which beats
want lengthening or trimming. Pacing is craft; craft comes after traction. The max() guard
means the flat baseline can never truncate a spoken line.

Per-beat overrides always win: a beat may declare `"hold": 4.5` in beats.json.

CHANNEL-AGNOSTIC BY CONSTRUCTION
--------------------------------
Nothing here names a channel. Knobs come from channel.json:

  {
    "timing_source": "beatsheet",
    "default_beat_hold": 6.0,
    "vo_tail": 0.4
  }

Usage (from the channel root, venv active):
  python ../shared/build_wordless_audio.py \
      --beats projects/sausage-heist/beats.json \
      --vo-map projects/sausage-heist/vo_map.json \
      --project projects/sausage-heist \
      --channel-config channel.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_HOLD = 6.0
DEFAULT_VO_TAIL = 0.4
SR = 44100


class WordlessAudioError(Exception):
    pass


def run(cmd: list, desc: str):
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-8:])
        raise WordlessAudioError(f"{desc} failed:\n{tail}")


def ffprobe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def compute_durations(beats, vo_map, default_hold, vo_tail):
    """durations.json payload + the cumulative start time of every beat.

    Spoken beats are never shorter than their line. Silent beats hold. Explicit
    per-beat `hold` always wins (it is the author speaking).
    """
    durations, starts = {}, {}
    t = 0.0
    for b in beats:
        idx = int(b["index"])
        vo = vo_map.get(str(idx))

        if b.get("hold") is not None:
            dur = float(b["hold"])
            src = "beatsheet_explicit"
            if vo and dur < vo["duration"] + vo_tail:
                print(f"  !! beat {idx}: explicit hold {dur:.2f}s is shorter than its "
                      f"VO line ({vo['duration']:.2f}s + {vo_tail}s tail) — the line will "
                      f"be clipped. Lengthen the hold or shorten the line.")
        elif vo:
            dur = max(default_hold, vo["duration"] + vo_tail)
            src = "beatsheet"
        else:
            dur = default_hold
            src = "beatsheet"

        if dur <= 0:
            raise WordlessAudioError(
                f"beat {idx} resolved to a non-positive duration ({dur}). "
                "assemble_episode.py drops such beats."
            )

        starts[idx] = t
        durations[str(idx)] = {
            "duration": round(dur, 3),
            "mode": b.get("mode", "A"),
            "component": b.get("component"),
            "source": src,          # never "no_narration" — that sentinel means error
        }
        t += dur
    return durations, starts, t


def build_voice_track(vo_map, starts, total, out_path: Path, work: Path):
    """One full-length track: silence, with each VO clip placed at its beat's timecode.

    Built with a single ffmpeg graph: an anullsrc base + adelay per clip + amix. The
    result is an ordinary voiceover.mp3 — the assembler mixes its music bed under it.
    """
    if not vo_map:
        # A fully wordless episode is legal. Emit pure silence of the right length so the
        # assembler still has its spine and VOICE-WINS length pin.
        run(["ffmpeg", "-y", "-f", "lavfi", "-i",
             f"anullsrc=channel_layout=stereo:sample_rate={SR}",
             "-t", f"{total:.3f}", "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)],
            "render silent voice track")
        return

    inputs = ["-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={SR}"]
    filters = []
    labels = ["[0:a]"]

    for n, (idx_s, vo) in enumerate(sorted(vo_map.items(), key=lambda kv: int(kv[0])), start=1):
        idx = int(idx_s)
        clip = Path(vo["clip"])
        if not clip.is_file():
            raise WordlessAudioError(f"VO clip missing for beat {idx}: {clip}")
        delay_ms = int(round(starts[idx] * 1000))
        inputs += ["-i", str(clip)]
        filters.append(f"[{n}:a]aresample={SR},adelay={delay_ms}|{delay_ms}[d{n}]")
        labels.append(f"[d{n}]")

    n_in = len(labels)
    graph = ";".join(filters) + ";" + "".join(labels) + \
            f"amix=inputs={n_in}:normalize=0:dropout_transition=0[out]"

    run(["ffmpeg", "-y", *inputs,
         "-filter_complex", graph,
         "-map", "[out]", "-t", f"{total:.3f}",
         "-c:a", "libmp3lame", "-b:a", "192k", "-ar", str(SR),
         str(out_path)],
        "lay VO clips onto the voice track")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--vo-map", default=None, help="vo_map.json from generate_twovoice_vo.py")
    ap.add_argument("--project", required=True)
    ap.add_argument("--channel-config", default="channel.json")
    args = ap.parse_args()

    try:
        cfg = json.loads(Path(args.channel_config).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"!! channel.json did not parse: {e}", file=sys.stderr)
        return 2

    if cfg.get("timing_source") != "beatsheet":
        print('!! channel.json timing_source is not "beatsheet" — this channel uses the '
              "standard narration-timed audio leg. Refusing to run.", file=sys.stderr)
        return 2

    default_hold = float(cfg.get("default_beat_hold", DEFAULT_HOLD))
    vo_tail = float(cfg.get("vo_tail", DEFAULT_VO_TAIL))

    beats = json.loads(Path(args.beats).read_text(encoding="utf-8"))
    if isinstance(beats, dict):
        beats = beats.get("beats", [])
    beats = sorted(beats, key=lambda b: int(b["index"]))

    vo_map = {}
    if args.vo_map and Path(args.vo_map).is_file():
        vo_map = json.loads(Path(args.vo_map).read_text(encoding="utf-8"))

    project = Path(args.project)
    project.mkdir(parents=True, exist_ok=True)

    try:
        durations, starts, total = compute_durations(beats, vo_map, default_hold, vo_tail)
    except WordlessAudioError as e:
        print(f"!! {e}", file=sys.stderr)
        return 1

    dpath = project / "durations.json"
    dpath.write_text(json.dumps(durations, indent=2), encoding="utf-8")

    out = project / "voiceover.mp3"
    work = Path(tempfile.mkdtemp(prefix="wordless_", dir=str(project)))
    try:
        build_voice_track(vo_map, starts, total, out, work)
    except WordlessAudioError as e:
        print(f"!! {e}", file=sys.stderr)
        return 1
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)

    measured = ffprobe_duration(out)
    if measured <= 0:
        print("!! voiceover.mp3 has no measurable duration", file=sys.stderr)
        return 1

    spoken = len(vo_map)
    print(f"OK  {len(beats)} beats · {spoken} spoken · {len(beats)-spoken} silent (legal)")
    print(f"    default hold {default_hold}s · vo tail {vo_tail}s")
    print(f"    planned length {total:.1f}s · voice track {measured:.1f}s")
    print(f"    -> {dpath}")
    print(f"    -> {out}")
    print("\nNEXT:  assemble_episode.py --durations durations.json --voiceover voiceover.mp3 "
          "--project ...   (music bed is added there; assembler untouched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
