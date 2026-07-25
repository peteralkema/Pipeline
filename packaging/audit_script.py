#!/usr/bin/env python3
"""
audit_script.py — Step 3 of the bridge (_BRIDGE.md §5).

Read-only audit of a LEGO master.csv BEFORE compile and BEFORE any spend.
Runs the three dials, variety instruments, word gates (parser counting rules),
render-safety scan, topic mix, and the bill of materials. Pure stdlib.

Usage
  python3 audit_script.py master.csv
  python3 audit_script.py master.csv --canon canon.json --front 40 --json report.json

Exit codes: 0 = all hard gates pass · 1 = hard failure(s) · 2 = input error
Hard failures: narration > --max-words · air=kling with blank motion ·
unresolved {token} (when --canon given) · missing required columns.
Everything else is reported, judged by the operator, never auto-fixed.
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict

REQUIRED = ["narration", "phenomenon"]
OPTIONAL = ["block_id", "clip_index", "weight", "register", "subject", "scale",
            "air", "move", "motion", "topic_class", "fx"]

# Words that indicate a human is in frame (approximate, for absence-run detection)
HUMAN_WORDS = {
    "man", "men", "woman", "women", "figure", "figures", "face", "faces",
    "hand", "hands", "child", "children", "crowd", "people", "priest",
    "king", "queen", "shepherd", "elder", "elders", "soldier", "soldiers",
    "prophet", "family", "mother", "father", "son", "daughter", "worker",
    "workers", "servant", "servants", "witness", "witnesses", "body", "bodies",
    "silhouette", "silhouettes", "profile",
}

# Distress-signal verbs/phrases that trip the render classifier silently.
# Banked: use environmental/consequence verbs instead, esp. cold open + front 40.
RENDER_RISK = [
    "scream", "screaming", "screams", "corpse", "corpses", "blood", "bleeding",
    "drowning", "drowns", "burning alive", "burned alive", "strangl", "chok",
    "stabb", "slaughter", "butcher", "mutilat", "severed", "severing", "impal", "writh",
    "agony", "tortur", "dying", "dies ", "dead bod", "carnage", "gore",
]

VISUAL_VERBS = {
    "stands", "standing", "walks", "walking", "rises", "rising", "falls",
    "falling", "burns", "burning", "glows", "glowing", "moves", "moving",
    "turns", "turning", "opens", "opening", "closes", "closing", "pours",
    "pouring", "breaks", "breaking", "spreads", "spreading", "hangs",
    "hanging", "drifts", "drifting", "settles", "settling", "cracks",
    "cracking", "flows", "flowing", "climbs", "climbing", "descends",
    "descending", "gathers", "gathering", "scatters", "scattering",
    "kneels", "kneeling", "reaches", "reaching", "waits", "waiting",
    "watches", "watching", "carries", "carrying", "lifts", "lifting",
    "sinks", "sinking", "swells", "swelling", "erupts", "erupting",
    "collapses", "collapsing", "towers", "towering", "stretches",
    "stretching", "shines", "shining", "flickers", "flickering",
}

TOKEN_RE = re.compile(r"\{([a-z0-9_]+)\}")


def log(msg=""):
    print(msg, flush=True)


def rule(c="-", n=78):
    log(c * n)


def words_parser_style(text):
    """The parser's own counting: plain .split(). Em-dashes count as tokens."""
    return len(text.split())


def tok_set(text):
    return set(re.findall(r"[a-z']+", text.lower()))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        cols = rdr.fieldnames or []
        rows = list(rdr)
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        log("INPUT ERROR: missing required columns: %s" % ", ".join(missing))
        log("Columns present: %s" % ", ".join(cols))
        sys.exit(2)
    return rows, cols


