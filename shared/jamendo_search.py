#!/usr/bin/env python3
"""
jamendo_search.py — Music library search for Synthetic Press / Final Hours / Lazarus Films

Six pre-mapped category searches against the Jamendo API.
Run: python jamendo_search.py <category> [--limit N] [--download]

Categories:
  opening-portent       — cold open tension, atmospheric dread
  exposition-restrained — act-one historical context, sparse piano
  rising-stakes         — building tension, strings + restrained percussion
  climactic-stillness   — dramatic moment that needs space, NOT crescendo
  aftermath-reflection  — closer, reflective, solo piano
  bridge                — short transitions between acts (under 60s)

Output: prints results to terminal AND appends JSON to ./music-results.json
Optional: --download fetches MP3s to ./music-library/<category>/

Setup:
  1. pip install requests python-dotenv
  2. Create .env file with: JAMENDO_CLIENT_ID=your_client_id_here
  3. python jamendo_search.py climactic-stillness
"""

import os
import sys
import json
import argparse
import urllib.parse
from pathlib import Path
from datetime import datetime

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from dotenv import load_dotenv

load_dotenv()

JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")
if not JAMENDO_CLIENT_ID:
    print("ERROR: JAMENDO_CLIENT_ID not found in .env file.")
    print("Create .env in this directory with: JAMENDO_CLIENT_ID=your_client_id")
    sys.exit(1)

BASE_URL = "https://api.jamendo.com/v3.0/tracks/"

# Category-to-Jamendo-params mappings.
# These translate your six script-beat categories into Jamendo search params.
# `fuzzytags` allows multi-tag fuzzy matching. `speed` filters by tempo bucket.
# `vocalinstrumental=instrumental` is locked for all documentary scoring.
CATEGORIES = {
    "opening-portent": {
        "fuzzytags": "cinematic dark ambient atmospheric",
        "speed": "low",
        "vocalinstrumental": "instrumental",
        "boost": "popularity_total",
        "description": "Cold open tension. Atmospheric dread. Strings, ambient pads, low register."
    },
    "exposition-restrained": {
        "fuzzytags": "cinematic documentary piano minimal",
        "speed": "medium",
        "vocalinstrumental": "instrumental",
        "acousticelectric": "acoustic",
        "description": "Act-one context. Sparse piano underbed. Present but not dominant."
    },
    "rising-stakes": {
        "fuzzytags": "cinematic suspense strings tension",
        "speed": "medium high",
        "vocalinstrumental": "instrumental",
        "description": "Building drama. Strings entering, harmonic tension, restrained percussion."
    },
    "climactic-stillness": {
        "fuzzytags": "ambient sad cinematic",
        "tags": "soundtrack",
        "speed": "verylow low",
        "vocalinstrumental": "instrumental",
        "description": "Dramatic moment needing SPACE not crescendo. Single sustained notes. Single piano. Held silence."
    },
    "aftermath-reflection": {
        "fuzzytags": "reflective piano emotional ambient",
        "speed": "low",
        "vocalinstrumental": "instrumental",
        "description": "Closer. The story is done, meaning lingers. Solo piano, warm strings."
    },
    "bridge": {
        "fuzzytags": "cinematic transition interlude",
        "speed": "medium",
        "vocalinstrumental": "instrumental",
        "duration_max": 60,
        "description": "Short transitions between acts. Under 60 seconds. Same family as surrounding tracks."
    }
}


def search_jamendo(category, limit=10):
    """Search Jamendo for tracks matching a category's params."""
    if category not in CATEGORIES:
        print(f"ERROR: Unknown category '{category}'. Valid: {list(CATEGORIES.keys())}")
        sys.exit(1)

    params = {
        "client_id": JAMENDO_CLIENT_ID,
        "format": "jsonpretty",
        "limit": limit,
        "include": "musicinfo stats licenses",
        "order": "popularity_total_desc",
        **CATEGORIES[category]
    }
    # Remove our internal "description" key before sending to API
    params.pop("description", None)

    response = requests.get(BASE_URL, params=params, timeout=30, verify=False)
    response.raise_for_status()
    data = response.json()

    if data["headers"]["status"] != "success":
        print(f"API ERROR: {data['headers'].get('error_message', 'unknown')}")
        sys.exit(1)

    return data["results"]


def format_track(track, index):
    """Pretty-print a track summary to terminal."""
    duration_sec = int(track.get("duration", 0))
    duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"
    musicinfo = track.get("musicinfo", {})
    tags = musicinfo.get("tags", {})
    vocal_inst = tags.get("vocalinstrumental", ["?"])[0] if tags else "?"
    speed = tags.get("speed", ["?"])[0] if tags else "?"
    instruments = ", ".join(tags.get("instruments", [])[:3]) if tags else ""

    download_allowed = track.get("audiodownload_allowed", False)
    download_flag = "✓ download" if download_allowed else "✗ stream only"

    print(f"\n  [{index}] {track['name']}")
    print(f"      Artist:    {track['artist_name']}")
    print(f"      Duration:  {duration_str}  |  Speed: {speed}  |  {vocal_inst}")
    if instruments:
        print(f"      Instruments: {instruments}")
    print(f"      License:   {track.get('license_ccurl', 'n/a')}")
    print(f"      Preview:   {track['audio']}")
    print(f"      Download:  {download_flag}")
    print(f"      Track ID:  {track['id']}")


