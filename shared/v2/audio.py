"""shared/v2/audio.py -- stage 1: full-script voiceover.

Extraction provenance (v1 organ donor, decommission map): _chunk_text and
_synthesize_chunk carried verbatim from recreation_pipeline.py; the moviepy
concat pattern likewise. The ONE deliberate v2 change: voice and rate come
from the project row, never from a channel.json walk -- the DB is the truth.

Idempotence: if project.voiceover_path is set and the file exists, no-op.
Output: <project_dir>/voiceover.mp3, path written to project.voiceover_path,
one generations row (stage='audio', full as-sent script kept for the golden
principle: DB + assets = reconstructible).
"""
from __future__ import annotations
import base64
import json
import os
import re
from pathlib import Path

import requests

import db as v2db

INWORLD_TTS_URL = "https://api.inworld.ai/tts/v1/voice"
INWORLD_MODEL = "inworld-tts-2"
INWORLD_MAX_CHARS = 1800
INWORLD_API_KEY = os.getenv("INWORLD_API_KEY")


def _chunk_text(text: str, max_chars: int = INWORLD_MAX_CHARS) -> list:
    """Split at sentence boundaries so long scripts stay under the char limit.
    (Verbatim from recreation_pipeline.py.)"""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current.strip())
    return chunks


def _synthesize_chunk(text: str, voice_id: str, speaking_rate: float) -> bytes:
    """One Inworld call -> raw audio bytes. (Verbatim API shape from
    recreation_pipeline.py; config now injected instead of file-walked.)"""
    if not INWORLD_API_KEY:
        raise SystemExit("INWORLD_API_KEY is not set")
    headers = {"Authorization": f"Basic {INWORLD_API_KEY}",
               "Content-Type": "application/json"}
    payload = {"text": text,
               "voiceId": voice_id,
               "modelId": INWORLD_MODEL,
               "audioConfig": {"audioEncoding": "MP3",
                               "speakingRate": speaking_rate},
               "deliveryMode": "EXPRESSIVE"}
    resp = requests.post(INWORLD_TTS_URL, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    audio_b64 = data.get("audioContent")
    if not audio_b64:
        raise RuntimeError(f"No audio returned. Response keys: {list(data.keys())}")
    return base64.b64decode(audio_b64)


def run(con, project_dir: Path, speaking_rate: float = 1.0) -> Path:
    proj = con.execute("SELECT * FROM project WHERE id=1").fetchone()
    out_path = project_dir / "voiceover.mp3"

    if proj["voiceover_path"] and Path(proj["voiceover_path"]).exists():
        print(f"   audio already done: {proj['voiceover_path']} -- no-op")
        return Path(proj["voiceover_path"])

    beats = con.execute(
        "SELECT narration FROM beats ORDER BY id").fetchall()
    script = "\n\n".join(b["narration"] for b in beats)
    voice_id = proj["voice"] or "Victor"

    chunks = _chunk_text(script)
    print(f"   voice: {voice_id} | {len(script)} chars -> {len(chunks)} chunk(s)")
    if len(chunks) == 1:
        out_path.write_bytes(_synthesize_chunk(chunks[0], voice_id, speaking_rate))
    else:
        part_paths = []
        for i, ch in enumerate(chunks, 1):
            print(f"   narrating chunk {i}/{len(chunks)}...")
            p = project_dir / f"_voice_part_{i:02d}.mp3"
            p.write_bytes(_synthesize_chunk(ch, voice_id, speaking_rate))
            part_paths.append(p)
        from moviepy.editor import AudioFileClip, concatenate_audioclips
        clips = [AudioFileClip(str(p)) for p in part_paths]
        full = concatenate_audioclips(clips)
        full.write_audiofile(str(out_path), verbose=False, logger=None)
        for c in clips:
            c.close()
        for p in part_paths:
            p.unlink(missing_ok=True)

    con.execute("UPDATE project SET voiceover_path=? WHERE id=1", (str(out_path),))
    v2db.log_generation(
        con, stage="audio", model=INWORLD_MODEL, prompt=script,
        params_json=json.dumps({"voiceId": voice_id,
                                "speakingRate": speaking_rate}),
        result_path=str(out_path))
    con.commit()
    print(f"   wrote {out_path}")
    return out_path
