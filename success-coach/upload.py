"""
upload.py — Upload a finished Final Hours video to YouTube.

What it does, in order:
  1. Reads the project (script + storyboard + final_video.mp4)
  2. Asks Claude to generate metadata (title, description, tags) from the script
  3. Generates subtitles.srt from the storyboard timing
  4. Uploads the video as PRIVATE by default (you review on platform, then publish)
  5. Uploads the SRT as a caption track
  6. Uploads thumbnail.jpg/.png from the project folder if present
  7. Prints the YouTube studio URL for you to review and publish

Run:
    python3 upload.py --project pompeii_v1
    python3 upload.py --project pompeii_v1 --privacy unlisted
    python3 upload.py --project pompeii_v1 --privacy public   # ship it

Requirements (already installed for the auth step):
    pip install google-auth-oauthlib google-auth google-api-python-client anthropic python-dotenv
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

import anthropic
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from srt_generator import generate_srt

load_dotenv()

# Zscaler cert handling — same pattern as the rest of the pipeline.
CERT_BUNDLE = os.path.expanduser("~/combined_cacert.pem")
if os.path.exists(CERT_BUNDLE):
    os.environ.setdefault("SSL_CERT_FILE", CERT_BUNDLE)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", CERT_BUNDLE)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL      = "claude-sonnet-4-6"

TOKEN_FILE = "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",   # needed for captions + thumbnail
]

CATEGORY_EDUCATION = "27"   # YouTube category ID for Education


# ── Step 1: generate title, description, tags via Claude ──────────────────────

def generate_metadata(script: str) -> dict:
    """
    Ask Claude to write YouTube metadata from the script. Returns
    {"title": ..., "description": ..., "tags": [...]}
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""You write YouTube metadata for a faceless historical-recreation
channel called "Final Hours". The channel tells the last hours of people and
places history remembers, in slow cinematic photorealistic recreation.

Here is the narration script for the video:
---
{script}
---

Return ONLY a JSON object (no preamble, no markdown fences) with these exact keys:

- "title": punchy YouTube title, max 60 chars, emotional and curiosity-driven.
  Avoid "the story of" / "what happened at" — too generic. Lean into the reframe.
  Example shape: "Pompeii Gave Them One Day to Escape. This Is Why They Stayed."

- "description": the first 2 lines must be the hook from the script (set up the
  curiosity gap without resolving it). Then 2-3 sentences of summary in the same
  documentary tone. Then a blank line. Then a "CHAPTERS:" placeholder section
  (chapters will be inserted later — leave it as just the word CHAPTERS:). Then
  a blank line. Then channel furniture: a one-line subscribe nudge in voice, and
  the hashtags #FinalHours #history #Pompeii plus 2-3 more specific to this video.

- "tags": list of 10-15 YouTube tags. Specific to this video. Include the place,
  date, key figures, and the emotional/structural framing words.

Return ONLY the JSON object."""

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)


# ── Step 1b: generate chapters and insert into description ─────────────────────

def _fmt_chapter_time(seconds: float) -> str:
    s = int(seconds)
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def build_chapters(project: Path, script: str) -> str:
    """
    Ask Claude to divide the story into ~6 sections, map each to a starting shot
    index, and compute its timestamp from the even-spacing z = narration/shots
    (the same model the assembler uses). Returns the formatted CHAPTERS block.

    YouTube chapter rules enforced: first chapter at 0:00, >=3 chapters,
    each >=10s apart. The first chapter is always forced to 0:00.
    """
    import subprocess
    storyboard = json.loads((project / "storyboard.json").read_text())
    n = len(storyboard)
    voice = project / "voiceover.mp3"
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(voice)],
        capture_output=True, text=True).stdout.strip())
    z = dur / n

    prompt = f"""This narration script becomes a video of {n} shots, each shown for
{z:.2f} seconds, total {dur/60:.1f} minutes.

Script:
---
{script}
---

Divide it into 5 to 7 chapters for a YouTube description. For each chapter give a
short evocative title (3-5 words, documentary tone, no numbering) and the SHOT
NUMBER (1 to {n}) where that chapter begins. The first chapter must begin at shot 1.

