#!/usr/bin/env python3
"""
patch_channel_anchor_resolution_v2.py — project-anchored channel/voice resolution.

Fixes the wrong-voice bug (gaming-series shipped Victor instead of Vinny): config
was resolved by walking up from CWD, so launching from the repo root found the
wrong channel.json (or the Victor default). Now resolution can be anchored on the
project path, and generate_voiceover anchors on out_path.parent so the voice is
always the OWNING channel's. Also fixes the single-global cache (which let the
first-resolved channel poison later lookups) by keying the cache per channel dir.

Fully automated — no manual step. Idempotent. Run from repo root:
  python shared/patch_channel_anchor_resolution_v2.py
"""

import sys, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RP = REPO / "shared" / "recreation_pipeline.py"

EDITS = [
    # 1) cache: single global -> dict keyed by channel dir
    ("cache → dict",
     "_CHANNEL_CACHE = None\n",
     "_CHANNEL_CACHE = {}   # keyed by resolved channel dir\n"),

    # 2) def signature gains optional anchor
    ("def signature",
     "def load_channel_config(strict: bool = False) -> dict:",
     "def load_channel_config(strict: bool = False, anchor: Path = None) -> dict:"),

    # 3) anchor-aware resolution + per-dir cache lookup
    ("anchor + per-dir cache",
     """    global _CHANNEL_CACHE
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
        return _CHANNEL_CACHE""",
     """    global _CHANNEL_CACHE

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
        return defaults"""),

    # 4) cache tail writes into the dict
    ("cache tail",
     """    config["_channel_dir"] = str(marker.parent)
    _CHANNEL_CACHE = config
    return config""",
     """    config["_channel_dir"] = str(marker.parent)
    _CHANNEL_CACHE[cache_key] = config
    return config"""),

    # 5) _synthesize_chunk accepts an anchor + prints the resolved voice once
    ("_synthesize_chunk anchor + voice print",
     """def _synthesize_chunk(text: str) -> bytes:
    \"\"\"One Inworld call -> raw audio bytes. Handles the current JSON+base64 API.\"\"\"
    config = load_channel_config(strict=False)
    voice_id = config["voice_id"]""",
     """def _synthesize_chunk(text: str, anchor: Path = None) -> bytes:
    \"\"\"One Inworld call -> raw audio bytes. Handles the current JSON+base64 API.\"\"\"
    config = load_channel_config(strict=False, anchor=anchor)
    voice_id = config["voice_id"]
    if not getattr(_synthesize_chunk, "_announced", False):
        _ch = Path(config.get("_channel_dir", "?")).name
        print(f"   voice: {voice_id}  [channel: {_ch}]")
        _synthesize_chunk._announced = True"""),

    # 6) both generate_voiceover call sites pass anchor=out_path.parent
    ("single-chunk call site",
     "        out_path.write_bytes(_synthesize_chunk(chunks[0]))",
     "        out_path.write_bytes(_synthesize_chunk(chunks[0], anchor=out_path.parent))"),

    ("multi-chunk call site",
     "        p.write_bytes(_synthesize_chunk(ch))",
     "        p.write_bytes(_synthesize_chunk(ch, anchor=out_path.parent))"),
]


def main():
    if not RP.exists():
        sys.exit(f"ERROR: {RP} not found. Run from repo root.")
    src = RP.read_text(encoding="utf-8")

    if "anchor: Path = None" in src and "_CHANNEL_CACHE = {}" in src:
        print("  [skip] already applied.")
        return

    for label, old, _new in EDITS:
        if old not in src:
            sys.exit(f"  [FAIL] anchor not found: {label}. Aborting, no write.")
        if src.count(old) != 1:
            sys.exit(f"  [FAIL] {label} found {src.count(old)}x (expected 1). Aborting.")

    bak = RP.with_suffix(".py.pre_channel_anchor")
    shutil.copy2(RP, bak)
    for label, old, new in EDITS:
        src = src.replace(old, new, 1)
        print(f"  [ok] {label}")
    RP.write_text(src, encoding="utf-8")
    print(f"\n  DONE (backup -> {bak.name}). Verify:")
    print('    grep -n "anchor=out_path.parent" shared/recreation_pipeline.py   (expect 2)')
    print("  Then regenerate the audio from ANYWHERE (CWD no longer matters):")
    print("    python shared/generate_episode_vo.py --text you-had-to-be-there/projects/gaming-series/ep_audio.txt --project you-had-to-be-there/projects/gaming-series")
    print('  Watch for:  voice: Vinny  [channel: you-had-to-be-there]')


if __name__ == "__main__":
    main()
