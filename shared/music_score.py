"""
Music Scoring Pipeline — Scene-Level Jamendo Integration
=========================================================
Reads storyboard.json music_category transitions, groups consecutive same-category
shots into music regions, queries Jamendo per region, downloads tracks, and
assembles a single pre-mixed music.mp3 with crossfades at region boundaries.

This REPLACES the fal-generated single-track approach. Output is still a single
music.mp3 in the project root, so assemble() in recreation_pipeline.py works
unchanged — it just consumes a smarter music file.

Usage (run from channel root, e.g. final-hours/):
    python3 ../shared/music_score.py --project projects/mary_celeste

What it does:
1. Reads project/storyboard.json
2. Validates each shot has music_category, audio_start, audio_duration
3. Groups consecutive same-category shots into regions
4. For each region: queries Jamendo with category params, picks first usable track,
   downloads to project/audio/
5. Composites tracks into project/music.mp3 with 3s crossfades
6. Writes project/audio_credits.txt with attribution for YouTube description

What it deliberately does NOT do (Phase 2):
- Harmonic key matching across regions
- BPM compatibility scoring
- Popularity floor / popularity-aware filtering
- Per-channel track exclusion list (to prevent house-track drift)
- Multi-track weighted scoring (currently picks first usable result)
"""

import os
import sys
import json
import math
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Portable CA baseline: point requests at certifi's bundle on every machine.
# (On the ABB laptop, ~/combined_cacert.pem via ssl_compat layers Zscaler on top.)
import os as _os_for_ssl
try:
    import certifi as _certifi
    _os_for_ssl.environ.setdefault("SSL_CERT_FILE", _certifi.where())
    _os_for_ssl.environ.setdefault("REQUESTS_CA_BUNDLE", _certifi.where())
except ImportError:
    pass

import requests

from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout


# ── Env / config ────────────────────────────────────────────────────────────────
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")
if not JAMENDO_CLIENT_ID:
    raise SystemExit("Missing JAMENDO_CLIENT_ID in .env")

JAMENDO_API = "https://api.jamendo.com/v3.0/tracks/"

# Crossfade between regions. 3s is documentary standard — long enough to mask
# the transition, short enough that the new mood lands quickly.
CROSSFADE_SECONDS = 3.0

# Minimum buffer beyond region duration when picking a track. Prevents picking
# a track that's exactly region_duration since the crossfade-out eats the last
# 3 seconds. 5s buffer = safe.
TRACK_DURATION_BUFFER = 5.0


# ── Jamendo category mapping ───────────────────────────────────────────────────
# These mirror the categories in shared/jamendo_search.py but we keep them here
# for self-contained operation. Update both if you tune one.
CATEGORIES = {
    "opening-portent": {
        "fuzzytags": "cinematic dark ambient",
        "tags": "soundtrack",
        "speed": "verylow low",
        "vocalinstrumental": "instrumental",
    },
    "exposition-restrained": {
        "fuzzytags": "ambient calm minimal",
        "tags": "soundtrack",
        "speed": "low medium",
        "vocalinstrumental": "instrumental",
    },
    "rising-stakes": {
        "fuzzytags": "tension building cinematic",
        "tags": "soundtrack",
        "speed": "medium high",
        "vocalinstrumental": "instrumental",
    },
    "climactic-stillness": {
        "fuzzytags": "ambient sad cinematic",
        "tags": "soundtrack",
        "speed": "verylow low",
        "vocalinstrumental": "instrumental",
    },
    "aftermath-reflection": {
        "fuzzytags": "piano emotional sad",
        "tags": "soundtrack",
        "speed": "verylow low",
        "vocalinstrumental": "instrumental",
    },
}


# ── Core: group shots into regions ──────────────────────────────────────────────

