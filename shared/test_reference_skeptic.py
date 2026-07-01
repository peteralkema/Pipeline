#!/usr/bin/env python
"""
test_reference_skeptic.py  --  Q-Qrew character-reference bake-off (the go/no-go probe)

WHAT THIS ANSWERS (in one cheap run, ~$1.90):
  1. Does the SKEPTIC hold as the SAME PERSON across 6 varied scenes when rendered
     FROM her reference image (image-to-image / edit), instead of from a text canon?
  2. ONE reference or TWO?  (single tan-jacket ref  vs  tan+green two-ref conditioning)
  3. Is Nano-Banana-2 enough, or do we need Nano-Banana-Pro?

It is STANDALONE. It does NOT import or touch the pipeline. Nothing here is wired
into generate_still yet -- that patch comes only if this probe clears.

RUN IT (BOX preferred):
    ssh -p 443 peter@116.202.18.68
    source ~/venvs/pipeline/bin/activate
    cd ~/Pipeline
    set -a; source .env; set +a
    python shared/test_reference_skeptic.py

  Refs expected at:  qqrew/characters/skeptic_ref.png  (+ skeptic_ref_green.png for the 2-ref pass)
  Output written to: qqrew/characters/_bakeoff/<condition>__<scene>.png  + manifest.json

FLAGS:
    --refs-dir DIR     where the ref pngs live      (default: qqrew/characters)
    --out DIR          where to write outputs       (default: qqrew/characters/_bakeoff)
    --conditions LIST  comma list of conditions to run (default: nb2_1ref,nb2_2ref,nbpro_1ref)
                       choices: nb2_1ref nb2_2ref nbpro_1ref nb1_1ref
    --resolution R     1K|2K|4K (nb2/pro only)       (default: 1K)
    --dry-run          print the plan + cost, spend nothing

The probe is judged by EYE, not by this script: pull the pngs and ask
"is she the same person in all six, in the cinematic-illustrated style?"
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# --- Mac-only SSL wrinkle (canonical ref §12): monkey-patch before fal imports; no-op on the box.
if sys.platform == "darwin":
    import httpx
    _orig_init = httpx.Client.__init__
    def _patched_init(self, *a, **k):
        k["verify"] = False
        return _orig_init(self, *a, **k)
    httpx.Client.__init__ = _patched_init

import fal_client  # noqa: E402

# ---------------------------------------------------------------------------
# ENDPOINTS + PRICING (verified on fal.ai, 01 Jul 2026). 1K pricing.
# All /edit endpoints share the SAME input shape: prompt + image_urls[] (+ aspect_ratio,
# resolution, num_images, output_format, safety_tolerance, limit_generations).
# ---------------------------------------------------------------------------
EDIT_ENDPOINTS = {
    "nb1":   "fal-ai/nano-banana/edit",       # Gemini 2.5 Flash Image  -- cheapest
    "nb2":   "fal-ai/nano-banana-2/edit",     # Gemini 3.1 Flash Image  -- lead candidate (holds up to 5 people)
    "nbpro": "fal-ai/nano-banana-pro/edit",   # Gemini 3 Pro Image      -- quality escalation
}
PRICE_1K = {"nb1": 0.039, "nb2": 0.08, "nbpro": 0.15}
RES_MULT = {"0.5K": 0.75, "1K": 1.0, "2K": 1.5, "4K": 2.0}

# condition -> (endpoint_key, ref_mode)   ref_mode: "single" or "double"
CONDITIONS = {
    "nb1_1ref":   ("nb1",   "single"),
    "nb2_1ref":   ("nb2",   "single"),
    "nb2_2ref":   ("nb2",   "double"),
    "nbpro_1ref": ("nbpro", "single"),
}

# ---------------------------------------------------------------------------
# THE STYLE + IDENTITY LOCK.
# We condition on the cinematic-illustrated ref, so the STYLE rides along with the
# identity -- we do NOT describe "flat-cel" or "NOT photorealistic" here. We tell it
# to PRESERVE the reference's look and person, then describe only the new scene.
# ---------------------------------------------------------------------------
STYLE_LOCK = (
    "Keep the EXACT same young woman shown in the reference image(s): same face, "
    "same blonde tousled shoulder-length wavy hair, same wardrobe (white tee, layered "
    "gold necklaces, jacket), same dry composed personality. Preserve the reference's "
    "semi-realistic cinematic-illustration art style exactly -- soft warm lighting, "
    "painterly rendered skin, clean rich illustrated backgrounds. Do NOT change her "
    "identity and do NOT change the art style. Render her in this new scene: "
)
STYLE_TAIL = (
    " Rich illustrated background, warm cinematic lighting, 16:9 wide composition, "
    "no on-image text, no letters, no captions."
)

# 6 scenes spanning the QQrew beat classes + the brief's varied-scene spread
# (extreme close / crouch-at-diagram / medium indoor / wide-distant / outdoor full-body / reaction).
SCENES = [
    ("close_up_address",
     "Extreme close-up, she looks straight at the camera with a dry deadpan half-smile, "
     "arms crossed, addressing the viewer directly."),
    ("crouch_diagram",
     "She crouches beside a faint glowing anatomical bone diagram projected on the floor "
     "of a dim museum hall, pointing at it with one hand, curious, three-quarter view."),
    ("arms_crossed_indoor",
     "Medium shot, she stands with arms crossed and one eyebrow raised in wry skepticism, "
     "a bright modern kitchen behind her."),
    ("wide_small_in_frame",
     "Wide establishing shot of a vast ancient Egyptian tomb interior lit by golden light; "
     "she stands small in the lower third, looking up at towering hieroglyph walls."),
    ("outdoor_walk",
     "Full-body shot, she walks outdoors through a sunlit Mughal palace courtyard with "
     "fountains, mid-stride, glancing back over her shoulder."),
    ("reaction_shock",
     "Close-up reaction shot: her eyes wide and mouth open in surprised delight, both hands "
     "raised near her face, plain bright teal pop background."),
]


def data_uri(path: Path) -> str:
    b = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def call_with_retry(endpoint: str, arguments: dict, tries: int = 3):
    """Reliability doctrine (§6): retry-with-backoff on every external call, even in a probe."""
    last = None
    for i in range(tries):
        try:
            return fal_client.subscribe(endpoint, arguments=arguments, with_logs=False)
        except Exception as e:  # noqa: BLE001
            last = e
            wait = 2 ** i
            print(f"      ! attempt {i+1}/{tries} failed: {e} -- retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"all {tries} attempts failed for {endpoint}: {last}")


def download(url: str, dest: Path):
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs-dir", default="qqrew/characters")
    ap.add_argument("--out", default="qqrew/characters/_bakeoff")
    ap.add_argument("--conditions", default="nb2_1ref,nb2_2ref,nbpro_1ref")
    ap.add_argument("--resolution", default="1K", choices=["0.5K", "1K", "2K", "4K"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY not set. Run:  set -a; source .env; set +a")

    refs_dir = Path(args.refs_dir)
    out_dir = Path(args.out)
    ref_primary = refs_dir / "skeptic_ref.png"
    ref_alt = refs_dir / "skeptic_ref_green.png"

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    for c in conditions:
        if c not in CONDITIONS:
            sys.exit(f"unknown condition '{c}'. choices: {list(CONDITIONS)}")

    # ---- pre-flight: refs exist, cost estimate --------------------------------
    if not ref_primary.exists():
        sys.exit(f"missing primary ref: {ref_primary}")
    need_alt = any(CONDITIONS[c][1] == "double" for c in conditions)
    if need_alt and not ref_alt.exists():
        sys.exit(f"a 2-ref condition was requested but {ref_alt} is missing")

    n_scenes = len(SCENES)
    total = 0.0
    print("=" * 70)
    print("SKEPTIC REFERENCE BAKE-OFF -- plan")
    print(f"  refs : {ref_primary}" + (f"  +  {ref_alt}" if need_alt else ""))
    print(f"  out  : {out_dir}")
    print(f"  res  : {args.resolution}   scenes: {n_scenes}")
    print("-" * 70)
    for c in conditions:
        ek, mode = CONDITIONS[c]
        unit = PRICE_1K[ek] * RES_MULT[args.resolution]
        cost = unit * n_scenes
        total += cost
        print(f"  {c:<11} {EDIT_ENDPOINTS[ek]:<28} {mode:<6} "
              f"{n_scenes} img x ${unit:.3f} = ${cost:.2f}")
    print("-" * 70)
    print(f"  TOTAL ESTIMATED SPEND: ${total:.2f}")
    print("=" * 70)

    if args.dry_run:
        print("dry-run: nothing spent.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    started_at = time.time()
    uri_primary = data_uri(ref_primary)
    uri_alt = data_uri(ref_alt) if need_alt else None

    manifest = {"started": started_at, "resolution": args.resolution,
                "style_lock": STYLE_LOCK, "results": []}
    written = []

    for c in conditions:
        ek, mode = CONDITIONS[c]
        endpoint = EDIT_ENDPOINTS[ek]
        image_urls = [uri_primary] if mode == "single" else [uri_primary, uri_alt]
        print(f"\n### condition {c}  ({endpoint}, {mode}-ref)")
        for slug, scene in SCENES:
            prompt = STYLE_LOCK + scene + STYLE_TAIL
            arguments = {
                "prompt": prompt,
                "image_urls": image_urls,
                "num_images": 1,
                "aspect_ratio": "16:9",
                "output_format": "png",
                "safety_tolerance": "5",
                "limit_generations": True,
            }
            if ek in ("nb2", "nbpro"):
                arguments["resolution"] = args.resolution
            t0 = time.time()
            print(f"   - {slug} ...", end=" ", flush=True)
            try:
                res = call_with_retry(endpoint, arguments)
                url = res["images"][0]["url"]
                dest = out_dir / f"{c}__{slug}.png"
                download(url, dest)
                dt = time.time() - t0
                kb = dest.stat().st_size // 1024
                written.append(dest)
                print(f"ok  {kb}KB  {dt:.1f}s")
                manifest["results"].append(
                    {"condition": c, "scene": slug, "endpoint": endpoint,
                     "file": str(dest), "url": url, "kb": kb, "seconds": round(dt, 1),
                     "prompt": prompt})
            except Exception as e:  # noqa: BLE001
                print(f"FAILED: {e}")
                manifest["results"].append(
                    {"condition": c, "scene": slug, "endpoint": endpoint,
                     "error": str(e), "prompt": prompt})

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # ---- FILE-COUNT TRUTH (Hard Rule #4: never trust a log string) ------------
    fresh = sorted(p for p in out_dir.glob("*.png")
                   if p.stat().st_mtime >= started_at - 1)
    print("\n" + "=" * 70)
    print(f"WROTE {len(written)} images this run. Fresh pngs on disk (mtime-checked): {len(fresh)}")
    for p in fresh:
        print(f"   {p.name:<32} {p.stat().st_size//1024:>5}KB  "
              f"{time.strftime('%H:%M:%S', time.localtime(p.stat().st_mtime))}")
    print("=" * 70)
    print("JUDGE BY EYE: pull these and ask -- is she the SAME PERSON across all six,")
    print("in the cinematic-illustrated style? Compare 1-ref vs 2-ref, nb2 vs nbpro.")
    print(f"scp -P 443 peter@116.202.18.68:~/Pipeline/{out_dir}/*.png ~/Downloads/skeptic_bakeoff/")


if __name__ == "__main__":
    main()
