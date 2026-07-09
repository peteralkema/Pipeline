#!/usr/bin/env python3
"""
generate_twovoice_vo.py — per-character VO clips for WORDLESS-SPINE channels.

WHY THIS EXISTS
---------------
The standard audio leg (build_audio_script.py -> generate_episode_vo.py) enforces the
CONTINUOUS-NARRATION doctrine: one voice, one unbroken read, every beat speaks, and the
narration is the sole source of timing. That doctrine is correct and load-bearing for the
voice-led channels and is NOT touched here.

A wordless-spine channel (picture + score carry the story; VO is a sparse, removable
flavour layer) is the case that doctrine forbids. Such a channel runs its own legs:

    build_wordless_audio.py   <- writes durations.json + voiceover.mp3
    generate_twovoice_vo.py   <- THIS FILE: renders the per-beat VO clips

and then reconverges on the ordinary artifacts (durations.json + voiceover.mp3), which
assemble_episode.py consumes without knowing anything unusual happened.

CHANNEL-AGNOSTIC BY CONSTRUCTION
--------------------------------
Nothing here is specific to any channel. Speakers are whatever keys exist under
channel.json's `elevenlabs_voices`. Two dogs, three narrators, one grandmother — the
code does not care. The channel's config is the only place identity lives.

REUSE, DON'T REIMPLEMENT
-----------------------
Each line is rendered by the EXISTING public entry point
`elevenlabs_tts.generate_voiceover_elevenlabs(text, out_path, channel_config)`, so this
file inherits, for free and unmodified:
  - sentence-boundary chunking + the API's char limits
  - retry-with-exponential-backoff on every POST
  - per-chunk ffprobe verification (never silently concatenates dead air)
  - loud failure on a missing voice_id
We synthesize a per-character channel_config (a dict shaped exactly like the single-voice
contract) and hand it in. No private functions are called. No TTS code is rewritten.

channel.json contract (additive; the single-voice `elevenlabs` block is untouched):

  {
    "tts_provider": "elevenlabs",
    "timing_source": "beatsheet",
    "elevenlabs_voices": {
      "<speaker>": {
        "voice_id": "REQUIRED",
        "model_id": "eleven_multilingual_v2",
        "stability": 0.5, "similarity_boost": 0.75, "style": 0.5, "speed": 1.0
      },
      ...
    }
  }

BEATS CONTRACT
--------------
Reads beats.json (a list of beat dicts). A beat carries VO via either:
  - an explicit field:  {"vo_speaker": "bentley", "vo_text": "..."}
  - or a tagged line:   {"vo": "[bentley] The humans think the counter is safe."}
Beats with no VO are SILENT AND LEGAL — no warning, no error. That is the whole point of
this path.

OUTPUT
------
  <project>/vo_clips/beat_<NNN>_<speaker>.mp3   one clip per spoken beat
  <project>/vo_map.json                          {beat_index: {clip, duration, speaker, text}}

Silence is legal. Unknown speaker -> hard fail, loudly (resolve identity explicitly,
fail loudly, never assume).

Usage (from the channel root, venv active, ELEVENLABS_API_KEY sourced):
  python ../shared/generate_twovoice_vo.py \
      --beats projects/sausage-heist/beats.json \
      --project projects/sausage-heist \
      --channel-config channel.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TAG_RE = re.compile(r"^\s*\[([A-Za-z0-9_\-]+)\]\s*(.+?)\s*$", re.DOTALL)


class TwoVoiceError(Exception):
    pass


def _ffprobe_duration(path: Path) -> float:
    """Measured duration. A clip we cannot measure is a clip we do not trust."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    try:
        d = float(r.stdout.strip())
    except ValueError:
        raise TwoVoiceError(f"ffprobe returned no duration for {path.name}")
    if d <= 0:
        raise TwoVoiceError(f"{path.name} has zero duration")
    return d


def extract_vo(beat: dict):
    """Return (speaker, text) or (None, None) if this beat is silent.

    Silence is legal on this path. Two accepted shapes:
      explicit:  {"vo_speaker": "...", "vo_text": "..."}
      tagged:    {"vo": "[speaker] text"}
    """
    spk = (beat.get("vo_speaker") or "").strip()
    txt = (beat.get("vo_text") or "").strip()
    if spk and txt:
        return spk.lower(), txt

    raw = (beat.get("vo") or "").strip()
    if not raw:
        return None, None
    m = TAG_RE.match(raw)
    if not m:
        raise TwoVoiceError(
            f"beat {beat.get('index')}: VO line is not speaker-tagged. "
            f"Expected '[speaker] text', got: {raw[:60]!r}"
        )
    return m.group(1).lower(), m.group(2).strip()