def group_into_regions(shots):
    """
    Walk the storyboard shot list, group consecutive same-category shots
    into music regions. Returns a list of region dicts:
        {
            "category": "climactic-stillness",
            "start": 245.32,
            "end": 387.91,
            "duration": 142.59,
            "shot_indices": [41, 42, 43, ..., 60]
        }
    """
    if not shots:
        return []

    # Validate every shot has required fields
    required = ["music_category", "audio_start", "audio_duration"]
    for s in shots:
        for field in required:
            if field not in s:
                raise SystemExit(
                    f"Shot {s.get('index', '?')} missing required field '{field}'. "
                    f"Run annotate_music_categories.py first to add music_category "
                    f"to existing storyboards."
                )

    regions = []
    current = {
        "category": shots[0]["music_category"],
        "start": shots[0]["audio_start"],
        "end": shots[0]["audio_start"] + shots[0]["audio_duration"],
        "shot_indices": [shots[0]["index"]],
    }

    for s in shots[1:]:
        if s["music_category"] == current["category"]:
            # Extend the current region
            current["end"] = s["audio_start"] + s["audio_duration"]
            current["shot_indices"].append(s["index"])
        else:
            # Close the current region, start a new one
            current["duration"] = current["end"] - current["start"]
            regions.append(current)
            current = {
                "category": s["music_category"],
                "start": s["audio_start"],
                "end": s["audio_start"] + s["audio_duration"],
                "shot_indices": [s["index"]],
            }

    current["duration"] = current["end"] - current["start"]
    regions.append(current)
    return regions


# ── Core: query Jamendo for a region ────────────────────────────────────────────

def find_track_for_region(category, region_duration, exclude_ids=None):
    """
    Query Jamendo for a track matching the category, long enough to cover
    region_duration + buffer (so the crossfade-out has room).

    exclude_ids: set/list of track IDs to skip (typically the previous region's
    track) — prevents adjacent regions from using the same track, which would
    sound like one long uninterrupted music section to the listener.
    """
    exclude_ids = set(exclude_ids or [])
    if category not in CATEGORIES:
        raise SystemExit(f"Unknown music category: '{category}'. "
                         f"Valid: {', '.join(CATEGORIES.keys())}")

    params = {
        "client_id": JAMENDO_CLIENT_ID,
        "format": "jsonpretty",
        "limit": 20,  # over-fetch so we have alternatives after duration filtering
        "include": "musicinfo stats licenses",
        "order": "popularity_total_desc",
        **CATEGORIES[category],
    }

    response = requests.get(JAMENDO_API, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "headers" in data and data["headers"].get("error_message"):
        raise SystemExit(f"Jamendo API error: {data['headers']['error_message']}")

    candidates = data.get("results", [])
    min_duration_needed = region_duration + TRACK_DURATION_BUFFER

    for track in candidates:
        if str(track.get("id")) in exclude_ids:
            continue
        if not track.get("audiodownload_allowed", False):
            continue
        if not track.get("audiodownload"):
            continue
        try:
            track_dur = float(track.get("duration", 0))
        except (TypeError, ValueError):
            continue
        if track_dur >= min_duration_needed:
            return track

    # Fallback: no track meets duration. Take longest downloadable one we found
    # and we'll loop it during assembly.
    downloadable = [t for t in candidates
                    if t.get("audiodownload_allowed") and t.get("audiodownload")
                    and str(t.get("id")) not in exclude_ids]
    if downloadable:
        longest = max(downloadable, key=lambda t: float(t.get("duration", 0)))
        print(f"   WARN: no Jamendo track >= {min_duration_needed:.0f}s for {category}. "
              f"Using longest available ({float(longest['duration']):.0f}s, will loop).")
        return longest

    raise SystemExit(f"No usable Jamendo tracks for category '{category}' "
                     f"(region: {region_duration:.0f}s, needed >= {min_duration_needed:.0f}s)")


# ── Core: download a track ──────────────────────────────────────────────────────

def download_track(track, audio_dir):
    """Download an MP3 into audio_dir/, return the local file path."""
    audio_dir.mkdir(parents=True, exist_ok=True)

    safe_artist = "".join(c if c.isalnum() or c in " -_" else "_" for c in track["artist_name"])
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in track["name"])
    filename = f"{safe_artist} - {safe_name} [{track['id']}].mp3"
    filepath = audio_dir / filename

    if filepath.exists():
        print(f"   EXISTS: {filename}")
        return filepath

    print(f"   Downloading: {filename}")
    r = requests.get(track["audiodownload"], stream=True, timeout=60)
    r.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return filepath


