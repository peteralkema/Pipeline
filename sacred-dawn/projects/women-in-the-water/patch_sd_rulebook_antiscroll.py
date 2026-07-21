#!/usr/bin/env python3
"""patch_sd_rulebook_antiscroll.py

G11/G12 -- add the Enoch-scroll gravity-well STAGING negatives to
sacred-dawn/rulebook.json so the grid does not default to scroll/lectern/study
furniture. Bans the STAGING only; NEVER bans the subject ("book"/"bound
book"/"codex") -- {codex} is a bound book rendered as a monument.

Pure stdlib. LAPTOP-side (edits engine-owned data; does not import the engine).
Idempotent: skips any negative already present; writes a .pre_ backup once;
ASCII-only output. Dogfoods G22 -- defaults to the canonical repo path by
walking up for .git; pass --rulebook PATH to override.

    run from anywhere inside ~/Projects/Pipeline:
        python3 patch_sd_rulebook_antiscroll.py
    then verify, commit the named path, push; box: git pull --no-edit
"""
import argparse
import json
import os
import sys

# STAGING only -- the furniture/props the Enoch topic pulls in unprompted.
# Deliberately NOT "book"/"scroll" as bare subjects; scroll appears here only
# as staging phrases because {codex} replaced the scroll on this channel.
ADD = [
    "unfurled scroll",
    "rolled parchment scroll",
    "open scroll laid on a table",
    "book resting on a lectern",
    "open book on a reading stand",
    "book propped on a carved wooden stand",
    "lectern",
    "reading stand",
    "scholar's study interior",
    "library interior with rows of bookshelves",
    "writing desk beneath a tall window",
    "window directly behind a writing desk",
    "quill pen and inkwell on a desk",
    "scattered loose manuscript pages strewn across a surface",
]

# Guard: refuse to ever ban the subject, no matter how ADD is edited later.
FORBIDDEN_TO_BAN = {"book", "bound book", "codex", "the book", "ancient book"}


def repo_root(start):
    d = os.path.abspath(start)
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rulebook", default=None,
                    help="override path to rulebook.json (default: canonical)")
    args = ap.parse_args()

    if args.rulebook:
        path = os.path.abspath(args.rulebook)
    else:
        root = repo_root(os.getcwd()) or repo_root(os.path.dirname(os.path.abspath(__file__)))
        if not root:
            sys.stderr.write("ERROR: no .git found walking up; pass --rulebook PATH\n")
            sys.exit(1)
        path = os.path.join(root, "sacred-dawn", "rulebook.json")

    if not os.path.isfile(path):
        sys.stderr.write("ERROR: not found: %s\n" % path)
        sys.exit(1)

    # subject-safety guard
    bad = FORBIDDEN_TO_BAN.intersection({a.strip().lower() for a in ADD})
    if bad:
        sys.stderr.write("ERROR: refusing to ban subject(s): %s\n" % ", ".join(sorted(bad)))
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # anchor verify: must be the rulebook shape
    if not isinstance(data, dict) or not isinstance(data.get("negative"), list):
        sys.stderr.write("ERROR: anchor fail: no 'negative' list in %s\n" % path)
        sys.exit(1)

    existing = set(data["negative"])
    to_add = [x for x in ADD if x not in existing]

    if not to_add:
        print("OK: all %d anti-scroll negatives already present in %s; no change." % (len(ADD), path))
        return

    bak = path + ".pre_antiscroll"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="ascii") as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
        print("backup: %s" % bak)

    data["negative"].extend(to_add)

    with open(path, "w", encoding="ascii") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")

    print("OK: added %d staging negatives to %s:" % (len(to_add), path))
    for x in to_add:
        print("  + %s" % x)
    print("subject preserved: 'book' / 'bound book' / 'codex' NOT banned.")


if __name__ == "__main__":
    main()
