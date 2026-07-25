#!/usr/bin/env python3
"""
csv2script.py — Step 4 of the bridge (_BRIDGE.md §5).

Deterministic one-way compiler: LEGO master.csv (+ canon.json) -> the batch pair
  <slug>.md  +  <slug>.thumb.json   (+ <slug>.kling.json sidecar plan)

FORMAT AUTHORITY: the GOLDEN PAIR — bible-they-burned-v2.md + .thumb.json, the
channel's most successful batch-produced video — verified against parse_script.py
itself. Its inherited properties (the explicit build-order contract):

  LAW (format, inherited by every compiled script):
    header = channel / title / description / tags, single-line values, no slug key
    body starts '## COLD OPEN'; blocks emit '## ACT <ROMAN> — <NAME>'
    beat = '[A] <narration on the tag line>' + 'VISUAL: ...' + optional 'MOTION: ...'
    blank line BETWEEN beats, none inside a block
  INCIDENTAL (content, per-film, NOT inherited law):
    its beat length (~45w), MOTION on every beat, its title grammar, its act names

Same CSV in = byte-identical pair out. Tokens expanded HERE — the .md is fully
resolved. parse_script.py remains the gate of record: if parser and compiler ever
disagree, the parser wins and this file is fixed.

Usage
  python3 csv2script.py master.csv --canon canon.json --channel sacred_dawn \
      --slug chambers-of-the-dead --title "..." --description-file desc.txt \
      --tags "tag one, tag two" --sections sections.json \
      --thumb-subject-file thumbsubject.txt --thumb-title "THE FOUR CHAMBERS" \
      --thumb-subtitle "AND THE ONE WITH NO WAY OUT" --out-dir ./out --kling csv

--sections sections.json: ordered {"b00": "COLD OPEN", "b01": "THE ROAD WEST", ...}
  (values WITHOUT the '## ' / 'ACT N — ' furniture; the compiler adds it).
  Absent: block ids named b00/cold* -> COLD OPEN, the rest ACT I..N — <BLOCK_ID>.
--kling modes:  csv (air/motion columns) | auto:N (heroes first, front-loaded) | none
"""

import argparse
import csv
import json
import os
import re
import sys
import unicodedata

TOKEN_RE = re.compile(r"\{([a-z0-9_]+)\}")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
MAX_WORDS = 55
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
COLD_IDS = {"b00", "b0", "cold", "cold_open", "coldopen", "co"}


def log(m):
    print(m, flush=True)


def die(m):
    log("COMPILE FAIL: " + m)
    sys.exit(1)


def normalise(text):
    text = (text.replace("\u2018", "'").replace("\u2019", "'")
                .replace("\u201c", '"').replace("\u201d", '"'))
    return unicodedata.normalize("NFKC", text)


def expand(text, canon, where):
    def sub(m):
        t = m.group(1)
        if t not in canon:
            die("unresolved token {%s} in %s" % (t, where))
        return canon[t]
    out = TOKEN_RE.sub(sub, text)
    if "{" in out or "}" in out:
        die("stray brace after expansion in %s: %r" % (where, out[:80]))
    return out


