"""
Recreation Pipeline — Final Hours YouTube Channel
==================================================
Turns a narration script into a photorealistic historical recreation video,
fully programmatically. No editor, no dragging stills around.

Pipeline:
1. Claude API turns a script into a storyboard (shot list as JSON)
2. fal (Seedream / Nano Banana) generates a still per shot       [STILLS PHASE]
3. -- YOU REVIEW THE STILLS FOLDER, fix any bad ones --          [APPROVAL GATE]
4. fal (Kling) animates each approved still into a ~5s clip      [MOTION PHASE]
5. Inworld TTS narrates the full script (Victor voice)
6. moviepy assembles clips + lays Victor over the top, synced to narration

Design notes:
- Two-phase by default: stills first (cheap, ~$0.03 each), you approve,
  THEN motion (expensive, ~$0.15-0.20 each). Never pay for motion on a bad still.
- Zscaler cert handling is baked in (CERT_BUNDLE) so fal + requests both work
  on the ABB laptop without exporting env vars every time.
- Audio is Victor-only in this build. Music bed + per-shot SFX are stubbed
  at the bottom for when you switch them on.

Usage — run in three commands:

    # Phase 1: script -> storyboard -> stills (cheap). Writes a project folder.
    python3 recreation_pipeline.py stills \
        --script path/to/pompeii_script.txt \
        --project ~/final-hours/projects/pompeii_test

    # ... open the stills/ folder, eyeball them, re-run a single shot if needed:
    python3 recreation_pipeline.py restill \
        --project ~/final-hours/projects/pompeii_test --shot 3

    # Phase 2: animate approved stills + narrate + assemble the final video.
    python3 recreation_pipeline.py finish \
        --project ~/final-hours/projects/pompeii_test

Requirements:
    pip install anthropic fal-client requests "moviepy<2" python-dotenv

.env file (in the folder you run this from):
    ANTHROPIC_API_KEY=your_claude_key
    INWORLD_API_KEY=your_inworld_base64_key
    FAL_KEY=your_fal_key
"""

import os
import json
import base64
import argparse
from pathlib import Path
from dotenv import load_dotenv

import requests
import fal_client
import anthropic
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
)

# Single source of truth for env vars. The .env lives at the project root
# (03. Pipeline/.env, one level above shared/) so it's shared across all
# channels. python-dotenv's default search starts from the calling module's
# directory, which after the multi-channel migration is shared/ — not CWD —
# so we must point at it explicitly. Falls back to default search if the
# expected path doesn't exist (useful for VPS / cloud setups).
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

# ── Channel config ─────────────────────────────────────────────────────────────
# Each channel folder has its own channel.json marker holding the channel's
# overrides: voice_id, style_suffix, base_canon (auto-merged into every
# beat-script), and default_music_prompt. The pipeline finds the channel by
# walking up from CWD looking for that marker, so you switch channels by
# `cd`-ing into the relevant folder — no --channel flag needed.

CHANNEL_MARKER = "channel.json"

CHANNEL_DEFAULTS = {
    # Used if a channel config is missing a field. These match the historical
    # Final Hours defaults so existing behaviour is preserved when the file
    # isn't present.
    "name": "unknown",
    "voice_id": "Victor",
    "style_suffix": (
        "cinematic photorealistic recreation, painterly golden-hour and candlelit "
        "tones, deep shadows, volumetric light, film grain, shallow depth of field, "
        "historically accurate period detail, muted desaturated palette, 35mm film look"
    ),
    "default_music_prompt": (
        "Slow, mournful cinematic underscore for a historical documentary about "
        "death and disaster. Low sustained strings, a deep ambient drone, sparse "
        "distant piano. Funereal, foreboding, restrained. No percussion, no melody "
        "that competes with a narrator. Builds dread very slowly. Dark and solemn."
    ),
    "default_motion": (
        "Slow, subtle atmospheric motion. Drifting light, faint air. "
        "No fast movement, no camera shake."
    ),
    "base_canon": {},   # auto-merged into every beat-script's canon block
}


