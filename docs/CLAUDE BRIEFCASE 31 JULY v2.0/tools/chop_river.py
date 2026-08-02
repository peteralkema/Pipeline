#!/usr/bin/env python3
"""
chop_river.py -- river draft (.md) + per-project config (.json) -> master.csv

This is the generalized, config-driven version of the four scratch scripts
written during the Astronomy Book of Enoch (Part II) session (chop_river_stage1.py
+ tag_beats.py + gen_visuals.py + assign_and_write.py). Proven against Part II's
own river draft (reproduces the same 271-beat split) before being used for real
on Part III -- see PROOF section at the bottom of this docstring.

WHAT STAYS GENERIC (the engine, this file):
  - sentence-aware chunking with a hard word-cap, two merge passes
  - ordered-regex token routing + an exact-substring FORCE_REASSIGN override list
  - per-token visual-variant cycling with human-word forcing + distance-repeat guard
  - scale/move/weight/topic_class/air assignment, kling front-N slicing
  - master.csv writer (ascii, matches audit_script.py's encoding expectation)

WHAT MUST COME FROM THE CONFIG (per-project, never hardcoded here):
  - register (target/hardcap word counts, kling_count) -- Line B's 15-25 w/beat
    band and golden-pair's ~46 are different tools with different numbers, not
    the same tool with a flag
  - block list (scale baseline per block, ordered regex routes per block)
  - force_reassign overrides
  - canon token descriptions + visual variant banks
  - kling motion prompts (one per kling-count beat)
  - scale-5 finale rules (which block/subject gets the one or two permitted
    scale-5 beats -- keep this to a handful film-wide, per the "finale-only
    discipline" audit_script.py's own warning threshold implies)

CONFIG SCHEMA (see the Part III config shipped alongside this file for a real
worked example):
{
  "register": {"target_words": 46, "hardcap_words": 55,
               "merge_floor": 32, "aggressive_floor": 15, "aggressive_hardcap": 58},
  "kling_count": 12,
  "kling_motion": ["...", ...],            # len == kling_count
  "blocks": {
    "0": {"scale": 4, "routes": [["regex", "token", "subject"], ...]},
    ...
  },
  "force_reassign": [["block_id", "narration substring", "token", "subject"], ...],
  "canon": {"token": "canon.json description string", ...},
  "variants": {"token": [["dist", "description text", true_or_false_has_human], ...], ...},
  "lore_tokens": ["token_that_should_be_topic_class_lore_not_universal", ...],
  "scale5_rules": [{"block": "4", "position": "last"}, {"subject": "throne_glimpse", "position": "last"}]
}

USAGE:
    python3 chop_river.py river-draft.md config.json --out master.csv

LIMITATIONS, stated plainly rather than hidden:
  - The routing/variant DATA in a config is still hand-authored creative work --
    this tool does not invent canon tokens or visual language from the river
    text. It automates the MECHANICAL half of the chop (word-count discipline,
    variety-gate compliance, CSV assembly), not the creative half (deciding
    what a beat should look like). That decision stays human/session-judged,
    same as it was in scratch form.
  - No per-token hard-cap enforcement yet (the same gap flagged for
    audit_script.py in _CANONICAL.md Sec 9) -- a config that overuses one token
    will still need a human to notice the histogram and fix the config, same
    as Part II needed twice. Proposed next addition, not yet built.
  - Sentence splitting is a regex heuristic, not a real tokenizer. Good enough
    for prose this consistently punctuated; would need hardening for messier
    source material (e.g. heavy quotation, dialogue).

PROOF THIS IS GENUINELY GENERIC, NOT JUST PART II RENAMED:
  Run against Part III's river draft with a from-scratch Part III config
  (different token names, different variant banks, different scale/kling
  choices) in the same session that built this file -- see SESSION-NOTES for
  the Part III beat count / audit / compile / machine-gate results as the
  actual proof, not an isolated unit test of this file alone.
"""
import argparse
import csv
import itertools
import json
import random
import re
import sys
from collections import Counter


