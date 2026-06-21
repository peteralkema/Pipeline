#!/usr/bin/env python3
"""
fetch_enoch_source.py  (one-time setup, run on the BOX)

Download the full public-domain R.H. Charles 1917 translation of 1 Enoch
(CCEL single-page edition) and split it into per-chapter plain-text files:

    sacred-soak/source/enoch/ch01.txt ... ch108.txt

After this runs once, every Sacred Soak volume is authored from local source:
no fetching, no snippet-stitching, and the slate word-count (doctrine 12.5) is
a one-line `wc -w sacred-soak/source/enoch/ch*.txt`.

Source format (verified): each chapter begins with a line '[Chapter N]'.
We split on those markers, drop the section/intro headings, keep verse text
and the poetic line breaks intact.

Idempotent: re-running overwrites the same files. Writes a manifest with
per-chapter word counts so the slate is immediately visible.

Run:
    cd ~/Pipeline
    set -a; source .env; set +a            # not strictly needed; no API keys used
    python shared/fetch_enoch_source.py
"""

import re
import sys
import urllib.request
from pathlib import Path

SRC_URL = "https://ccel.org/c/charles/otpseudepig/enoch.htm"
OUT_DIR = Path(__file__).resolve().parent.parent / "sacred-soak" / "source" / "enoch"

CHAPTER_RE = re.compile(r"\[Chapter\s+(\d+)\]")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pipeline source fetch)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    return raw.decode("utf-8", errors="replace")


def strip_html(html: str) -> str:
    # CCEL serves light HTML; collapse tags to text but keep line structure.
    # Remove script/style blocks.
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # <br> -> newline (preserves the poetic line breaks)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    # block-level close tags -> newline
    html = re.sub(r"</(p|div|h[1-6]|li)>", "\n", html, flags=re.IGNORECASE)
    # drop all remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    # unescape the few entities that matter
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                 ("&#39;", "'"), ("&apos;", "'"), ("&nbsp;", " ")):
        html = html.replace(a, b)
    return html


def clean_block(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    out = []
    for ln in lines:
        s = ln.strip()
        # drop section headings and editorial markers that aren't scripture
        if re.match(r"^#{1,6}\s", ln):
            continue
        if re.match(r"^Section\s+[IVXLC]+\.", s):
            continue
        if s in ("INTRODUCTION", "BOOK OF ENOCH", ""):
            if s == "":
                out.append("")
            continue
        out.append(s)
    # collapse 3+ blank lines to one
    joined = "\n".join(out)
    joined = re.sub(r"\n{3,}", "\n\n", joined).strip()
    return joined


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("fetching {0}".format(SRC_URL))
    html = fetch(SRC_URL)
    text = strip_html(html)

    # find all chapter markers and their positions
    marks = list(CHAPTER_RE.finditer(text))
    if not marks:
        sys.exit("ERROR: no '[Chapter N]' markers found; source format changed. "
                 "Inspect the fetched page before trusting the split.")

    written = []
    for i, m in enumerate(marks):
        num = int(m.group(1))
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = clean_block(text[start:end])
        if not body:
            continue
        fn = OUT_DIR / "ch{0:02d}.txt".format(num)
        fn.write_text(body + "\n", encoding="utf-8")
        wc = len(body.split())
        written.append((num, wc))

    # manifest + slate-friendly word counts
    manifest = OUT_DIR / "_wordcounts.txt"
    with manifest.open("w", encoding="utf-8") as f:
        total = 0
        for num, wc in sorted(written):
            f.write("ch{0:02d}  {1:5d}\n".format(num, wc))
            total += wc
        f.write("TOTAL {0}\n".format(total))

    nums = sorted(n for n, _ in written)
    print("wrote {0} chapter files to {1}".format(len(written), OUT_DIR))
    if nums:
        print("  chapters: {0}..{1}".format(nums[0], nums[-1]))
        missing = [n for n in range(nums[0], nums[-1] + 1) if n not in nums]
        if missing:
            print("  NOTE missing chapter numbers: {0}".format(missing))
    print("  word-count manifest -> {0}".format(manifest.name))
    # quick echo of the Vol.2 span so we can eyeball it immediately
    span = [n for n in nums if 37 <= n <= 44]
    if span:
        wc_map = dict(written)
        tot = sum(wc_map[n] for n in span)
        print("  Vol.2 span ch37-44: {0} words total".format(tot))


if __name__ == "__main__":
    main()
