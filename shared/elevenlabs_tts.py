#!/usr/bin/env python3
"""
elevenlabs_tts.py — ElevenLabs TTS provider for the pipeline audio leg.

Self-contained: no imports from recreation_pipeline. The engine delegates here
when the resolved channel config carries tts_provider: "elevenlabs".

channel.json contract:

  {
    "tts_provider": "elevenlabs",
    "elevenlabs": {
      "voice_id": "REQUIRED — the ElevenLabs voice_id",
      "model_id": "eleven_multilingual_v2",
      "stability": 0.45,
      "similarity_boost": 0.75,
      "style": 0.25,
      "speed": 1.0
    }
  }

Absent tts_provider (or any other value) -> the engine's existing Inworld path
runs untouched. Missing voice_id under elevenlabs -> hard fail, loudly
(resolve identity explicitly, fail loudly, never assume).

RELIABILITY DOCTRINE (banked 23 June) is built in:
  - retry-with-exponential-backoff on every external POST
  - every chunk ffprobe-verified (exists, >0 bytes, decodable, duration > 0)
    before concat — a failed/empty chunk retries then hard-fails; it is
    NEVER silently concatenated as dead air.

Requires: ELEVENLABS_API_KEY in the environment (subprocesses do not inherit
an interactive shell's .env — source it: set -a; source .env; set +a).

Standalone test (from a project dir or anywhere):
  python elevenlabs_tts.py --text-file script.txt --voice-id VOICE_ID --out voiceover.mp3
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

API_BASE = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
OUTPUT_FORMAT = "mp3_44100_128"
MAX_CHUNK_CHARS = 2400          # well under API limits; split on sentence boundaries
STITCH_CONTEXT_CHARS = 500      # previous_text / next_text window for prosody continuity
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 2        # 2, 4, 8, 16, 32
REQUEST_TIMEOUT = 180

DEFAULT_VOICE_SETTINGS = {
    "stability": 0.45,
    "similarity_boost": 0.75,
    "style": 0.25,
    "use_speaker_boost": True,
    "speed": 1.0,
}


class ElevenLabsTTSError(RuntimeError):
    pass


def _api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise ElevenLabsTTSError(
            "ELEVENLABS_API_KEY is not set in the environment. "
            "On the box: set -a; source .env; set +a  (and add the key to .env)."
        )
    return key


def split_into_chunks(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list:
    """Split on sentence boundaries, never exceeding max_chars per chunk."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise ElevenLabsTTSError("Empty narration text — refusing to render silence.")
    # Sentence split that keeps terminators attached.
    sentences = re.findall(r"[^.!?]+[.!?]+(?:\s|$)|[^.!?]+$", text)
    chunks, current = [], ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(s) > max_chars:
            # Pathological sentence: hard-split on commas, then spaces.
            parts = re.split(r"(?<=,)\s", s)
            for p in parts:
                while len(p) > max_chars:
                    cut = p.rfind(" ", 0, max_chars)
                    cut = cut if cut > 0 else max_chars
                    piece, p = p[:cut].strip(), p[cut:].strip()
                    if current:
                        chunks.append(current)
                        current = ""
                    chunks.append(piece)
                if p:
                    if current and len(current) + 1 + len(p) > max_chars:
                        chunks.append(current)
                        current = p
                    else:
                        current = (current + " " + p).strip()
            continue
        if current and len(current) + 1 + len(s) > max_chars:
            chunks.append(current)
            current = s
        else:
            current = (current + " " + s).strip()
    if current:
        chunks.append(current)
    if not chunks:
        raise ElevenLabsTTSError("Chunking produced zero chunks — refusing to continue.")
    return chunks


