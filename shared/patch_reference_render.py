#!/usr/bin/env python3
"""
patch_reference_render.py  --  add per-channel REFERENCE render mode to the pipeline.

WHAT IT DOES (non-breaking, per-channel, same shape as the image_model switch):
  - generate_still() gains an optional `reference_images` arg and, when the channel's
    channel.json sets  "render_mode": "reference"  AND a beat resolved to one or more
    character reference images, renders via a fal /edit endpoint conditioned on those
    refs (identity + art style preserved from the reference). All other channels omit
    render_mode -> unchanged text-to-image path.
  - cmd_stills() detects which {skeptic}/{driver}/{brain} canon tags a beat uses (on the
    RAW beat, before canon expansion), maps them to ref files via channel.json
    "reference_map", and passes them down. A crew-absent beat falls back to an optional
    "reference_style_anchor" plate so the whole video shares one look; if none is set it
    falls through to today's text path.
  - cmd_restill() reads the stored per-shot refs so single-shot reshoots stay in ref mode.
  - storyboard.json now carries "_reference_images" per shot.

DISCIPLINE:
  - Idempotent: re-running is a no-op (checks a marker).
  - Verifies every anchor exists before writing; fails loud if the source drifted.
  - Backs up to recreation_pipeline.py.bak-<ts> and py_compile-gates before committing.

USAGE (LAPTOP, then git -> box pull):
  cd ~/Projects/Pipeline
  python3 shared/patch_reference_render.py            # apply
  python3 shared/patch_reference_render.py --check    # dry-run: report only
"""
import argparse
import py_compile
import re
import sys
import time
from pathlib import Path

TARGET = Path(__file__).parent / "recreation_pipeline.py"
MARKER = "_generate_still_reference"   # presence => already patched

# ---------------------------------------------------------------------------
# The helper block inserted just after the "Step 2" banner comment.
# ---------------------------------------------------------------------------
HELPER_BLOCK = '''
def _ref_data_uri(path) -> str:
    """Read a local image file and return it as a base64 data URI for fal image_urls."""
    import base64 as _b64
    from pathlib import Path as _P
    return "data:image/png;base64," + _b64.b64encode(_P(path).read_bytes()).decode("ascii")


# Identity + style lock for REFERENCE rendering. Conditioning on the cinematic
# reference makes the model preserve BOTH the character(s) and the art style, so we
# deliberately do NOT send the text-path style_suffix or negatives here.
REFERENCE_PROMPT_LOCK = (
    "Use the reference image(s) as the exact visual template. Preserve their art "
    "style precisely -- semi-realistic cinematic illustration, soft warm lighting, "
    "painterly rendered skin, clean rich illustrated backgrounds. If a reference shows "
    "a person, keep that EXACT character: same face, same hair, same wardrobe, same "
    "personality; do not change their identity. Do not change the art style. "
    "Render this new scene: "
)
REFERENCE_PROMPT_TAIL = (
    " Rich illustrated background, warm cinematic lighting, 16:9 wide composition, "
    "no on-image text, no letters, no captions."
)


def _generate_still_reference(scene_prompt, out_path, reference_images, config) -> Path:
    """Render one still via a fal /edit endpoint, conditioned on character reference
    image(s). Reuses the module download() + on_update(). Endpoint/resolution/aspect
    come from channel.json (reference_endpoint / reference_resolution / reference_aspect)."""
    endpoint = config.get("reference_endpoint", "fal-ai/nano-banana-2/edit")
    resolution = config.get("reference_resolution", "1K")
    aspect = config.get("reference_aspect", "16:9")
    lock = config.get("reference_prompt_lock", REFERENCE_PROMPT_LOCK)
    tail = config.get("reference_prompt_tail", REFERENCE_PROMPT_TAIL)
    urls = [_ref_data_uri(p) for p in reference_images]
    prompt = f"{lock}{scene_prompt}{tail}"
    args = {
        "prompt": prompt,
        "image_urls": urls,
        "num_images": 1,
        "aspect_ratio": aspect,
        "output_format": "png",
        "safety_tolerance": "5",
        "limit_generations": True,
    }
    if "nano-banana-2" in endpoint or "nano-banana-pro" in endpoint:
        args["resolution"] = resolution
    result = fal_client.subscribe(
        endpoint, arguments=args, with_logs=True, on_queue_update=on_update,
    )
    images = result.get("images", [])
    if not images:
        raise RuntimeError(f"No image returned (reference mode). Result: {result}")
    download(images[0]["url"], out_path)
    return out_path

'''

