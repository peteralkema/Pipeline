#!/usr/bin/env python
"""
test_reference_scenes.py  --  render the SKEPTIC reference across a custom scene set.

Standalone (touches nothing in the pipeline). Renders skeptic_ref.png through
fal-ai/nano-banana-2/edit across six specified scenes. Five suppress on-image text;
scene 6 (the 3D bar chart) ALLOWS text so the "10%/30%/90%" labels render -- that
scene doubles as a test of whether NB2 can bake clean labelled charts (i.e. whether
QQrew needs Remotion for number beats at all).

RUN (BOX):
    cd ~/Pipeline && source ~/venvs/pipeline/bin/activate && set -a; source .env; set +a
    python shared/test_reference_scenes.py --dry-run     # print full prompts, spend $0
    python shared/test_reference_scenes.py               # render (6 x $0.08 = ~$0.48)

PULL (LAPTOP):
    mkdir -p ~/Downloads/scenetest
    scp -P 443 peter@116.202.18.68:'~/Pipeline/qqrew/characters/_scenetest/*.png' ~/Downloads/scenetest/
"""
import argparse, base64, json, sys, time, urllib.request
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
    "blonde tousled shoulder-length wavy hair, same wardrobe (white tee, layered gold "
    "necklaces, tan jacket), same dry composed personality. Preserve the reference's "
    "semi-realistic cinematic-illustration art style exactly -- soft warm lighting, "
    "painterly rendered skin, clean rich illustrated backgrounds. Do NOT change her "
    "identity and do NOT change the art style. Bright, curious, wry QQrew register, "
    "she is teaching the viewer. Render her in this new scene: "
)
TAIL_NOTEXT = (" Rich illustrated background, warm cinematic lighting, 16:9 wide "
              "composition, no on-image text, no letters, no captions, no legible signage.")
TAIL_TEXT = (" Rich illustrated background, warm cinematic lighting, 16:9 wide composition, "
             "clean modern infographic look.")

# (slug, scene, allow_text)
SCENES = [
    ("1_stadium_ref",
     "She stands on the centre line of a massive roaring modern soccer stadium, one foot "
     "resting on top of a soccer ball, arms crossed, chin up with a confident wry look like "
     "a referee about to start the match. Behind her, vast tiered crowds cheer and wave "
     "colourful country flags under bright floodlights. Dynamic and energetic.",
     False),
    ("2_colosseum_narrator",
     "She crouches low on the sandy floor inside the ancient Roman Colosseum, one hand "
     "touching the sand, looking toward the viewer mid-explanation. Behind her a chariot "
     "races past in a motion blur and vast tiered crowds roar beneath tall imperial Roman "
     "banners and eagle standards. Warm dusty golden light. Thoughtful and atmospheric, "
     "no gore, no violence.",
     False),
    ("3_mars_rover",
     "She crouches on her haunches on the rocky red surface of Mars beside a modern NASA "
     "rover, one hand pointing to the rover's articulated suspension and large treaded "
     "wheels, explaining to the viewer. Stylised illustrated Mars terrain and sky, not "
     "photorealistic. Curious, bright teaching energy.",
     False),
    ("4_times_square",
     "She stands in a stylised illustrated Times Square at night, glowing abstract "
     "billboards and coloured lights behind her (no readable words), diverse crowds "
     "streaming past in the background. She gestures with one hand, explaining to the "
     "viewer. Bright and energetic.",
     False),
    ("5_buckingham_guard",
     "She stands inside the forecourt of Buckingham Palace where the changing of the guard "
     "takes place, ceremonial guards in red tunics and tall black bearskin hats lined up "
     "behind her, a blurred public crowd peering in through the far railings. One hand on "
     "her hip, the other pointing, explaining something to the viewer. Bright daylight.",
     False),
    ("6_bar_chart_3d",
     "She stands inside a glowing three-dimensional data space on a grid floor. Three tall "
     "3D bar-chart columns rise out of the ground beside her, labelled left to right "
     "\"10%\", \"30%\", \"90%\" -- the left bar short, the middle taller, the right bar "
     "tallest. She points up at the tallest right-hand bar, explaining the difference to "
     "the viewer.",
     True),
]


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
    ap.add_argument("--out", default="qqrew/characters/_scenetest")
    ap.add_argument("--resolution", default="1K")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    ref = Path(a.ref)
    if not ref.exists():
        sys.exit(f"missing ref: {ref}")
    out = Path(a.out)

    print("=" * 70)
    print(f"SKEPTIC CUSTOM SCENES  ref={ref}  model={ENDPOINT}  res={a.resolution}")
    print(f"cost: {len(SCENES)} x ${PRICE_1K:.3f} = ${len(SCENES)*PRICE_1K:.2f}")
    print("=" * 70)
    for slug, scene, allow in SCENES:
        tail = TAIL_TEXT if allow else TAIL_NOTEXT
        print(f"\n[{slug}]  (text {'ALLOWED' if allow else 'suppressed'})")
        print("  " + (LOCK + scene + tail))
    if a.dry_run:
        print("\ndry-run: nothing spent. Tweak wording in SCENES and re-run.")
        return

    if not __import__("os").environ.get("FAL_KEY"):
        sys.exit("FAL_KEY not set. Run: set -a; source .env; set +a")
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    uri = data_uri(ref)

    for slug, scene, allow in SCENES:
        tail = TAIL_TEXT if allow else TAIL_NOTEXT
        args = {"prompt": LOCK + scene + tail, "image_urls": [uri], "num_images": 1,
                "aspect_ratio": "16:9", "output_format": "png",
                "safety_tolerance": "5", "limit_generations": True,
                "resolution": a.resolution}
        t0 = time.time(); print(f"  - {slug} ...", end=" ", flush=True)
        try:
            res = call(args)
            url = res["images"][0]["url"]
            dest = out / f"{slug}.png"
            with urllib.request.urlopen(url, timeout=120) as r:
                dest.write_bytes(r.read())
            print(f"ok {dest.stat().st_size//1024}KB {time.time()-t0:.1f}s")
        except Exception as e:  # noqa: BLE001
            print(f"FAILED: {e}")

    fresh = sorted(p for p in out.glob("*.png") if p.stat().st_mtime >= started - 1)
    print("\n" + "=" * 70)
    print(f"Fresh pngs (mtime-checked): {len(fresh)}")
    for p in fresh:
        print(f"   {p.name:<26} {p.stat().st_size//1024:>5}KB")
    print(f"scp -P 443 peter@116.202.18.68:'~/Pipeline/{out}/*.png' ~/Downloads/scenetest/")


if __name__ == "__main__":
    main()