def _find_channel_marker(start: Path = None) -> Path | None:
    """Walk upward from `start` (default CWD) looking for channel.json."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        marker = candidate / CHANNEL_MARKER
        if marker.exists():
            return marker
    return None


_CHANNEL_CACHE = {}   # keyed by resolved channel dir

def load_channel_config(strict: bool = False, anchor: Path = None) -> dict:
    """
    Find and load the current channel's config by walking up from CWD.
    Cached after first call so we don't re-read the file 85 times per render.

    If no channel.json is found:
      - strict=True raises (used by commands that genuinely need channel context)
      - strict=False returns the defaults silently (used by rulebook editing,
        which can operate on the shared rulebook without channel context).

    The returned dict always has every key from CHANNEL_DEFAULTS filled in,
    so callers don't need to defensively .get() each field.
    """
    global _CHANNEL_CACHE

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
        return defaults

    try:
        loaded = json.loads(marker.read_text())
    except Exception as e:
        raise SystemExit(f"Failed to parse channel config {marker}: {e}")

    if not isinstance(loaded, dict):
        raise SystemExit(f"Channel config {marker} must be a JSON object, got {type(loaded).__name__}.")

    # Fill missing fields from defaults; explicit values override.
    config = dict(CHANNEL_DEFAULTS)
    config.update(loaded)
    config["_marker_path"] = str(marker)
    config["_channel_dir"] = str(marker.parent)
    _CHANNEL_CACHE[cache_key] = config
    return config


# ── Config ────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
INWORLD_API_KEY   = os.getenv("INWORLD_API_KEY")
FAL_KEY           = os.getenv("FAL_KEY")

# Zscaler / ABB cert fix — point requests at the combined bundle we built.
# fal_client (httpx) reads SSL_CERT_FILE; requests reads this var. Set both,
# so you never have to export them by hand again.
CERT_BUNDLE = os.path.expanduser("~/combined_cacert.pem")
if os.path.exists(CERT_BUNDLE):
    os.environ.setdefault("SSL_CERT_FILE", CERT_BUNDLE)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", CERT_BUNDLE)
    REQUESTS_VERIFY = CERT_BUNDLE
else:
    # On a clean machine (home Mac / VPS) the bundle won't exist and isn't needed.
    REQUESTS_VERIFY = True

# Inworld — CURRENT API (changed from the old /v1/tts/synthesize endpoint).
# Synchronous endpoint returns JSON with base64 audioContent.
INWORLD_TTS_URL  = "https://api.inworld.ai/tts/v1/voice"
INWORLD_VOICE_ID = "Victor"          # if this 400s, pick from current voice list
INWORLD_MODEL    = "inworld-tts-2"
# Inworld accepts max ~2000 chars/request. Full 15-min scripts must be chunked
# (see chunk + stitch logic in generate_voiceover).
INWORLD_MAX_CHARS = 1800

# Claude — current model string (sonnet-4 was retired April 2026)
CLAUDE_MODEL = "claude-sonnet-4-6"

# ── fal model endpoints (swap versions in one place if they bump) ──────────────

# Image model is a config switch. Default Seedream for cinematic quality;
# flip IMAGE_MODEL to "nano_banana" when flooding/cost matters.
IMAGE_MODEL = "flux"   # "seedream" | "nano_banana" | "flux"
# Flux Pro v1.1 has a more diverse, less polished human-face prior than Seedream's
# catalogue-male default. Used for the Coach Alex avatar generation where the
# Seedream prior kept producing model-handsome faces. Same arg structure
# (image_size dict + prompt + negative_prompt) so it's a drop-in swap.

IMAGE_ENDPOINTS = {
    "seedream":     "fal-ai/bytedance/seedream/v3/text-to-image",
    "nano_banana":  "fal-ai/nano-banana",
    "flux":         "fal-ai/flux-pro/v1.1",
}

# O3 Standard: ~3x faster + cheaper than Pro. Good default for the channel.
# Uses image_url (NOT start_image_url — that's the v3 endpoints).
VIDEO_ENDPOINT = "fal-ai/kling-video/o3/standard/image-to-video"

SHOT_DURATION = "5"        # seconds per clip
def _channel_aspect():
    """Render resolution from channel.json (width/height), default 1280x720.
    Final Hours has no width/height in its channel.json so it stays 720p;
    Synthetic sets 1920x1080 to match the Mode B Remotion clips."""
    try:
        cfg = load_channel_config(strict=False)
        w = int(cfg.get("width", 1280))
        h = int(cfg.get("height", 720))
        return {"width": w, "height": h}
    except Exception:
        return {"width": 1280, "height": 720}

ASPECT = _channel_aspect()   # 16:9; per-channel via channel.json width/height

# House visual style appended to every image prompt for consistency.
# This IS the channel's look — keep it identical across every video.
STYLE_SUFFIX = (
    "cinematic photorealistic recreation, painterly golden-hour and candlelit "
    "tones, deep shadows, volumetric light, film grain, shallow depth of field, "
    "historically accurate period detail, muted desaturated palette, 35mm film look"
)

# ── THE RULEBOOK ────────────────────────────────────────────────────────────────
# This is the moat. Every spell-breaker caught in review becomes a permanent rule
# here, so it never recurs in any future video. The rulebook lives in a JSON file
# (rulebook.json next to this script) so it persists and grows across every video
# and every channel. It has two halves:
#   "negative"     -> appended to EVERY image prompt (things to never render)
#   "motion_rules" -> fed to the storyboard step (risky framings for Claude to avoid)
#
# Seeded with what we've already learned:
#   - the t-shirt (modern clothing on a Roman) — caught on the thumbnail
#   - the shutter hand with fingers clipping through the frame — caught in motion
#   - the dog with hallucinated rib-stripes — caught in a still
RULEBOOK_PATH = Path(__file__).parent / "rulebook.json"
CHANNEL_RULEBOOK_NAME = "rulebook.json"   # looked for inside the channel folder

DEFAULT_RULEBOOK = {
    # NEGATIVE: specific spell-breakers only. CRITICAL LESSON (Pompeii v1):
    # broad anatomy negatives ("deformed hands, malformed anatomy, warped faces")
    # cause the image model to AVOID GENERATING PEOPLE AT ALL — it satisfies the
    # constraint by producing empty rooms and landscapes. NEVER put blunt anatomy
    # terms here. People are the emotional core of the channel. Handle anatomy
    # quality through the POSITIVE prompt (people_directive) instead.
    "negative": [
        "modern clothing", "t-shirt", "wristwatch", "contemporary hairstyle",
        "eyeglasses", "zippers", "printed fabric",
        "visible ribs through skin", "skeletal striping on animals",
        "uncanny animal anatomy",
        "on-screen text", "captions", "watermark", "modern objects",
        "plastic textures", "oversaturated colors",
    ],
    # POSITIVE directive appended to image prompts. This is how we get GOOD anatomy
    # — by asking for it, not by negating bad anatomy (which suppresses people).
    "people_directive": (
        "include people where the narrative calls for them, with natural, "
        "well-formed faces and hands, period-accurate figures, anatomically correct, "
        "emotionally expressive, naturally posed"
    ),
    "motion_rules": [
        "PEOPLE ARE THE EMOTIONAL CORE. Most shots should include human figures — "
        "the families, the crowds at a distance, individuals reacting. Do NOT default "
        "to empty rooms and landscapes. Empty atmospheric shots are the exception, not the rule.",
        "Avoid shots where a hand manipulates an object on screen (closing a shutter, "
        "opening a door). Hands warp badly in motion. Show the RESULT instead — a "
        "shutter already closed, a door already shut, ash already settled on the sill.",
        "Avoid close side-on shots of animals; image models hallucinate their anatomy. "
        "Frame animals small, distant, in shadow, or partially obscured.",
        "Keep faces near-static in MOTION (to avoid warping when animated), but DO show "
        "people clearly in the still. Animate the environment (ash, smoke, water, light) "
        "around a still or barely-moving figure rather than animating the face itself.",
        "No fast action, no running, no combat, no crowds in fast motion. Slow and atmospheric only.",
    ],
}


def _read_rulebook_file(path: Path) -> dict:
    """Read a rulebook JSON from disk. Returns empty-shape dict if missing or unreadable."""
    if not path.exists():
        return {"negative": [], "motion_rules": [], "people_directive": ""}
    try:
        data = json.loads(path.read_text())
    except Exception:
        backup = path.with_suffix(".json.corrupt")
        path.rename(backup)
        print(f"   rulebook: {path.name} was corrupt, backed up to {backup.name}")
        return {"negative": [], "motion_rules": [], "people_directive": ""}
    data.setdefault("negative", [])
    data.setdefault("motion_rules", [])
    data.setdefault("people_directive", "")
    return data


def load_rulebook() -> dict:
    """
    Two-layer rulebook:
      1. Universal rulebook at shared/rulebook.json — anatomy, gravity, text-rendering.
         Applies to every channel. Seeded from DEFAULT_RULEBOOK on first run.
      2. Channel rulebook at <channel_folder>/rulebook.json — period-specific or
         topic-specific rules. Appends on top of the universal layer; never replaces.

    Channel rules ADD to universal rules. The same negative term in both layers is
    de-duplicated. The people_directive from the channel layer (if non-empty)
    overrides the universal one, so a channel can shape its own positive prompt.

    The on-disk shared rulebook is the source of truth and only ever grows.
    """
    # Universal layer
    if not RULEBOOK_PATH.exists():
        RULEBOOK_PATH.write_text(json.dumps(DEFAULT_RULEBOOK, indent=2))
        universal = dict(DEFAULT_RULEBOOK)
    else:
        universal = _read_rulebook_file(RULEBOOK_PATH)
        universal.setdefault("people_directive", DEFAULT_RULEBOOK["people_directive"])
        # Additive merge from code defaults (so new default rules flow in)
        changed = False
        for key in ("negative", "motion_rules"):
            existing_lower = [x.lower() for x in universal[key]]
            for item in DEFAULT_RULEBOOK.get(key, []):
                if item.lower() not in existing_lower:
                    universal[key].append(item)
                    existing_lower.append(item.lower())
                    changed = True
        if changed:
            RULEBOOK_PATH.write_text(json.dumps(universal, indent=2))
            print("   rulebook: merged in new default rules from code")

    # Channel overlay (if we're inside a channel folder)
    config = load_channel_config(strict=False)
    channel_dir = config.get("_channel_dir")
    if channel_dir:
        channel_rb_path = Path(channel_dir) / CHANNEL_RULEBOOK_NAME
        channel_rb = _read_rulebook_file(channel_rb_path)
        # Additive merge channel rules on top
        existing_neg = [x.lower() for x in universal["negative"]]
        for item in channel_rb["negative"]:
            if item.lower() not in existing_neg:
                universal["negative"].append(item)
                existing_neg.append(item.lower())
        existing_motion = [x.lower() for x in universal["motion_rules"]]
        for item in channel_rb["motion_rules"]:
            if item.lower() not in existing_motion:
                universal["motion_rules"].append(item)
                existing_motion.append(item.lower())
        # Channel's people_directive (if set) overrides universal
        if channel_rb["people_directive"]:
            universal["people_directive"] = channel_rb["people_directive"]

    return universal


def _active_rulebook_path() -> Path:
    """
    Where rule edits get written. Inside a channel folder, edits land in
    <channel>/rulebook.json; outside a channel, edits land in the universal
    shared rulebook. This means a Final Hours lesson is banked to Final Hours
    only, while truly universal rules can still be added by running from
    outside any channel folder.
    """
    config = load_channel_config(strict=False)
    channel_dir = config.get("_channel_dir")
    if channel_dir:
        return Path(channel_dir) / CHANNEL_RULEBOOK_NAME
    return RULEBOOK_PATH


def add_negative_rule(term: str):
    """Append a new spell-breaker to the active rulebook (channel-scoped if inside a channel)."""
    path = _active_rulebook_path()
    rb = _read_rulebook_file(path)
    term = term.strip()
    if term and term.lower() not in [t.lower() for t in rb["negative"]]:
        rb["negative"].append(term)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rb, indent=2))
        scope = "channel" if path != RULEBOOK_PATH else "universal"
        print(f"   rulebook ({scope}): added negative rule '{term}'")


def remove_negative_rule(term: str):
    """
    Surgically remove rules from the active rulebook (channel-scoped if inside a channel).
    Matches case-insensitively on substring.
    """
    path = _active_rulebook_path()
    rb = _read_rulebook_file(path)
    term_l = term.strip().lower()
    before = len(rb["negative"])
    removed = [r for r in rb["negative"] if term_l in r.lower()]
    rb["negative"] = [r for r in rb["negative"] if term_l not in r.lower()]
    path.write_text(json.dumps(rb, indent=2))
    scope = "channel" if path != RULEBOOK_PATH else "universal"
    if removed:
        print(f"   rulebook ({scope}): removed {before - len(rb['negative'])} rule(s): {removed}")
    else:
        print(f"   rulebook ({scope}): no negative rule matching '{term}' found")



# ── Small helpers ──────────────────────────────────────────────────────────────

def claude():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def download(url: str, out_path: Path):
    resp = requests.get(url, verify=REQUESTS_VERIFY)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    return out_path


def on_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs or []:
            print("   ", log.get("message", ""))


# ── Step 1: script -> storyboard JSON ──────────────────────────────────────────

def build_storyboard(script: str) -> list:
    """
    Ask Claude to break the narration script into a sequence of shots.
    Each shot gets an image prompt, a motion prompt, and the slice of
    narration it covers. Returns a list of shot dicts.
    """
    rb = load_rulebook()
    motion_rules = "\n".join(f"- {r}" for r in rb["motion_rules"])

    # Compute target shot count from script length so footage covers the FULL
    # narration. Pompeii v1 failed because 38 shots (~190s) didn't cover a 5:49
    # narration, leaving the last shot frozen for ~2:43. Documentary pace ~135 wpm;
    # at ~4 seconds per shot that's one shot per ~9 words.
    word_count = len(script.split())
    est_seconds = (word_count / 135) * 60
    target_shots = max(12, round(est_seconds / 4.0))

    prompt = f"""You are a cinematographer and storyboard artist for a faceless
