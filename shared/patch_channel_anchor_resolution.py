#!/usr/bin/env python3
"""
patch_channel_anchor_resolution.py — fix config resolution so the VOICE (and every
other channel field) is decided by WHICH PROJECT is being rendered, not by the
directory the command happened to launch from.

THE BUG (gaming-series shipped in Victor instead of Vinny):
  generate_voiceover → _synthesize_chunk → load_channel_config() walks up from CWD
  to find channel.json. Run from the repo root, the walk-up misses
  you-had-to-be-there/channel.json and falls through to a Victor channel (or the
  Victor default at CHANNEL_DEFAULTS). The channel.json was CORRECT (Vinny); the
  resolver just looked in the wrong place. Resolution was by LOCATION, not IDENTITY.

  Second, latent bug: _CHANNEL_CACHE is a single global. In any process that
  resolves more than one channel (batched/multi-channel), the FIRST channel
  resolved poisons every later lookup — even a correct call returns stale config.

THE FIX (project-anchored resolution + per-dir cache):
  1. load_channel_config(strict=False, anchor=None) — optional anchor path; walk up
     from there instead of CWD. Existing callers (anchor=None) keep CWD behaviour.
  2. Cache keyed by resolved channel dir (dict), not one global — so different
     channels in one process don't clobber each other.
  3. generate_voiceover(script, out_path) passes out_path.parent as the anchor, so
     the voice resolves from <project>/ up to the OWNING channel.json. Always right,
     regardless of CWD.
  4. Print the resolved voice + channel when synthesizing, so a wrong voice is
     visible immediately (the audio gate / log shows "voice: Vinny [you-had-to-be-there]").

Backward-compatible: every current caller that calls load_channel_config() with no
anchor still resolves from CWD exactly as before. Only generate_voiceover now passes
an anchor. Idempotent.

Run from repo root:  python shared/patch_channel_anchor_resolution.py
"""

import sys, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RP = REPO / "shared" / "recreation_pipeline.py"

# ---- edit 1: load_channel_config signature + anchor + per-dir cache ----
OLD_CACHE = "_CHANNEL_CACHE = None\n"
NEW_CACHE = "_CHANNEL_CACHE = {}   # keyed by resolved channel dir (str) or '__cwd__/__none__'\n"

OLD_SIG = """    global _CHANNEL_CACHE
    if _CHANNEL_CACHE is not None:
        return _CHANNEL_CACHE

    marker = _find_channel_marker()
    if marker is None:
        if strict:
            raise SystemExit(
                f"No {CHANNEL_MARKER} found by walking up from {Path.cwd()}. "
                f"Run pipeline commands from inside a channel folder (e.g. final-hours/ or success-coach/)."
            )
        _CHANNEL_CACHE = dict(CHANNEL_DEFAULTS)
        _CHANNEL_CACHE["_marker_path"] = None
        return _CHANNEL_CACHE"""

NEW_SIG = """    global _CHANNEL_CACHE

    marker = _find_channel_marker(anchor)
    cache_key = str(marker.parent) if marker is not None else "__none__"
    if cache_key in _CHANNEL_CACHE:
        return _CHANNEL_CACHE[cache_key]

    if marker is None:
        if strict:
            raise SystemExit(
                f"No {CHANNEL_MARKER} found by walking up from {anchor or Path.cwd()}. "
                f"Run pipeline commands from inside a channel folder (e.g. final-hours/ or success-coach/)."
            )
        defaults = dict(CHANNEL_DEFAULTS)
        defaults["_marker_path"] = None
        _CHANNEL_CACHE[cache_key] = defaults
        return defaults"""

# the def line gets the new kwarg
OLD_DEF = "def load_channel_config(strict: bool = False) -> dict:"
NEW_DEF = "def load_channel_config(strict: bool = False, anchor: Path = None) -> dict:"

# the tail of load_channel_config caches into the global differently
OLD_TAIL = """    config["_channel_dir"] = str(marker.parent)
    _CHANNEL_CACHE = config
    return config"""
NEW_TAIL = """    config["_channel_dir"] = str(marker.parent)
    _CHANNEL_CACHE[cache_key] = config
    return config"""

# ---- edit 2: _synthesize_chunk takes an anchor so the voice resolves per-project ----
OLD_SYNTH = """def _synthesize_chunk(text: str) -> bytes:
    \"\"\"One Inworld call -> raw audio bytes. Handles the current JSON+base64 API.\"\"\"
    config = load_channel_config(strict=False)
    voice_id = config["voice_id"]"""
NEW_SYNTH = """def _synthesize_chunk(text: str, anchor: Path = None) -> bytes:
    \"\"\"One Inworld call -> raw audio bytes. Handles the current JSON+base64 API.\"\"\"
    config = load_channel_config(strict=False, anchor=anchor)
    voice_id = config["voice_id"]"""


def main():
    if not RP.exists():
        sys.exit(f"ERROR: {RP} not found. Run from repo root.")
    src = RP.read_text(encoding="utf-8")

    if "anchor: Path = None" in src and "_CHANNEL_CACHE = {}" in src:
        print("  [skip] channel-anchor resolution already applied.")
        # still report the generate_voiceover wiring state
        if "_synthesize_chunk(" in src and "anchor=" not in src.split("def generate_voiceover")[-1][:1500]:
            print("  [WARN] generate_voiceover may not pass anchor to _synthesize_chunk — check manually.")
        return

    edits = [
        ("cache → dict", OLD_CACHE, NEW_CACHE),
        ("def signature", OLD_DEF, NEW_DEF),
        ("anchor + per-dir cache lookup", OLD_SIG, NEW_SIG),
        ("cache tail", OLD_TAIL, NEW_TAIL),
        ("_synthesize_chunk anchor", OLD_SYNTH, NEW_SYNTH),
    ]
    for label, old, _new in edits:
        if old not in src:
            sys.exit(f"  [FAIL] anchor not found: {label}. Aborting (no write). "
                     f"Source may have drifted — re-grep before patching.")
        if src.count(old) != 1:
            sys.exit(f"  [FAIL] {label} found {src.count(old)}x (expected 1). Aborting.")

    bak = RP.with_suffix(".py.pre_channel_anchor")
    shutil.copy2(RP, bak)
    for label, old, new in edits:
        src = src.replace(old, new, 1)
        print(f"  [ok] {label}")
    RP.write_text(src, encoding="utf-8")

    print(f"\n  Backup -> {bak.name}")
    print("\n  ONE MANUAL STEP REMAINS (signature differs per codebase):")
    print("  In generate_voiceover(script, out_path), the calls to _synthesize_chunk(...)")
    print("  must pass anchor=out_path.parent so the voice resolves from the project up")
    print("  to the owning channel.json. Find them with:")
    print("    grep -n '_synthesize_chunk(' shared/recreation_pipeline.py")
    print("  and add  , anchor=out_path.parent  to each call inside generate_voiceover.")
    print("  Also add a one-time print after resolving config, e.g.:")
    print('    print(f"   voice: {config[\\'voice_id\\']}  [{Path(config.get(\\'_channel_dir\\',\\'?\\')).name}]")')


if __name__ == "__main__":
    main()