def wc(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", s))


def asciify(s: str) -> str:
    repl = {
        "\u2014": " -- ", "\u2013": "-",
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2026": "...",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def para_list(txt: str):
    paras = [p.strip() for p in txt.split("\n\n")]
    return [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip() and p.strip() != "---"]


def sentences(para: str):
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z"*])', para.strip())
    return [s.strip() for s in raw if s.strip()]


def split_long(s: str, hardcap: int):
    if wc(s) <= hardcap:
        return [s]
    for delim in [" -- ", "; ", ": ", ", "]:
        positions = [m.start() for m in re.finditer(re.escape(delim), s)]
        if not positions:
            continue
        mid = len(s) / 2
        best = min(positions, key=lambda p: abs(p - mid))
        left = s[: best + len(delim)].strip()
        right = s[best + len(delim):].strip()
        if left and right and wc(left) < wc(s) and wc(right) < wc(s):
            return split_long(left, hardcap) + split_long(right, hardcap)
    words = s.split()
    left = " ".join(words[:hardcap])
    right = " ".join(words[hardcap:])
    return [left] + (split_long(right, hardcap) if right else [])


def chunk_paragraph(para: str, target: int, hardcap: int):
    pieces = []
    for s in sentences(para):
        pieces.extend(split_long(s, hardcap))
    beats, cur, curwc = [], [], 0
    for p in pieces:
        pw = wc(p)
        if curwc + pw > hardcap and cur:
            beats.append(" ".join(cur))
            cur, curwc = [], 0
        cur.append(p)
        curwc += pw
        if curwc >= target and curwc >= target - 16:
            beats.append(" ".join(cur))
            cur, curwc = [], 0
    if cur:
        beats.append(" ".join(cur))
    return beats


def merge_pass(beats, hardcap, floor):
    out, i = [], 0
    while i < len(beats):
        cur = beats[i]
        while wc(cur) < floor and i + 1 < len(beats) and wc(cur) + wc(beats[i + 1]) <= hardcap:
            i += 1
            cur = cur + " " + beats[i]
        out.append(cur)
        i += 1
    return out


def aggressive_merge(beats, hardcap, floor):
    beats = list(beats)
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(beats):
            if wc(beats[i]) < floor:
                if i + 1 < len(beats) and wc(beats[i]) + wc(beats[i + 1]) <= hardcap:
                    beats[i:i + 2] = [beats[i] + " " + beats[i + 1]]
                    changed = True
                    continue
                elif i - 1 >= 0 and wc(beats[i - 1]) + wc(beats[i]) <= hardcap:
                    beats[i - 1:i + 1] = [beats[i - 1] + " " + beats[i]]
                    changed = True
                    continue
            i += 1
    return beats


def parse_blocks(text: str):
    text = asciify(text)
    body = text.split("\n\n---\n\n", 1)[1] if "\n\n---\n\n" in text else text.split("---", 1)[1]
    parts = re.split(r"\n## ([IVX]+)\. (.+?)\n\n", body)
    cold_open = parts[0]
    acts = []
    i = 1
    while i < len(parts):
        acts.append((parts[i], parts[i + 1], parts[i + 2]))
        i += 3
    blocks = {0: para_list(cold_open)}
    for idx, (roman, title, acttext) in enumerate(acts, start=1):
        blocks[idx] = para_list(acttext)
    return blocks


AUDIT_HUMAN_WORDS = ["man", "men", "woman", "women", "figure", "hand", "hands", "face",
                      "crowd", "teacher", "child", "children", "thief", "soldier", "soldiers",
                      "mourners", "beggar", "martha", "mary", "shepherd", "farmer", "servant",
                      "angels", "official", "officials", "brothers", "messenger"]
HUMAN_TEST = re.compile(r"\b(" + "|".join(AUDIT_HUMAN_WORDS) + r")'?s?\b", re.IGNORECASE)


def route(block_id, text, routes):
    for pattern, token, subj in routes:
        if re.search(pattern, text, re.IGNORECASE):
            return token, subj
    return None, None


def assign_moves_fuzzy(n, palette=("push", "pull", "crane", "settle", "jibl", "jibr"), max_run=3, seed=42):
    """Pure distributional move assignment -- no content read, no semantics.
    Roughly equal share of each move type across n beats, no run longer than
    max_run identical values in a row. Deterministic (seeded) so the same
    river+config always produces the same move sequence -- reproducible, not
    random each run. This replaces content-based move selection entirely per
    Peter's 30 Jul direction: 'pure maths... you don't even need to read the
    script... just apply fuzzy logic' -- Part II's move column had defaulted
    to 83.6% push because narrow keyword/token conditions rarely matched and
    'push' was both the close-up default AND the unconditional fallback."""
    rng = random.Random(seed)
    base = n // len(palette)
    rem = n % len(palette)
    counts = {m: base for m in palette}
    for m in rng.sample(palette, rem):
        counts[m] += 1
    pool = []
    for m, c in counts.items():
        pool += [m] * c
    rng.shuffle(pool)
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(pool):
            run = 1
            j = i - 1
            while j >= 0 and pool[j] == pool[i]:
                run += 1
                j -= 1
            if run > max_run:
                for k in range(i + 1, len(pool)):
                    if pool[k] != pool[i] and not (k > 0 and pool[k - 1] == pool[i]):
                        pool[i], pool[k] = pool[k], pool[i]
                        changed = True
                        break
            i += 1
    return pool


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("river_md")
    ap.add_argument("config_json")
    ap.add_argument("--out", default="master.csv")
    args = ap.parse_args()

    text = open(args.river_md, encoding="utf-8").read()
    cfg = json.load(open(args.config_json, encoding="utf-8"))

    reg = cfg["register"]
    target, hardcap = reg["target_words"], reg["hardcap_words"]
    merge_floor = reg.get("merge_floor", 32)
    agg_floor = reg.get("aggressive_floor", 15)
    agg_hardcap = reg.get("aggressive_hardcap", hardcap + 3)

    raw_blocks = parse_blocks(text)

    chopped = {}
    for b, paras in raw_blocks.items():
        # Law 33 (1 Aug): per-block register override -- blocks may carry their
        # own "register" dict (any subset of the global keys). Block 0 chops
        # short (opening ramp); the feature register is earned, not default.
        breg = (cfg["blocks"].get(str(b), {}) or {}).get("register", {})
        b_target = breg.get("target_words", target)
        b_hardcap = breg.get("hardcap_words", hardcap)
        b_mfloor = breg.get("merge_floor", merge_floor)
        b_afloor = breg.get("aggressive_floor", agg_floor)
        b_ahard = breg.get("aggressive_hardcap", agg_hardcap if not breg else b_hardcap)
        beats = []
        for p in paras:
            beats.extend(chunk_paragraph(p, b_target, b_hardcap))
        beats = merge_pass(beats, b_hardcap, b_mfloor)
        beats = aggressive_merge(beats, b_ahard, b_afloor)
        chopped[str(b)] = beats

    def _hc(b):
        return (cfg["blocks"].get(str(b), {}) or {}).get("register", {}).get("hardcap_words", hardcap)
    over = [(b, wc(x)) for b, beats in chopped.items() for x in beats if wc(x) > _hc(b)]
    if over:
        print(f"WARNING: {len(over)} beat(s) over the {hardcap}-word hard cap after merge -- "
              f"these need a manual one-line trim before AUDIT: {over}", file=sys.stderr)

    # ---- route each beat to a token/subject ----
    tagged = {}
    for b_str, beats in chopped.items():
        block_cfg = cfg["blocks"][b_str]
        routes = block_cfg["routes"]
        last_token = None
        fallback = routes[0][1] if routes else "untagged"
        out = []
        for beat in beats:
            token, subj = route(b_str, beat, routes)
            if token is None:
                token, subj = last_token or fallback, last_token or fallback
            for fb, snippet, ftok, fsubj in cfg.get("force_reassign", []):
                if fb == b_str and snippet in beat:
                    token, subj = ftok, fsubj
                    break
            last_token = token
            out.append({"narration": beat, "token": token, "subject": subj})
        tagged[b_str] = out

    variants = cfg["variants"]

    # ---- break same-token runs > 6 (the TABLEAU RUN hard gate intake.py checks
    # and audit_script.py does not -- proven 29 Jul evening: a previously
    # audit-clean CSV had 8 real runs of 7-9 identical tokens invisible to
    # audit_script.py's own checks). Round-robins to the block's other tokens
    # rather than leaving a bare/awkward cut. ----
    for b_str, beats in tagged.items():
        block_tokens = [t for _, t, _ in cfg["blocks"][b_str]["routes"]]
        seen_block_tokens = sorted(set(b["token"] for b in beats))
        alt_pool = [t for t in seen_block_tokens] or block_tokens
        run_tok, run_start, alt_cursor = None, 0, 0
        i = 0
        while i < len(beats):
            tok = beats[i]["token"]
            if tok == run_tok:
                run_len = i - run_start + 1
                if run_len > 6:
                    alternatives = [t for t in alt_pool if t != tok]
                    if alternatives:
                        new_tok = alternatives[alt_cursor % len(alternatives)]
                        alt_cursor += 1
                        beats[i]["token"] = new_tok
                        beats[i]["subject"] = new_tok
                        run_tok, run_start = new_tok, i
            else:
                run_tok, run_start = tok, i
            i += 1

    # regenerate VISUAL/phenomenon after any run-break reassignment above
    counters = {k: itertools.cycle(range(len(v))) for k, v in variants.items()}
    for b_str, beats in tagged.items():
        since_human = 0
        prev_dist = None
        dist_run = 0
        for beat in beats:
            token = beat["token"]
            vlist = variants[token]
            idx = next(counters[token])
            dist, desc, _declared = vlist[idx]
            if dist == prev_dist:
                dist_run += 1
            else:
                dist_run = 1
            if dist_run >= 3:
                alt = [v for v in vlist if v[0] != dist]
                if alt:
                    dist, desc, _ = alt[idx % len(alt)]
                    dist_run = 1
            prev_dist = dist
            # human-forcing runs LAST so no later swap can discard the appended
            # element (30 Jul bug: dist-swap after forcing silently dropped it,
            # producing audit HUMAN-ABSENT failures the generator thought it
            # had prevented)
            has_human = bool(HUMAN_TEST.search(desc))
            if not has_human and since_human >= 3:
                desc = desc + ", a hand's silhouette just visible at the frame's edge"
                has_human = True
            since_human = 0 if has_human else since_human + 1
            beat["phenomenon"] = "{%s} %s, %s" % (token, dist, desc)
            beat["dist"] = dist

    # ---- assign scale/move/weight/topic_class/air ----
    lore_tokens = set(cfg.get("lore_tokens", []))
    rows = []
    for b_str, beats in tagged.items():
        block_cfg = cfg["blocks"][b_str]
        scale_base = block_cfg["scale"]
        for i, beat in enumerate(beats, start=1):
            dist = beat["dist"]
            token = beat["token"]
            weight = "hero" if dist in ("wide", "extreme wide") and scale_base >= 3 else "support"
            tc = "lore" if token in lore_tokens else "universal"
            rows.append({
                "block_id": b_str, "clip_index": str(i),
                "narration": beat["narration"], "phenomenon": beat["phenomenon"],
                "weight": weight, "air": "floor", "topic_class": tc,
                "subject": beat["subject"], "scale": str(scale_base), "move": None,
                "motion": "",
            })

    # move: pure distributional assignment, not content-based -- see
    # assign_moves_fuzzy() docstring for why (roughly equal push/pull/crane/
    # settle, no run > 3, deterministic seed for reproducibility).
    move_cfg = cfg.get("move_distribution", {})
    move_pool = assign_moves_fuzzy(
        len(rows),
        palette=tuple(move_cfg.get("palette", ("push", "pull", "crane", "settle"))),
        max_run=move_cfg.get("max_run", 3),
        seed=move_cfg.get("seed", 42),
    )
    for r, m in zip(rows, move_pool):
        r["move"] = m

    for rule in cfg.get("scale5_rules", []):
        if "block" in rule:
            block_rows = [r for r in rows if r["block_id"] == rule["block"]]
            if block_rows:
                (block_rows[-1] if rule.get("position") == "last" else block_rows[0])["scale"] = "5"
        elif "subject" in rule:
            matches = [r for r in rows if r["subject"] == rule["subject"]]
            if matches:
                (matches[-1] if rule.get("position") == "last" else matches[0])["scale"] = "5"

    kling_count = cfg.get("kling_count", 0)
    kling_motion = cfg.get("kling_motion", [])
    for idx, r in enumerate(rows):
        if idx < kling_count:
            r["air"] = "kling"
            if idx < len(kling_motion):
                r["motion"] = kling_motion[idx]

    fieldnames = ["block_id", "clip_index", "narration", "phenomenon", "weight",
                  "air", "topic_class", "subject", "scale", "move", "motion"]
    with open(args.out, "w", newline="", encoding="ascii") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    tok_counts = Counter(r["phenomenon"].split("}")[0].strip("{") for r in rows)
    total_words = sum(wc(r["narration"]) for r in rows)
    print(f"wrote {args.out}: {len(rows)} beats, {total_words} words, "
          f"avg {total_words/len(rows):.1f} w/beat, {kling_count} kling", file=sys.stderr)
    print("token distribution (top 8):", tok_counts.most_common(8), file=sys.stderr)

    # ---- Law 22: composition-archetype report. Per-token gates pass while the
    # viewer sees one composition wearing several token names (Part III receipt:
    # ~80 seated-authority beats across four throne tokens). Config supplies
    # "token_archetypes": {token: archetype}; share cap default 25%. Untagged
    # tokens are flagged loudly -- tagging is mandatory, not optional. ----
    arch_map = cfg.get("token_archetypes", {})
    if arch_map:
        n = len(rows)
        cap = float(cfg.get("archetype_share_cap", 0.25))
        untagged = sorted(t for t in tok_counts if t not in arch_map)
        arch_counts = Counter()
        for t, c in tok_counts.items():
            arch_counts[arch_map.get(t, "UNTAGGED")] += c
        print("archetype shares (cap %.0f%%):" % (cap * 100), file=sys.stderr)
        over = []
        for a, c in arch_counts.most_common():
            share = c / n
            flag = "  <-- OVER CAP" if share > cap else ""
            print("  %-30s %3d  %5.1f%%%s" % (a, c, 100 * share, flag), file=sys.stderr)
            if share > cap:
                over.append(a)
        if untagged:
            print("LAW 22 WARNING: tokens missing archetype tag: %s" % ", ".join(untagged),
                  file=sys.stderr)
        if over:
            print("LAW 22 WARNING: archetype(s) over cap: %s -- vary how the subject "
                  "is SEEN (spanning rule), do not just rename tokens." % ", ".join(over),
                  file=sys.stderr)
    else:
        print("LAW 22 WARNING: config has no token_archetypes map -- archetype "
              "shares unchecked.", file=sys.stderr)


if __name__ == "__main__":
    main()
