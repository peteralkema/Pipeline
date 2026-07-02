#!/usr/bin/env python3
"""
patch_nb2_text.py -- worlds move to Nano-Banana-2 text-to-image + the no-people guard.

WHY (the photoreal probe, 02 Jul): the reference /edit path (NB2) went 13-for-13
on crew beats; every failure was the nano_banana v1 TEXT path -- the "all-NB2"
decision (banked 01 Jul, _QQrew.md 4b) was never actually implemented for text
beats. Worst failure class: "teaching-graphic" language triggers NB1's
cartoon-explainer-with-presenter genre prior, steamrolling both the photoreal
suffix and "no people". Second fault found while patching: the rulebook's
people_directive is appended to EVERY text prompt AFTER the beat text, actively
summoning humans onto beats that declare "no people/figures/crew".

WHAT (shared/recreation_pipeline.py, 4 edits):
  1. IMAGE_ENDPOINTS gains "nano_banana_2" -> "fal-ai/nano-banana-2" (verified
     against fal docs 02 Jul: text-to-image sibling of the /edit endpoint;
     aspect_ratio string + resolution param; ~$0.08/image).
  2. generate_still text path: skip the people_directive on beats whose prompt
     declares no people/figures/crew/person.
  3. generate_still text path: pass resolution (from reference_resolution, "1K")
     when the endpoint is NB2-family, mirroring the /edit path convention.
  4. _flux_fallback_still: same no-people guard.

AFTER PULLING ON THE BOX, flip the channel (config, not code):
    python3 - <<'EOF'
    import json, pathlib
    p = pathlib.Path("qqrew/channel.json"); d = json.loads(p.read_text())
    d["image_model"] = "nano_banana_2"
    p.write_text(json.dumps(d, indent=2) + "\n"); print("qqrew -> nano_banana_2")
    EOF
(on the LAPTOP, then commit/push/pull -- config discipline as usual.)

Idempotent (sentinel PATCH_NB2_TEXT_APPLIED), anchor-verified, backup to
<file>.pre_nb2_text, py_compiles before writing. No MC restart needed for the
engine change itself, BUT a running batch holds the old module -- relaunch renders.

    python3 patch_nb2_text.py --file shared/recreation_pipeline.py
"""

from __future__ import annotations
import argparse
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

SENTINEL = "PATCH_NB2_TEXT_APPLIED"
EDITS = [['endpoint table', 'IMAGE_ENDPOINTS = {\n    "seedream":     "fal-ai/bytedance/seedream/v3/text-to-image",\n    "nano_banana":  "fal-ai/nano-banana",\n    "flux":         "fal-ai/flux-pro/v1.1",\n}', 'IMAGE_ENDPOINTS = {\n    "seedream":      "fal-ai/bytedance/seedream/v3/text-to-image",\n    "nano_banana":   "fal-ai/nano-banana",\n    "nano_banana_2": "fal-ai/nano-banana-2",   # PATCH_NB2_TEXT_APPLIED: NB2 text-to-image -- same family as the /edit path; reasoning-guided (kills the teaching-graphic=cartoon-presenter genre prior); ~$0.08/img\n    "flux":          "fal-ai/flux-pro/v1.1",\n}'], ['people_directive guard (text path)', '    from look_resolver import resolve_look\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"\n    negative = ", ".join(rb["negative"])\n    # Per-channel image model: channel.json may set "image_model"', '    from look_resolver import resolve_look\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    # PATCH_NB2_TEXT: the people_directive is a face/people enhancer appended to\n    # EVERY text prompt -- on beats that declare themselves people-free ("no\n    # people/figures/crew") it actively summons humans onto clean plates\n    # (graphics, maps, empty wides). Skip it on those beats.\n    _lp = image_prompt.lower()\n    if people and any(t in _lp for t in ("no people", "no figures", "no crew", "no person")):\n        people = ""\n    full_prompt = f"{style_suffix}. {image_prompt}, {people}" if people else f"{style_suffix}. {image_prompt}"\n    negative = ", ".join(rb["negative"])\n    # Per-channel image model: channel.json may set "image_model"'], ['NB2 resolution arg', '    if model == "flux":\n        args = {"prompt": full_prompt, "image_size": ASPECT}\n    else:\n        _asp = config.get("reference_aspect", "16:9")\n        args = {"prompt": full_prompt, "aspect_ratio": _asp}', '    if model == "flux":\n        args = {"prompt": full_prompt, "image_size": ASPECT}\n    else:\n        _asp = config.get("reference_aspect", "16:9")\n        args = {"prompt": full_prompt, "aspect_ratio": _asp}\n        if "nano-banana-2" in endpoint or "nano-banana-pro" in endpoint:\n            # NB2 family: resolution param, mirroring the /edit path (banked 01 Jul)\n            args["resolution"] = config.get("reference_resolution", "1K")'], ['people_directive guard (flux fallback)', '    from look_resolver import resolve_look\n    rb = load_rulebook()\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people\n                   else f"{style_suffix}. {image_prompt}")', '    from look_resolver import resolve_look\n    rb = load_rulebook()\n    style_suffix = resolve_look(out_path, config)["style_suffix"]\n    people = rb.get("people_directive", "")\n    _lp = image_prompt.lower()  # PATCH_NB2_TEXT: same no-people guard as generate_still\n    if people and any(t in _lp for t in ("no people", "no figures", "no crew", "no person")):\n        people = ""\n    full_prompt = (f"{style_suffix}. {image_prompt}, {people}" if people\n                   else f"{style_suffix}. {image_prompt}")']]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="shared/recreation_pipeline.py")
    args = ap.parse_args()
    target = Path(args.file)
    if not target.is_file():
        print(f"ERROR: not found: {target}", file=sys.stderr); return 2
    src = target.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {target}"); return 0
    for label, old, _new in EDITS:
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor '{label}' found {c} times (need exactly 1). "
                  f"Refusing to half-apply.", file=sys.stderr); return 3
    out = src
    for _label, old, new in EDITS:
        out = out.replace(old, new, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: patched result does not compile:\n{e}", file=sys.stderr)
        tmp.unlink(missing_ok=True); return 4
    tmp.unlink(missing_ok=True)
    backup = target.with_suffix(target.suffix + ".pre_nb2_text")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")
    print(f"OK  patched {target}  (backup {backup.name}, {len(EDITS)} edits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