def main():
    ap = argparse.ArgumentParser(description="LEGO master.csv audit (read-only).")
    ap.add_argument("csv_path")
    ap.add_argument("--canon", help="canon.json to verify token resolution")
    ap.add_argument("--front", type=int, default=40, help="render-safety window")
    ap.add_argument("--max-words", type=int, default=55)
    ap.add_argument("--kling-words", type=int, default=18,
                    help="warn threshold for narration on air=kling beats")
    ap.add_argument("--dup-threshold", type=float, default=0.42)
    ap.add_argument("--topic-floor", type=float, default=0.70)
    ap.add_argument("--still-price", type=float, default=0.08)
    ap.add_argument("--kling-price", type=float, default=0.42)
    ap.add_argument("--json", dest="json_out", help="write full report as JSON")
    args = ap.parse_args()

    rows, cols = load(args.csv_path)
    n = len(rows)
    if n == 0:
        log("INPUT ERROR: empty csv")
        sys.exit(2)

    has = {c: (c in cols) for c in OPTIONAL}
    hard_fails = []
    report = {"beats": n, "columns": cols}

    canon = {}
    if args.canon:
        with open(args.canon, encoding="utf-8") as fh:
            canon = json.load(fh)

    # Per-row basics
    blocks = []
    for i, r in enumerate(rows):
        r["_i"] = i
        r["_narr"] = (r.get("narration") or "").strip()
        r["_phen"] = (r.get("phenomenon") or "").strip()
        r["_words"] = words_parser_style(r["_narr"])
        r["_block"] = (r.get("block_id") or "b?").strip() if has["block_id"] else "b?"
        r["_air"] = (r.get("air") or "").strip().lower() if has["air"] else ""
        blocks.append(r["_block"])
    block_order = list(dict.fromkeys(blocks))
    nblocks = len(block_order)

    log("AUDIT  %s  — %d beats · %d blocks · columns ok" % (args.csv_path, n, nblocks))
    rule("=")

    # ---- HARD GATE: words -------------------------------------------------
    over = [(r["_i"], r["_block"], r["_words"]) for r in rows if r["_words"] > args.max_words]
    empty_narr = [r["_i"] for r in rows if not r["_narr"]]
    empty_phen = [r["_i"] for r in rows if not r["_phen"]]
    log("WORDS  max %d | mean %.1f | >%d: %d beat(s)" % (
        max(r["_words"] for r in rows),
        sum(r["_words"] for r in rows) / n, args.max_words, len(over)))
    for i, b, w in over[:20]:
        log("  FAIL row %d (%s): %d words" % (i, b, w))
    if over:
        hard_fails.append("words: %d beats over %d" % (len(over), args.max_words))
    if empty_narr:
        hard_fails.append("empty narration rows: %s" % empty_narr[:10])
    if empty_phen:
        hard_fails.append("empty phenomenon rows (batch-killer): %s" % empty_phen[:10])
    report["words_over"] = over

    # ---- HARD GATE: kling/motion invariant --------------------------------
    if has["air"]:
        kling_rows = [r for r in rows if r["_air"] == "kling"]
        bad_motion = [r["_i"] for r in kling_rows
                      if not (r.get("motion") or "").strip()] if has["motion"] else \
                     [r["_i"] for r in kling_rows]
        long_kling = [(r["_i"], r["_words"]) for r in kling_rows
                      if r["_words"] > args.kling_words]
        log("AIR    kling %d | kb/floor %d" % (len(kling_rows), n - len(kling_rows)))
        if bad_motion:
            hard_fails.append("air=kling with blank motion: rows %s" % bad_motion[:10])
            log("  FAIL blank motion on kling rows: %s" % bad_motion[:10])
        for i, w in long_kling[:10]:
            log("  WARN row %d: %d words on a kling beat (>%d = freeze-tail risk)"
                % (i, w, args.kling_words))
        report["kling_count"] = len(kling_rows)
    else:
        kling_rows = []
        log("AIR    column absent — all-floor compile; kling plan can be auto-drafted")
        report["kling_count"] = 0

    # ---- HARD GATE: token resolution --------------------------------------
    used_tokens = Counter()
    for r in rows:
        for t in TOKEN_RE.findall(r["_phen"]):
            used_tokens[t] += 1
        for t in TOKEN_RE.findall(r["_narr"]):
            hard_fails.append("token {%s} in NARRATION row %d (never allowed)" % (t, r["_i"]))
    if args.canon:
        unresolved = [t for t in used_tokens if t not in canon]
        if unresolved:
            hard_fails.append("unresolved tokens: %s" % unresolved)
            log("TOKENS FAIL unresolved: %s" % unresolved)
        else:
            log("TOKENS %d distinct, all resolve against canon" % len(used_tokens))
    else:
        log("TOKENS %d distinct (no --canon given, resolution unchecked): %s"
            % (len(used_tokens), ", ".join(sorted(used_tokens)) or "none"))
    report["tokens"] = dict(used_tokens)

    rule()

    # ---- DIAL 1: novelty (new subjects per block) --------------------------
    if has["subject"]:
        first_block_of = {}
        subj_rows = defaultdict(list)
        for r in rows:
            s = (r.get("subject") or "").strip().lower()
            if not s:
                continue
            subj_rows[s].append(r["_i"])
            first_block_of.setdefault(s, r["_block"])
        new_per_block = Counter(first_block_of.values())
        log("DIAL 1 NOVELTY — new subjects per block (gate: >=2 every block, incl. last)")
        bad_blocks = []
        for b in block_order:
            c = new_per_block.get(b, 0)
            flag = "" if c >= 2 else "   <-- BELOW GATE"
            if c < 2:
                bad_blocks.append(b)
            log("  %-6s %d%s" % (b, c, flag))
        report["novelty"] = {b: new_per_block.get(b, 0) for b in block_order}

        # ---- DIAL 2: span ---------------------------------------------------
        log("DIAL 2 SPAN — (last-first)/(N-1) per subject (gate: <=0.35 except one spine)")
        spans = {}
        for s, idxs in sorted(subj_rows.items(), key=lambda kv: -len(kv[1])):
            span = (max(idxs) - min(idxs)) / max(1, n - 1)
            spans[s] = round(span, 2)
        wide = {s: v for s, v in spans.items() if v > 0.35}
        for s, v in sorted(wide.items(), key=lambda kv: -kv[1])[:15]:
            log("  %-28s span %.2f  (%d beats)" % (s, v, len(subj_rows[s])))
        log("  wide-span subjects: %d (one declared spine is legal; more is smear)"
            % len(wide))
        report["span"] = spans
    else:
        log("DIAL 1/2 SKIPPED — no subject column (authoring gap: add it; it is the")
        log("  instrument that killed Methuselah's 65th fire)")

    # ---- DIAL 3: escalation ------------------------------------------------
    if has["scale"]:
        try:
            per_block_scale = {}
            for b in block_order:
                vals = [int(r["scale"]) for r in rows
                        if r["_block"] == b and str(r.get("scale", "")).strip().isdigit()]
                per_block_scale[b] = round(sum(vals) / len(vals), 2) if vals else None
            log("DIAL 3 ESCALATION — mean scale per block (should rise; peak held back)")
            log("  " + "  ".join("%s:%s" % (b, per_block_scale[b]) for b in block_order))
            final_third = (2 * nblocks) // 3
            early5 = [(r["_i"], r["_block"]) for r in rows
                      if str(r.get("scale", "")).strip() == "5"
                      and block_order.index(r["_block"]) < final_third]
            if early5:
                log("  WARN scale-5 before final third: %d beat(s) %s"
                    % (len(early5), early5[:8]))
            report["escalation"] = per_block_scale
        except Exception as exc:
            log("DIAL 3 error reading scale column: %s" % exc)
    else:
        log("DIAL 3 SKIPPED — no scale column")

    rule()

    # ---- Variety: lexical/verb proxy --------------------------------------
    verb_hits = Counter()
    for r in rows:
        for w in r["_phen"].lower().split():
            w = w.strip(".,;:—-()\"'")
            if w in VISUAL_VERBS:
                verb_hits[w] += 1
    total_v = sum(verb_hits.values()) or 1
    top3 = verb_hits.most_common(3)
    top3_share = sum(c for _, c in top3) / total_v
    log("VERBS  (visual-verb proxy) distinct %d | top-3 share %.0f%% (gate <30%%): %s"
        % (len(verb_hits), 100 * top3_share,
           ", ".join("%s×%d" % (w, c) for w, c in top3)))
    report["verb_top3_share"] = round(top3_share, 2)

    # ---- Near-duplicates ---------------------------------------------------
    sets = [tok_set(r["_phen"]) for r in rows]
    dups = []
    for i in range(n):
        for j in range(i + 1, min(i + 60, n)):  # window: dupes cluster locally
            v = jaccard(sets[i], sets[j])
            if v >= args.dup_threshold:
                dups.append((i, j, round(v, 2)))
    # plus a coarse global pass on identical leading tokens
    log("DUPES  Jaccard>=%.2f (windowed): %d pair(s) — judge each, never mass-fix"
        % (args.dup_threshold, len(dups)))
    for i, j, v in sorted(dups, key=lambda t: -t[2])[:12]:
        log("  %d ~ %d  %.2f  | %s || %s" % (i, j, v, rows[i]["_phen"][:52],
                                             rows[j]["_phen"][:52]))
    report["dup_pairs"] = len(dups)

    # ---- Human-absence runs ------------------------------------------------
    absent_run, worst_run, run_start = 0, (0, -1), 0
    for r in rows:
        present = bool(tok_set(r["_phen"]) & HUMAN_WORDS)
        if present:
            absent_run = 0
        else:
            if absent_run == 0:
                run_start = r["_i"]
            absent_run += 1
            if absent_run > worst_run[0]:
                worst_run = (absent_run, run_start)
    no_human = sum(1 for r in rows if not (tok_set(r["_phen"]) & HUMAN_WORDS))
    log("HUMAN  absent %d/%d beats (%.0f%%) | longest absent run %d starting row %d "
        "(gate <=5)" % (no_human, n, 100 * no_human / n, worst_run[0], worst_run[1]))
    report["human_absent_run"] = worst_run[0]

    # ---- Render safety, front window --------------------------------------
    risky = []
    for r in rows[:args.front]:
        blob = (r["_narr"] + " " + r["_phen"]).lower()
        hits = [k for k in RENDER_RISK
                if (k in blob if " " in k
                    else re.search(r"\b" + re.escape(k), blob))]
        if hits:
            risky.append((r["_i"], hits))
    log("SAFETY front %d beats: %d risky (distress-signal terms trip the classifier "
        "silently)" % (args.front, len(risky)))
    for i, hits in risky[:10]:
        log("  row %d: %s" % (i, ", ".join(hits)))
    report["render_risk_front"] = risky

    # ---- Topic mix ---------------------------------------------------------
    if has["topic_class"]:
        mix = Counter((r.get("topic_class") or "untagged").strip().lower() for r in rows)
        uni = mix.get("universal", 0) / n
        log("TOPIC  %s | universal share %.0f%% (batch floor %.0f%%)"
            % (dict(mix), 100 * uni, 100 * args.topic_floor))
        report["topic_mix"] = dict(mix)
    else:
        log("TOPIC  column absent — REQUIRED for the N>=40 experiment; add topic_class")

    # ---- Hero density ------------------------------------------------------
    if has["weight"]:
        hero_by_block = Counter(r["_block"] for r in rows
                                if (r.get("weight") or "").strip().lower() == "hero")
        log("HEROES per block: %s" % {b: hero_by_block.get(b, 0) for b in block_order})

    rule()

    # ---- Bill of materials -------------------------------------------------
    kn = report["kling_count"]
    cost = n * args.still_price + kn * args.kling_price
    log("BILL   %d stills × $%.2f + %d kling × $%.2f  =  ~$%.2f  (+TTS ~$1)"
        % (n, args.still_price, kn, args.kling_price, cost))
    report["est_cost"] = round(cost, 2)

    rule("=")
    if hard_fails:
        log("HARD FAILURES (%d):" % len(hard_fails))
        for h in hard_fails:
            log("  FAIL %s" % h)
        log("Exit 1 — fix the named rows individually and re-run.")
        code = 1
    else:
        log("ALL HARD GATES PASS. Soft findings above are judged, not auto-fixed.")
        code = 0

    if args.json_out:
        report["hard_fails"] = hard_fails
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        log("Report written: %s" % args.json_out)
    sys.exit(code)


if __name__ == "__main__":
    main()
