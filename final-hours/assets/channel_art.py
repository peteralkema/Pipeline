"""
channel_art.py — Render the Final Hours channel avatar and banner via fal.
One-off script. Generates two images at the right aspect ratios:
  - avatar.png  (1:1, for the channel profile picture)
  - banner.png  (ultra-wide, for the YouTube banner)

Run:
    python3 channel_art.py

Output: channel_art/avatar.png and channel_art/banner.png
"""

import os
from pathlib import Path
import fal_client
import requests
from dotenv import load_dotenv

load_dotenv()

# Same cert handling as the rest of the pipeline.
CERT_BUNDLE = os.path.expanduser("~/combined_cacert.pem")
if os.path.exists(CERT_BUNDLE):
    os.environ.setdefault("SSL_CERT_FILE", CERT_BUNDLE)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", CERT_BUNDLE)
    VERIFY = CERT_BUNDLE
else:
    VERIFY = True

if not os.getenv("FAL_KEY"):
    raise SystemExit("FAL_KEY not set in .env")

ENDPOINT = "fal-ai/bytedance/seedream/v3/text-to-image"

OUT_DIR = Path("channel_art")
OUT_DIR.mkdir(exist_ok=True)

AVATAR_PROMPT = (
    "A single tall guttering candle flame, alone in deep shadow, warm "
    "orange-gold light against pure black background, painterly oil-painting "
    "style, cinematic, minimal, symbolic, no other elements, centred "
    "composition, ancient atmosphere, film grain"
)

BANNER_PROMPT = (
    "Ultra-wide cinematic landscape, a distant ancient volcanic mountain "
    "glowing faint orange against a dark dusk sky on the right side, a dark "
    "stone shoreline in the foreground, drifting volcanic ash in the air, "
    "deep shadow filling the left two-thirds of the frame, no people, no "
    "objects, mood of dread and stillness, painterly photorealistic, muted "
    "desaturated palette, 35mm film look, golden hour, room for large text "
    "overlay on the left"
)


def on_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs or []:
            print("   ", log.get("message", ""))


def render(prompt: str, size: dict, out_path: Path):
    print(f"\nRendering {out_path.name} ({size['width']}x{size['height']})...")
    result = fal_client.subscribe(
        ENDPOINT,
        arguments={"prompt": prompt, "image_size": size},
        with_logs=True,
        on_queue_update=on_update,
    )
    url = result["images"][0]["url"]
    resp = requests.get(url, verify=VERIFY)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"OK -> {out_path}")


# Avatar: 1:1 square, will be scaled to 800x800 for upload
render(AVATAR_PROMPT, {"width": 1024, "height": 1024}, OUT_DIR / "avatar.png")

# Banner: ultra-wide. Seedream caps at certain sizes; this gives ~3:1 which
# is close to the YouTube safe-zone aspect. We'll upscale/pad for upload later.
render(BANNER_PROMPT, {"width": 1536, "height": 512}, OUT_DIR / "banner.png")

print("\nDone. Open channel_art/ to review.")
print("Avatar: drop into Clickly or upload directly to YouTube as profile picture.")
print("Banner: needs text overlay (FINAL HOURS + tagline) — do that in Clickly,")
print("then upload to YouTube. YouTube wants 2560x1440 — Clickly export will scale up.")
