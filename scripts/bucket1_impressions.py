import argparse
import os
from datetime import date

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

IMPRESSIONS = "videoThumbnailImpressions"
CTR = "videoThumbnailImpressionsClickRate"


def load_creds(label, client_secret, token_dir):
    token_path = os.path.join(token_dir, "token_{}.json".format(label))
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as fh:
            fh.write(creds.to_json())
    return creds


def video_titles(youtube, video_ids):
    titles = {}
    if not video_ids:
        return titles
    resp = youtube.videos().list(part="snippet", id=",".join(video_ids)).execute()
    for item in resp.get("items", []):
        titles[item["id"]] = item["snippet"]["title"]
    return titles


def pull_channel(label, creds, start, end, top):
    analytics = build("youtubeAnalytics", "v2", credentials=creds)
    youtube = build("youtube", "v3", credentials=creds)
    channel = youtube.channels().list(part="snippet", mine=True).execute()
    channel_title = channel["items"][0]["snippet"]["title"] if channel.get("items") else label
    resp = analytics.reports().query(
        ids="channel==MINE",
        startDate=start,
        endDate=end,
        dimensions="video",
        metrics="views,{},{}".format(IMPRESSIONS, CTR),
        sort="-{}".format(IMPRESSIONS),
        maxResults=top,
    ).execute()
    rows = resp.get("rows", [])
    video_ids = [r[0] for r in rows]
    titles = video_titles(youtube, video_ids)
    out = []
    for r in rows:
        vid = r[0]
        out.append({
            "videoId": vid,
            "title": titles.get(vid, vid),
            "views": r[1],
            "impressions": r[2],
            "ctr": r[3],
        })
    return channel_title, out


def render(results, start, end):
    lines = ["Bucket 1 - top 3 videos by thumbnail impressions",
             "{} to {}".format(start, end), ""]
    for channel_title, videos in results:
        lines.append(channel_title)
        if not videos:
            lines.append("  no rows returned")
        for v in videos:
            lines.append("  {} | {} impressions | {} ctr | {} views | {}".format(
                v["title"], v["impressions"], v["ctr"], v["views"], v["videoId"]))
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-secret", required=True)
    parser.add_argument("--tokens", nargs="+", required=True)
    parser.add_argument("--token-dir", default="secrets")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    results = []
    for label in args.tokens:
        creds = load_creds(label, args.client_secret, args.token_dir)
        try:
            channel_title, videos = pull_channel(label, creds, args.start, args.end, args.top)
        except HttpError as err:
            channel_title, videos = label, []
            print("ERROR for {}: {}".format(label, err))
        results.append((channel_title, videos))

    report = render(results, args.start, args.end)
    print(report)
    out_path = args.out or "pipeline/shared/docs/bucket1_impressions_{}.md".format(date.today().isoformat())
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        fh.write(report)
    print("wrote {}".format(out_path))


if __name__ == "__main__":
    main()