historical-recreation documentary channel called "Final Hours". You turn a
narration script into a shot list for an AI image+video pipeline.

Here is the narration script:
---
{script}
---

This script is approximately {word_count} words, which at documentary narration
pace (~135 words/minute) runs about {est_seconds/60:.1f} minutes. Each generated
clip is ~4-5 seconds long. To cover the FULL narration with motion (never freezing
on a held frame), you MUST produce approximately {target_shots} shots — roughly one
shot every 4 seconds of narration. Do NOT under-produce shots; too few shots means
the video freezes before the narration ends. Aim for {target_shots} shots.

For each shot return:
- "narration": the exact slice of the script this shot covers (verbatim, in order, no gaps, no overlaps - concatenated they must equal the whole script)
- "image_prompt": a vivid, specific description of a SINGLE photorealistic frame. Describe subject, setting, lighting, composition. Do NOT describe motion here. Keep recurring characters visually consistent (same age, clothing, hair) across shots.
- "motion_prompt": the camera/scene motion for this frame. Keep it SLOW and atmospheric - drifting ash, lapping water, flickering firelight, slow push-in or pan. Avoid fast action, avoid anything that would warp faces.

SHOT GRAMMAR — VARY THE CAMERA (this is critical for visual interest):
Each shot must specify a deliberate framing. Draw from this vocabulary and
VARY IT AGGRESSIVELY across consecutive shots — never two adjacent shots with
the same distance-and-angle:
- ESTABLISHING / EXTREME WIDE: the subject tiny in a vast landscape; drone-height looking down over terrain
- WIDE: full scene, figure and surroundings together
- MEDIUM: a figure from the waist, or two elements in frame
- CLOSE DETAIL: hands at work, an object, turned earth, a tool, a texture — NOT a face
- EXTREME CLOSE-UP: a single object or texture filling the frame (grain of wood, weave of cloth, a single coin)
- LOW ANGLE: camera low, looking up (the sky, a ridge above, a doorway towering)
- HIGH ANGLE / DRONE: camera high, looking down (a lone figure on a slope, graves from above, a roof, a path)
- FROM BEHIND / OVER-THE-SHOULDER: looking where the subject looks (the channel's face-never-resolved default)

HARD RULES:
- When several consecutive shots occur in the same location, DELIBERATELY cycle the framing: establish wide, then cut to a close detail of hands or an object, then a low or high angle, then a from-behind medium. Treat repetition as a failure.
- Never produce two adjacent shots that would look like the same photograph. Vary camera height, distance, and angle as much as the scene allows.
- For CLOSE and MEDIUM framings of people, frame on HANDS, OBJECTS, BACKS, and SILHOUETTES rather than faces. A close-up is an opportunity for a detail of hands at work or a meaningful object — NEVER a resolved face. This keeps variety and face-never-resolved discipline working together.
- Put the chosen framing explicitly at the START of each image_prompt (e.g. "High aerial drone view of...", "Extreme close-up of hands gripping...", "Low angle looking up at...").

CRITICAL RULES learned from past production (these prevent the artifacts that break realism — follow them strictly when choosing framings):
{motion_rules}

Rules:
- Atmosphere over action. Slow, mournful, documentary.
- People are the emotional core — most shots should feature human figures, not empty rooms.
- No on-screen text, no captions, no modern objects.
- Produce approximately {target_shots} shots to cover the full narration length.
- Return ONLY a JSON array of shot objects. No preamble, no markdown fences, nothing else."""

    # Stream the response — required by SDK for max_tokens >= ~16000 since
    # the request may take longer than 10 minutes non-streaming.
    raw_parts = []
    with claude().messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=32000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            raw_parts.append(text)
    raw = "".join(raw_parts).strip()
    # Strip accidental markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    shots = json.loads(raw)
    for i, s in enumerate(shots, 1):
        s["index"] = i
    return shots


# ── Step 2: generate a still per shot ──────────────────────────────────────────

def generate_still(image_prompt: str, out_path: Path) -> Path:
    rb = load_rulebook()
    config = load_channel_config(strict=True, anchor=out_path)
    from look_resolver import resolve_look
    style_suffix = resolve_look(out_path, config)["style_suffix"]
    people = rb.get("people_directive", "")
    full_prompt = f"{image_prompt}, {people}, {style_suffix}" if people else f"{image_prompt}, {style_suffix}"
    negative = ", ".join(rb["negative"])
    endpoint = IMAGE_ENDPOINTS[IMAGE_MODEL]
    args = {"prompt": full_prompt, "image_size": ASPECT}
    if negative:
        # Most fal image models accept negative_prompt; harmless if ignored.
        args["negative_prompt"] = negative
    if IMAGE_MODEL == "flux":
        # flux-pro/v1.1 silently returns black ~7KB PNGs when its safety
        # filter trips (default tolerance ~2). "5" is the loosest practical
        # setting that stops the silent rejects. Gated to flux — seedream/
        # nano_banana do not take this arg and should not be handed it.
        args["safety_tolerance"] = "5"
    result = fal_client.subscribe(
        endpoint,
        arguments=args,
        with_logs=True,
        on_queue_update=on_update,
    )
    images = result.get("images", [])
    if not images:
        raise RuntimeError(f"No image returned for shot. Result: {result}")
    download(images[0]["url"], out_path)
    return out_path


# ── Step 4: animate a still into a clip ─────────────────────────────────────────

def _still_to_held_clip(still_path: Path, out_path: Path, duration: float = None) -> Path:
    """
    Turn a still PNG into a static video clip via ffmpeg — no AI motion.
    Used as the automatic fallback when Kling refuses a shot on content-policy
    grounds (e.g. casts, remains, executions). A held still over the narration
    is often better for these sensitive shots anyway.
    """
    import subprocess
    dur = duration or SHOT_DURATION
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(still_path),
        "-c:v", "libx264", "-t", str(dur), "-pix_fmt", "yuv420p",
        "-vf", f"scale={ASPECT['width']}:{ASPECT['height']}:force_original_aspect_ratio=decrease,pad={ASPECT['width']}:{ASPECT['height']}:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-r", "24", str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


def ken_burns_still(still_path: Path, out_path: Path, duration: float = None) -> Path:
    """
    TIERED RENDER — the free clip floor. Turn a still into a slow zoom-in clip via
    ffmpeg zoompan, rendered to the beat's EXACT duration (no Kling, no stretch, no
    cost). Writes the SAME artifact Kling writes (clips/shot_NNN.mp4, channel aspect),
    so assembly can't tell them apart and needs zero changes.

    Craft (banked): zooming the source directly judders — upscale the still first,
    then zoom, for smoothness. Slow zoom-IN always (one default, zero per-beat
    decisions). Cap the zoom so long beats do not creep too far in.
    """
    import subprocess
    dur = float(duration or SHOT_DURATION)
    fps = 24
    total_frames = max(1, int(round(dur * fps)))
    W, H = ASPECT["width"], ASPECT["height"]
    # Upscale to 4x the target first (smoothness), cover-crop to the 4x frame, then a
    # slow zoom-in (cap 1.25x), output at channel aspect.
    up_w, up_h = W * 4, H * 4
    vf = (
        f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
        f"crop={up_w}:{up_h},"
        f"zoompan=z='min(zoom+0.0024,1.50)':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={W}x{H}:fps={fps},setsar=1"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(still_path),
        "-vf", vf,
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(fps),
        str(out_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        tail = " | ".join(res.stderr.strip().splitlines()[-6:])
        raise RuntimeError(f"ken_burns ffmpeg failed: {tail}")
    return out_path


def _is_content_policy_error(exc) -> bool:
    """Detect Kling's content-policy refusal across the ways it can surface."""
    s = str(exc).lower()
    return ("content_policy" in s or "content checker" in s
            or "flagged by a content" in s or "unprocessable" in s)


