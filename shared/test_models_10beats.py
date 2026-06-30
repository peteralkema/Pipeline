# test_models_10beats.py
# Confirmation bake-off before switching QQrew off flux.
# Renders 10 representative beats on nano_banana AND seedream using each beat's
# EXACT resolved prompt (flat-cel suffix + hardened body) -- the same string
# generate_still would send. Standalone: does NOT touch IMAGE_MODEL or the
# pipeline. Pure read-only experiment.
#
# The 10 beats span every class so we test what actually matters:
#   character consistency (Skeptic portraits), figure scenes, empty wides,
#   diagrams, and text beats.
#
# Run from ~/Pipeline with env loaded:
#   set -a; source ~/Pipeline/.env; set +a
#   python shared/test_models_10beats.py
#
# Outputs: qqrew/projects/pregnancy1/model_test/beat<NNN>_<model>.png
import sys, json, pathlib
sys.path.insert(0, "shared")
import fal_client
from recreation_pipeline import (
    load_channel_config, load_rulebook, IMAGE_ENDPOINTS, ASPECT, download,
)
from look_resolver import resolve_look

PROJECT = "qqrew/projects/pregnancy1"
OUT_DIR = pathlib.Path(PROJECT) / "model_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 10 beats chosen to stress every class:
#   1,3   -> Skeptic character portraits  (consistency test: do 1 and 3 match?)
#   40    -> known-good flat character beat (control)
#   99    -> figure scene (ape silhouettes -- must keep figures, go flat)
#   161   -> crowd/social (dinner -- the Pixar-drift beat)
#   4     -> empty landscape wide
#   23,84 -> diagram/object beats (skull, brain+chimp)
#   7     -> text beat ("BORN" in canyon -- spelling + style)
#   213   -> sparse empty wide (the original candlelit-boy beat)
BEATS = [1, 3, 40, 99, 161, 4, 23, 84, 7, 213]

MODELS = ["nano_banana", "seedream"]

def on_update(update):
    pass

def resolved_prompt(image_prompt, anchor):
    config = load_channel_config(strict=True, anchor=anchor)
    style_suffix = resolve_look(anchor, config)["style_suffix"]
    rb = load_rulebook()
    people = rb.get("people_directive", "")
    full = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"
    negative = ", ".join(rb["negative"])
    return full, negative

def render(model, full_prompt, negative, out):
    endpoint = IMAGE_ENDPOINTS[model]
    args = {"prompt": full_prompt, "image_size": ASPECT}
    if negative:
        args["negative_prompt"] = negative
    if model == "flux":
        args["safety_tolerance"] = "5"
    result = fal_client.subscribe(endpoint, arguments=args,
                                  with_logs=False, on_queue_update=on_update)
    images = result.get("images", [])
    if not images:
        print(f"    [{model}] NO IMAGE. keys: {list(result.keys())}")
        return None
    download(images[0]["url"], out)
    return out

def main():
    sb = json.loads((pathlib.Path(PROJECT) / "storyboard.json").read_text())
    anchor = OUT_DIR / "anchor.png"  # resolves to qqrew

    print(f"=== Rendering {len(BEATS)} beats x {len(MODELS)} models "
          f"({len(BEATS)*len(MODELS)} images) ===\n")
    summary = []
    for b in BEATS:
        image_prompt = sb[b - 1]["image_prompt"]
        full, negative = resolved_prompt(image_prompt, anchor)
        body_preview = image_prompt.split("NOT painterly.", 1)[-1].strip()[:60]
        print(f"beat {b:3d}: {body_preview}...")
        for m in MODELS:
            out = OUT_DIR / f"beat{b:03d}_{m}.png"
            try:
                r = render(m, full, negative, out)
                print(f"    [{m:12s}] {'OK' if r else 'FAILED'} -> {out.name}")
                summary.append((b, m, bool(r)))
            except Exception as e:
                print(f"    [{m:12s}] ERROR: {e}")
                summary.append((b, m, False))
        print()

    ok = sum(1 for _,_,s in summary if s)
    print(f"=== DONE: {ok}/{len(summary)} rendered ===")
    print(f"\nPull from {OUT_DIR}/ and compare per beat:")
    print("  - Do beats 1 and 3 (Skeptic) match each other? (character consistency)")
    print("  - Does 99 keep its ape figures, flat? Does 161's crowd go flat?")
    print("  - Are 4/23/84/213 clean flat-cel with no invented figures?")
    print("  - Does 7's text spell 'BORN'? (likely still garbled -- overlay path)")

if __name__ == "__main__":
    main()
