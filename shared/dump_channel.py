#!/usr/bin/env python3
"""
dump_channel.py - channel-agnostic READ-ONLY metadata mirror.

Philosophy: same as upload_episode.py - the channel folder IS the identity
(token.json + client_secret.json live there). Point this at a channel dir, it
resolves credentials, walks the channel's uploads playlist, and writes the FULL
raw videos.list response for every video (published AND scheduled) to
  <channel_dir>/channel_dump.json

Raw capture, never pre-filtered: we grab every readable part the API exposes and
store it whole, so future questions are a local read instead of a new API trip.
Views on top (Artlist URL worklist, missing-chapters audit, schedule calendar)
read this file; they are NOT baked into the dump.

Reuses upload_episode.get_credentials() verbatim - same token, same refresh-in-
place, same scopes (force-ssl already grants read). No new consent.

success-coach is EXCLUDED from --all (dead channel, dead topic). It can still be
dumped explicitly via --channel success-coach if ever needed.

WHAT THIS CANNOT SEE (API does not expose - stays manual in Studio):
  - the "Altered/AI content" disclosure flag
  - Content ID copyright claims (needs partner youtubePartner scope)
  - end screens / cards / Studio editor state
  statistics.* here is a SNAPSHOT at dump time, not live - use NexLev for current perf.

Usage:
  python dump_channel.py --channel final-hours
  python dump_channel.py --channel final-hours --dry-run
  python dump_channel.py --all            # every channel dir with token.json, minus excludes
  python dump_channel.py --all --scheduled-only-summary
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Reuse the canonical credential loader from the upload step - do NOT reinvent it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from upload_episode import get_credentials, log, die  # noqa: E402

# Channels skipped by --all (still dumpable explicitly via --channel).
EXCLUDE = {"success-coach"}  # dead channel, dead topic - never auto-dump

# Every readable part videos.list exposes. Raw capture - grab it all.
VIDEO_PARTS = [
    "snippet",
    "status",
    "contentDetails",
    "statistics",
    "topicDetails",
    "recordingDetails",
    "localizations",
    "liveStreamingDetails",
    "player",
    "paidProductPlacementDetails",
]
PARTS_STR = ",".join(VIDEO_PARTS)

REPO_ROOT = Path(__file__).resolve().parent.parent  # shared/ -> repo root


def find_channel_dirs(explicit):
    """Return [channel_dir, ...] - the explicit one, or every dir with a token.json
    minus EXCLUDE. An explicit --channel is honoured even if excluded."""
    if explicit:
        d = (REPO_ROOT / explicit).resolve()
        if not d.is_dir():
            die(f"channel dir not found: {d}")
        return [d]
    found = []
    for token in sorted(REPO_ROOT.glob("*/token.json")):
        if token.parent.name in EXCLUDE:
            log(f"  (skipping excluded channel: {token.parent.name})")
            continue
        found.append(token.parent)
    return found


def get_youtube(channel_dir):
    token_path = channel_dir / "token.json"
    client_secret_path = channel_dir / "client_secret.json"
    if not token_path.exists():
        log(f"  skip {channel_dir.name}: no token.json (channel not authorised yet)")
        return None
    try:
        creds = get_credentials(token_path, client_secret_path)
    except SystemExit:
        # get_credentials calls die() on dead headless tokens - don't kill the whole --all run.
        log(f"  skip {channel_dir.name}: token dead / needs re-auth on laptop")
        return None
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)


def resolve_uploads_playlist(youtube):
    """Return (channel_title, uploads_playlist_id) for the authorised channel."""
    resp = youtube.channels().list(part="snippet,contentDetails", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        die("channels.list(mine=True) returned nothing - wrong/empty token?")
    ch = items[0]
    title = ch.get("snippet", {}).get("title", "?")
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    return title, uploads


def list_all_video_ids(youtube, uploads_playlist):
    """Walk the uploads playlist (1 unit/page) - includes private/scheduled videos."""
    ids, page = [], None
    while True:
        resp = youtube.playlistItems().list(
            part="contentDetails", playlistId=uploads_playlist,
            maxResults=50, pageToken=page).execute()
        for it in resp.get("items", []):
            vid = it.get("contentDetails", {}).get("videoId")
            if vid:
                ids.append(vid)
        page = resp.get("nextPageToken")
        if not page:
            break
    return ids


def fetch_videos(youtube, video_ids):
    """videos.list in batches of 50 (1 unit/page), all parts, raw."""
    out = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        resp = youtube.videos().list(part=PARTS_STR, id=",".join(batch), maxResults=50).execute()
        out.extend(resp.get("items", []))
    return out


def dump_one(channel_dir, dry_run):
    youtube = get_youtube(channel_dir)
    if youtube is None:
        return None

    title, uploads = resolve_uploads_playlist(youtube)
    ids = list_all_video_ids(youtube, uploads)
    log(f"  {channel_dir.name}: channel='{title}'  uploads={uploads}  videos={len(ids)}")

    if dry_run:
        pages = (len(ids) // 50) + 1
        log(f"  [dry-run] would fetch {len(ids)} videos "
            f"(~{1 + pages + pages} quota units) and write channel_dump.json")
        return None

    videos = fetch_videos(youtube, ids)

    payload = {
        "_meta": {
            "channel_dir": channel_dir.name,
            "channel_title": title,
            "uploads_playlist": uploads,
            "dumped_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "video_count": len(videos),
            "parts_captured": VIDEO_PARTS,
            "blind_spots": [
                "AI-content disclosure flag (not in API)",
                "Content ID copyright claims (needs partner scope)",
                "end screens / cards / editor state",
                "statistics.* is a snapshot at dump time, not live",
            ],
        },
        "videos": videos,
    }
    out_path = channel_dir / "channel_dump.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    scheduled = [v for v in videos
                 if v.get("status", {}).get("privacyStatus") == "private"
                 and v.get("status", {}).get("publishAt")]
    log(f"  -> {out_path.name}  ({len(videos)} videos, {len(scheduled)} scheduled)")
    return payload


def main():
    ap = argparse.ArgumentParser(description="Read-only YouTube metadata mirror (raw capture).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--channel", help="Channel dir name, e.g. final-hours")
    g.add_argument("--all", action="store_true", help="Every channel dir with a token.json, minus EXCLUDE")
    ap.add_argument("--dry-run", action="store_true", help="Resolve + count, no fetch, no write.")
    ap.add_argument("--scheduled-only-summary", action="store_true",
                    help="After dumping, print the forward schedule (publishAt) per channel.")
    args = ap.parse_args()

    channel_dirs = find_channel_dirs(None if args.all else args.channel)
    if not channel_dirs:
        die("no channel dirs to dump.")

    log("=" * 64)
    log(f"DUMP  -  {len(channel_dirs)} channel(s)  -  {'DRY-RUN' if args.dry_run else 'live'}")
    log("=" * 64)

    payloads = []
    for d in channel_dirs:
        p = dump_one(d, args.dry_run)
        if p:
            payloads.append(p)

    if args.scheduled_only_summary and not args.dry_run:
        log("")
        log("SCHEDULED (private + publishAt), soonest first:")
        for p in payloads:
            rows = []
            for v in p["videos"]:
                st = v.get("status", {})
                if st.get("privacyStatus") == "private" and st.get("publishAt"):
                    rows.append((st["publishAt"], v.get("snippet", {}).get("title", "?"), v["id"]))
            rows.sort()
            log(f"  {p['_meta']['channel_title']}:")
            if not rows:
                log("    (none scheduled)")
            for when, ttl, vid in rows:
                log(f"    {when}  {ttl[:60]}  https://youtu.be/{vid}")

    log("")
    log("done.")


if __name__ == "__main__":
    main()