def animate_still(still_path: Path, motion_prompt: str, out_path: Path) -> Path:
    # Kling needs a public URL — upload the local still to fal storage first.
    try:
        image_url = fal_client.upload_file(str(still_path))
        result = fal_client.subscribe(
            VIDEO_ENDPOINT,
            arguments={
                "image_url": image_url,
                "prompt": motion_prompt,
                "duration": SHOT_DURATION,
                "generate_audio": False,
            },
            with_logs=True,
            on_queue_update=on_update,
        )
        video = result.get("video") or {}
        url = video.get("url")
        if not url:
            raise RuntimeError(f"No video returned for shot. Result: {result}")
        download(url, out_path)
        return out_path
    except Exception as e:
        # AUTO-FALLBACK: if Kling refused on content-policy grounds (casts,
        # remains, executions), don't crash the whole render — turn the still
        # into a held clip and carry on. This is what makes unattended/cloud
        # rendering possible. Any OTHER error still raises.
        if _is_content_policy_error(e):
            print(f"      ⚠ content-policy refusal — using held still for this shot")
            return _still_to_held_clip(still_path, out_path)
        raise


# ── Step 5: narrate full script via Inworld (Victor) ───────────────────────────

def _synthesize_chunk(text: str, anchor: Path = None) -> bytes:
    """One Inworld call -> raw audio bytes. Handles the current JSON+base64 API."""
    config = load_channel_config(strict=False, anchor=anchor)
    voice_id = config["voice_id"]
    if not getattr(_synthesize_chunk, "_announced", False):
        _ch = Path(config.get("_channel_dir", "?")).name
        print(f"   voice: {voice_id}  [channel: {_ch}]")
        _synthesize_chunk._announced = True
    headers = {
        "Authorization": f"Basic {INWORLD_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voiceId": voice_id,                # camelCase in current API
        "modelId": INWORLD_MODEL,           # camelCase in current API
        "audioConfig": {"audioEncoding": "MP3",
                        "speakingRate": float(config.get("speaking_rate", 1.0))},
        "deliveryMode": "EXPRESSIVE",
    }
    resp = requests.post(INWORLD_TTS_URL, json=payload, headers=headers, verify=REQUESTS_VERIFY)
    resp.raise_for_status()
    data = resp.json()
    audio_b64 = data.get("audioContent")
    if not audio_b64:
        raise RuntimeError(f"No audio returned. Response keys: {list(data.keys())}")
    return base64.b64decode(audio_b64)


def _chunk_text(text: str, max_chars: int = INWORLD_MAX_CHARS) -> list:
    """Split at sentence boundaries so long scripts stay under the char limit."""
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current.strip())
    return chunks


def generate_voiceover(script: str, out_path: Path) -> Path:
    """
    Narrate the full script. If it fits in one request, one call. If it's long
    (full 15-min video), chunk at sentence boundaries and concatenate the MP3s.
    """
    chunks = _chunk_text(script)
    if len(chunks) == 1:
        out_path.write_bytes(_synthesize_chunk(chunks[0], anchor=out_path.parent))
        return out_path

    # Multiple chunks: synthesize each, then concat the audio with moviepy
    print(f"   script is long — splitting into {len(chunks)} chunks")
    part_paths = []
    for i, ch in enumerate(chunks, 1):
        print(f"   narrating chunk {i}/{len(chunks)}...")
        p = out_path.parent / f"_voice_part_{i:02d}.mp3"
        p.write_bytes(_synthesize_chunk(ch, anchor=out_path.parent))
        part_paths.append(p)

    from moviepy.editor import concatenate_audioclips
    clips = [AudioFileClip(str(p)) for p in part_paths]
    full = concatenate_audioclips(clips)
    full.write_audiofile(str(out_path), verbose=False, logger=None)
    for c in clips:
        c.close()
    for p in part_paths:
        p.unlink(missing_ok=True)
    return out_path


# ── Step 5b: generate music bed via fal (ElevenLabs Music) ─────────────────────

# ElevenLabs Music through fal — same key, no separate signup.
# Returns audio at result["audio"]["url"]. Durations 10s-5min.
MUSIC_ENDPOINT = "fal-ai/elevenlabs/music"

# The Final Hours house sound. Keep this consistent for channel identity.
DEFAULT_MUSIC_PROMPT = (
    "Slow, mournful cinematic underscore for a historical documentary about "
    "death and disaster. Low sustained strings, a deep ambient drone, sparse "
    "distant piano. Funereal, foreboding, restrained. No percussion, no melody "
    "that competes with a narrator. Builds dread very slowly. Dark and solemn."
)

def generate_music(out_path: Path, prompt: str = None,
                   duration_seconds: int = 120) -> Path:
    if prompt is None:
        config = load_channel_config(strict=False)
        prompt = config["default_music_prompt"]
    result = fal_client.subscribe(
        MUSIC_ENDPOINT,
        arguments={"prompt": prompt, "music_length_ms": duration_seconds * 1000},
        with_logs=True,
        on_queue_update=on_update,
    )
    audio = result.get("audio") or {}
    url = audio.get("url")
    if not url:
        raise RuntimeError(f"No music returned. Result keys: {list(result.keys())}")
    download(url, out_path)
    return out_path


# ── Step 6: assemble ────────────────────────────────────────────────────────────

# Audio mix levels — tune by ear. Victor full; music/SFX low underneath.
VOICE_LEVEL = 1.15
MUSIC_LEVEL = 0.07   # bed sits low under the narration (calibrated for Jamendo tracks, 3 June 2026)
SFX_LEVEL   = 0.28   # used only if per-shot SFX is switched on