def emit_beat(narration, visual, motion, move=""):
    """GOLDEN-PAIR beat shape: narration rides ON the tag line."""
    lines = ["[A] " + narration, "VISUAL: " + visual]
    if motion:
        lines.append("MOTION: " + motion)
    if move:
        lines.append("MOVE: " + move)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="LEGO csv -> batch pair compiler.")
    ap.add_argument("csv_path")
    ap.add_argument("--canon", help="canon.json (required if any {tokens} used)")
    ap.add_argument("--channel", required=True, help="e.g. sacred_dawn (underscore form)")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--tags", required=True, help="comma-separated; preflight halts if empty")
    ap.add_argument("--description-file", required=True)
    ap.add_argument("--sections", help="sections.json: ordered block_id -> heading name")
    ap.add_argument("--thumb-subject-file", required=True,
                    help="file containing the full thumbnail image prompt (from package.md)")
    ap.add_argument("--thumb-title", required=True, help="lockup line 1")
    ap.add_argument("--thumb-subtitle", required=True, help="lockup line 2")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--kling", default="csv", help="csv | auto:N | none")
    args = ap.parse_args()

    if not SLUG_RE.match(args.slug):
        die("slug fails ^[a-z0-9][a-z0-9-]{0,60}$ : %r" % args.slug)
    if len(args.title) > 100:
        die("title %d chars (max 100)" % len(args.title))

    with open(args.csv_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        die("empty csv")

    canon = {}
    if args.canon:
        with open(args.canon, encoding="utf-8") as fh:
            canon = json.load(fh)

    with open(args.description_file, encoding="utf-8") as fh:
        description = " ".join(fh.read().split()).strip()
    if not description:
        die("empty description (orchestrator preflight halts on it)")
    tags = normalise(args.tags).strip()
    if not tags:
        die("empty tags (orchestrator preflight halts on it)")

    with open(args.thumb_subject_file, encoding="utf-8") as fh:
        thumb_subject = " ".join(fh.read().split()).strip()
    if not thumb_subject:
        die("empty thumbnail subject prompt")

    sections = {}
    if args.sections:
        with open(args.sections, encoding="utf-8") as fh:
            sections = json.load(fh)

    # ---- kling plan ------------------------------------------------------
    has_air = "air" in rows[0]
    mode = args.kling
    if mode == "csv" and not has_air:
        mode = "none"
        log("NOTE no air column; falling back to --kling none (all-floor)")

    kling_idx = []
    if mode == "csv":
        for i, r in enumerate(rows):
            if (r.get("air") or "").strip().lower() == "kling":
                if not (r.get("motion") or "").strip():
                    die("row %d: air=kling with blank motion" % i)
                kling_idx.append(i)
    elif mode.startswith("auto:"):
        want = int(mode.split(":", 1)[1])
        order = sorted(range(len(rows)),
                       key=lambda i: (0 if (rows[i].get("weight") or "").strip().lower()
                                      == "hero" else 1, i))
        kling_idx = sorted(order[:want])
        log("AUTO kling plan: %d beats (heroes first, front-loaded)" % want)
    elif mode != "none":
        die("unknown --kling mode %r" % mode)

    # ---- compile ---------------------------------------------------------
    out_parts = []
    header = ("channel: %s\ntitle: %s\ndescription: %s\ntags: %s\n"
              % (args.channel, normalise(args.title), normalise(description), tags))
    out_parts.append(header)

    has_block = "block_id" in rows[0]
    seen_blocks = []
    act_counter = 0
    cur_block = object()

    for i, r in enumerate(rows):
        narr = normalise((r.get("narration") or "").strip())
        phen = normalise((r.get("phenomenon") or "").strip())
        if not narr:
            die("row %d: empty narration" % i)
        if not phen:
            die("row %d: empty phenomenon (no VISUAL = batch-killer)" % i)
        if len(narr.split()) > MAX_WORDS:
            die("row %d: narration %d words (max %d)" % (i, len(narr.split()), MAX_WORDS))
        for bad in TOKEN_RE.findall(narr):
            die("row %d: token {%s} in narration (never allowed)" % (i, bad))
        phen = expand(phen, canon, "row %d phenomenon" % i)

        motion = normalise((r.get("motion") or "").strip())
        move = (r.get("move") or "").strip().lower()
        if motion:
            motion = expand(motion, canon, "row %d motion" % i)
        if i in kling_idx and not motion:
            die("row %d: on the kling plan but motion is blank" % i)

        block = (r.get("block_id") or "").strip() if has_block else ""
        if block != cur_block:
            cur_block = block
            seen_blocks.append(block)
            if block in sections:
                name = sections[block].strip()
                if name.upper() == "COLD OPEN":
                    out_parts.append("## COLD OPEN\n")
                else:
                    act_counter += 1
                    out_parts.append("## ACT %s — %s\n"
                                     % (ROMAN[act_counter - 1], name.upper()))
            elif block.lower() in COLD_IDS or (not sections and len(seen_blocks) == 1
                                               and block.lower() in COLD_IDS):
                out_parts.append("## COLD OPEN\n")
            else:
                if len(seen_blocks) == 1 and block.lower() not in COLD_IDS:
                    # no cold-open block in the CSV: first section must still be
                    # a recognized heading or the parser HALTS. COLD OPEN it is —
                    # and the bridge folds the cold open into the first beats anyway.
                    out_parts.append("## COLD OPEN\n")
                else:
                    act_counter += 1
                    out_parts.append("## ACT %s — %s"
                                     % (ROMAN[act_counter - 1],
                                        (block or ("PART %d" % act_counter)).upper())
                                     + "\n")
        out_parts.append(emit_beat(narr, phen, motion, move) + "\n")

    body = "\n".join(out_parts)

    # ---- write -----------------------------------------------------------
    os.makedirs(args.out_dir, exist_ok=True)
    md_path = os.path.join(args.out_dir, args.slug + ".md")
    tj_path = os.path.join(args.out_dir, args.slug + ".thumb.json")
    kp_path = os.path.join(args.out_dir, args.slug + ".kling.json")

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    with open(tj_path, "w", encoding="utf-8") as fh:
        json.dump({"subject": thumb_subject,
                   "title": args.thumb_title,
                   "subtitle": args.thumb_subtitle}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(kp_path, "w", encoding="utf-8") as fh:
        json.dump({"kling_beats": kling_idx, "count": len(kling_idx), "mode": mode},
                  fh, indent=2)

    log("WROTE  %s  (%d beats, %d kling, blocks: %s)"
        % (md_path, len(rows), len(kling_idx), " ".join(b or "-" for b in seen_blocks)))
    log("WROTE  %s" % tj_path)
    log("WROTE  %s" % kp_path)
    log("NEXT   python3 parse_script.py %s   — the parser is the gate of record."
        % md_path)


if __name__ == "__main__":
    main()
