#!/usr/bin/env python3
"""
make_music.py — Tier-2 music: ONE loopable instrumental bed per episode, generated
from a prompt Claude writes after READING this episode's narration.

The model (script-craft Part II in spirit): the music is ONE continuous bed laid under
the ONE continuous voice. No regions, no music_category, no crossfades — that complexity
served within-episode variety, which isn't worth the timing-coupling. Variety lives
ACROSS episodes (each script gets its own Claude-written prompt), simplicity WITHIN one.

Three stages:
  1. READ the narration (the continuous read from the audio leg, <project>/<vo>.txt,
     or fall back to concatenating beats.json narration).
  2. Claude (claude-sonnet-4-6) writes ONE fal music prompt tuned to this episode's mood
     — instrumental, loopable (no hard intro/outro, no resolving cadence), sits under a
     narrator, never competes. Channel default_music_prompt is given as house-style context.
  3. fal (fal-ai/elevenlabs/music) generates ONE bed at the voice length (capped to the
     model max) -> <project>/music.mp3. Sanity-checked (exists, non-trivial size/length).

The assembler / convergence leg then muxes music.mp3 under the voice (looping if shorter).

Reuses the repo's existing anthropic + fal_client setup (same as recreation_pipeline.py):
env ANTHROPIC_API_KEY + FAL_KEY, the SSL cert vars already exported.

Usage (from repo root):
  python3 shared/make_music.py \
      --project final-hours/projects/test-fh-modea \
      --voiceover final-hours/projects/test-fh-modea/voiceover.mp3 \
      --narration final-hours/projects/test-fh-modea/test_audio.txt \
      --channel-json final-hours/channel.json
  # then assemble WITH music (convergence ctx['music']=True, or assemble --music <project>/music.mp3)
"""
import os
import sys
import json
import argparse
import subprocess
import urllib.request
from pathlib import Path

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"
FAL_MUSIC_MODEL = "fal-ai/elevenlabs/music"
MODEL_MAX_MS = 600_000          # ElevenLabs music: up to 10 min in one call
MIN_OK_BYTES = 20_000           # a real bed is tens of KB+; smaller = failed/empty


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def read_narration(narration_path, beats_path):
    """The episode's spoken text — the mood source. Prefer the audio leg's continuous
    read (<out>.txt); fall back to concatenating beats.json narration."""
    if narration_path and Path(narration_path).exists():
        txt = Path(narration_path).read_text(encoding="utf-8").strip()
        if txt:
            return txt
    if beats_path and Path(beats_path).exists():
        beats = json.load(open(beats_path, encoding="utf-8"))
        if isinstance(beats, dict):
            beats = beats.get("beats", [])
        return " ".join((b.get("narration") or "").strip() for b in beats).strip()
    return ""


