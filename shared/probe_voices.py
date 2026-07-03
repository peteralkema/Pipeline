#!/usr/bin/env python3
"""
probe_voices.py — blind A/B voice probe: ElevenLabs candidates vs existing pipeline voice(s).

LAPTOP usage:

  1. List voices available to your account (premade + anything added from Voice Library):
       python3 probe_voices.py --list

  2. Render the probe passage through chosen ElevenLabs voices, optionally include
     pre-rendered mp3s (e.g. Victor via the existing Inworld leg), optionally score
     every sample over the same music bed:

       python3 probe_voices.py \
           --voices VOICE_ID_1,VOICE_ID_2,VOICE_ID_3 \
           --include victor_probe.mp3 \
           --bed path/to/bed.mp3 \
           --outdir probe_out

  3. Listen to probe_out/sample_*.mp3 (scored versions: sample_*_scored.mp3),
     rank them, THEN open probe_out/blind_key.json to see which was which.

Requires: ELEVENLABS_API_KEY env var, `requests`, ffmpeg on PATH.
All samples are loudness-normalized to -16 LUFS so level differences can't bias ranking.
"""

import argparse
import json
import os
import random
import string
import subprocess
import sys
from pathlib import Path

import requests

API_BASE = "https://api.elevenlabs.io/v1"
MODEL_ID = "eleven_multilingual_v2"      # stable narration-quality baseline
OUTPUT_FORMAT = "mp3_44100_128"
VOICE_SETTINGS = {
    "stability": 0.45,       # a little movement, not monotone
    "similarity_boost": 0.75,
    "style": 0.25,           # mild expressive shading for documentary read
    "use_speaker_boost": True,
}
TARGET_LUFS = -16
BED_DUCK_DB = -17            # music bed level under VO when --bed is used

PROBE_TEXT = (
    "November first, seventeen fifty-five. All Saints' Day. "
    "Lisbon is the jewel of the Atlantic, rich on gold from Brazil, "
    "its harbor crowded with ships from every nation on earth. "
    "The churches are full this morning. Tens of thousands of candles "
    "burn before the altars. "
    "At nine forty in the morning, the ground begins to move. "
    "In six minutes, one of the wealthiest cities in Europe is rubble. "
    "The survivors run to the open ground of the waterfront, and then "
    "they see the sea itself pull back, out past the harbor bar, "
    "stranding the ships in the mud. "
    "Some of them understand what that means. Most do not. "
    "The wave that follows is higher than the rooftops. "
    "And then the candles, thousands of them, scattered through the ruins, "
    "begin to burn. The fires will not stop for six days. "
    "This is the story of the morning an empire's capital was erased, "
    "and of the question it forced on the whole of Europe: "
    "if this could happen to Lisbon, on the holiest day of the year, "
    "then nowhere, and no one, is safe."
)


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        die("ELEVENLABS_API_KEY is not set. export ELEVENLABS_API_KEY=... first.")
    return key


def list_voices() -> None:
    r = requests.get(f"{API_BASE}/voices", headers={"xi-api-key": api_key()}, timeout=30)
    if r.status_code != 200:
        die(f"/voices returned {r.status_code}: {r.text[:300]}")
    voices = r.json().get("voices", [])
    if not voices:
        print("No voices on this account yet. Add some from the Voice Library in the UI.")
        return
    print(f"{'voice_id':<24} {'name':<20} labels")
    print("-" * 80)
    for v in voices:
        labels = v.get("labels") or {}
        label_str = ", ".join(f"{k}={val}" for k, val in labels.items())
        print(f"{v.get('voice_id',''):<24} {v.get('name',''):<20} {label_str}")
    print(f"\n{len(voices)} voices. Use --voices id1,id2,... to render the probe.")


