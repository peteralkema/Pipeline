#!/usr/bin/env python3
"""
dump_impressions.py

Dump per-video REACH metrics for ONE owned channel, straight from the
YouTube Analytics API:

    videoThumbnailImpressions          - times the thumbnail was shown
    videoThumbnailImpressionsClickRate - CTR on those impressions
    views, estimatedMinutesWatched, averageViewPercentage  (funnel context)

This is the top-of-funnel data NexLev does NOT expose. The two impression
metrics were only added to the Analytics API on 2026-01-15, which is why no
third-party tool has them yet.

Output is a dict keyed by video_id, so it merges cleanly onto your existing
schedule-date dump (join on the id). It also pulls title + publishAt from the
Data API, so it can stand alone if you'd rather not merge.

NOTE ON APIS / SCOPE
--------------------
Impressions come from the Analytics API (youtubeAnalytics.reports.query),
a DIFFERENT service from the Data API your schedule dump uses. It needs the
scope:  https://www.googleapis.com/auth/yt-analytics.readonly
If this channel's existing token was minted without that scope, delete the
token file and re-run once to re-consent (pick the CORRECT channel).

channel==MINE resolves to whatever channel the supplied token authorizes,
so run this once per channel with that channel's token.

LAPTOP (python3):
    python3 dump_impressions.py \
        --token tokens/sacred_dawn.json \
        --client-secret client_secret.json \
        --start 2026-06-11 --end 2026-06-26 \
        --out dumps/sacred_dawn_reach.json
"""

import argparse
import json
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# yt-analytics.readonly unlocks the impression metrics.
# youtube.readonly is only for turning ids into titles/publishAt (optional).
SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

# videoThumbnailImpressions* are the new top-of-funnel (added 2026-01-15).
# The rest let a row stand on its own without a join if you ever want it to.
METRICS = ",".join([
    "videoThumbnailImpressions",
    "videoThumbnailImpressionsClickRate",
    "views",
    "estimatedMinutesWatched",
    "averageViewPercentage",
])

# video dimension reports REQUIRE sort + maxResults to be set explicitly.
SORT = "-videoThumbnailImpressions"
PAGE = 200


def load_credentials(token_path, client_secret_path):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds, token_path)
            return creds
        except Exception as e:  # noqa: BLE001 - want any refresh failure to fall through to interactive
            print(f"[warn] token refresh failed ({e}); running interactive auth", file=sys.stderr)
    if not os.path.exists(client_secret_path):
        sys.exit(f"[fatal] no valid token at {token_path} and no client secret at {client_secret_path}")
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds, token_path)
    return creds


def _save_token(creds, token_path):
    parent = os.path.dirname(token_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(token_path, "w") as f:
        f.write(creds.to_json())


def fetch_reach(creds, start_date, end_date):
    yta = build("youtubeAnalytics", "v2", credentials=creds)
    rows_by_video = {}
    start_index = 1
    while True:
        try:
            resp = yta.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics=METRICS,
                dimensions="video",
                sort=SORT,
                maxResults=PAGE,
                startIndex=start_index,
            ).execute()
        except HttpError as e:
            _explain_http_error(e)
            raise
        headers = [h["name"] for h in resp.get("columnHeaders", [])]
        rows = resp.get("rows", [])
        if not rows:
            break
        for row in rows:
            rec = dict(zip(headers, row))   # map by header name, never by position
            vid = rec.pop("video", None)
            if vid:
                rows_by_video[vid] = rec
        if len(rows) < PAGE:
            break
        start_index += PAGE
    return rows_by_video


def enrich_titles(creds, rows_by_video):
    """Attach title + publishAt (schedule date) from the Data API. Optional."""
    if not rows_by_video:
        return rows_by_video
    yt = build("youtube", "v3", credentials=creds)
    ids = list(rows_by_video.keys())
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        resp = yt.videos().list(part="snippet,status", id=",".join(chunk)).execute()
        for item in resp.get("items", []):
            vid = item["id"]
            if vid in rows_by_video:
                snippet = item.get("snippet", {})
                status = item.get("status", {})
                rows_by_video[vid]["title"] = snippet.get("title")
                # publishAt = scheduled time if set, else the actual publish time
                rows_by_video[vid]["publishAt"] = status.get("publishAt") or snippet.get("publishedAt")
    return rows_by_video


def _explain_http_error(e):
    status = getattr(getattr(e, "resp", None), "status", None)
    msg = str(e)
    if status == 403 or "insufficient" in msg.lower() or "scope" in msg.lower():
        sys.stderr.write(
            "\n[fatal] 403 from the Analytics API.\n"
            "  This token almost certainly lacks the analytics scope.\n"
            "  Fix: delete this channel's token file and re-run to re-consent with\n"
            "       https://www.googleapis.com/auth/yt-analytics.readonly\n"
            "  Make sure you pick the CORRECT channel on the Google consent screen.\n\n"
        )
    elif status == 400 and "videoThumbnailImpressions" in msg:
        sys.stderr.write(
            "\n[fatal] 400 - the API rejected videoThumbnailImpressions.\n"
            "  These metrics were added 2026-01-15; confirm the metric names\n"
            "  against https://developers.google.com/youtube/analytics/metrics\n\n"
        )


def main():
    ap = argparse.ArgumentParser(description="Dump per-video thumbnail impressions + CTR for one owned channel.")
    ap.add_argument("--token", required=True, help="OAuth token json for THIS channel")
    ap.add_argument("--client-secret", default="client_secret.json")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", help="write JSON here; default stdout")
    ap.add_argument("--no-titles", action="store_true", help="skip Data API title/publishAt enrichment")
    args = ap.parse_args()

    creds = load_credentials(args.token, args.client_secret)
    rows = fetch_reach(creds, args.start, args.end)

    if not args.no_titles:
        try:
            rows = enrich_titles(creds, rows)
        except HttpError as e:
            print(f"[warn] title enrichment failed ({e}); continuing without titles", file=sys.stderr)

    out = {
        "start": args.start,
        "end": args.end,
        "video_count": len(rows),
        "videos": rows,
    }
    text = json.dumps(out, indent=2, ensure_ascii=False)

    if args.out:
        parent = os.path.dirname(args.out)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.out, "w") as f:
            f.write(text)
        print(f"[ok] {len(rows)} videos -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
