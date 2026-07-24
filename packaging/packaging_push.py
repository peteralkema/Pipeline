#!/usr/bin/env python3
"""
packaging_push.py  v2

Metadata + thumbnail repair for EXISTING videos. videos.update + thumbnails.set.
Separate from the upload step (videos.insert) on purpose.

DRY RUN BY DEFAULT. Nothing is written without --commit.

Typical run
  1. python3 packaging_push.py --csv batch.csv --thumbs-dir thumbs --make-thumb-map
     -> writes thumb_map.csv, lists the folder, you fill in the file column

  2. python3 packaging_push.py --csv batch.csv --thumbs-dir thumbs
     -> dry run, prints every title/tag diff and every thumbnail pairing

  3. same + --commit
     -> archives current thumbnails, writes revert json, pushes

  4. python3 packaging_push.py --revert reverts/revert_XXXX.json --commit
     -> puts titles and tags back

Quota
  videos.list           1 unit per batch of 50
  videos.update        50 units per video
  thumbnails.set       50 units per video
  playlists.insert     50 units
  playlistItems.insert 50 units per item
  20 titles + 20 thumbs + 40 playlist items = ~4050 of 10000/day.

Scope
  Requires https://www.googleapis.com/auth/youtube.force-ssl
  Custom thumbnails also require the channel to be phone-verified, or
  thumbnails.set returns 403.

Thumbnail revert is APPROXIMATE. thumbnails.set has no undo, and the archive
saves YouTube's re-encoded derivative, not your original upload. Keep your
originals. Titles and tags revert exactly.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError:
    sys.exit(
        "Missing deps. Run:\n"
        "  python3 -m pip install google-api-python-client "
        "google-auth-httplib2 google-auth-oauthlib"
    )

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
WRITE_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
CLIENT_SECRETS = os.environ.get("YT_CLIENT_SECRETS", "client_secrets.json")
TOKEN_FILE = os.environ.get("YT_TOKEN_FILE", "token_force_ssl.json")

TITLE_MAX = 100
TAGS_MAX = 500
TAGS_WARN = 450
LIST_BATCH = 50
THUMB_MAX_BYTES = 2 * 1024 * 1024
THUMB_MIN_WIDTH = 640
THUMB_IDEAL = (1280, 720)
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

THUMB_ARCHIVE = os.path.join("reverts", "thumbs")
THUMB_LEDGER = os.path.join("reverts", "thumbs_pushed.json")


def log(msg):
    print(msg, flush=True)


def rule(char="-", n=78):
    log(char * n)


def get_service():
    creds = None
    preexisting = os.path.exists(TOKEN_FILE)
    if preexisting:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS):
                sys.exit(
                    "No client secrets at %s.\n"
                    "Set YT_CLIENT_SECRETS or drop the OAuth client JSON there."
                    % CLIENT_SECRETS
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)
            preexisting = False
        if not preexisting:
            with open(TOKEN_FILE, "w") as fh:
                fh.write(creds.to_json())
        else:
            log("Refreshed in memory; %s left untouched." % TOKEN_FILE)

    granted = set(getattr(creds, "scopes", None) or [])
    if granted and WRITE_SCOPE not in granted:
        sys.exit(
            "Token lacks youtube.force-ssl.\n"
            "Granted: %s\n"
            "Re-mint with shared/upload_episode.py --auth-only."
            % (sorted(granted),)
        )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def tags_len(tags):
    total = 0
    for t in tags:
        total += len(t) + (2 if " " in t else 0)
    if tags:
        total += len(tags) - 1
    return total


def non_ascii(s):
    return [c for c in s if ord(c) > 127]


def load_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            vid = (r.get("video_id") or "").strip()
            if not vid:
                continue
            tags = [t.strip() for t in (r.get("keywords") or "").split(",") if t.strip()]
            rows.append(
                {
                    "rank": (r.get("rank") or "").strip(),
                    "video_id": vid,
                    "new_title": (r.get("new_title") or "").strip(),
                    "tags": tags,
                    "notes": (r.get("notes") or "").strip(),
                    "retention": (r.get("retention_pct") or "").strip(),
                    "thumb": "",
                }
            )
    return rows


def list_images(folder):
    if not os.path.isdir(folder):
        return []
    return [f for f in sorted(os.listdir(folder)) if f.lower().endswith(IMAGE_EXTS)]


def make_thumb_map(rows, folder, out_path):
    files = list_images(folder)
    log("Folder %s contains %d images:" % (folder, len(files)))
    for i, f in enumerate(files, 1):
        log("  %2d  %s" % (i, f))
    rule()
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "video_id", "new_title", "file"])
        for r in rows:
            auto = ""
            for f in files:
                if os.path.splitext(f)[0] == r["video_id"]:
                    auto = f
                    break
            w.writerow([r["rank"], r["video_id"], r["new_title"], auto])
    log("Wrote %s" % out_path)
    log("Fill the 'file' column with a filename from the list above, then re-run")
    log("without --make-thumb-map.")


def load_thumb_map(rows, folder, map_path):
    """Attach a thumbnail path to each row. Returns a list of problems."""
    problems = []
    mapping = {}

    if map_path and os.path.exists(map_path):
        with open(map_path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                vid = (r.get("video_id") or "").strip()
                fn = (r.get("file") or "").strip()
                if vid and fn:
                    mapping[vid] = fn

    for r in rows:
        fn = mapping.get(r["video_id"], "")
        if not fn:
            for ext in IMAGE_EXTS:
                cand = r["video_id"] + ext
                if os.path.exists(os.path.join(folder, cand)):
                    fn = cand
                    break
        if not fn:
            continue
        path = os.path.join(folder, fn)
        if not os.path.exists(path):
            problems.append("%s: file not found: %s" % (r["video_id"], path))
            continue
        size = os.path.getsize(path)
        if size > THUMB_MAX_BYTES:
            problems.append(
                "%s: %s is %.2f MB, max is 2 MB" % (r["video_id"], fn, size / 1048576.0)
            )
            continue
        if HAVE_PIL:
            try:
                with Image.open(path) as im:
                    w, h = im.size
                if w < THUMB_MIN_WIDTH:
                    problems.append(
                        "%s: %s is %dx%d, min width %d"
                        % (r["video_id"], fn, w, h, THUMB_MIN_WIDTH)
                    )
                    continue
                if (w, h) != THUMB_IDEAL:
                    log("  WARN %s %s is %dx%d, ideal is 1280x720"
                        % (r["video_id"], fn, w, h))
            except Exception as exc:
                problems.append("%s: cannot read %s (%s)" % (r["video_id"], fn, exc))
                continue
        r["thumb"] = path
    return problems


def validate(rows, retention_floor):
    ok, skipped = [], []
    for r in rows:
        reasons = []

        if r["notes"].upper().startswith("BLOCKED"):
            reasons.append("marked BLOCKED in CSV")

        if not r["new_title"]:
            reasons.append("empty new_title")
        elif len(r["new_title"]) > TITLE_MAX:
            reasons.append("title %d chars (max %d)" % (len(r["new_title"]), TITLE_MAX))

        bad = non_ascii(r["new_title"]) + non_ascii(",".join(r["tags"]))
        if bad:
            reasons.append("non-ASCII chars: %s" % "".join(sorted(set(bad))))

        tl = tags_len(r["tags"])
        if tl > TAGS_MAX:
            reasons.append("tags %d chars (max %d)" % (tl, TAGS_MAX))

        try:
            if retention_floor and float(r["retention"]) < retention_floor:
                reasons.append(
                    "retention %.1f%% below floor %.1f%% - re-cut, do not re-title"
                    % (float(r["retention"]), retention_floor)
                )
        except ValueError:
            pass

        if reasons:
            skipped.append((r, "; ".join(reasons)))
        else:
            if tl > TAGS_WARN:
                log("  WARN %s tags at %d chars, close to the %d cap"
                    % (r["video_id"], tl, TAGS_MAX))
            ok.append(r)
    return ok, skipped


def fetch_snippets(yt, video_ids):
    out = {}
    for i in range(0, len(video_ids), LIST_BATCH):
        chunk = video_ids[i:i + LIST_BATCH]
        resp = yt.videos().list(part="snippet,status", id=",".join(chunk)).execute()
        for item in resp.get("items", []):
            out[item["id"]] = item
    return out


def build_new_snippet(current_snippet, row):
    """videos.update REPLACES the part, so every field must be echoed back."""
    s = dict(current_snippet)
    for k in ("channelId", "publishedAt", "thumbnails", "liveBroadcastContent",
              "channelTitle", "localized"):
        s.pop(k, None)
    if "categoryId" not in s:
        raise ValueError("snippet has no categoryId - refusing to write")
    s["title"] = row["new_title"]
    s["tags"] = row["tags"]
    return s


def best_thumb_url(snippet):
    thumbs = snippet.get("thumbnails", {})
    for key in ("maxres", "standard", "high", "medium", "default"):
        if key in thumbs and thumbs[key].get("url"):
            return thumbs[key]["url"]
    return None


def archive_thumb(video_id, url):
    if not url:
        return None
    os.makedirs(THUMB_ARCHIVE, exist_ok=True)
    dest = os.path.join(THUMB_ARCHIVE, "%s.jpg" % video_id)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "packaging_push"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(dest, "wb") as fh:
            fh.write(data)
        return dest
    except Exception as exc:
        log("  WARN could not archive thumbnail for %s (%s)" % (video_id, exc))
        return None


def load_ledger():
    if os.path.exists(THUMB_LEDGER):
        try:
            with open(THUMB_LEDGER, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}


def save_ledger(led):
    os.makedirs(os.path.dirname(THUMB_LEDGER), exist_ok=True)
    with open(THUMB_LEDGER, "w", encoding="utf-8") as fh:
        json.dump(led, fh, indent=2)


def write_revert(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    log("Revert file written: %s" % path)


def push(yt, rows, live, revert_path, do_thumbs):
    ids = [r["video_id"] for r in rows]
    log("Fetching current snippets for %d videos..." % len(ids))
    current = fetch_snippets(yt, ids)

    missing = [v for v in ids if v not in current]
    if missing:
        log("  NOT FOUND (wrong channel or deleted): %s" % ", ".join(missing))

    ledger = load_ledger()
    plan, revert = [], {}

    for r in rows:
        item = current.get(r["video_id"])
        if not item:
            continue
        cur = item["snippet"]

        meta_same = (cur.get("title") == r["new_title"]
                     and cur.get("tags", []) == r["tags"])
        thumb_wanted = bool(do_thumbs and r["thumb"])
        thumb_done = ledger.get(r["video_id"], {}).get("file") == r["thumb"]

        if meta_same and (not thumb_wanted or thumb_done):
            log("  SKIP %s already current (idempotent)" % r["video_id"])
            continue

        new_snip = None
        if not meta_same:
            try:
                new_snip = build_new_snippet(cur, r)
            except ValueError as exc:
                log("  SKIP %s %s" % (r["video_id"], exc))
                continue
            revert[r["video_id"]] = cur

        plan.append({
            "row": r,
            "cur": cur,
            "snippet": new_snip,
            "thumb": r["thumb"] if (thumb_wanted and not thumb_done) else "",
        })

    rule()
    for p in plan:
        r, cur = p["row"], p["cur"]
        log("#%s  %s   (retention %s%%)" % (r["rank"], r["video_id"], r["retention"]))
        if p["snippet"]:
            log("  OLD title: %s" % cur.get("title", ""))
            log("  NEW title: %s   [%d chars]" % (r["new_title"], len(r["new_title"])))
            log("  OLD tags : %s" % (", ".join(cur.get("tags", [])) or "(none)"))
            log("  NEW tags : %s   [%d chars]"
                % (", ".join(r["tags"]), tags_len(r["tags"])))
        else:
            log("  metadata already current")
        if p["thumb"]:
            log("  THUMB    : %s" % p["thumb"])
        elif do_thumbs:
            log("  THUMB    : (none mapped)")
        rule()

    if not plan:
        log("Nothing to write.")
        return

    n_meta = sum(1 for p in plan if p["snippet"])
    n_thumb = sum(1 for p in plan if p["thumb"])
    log("%d metadata updates, %d thumbnail uploads (%d quota units)."
        % (n_meta, n_thumb, n_meta * 50 + n_thumb * 50))

    unmapped = [p["row"]["video_id"] for p in plan if do_thumbs and not p["thumb"]]
    if unmapped:
        log("NOTE %d videos have no thumbnail mapped: %s"
            % (len(unmapped), ", ".join(unmapped)))

    if not live:
        log("DRY RUN. Re-run with --commit to write.")
        return

    if revert:
        write_revert(revert_path, revert)

    if n_thumb:
        log("Archiving current thumbnails to %s ..." % THUMB_ARCHIVE)
        for p in plan:
            if p["thumb"]:
                archive_thumb(p["row"]["video_id"], best_thumb_url(p["cur"]))

    done_meta = done_thumb = 0
    for p in plan:
        vid = p["row"]["video_id"]
        if p["snippet"]:
            try:
                yt.videos().update(
                    part="snippet",
                    body={"id": vid, "snippet": p["snippet"]},
                ).execute()
                done_meta += 1
                log("  OK   %s title -> %s" % (vid, p["row"]["new_title"][:55]))
                time.sleep(0.4)
            except HttpError as exc:
                log("  FAIL %s metadata %s" % (vid, exc))
                continue
        if p["thumb"]:
            try:
                yt.thumbnails().set(
                    videoId=vid,
                    media_body=MediaFileUpload(p["thumb"], resumable=False),
                ).execute()
                done_thumb += 1
                ledger[vid] = {"file": p["thumb"],
                               "at": datetime.now().isoformat(timespec="seconds")}
                save_ledger(ledger)
                log("  OK   %s thumb -> %s" % (vid, os.path.basename(p["thumb"])))
                time.sleep(0.6)
            except HttpError as exc:
                log("  FAIL %s thumbnail %s" % (vid, exc))
                if "403" in str(exc):
                    log("       403 usually means the channel is not phone-verified.")

    log("Done. %d metadata, %d thumbnails." % (done_meta, done_thumb))


def do_revert(yt, path, live):
    with open(path, encoding="utf-8") as fh:
        saved = json.load(fh)
    log("Reverting %d videos from %s" % (len(saved), path))
    log("NOTE reverts titles and tags only. Thumbnails must be re-uploaded by")
    log("     hand from %s if needed." % THUMB_ARCHIVE)
    if not live:
        for vid, snip in saved.items():
            log("  %s -> %s" % (vid, snip.get("title", "")))
        log("DRY RUN. Re-run with --commit to write.")
        return
    for vid, snip in saved.items():
        s = dict(snip)
        for k in ("channelId", "publishedAt", "thumbnails", "liveBroadcastContent",
                  "channelTitle", "localized"):
            s.pop(k, None)
        try:
            yt.videos().update(part="snippet", body={"id": vid, "snippet": s}).execute()
            log("  OK   %s reverted" % vid)
            time.sleep(0.4)
        except HttpError as exc:
            log("  FAIL %s %s" % (vid, exc))


def find_playlist(yt, title):
    req = yt.playlists().list(part="snippet", mine=True, maxResults=50)
    while req is not None:
        resp = req.execute()
        for item in resp.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
        req = yt.playlists().list_next(req, resp)
    return None


def existing_items(yt, playlist_id):
    have = set()
    req = yt.playlistItems().list(
        part="contentDetails", playlistId=playlist_id, maxResults=50
    )
    while req is not None:
        resp = req.execute()
        for item in resp.get("items", []):
            have.add(item["contentDetails"]["videoId"])
        req = yt.playlistItems().list_next(req, resp)
    return have


def build_playlist(yt, title, description, video_ids, live):
    pid = find_playlist(yt, title)
    if pid:
        log("Playlist exists: %s (%s)" % (title, pid))
        have = existing_items(yt, pid)
    else:
        log("Playlist not found: %s" % title)
        have = set()
        if not live:
            log("DRY RUN. Would create playlist and add %d videos (%d units)."
                % (len(video_ids), 50 + 50 * len(video_ids)))
            return
        pid = yt.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": "public"},
            },
        ).execute()["id"]
        log("Created playlist %s" % pid)

    todo = [v for v in video_ids if v not in have]
    if not todo:
        log("Playlist already contains all %d videos." % len(video_ids))
        return
    if not live:
        log("DRY RUN. Would add %d videos to %s (%d units)."
            % (len(todo), pid, 50 * len(todo)))
        return

    for vid in todo:
        try:
            yt.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": pid,
                        "resourceId": {"kind": "youtube#video", "videoId": vid},
                    }
                },
            ).execute()
            log("  OK   added %s" % vid)
            time.sleep(0.4)
        except HttpError as exc:
            log("  FAIL %s %s" % (vid, exc))
    log("Playlist URL: https://www.youtube.com/playlist?list=%s" % pid)


def main():
    ap = argparse.ArgumentParser(description="Title, tag and thumbnail repair.")
    ap.add_argument("--csv", help="re-title CSV")
    ap.add_argument("--commit", action="store_true",
                    help="actually write (default dry run)")
    ap.add_argument("--revert", help="path to a revert JSON")
    ap.add_argument("--thumbs-dir", help="folder of hand-made thumbnails")
    ap.add_argument("--thumb-map", default="thumb_map.csv",
                    help="video_id -> filename mapping CSV")
    ap.add_argument("--make-thumb-map", action="store_true",
                    help="write a mapping stub and list the folder, then exit")
    ap.add_argument("--playlist", help="catch-all playlist title to create/populate")
    ap.add_argument("--playlist-desc", default="", help="playlist description")
    ap.add_argument("--playlist-ids", help="file with one video id per line")
    ap.add_argument("--retention-floor", type=float, default=20.0,
                    help="skip rows below this retention pct (0 disables)")
    ap.add_argument("--only", help="comma-separated video ids to restrict to")
    args = ap.parse_args()

    if not args.csv and not args.revert and not args.playlist:
        ap.error("need --csv, --revert or --playlist")

    if args.make_thumb_map:
        if not args.csv or not args.thumbs_dir:
            ap.error("--make-thumb-map needs --csv and --thumbs-dir")
        make_thumb_map(load_rows(args.csv), args.thumbs_dir, args.thumb_map)
        return

    yt = get_service()
    try:
        me = yt.channels().list(part="snippet", mine=True).execute()["items"][0]
        log("Auth OK. Bound channel: %s (%s)" % (me["snippet"]["title"], me["id"]))
    except Exception as exc:
        sys.exit("Could not resolve the bound channel: %s" % exc)
    if args.thumbs_dir and not HAVE_PIL:
        log("NOTE Pillow not installed, skipping image dimension checks.")
    if not args.commit:
        log(">>> DRY RUN. Nothing will be written. <<<")
    rule("=")

    if args.revert:
        do_revert(yt, args.revert, args.commit)
        return

    rows = []
    if args.csv:
        rows = load_rows(args.csv)
        log("Loaded %d rows from %s" % (len(rows), args.csv))
        if args.only:
            keep = {v.strip() for v in args.only.split(",")}
            rows = [r for r in rows if r["video_id"] in keep]
            log("Restricted to %d rows via --only" % len(rows))

        do_thumbs = bool(args.thumbs_dir)
        if do_thumbs:
            problems = load_thumb_map(rows, args.thumbs_dir, args.thumb_map)
            mapped = sum(1 for r in rows if r["thumb"])
            log("Mapped %d/%d thumbnails from %s"
                % (mapped, len(rows), args.thumbs_dir))
            for p in problems:
                log("  THUMB PROBLEM %s" % p)

        ok, skipped = validate(rows, args.retention_floor)
        if skipped:
            rule()
            log("SKIPPED %d rows:" % len(skipped))
            for r, why in skipped:
                log("  #%s %s  %s" % (r["rank"], r["video_id"], why))
        rule("=")

        if ok:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            push(yt, ok, args.commit,
                 os.path.join("reverts", "revert_%s.json" % stamp), do_thumbs)
        else:
            log("No valid rows to push.")

    if args.playlist:
        rule("=")
        if args.playlist_ids:
            with open(args.playlist_ids, encoding="utf-8") as fh:
                vids = [l.strip() for l in fh if l.strip()]
        else:
            vids = [r["video_id"] for r in rows]
        build_playlist(yt, args.playlist, args.playlist_desc, vids, args.commit)


if __name__ == "__main__":
    main()
