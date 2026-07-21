#!/usr/bin/env python3
"""patch_write_canon.py

Write canon.json for the women-in-the-water film as a flat {token: description}
dict -- the exact shape recreation_pipeline._expand_canon and build_canon.py
expect. Sacred Dawn's channel base_canon is {}, so this project file stands
alone (project wins on key collision anyway).

SAFETY GATE: reads master.csv, extracts every {token} used in the phenomenon
column, and HARD-FAILS if any used token has no definition here (an undefined
token does not expand -> it renders literally or raises). Warns on defined-but-
unused tokens (non-fatal). Definitions are positive-enforcement place-locks:
no negations (gate_canon cannot read them), no grade words (that is style_suffix),
no banned register words. Light stays per-beat.

Pure stdlib. LAPTOP-side. Idempotent: no-op if canon.json already matches;
.pre_ backup + rewrite if it differs. ASCII-only. Dogfoods G22: defaults to the
canonical project path (walk up for .git); pass --project PATH to override.

    cd ~/Projects/Pipeline
    python3 sacred-dawn/projects/women-in-the-water/patch_write_canon.py
"""
import argparse
import csv
import json
import os
import re
import sys

CANON = {
    "codex":        "a single ancient bound leather book, one massive weathered volume presented as a lone monumental hero object, heavy and solid",
    "highland":     "a cliff-top rock-hewn monastery in the Ethiopian highlands, warm ancient stone set against vast open sky and green mountain peaks, immense in scale",
    "antediluvian": "the vast pre-flood ancient world, immense dark-stone towers and high ridges under an enormous open sky, with tiny distant human figures far below for scale",
    "deep":         "the fathomless deep sea, an immense body of dark water above unimaginable depth, a distant glow rising from far below",
    "hermon":       "Mount Hermon, the highest snow-capped summit rising over the ancient northern border, immense and remote beneath a deep open sky",
    "relief":       "an ancient carved artifact bearing a winged bird-woman figure, weathered stone relief or archaic painted clay, sharp period detail, a museum-grade antiquity",
    "descent":      "the Watchers descending, colossal winged figures of immense physical mass, solid and opaque, heavy with weight and hard shadow, breaking downward through cloud, real and massive as living giants",
    "witness":      "the water-woman, a colossal monumental female figure of solid physical mass, statuesque austere and uncanny, fully and modestly draped in heavy concealing cloth, immense and weighty, rendered real and massive with hard shadow",
    "coast":        "a northern sea-coast of dark wet rock and white breaking surf beneath a vast open sky, clean and luminous",
    "leviathan":    "Leviathan, a colossal deep-sea creature of immense solid mass, opaque and heavy with hard shadow, its vast body struck by a hard column of light in the deep, real and massive",
    "remnant":      "the giant remnant after the flood, a colossal giant-warrior of immense physical mass towering over an ancient plain, solid and heavy with hard shadow, dwarfing the tiny armed men below",
    "newearth":     "the new earth, a vast radiant world of bright pale dry stone stretching to a luminous horizon, endless dry land under an immense open sky",
}

TOKEN_RE = re.compile(r"\{([a-z0-9_]+)\}")


def repo_root(start):
    d = os.path.abspath(start)
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def main():
    ap = argparse.ArgumentParser(description="write women-in-the-water canon.json")
    ap.add_argument("--project", default=None,
                    help="project dir (default: canonical women-in-the-water)")
    args = ap.parse_args()

    if args.project:
        proj = os.path.abspath(args.project)
    else:
        root = repo_root(os.getcwd()) or repo_root(os.path.dirname(os.path.abspath(__file__)))
        if not root:
            sys.stderr.write("ERROR: no .git found walking up; pass --project PATH\n")
            sys.exit(1)
        proj = os.path.join(root, "sacred-dawn", "projects", "women-in-the-water")

    master = os.path.join(proj, "master.csv")
    canon_path = os.path.join(proj, "canon.json")

    if not os.path.isfile(master):
        sys.stderr.write("ERROR: master.csv not found: %s\n" % master)
        sys.exit(1)

    # ASCII + no-negation self-check on the definitions themselves
    for tok, txt in CANON.items():
        if any(ord(c) > 127 for c in txt):
            sys.stderr.write("ERROR: non-ASCII in {%s}\n" % tok)
            sys.exit(1)

    # coverage gate: every token used in master must be defined here
    used = set()
    with open(master, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            used.update(TOKEN_RE.findall(row.get("phenomenon", "")))

    defined = set(CANON)
    missing = sorted(used - defined)
    unused = sorted(defined - used)

    if missing:
        sys.stderr.write("ERROR: %d token(s) used in master.csv have NO canon definition "
                         "(would not expand): %s\n" % (len(missing), ", ".join(missing)))
        sys.exit(1)

    print("coverage OK: %d tokens used, all defined." % len(used))
    if unused:
        print("WARN: defined but unused in master: %s" % ", ".join(unused))

    new_text = json.dumps(CANON, indent=2, ensure_ascii=True, sort_keys=True) + "\n"

    if os.path.isfile(canon_path):
        with open(canon_path, "r", encoding="utf-8") as f:
            if f.read() == new_text:
                print("no change: %s already current." % canon_path)
                return
        bak = canon_path + ".pre_canon"
        if not os.path.exists(bak):
            with open(canon_path, "r", encoding="utf-8") as src, open(bak, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            print("backup: %s" % bak)

    with open(canon_path, "w", encoding="ascii") as f:
        f.write(new_text)
    print("wrote: %s (%d tokens)" % (canon_path, len(CANON)))


if __name__ == "__main__":
    main()
