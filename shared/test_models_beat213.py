# test_models_beat213.py
# One-beat, three-model bake-off for QQrew flat-cel.
# Renders beat 213's EXACT resolved prompt (flat-cel suffix + hardened body)
# on flux, seedream, and nano_banana with correct per-model args.
# Standalone: does NOT touch IMAGE_MODEL or the pipeline. Pure read-only experiment.
#
# Run from ~/Pipeline with env loaded:
#   set -a; source ~/Pipeline/.env; set +a
#   python shared/test_models_beat213.py
#
# Outputs: qqrew/projects/pregnancy1/model_test/test_213_<model>.png
import sys, json, pathlib
sys.path.insert(0, "shared")
import fal_client
from recreation_pipeline import (
    load_channel_config, load_rulebook, IMAGE_ENDPOINTS, ASPECT, download,
)
from look_resolver import resolve_look

PROJECT = "qqrew/projects/pregnancy1"
BEAT_INDEX = 213  # 1-based
OUT_DIR = pathlib.Path(PROJECT) / "model_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = ["flux", "seedream", "nano_banana"]

def on_update(update):
    pass  # quiet

def build_full_prompt():
    """Reconstruct the EXACT prompt generate_still would send for beat 213:
    resolve_look(style_suffix) + image_prompt (+ people_directive)."""
    sb = json.loads((pathlib.Path(PROJECT) / "storyboard.json").read_text())
    image_prompt = sb[BEAT_INDEX - 1]["image_prompt"]
    # anchor on a real still path in this project so the resolver picks qqrew
    anchor = OUT_DIR / "test_213_anchor.png"
    config = load_channel_config(strict=True, anchor=anchor)
    style_suffix = resolve_look(anchor, config)["style_suffix"]
    rb = load_rulebook()
    people = rb.get("people_directive", "")
    if people:
        full = f"{style_suffix}. {image_prompt}, {people}"
    else:
        full = f"{style_suffix}. {image_prompt}"
    negative = ", ".join(rb["negative"])
    return full, negative

def render(model, full_prompt, negative):
    endpoint = IMAGE_ENDPOINTS[model]
    args = {"prompt": full_prompt, "image_size": ASPECT}
    if negative:
        args["negative_prompt"] = negative
    if model == "flux":
        args["safety_tolerance"] = "5"   # flux-only; others reject this arg
    print(f"\n[{model}] -> {endpoint}")
    result = fal_client.subscribe(endpoint, arguments=args,
                                  with_logs=False, on_queue_update=on_update)
    images = result.get("images", [])
    if not images:
        print(f"  [{model}] NO IMAGE returned. Result keys: {list(result.keys())}")
        return None
    out = OUT_DIR / f"test_213_{model}.png"
    download(images[0]["url"], out)
    print(f"  [{model}] OK -> {out}")
    return out

def main():
    full, negative = build_full_prompt()
    print("=== EXACT prompt sent to all three models (beat 213) ===")
    print(full[:400], "..." if len(full) > 400 else "")
    print(f"\n(negative_prompt: {negative[:120]}...)")
    print("\n=== Rendering on 3 models ===")
    results = {}
    for m in MODELS:
        try:
            results[m] = render(m, full, negative)
        except Exception as e:
            print(f"  [{m}] ERROR: {e}")
            results[m] = None
    print("\n=== DONE ===")
    for m in MODELS:
        status = results[m].name if results[m] else "FAILED"
        print(f"  {m:14s} {status}")
    print(f"\nscp these from {OUT_DIR} and eyeball which holds flat-cel.")

if __name__ == "__main__":
    main()