def download_track(track, project_path):
    """Download a track's MP3 directly into a project's audio/ folder."""
    if not track.get("audiodownload_allowed", False):
        print(f"      SKIP: audiodownload_allowed is False for track {track['id']}")
        return None

    target_path = Path(project_path) / "audio"
    target_path.mkdir(parents=True, exist_ok=True)

    safe_artist = "".join(c if c.isalnum() or c in " -_" else "_" for c in track["artist_name"])
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in track["name"])
    filename = f"{safe_artist} - {safe_name} [{track['id']}].mp3"
    filepath = target_path / filename

    if filepath.exists():
        print(f"      EXISTS: {filename}")
        return str(filepath)

    audio_url = track["audiodownload"]
    print(f"      Downloading: {filename}")
    r = requests.get(audio_url, stream=True, timeout=60, verify=False)
    r.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"      Saved: {filepath}")

    # Append attribution record
    credits_file = Path(project_path) / "audio_credits.txt"
    credit_line = "{} by {} (Jamendo ID {}) - {}\n".format(track["name"], track["artist_name"], track["id"], track.get("license_ccurl", "unknown license"))
    with open(credits_file, "a") as f:
        f.write(credit_line)
    print(f"      Attribution added to {credits_file}")
    return str(filepath)


def save_results_json(category, tracks):
    """Append search results to music-results.json for later manifest integration."""
    output_file = Path("music-results.json")
    existing = {}
    if output_file.exists():
        existing = json.loads(output_file.read_text())

    existing[category] = {
        "searched_at": datetime.now().isoformat(),
        "params": {k: v for k, v in CATEGORIES[category].items() if k != "description"},
        "description": CATEGORIES[category]["description"],
        "tracks": [
            {
                "id": t["id"],
                "name": t["name"],
                "artist_name": t["artist_name"],
                "duration": t.get("duration"),
                "audio_preview": t["audio"],
                "audio_download": t.get("audiodownload", ""),
                "audiodownload_allowed": t.get("audiodownload_allowed", False),
                "license_ccurl": t.get("license_ccurl"),
                "musicinfo": t.get("musicinfo", {}),
                "shareurl": t.get("shareurl", "")
            }
            for t in tracks
        ]
    }
    output_file.write_text(json.dumps(existing, indent=2))
    print(f"\n  Results saved to {output_file}")


def cmd_search(args):
    print(f"\n{'='*70}")
    print(f"  Category: {args.category}")
    print(f"  {CATEGORIES[args.category]['description']}")
    print(f"{'='*70}")

    tracks = search_jamendo(args.category, limit=args.limit)
    if not tracks:
        print("\n  No results. Try adjusting tags or speed in CATEGORIES dict.")
        return

    print(f"\n  Found {len(tracks)} tracks:")
    for i, track in enumerate(tracks, 1):
        format_track(track, i)

    save_results_json(args.category, tracks)




def cmd_download_one(args):
    """Download a single track by ID after you've previewed it."""
    params = {
        "client_id": JAMENDO_CLIENT_ID,
        "format": "jsonpretty",
        "id": args.track_id,
        "include": "musicinfo stats licenses"
    }
    r = requests.get(BASE_URL, params=params, timeout=30, verify=False)
    r.raise_for_status()
    data = r.json()
    if not data["results"]:
        print(f"Track {args.track_id} not found.")
        return
    track = data["results"][0]
    print(f"Downloading: {track['name']} by {track['artist_name']}")
    download_track(track, args.category)


def cmd_all(args):
    """Run all six category searches in one go."""
    for category in CATEGORIES:
        args.category = category
        cmd_search(args)
    print(f"\n{'='*70}")
    print("  All six categories searched. Review music-results.json")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Jamendo music search for documentary scoring")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # search <category>
    p_search = subparsers.add_parser("search", help="Search one category")
    p_search.add_argument("category", choices=list(CATEGORIES.keys()))
    p_search.add_argument("--limit", type=int, default=10, help="Results per query (default 10)")
    p_search.set_defaults(func=cmd_search)

    # all
    p_all = subparsers.add_parser("all", help="Search all six categories")
    p_all.add_argument("--limit", type=int, default=10)
    p_all.set_defaults(func=cmd_all)

    # download-one <track_id>
    p_dl = subparsers.add_parser("download-one", help="Download a specific track by ID")
    p_dl.add_argument("track_id", help="Jamendo track ID")
    p_dl.add_argument("project", help="Project path to save into (e.g. final-hours/projects/hindenburg)")
    p_dl.set_defaults(func=cmd_download_one)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
