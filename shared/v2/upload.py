"""shared/v2/upload.py -- stage 6: the DB is the header.

Extraction provenance (upload_episode.py organ donor): SCOPES, the YouTube
hard limits, parse_tags, get_credentials (refresh-in-place + laptop re-auth
guidance), the resumable insert loop, thumbnail set, and captions insert are
all carried verbatim. What changes is only where metadata comes from: the
project row replaces beats_full.json's header (title/description/tags), and
the outcome is written BACK -- video_id, publish_status, published_at -- so
--status can answer "is it up?" from the data.

Credentials stay on disk, never in the DB: token.json + client_secret.json
resolve by walking up from the project dir (v1 channel layout first:
<channel>/projects/<slug> -> <channel>/), overridable with --creds-dir.

v1's parts>1 batch-exit-gate is gone by construction: a v2 project is one
video; shorts and cuts are EDL rows, not multi-part uploads.

Defaults PRIVATE. Nothing goes public unreviewed -- you finish in Studio.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import db as v2db

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
TITLE_MAX = 100
DESC_MAX = 5000
TAGS_TOTAL_MAX = 480
DEFAULT_CATEGORY = "24"


def _log(msg=""):
    print(msg, flush=True)


def parse_tags(tags_field) -> list:
    if isinstance(tags_field, list):
        items = [str(t).strip() for t in tags_field]
    else:
        items = [t.strip() for t in str(tags_field or "").split(",")]
    items = [t for t in items if t]
    out, total = [], 0
    for t in items:
        total += len(t) + 1
        if total > TAGS_TOTAL_MAX:
            break
        out.append(t)
    return out


def resolve_creds_dir(project_dir: Path, override: str = None) -> Path:
    if override:
        d = Path(override).expanduser()
        if (d / "token.json").exists() or (d / "client_secret.json").exists():
            return d
        raise SystemExit(f"--creds-dir {d} has neither token.json nor "
                         f"client_secret.json")
    for cand in (project_dir.parent.parent, project_dir.parent, project_dir):
        if (cand / "token.json").exists() or (cand / "client_secret.json").exists():
            return cand
    raise SystemExit(
        f"no token.json/client_secret.json found walking up from "
        f"{project_dir} -- pass --creds-dir <channel dir>")


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
            _log(f"token refresh failed ({e}) -- re-authentication needed.")
    if not client_secret_path.exists():
        raise SystemExit(f"no valid token and no {client_secret_path} to "
                         f"re-authenticate.")
    if not sys.stdin.isatty():
        raise SystemExit(
            "token is dead and this is a headless session. Re-auth on the "
            "LAPTOP (python upload.py --project <same> --auth-only), then "
            f"scp {token_path} back to the box.")
    _log("no valid token -- launching browser for one-time authorization...")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path),
                                                     SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())
    return creds


def run(con, project_dir: Path, privacy: str = "private",
        publish_at: str = None, dry_run: bool = False,
        creds_dir: str = None, category: str = None,
        no_thumbnail: bool = False, no_captions: bool = False) -> None:
    proj = con.execute("SELECT * FROM project WHERE id=1").fetchone()
    if proj["video_id"]:
        _log(f"   already uploaded: video ID {proj['video_id']} -- no-op")
        return

    video = Path(proj["final_video_path"] or (project_dir / "final_video.mp4"))
    if not video.exists():
        raise SystemExit("stage 'upload': no final_video.mp4 -- run assemble.")
    thumbnail = Path(proj["thumbnail_path"] or (project_dir / "thumbnail.png"))
    captions = project_dir / "subtitles.srt"

    title = str(proj["title"]).strip()
    if len(title) > TITLE_MAX:
        _log(f"WARNING: title is {len(title)} chars (>{TITLE_MAX}) -- truncating.")
        title = title[:TITLE_MAX]
    description = str(proj["description"] or "").strip()[:DESC_MAX]
    tags = parse_tags(proj["tags"])
    category_id = category or DEFAULT_CATEGORY

    if publish_at:
        privacy = "private"
    snippet = {"title": title, "description": description, "tags": tags,
               "categoryId": category_id}
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at

    _log("=" * 64)
    _log(f"UPLOAD  ·  channel={proj['channel']}  ·  project={proj['slug']}")
    _log(f"  title    : {title}")
    _log(f"  category : {category_id}   privacy: {privacy}"
         + (f"   publishAt: {publish_at}" if publish_at else ""))
    _log(f"  tags     : {len(tags)}  ·  video: {video.name} "
         f"({video.stat().st_size // (1024*1024)} MB)")
    _log(f"  thumbnail: {'yes' if (thumbnail.exists() and not no_thumbnail) else 'none'}"
         f"   captions: {'yes' if (captions.exists() and not no_captions) else 'none'}")
    _log("=" * 64)

    if dry_run:
        _log("[dry-run] would send this snippet/status. No API calls made.")
        _log(json.dumps({"snippet": snippet, "status": status}, indent=2,
                        ensure_ascii=False))
        return

    cdir = resolve_creds_dir(project_dir, creds_dir)
    creds = get_credentials(cdir / "token.json", cdir / "client_secret.json")

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    youtube = build("youtube", "v3", credentials=creds)

    _log("uploading (resumable)...")
    media = MediaFileUpload(str(video), chunksize=5 * 1024 * 1024,
                            resumable=True)
    req = youtube.videos().insert(part="snippet,status",
                                  body={"snippet": snippet, "status": status},
                                  media_body=media)
    response = None
    while response is None:
        chunk_status, response = req.next_chunk()
        if chunk_status:
            _log(f"  {int(chunk_status.progress() * 100)}%")
    video_id = response["id"]
    _log(f"uploaded -- video ID: {video_id}")

    if thumbnail.exists() and not no_thumbnail:
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail))).execute()
            _log("thumbnail set")
        except Exception as e:
            _log(f"WARNING: thumbnail upload failed ({e}) -- set it in Studio.")
    if captions.exists() and not no_captions:
        try:
            youtube.captions().insert(
                part="snippet",
                body={"snippet": {"videoId": video_id, "language": "en",
                                  "name": "English", "isDraft": False}},
                media_body=MediaFileUpload(str(captions))).execute()
            _log("captions attached")
        except Exception as e:
            _log(f"WARNING: caption upload failed ({e}) -- not fatal.")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    con.execute(
        "UPDATE project SET video_id=?, publish_status='uploaded', "
        "published_at=? WHERE id=1", (video_id, publish_at or now))
    v2db.log_generation(con, stage="upload", model="youtube-v3",
                        result_path=video_id,
                        params_json=json.dumps({"privacy": privacy,
                                                "publishAt": publish_at}))
    con.commit()
    _log("")
    _log(f"Studio: https://studio.youtube.com/video/{video_id}/edit")
    _log(f"Watch : https://youtu.be/{video_id}  (currently {privacy})")


def main():
    ap = argparse.ArgumentParser(description="v2 uploader: the DB is the header")
    ap.add_argument("--project", required=True)
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", default=None,
                    help="RFC3339 UTC publishAt (forces private)")
    ap.add_argument("--category", default=None)
    ap.add_argument("--creds-dir", default=None)
    ap.add_argument("--no-thumbnail", action="store_true")
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--auth-only", action="store_true")
    a = ap.parse_args()
    pdir = Path(a.project).resolve()
    if a.auth_only:
        cdir = resolve_creds_dir(pdir, a.creds_dir)
        get_credentials(cdir / "token.json", cdir / "client_secret.json")
        _log(f"OK -- token ready at {cdir/'token.json'}")
        return
    con = v2db.connect(pdir / f"{pdir.name}.db")
    run(con, pdir, a.privacy, a.publish_at, a.dry_run, a.creds_dir,
        a.category, a.no_thumbnail, a.no_captions)


if __name__ == "__main__":
    main()