# ── Core: build the music timeline with crossfades ──────────────────────────────

def assemble_music_timeline(regions, total_duration, out_path):
    """
    Composite per-region track files into a single music.mp3 covering the
    full narration duration. Adjacent regions crossfade by CROSSFADE_SECONDS.

    Each region's track is:
    - Trimmed to its region_duration + CROSSFADE_SECONDS (for the fade tail)
    - Looped if too short
    - Faded in at the region start (except for the very first region)
    - Faded out at the region end (except for the very last region)
    - set_start() to the region's start time minus crossfade overlap

    The CompositeAudioClip overlays them so the fades blend naturally.
    """
    layers = []

    for i, region in enumerate(regions):
        track_path = region["track_path"]
        region_start = region["start"]
        region_dur = region["duration"]
        is_first = (i == 0)
        is_last = (i == len(regions) - 1)

        # Slice duration depends on position. First region ends exactly at its
        # boundary (no extension) — its fadeout is the LAST CROSSFADE seconds of
        # region_dur. Non-first regions start CROSSFADE seconds early to overlap
        # with the previous region's fadeout, so their slice is region_dur +
        # CROSSFADE. This produces a TRUE crossfade where both tracks are at
        # 50% at the midpoint, rather than both at 100% briefly.
        if is_first:
            slice_duration = region_dur
        else:
            slice_duration = region_dur + CROSSFADE_SECONDS

        # Load the track
        full_clip = AudioFileClip(str(track_path))
        track_duration = full_clip.duration

        # Pick a START OFFSET inside the track that avoids the intro and outro.
        # Documentary scoring principle: tracks usually have weak intros (sparse,
        # building) and outros (fading) — the best material is in the middle.
        # Skip first INTRO_SKIP seconds, leave OUTRO_BUFFER seconds at the end.
        INTRO_SKIP = 30.0
        OUTRO_BUFFER = 20.0
        usable_start_max = track_duration - slice_duration - OUTRO_BUFFER

        if usable_start_max <= INTRO_SKIP:
            # Track too short to skip intro — loop from start instead
            print(f"   Track {track_path.name} ({track_duration:.0f}s) too short for offset; looping from 0")
            full_clip.close()
            if track_duration < slice_duration:
                repeats = math.ceil(slice_duration / track_duration)
                base = AudioFileClip(str(track_path))
                clip = concatenate_audioclips([base] * repeats)
            else:
                clip = AudioFileClip(str(track_path))
            clip = clip.subclip(0, min(slice_duration, clip.duration))
        else:
            # Pick a random offset between INTRO_SKIP and usable_start_max.
            # Use region index as seed so the same region always picks the same
            # offset (deterministic re-runs). Different regions get different offsets.
            import random
            rng = random.Random(f"{track_path.name}_{i}")
            offset = rng.uniform(INTRO_SKIP, usable_start_max)
            print(f"   Track offset: {offset:.1f}s into {track_duration:.0f}s track "
                  f"(avoiding 0-{INTRO_SKIP:.0f}s intro and last {OUTRO_BUFFER:.0f}s)")
            clip = full_clip.subclip(offset, offset + slice_duration)

        # Apply fades
        is_first = (i == 0)
        is_last = (i == len(regions) - 1)

        if not is_first:
            # Crossfade IN with the previous region's fade out
            clip = audio_fadein(clip, CROSSFADE_SECONDS)

        if not is_last:
            # Crossfade OUT with the next region's fade in
            clip = audio_fadeout(clip, CROSSFADE_SECONDS)

        # Place this region at its narration timestamp, but pull it forward by
        # CROSSFADE_SECONDS so the fade-in overlaps the previous region's tail.
        # First region starts exactly at 0.
        start_offset = region_start if is_first else region_start - CROSSFADE_SECONDS
        start_offset = max(0.0, start_offset)
        clip = clip.set_start(start_offset)
        layers.append(clip)

    # Composite all regions into one timeline
    mix = CompositeAudioClip(layers)

    # Ensure the output covers exactly the narration duration
    mix = mix.set_duration(total_duration)
    # CompositeAudioClip doesn't auto-set fps when child clips have been modified
    # via subclip/fadein/fadeout — set it explicitly. 44100 Hz is CD-quality stereo.
    mix.fps = 44100

    print(f"   Writing {out_path} ({total_duration:.1f}s)...")
    mix.write_audiofile(str(out_path), codec="libmp3lame", bitrate="192k",
                        verbose=False, logger=None)

    # Cleanup
    for c in layers:
        try:
            c.close()
        except Exception:
            pass
    mix.close()
    return out_path