def _auto_align_with_whisper(voice_path: Path, storyboard_path: Path) -> bool:
    """Auto-run whisper + alignment if not already done. Returns True on success.

    Idempotent: skips if storyboard already has audio_duration on every shot.
    Graceful: returns False (with warning) if whisper isn't installed.
    """
    import json as _json
    import shutil as _shutil
    import subprocess as _subprocess

    # Skip if already aligned
    try:
        with open(storyboard_path) as _f:
            _data = _json.load(_f)
        _shots = _data if isinstance(_data, list) else _data.get("beats", _data.get("shots", []))
        if _shots and all("audio_duration" in s for s in _shots):
            print("   sync: storyboard already aligned (audio_duration present on all shots)")
            return True
    except Exception:
        pass

    # Check whisper is installed
    if not _shutil.which("whisper"):
        print("   sync: WARNING — whisper not installed; falling back to word-count proxy")
        print("   sync: install with: pip install openai-whisper --break-system-packages")
        return False

    project_dir = voice_path.parent
    whisper_json = project_dir / "voiceover.json"

    # Run whisper if needed
    if not whisper_json.exists():
        print(f"   sync: running whisper on {voice_path.name} (3-5 min on M-series)...")
        try:
            _subprocess.run([
                "whisper", str(voice_path),
                "--model", "small",
                "--output_format", "json",
                "--output_dir", str(project_dir),
                "--word_timestamps", "True",
                "--verbose", "False",
            ], check=True, capture_output=True, text=True)
        except _subprocess.CalledProcessError as _e:
            print(f"   sync: whisper failed: {_e.stderr[:300]}")
            return False
    else:
        print(f"   sync: using existing {whisper_json.name}")

    # Run alignment via shared script
    align_script = Path(__file__).parent / "align_with_whisper.py"
    if not align_script.exists():
        print(f"   sync: alignment script not found at {align_script}")
        return False

    print("   sync: aligning shots to measured audio timestamps...")
    try:
        import sys as _sys
        _result = _subprocess.run([
            _sys.executable, str(align_script),
            "--project", str(project_dir),
        ], check=True, capture_output=True, text=True)
        # Echo the alignment summary
        for line in _result.stdout.splitlines():
            if line.strip() and not line.startswith("Whisper detected"):
                print(f"   sync: {line.strip()}")
        return True
    except _subprocess.CalledProcessError as _e:
        print(f"   sync: alignment failed: {_e.stderr[:300]}")
        return False


def assemble(clip_paths: list, voice_path: Path, out_path: Path,
             music_path=None) -> Path:
    """
    ffmpeg-based assembly (replaces the moviepy version, which OOMs on long
    videos). Trims each clip to its per-shot duration, concatenates via the
    ffmpeg concat demuxer (streaming, near-constant memory), then muxes the
    voiceover and optional music bed. The moviepy implementation is preserved
    as assemble_moviepy() for fallback.

    Per-shot duration source priority (unchanged from the moviepy version):
      1. Whisper-measured audio_duration in storyboard.json
      2. word-count proxy from narration
      3. uniform (voice_duration / n)
    """
    import json as _json
    import subprocess as _sub
    import tempfile as _tmp
    import shutil as _shutil
    import math as _math

    n = len(clip_paths)
    if n == 0:
        raise SystemExit("No clips to assemble.")

    project_dir = Path(voice_path).parent

    def _probe(p):
        r = _sub.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                     stdout=_sub.PIPE, stderr=_sub.DEVNULL, text=True)
        try:
            return float(r.stdout.strip())
        except ValueError:
            return 0.0

    def _run(cmd, desc):
        r = _sub.run(cmd, stdout=_sub.DEVNULL, stderr=_sub.PIPE, text=True)
        if r.returncode != 0:
            tail = "\n".join(r.stderr.strip().splitlines()[-8:])
            raise SystemExit(f"ffmpeg failed during {desc}:\n{tail}")

    voice_dur = _probe(voice_path)

    # Auto-align with Whisper if available (same hook the moviepy path used).
    _storyboard_path = project_dir / "storyboard.json"
    if _storyboard_path.exists():
        try:
            _auto_align_with_whisper(voice_path, _storyboard_path)
        except Exception as _e:
            print(f"   assemble: whisper auto-align skipped ({_e})")

    # Resolve per-shot durations.
    durations = None
    try:
        if _storyboard_path.exists():
            _data = _json.loads(_storyboard_path.read_text())
            _shots = _data if isinstance(_data, list) else _data.get("beats", _data.get("shots", []))
            if len(_shots) == n:
                if all("audio_duration" in s for s in _shots):
                    durations = [float(s["audio_duration"]) for s in _shots]
                    print(f"   assemble: Whisper-measured per-shot durations")
                else:
                    _words = [max(1, len(s.get("narration", "").split())) for s in _shots]
                    _total = sum(_words)
                    durations = [voice_dur * (w / _total) for w in _words]
                    print(f"   assemble: word-count-proxy per-shot durations")
    except Exception as _e:
        print(f"   assemble: duration lookup failed ({_e}), using uniform")
        durations = None

    if durations is None:
        z = voice_dur / n
        durations = [z] * n
        print(f"   assemble: uniform {voice_dur:.1f}s / {n} = {z:.2f}s per clip")

    print(f"   assemble: range {min(durations):.2f}s - {max(durations):.2f}s, "
          f"total {sum(durations):.1f}s (ffmpeg streaming)")

    work = Path(_tmp.mkdtemp(prefix="assemble_", dir=str(project_dir)))
    try:
        # Trim each clip to its target duration (low-memory, one at a time).
        trimmed = []
        for i, (clip, target) in enumerate(zip(clip_paths, durations), 1):
            dst = work / f"t_{i:03d}.mp4"
            native = _probe(clip)
            scale_pad = (f"scale={ASPECT['width']}:{ASPECT['height']}:force_original_aspect_ratio=decrease,"
                         f"pad={ASPECT['width']}:{ASPECT['height']}:(ow-iw)/2:(oh-ih)/2,setsar=1")
            if native > 0 and target > native + 0.05:
                factor = target / native
                _run([
                    "ffmpeg", "-y", "-i", str(clip),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an",
                    "-vf", f"setpts={factor:.6f}*PTS,{scale_pad},fps=24",
                    "-t", f"{target:.3f}",
                    str(dst),
                ], f"stretch clip {i} ({native:.1f}->{target:.1f}s {factor:.2f}x)")
            else:
                cut = min(target, native) if native > 0 else target
                _run([
                    "ffmpeg", "-y", "-i", str(clip),
                    "-t", f"{cut:.3f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an",
                    "-vf", f"{scale_pad},fps=24",
                    str(dst),
                ], f"trim clip {i}")
            trimmed.append(dst)
            if i % 10 == 0 or i == n:
                print(f"   assemble: trimmed {i}/{n}")

        # Concat via demuxer (streaming).
        print("   assemble: concatenating (ffmpeg demuxer)...")
        concat_list = work / "concat.txt"
        concat_list.write_text("".join(f"file '{c.resolve()}'\n" for c in trimmed))
        silent = work / "silent.mp4"
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
              "-i", str(concat_list), "-c", "copy", str(silent)], "concat")

        # Build audio: voice, optional music bed looped + ducked under it.
        if music_path and Path(music_path).exists():
            print("   assemble: muxing voice + music bed...")
            music_dur = _probe(music_path)
            looped_music = work / "music_looped.m4a"
            if music_dur > 0 and music_dur < voice_dur:
                reps = _math.ceil(voice_dur / music_dur)
                mlist = work / "mlist.txt"
                mlist.write_text("".join(f"file '{Path(music_path).resolve()}'\n" for _ in range(reps)))
                _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
                      "-c", "copy", str(looped_music)], "loop music")
                music_src = looped_music
            else:
                music_src = Path(music_path)
            # Mix: voice at 1.15, music at 0.07 (original VOICE_LEVEL/MUSIC_LEVEL).
            _run([
                "ffmpeg", "-y",
                "-i", str(silent),
                "-i", str(voice_path),
                "-i", str(music_src),
                "-filter_complex",
                "[1:a]volume=1.15[v];[2:a]volume=0.07[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                "-map", "0:v:0", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-t", f"{voice_dur:.3f}",
                str(out_path),
            ], "mux voice+music")
        else:
            print("   assemble: muxing voiceover...")
            _run([
                "ffmpeg", "-y",
                "-i", str(silent),
                "-i", str(voice_path),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-map", "0:v:0", "-map", "1:a:0",
                "-t", f"{voice_dur:.3f}",
                str(out_path),
            ], "mux voice")

        final_dur = _probe(out_path)
        print(f"   assemble: DONE {final_dur:.1f}s ({final_dur/60:.1f} min) -> {out_path}")
    finally:
        _shutil.rmtree(work, ignore_errors=True)

    return out_path