def write_music_prompt(narration, channel_default, channel_name):
    """Stage 2: Claude reads the narration and writes ONE fal music prompt for the bed.
    Returns a short prose prompt string (genre, mood, instrumentation; instrumental;
    loopable; sits under a narrator). Channel default is house-style context, not a cage."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    house = f'\nThe channel\'s house music style (for consistency, adapt — do not copy verbatim):\n"{channel_default}"\n' if channel_default else ""
    sys_prompt = (
        "You are a music supervisor for a faceless documentary YouTube channel. You write ONE "
        "concise text-to-music prompt (for ElevenLabs Music on fal) for a single instrumental "
        "underscore bed that plays under a narrator for an entire episode.\n\n"
        "Hard requirements for the bed you describe:\n"
        "- INSTRUMENTAL only. No vocals, no lyrics, no spoken word.\n"
        "- It must SIT UNDER a narrator and never compete: low, restrained, no busy melody, "
        "no sudden hits, no loud drops.\n"
        "- LOOPABLE: even, continuous texture; no hard intro or outro, no big resolving cadence "
        "that would make a repeat obvious.\n"
        "- Mood must fit THIS episode's content (read the narration).\n\n"
        "Output ONLY the prompt text itself — one paragraph, 2-4 sentences, no preamble, no "
        "quotes, no labels. It will be passed straight to the music model."
    )
    user = (
        f"Channel: {channel_name}.{house}\n"
        f"Episode narration (read it for mood, pacing, subject):\n\"\"\"\n{narration}\n\"\"\"\n\n"
        "Write the single instrumental, loopable, under-narration music prompt now."
    )
    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=400,
        system=sys_prompt,
        messages=[{"role": "user", "content": user}],
    )
    prompt = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
    # strip stray wrapping quotes if the model added them
    if len(prompt) > 1 and prompt[0] in "\"'" and prompt[-1] == prompt[0]:
        prompt = prompt[1:-1].strip()
    return prompt


def generate_bed(prompt, length_ms, out_path):
    """Stage 3: fal generates ONE instrumental bed at length_ms -> out_path (mp3)."""
    import fal_client

    def on_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in (getattr(update, "logs", None) or []):
                msg = log.get("message") if isinstance(log, dict) else None
                if msg:
                    print("   fal:", msg)

    print(f"   generating bed: {length_ms} ms, instrumental, model={FAL_MUSIC_MODEL}")
    result = fal_client.subscribe(
        FAL_MUSIC_MODEL,
        arguments={
            "prompt": prompt,
            "music_length_ms": int(length_ms),
            "instrumental": True,
            "output_format": "mp3_44100_128",
        },
        with_logs=True,
        on_queue_update=on_update,
    )
    # result shape: {"audio": {"url": ...}} (fal audio models return an 'audio' file dict)
    audio = (result or {}).get("audio") or {}
    url = audio.get("url")
    if not url:
        # some models nest differently; try a couple of fallbacks before giving up
        for k in ("audio_file", "file", "output"):
            v = (result or {}).get(k)
            if isinstance(v, dict) and v.get("url"):
                url = v["url"]; break
    if not url:
        raise SystemExit(f"!! fal returned no audio url. Raw result keys: {list((result or {}).keys())}")
    urllib.request.urlretrieve(url, str(out_path))
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="project dir; music.mp3 written here")
    ap.add_argument("--voiceover", default=None, help="voiceover.mp3 (to size the bed to the voice)")
    ap.add_argument("--narration", default=None, help="continuous read .txt (mood source)")
    ap.add_argument("--beats", default=None, help="beats.json fallback for narration")
    ap.add_argument("--channel-json", default=None, help="channel.json for house default_music_prompt + name")
    ap.add_argument("--model", default=FAL_MUSIC_MODEL, help="fal music model id (swappable)")
    ap.add_argument("--length-ms", type=int, default=None, help="override bed length (default: voice length)")
    ap.add_argument("--print-prompt-only", action="store_true",
                    help="stage 1+2 only: write the Claude prompt to stdout, DO NOT call fal (free)")
    args = ap.parse_args()

    global FAL_MUSIC_MODEL
    FAL_MUSIC_MODEL = args.model

    if not ANTHROPIC_API_KEY:
        sys.exit("!! ANTHROPIC_API_KEY not set.")

    proj = Path(args.project)
    out_path = proj / "music.mp3"

    channel_default, channel_name = "", "this channel"
    if args.channel_json and Path(args.channel_json).exists():
        cfg = json.load(open(args.channel_json, encoding="utf-8"))
        channel_default = cfg.get("default_music_prompt", "")
        channel_name = cfg.get("name", channel_name)

    narration = read_narration(args.narration, args.beats)
    if not narration:
        sys.exit("!! no narration found (need --narration <out>.txt or --beats beats.json).")
    print(f"   narration: {len(narration.split())} words read for mood")

    prompt = write_music_prompt(narration, channel_default, channel_name)
    print("\n   === Claude's music prompt ===")
    print("   " + prompt.replace("\n", "\n   "))
    print()

    if args.print_prompt_only:
        print("   (--print-prompt-only: stopping before fal. No spend.)")
        return

    # Size the bed to the voice (capped to the model max), unless overridden.
    if args.length_ms:
        length_ms = min(args.length_ms, MODEL_MAX_MS)
    else:
        vdur = probe_duration(args.voiceover) if args.voiceover else 0.0
        # add a small tail so the bed covers the voice even with rounding; cap to model max
        length_ms = min(int((vdur + 2.0) * 1000) if vdur > 0 else 60_000, MODEL_MAX_MS)
    print(f"   bed length: {length_ms} ms (voice {'~%.1fs' % (length_ms/1000)})")

    generate_bed(prompt, length_ms, out_path)

    if not out_path.exists() or out_path.stat().st_size < MIN_OK_BYTES:
        sz = out_path.stat().st_size if out_path.exists() else 0
        sys.exit(f"!! generated music.mp3 is missing or too small ({sz} bytes) — likely a failed "
                 f"generation. NOT trusting it. (model rejection or empty output.)")
    dur = probe_duration(out_path)
    print(f"\nOK -> {out_path}  ({out_path.stat().st_size/1024:.0f} KB, {dur:.1f}s)")
    print("   Convergence/assemble will mux this under the voice (looping if shorter).")


if __name__ == "__main__":
    main()
