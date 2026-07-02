#!/usr/bin/env python3
"""
make_character_ref.py — render ONE clean character reference sheet for the
reference-render (/edit) path.

The /edit model CLONES the fidelity of whatever reference it is handed. So the
single biggest lever on a recurring character's look is this sheet: a photoreal
sheet => photoreal character in every scene; an illustrated sheet => illustrated.
This renders a clean, front-lit, upper-body portrait from a prompt and writes it
to the channel's characters/ folder (e.g. qqrew/characters/skeptic_ref.png).

Model-agnostic on purpose: the /edit clones appearance regardless of which model
made the sheet. Default is flux-pro (very reliable, clean photoreal faces); pass
--model nano_banana to match the worlds' text-to-image model instead.

ENV: needs FAL_KEY. On the box:  set -a; source ~/Pipeline/.env; set +a

Usage:
  python make_character_ref.py \
    --out qqrew/characters/skeptic_ref.png \
    --prompt "photorealistic cinematic portrait of a late-twenties woman, blonde tousled shoulder-length hair, tan camel jacket over a white tee, layered gold necklaces, bright engaged warm easy half-smile, natural realistic skin, bright high-key studio lighting, vibrant color, clean simple bright background, upper body, facing camera, sharp photographic detail" \
    --aspect 3:4

  # match the worlds' model instead of flux:
  python make_character_ref.py --model nano_banana --out ... --prompt "..."
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

MODELS = {
    "flux":        "fal-ai/flux-pro/v1.1",
    "nano_banana": "fal-ai/nano-banana",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output PNG path (the reference sheet)")
    ap.add_argument("--prompt", required=True, help="the character portrait prompt")
    ap.add_argument("--model", default="flux", choices=sorted(MODELS),
                    help="flux (default, reliable photoreal) or nano_banana (match worlds)")
    ap.add_argument("--aspect", default="3:4",
                    help="aspect ratio string for nano_banana (e.g. 3:4, 1:1, 16:9)")
    args = ap.parse_args()

    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY not set. Run:  set -a; source ~/Pipeline/.env; set +a",
              file=sys.stderr)
        return 2

    try:
        import fal_client
    except ImportError:
        print("ERROR: fal-client not installed (pip install fal-client)", file=sys.stderr)
        return 2

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    endpoint = MODELS[args.model]

    if args.model == "flux":
        arg = {"prompt": args.prompt,
               "image_size": {"width": 1024, "height": 1344},  # portrait, clean face anchor
               "safety_tolerance": "5",          # flux only — stops silent black-PNG rejects
               "num_images": 1, "output_format": "png"}
    else:
        arg = {"prompt": args.prompt, "aspect_ratio": args.aspect,
               "num_images": 1, "output_format": "png"}

    print(f"rendering reference on {endpoint} -> {out}")
    result = fal_client.subscribe(endpoint, arguments=arg, with_logs=False)
    images = result.get("images", [])
    if not images:
        print("ERROR: no image returned (content refusal?) — reword the prompt.",
              file=sys.stderr)
        return 1

    import urllib.request
    urllib.request.urlretrieve(images[0]["url"], str(out))
    kb = out.stat().st_size // 1024
    print(f"OK  reference sheet -> {out}  ({kb} KB)")
    print("Eyeball it: clean front-lit face, right wardrobe, bright expression, no warps.")
    print("If good, re-render the episode — every {character} beat now clones THIS fidelity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