def assemble_moviepy(clip_paths: list, voice_path: Path, out_path: Path,
             music_path=None) -> Path:
    """
    Even-spacing assembly. The narration is the master track. Every clip is
    shown for exactly z = narration_duration / number_of_clips seconds, so:
      - every clip is always used (no footage cut off, the v2 shot-68 bug)
      - the video length always exactly matches the narration
      - clips are roughly (not tightly) aligned to the words, which is fine for
        atmospheric content where images set mood rather than illustrate
        sentences literally.

    If z is shorter than a clip's native length, the clip is trimmed to its
    first z seconds. If z is longer (rare — would mean very few clips over long
    narration), the clip is slowed to fill z so there's never a frozen gap.
    """
    voice = AudioFileClip(str(voice_path))
    n = len(clip_paths)
    if n == 0:
        raise SystemExit("No clips to assemble.")

    # Auto-align voiceover with Whisper before computing per-shot durations.
    # Adds 3-5 min on first run, idempotent on subsequent runs.
    _storyboard_path = voice_path.parent / "storyboard.json"
    if _storyboard_path.exists():
        _auto_align_with_whisper(voice_path, _storyboard_path)

    # Per-shot duration source priority:
    # 1. Whisper-measured audio_duration in storyboard.json (frame-accurate)
    # 2. Word-count proxy from narration text (introduces drift over long videos)
    # 3. Uniform per-clip (legacy fallback)
    durations = None
    try:
        storyboard_path = Path(clip_paths[0]).parent.parent / "storyboard.json"
        if storyboard_path.exists():
            import json as _json
            with open(storyboard_path) as _f:
                _data = _json.load(_f)
            _shots = _data if isinstance(_data, list) else _data.get("beats", _data.get("shots", []))
            if len(_shots) == n:
                # Prefer Whisper-measured durations if present on every shot
                if all("audio_duration" in s for s in _shots):
                    durations = [s["audio_duration"] for s in _shots]
                    print(f"   assemble: Whisper-measured per-shot durations")
                    print(f"   assemble: range {min(durations):.2f}s - {max(durations):.2f}s, total {sum(durations):.1f}s")
                else:
                    # Fall back to word-count proxy
                    _words = [max(1, len(s.get("narration", "").split())) for s in _shots]
                    _total = sum(_words)
                    durations = [voice.duration * (w / _total) for w in _words]
                    print(f"   assemble: word-count-proxy per-shot durations (run align_with_whisper.py for frame-accurate sync)")
                    print(f"   assemble: range {min(durations):.2f}s - {max(durations):.2f}s, total {voice.duration:.1f}s")
    except Exception as _e:
        print(f"   assemble: storyboard sync failed ({_e}), falling back to uniform")
        durations = None

    if durations is None:
        z = voice.duration / n
        durations = [z] * n
        print(f"   assemble: uniform narration {voice.duration:.1f}s / {n} clips = {z:.2f}s per clip")

    timed = []
    for p, d in zip(clip_paths, durations):
        clip = VideoFileClip(str(p))
        if clip.duration >= d:
            # Trim down to target duration
            timed.append(clip.subclip(0, d))
        else:
            # Clip shorter than target slot — slow it to fill
            factor = clip.duration / d
            from moviepy.editor import vfx
            timed.append(clip.fx(vfx.speedx, factor))

    video = concatenate_videoclips(timed, method="compose")
    # Guard against tiny rounding drift so audio never gets clipped
    video = video.subclip(0, min(video.duration, voice.duration))

    # Build the audio mix
    audio_layers = [voice.volumex(VOICE_LEVEL)]
    if music_path and Path(music_path).exists():
        from moviepy.editor import concatenate_audioclips
        base = AudioFileClip(str(music_path)).volumex(MUSIC_LEVEL)
        # Loop the music to cover the full narration. afx.audio_loop is
        # unreliable across moviepy versions (it silently under-fills — the
        # music-stops-at-3:57 bug), so build the loop explicitly by repeating
        # the track enough times to exceed the voice, then trim to exact length.
        if base.duration < voice.duration:
            import math
            repeats = math.ceil(voice.duration / base.duration)
            looped = concatenate_audioclips([base] * repeats)
        else:
            looped = base
        music = looped.subclip(0, voice.duration)
        audio_layers.append(music)

    mix = CompositeAudioClip(audio_layers) if len(audio_layers) > 1 else audio_layers[0]
    final = video.set_audio(mix)
    final.write_videofile(str(out_path), codec="libx264", audio_codec="aac",
                          fps=24, verbose=False, logger=None)

    for c in timed:
        c.close()
    voice.close()
    final.close()
    return out_path


# ── Project state on disk ────────────────────────────────────────────────────────

def proj_paths(project):
    project = Path(project).expanduser()
    # Auto-resolve bare project names to projects/<name> to match channel architecture.
    # "mary_celeste" -> "projects/mary_celeste" when run from channel root.
    # Absolute paths and already-prefixed paths are left alone.
    if not project.is_absolute() and len(project.parts) == 1 and Path('projects').is_dir():
        project = Path('projects') / project
    return {
        "root":       project,
        "script":     project / "script.txt",
        "storyboard": project / "storyboard.json",
        "stills":     project / "stills",
        "clips":      project / "clips",
        "voice":      project / "voiceover.mp3",
        "final":      project / "final_video.mp4",
    }


# ── Phase commands ────────────────────────────────────────────────────────────

def _load_beats_with_canon(beats_path: Path) -> tuple[list, dict]:
    """
    Load a beat-script JSON file in either format:

    1. LEGACY (still supported): a flat list of beats, no canon:
       [
         {"narration": "...", "image_prompt": "...", "motion_prompt": "..."},
         ...
       ]

    2. NEW: a dict with an optional 'canon' block plus the beats list:
       {
         "canon": {
           "hartley": "Wallace Hartley, 33, dark hair, dark bandsman tunic...",
           "hartley_deck": "{hartley}, with a brown wool overcoat over the uniform",
           "band_deck": "Six Edwardian string musicians in matching dark uniforms..."
         },
         "beats": [
           {"narration": "...",
            "image_prompt": "{hartley_deck} plays his violin on the cold deck...",
            "motion_prompt": "..."},
           ...
         ]
       }

    Canon entries can reference other canon entries via {tag} syntax — they're
    resolved recursively (so hartley_deck can build on hartley). This is the
    consistency-injection mechanism: anything that appears across multiple shots
    (a character, a uniform, an ensemble) lives in one canonical descriptor and
    gets substituted into every prompt that references it, so the model can't
    invent its own version per shot.

    Channel-level base canon (from channel.json) is auto-merged underneath the
    beat-script's own canon — so e.g. Success Coach beat-scripts can use
    `{coach_avatar}` without redefining it. Beat-script canon entries override
    channel base canon entries with the same key, so a video can locally
    redefine a base entry if needed for that one episode.

    Returns (beats_list, merged_canon_dict).
    """
    data = json.loads(beats_path.read_text())
    if isinstance(data, list):
        beats, canon = data, {}
    elif isinstance(data, dict) and "beats" in data:
        beats = data["beats"]
        canon = data.get("canon", {})
        if not isinstance(canon, dict):
            raise SystemExit(f"Canon block in {beats_path} must be a dict of tag -> description.")
    else:
        raise SystemExit(
            f"Unrecognised beats format in {beats_path}. Expected either a list of beats, "
            "or a dict with 'beats' (and optional 'canon') keys."
        )

    # Layer channel base_canon underneath beat-script canon (beat-script wins on key collision).
    channel_config = load_channel_config(strict=True, anchor=beats_path)
    base_canon = channel_config.get("base_canon", {})
    if base_canon:
        merged = dict(base_canon)
        merged.update(canon)
        canon = merged

    return beats, canon