# ── Attribution: write audio_credits.txt for YouTube description ───────────────

def write_credits(regions, project_path):
    """Write a paste-ready attribution block for YouTube descriptions."""
    credits_path = project_path / "audio_credits.txt"
    lines = ["MUSIC CREDITS", "=" * 60, "", "Tracks licensed from Jamendo under Creative Commons:", ""]

    seen = set()
    for region in regions:
        track = region["track"]
        key = track["id"]
        if key in seen:
            continue
        seen.add(key)
        license_url = track.get("license_ccurl", "unknown license")
        lines.append(
            f"- \"{track['name']}\" by {track['artist_name']}"
        )
        lines.append(f"  Jamendo ID {track['id']} | {license_url}")
        lines.append("")

    credits_path.write_text("\n".join(lines))
    return credits_path


# ── Main entrypoint ─────────────────────────────────────────────────────────────

def music_score(project_path):
    """
    Score an entire project end-to-end. Reads storyboard, picks tracks per
    scene, downloads them, assembles single music.mp3.
    """
    project_path = Path(project_path).expanduser()
    if not project_path.is_absolute() and len(project_path.parts) == 1 and Path("projects").is_dir():
        project_path = Path("projects") / project_path

    storyboard_path = project_path / "storyboard.json"
    if not storyboard_path.exists():
        raise SystemExit(f"Missing storyboard.json at {storyboard_path}")

    shots = json.loads(storyboard_path.read_text())
    if not isinstance(shots, list):
        shots = shots.get("beats", shots.get("shots", []))

    print(f"Loaded {len(shots)} shots from {storyboard_path.name}")

    # Group into regions
    regions = group_into_regions(shots)
    total_duration = max(r["end"] for r in regions)
    print(f"Grouped into {len(regions)} music regions, total {total_duration:.1f}s:")
    for i, r in enumerate(regions):
        print(f"  [{i+1}] {r['category']:25s} "
              f"shots {r['shot_indices'][0]:3d}-{r['shot_indices'][-1]:3d}  "
              f"{r['start']:6.1f}s -> {r['end']:6.1f}s  ({r['duration']:5.1f}s)")

    # Find + download a track per region
    audio_dir = project_path / "audio"
    print(f"\nFetching tracks from Jamendo...")
    prev_track_id = None
    for region in regions:
        print(f"\n[{region['category']}] (region {region['duration']:.0f}s)")
        exclude = {str(prev_track_id)} if prev_track_id else set()
        track = find_track_for_region(region["category"], region["duration"],
                                       exclude_ids=exclude)
        track_path = download_track(track, audio_dir)
        region["track"] = track
        region["track_path"] = track_path
        prev_track_id = track["id"]

    # Assemble the timeline
    print(f"\nAssembling music timeline with {CROSSFADE_SECONDS}s crossfades...")
    out_path = project_path / "music.mp3"
    assemble_music_timeline(regions, total_duration, out_path)
    print(f"OK Music -> {out_path}")

    # Write attribution
    credits_path = write_credits(regions, project_path)
    print(f"OK Credits -> {credits_path}")

    return out_path


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Scene-level music scoring via Jamendo")
    ap.add_argument("--project", required=True,
                    help="Project path (e.g. projects/mary_celeste). "
                         "Reads storyboard.json, writes music.mp3 + audio_credits.txt.")
    args = ap.parse_args()
    music_score(args.project)


if __name__ == "__main__":
    main()
