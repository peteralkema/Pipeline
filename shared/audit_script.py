#!/usr/bin/env python3
"""
audit_script.py -- read-only auditor for Line B LEGO-authored CSVs (the Bridge, step 3).

Reads master.csv (+ canon.json, + architecture.md if present) from a project
directory and prints: the three dials (novelty, span, escalation), spectacle
share, verb histogram, noun-palette coverage, longest human-absent run,
near-duplicate phenomenon pairs, word histogram + 55w ceiling violations
(parser counting rules), hero density per block, topic_class composition,
unresolved canon tokens, and a pre-spend bill of materials.

Never imports the engine. Pure stdlib. Exits non-zero on any hard gate
failure so it can sit in a shell chain ahead of csv2script.py.

Usage:
    python3 audit_script.py --project-dir <path/to/slug-src>
    python3 audit_script.py --csv master.csv --canon canon.json
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

STOPWORDS = set(
    "a an the of to in on at with and but or from into onto for as is are "
    "was were be been being he she they his her their this that it its who "
    "whom which not no do does did has have had you your yourself i we our".split()
)

HUMAN_WORDS = [
    "man", "men", "woman", "women", "figure", "hand", "hands", "face",
    "crowd", "teacher", "child", "children", "thief", "soldier", "soldiers",
    "mourners", "beggar", "martha", "mary", "shepherd", "farmer", "servant",
    "angels", "official", "officials", "brothers", "messenger",
]

HARD_GATE_FAILURES = []
WARNINGS = []


def load_rows(csv_path):
    with open(csv_path, newline="", encoding="ascii") as f:
        reader = csv.reader(f)
        header = next(reader)
        bad_field_count = []
        raw_rows = []
        for i, row in enumerate(reader, start=2):
            if len(row) != len(header):
                bad_field_count.append(i)
                continue
            raw_rows.append(dict(zip(header, row)))
    if bad_field_count:
        HARD_GATE_FAILURES.append(
            "CSV FIELD COUNT: rows with wrong column count (likely an unquoted "
            "comma in narration/phenomenon): lines %s" % bad_field_count
        )
    return raw_rows


def strip_breaks(text):
    return re.sub(r"<break[^>]*/>", " ", text)


def word_count(text):
    """Parser counting rule approximation: em-dash and SSML-break filtered,
    alnum tokens split on whitespace."""
    text = strip_breaks(text)
    text = text.replace("--", " ")
    return len(re.findall(r"[A-Za-z0-9']+", text))


def token_of(phenomenon):
    m = re.match(r"\{([a-z_]+)\}", phenomenon)
    return m.group(1) if m else None


def shot_scale_category(phenomenon):
    after = re.sub(r"^\{[a-z_]+\}\s*", "", phenomenon).lower()
    for k in ["extreme close", "extreme wide", "close", "medium", "wide"]:
        if after.startswith(k):
            return k
    return "other"


def check_negation(phenomenon):
    return bool(re.search(r"\bno[t]?\b", phenomenon.lower()))


def check_human_present(phenomenon):
    p = phenomenon.lower()
    return any(re.search(r"\b" + w + r"'?s?\b", p) for w in HUMAN_WORDS)


def tokenset(phenomenon):
    p = re.sub(r"\{[a-z_]+\}", "", phenomenon.lower())
    return set(re.findall(r"[a-z']+", p)) - STOPWORDS


def run_audit(rows, canon_tokens, spectacle_floor, topic_floor, human_absent_ceiling):
    N = len(rows)
    print("=" * 60)
    print("BASIC STATS")
    print("=" * 60)

    words = [word_count(r["narration"]) for r in rows]
    total_words = sum(words)
    print(f"rows (beats): {N}")
    print(f"total narration words: {total_words}")
    print(f"avg words/beat: {total_words / N:.1f}")
    print(f"min/max words per beat: {min(words)} / {max(words)}")
    runtime_min = total_words / 165
    print(f"estimated runtime @165wpm: {runtime_min:.1f} min ({runtime_min * 60:.0f}s)")

    violations = [(r["block_id"] + "." + r["clip_index"], w) for r, w in zip(rows, words) if w > 55]
    if violations:
        HARD_GATE_FAILURES.append(f"55W CEILING: {len(violations)} beats over: {violations}")
    print(f"55w ceiling violations: {len(violations)}")

    for r in rows:
        if check_negation(r["phenomenon"]):
            HARD_GATE_FAILURES.append(
                f"NEGATION in phenomenon at {r['block_id']}.{r['clip_index']}: {r['phenomenon']}"
            )
        if r["narration"].strip("\"") and token_of(r["narration"]):
            HARD_GATE_FAILURES.append(
                f"TOKEN LEAKED INTO NARRATION at {r['block_id']}.{r['clip_index']}"
            )

    if canon_tokens is not None:
        used_tokens = {token_of(r["phenomenon"]) for r in rows if token_of(r["phenomenon"])}
        unresolved = used_tokens - set(canon_tokens.keys())
        if unresolved:
            HARD_GATE_FAILURES.append(f"UNRESOLVED CANON TOKENS: {sorted(unresolved)}")
        print(f"canon tokens used: {len(used_tokens)}  defined: {len(canon_tokens)}  unresolved: {len(unresolved)}")

    print()
    print("=" * 60)
    print("HERO DENSITY PER BLOCK")
    print("=" * 60)
    blocks = defaultdict(list)
    for r in rows:
        blocks[r["block_id"]].append(r)
    for b in sorted(blocks, key=lambda x: int(x)):
        brows = blocks[b]
        heroes = sum(1 for r in brows if r["weight"] == "hero")
        print(f"block {b}: {heroes}/{len(brows)} hero ({heroes / len(brows) * 100:.0f}%)")

    print()
    print("=" * 60)
    print("KLING OVERRIDE BUDGET")
    print("=" * 60)
    kling = [r for r in rows if r["air"] == "kling"]
    kling_pct = len(kling) / N * 100
    print(f"kling beats: {len(kling)}/{N} = {kling_pct:.1f}% (target band 10-15%)")
    if not (8 <= kling_pct <= 17):
        WARNINGS.append(f"kling override at {kling_pct:.1f}%, outside the 10-15% band")

    print()
    print("=" * 60)
    print("TOPIC CLASS COMPOSITION")
    print("=" * 60)
    tc = Counter(r["topic_class"] for r in rows)
    universal_pct = tc.get("universal", 0) / N * 100
    print(f"{dict(tc)}  universal share: {universal_pct:.0f}% (floor {topic_floor}%)")
    if universal_pct < topic_floor:
        HARD_GATE_FAILURES.append(f"TOPIC MIX: universal share {universal_pct:.0f}% below {topic_floor}% floor")

    print()
    print("=" * 60)
    print("DIAL 1: NOVELTY PER BLOCK (unique subjects / beats)")
    print("=" * 60)
    for b in sorted(blocks, key=lambda x: int(x)):
        brows = blocks[b]
        subs = [r["subject"] for r in brows]
        uniq = len(set(subs))
        print(f"block {b}: {uniq} unique / {len(subs)} beats = {uniq / len(subs):.2f}")
        if uniq < 2:
            WARNINGS.append(f"block {b} has fewer than 2 distinct subjects")

    print()
    print("=" * 60)
    print("DIAL 2: SPAN PER SUBJECT (normalized block spread, ceiling 0.35 except declared spine)")
    print("=" * 60)
    subj_blocks = defaultdict(set)
    for r in rows:
        subj_blocks[r["subject"]].add(int(r["block_id"]))
    total_blocks = max(int(b) for b in blocks) - min(int(b) for b in blocks) + 1
    spans = []
    for s, bs in subj_blocks.items():
        span = (max(bs) - min(bs)) / max(1, (total_blocks - 1))
        spans.append((s, span, sorted(bs)))
    spans.sort(key=lambda x: -x[1])
    over_ceiling = [s for s in spans if s[1] > 0.35]
    for s, span, bs in spans[:15]:
        flag = "  *** OVER 0.35, VERIFY THIS IS A DECLARED SPINE ***" if span > 0.35 else ""
        print(f"{span:.2f}  blocks {bs}  '{s}'{flag}")
    if len(over_ceiling) > 3:
        WARNINGS.append(f"{len(over_ceiling)} subjects exceed the 0.35 span ceiling -- verify each is intentional")

    print()
    print("=" * 60)
    print("DIAL 3: ESCALATION (avg scale per block)")
    print("=" * 60)
    scale_by_block = {b: [int(r["scale"]) for r in blocks[b]] for b in blocks}
    for b in sorted(scale_by_block, key=lambda x: int(x)):
        v = scale_by_block[b]
        print(f"block {b}: avg {sum(v) / len(v):.2f}, max {max(v)}")
    scale5 = [r["block_id"] + "." + r["clip_index"] for r in rows if r["scale"] == "5"]
    if len(scale5) > 2:
        WARNINGS.append(f"scale-5 used on {len(scale5)} beats, verify the finale-only discipline: {scale5}")

    print()
    print("=" * 60)
    print("SPECTACLE SHARE (scale>=3)")
    print("=" * 60)
    spectacle = [r for r in rows if int(r["scale"]) >= 3]
    spec_pct = len(spectacle) / N * 100
    print(f"{len(spectacle)}/{N} = {spec_pct:.1f}% (gate >= {spectacle_floor}%)")
    if spec_pct < spectacle_floor:
        HARD_GATE_FAILURES.append(f"SPECTACLE SHARE: {spec_pct:.1f}% below {spectacle_floor}% gate")

    print()
    print("=" * 60)
    print("SHOT-SCALE REPETITION (3+ consecutive identical framing)")
    print("=" * 60)
    cats = [shot_scale_category(r["phenomenon"]) for r in rows]
    run_start = 0
    any_run = False
    for i in range(1, len(cats) + 1):
        if i == len(cats) or cats[i] != cats[run_start]:
            length = i - run_start
            if length >= 3:
                beat_ids = [rows[j]["block_id"] + "." + rows[j]["clip_index"] for j in range(run_start, i)]
                print(f"RUN: {cats[run_start]} x{length}  beats {beat_ids}")
                any_run = True
            run_start = i
    if any_run:
        HARD_GATE_FAILURES.append("SHOT-SCALE REPETITION: 3+ consecutive identical framing found (see above)")
    else:
        print("clean")

    print()
    print("=" * 60)
    print("VERB HISTOGRAM (top 8, -ing forms in phenomenon lines)")
    print("=" * 60)
    verb_like = Counter()
    for r in rows:
        text = r["phenomenon"].lower()
        for w in re.findall(r"[a-z']+", text):
            if w.endswith("ing") and w not in ("king", "morning", "evening", "something"):
                verb_like[w] += 1
    total_verbs = sum(verb_like.values()) or 1
    for w, c in verb_like.most_common(8):
        print(f"{w}: {c} ({c / total_verbs * 100:.1f}%)")
    top3_share = sum(c for _, c in verb_like.most_common(3)) / total_verbs * 100
    print(f"top-3 share: {top3_share:.1f}% (gate < 30%)")
    if top3_share >= 30:
        WARNINGS.append(f"verb top-3 share {top3_share:.1f}%, at or above the 30% ceiling")

    print()
    print("=" * 60)
    print("NOUN PALETTE COVERAGE")
    print("=" * 60)
    noun_like = Counter()
    for r in rows:
        text = re.sub(r"\{[a-z_]+\}", "", r["phenomenon"].lower())
        for w in re.findall(r"[a-z']+", text):
            if w not in STOPWORDS and len(w) > 3 and not w.endswith("ing"):
                noun_like[w] += 1
    print(f"unique descriptive words (len>3, non-stop, non -ing): {len(noun_like)}")
    print("top 10:", noun_like.most_common(10))

    print()
    print("=" * 60)
    print(f"HUMAN-ABSENT RUNS (gate: longest <= {human_absent_ceiling})")
    print("=" * 60)
    runs = []
    cur = 0
    for r in rows:
        if not check_human_present(r["phenomenon"]):
            cur += 1
        else:
            if cur > 0:
                runs.append(cur)
            cur = 0
    if cur > 0:
        runs.append(cur)
    longest = max(runs) if runs else 0
    print(f"runs: {runs if runs else 'none'}")
    print(f"longest: {longest}")
    if longest > human_absent_ceiling:
        HARD_GATE_FAILURES.append(f"HUMAN-ABSENT RUN: longest run {longest} exceeds ceiling {human_absent_ceiling}")

    print()
    print("=" * 60)
    print("NEAR-DUPLICATE PAIRS (Jaccard >= 0.42 on phenomenon, token stripped)")
    print("=" * 60)
    sets = [tokenset(r["phenomenon"]) for r in rows]
    dupes = []
    for i in range(N):
        for j in range(i + 1, N):
            a, b = sets[i], sets[j]
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            if jac >= 0.42:
                dupes.append((jac, rows[i]["block_id"] + "." + rows[i]["clip_index"],
                              rows[j]["block_id"] + "." + rows[j]["clip_index"]))
    dupes.sort(reverse=True)
    print(f"count: {len(dupes)}")
    for jac, a, b in dupes[:15]:
        print(f"{jac:.2f}  {a} <-> {b}")
    if dupes:
        WARNINGS.append(f"{len(dupes)} near-duplicate phenomenon pairs found -- judge each, do not mass-fix")

    print()
    print("=" * 60)
    print("PRE-SPEND BILL OF MATERIALS")
    print("=" * 60)
    still_cost = N * 0.08
    kling_cost = len(kling) * 0.42
    tts_cost = 1.0
    total = still_cost + kling_cost + tts_cost
    print(f"stills: {N} x $0.08 = ${still_cost:.2f}")
    print(f"kling: {len(kling)} x $0.42 = ${kling_cost:.2f}")
    print(f"TTS+whisper: ~${tts_cost:.2f}")
    print(f"TOTAL: ~${total:.2f}")

    print()
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    if WARNINGS:
        print(f"{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print(f"  - {w}")
    if HARD_GATE_FAILURES:
        print(f"\n{len(HARD_GATE_FAILURES)} HARD GATE FAILURE(S):")
        for f in HARD_GATE_FAILURES:
            print(f"  - {f}")
        print("\nAUDIT FAILED. Do not compile.")
        return 1
    print("\nAUDIT PASSED. Clear to compile.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Read-only audit for Line B LEGO-authored CSVs.")
    ap.add_argument("--project-dir", help="directory containing master.csv (+ canon.json, architecture.md)")
    ap.add_argument("--csv", help="explicit path to master.csv (overrides --project-dir)")
    ap.add_argument("--canon", help="explicit path to canon.json (overrides --project-dir)")
    ap.add_argument("--spectacle-floor", type=float, default=30.0)
    ap.add_argument("--topic-floor", type=float, default=70.0)
    ap.add_argument("--human-absent-ceiling", type=int, default=5)
    args = ap.parse_args()

    if args.csv:
        csv_path = Path(args.csv)
    elif args.project_dir:
        csv_path = Path(args.project_dir) / "master.csv"
    else:
        ap.error("must supply --project-dir or --csv")

    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found", file=sys.stderr)
        return 2

    canon_path = None
    if args.canon:
        canon_path = Path(args.canon)
    elif args.project_dir:
        candidate = Path(args.project_dir) / "canon.json"
        if candidate.exists():
            canon_path = candidate

    canon_tokens = None
    if canon_path and canon_path.exists():
        with open(canon_path, encoding="ascii") as f:
            canon_tokens = json.load(f)

    rows = load_rows(csv_path)
    if HARD_GATE_FAILURES:
        for f in HARD_GATE_FAILURES:
            print(f"HARD FAILURE: {f}", file=sys.stderr)
        return 1

    return run_audit(rows, canon_tokens, args.spectacle_floor, args.topic_floor, args.human_absent_ceiling)


if __name__ == "__main__":
    sys.exit(main())