def _expand_canon(text: str, canon: dict, max_depth: int = 10) -> str:
    """
    Replace {tag} references in `text` with the corresponding canon entry.
    Canon entries can themselves contain {tag} references — resolved recursively
    up to max_depth iterations. Fails loudly on unknown tags (so typos don't
    silently produce vague prompts) and on circular references.
    """
    import re
    pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
    for _ in range(max_depth):
        tags = pattern.findall(text)
        if not tags:
            return text
        unknown = [t for t in tags if t not in canon]
        if unknown:
            raise SystemExit(
                f"Unknown canon tag(s) in prompt: {unknown}. "
                f"Available canon tags: {sorted(canon.keys()) or '(none defined)'}"
            )
        text = pattern.sub(lambda m: canon[m.group(1)], text)
    raise SystemExit(
        f"Canon expansion exceeded depth {max_depth} — likely a circular reference in the canon block."
    )


def cmd_stills(args):
    p = proj_paths(args.project)
    p["root"].mkdir(parents=True, exist_ok=True)
    p["stills"].mkdir(exist_ok=True)

    if bool(getattr(args, "beats", None)) == bool(args.script):
        raise SystemExit("Provide exactly one of --beats (pre-written) or --script (prose to slice).")

    if getattr(args, "beats", None):
        # Beat-script path: a pre-written, pre-beaten storyboard JSON is supplied
        # directly. The script IS the shot list — no Claude slicing, no drift.
        # Each beat must have: narration, image_prompt, motion_prompt. The file
        # may also include a top-level `canon` block of named descriptors; those
        # get substituted into any {tag} references in the prompts. The fully
        # expanded prompts are saved to storyboard.json so the rest of the
        # pipeline (finish, restill) never has to know about the canon.
        beats, canon = _load_beats_with_canon(Path(args.beats).expanduser())
        if canon:
            print(f"Canon block loaded with {len(canon)} tag(s): {sorted(canon.keys())}")
        # Normalise: ensure sequential indices, required fields, and canon-expansion.
        _default_motion = (load_channel_config(strict=True, anchor=Path(args.project)).get("default_motion")
                           or CHANNEL_DEFAULTS["default_motion"])
        shots = []
        for i, b in enumerate(beats, 1):
            image_prompt = _expand_canon(b["image_prompt"].strip(), canon)
            motion_prompt = _expand_canon(
                (b.get("motion_prompt") or _default_motion).strip(),
                canon,
            )
            shots.append({
                "index": i,
                "narration": b.get("narration", "").strip(),
                "image_prompt": image_prompt,
                "motion_prompt": motion_prompt,
            })
        # Save the concatenated narration as the script (used later for metadata).
        p["script"].write_text(" ".join(s["narration"] for s in shots))
        p["storyboard"].write_text(json.dumps(shots, indent=2))
        print(f"OK Beat-script ingested: {len(shots)} beats -> {p['storyboard']}")
    else:
        script = Path(args.script).expanduser().read_text().strip()
        p["script"].write_text(script)
        print("Building storyboard from script (Claude)...")
        shots = build_storyboard(script)
        p["storyboard"].write_text(json.dumps(shots, indent=2))
        print(f"OK Storyboard: {len(shots)} shots -> {p['storyboard']}")

    if getattr(args, "storyboard_only", False):
        print("Storyboard-only mode: skipping still generation.")
        return
    print(f"\nGenerating {len(shots)} stills with {IMAGE_MODEL}...")
    force = bool(getattr(args, "force", False))
    for s in shots:
        out = p["stills"] / f"shot_{s['index']:03d}.png"
        if out.exists() and not force:  # resume-safe: skip stills already on disk
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
            continue
        print(f"  [{s['index']}/{len(shots)}] {s['image_prompt'][:60]}...")
        generate_still(s["image_prompt"], out)
    print(f"\nOK Stills done -> {p['stills']}")
    print("\nNEXT: open the stills folder and review every frame.")
    print("Fix a bad one with:  restill --project <dir> --shot N")
    print("When happy, run:     finish --project <dir>")


def cmd_restill(args):
    p = proj_paths(args.project)
    shots = json.loads(p["storyboard"].read_text())
    shot = next(s for s in shots if s["index"] == args.shot)
    out = p["stills"] / f"shot_{shot['index']:03d}.png"

    # If you caught a spell-breaker, bank it as a permanent global rule FIRST,
    # so this reshoot — and every future video — avoids it.
    if args.add_rule:
        add_negative_rule(args.add_rule)

    prompt = args.prompt or shot["image_prompt"]
    if args.prompt:
        shot["image_prompt"] = args.prompt
        p["storyboard"].write_text(json.dumps(shots, indent=2))

    print(f"Regenerating shot {args.shot}...")
    generate_still(prompt, out)
    print(f"OK -> {out}")


def _tiered_kling_count(project_root, override=None):
    """TIERED RENDER policy N: first N beats Kling, the rest Ken Burns.
    Precedence: --kling-count override > render_policy.json > default 40."""
    import json as _json
    if override is not None:
        return max(0, int(override))
    rp = project_root / "render_policy.json"
    if rp.is_file():
        try:
            return max(0, int(_json.loads(rp.read_text()).get("kling_count", 40)))
        except Exception:
            return 40
    return 40


def _tiered_beat_index(engine_shot, project_root):
    """Map a 1-based engine shot to its 0-based timeline beat index via _index.json.
    Falls back to engine_shot-1 (pure Mode A) when the map is absent."""
    import json as _json
    idx = project_root / "_index.json"
    if idx.is_file():
        try:
            m = _json.loads(idx.read_text())
            if str(engine_shot) in m:
                return int(m[str(engine_shot)])
        except Exception:
            pass
    return engine_shot - 1


def _tiered_duration(beat_index, project_root):
    """Whisper-measured duration for a beat from durations.json, or None if absent."""
    import json as _json
    dp = project_root / "durations.json"
    if dp.is_file():
        try:
            e = _json.loads(dp.read_text()).get(str(beat_index))
            if e and "duration" in e:
                return float(e["duration"])
        except Exception:
            pass
    return None


