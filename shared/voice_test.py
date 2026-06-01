"""
voice_test.py — Test an Inworld voice against a short passage.

Self-contained — no dependency on the recreation_pipeline. Used to audition new
voices before committing them as the channel default in channel.json.

Usage:
    python3 shared/voice_test.py Reed
    python3 shared/voice_test.py Ashley --text "Custom passage here"
    python3 shared/voice_test.py Reed --out my_reed_sample.mp3

Saves output to voice_test_<voice_id>.mp3 in the current directory by default.
Open it with `open voice_test_Reed.mp3` on macOS to play.

If the voice doesn't exist or the ID is wrong, you'll get a clean error
pointing you to https://studio.inworld.ai/ to check the catalogue.
"""

import os
import sys
import base64
import argparse
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load the project-root .env (one level up from shared/), same convention as
# the pipeline. Falls back to default search if not found.
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

INWORLD_TTS_URL = "https://api.inworld.ai/tts/v1/voice"
INWORLD_MODEL = "inworld-tts-2"
INWORLD_API_KEY = os.getenv("INWORLD_API_KEY")

# Zscaler / ABB cert fix (same as the pipeline)
_cert = os.path.expanduser("~/combined_cacert.pem")
VERIFY = _cert if os.path.exists(_cert) else True


# A short passage in the actual register this voice will narrate. Tests the
# voice on the kind of content it will produce, not on generic "the quick
# brown fox" text. Three sentence lengths, one number, one human name.
DEFAULT_TEXT = (
    "I want to tell you about six minutes. The most important six minutes in Sarah's career. "
    "She walked into a meeting room earning fifty-eight thousand. She walked out earning a hundred and twenty. "
    "It was not luck. It was three small choices she made in those six minutes."
)


def main():
    ap = argparse.ArgumentParser(description="Audition an Inworld voice with a short test passage.")
    ap.add_argument("voice_id", help="Inworld voice ID to test, e.g. 'Reed', 'Ashley', 'Victor'")
    ap.add_argument("--text", default=DEFAULT_TEXT,
                    help="Test passage. Defaults to a Success Coach opening passage.")
    ap.add_argument("--out", default=None,
                    help="Output mp3 path. Defaults to voice_test_<voice_id>.mp3 in CWD.")
    args = ap.parse_args()

    if not INWORLD_API_KEY:
        sys.exit("INWORLD_API_KEY not set in environment. Check .env at project root.")

    out_path = Path(args.out or f"voice_test_{args.voice_id}.mp3")

    headers = {
        "Authorization": f"Basic {INWORLD_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": args.text,
        "voiceId": args.voice_id,
        "modelId": INWORLD_MODEL,
        "audioConfig": {"audioEncoding": "MP3"},
        "deliveryMode": "EXPRESSIVE",
    }

    print(f"Synthesising with voice '{args.voice_id}' on model {INWORLD_MODEL}...")
    resp = requests.post(INWORLD_TTS_URL, json=payload, headers=headers, verify=VERIFY)

    if resp.status_code != 200:
        print(f"FAIL [{resp.status_code}]: {resp.text[:500]}")
        if resp.status_code in (400, 404):
            print()
            print("The voice ID may not exist on this model, or be spelled differently.")
            print("Check the current Inworld voice catalogue here:")
            print("  https://studio.inworld.ai/")
            print()
            print("Common voice IDs that have worked before: Victor, Ashley.")
        sys.exit(1)

    data = resp.json()
    audio_b64 = data.get("audioContent")
    if not audio_b64:
        sys.exit(f"No audio returned. Response keys: {list(data.keys())}")

    out_path.write_bytes(base64.b64decode(audio_b64))
    size_kb = out_path.stat().st_size / 1024
    duration_estimate = len(args.text.split()) / 135 * 60
    print(f"OK saved {out_path} ({size_kb:.0f} KB, ~{duration_estimate:.0f}s)")
    print(f"Play it: open '{out_path}'")


if __name__ == "__main__":
    main()
