#!/usr/bin/env python3
"""
look_resolver.py — per-job decade look resolution (Phase 1: stills look).

Mirrors load_channel_config's pattern: self-discovers context by walking up
from a path, resolves channel-default -> project-override, caches the result.

The LOOK governs the visual stock/aesthetic of a job (1950s 16mm ... 2000s
digicam). Phase 1 wires only the Flux still layer: the resolved `style_suffix`
is what generate_still() appends to every image prompt. The grade layer
(film_emulate) is Phase 2 and reads the same resolved profile's `grade_preset`.

Resolution order (channel-then-project, per PIPELINE_PLAYBOOK §624):
  1. project folder has look.json  -> use it (era key OR inline style_suffix)
  2. else channel.json style_suffix -> use it  (EXACTLY today's behaviour)

look.json in a project folder may be either:
  {"look": "2000s"}                         # name a registry profile
  {"style_suffix": "...custom...",          # or inline an ad-hoc look
   "grade_preset": "digicam_2000s"}         # (grade_preset optional, Phase 2)

A project with NO look.json renders identically to today. Final Hours and all
existing projects are untouched.
"""

import json
from pathlib import Path

# ── The decade look registry ────────────────────────────────────────────────
# Adding a decade is a DATA edit here — never a code change.
# `style_suffix` is the high-value field: it's appended to every Flux prompt and
# is what makes stills period-correct on the first pass. `grade_preset` names the
# (Phase 2) film_emulate preset. `aspect` is intentionally OMITTED so jobs inherit
# the channel frame (channel owns the frame; the job owns the film stock).

LOOKS = {
    "kodachrome_50s": {
        "aliases": ["1950s", "50s"],
        "style_suffix": (
            "1950s home-movie aesthetic, 16mm Kodachrome film, rich saturated color, "
            "warm vintage tones, soft focus, heavy fine grain, gentle gate weave, "
            "slightly faded, period-accurate 1950s detail"
        ),
        "grade_preset": "sixteen_mm_50s",
    },
    "color_60s": {
        "aliases": ["1960s", "60s"],
        "style_suffix": (
            "1960s home-movie aesthetic, early color film stock, slightly faded warm tones, "
            "fine film grain, soft focus, gentle halation, period-accurate 1960s detail"
        ),
        "grade_preset": "sixteen_mm_60s",
    },
    "super8_70s": {
        "aliases": ["1970s", "70s"],
        "style_suffix": (
            "1970s home-movie aesthetic, Super 8 film look, warm faded color palette, "
            "heavy film grain, soft focus, slight halation and gentle light leaks, "
            "slightly overexposed, vignette, nostalgic and intimate, shot on vintage film stock"
        ),
        "grade_preset": "super8_70s",
    },
    "vhs_80s": {
        "aliases": ["1980s", "80s"],
        "style_suffix": (
            "1980s home-video aesthetic, VHS camcorder look, slightly soft analog video, "
            "mild chroma bleed, faint scan lines, lower saturation, muted warm tones, "
            "subtle tracking noise, period-accurate 1980s detail"
        ),
        "grade_preset": "vhs_80s",
    },
    "hi8_90s": {
        "aliases": ["1990s", "90s"],
        "style_suffix": (
            "1990s home-video aesthetic, Hi8 / early camcorder look, slightly sharper analog "
            "video, mild video noise, naturalistic 1990s color, faint chroma noise, "
            "subtle on-screen timestamp feel, period-accurate 1990s detail"
        ),
        "grade_preset": "hi8_90s",
    },
    "digicam_2000s": {
        "aliases": ["2000s", "00s", "y2k"],
        "style_suffix": (
            "early-2000s home-video aesthetic, early digital camcorder and point-and-shoot "
            "digicam look, slightly oversharpened, washed-out on-camera flash highlights, "
            "cooler digital color, faint digital noise and light JPEG compression, "
            "period-accurate Y2K detail"
        ),
        "grade_preset": "digicam_2000s",
    },
}

# alias -> canonical key
_ALIAS = {}
for _k, _v in LOOKS.items():
    _ALIAS[_k.lower()] = _k
    for _a in _v.get("aliases", []):
        _ALIAS[str(_a).lower()] = _k


def get_look(key_or_alias):
    """Return the look profile dict for a canonical key or alias, or None."""
    if not key_or_alias:
        return None
    canon = _ALIAS.get(str(key_or_alias).strip().lower())
    return LOOKS.get(canon) if canon else None


# ── Project discovery (mirror of load_channel_config's walk-up) ──────────────
# A still is written to <project>/modea/stills/shot_NNN.png (or <project>/stills/).
# We walk up from the output path looking for a project-level look.json. We stop
# at the channel marker so we never escape the project into the channel root.

_LOOK_CACHE = {}   # project_dir(str) -> resolved profile (or channel-default sentinel)
CHANNEL_MARKER = "channel.json"
LOOK_MARKER = "look.json"


def _find_look_json(anchor: Path):
    """Walk up from `anchor` to find a look.json, stopping if we hit a channel.json
    (that means we've left the project and reached the channel root)."""
    p = anchor if anchor.is_dir() else anchor.parent
    for d in [p, *p.parents]:
        lj = d / LOOK_MARKER
        if lj.is_file():
            return lj
        if (d / CHANNEL_MARKER).is_file():
            break   # reached the channel root; no project look.json above this
    return None


def resolve_look(anchor_path, channel_config: dict) -> dict:
    """Resolve the look for a job, given any path inside the project (e.g. the
    still's out_path) and the already-loaded channel config.

    Returns a dict guaranteed to contain at least 'style_suffix'. Falls back to
    the channel's style_suffix when no project look.json is present — i.e. exactly
    today's behaviour for every existing project.
    """
    anchor = Path(anchor_path).resolve()
    project_key = str(anchor.parent)
    if project_key in _LOOK_CACHE:
        return _LOOK_CACHE[project_key]

    resolved = None
    lj = _find_look_json(anchor)
    if lj is not None:
        try:
            data = json.loads(lj.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"   look: WARNING failed to read {lj} ({e}); using channel default.")
            data = {}
        # form 1: {"look": "2000s"} -> registry profile
        prof = get_look(data.get("look")) if data.get("look") else None
        if prof:
            resolved = dict(prof)
            print(f"   look: resolved -> {_ALIAS.get(str(data['look']).lower())} "
                  f"(grade: {prof.get('grade_preset')}) from {lj.name}")
        # form 2: inline style_suffix (+ optional grade_preset)
        elif data.get("style_suffix"):
            resolved = {
                "style_suffix": data["style_suffix"],
                "grade_preset": data.get("grade_preset"),
            }
            print(f"   look: resolved -> inline style_suffix from {lj.name}")
        elif data.get("look"):
            print(f"   look: WARNING unknown look '{data.get('look')}' in {lj.name}; "
                  f"using channel default.")

    if resolved is None:
        # No project look.json (or unusable) -> channel default. Today's behaviour.
        resolved = {"style_suffix": channel_config.get("style_suffix", ""),
                    "grade_preset": None}

    _LOOK_CACHE[project_key] = resolved
    return resolved


def reset_cache():
    """Test helper — clear the per-project cache."""
    _LOOK_CACHE.clear()