def cmd_finish(args):
    p = proj_paths(args.project)
    p["clips"].mkdir(exist_ok=True)
    shots = json.loads(p["storyboard"].read_text())
    script = p["script"].read_text()

    # ── Assemble-only fast path ──────────────────────────────────────────────
    # Re-stitch an already-rendered project using the current assembly logic
    # (e.g. after changing clip-duration logic). Uses existing clips, voiceover,
    # and music on disk — no Kling, no Inworld, no fal, no cost. Errors clearly
    # if a required piece is missing.
    if getattr(args, "assemble_only", False):
        print("Assemble-only: re-stitching from existing clips/voice/music (no rendering)...")
        clip_paths = []
        missing = []
        for s in shots:
            clip = p["clips"] / f"shot_{s['index']:03d}.mp4"
            if not clip.exists():
                missing.append(clip.name)
            clip_paths.append(clip)
        if missing:
            raise SystemExit(f"Cannot assemble — missing clips: {missing[:5]}"
                             f"{' ...' if len(missing) > 5 else ''}")
        # assemble-only: root-level artifacts (voiceover, final, music) live at the
        # PROJECT ROOT, one level above p["root"] when --project is "<slug>/modea"
        # (same as the normal path's project_root = p["root"].parent). Clips stay under modea.
        _asm_root = p["root"].parent
        _voice = _asm_root / "voiceover.mp3"
        _final = _asm_root / "final_video.mp4"
        if not _voice.exists():
            raise SystemExit(f"Cannot assemble — missing voiceover: {_voice}")

        music = None
        if args.music:
            music = Path(args.music).expanduser()
        elif not args.no_music:
            music_path = _asm_root / "music.mp3"
            if music_path.exists():
                music = music_path
            else:
                print("   (no music.mp3 found — assembling without music bed)")

        print("\nAssembling final video...")
        assemble(clip_paths, _voice, _final, music_path=music)
        print(f"\nDONE -> {_final}")
        return

    project_root = p["root"].parent  # durations.json / _index.json / render_policy.json live one level up
    kling_count = _tiered_kling_count(project_root, getattr(args, "kling_count", None))
    plan = []
    for s in shots:
        bi = _tiered_beat_index(s["index"], project_root)
        engine = "kling" if bi < kling_count else "kenburns"
        plan.append((s, bi, engine))
    n_kling = sum(1 for _, _, e in plan if e == "kling")
    n_kb = len(plan) - n_kling
    print(f"TIERED RENDER: N={kling_count}  ->  {n_kling} Kling (~${n_kling * 0.42:.2f}) "
          f"+ {n_kb} Ken Burns (free)")
    if getattr(args, "plan", False):
        for s, bi, engine in plan:
            dur = _tiered_duration(bi, project_root)
            durtxt = (f"{dur:.2f}s" if dur is not None else "?")
            print(f"  shot {s['index']:03d}  beat {bi:>3}  {durtxt:>7}  -> {engine}")
        print("(--plan: routing only, nothing rendered, no cost)")
        return
    clip_paths = []
    for s, bi, engine in plan:
        still = p["stills"] / f"shot_{s['index']:03d}.png"
        clip  = p["clips"] / f"shot_{s['index']:03d}.mp4"
        if clip.exists() and not args.force:
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
        elif engine == "kling":
            print(f"  [{s['index']}/{len(shots)}] Kling animating...")
            animate_still(still, s["motion_prompt"], clip)
        else:
            dur = _tiered_duration(bi, project_root) or float(SHOT_DURATION)
            print(f"  [{s['index']}/{len(shots)}] Ken Burns ({dur:.2f}s, free)...")
            ken_burns_still(still, clip, dur)
        clip_paths.append(clip)

    if getattr(args, "animate_only", False):
        print(f"\nAnimate-only: {len(clip_paths)} clips in {p['clips']}, "
              f"stopping before narrate/score/assemble (audio + assembly are separate legs).")
        return

    print("\nNarrating script (Victor)...")
    generate_voiceover(script, p["voice"])
    print(f"OK Voiceover -> {p['voice']}")

    # Music bed: auto-generated via fal by default (no manual step).
    # --no-music skips it; --music FILE uses your own track instead.
    music = None
    if args.music:
        music = Path(args.music).expanduser()
    elif not args.no_music:
        music_path = p["root"] / "music.mp3"
        if music_path.exists() and not args.force:
            print("\nMusic bed already generated, reusing.")
        else:
            print("\nGenerating music bed (fal / ElevenLabs Music)...")
            generate_music(music_path)
            print(f"OK Music -> {music_path}")
        music = music_path

    print("\nAssembling final video...")
    assemble(clip_paths, p["voice"], p["final"], music_path=music)
    print(f"\nDONE -> {p['final']}")


# ── Per-shot SFX (STUBBED — switch on later, via fal not ElevenLabs) ───────────
# When ready: in build_storyboard, also ask Claude for a "sound_prompt" per shot,
# generate each via a fal text-to-audio endpoint, and add them as a third
# CompositeAudioClip layer at SFX_LEVEL, each set_start() to its shot's offset.


# ── CLI ─────────────────────────────────────────────────────────────────────────

def cmd_kenburns(args):
    """Isolation test for the Ken Burns producer: still -> duration-correct mp4.
    Free (ffmpeg only). Prints the measured duration so length can be verified."""
    import subprocess
    still = Path(args.still).expanduser()
    out = Path(args.out).expanduser()
    if not still.exists():
        raise SystemExit(f"still not found: {still}")
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Ken Burns: {still.name} -> {out.name} @ {args.duration:.2f}s ...")
    ken_burns_still(still, out, args.duration)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(out)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    print(f"OK -> {out}")
    print(f"   measured duration: {r.stdout.strip()}s  (target {args.duration:.2f}s)")


def cmd_rulebook(args):
    if args.add:
        add_negative_rule(args.add)
    if args.remove:
        remove_negative_rule(args.remove)
    if args.view or (not args.add and not args.remove):
        rb = load_rulebook()
        print(json.dumps(rb, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Final Hours recreation pipeline")
    sub = ap.add_subparsers(dest="command", required=True)

    a = sub.add_parser("stills", help="script -> storyboard -> stills (cheap)")
    a.add_argument("--script", default=None, help="plain prose script (Claude slices it into shots)")
    a.add_argument("--beats", default=None,
                   help="pre-written beat-script JSON (used directly as storyboard, no slicing); "
                        "either a flat list of beats, or a dict with optional 'canon' block + 'beats' list "
                        "where canon tags like {hartley} get substituted into prompts")
    a.add_argument("--project", required=True)
    a.add_argument("--storyboard-only", action="store_true", help="generate storyboard JSON and stop (no image generation)")
    a.add_argument("--force", action="store_true", help="re-generate stills even if they already exist on disk")
    a.set_defaults(func=cmd_stills)

    b = sub.add_parser("restill", help="regenerate one shot's still")
    b.add_argument("--project", required=True)
    b.add_argument("--shot", type=int, required=True)
    b.add_argument("--prompt", default=None, help="optional new image prompt")
    b.add_argument("--add-rule", default=None,
                   help="bank a spell-breaker as a permanent global negative rule, e.g. --add-rule 'visible ribs on animals'")
    b.set_defaults(func=cmd_restill)

    c = sub.add_parser("finish", help="animate + narrate + assemble")
    c.add_argument("--project", required=True)
    c.add_argument("--music", default=None, help="use your own music mp3 instead of generating one")
    c.add_argument("--no-music", action="store_true", help="skip the music bed entirely")
    c.add_argument("--force", action="store_true", help="re-animate existing clips + regenerate music")
    c.add_argument("--animate-only", action="store_true",
                   help="animate stills to clips, then STOP (no narrate/score/assemble)")
    c.add_argument("--assemble-only", action="store_true",
                   help="re-stitch from existing clips/voice/music only (no rendering, no cost)")
    c.add_argument("--kling-count", type=int, default=None,
                   help="TIERED RENDER: render the first N beats with Kling, the rest with free "
                        "Ken Burns (overrides render_policy.json; default 40)")
    c.add_argument("--plan", action="store_true",
                   help="TIERED RENDER: print the Kling/Ken-Burns routing and exit (no render, no cost)")
    c.set_defaults(func=cmd_finish)

    # TIERED RENDER (step a) — isolation test for the Ken Burns producer (no fal, no cost)
    e = sub.add_parser("kenburns",
                       help="still -> ffmpeg ken-burns zoom clip at a target duration (TIERED RENDER floor)")
    e.add_argument("--still", required=True, help="path to the still PNG")
    e.add_argument("--out", required=True, help="output mp4 path")
    e.add_argument("--duration", type=float, default=9.0, help="target clip duration in seconds")
    e.set_defaults(func=cmd_kenburns)

    # Rulebook management — no project needed
    d = sub.add_parser("rulebook", help="view or edit the rulebook (the moat)")
    d.add_argument("--view", action="store_true", help="print the current rulebook")
    d.add_argument("--add", default=None, help="add a negative rule")
    d.add_argument("--remove", default=None, help="remove negative rule(s) matching this text")
    d.set_defaults(func=cmd_rulebook)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
