#!/usr/bin/env python3
"""
upload_episode.py — the ONE channel-agnostic upload step.

Philosophy: same as every leg. The header IS the metadata (no Claude regeneration, no
metadata.json) and the channel folder IS the identity (token + client_secret + channel.json
live there). Point this at a project, it resolves the channel, reads the header, and uploads
final_video.mp4 under that channel's YouTube account. No per-channel upload scripts.

Resolution from --project <channel>/projects/<slug>:
  channel_dir   = project_dir.parent.parent          ->  <channel>/
  header        = project_dir/beats_full.json["header"]   (title, description, tags, channel, [parts])
  channel.json  = channel_dir/channel.json           (optional "upload": {category_id, privacy_status})
  token         = channel_dir/token.json             (refreshed in place if expired)
  client_secret = channel_dir/client_secret.json     (only needed for first-time / re-auth)
  video         = project_dir/final_video.mp4
  thumbnail     = project_dir/thumbnail.png          (optional, attached if present)
  captions      = project_dir/subtitles.srt          (optional, attached if present)

Defaults to PRIVATE (nothing goes public unreviewed — you finish in Studio).

Batch-exit-gate: if the header has parts > 1 this is a batched multi-video job — it is NOT
uploaded; it exits at final_video.mp4 for manual cutting.

Usage:
  python upload_episode.py --project final-hours/projects/gustloff
  python upload_episode.py --project final-hours/projects/gustloff --dry-run
  python upload_episode.py --project final-hours/projects/gustloff --schedule-cet-1am
  python upload_episode.py --project final-hours/projects/gustloff --privacy unlisted
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

# YouTube hard limits
TITLE_MAX = 100
DESC_MAX = 5000
TAGS_TOTAL_MAX = 480  # API ceiling is 500 chars across all tags; leave headroom
DEFAULT_CATEGORY = "24"  # Entertainment (Final Hours / You Had To Be There). Override per channel.json.


def log(msg=""):
    print(msg, flush=True)


def die(msg):
    log(f"ERROR: {msg}")
    sys.exit(1)


def load_header(project_dir: Path) -> dict:
    bf = project_dir / "beats_full.json"
    if not bf.exists():
        die(f"no beats_full.json in {project_dir} — the header is the metadata; "
            f"run parse_script.py with --json-full first.")
    try:
        data = json.load(open(bf, encoding="utf-8"))
    except Exception as e:
        die(f"could not read {bf}: {e}")
    header = data.get("header") or {}
    for k in ("title", "description", "tags", "channel"):
        if not str(header.get(k, "")).strip():
            die(f"header missing required key '{k}' in {bf}")
    return header


def load_channel_cfg(channel_dir: Path) -> dict:
    cj = channel_dir / "channel.json"
    if not cj.exists():
        return {}
    try:
        return json.load(open(cj, encoding="utf-8")) or {}
    except Exception:
        return {}


def parse_tags(tags_field) -> list:
    if isinstance(tags_field, list):
        items = [str(t).strip() for t in tags_field]
    else:
        items = [t.strip() for t in str(tags_field).split(",")]
    items = [t for t in items if t]
    # trim to stay under the API's total-length ceiling
    out, total = [], 0
    for t in items:
        total += len(t) + 1
        if total > TAGS_TOTAL_MAX:
            break
        out.append(t)
    return out


def next_warsaw_1am_utc() -> str:
    """RFC3339 UTC string for the next 01:00 Europe/Warsaw (~19:00 US Eastern)."""
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        die("zoneinfo unavailable (needs Python 3.9+) — cannot compute schedule time.")
    tz = ZoneInfo("Europe/Warsaw")
    now = datetime.now(tz)
    target = now.replace(hour=1, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_credentials(token_path: Path, client_secret_path: Path):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
            return creds
        except Exception as e:
            log(f"token refresh failed ({e}) — re-authentication needed.")

    # No usable token. Interactive re-auth only works with a browser (laptop), not headless.
    if not client_secret_path.exists():
        die(f"no valid token and no {client_secret_path} to re-authenticate.")
    if not sys.stdin.isatty():
        die("token is dead and this is a non-interactive/headless session. "
            f"Re-auth on your LAPTOP, then copy the token over:\n"
            f"    (laptop) python shared/upload_episode.py --project <same project> --auth-only\n"
            f"    (laptop) scp -P 443 {token_path} peter@116.202.18.68:~/Pipeline/{token_path}")
    log("no valid token — launching browser for one-time authorization...")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())
    return creds


def main():
    ap = argparse.ArgumentParser(description="Channel-agnostic YouTube uploader (header = metadata).")
    ap.add_argument("--project", required=True,
                    help="Path to the project dir, e.g. final-hours/projects/gustloff")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"],
                    help="Privacy status (default: private — review in Studio).")
    ap.add_argument("--schedule-cet-1am", action="store_true",
                    help="Force private + publishAt the next 01:00 Europe/Warsaw.")
    ap.add_argument("--publish-at", default=None, help="Explicit RFC3339 UTC publishAt (forces private).")
    ap.add_argument("--category", default=None, help="Override categoryId.")
    ap.add_argument("--no-thumbnail", action="store_true", help="Do not attach thumbnail.png.")
    ap.add_argument("--no-captions", action="store_true", help="Do not attach subtitles.srt.")
    ap.add_argument("--auth-only", action="store_true",
                    help="Run/refresh OAuth and write token.json, then exit (use on the laptop).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Resolve everything and print the request body — no API calls.")
    args = ap.parse_args()

    project_dir = Path(args.project).resolve()
    if not project_dir.is_dir():
        die(f"project dir not found: {project_dir}")
    channel_dir = project_dir.parent.parent

    token_path = channel_dir / "token.json"
    client_secret_path = channel_dir / "client_secret.json"

    # --auth-only: just establish/refresh the token (laptop convenience) and stop.
    if args.auth_only:
        get_credentials(token_path, client_secret_path)
        log(f"OK — token ready at {token_path}")
        return

    header = load_header(project_dir)
    cfg = load_channel_cfg(channel_dir)
    upload_cfg = cfg.get("upload", {}) if isinstance(cfg.get("upload"), dict) else {}

    # ── batch-exit-gate ────────────────────────────────────────────────
    parts = 1
    try:
        parts = int(str(header.get("parts", 1)).strip() or 1)
    except Exception:
        parts = 1
    if parts > 1:
        log(f"batched job ({parts} parts) → not uploading. "
            f"Exit at final_video.mp4 for manual cutting into {parts} videos.")
        return

    video = project_dir / "final_video.mp4"
    if not video.exists():
        die(f"no final_video.mp4 in {project_dir} — nothing to upload.")
    thumbnail = project_dir / "thumbnail.png"
    captions = project_dir / "subtitles.srt"

    # ── metadata (header wins; channel.json supplies categoryId/privacy defaults) ──
    title = str(header["title"]).strip()
    if len(title) > TITLE_MAX:
        log(f"WARNING: title is {len(title)} chars (>{TITLE_MAX}) — truncating.")
        title = title[:TITLE_MAX]
    description = str(header["description"]).strip()[:DESC_MAX]
    tags = parse_tags(header["tags"])
    category_id = args.category or str(upload_cfg.get("category_id", DEFAULT_CATEGORY))

    privacy = args.privacy
    publish_at = None
    if args.schedule_cet_1am:
        publish_at = next_warsaw_1am_utc()
        privacy = "private"
    elif args.publish_at:
        publish_at = args.publish_at
        privacy = "private"
    elif not args.category and upload_cfg.get("privacy_status") and "--privacy" not in sys.argv:
        privacy = str(upload_cfg["privacy_status"])

    snippet = {"title": title, "description": description, "tags": tags, "categoryId": category_id}
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at

    log("=" * 64)
    log(f"UPLOAD  ·  channel={header['channel']}  ·  project={project_dir.name}")
    log(f"  title    : {title}")
    log(f"  category : {category_id}   privacy: {privacy}" + (f"   publishAt: {publish_at}" if publish_at else ""))
    log(f"  tags     : {len(tags)}  ·  video: {video.name} ({video.stat().st_size // (1024*1024)} MB)")
    log(f"  thumbnail: {'yes' if (thumbnail.exists() and not args.no_thumbnail) else 'none'}"
        f"   captions: {'yes' if (captions.exists() and not args.no_captions) else 'none'}")
    log("=" * 64)

    if args.dry_run:
        log("[dry-run] would send this snippet/status, then attach thumbnail/captions. No API calls made.")
        log(json.dumps({"snippet": snippet, "status": status}, indent=2, ensure_ascii=False))
        return

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_credentials(token_path, client_secret_path)
    youtube = build("youtube", "v3", credentials=creds)

    log("uploading (resumable)...")
    media = MediaFileUpload(str(video), chunksize=5 * 1024 * 1024, resumable=True)
    req = youtube.videos().insert(part="snippet,status",
                                  body={"snippet": snippet, "status": status},
                                  media_body=media)
    response = None
    while response is None:
        chunk_status, response = req.next_chunk()
        if chunk_status:
            log(f"  {int(chunk_status.progress() * 100)}%")
    video_id = response["id"]
    log(f"✓ uploaded — video ID: {video_id}")

    if thumbnail.exists() and not args.no_thumbnail:
        try:
            youtube.thumbnails().set(videoId=video_id,
                                     media_body=MediaFileUpload(str(thumbnail))).execute()
            log("✓ thumbnail set")
        except Exception as e:
            log(f"WARNING: thumbnail upload failed ({e}) — set it in Studio.")

    if captions.exists() and not args.no_captions:
        try:
            youtube.captions().insert(
                part="snippet",
                body={"snippet": {"videoId": video_id, "language": "en",
                                  "name": "English", "isDraft": False}},
                media_body=MediaFileUpload(str(captions))).execute()
            log("✓ captions attached")
        except Exception as e:
            log(f"WARNING: caption upload failed ({e}) — not fatal.")

    log("")
    log(f"Studio: https://studio.youtube.com/video/{video_id}/edit")
    log(f"Watch : https://youtu.be/{video_id}  (currently {privacy})")


if __name__ == "__main__":
    main()