def resolve_speaker_config(speaker: str, channel_config: dict) -> dict:
    """Build a single-voice channel_config for this speaker.

    Mirrors resolve_elevenlabs_config's discipline: the voice_id is REQUIRED and its
    absence is a loud failure, never a silent default.
    """
    voices = channel_config.get("elevenlabs_voices") or {}
    if not voices:
        raise TwoVoiceError(
            'channel.json has no "elevenlabs_voices" block — this channel is not '
            "configured for the two-voice wordless path."
        )
    block = voices.get(speaker)
    if block is None:
        known = ", ".join(sorted(voices)) or "(none)"
        raise TwoVoiceError(
            f'unknown speaker "{speaker}" — channel.json knows: {known}'
        )
    if not (block.get("voice_id") or "").strip():
        raise TwoVoiceError(f'speaker "{speaker}" has no voice_id in channel.json')

    # Shape it exactly like the single-voice contract the provider already understands.
    return {"tts_provider": "elevenlabs", "elevenlabs": dict(block)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True, help="beats.json for the episode")
    ap.add_argument("--project", required=True, help="project dir; vo_clips/ + vo_map.json written here")
    ap.add_argument("--channel-config", default="channel.json", help="the channel's channel.json")
    ap.add_argument("--shared", default=None, help="path to shared/ holding elevenlabs_tts.py")
    ap.add_argument("--force", action="store_true", help="re-render clips that already exist")
    args = ap.parse_args()

    shared_dir = Path(args.shared) if args.shared else Path(__file__).resolve().parent
    sys.path.insert(0, str(shared_dir))
    try:
        from elevenlabs_tts import generate_voiceover_elevenlabs
    except Exception as e:
        print(f"!! could not import elevenlabs_tts from {shared_dir}: {e}", file=sys.stderr)
        return 2

    try:
        channel_config = json.loads(Path(args.channel_config).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"!! channel.json did not parse ({args.channel_config}): {e}", file=sys.stderr)
        return 2

    beats = json.loads(Path(args.beats).read_text(encoding="utf-8"))
    if isinstance(beats, dict):
        beats = beats.get("beats", [])

    project = Path(args.project)
    clips_dir = project / "vo_clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    vo_map = {}
    spoken = 0
    silent = 0

    try:
        for b in beats:
            idx = int(b.get("index"))
            speaker, text = extract_vo(b)
            if not speaker:
                silent += 1
                continue  # silence is legal here — no warning, no error

            cfg = resolve_speaker_config(speaker, channel_config)
            out = clips_dir / f"beat_{idx:03d}_{speaker}.mp3"

            if out.exists() and out.stat().st_size > 1000 and not args.force:
                print(f"  beat {idx:3d}  {speaker:<10} (cached)")
            else:
                print(f"  beat {idx:3d}  {speaker:<10} rendering: {text[:48]!r}")
                generate_voiceover_elevenlabs(text, out, cfg)

            dur = _ffprobe_duration(out)   # verify at artifact, always
            vo_map[str(idx)] = {
                "clip": str(out),
                "duration": round(dur, 3),
                "speaker": speaker,
                "text": text,
            }
            spoken += 1

    except TwoVoiceError as e:
        print(f"\n!! {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n!! VO render failed: {e}", file=sys.stderr)
        return 1

    map_path = project / "vo_map.json"
    map_path.write_text(json.dumps(vo_map, indent=2), encoding="utf-8")

    total_vo = sum(v["duration"] for v in vo_map.values())
    speakers = sorted({v["speaker"] for v in vo_map.values()})
    print(f"\nOK  {spoken} spoken beat(s), {silent} silent beat(s) (silence is legal here)")
    print(f"    speakers: {', '.join(speakers) if speakers else '(none)'}")
    print(f"    total VO audio: {total_vo:.1f}s across {spoken} clip(s)")
    print(f"    -> {map_path}")
    print("\nNEXT:  build_wordless_audio.py --beats ... --vo-map vo_map.json --project ...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
