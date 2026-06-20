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

Reuses upload_episode.get_credentials() verbatim - same token, same refresh-in-
place, same scopes (force-ssl already grants read). No new consent.

success-coach is EXCLUDED from --all (dead channel, dead topic). It can still be
dumped explicitly via --channel success-coach if ever needed.

SCHEDULE DISPLAY (--scheduled-only-summary): prints publishAt in a LOCAL timezone
(default Europe/Amsterdam) with UTC in parens, so it matches what Studio shows.
Override with --tz (e.g. Asia/Kolkata) when scheduling from another zone.

CADENCE CHECK (--cadence): the post-batch verifier for "post every day, forever".
Per channel, buckets scheduled videos by LOCAL date and reports any missing day
inside the scheduled span - i.e. the holes a batch run left behind. A same-day
double counts as ONE covered day (doubling up does not fill the next hole).

WHAT THIS CANNOT SEE (API does not expose - stays manual in Studio):
  - the "Altered/AI content" disclosure flag
  - Content ID copyright claims (needs partner youtubePartner scope)
  - end screens / cards / Studio editor state
  statistics.* here is a SNAPSHOT at dump time, not live - use NexLev for current perf.

Usage:
  python dump_channel.py --channel final-hours
  python dump_channel.py --all --scheduled-only-summary
  python dump_channel.py --all --cadence
  python dump_channel.py --all --scheduled-only-summary --cadence --tz Asia/Kolkata
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Reuse the canonical credential loader from the upload step - do NOT reinvent it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from upload_episode import get_credentials, log, die  # noqa: E402

# Channels skipped by --all (still dumpable explicitly via --channel).
EXCLUDE = {"success-coach"}  # dead channel, dead topic - never auto-dump

# Default timezone for schedule/cadence - home/Studio locale. Override with --tz.
DEFAULT_TZ_NAME = "Europe/Amsterdam"

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


def parse_publish_at(pub):
    """Parse an RFC3339 publishAt string to an aware UTC datetime, or None."""
    if not pub:
        return None
    try:
        return datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.fromisoformat(pub.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            return None


def resolve_tz(tz_name):
    """Return a ZoneInfo or die loudly on a bad zone name (no silent mis-render)."""
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError, ValueError):
        die(f"unknown timezone '{tz_name}'. Use an IANA name, e.g. "
            f"Europe/Amsterdam, Asia/Kolkata, America/New_York.")


def scheduled_local_dates(payload, local_tz):
    """Map private+publishAt videos to a {local_date: count} dict for one channel."""
    counts = {}
    for v in payload["videos"]:
        st = v.get("status", {})
        if st.get("privacyStatus") != "private":
            continue
        dt_utc = parse_publish_at(st.get("publishAt"))
        if dt_utc is None:
            continue
        d = dt_utc.astimezone(local_tz).date()
        counts[d] = counts.get(d, 0) + 1
    return counts


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
                "publishAt is UTC; convert to local to compare with Studio",
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


def print_schedule_summary(payloads, tz_name):
    """Forward schedule in the chosen timezone (matches Studio), UTC in parens, soonest first."""
    local_tz = resolve_tz(tz_name)
    now_utc = datetime.now(timezone.utc)
    log("")
    log(f"SCHEDULED (private + publishAt). Local time = {tz_name} (match to where Studio shows you); UTC in parens.")
    log("  [PAST] = publishAt already elapsed (published or stale).  [<status>] = not private.")
    for p in payloads:
        rows = []
        for v in p["videos"]:
            st = v.get("status", {})
            dt_utc = parse_publish_at(st.get("publishAt"))
            if dt_utc is None:
                continue
            rows.append((dt_utc, st.get("privacyStatus", "?"),
                         v.get("snippet", {}).get("title", "?"), v["id"]))
        rows.sort(key=lambda r: r[0])
        log(f"  {p['_meta']['channel_title']}:")
        if not rows:
            log("    (none scheduled)")
            continue
        for dt_utc, priv, ttl, vid in rows:
            dt_local = dt_utc.astimezone(local_tz)
            flags = []
            if dt_utc < now_utc:
                flags.append("PAST")
            if priv != "private":
                flags.append(priv.upper())
            flag_str = ("  [" + ",".join(flags) + "]") if flags else ""
            local_s = dt_local.strftime("%a %Y-%m-%d %H:%M %Z")
            utc_s = dt_utc.strftime("%H:%MZ")
            log(f"    {local_s} ({utc_s})  {ttl[:50]}  https://youtu.be/{vid}{flag_str}")


def print_cadence(payloads, tz_name):
    """Post-batch verifier for 'post every day, forever': any missing day inside
    each channel's scheduled span is a gap. Same-day double = one covered day."""
    local_tz = resolve_tz(tz_name)
    log("")
    log(f"CADENCE CHECK (rule: post every day). Dates bucketed in {tz_name}.")
    log("  A gap = a calendar day with no scheduled video inside the span.")
    any_gap = False
    for p in payloads:
        name = p["_meta"]["channel_title"]
        counts = scheduled_local_dates(p, local_tz)
        if not counts:
            log(f"  {name}: (none scheduled)")
            continue
        covered = sorted(counts)
        first, last = covered[0], covered[-1]
        span_days = (last - first).days + 1
        gaps = []
        d = first
        while d <= last:
            if d not in counts:
                gaps.append(d)
            d += timedelta(days=1)
        doubles = sorted(d for d, c in counts.items() if c > 1)
        span_str = f"{first.strftime('%a %m-%d')}..{last.strftime('%a %m-%d')}"
        head = f"  {name}: {len(covered)} day(s) covered, span {span_str} ({span_days}d)"
        if gaps:
            any_gap = True
            gap_str = ", ".join(g.strftime("%a %m-%d") for g in gaps)
            head += f"  -> GAP: {gap_str}"
        else:
            head += "  -> continuous"
        if doubles:
            dbl_str = ", ".join(g.strftime("%a %m-%d") for g in doubles)
            head += f"  | doubles: {dbl_str}"
        log(head)
    log("")
    log("  RESULT: GAPS FOUND - fill them in Studio." if any_gap
        else "  RESULT: all channels continuous across their spans.")


def main():
    ap = argparse.ArgumentParser(description="Read-only YouTube metadata mirror (raw capture).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--channel", help="Channel dir name, e.g. final-hours")
    g.add_argument("--all", action="store_true", help="Every channel dir with a token.json, minus EXCLUDE")
    ap.add_argument("--dry-run", action="store_true", help="Resolve + count, no fetch, no write.")
    ap.add_argument("--scheduled-only-summary", action="store_true",
                    help="After dumping, print the forward schedule (publishAt) per channel.")
    ap.add_argument("--cadence", action="store_true",
                    help="After dumping, check each channel for missing days in its scheduled span.")
    ap.add_argument("--tz", default=DEFAULT_TZ_NAME,
                    help=f"IANA timezone for summary/cadence (default {DEFAULT_TZ_NAME}), e.g. Asia/Kolkata.")
    args = ap.parse_args()

    # Validate --tz early so a typo fails before we spend any quota.
    if args.scheduled_only_summary or args.cadence:
        resolve_tz(args.tz)

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

    if not args.dry_run:
        if args.scheduled_only_summary:
            print_schedule_summary(payloads, args.tz)
        if args.cadence:
            print_cadence(payloads, args.tz)

    log("")
    log("done.")


if __name__ == "__main__":
    main()
