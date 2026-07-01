#!/usr/bin/env python3
"""Stills leg: on a content-refusal, FALL BACK TO FLUX instead of dying.

The behaviour Peter has seen before: a still that "didn't match the beat
directly" because the model returned a softened/safe version. That is flux's
silent safety-downshift (safety_tolerance='5' -> flux returns an altered image
that clears its filter instead of a black reject). NB2 / nano_banana does NOT
do this -- it hard-refuses with `no_media_generated`. So when a beat is rendered
through NB2 (reference /edit OR a nano_banana text beat) and gets refused, we
re-render THAT beat through flux text-to-image, which either renders it or
downshifts to a safe version. Only if flux ALSO refuses do we skip (return None)
for a manual reworded restill.

Adds one helper (_flux_fallback_still) and wraps the fal call in BOTH still
paths (_generate_still_reference and the text branch of generate_still).

Idempotent: verifies anchors, backs up, parses before writing, no-ops if applied.
"""
import ast
import shutil
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "recreation_pipeline.py"
MARKER = "# STILLS-FLUX-FALLBACK applied"

# --- Helper inserted just above generate_still ------------------------------
HELPER_ANCHOR = "def generate_still(image_prompt: str, out_path: Path, reference_images=None) -> Path:"

HELPER_CODE = '''def _flux_fallback_still(image_prompt, out_path, config) -> Path:
    """# STILLS-FLUX-FALLBACK applied
    Last-resort still render through flux. flux-pro/v1.1 with safety_tolerance='5'
    either renders the beat or silently downshifts to a safe (softened) version
    that clears its filter -- unlike nano_banana, which hard-refuses. Used when a
    reference /edit or nano_banana still comes back refused / no-media. Returns the
    written path, or None if flux ALSO refuses (rare -> manual reworded restill).
    """
    from look_resolver import resolve_look
    rb = load_rulebook()
    style_suffix = resolve_look(out_path, config)["style_suffix"]
    people = rb.get("people_directive", "")
    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people
                   else f"{style_suffix}. {image_prompt}")
    negative = ", ".join(rb["negative"])
    endpoint = IMAGE_ENDPOINTS["flux"]
    args = {"prompt": full_prompt, "image_size": ASPECT, "safety_tolerance": "5"}
    if negative:
        args["negative_prompt"] = negative
    try:
        result = fal_client.subscribe(
            endpoint, arguments=args, with_logs=True, on_queue_update=on_update,
        )
        images = result.get("images", [])
    except Exception as _e:
        print(f"  SKIP (flux fallback also refused): {out_path.name} -- "
              f"{type(_e).__name__}. restill with a reworded prompt.")
        return None
    if not images:
        print(f"  SKIP (flux fallback, no media): {out_path.name}. "
              f"restill with a reworded prompt.")
        return None
    download(images[0]["url"], out_path)
    print(f"  flux-fallback rendered: {out_path.name} (softened; eyeball this beat)")
    return out_path


'''

# --- Anchor 1: reference path -----------------------------------------------
REF_ANCHOR = '''    result = fal_client.subscribe(
        endpoint, arguments=args, with_logs=True, on_queue_update=on_update,
    )
    images = result.get("images", [])
    if not images:
        raise RuntimeError(f"No image returned (reference mode). Result: {result}")
    download(images[0]["url"], out_path)
    return out_path'''

REF_REPLACEMENT = '''    try:
        result = fal_client.subscribe(
            endpoint, arguments=args, with_logs=True, on_queue_update=on_update,
        )
        images = result.get("images", [])
    except Exception as _e:  # NB2 content refusal / no_media_generated / transport
        print(f"  reference refusal on {out_path.name} ({type(_e).__name__}); "
              f"falling back to flux.")
        return _flux_fallback_still(scene_prompt, out_path, config)
    if not images:
        print(f"  reference returned no media on {out_path.name}; falling back to flux.")
        return _flux_fallback_still(scene_prompt, out_path, config)
    download(images[0]["url"], out_path)
    return out_path'''

# --- Anchor 2: text-to-image path -------------------------------------------
TXT_ANCHOR = '''    result = fal_client.subscribe(
        endpoint,
        arguments=args,
        with_logs=True,
        on_queue_update=on_update,
    )
    images = result.get("images", [])
    if not images:
        raise RuntimeError(f"No image returned for shot. Result: {result}")
    download(images[0]["url"], out_path)
    return out_path'''

TXT_REPLACEMENT = '''    try:
        result = fal_client.subscribe(
            endpoint,
            arguments=args,
            with_logs=True,
            on_queue_update=on_update,
        )
        images = result.get("images", [])
    except Exception as _e:  # content refusal / no_media_generated / transport
        if model != "flux":
            print(f"  {model} refusal on {out_path.name} ({type(_e).__name__}); "
                  f"falling back to flux.")
            return _flux_fallback_still(image_prompt, out_path, config)
        print(f"  SKIP (flux refused): {out_path.name} -- {type(_e).__name__}. "
              f"restill with a reworded prompt.")
        return None
    if not images:
        if model != "flux":
            print(f"  {model} returned no media on {out_path.name}; falling back to flux.")
            return _flux_fallback_still(image_prompt, out_path, config)
        print(f"  SKIP (flux no media): {out_path.name}. restill with a reworded prompt.")
        return None
    download(images[0]["url"], out_path)
    return out_path'''


def main() -> int:
    src = TARGET.read_text()
    if MARKER in src:
        print("Already patched (STILLS-FLUX-FALLBACK present). No-op.")
        return 0

    for name, anchor in (("helper", HELPER_ANCHOR),
                         ("reference", REF_ANCHOR),
                         ("text-to-image", TXT_ANCHOR)):
        n = src.count(anchor)
        if n != 1:
            print(f"ERROR: {name} anchor found {n} times (expected 1). Aborting, no changes.")
            return 1

    new_src = src.replace(HELPER_ANCHOR, HELPER_CODE + HELPER_ANCHOR, 1)
    new_src = new_src.replace(REF_ANCHOR, REF_REPLACEMENT, 1)
    new_src = new_src.replace(TXT_ANCHOR, TXT_REPLACEMENT, 1)

    try:
        ast.parse(new_src)
    except SyntaxError as e:
        print(f"ERROR: patched source fails to parse: {e}. Aborting, no changes made.")
        return 1

    backup = TARGET.with_suffix(".py.bak_stills_flux_fallback")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new_src)
    print(f"OK patched {TARGET.name} (backup: {backup.name})")
    print("Stills leg now falls back to flux on NB2 refusal; only skips if flux also refuses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