# ---------------------------------------------------------------------------
# (anchor_substring, replacement) edits. Applied in order. Each anchor must
# appear EXACTLY ONCE or the patch aborts (loud) rather than guessing.
# ---------------------------------------------------------------------------
EDITS = [
    # 1) generate_still: prepend the helper block + new signature + reference branch.
    #    Anchors on the unique function signature (no fragile banner-dash matching).
    (
        "def generate_still(image_prompt: str, out_path: Path) -> Path:\n"
        "    rb = load_rulebook()\n"
        "    config = load_channel_config(strict=True, anchor=out_path)\n"
        "    from look_resolver import resolve_look\n",
        HELPER_BLOCK.rstrip("\n") + "\n\n\n"
        "def generate_still(image_prompt: str, out_path: Path, reference_images=None) -> Path:\n"
        "    rb = load_rulebook()\n"
        "    config = load_channel_config(strict=True, anchor=out_path)\n"
        "    # --- REFERENCE render mode (per-channel, non-breaking) -------------------\n"
        "    # channel.json sets \"render_mode\":\"reference\"; a beat that resolved to one or\n"
        "    # more character refs renders via the fal /edit endpoint. Everything else\n"
        "    # (no render_mode, or no refs for this beat) falls through to text-to-image.\n"
        "    if config.get(\"render_mode\") == \"reference\" and reference_images:\n"
        "        return _generate_still_reference(image_prompt, out_path, reference_images, config)\n"
        "    from look_resolver import resolve_look\n",
    ),
    # 3a) cmd_stills: load config once, detect ref mode + map
    (
        "        # Normalise: ensure sequential indices, required fields, and canon-expansion.\n"
        "        _default_motion = (load_channel_config(strict=True, anchor=Path(args.project)).get(\"default_motion\")\n"
        "                           or CHANNEL_DEFAULTS[\"default_motion\"])\n"
        "        shots = []\n"
        "        for i, b in enumerate(beats, 1):\n"
        "            image_prompt = _expand_canon(b[\"image_prompt\"].strip(), canon)\n",
        "        # Normalise: ensure sequential indices, required fields, and canon-expansion.\n"
        "        _cfg_stills = load_channel_config(strict=True, anchor=Path(args.project))\n"
        "        _default_motion = (_cfg_stills.get(\"default_motion\")\n"
        "                           or CHANNEL_DEFAULTS[\"default_motion\"])\n"
        "        # REFERENCE render mode: resolve per-beat character reference images from the\n"
        "        # RAW {tag} canon references (BEFORE expansion). No-op for other channels.\n"
        "        import re as _re_ref\n"
        "        _ref_mode = _cfg_stills.get(\"render_mode\") == \"reference\"\n"
        "        _ref_map = _cfg_stills.get(\"reference_map\", {}) if _ref_mode else {}\n"
        "        _ref_anchor = _cfg_stills.get(\"reference_style_anchor\") if _ref_mode else None\n"
        "        _ref_chdir = Path(_cfg_stills.get(\"_channel_dir\", \".\"))\n"
        "        if _ref_mode:\n"
        "            print(f\"Reference render mode ON. Character refs: {sorted(_ref_map.keys())}\"\n"
        "                  + (f\"  style-anchor: {_ref_anchor}\" if _ref_anchor else \"\"))\n"
        "        shots = []\n"
        "        for i, b in enumerate(beats, 1):\n"
        "            _raw_ip = b[\"image_prompt\"].strip()\n"
        "            image_prompt = _expand_canon(_raw_ip, canon)\n",
    ),
    # 3b) cmd_stills: resolve refs per beat + store on the shot
    (
        "            shots.append({\n"
        "                \"index\": i,\n"
        "                \"narration\": b.get(\"narration\", \"\").strip(),\n"
        "                \"image_prompt\": image_prompt,\n"
        "                \"motion_prompt\": motion_prompt,\n"
        "            })\n",
        "            _refs = []\n"
        "            if _ref_mode:\n"
        "                _seen = set()\n"
        "                for _t in _re_ref.findall(r\"\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}\", _raw_ip):\n"
        "                    if _t in _ref_map and _t not in _seen:\n"
        "                        _seen.add(_t)\n"
        "                        _entry = _ref_map[_t]\n"
        "                        for _f in (_entry if isinstance(_entry, list) else [_entry]):\n"
        "                            _refs.append(str(_ref_chdir / _f))\n"
        "                if not _refs and _ref_anchor:\n"
        "                    _refs.append(str(_ref_chdir / _ref_anchor))\n"
        "            shots.append({\n"
        "                \"index\": i,\n"
        "                \"narration\": b.get(\"narration\", \"\").strip(),\n"
        "                \"image_prompt\": image_prompt,\n"
        "                \"motion_prompt\": motion_prompt,\n"
        "                \"_reference_images\": _refs,\n"
        "            })\n",
    ),
    # 3c) cmd_stills: pass refs at the generate call
    (
        "        print(f\"  [{s['index']}/{len(shots)}] {s['image_prompt'][:60]}...\")\n"
        "        generate_still(s[\"image_prompt\"], out)\n",
        "        _rfs = s.get(\"_reference_images\") or None\n"
        "        if _rfs:\n"
        "            print(f\"  [{s['index']}/{len(shots)}] [ref:{len(_rfs)}] {s['image_prompt'][:52]}...\")\n"
        "        else:\n"
        "            print(f\"  [{s['index']}/{len(shots)}] {s['image_prompt'][:60]}...\")\n"
        "        generate_still(s[\"image_prompt\"], out, reference_images=_rfs)\n",
    ),
    # 4) cmd_restill: pass stored refs so single-shot reshoots stay in ref mode
    (
        "    print(f\"Regenerating shot {args.shot}...\")\n"
        "    generate_still(prompt, out)\n",
        "    print(f\"Regenerating shot {args.shot}...\")\n"
        "    generate_still(prompt, out, reference_images=(shot.get(\"_reference_images\") or None))\n",
    ),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="dry-run: verify anchors, write nothing")
    args = ap.parse_args()

    if not TARGET.exists():
        sys.exit(f"ABORT: {TARGET} not found. Run from the repo (shared/ next to recreation_pipeline.py).")

    src = TARGET.read_text()

    if MARKER in src:
        print("Already patched (marker present). No-op.")
        return

    # Verify every anchor appears exactly once BEFORE touching anything.
    problems = []
    for i, (anchor, _repl) in enumerate(EDITS, 1):
        n = src.count(anchor)
        if n != 1:
            problems.append(f"  edit {i}: anchor found {n} times (expected 1)")
    if problems:
        print("ABORT: source has drifted from the expected shape:")
        print("\n".join(problems))
        print("Re-read the live file and update the anchors before patching.")
        sys.exit(1)
    print(f"All {len(EDITS)} anchors verified (each present exactly once).")

    if args.check:
        print("--check: anchors OK, nothing written.")
        return

    patched = src
    for anchor, repl in EDITS:
        patched = patched.replace(anchor, repl, 1)

    # Backup, write to a temp, py_compile-gate, then commit.
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(f".py.bak-{ts}")
    backup.write_text(src)
    tmp = TARGET.with_suffix(".py.patched-tmp")
    tmp.write_text(patched)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        tmp.unlink(missing_ok=True)
        sys.exit(f"ABORT: patched file failed py_compile, original untouched.\n{e}")

    tmp.replace(TARGET)
    py_compile.compile(str(TARGET), doraise=True)
    print(f"OK patched {TARGET.name}  (backup: {backup.name})")
    print("Added: reference render mode (generate_still branch + cmd_stills detection + restill).")
    print("Next: set qqrew/channel.json render_mode/reference_endpoint/reference_map, then render.")


if __name__ == "__main__":
    main()