def _post_with_retry(url: str, payload: dict, params: dict) -> bytes:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(
                url,
                headers={"xi-api-key": _api_key(), "Content-Type": "application/json"},
                params=params,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            if r.status_code == 200 and r.content:
                return r.content
            last_err = f"HTTP {r.status_code}: {r.text[:300]}"
            # 4xx that isn't rate-limit will not heal — fail fast, loudly.
            if 400 <= r.status_code < 500 and r.status_code != 429:
                raise ElevenLabsTTSError(f"ElevenLabs rejected the request ({last_err})")
        except ElevenLabsTTSError:
            raise
        except requests.RequestException as e:
            last_err = f"{type(e).__name__}: {e}"
        wait = BACKOFF_BASE_SECONDS ** attempt
        print(f"  [elevenlabs] attempt {attempt}/{MAX_RETRIES} failed ({last_err}); "
              f"retrying in {wait}s", flush=True)
        time.sleep(wait)
    raise ElevenLabsTTSError(
        f"ElevenLabs TTS failed after {MAX_RETRIES} attempts: {last_err}"
    )


def _ffprobe_duration(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise ElevenLabsTTSError(f"ffprobe failed on {path.name}: {res.stderr[-200:]}")
    try:
        return float(res.stdout.strip())
    except ValueError:
        raise ElevenLabsTTSError(f"ffprobe returned no duration for {path.name}")


def _validate_chunk(path: Path, idx: int, total: int) -> None:
    """PREVENTION half of the reliability doctrine: dead air never ships."""
    if not path.is_file() or path.stat().st_size < 1024:
        raise ElevenLabsTTSError(
            f"Chunk {idx}/{total} is missing or suspiciously small "
            f"({path.stat().st_size if path.is_file() else 0} bytes) — hard fail."
        )
    dur = _ffprobe_duration(path)
    if dur <= 0.2:
        raise ElevenLabsTTSError(
            f"Chunk {idx}/{total} decoded to {dur:.2f}s of audio — dead air, hard fail."
        )


def _render_chunk(chunk: str, prev_text: str, next_text: str,
                  voice_id: str, model_id: str, voice_settings: dict,
                  out_path: Path, idx: int, total: int) -> None:
    payload = {
        "text": chunk,
        "model_id": model_id,
        "voice_settings": voice_settings,
    }
    if prev_text:
        payload["previous_text"] = prev_text[-STITCH_CONTEXT_CHARS:]
    if next_text:
        payload["next_text"] = next_text[:STITCH_CONTEXT_CHARS]
    audio = _post_with_retry(
        f"{API_BASE}/text-to-speech/{voice_id}",
        payload,
        {"output_format": OUTPUT_FORMAT},
    )
    out_path.write_bytes(audio)
    _validate_chunk(out_path, idx, total)
    print(f"  [elevenlabs] chunk {idx}/{total} ok "
          f"({len(chunk)} chars, {out_path.stat().st_size} bytes)", flush=True)


def _concat_chunks(chunk_paths: list, out_path: Path,
                   min_total_duration: float = 1.0) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for p in chunk_paths:
            f.write(f"file '{p.resolve()}'\n")
        list_path = f.name
    try:
        res = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
             "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", str(out_path)],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            raise ElevenLabsTTSError(f"ffmpeg concat failed: {res.stderr[-400:]}")
    finally:
        os.unlink(list_path)
    total_dur = _ffprobe_duration(out_path)
    # Dead air never ships. The FLOOR is caller-supplied because it depends on what is
    # being rendered: a full-episode narration under 1s means the API returned garbage;
    # a single VO line ("Beautiful.") is legitimately shorter than that. Default 1.0
    # preserves the original behaviour for every narration caller.
    if total_dur <= min_total_duration:
        raise ElevenLabsTTSError(
            f"Concatenated voiceover is {total_dur:.2f}s "
            f"(floor {min_total_duration:.2f}s) — something is wrong, hard fail."
        )
    print(f"  [elevenlabs] voiceover assembled: {out_path} ({total_dur:.1f}s)", flush=True)


def resolve_elevenlabs_config(channel_config: dict) -> dict:
    """Fail loudly on a missing voice_id; defaults for everything else."""
    block = channel_config.get("elevenlabs") or {}
    voice_id = (block.get("voice_id") or "").strip()
    if not voice_id:
        raise ElevenLabsTTSError(
            'tts_provider is "elevenlabs" but channel.json has no elevenlabs.voice_id '
            "— refusing to guess a voice (resolve identity explicitly)."
        )
    settings = dict(DEFAULT_VOICE_SETTINGS)
    for k in ("stability", "similarity_boost", "style", "speed"):
        if k in block:
            settings[k] = float(block[k])
    if not (0.7 <= settings["speed"] <= 1.2):
        raise ElevenLabsTTSError(
            f"elevenlabs.speed {settings['speed']} outside ElevenLabs' 0.7-1.2 range."
        )
    return {
        "voice_id": voice_id,
        "model_id": (block.get("model_id") or DEFAULT_MODEL_ID).strip(),
        "voice_settings": settings,
    }


def generate_voiceover_elevenlabs(text: str, out_path, channel_config: dict,
                                  min_total_duration: float = 1.0) -> str:
    """
    The provider entry point the engine delegates to.

    text            full continuous narration (the <out>.txt content)
    out_path        destination voiceover.mp3 (str or Path)
    channel_config  the resolved channel.json dict
    Returns str(out_path) on success; raises ElevenLabsTTSError on any failure.
    """
    out_path = Path(out_path)
    cfg = resolve_elevenlabs_config(channel_config)
    chunks = split_into_chunks(text)
    total = len(chunks)
    print(f"[elevenlabs] rendering {total} chunk(s) with voice {cfg['voice_id']} "
          f"(model {cfg['model_id']})", flush=True)

    workdir = out_path.parent / "_el_chunks"
    workdir.mkdir(parents=True, exist_ok=True)
    chunk_paths = []
    for i, chunk in enumerate(chunks):
        prev_text = chunks[i - 1] if i > 0 else ""
        next_text = chunks[i + 1] if i < total - 1 else ""
        cpath = workdir / f"chunk_{i:04d}.mp3"
        _render_chunk(chunk, prev_text, next_text,
                      cfg["voice_id"], cfg["model_id"], cfg["voice_settings"],
                      cpath, i + 1, total)
        chunk_paths.append(cpath)

    _concat_chunks(chunk_paths, out_path, min_total_duration=min_total_duration)
    return str(out_path)


def main() -> None:
    p = argparse.ArgumentParser(description="Standalone ElevenLabs VO render")
    p.add_argument("--text-file", required=True)
    p.add_argument("--voice-id", required=True)
    p.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    p.add_argument("--out", default="voiceover.mp3")
    args = p.parse_args()
    text = Path(args.text_file).read_text(encoding="utf-8")
    channel_config = {
        "tts_provider": "elevenlabs",
        "elevenlabs": {"voice_id": args.voice_id, "model_id": args.model_id},
    }
    generate_voiceover_elevenlabs(text, args.out, channel_config)


if __name__ == "__main__":
    main()
