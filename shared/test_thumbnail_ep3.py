#!/usr/bin/env python
"""
test_thumbnail_ep3.py  --  render Ep3 thumbnail reaction-face candidates.

"YOU SURVIVED / THIS?" -- shocked Skeptic, hands to face, NO prop, NO echo,
pushed RIGHT with the LEFT third empty for the Anton headline overlay.
Two background colours (alarm red / clinical teal) x two comps each = 4 candidates.

The headline is NOT baked here -- make_thumbnail.py stamps it deterministically over
the empty left third. This only produces the face+background substrate.

RUN (BOX):
    cd ~/Pipeline && source ~/venvs/pipeline/bin/activate && set -a; source .env; set +a
    python shared/test_thumbnail_ep3.py                # 4 renders, ~$0.32
    python shared/test_thumbnail_ep3.py --dry-run      # print prompts, $0

PULL (LAPTOP):
    mkdir -p ~/Downloads/ep3thumb
    scp -P 443 peter@116.202.18.68:'~/Pipeline/qqrew/characters/_thumbtest/*.png' ~/Downloads/ep3thumb/
"""
import argparse, base64, sys, time, urllib.request, os
from pathlib import Path

if sys.platform == "darwin":
    import httpx
    _o = httpx.Client.__init__
    httpx.Client.__init__ = lambda self, *a, **k: _o(self, *a, **{**k, "verify": False})

import fal_client  # noqa: E402

ENDPOINT = "fal-ai/nano-banana-2/edit"
PRICE_1K = 0.08

LOCK = (
    "Keep the EXACT same young woman shown in the reference image: same face, same "
    "blonde tousled shoulder-length wavy hair, same white tee and tan jacket, same "
    "layered gold necklaces. Preserve the reference's semi-realistic cinematic-illustration "
    "art style -- soft warm lighting, painterly rendered skin, clean bold rendering. "
    "Do NOT change her identity or the art style. Render this new scene: "
)

# Two composition variants -- both push her RIGHT, keep the LEFT third empty for a headline.
COMPS = {
    "compA_closeup":
        "EXTREME CLOSE-UP reaction. Her eyes wide with shocked disbelief, both hands "
        "raised up near her cheeks, mouth open in alarm. Her face and hands fill the "
        "RIGHT side of the frame; she is pushed hard to the RIGHT so the entire LEFT "
        "HALF of the image is empty flat background. ",
    "compB_chestup":
        "Chest-up reaction shot. Her eyes wide in shock, both hands flying up toward her "
        "face, shoulders raised, mouth open. She is positioned in the RIGHT THIRD of the "
        "frame, leaving the LEFT TWO-THIRDS as empty flat background with clean negative space. ",
}

# Two flat pop backgrounds.
COLOURS = {
    "red":  "Plain flat saturated alarm-red pop background, bright and bold.",
    "teal": "Plain flat saturated clinical-teal pop background, bright and bold.",
}

TAIL = (" No props, no objects, nothing in her hands, no on-image text, no letters. "
        "Thumbnail composition, high contrast, 16:9 wide.")


def data_uri(p: Path):
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def call(args, tries=3):
    last = None
    for i in range(tries):
        try:
            return fal_client.subscribe(ENDPOINT, arguments=args, with_logs=False)
        except Exception as e:  # noqa: BLE001
            last = e; w = 2 ** i
            print(f"      ! attempt {i+1}/{tries}: {e} -- retry {w}s"); time.sleep(w)
    raise RuntimeError(f"all {tries} failed: {last}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="qqrew/characters/skeptic_ref.png")
    ap.add_argument("--out", default="qqrew/characters/_thumbtest")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    ref = Path(a.ref)
    if not ref.exists():
        sys.exit(f"missing ref: {ref}")
    out = Path(a.out)

    jobs = [(f"{cn}_{comp}", COMPS[comp] + COLOURS[cn])
            for cn in COLOURS for comp in COMPS]

    print("=" * 66)
    print(f"EP3 THUMBNAIL CANDIDATES  ref={ref}  model={ENDPOINT}")
    print(f'headline (overlaid later): "YOU SURVIVED / THIS?"')
    print(f"cost: {len(jobs)} x ${PRICE_1K:.3f} = ${len(jobs)*PRICE_1K:.2f}")
    print("=" * 66)
    for slug, scene in jobs:
        print(f"\n[{slug}]\n  {LOCK + scene + TAIL}")
    if a.dry_run:
        print("\ndry-run: nothing spent.")
        return

    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY not set. Run: set -a; source .env; set +a")
    out.mkdir(parents=True, exist_ok=True)
    uri = data_uri(ref)
    started = time.time()

    for slug, scene in jobs:
        args = {"prompt": LOCK + scene + TAIL, "image_urls": [uri], "num_images": 1,
                "aspect_ratio": "16:9", "output_format": "png",
                "safety_tolerance": "5", "limit_generations": True, "resolution": "1K"}
        t0 = time.time(); print(f"  - {slug} ...", end=" ", flush=True)
        try:
            res = call(args)
            dest = out / f"{slug}.png"
            with urllib.request.urlopen(res["images"][0]["url"], timeout=120) as r:
                dest.write_bytes(r.read())
            print(f"ok {dest.stat().st_size//1024}KB {time.time()-t0:.1f}s")
        except Exception as e:  # noqa: BLE001
            print(f"FAILED: {e}")

    fresh = sorted(p for p in out.glob("*.png") if p.stat().st_mtime >= started - 1)
    print(f"\nWrote {len(fresh)} candidates -> {out}")
    print(f"scp -P 443 peter@116.202.18.68:'~/Pipeline/{out}/*.png' ~/Downloads/ep3thumb/")


if __name__ == "__main__":
    main()