Return ONLY a JSON array like:
[{{"title": "The Ordinary Morning", "start_shot": 1}}, {{"title": "The Mountain Wakes", "start_shot": 14}}]
Nothing else."""

    resp = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY).messages.create(
        model=CLAUDE_MODEL, max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    chapters = json.loads(raw)

    lines = ["CHAPTERS:"]
    prev_t = -10
    for idx, ch in enumerate(chapters):
        shot = max(1, int(ch.get("start_shot", 1)))
        t = 0.0 if idx == 0 else (shot - 1) * z   # force first to 0:00
        if t - prev_t < 10 and idx != 0:
            continue   # enforce YouTube's 10s minimum gap
        lines.append(f"{_fmt_chapter_time(t)} {ch['title']}")
        prev_t = t
    return "\n".join(lines)


# ── Step 2: get authenticated YouTube client ──────────────────────────────────

def get_youtube_client():
    if not os.path.exists(TOKEN_FILE):
        raise SystemExit(
            f"No {TOKEN_FILE} found. Run auth.py first."
        )
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            raise SystemExit("Token invalid and not refreshable — re-run auth.py")
    return build("youtube", "v3", credentials=creds)


# ── Step 3: upload ────────────────────────────────────────────────────────────

def _next_cet_1am_iso() -> str:
    """
    Compute the next 01:00 Europe/Warsaw datetime that's at least 15 minutes
    in the future, return it as an RFC3339 string suitable for YouTube's
    publishAt field.

    Why 01:00 Europe/Warsaw specifically: this puts the publish at ~19:00 US
    Eastern, which is the start of the prime US history-watching evening
    window. The YouTube algorithm's first impression-expansion test (~6-12 hrs
    after publish) then lands on the next US evening too — maximising the
    chance the wider test is served to active viewers, not sleeping ones.
    Europe/Warsaw is used (not fixed CET) so it tracks DST automatically.
    """
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Europe/Warsaw")
    now_local = datetime.now(tz)
    target = now_local.replace(hour=1, minute=0, second=0, microsecond=0)
    # If 01:00 today has passed (or is less than 15 min away), use tomorrow's 01:00.
    if target <= now_local + timedelta(minutes=15):
        target = target + timedelta(days=1)
    # YouTube wants RFC3339; Python's isoformat with a tz-aware datetime gives that.
    return target.isoformat()


def upload_video(youtube, video_path: Path, metadata: dict, privacy: str,
                 publish_at: str | None = None) -> str:
    """
    Upload a video. If `publish_at` is provided (RFC3339), the video is
    scheduled — YouTube requires it to be uploaded as PRIVATE and will flip
    it to public at the scheduled time. Caller is responsible for setting
    privacy='private' when scheduling.
    """
    if publish_at:
        print(f"\nUploading SCHEDULED for {publish_at} (privacy forced to private until then)...")
    else:
        print(f"\nUploading video as {privacy.upper()}...")
    status = {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
    }
    if publish_at:
        status["publishAt"] = publish_at
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": CATEGORY_EDUCATION,
        },
        "status": status,
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )

    # Resumable upload with progress
    response = None
    while response is None:
        status_chunk, response = request.next_chunk()
        if status_chunk:
            print(f"   {int(status_chunk.progress() * 100)}% uploaded")
    video_id = response["id"]
    print(f"OK Video uploaded -> https://youtu.be/{video_id}")
    return video_id


def upload_captions(youtube, video_id: str, srt_path: Path):
    print("Uploading captions (SRT)...")
    body = {
        "snippet": {
            "videoId": video_id,
            "language": "en",
            "name": "English",
            "isDraft": False,
        }
    }
    youtube.captions().insert(
        part="snippet",
        body=body,
        media_body=MediaFileUpload(str(srt_path), mimetype="application/octet-stream"),
    ).execute()
    print(f"OK Captions uploaded")


def upload_thumbnail(youtube, video_id: str, thumb_path: Path):
    print(f"Uploading thumbnail: {thumb_path.name}")
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumb_path)),
    ).execute()
    print(f"OK Thumbnail set")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_chapters_placeholder(desc: str) -> str:
    """
    Remove the literal 'CHAPTERS:' placeholder line from the description and
    collapse the blank-line gap it leaves so the published description reads
    cleanly. Used when chapters are not being generated.
    """
    import re
    # Drop the CHAPTERS: line and any timestamp lines Claude might have
    # written underneath it as illustration. Stops at the next blank line.
    desc = re.sub(r"(?m)^CHAPTERS:.*(?:\n(?!\s*$).*)*\n?", "", desc)
    # Collapse 3+ consecutive newlines down to a double-newline paragraph break.
    desc = re.sub(r"\n{3,}", "\n\n", desc).strip() + "\n"
    return desc


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Upload a Final Hours video")
    ap.add_argument("--project", required=True)
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"])
    ap.add_argument("--chapters", action="store_true",
                    help="generate chapter timestamps and insert into description "
                         "(off by default — even-spacing timing doesn't match speech, "
                         "so chapters point to the wrong moments until Whisper-based "
                         "timing is built)")
    ap.add_argument("--schedule-cet-1am", action="store_true",
                    help="schedule the video to go public at the next 01:00 Europe/Warsaw "
                         "(=~19:00 US Eastern) — the prime US evening window, which also "
                         "aligns the algorithm's first impression-expansion test with US "
                         "evening viewing. Forces upload as private until that time.")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    video_path  = project / "final_video.mp4"
    script_path = project / "script.txt"

    if not video_path.exists():
        raise SystemExit(f"No video found: {video_path}. Run `finish` first.")
    if not script_path.exists():
        raise SystemExit(f"No script found: {script_path}.")

    script = script_path.read_text()

    # Step 1: metadata
    print("Generating metadata (Claude)...")
    metadata = generate_metadata(script)
    print(f"   title: {metadata['title']}")
    print(f"   tags : {metadata['tags']}")

    # Step 1b: chapters — opt-in, off by default.
    # When off, strip the CHAPTERS: placeholder from the description entirely
    # (and tidy any blank-line gap it leaves) so the published description is clean.
    desc = metadata["description"]
    if args.chapters:
        print("Generating chapters...")
        try:
            chapters_block = build_chapters(project, script)
            import re
            if "CHAPTERS:" in desc:
                desc = re.sub(r"CHAPTERS:\s*", chapters_block + "\n", desc, count=1)
            else:
                desc = desc.rstrip() + "\n\n" + chapters_block + "\n"
            print("   chapters inserted")
        except Exception as e:
            print(f"   chapters skipped ({e}) — publishing without them")
            desc = _strip_chapters_placeholder(desc)
    else:
        desc = _strip_chapters_placeholder(desc)
        print("Chapters skipped (use --chapters to include).")
    metadata["description"] = desc

    # Save it next to the video for reference / reuse
    (project / "metadata.json").write_text(json.dumps(metadata, indent=2))

    # Step 2: SRT
    print("\nGenerating SRT from storyboard...")
    srt_path = generate_srt(project)
    print(f"OK SRT -> {srt_path}")

    # Step 3: auth + upload
    youtube = get_youtube_client()

    # Scheduling: if requested, compute the next 01:00 Europe/Warsaw slot and
    # force privacy to 'private' (YouTube requires this for scheduled videos —
    # it flips the visibility to public itself at the scheduled time).
    publish_at = None
    privacy = args.privacy
    if args.schedule_cet_1am:
        publish_at = _next_cet_1am_iso()
        if privacy != "private":
            print(f"   (overriding --privacy {privacy} to private — required for scheduling)")
            privacy = "private"
        print(f"   scheduled publish time: {publish_at}")

    video_id = upload_video(youtube, video_path, metadata, privacy, publish_at=publish_at)

    upload_captions(youtube, video_id, srt_path)

    # Step 4: optional thumbnail
    thumb_jpg = project / "thumbnail.jpg"
    thumb_png = project / "thumbnail.png"
    if thumb_jpg.exists():
        upload_thumbnail(youtube, video_id, thumb_jpg)
    elif thumb_png.exists():
        upload_thumbnail(youtube, video_id, thumb_png)
    else:
        print("\nNote: no thumbnail.jpg/png in project folder. YouTube will use an auto-generated one.")
        print("Drop your custom thumbnail in there and re-run with --privacy unchanged to attach it.")

    print(f"\nDONE.")
    print(f"Studio: https://studio.youtube.com/video/{video_id}/edit")
    print(f"Watch : https://youtu.be/{video_id}")
    if args.privacy == "private":
        print(f"\nIt's PRIVATE — review on YouTube, set thumbnail if needed, then publish from Studio.")


if __name__ == "__main__":
    main()
