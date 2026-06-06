#!/usr/bin/env python3
"""
generate_episode_vo.py — Step 4c / Piece 2b: generate the full-episode Victor read.

Reuses the EXISTING, proven generate_voiceover() from recreation_pipeline.py
(Inworld Victor + sentence-boundary chunking + the 1800-char limit handling).
We do NOT reimplement TTS — we import the function that already works.

Reads the full-episode read (2a's <out>.txt) and writes voiceover.mp3 into the
project folder, where Whisper (then 2c) will measure it.

Run from the channel root with the venv active (needs INWORLD_API_KEY in .env):
  python ../shared/generate_episode_vo.py \
      --text /tmp/ep1_audio.txt \
      --project projects/ep1-the-promise

Then Whisper it (the aligner needs word timestamps):
  whisper projects/ep1-the-promise/voiceover.mp3 --model small \
      --output_format json --output_dir projects/ep1-the-promise/ \
      --word_timestamps True

Then run build_beat_durations.py (2c).
"""
import os, sys, argparse
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="2a's full-episode read (<out>.txt)")
    ap.add_argument("--project", required=True, help="project dir; voiceover.mp3 written here")
    ap.add_argument("--shared", default=None,
                    help="path to shared/ holding recreation_pipeline.py (default: this script's dir)")
    args = ap.parse_args()

    shared_dir = Path(args.shared) if args.shared else Path(__file__).resolve().parent
    sys.path.insert(0, str(shared_dir))
    try:
        import recreation_pipeline as rp
    except Exception as e:
        print(f"!! could not import recreation_pipeline from {shared_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    text = Path(args.text).read_text(encoding="utf-8").strip()
    if not text:
        print("!! empty text file", file=sys.stderr); sys.exit(1)

    project = Path(args.project)
    project.mkdir(parents=True, exist_ok=True)
    out = project / "voiceover.mp3"

    words = len(text.split())
    print(f"generating Victor VO: {words} words ({len(text)} chars) -> {out}")
    print("(reuses recreation_pipeline.generate_voiceover — chunks at sentence boundaries)\n")

    # The channel's voice comes from channel.json via load_channel_config inside
    # generate_voiceover; run this from the Synthetic channel root so it picks
    # Victor (or whatever synthetic/channel.json voices->narrator resolves to).
    rp.generate_voiceover(text, out)

    if out.exists() and out.stat().st_size > 1000:
        print(f"\nOK -> {out}  ({out.stat().st_size/1_000_000:.2f} MB)")
        print("\nNEXT:")
        print(f"  whisper {out} --model small --output_format json \\")
        print(f"      --output_dir {project}/ --word_timestamps True")
        print("  then: build_beat_durations.py --manifest <2a manifest> "
              f"--whisper {project}/voiceover.json --out {project}/durations.json")
    else:
        print(f"\n!! voiceover.mp3 missing or too small — check INWORLD_API_KEY and the Inworld response", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