def tts_render(voice_id: str, out_path: Path) -> None:
    url = f"{API_BASE}/text-to-speech/{voice_id}"
    payload = {
        "text": PROBE_TEXT,
        "model_id": MODEL_ID,
        "voice_settings": VOICE_SETTINGS,
    }
    r = requests.post(
        url,
        headers={"xi-api-key": api_key(), "Content-Type": "application/json"},
        params={"output_format": OUTPUT_FORMAT},
        json=payload,
        timeout=120,
    )
    if r.status_code != 200:
        die(f"TTS for voice {voice_id} returned {r.status_code}: {r.text[:300]}")
    out_path.write_bytes(r.content)


def voice_name(voice_id: str) -> str:
    try:
        r = requests.get(
            f"{API_BASE}/voices/{voice_id}", headers={"xi-api-key": api_key()}, timeout=30
        )
        if r.status_code == 200:
            return r.json().get("name", voice_id)
    except requests.RequestException:
        pass
    return voice_id


def ffmpeg_ok() -> None:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        die("ffmpeg not found on PATH.")


def loudnorm(src: Path, dst: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-af", f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11",
        "-ar", "44100", "-b:a", "128k",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        die(f"loudnorm failed for {src.name}: {res.stderr[-400:]}")


def mix_over_bed(vo: Path, bed: Path, dst: Path) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", str(vo), "-i", str(bed),
        "-filter_complex",
        f"[1:a]volume={BED_DUCK_DB}dB[bed];"
        f"[0:a][bed]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]", "-ar", "44100", "-b:a", "128k",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        die(f"bed mix failed for {vo.name}: {res.stderr[-400:]}")


def main() -> None:
    p = argparse.ArgumentParser(description="Blind voice probe")
    p.add_argument("--list", action="store_true", help="list voices on the account")
    p.add_argument("--voices", default="", help="comma-separated ElevenLabs voice IDs")
    p.add_argument("--include", default="",
                   help="comma-separated existing mp3 paths to include blind (e.g. Victor)")
    p.add_argument("--bed", default="", help="optional music bed mp3 to mix under every sample")
    p.add_argument("--outdir", default="probe_out")
    args = p.parse_args()

    if args.list:
        list_voices()
        return

    voice_ids = [v.strip() for v in args.voices.split(",") if v.strip()]
    includes = [Path(x.strip()) for x in args.include.split(",") if x.strip()]
    if not voice_ids and not includes:
        die("Nothing to do. Use --list, or provide --voices and/or --include.")
    for path in includes:
        if not path.is_file():
            die(f"--include file not found: {path}")
    bed = Path(args.bed) if args.bed else None
    if bed and not bed.is_file():
        die(f"--bed file not found: {bed}")

    ffmpeg_ok()
    outdir = Path(args.outdir)
    raw_dir = outdir / "_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Render + collect (identity, raw_path)
    entries = []
    for vid in voice_ids:
        name = voice_name(vid)
        raw = raw_dir / f"el_{vid}.mp3"
        print(f"Rendering ElevenLabs voice: {name} ({vid}) ...")
        tts_render(vid, raw)
        entries.append((f"elevenlabs:{name}:{vid}", raw))
    for path in includes:
        entries.append((f"included:{path.name}", path))

    # Shuffle into blind letters
    random.shuffle(entries)
    letters = string.ascii_uppercase
    key = {}
    for i, (identity, raw) in enumerate(entries):
        letter = letters[i]
        sample = outdir / f"sample_{letter}.mp3"
        print(f"Normalizing -> sample_{letter}.mp3")
        loudnorm(raw, sample)
        key[f"sample_{letter}"] = identity
        if bed:
            scored = outdir / f"sample_{letter}_scored.mp3"
            print(f"Scoring    -> sample_{letter}_scored.mp3")
            mix_over_bed(sample, bed, scored)

    key_path = outdir / "blind_key.json"
    key_path.write_text(json.dumps(key, indent=2))
    print("\nDone.")
    print(f"  Samples: {outdir}/sample_*.mp3" + ("  (+ *_scored.mp3)" if bed else ""))
    print(f"  Sealed key: {key_path}  <-- do NOT open until you have ranked the samples")


if __name__ == "__main__":
    main()
