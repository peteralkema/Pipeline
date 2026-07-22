#!/usr/bin/env python3
"""
patch_methuselah_b6_restore.py -- VO convergence pass 2, block 6 only.

Pass 1 over-trimmed four beats in block 6; the block came in ~9s under and its
seam read -11.9s. Some of that is a real shortfall and some is measurement drift
(the pointer desynced where whisper dropped tail words), but these four beats are
genuinely too terse as WRITING regardless of the number, so they get words back.

Restores 6/21, 6/24, 6/25, 6/36 (+15 words, ~+5.5s). Leaves the 6/40 break tag
untouched. Idempotent; verifies each beat still holds its pass-1 text before
writing; backs up to master.csv.pre_b6.

  cd ~/Pipeline/sacred-dawn/projects
  python ~/Pipeline/shared/patch_methuselah_b6_restore.py
"""
import csv
import re
import shutil
import sys
from pathlib import Path

MASTER = Path.home() / "Pipeline" / "sacred-dawn" / "projects" / "methuselah" / "master.csv"

# key -> (expected pass-1 text, new text)
EDITS = {
    "6/21": (
        "Enoch was inside it by lamplight, bent over stretched hides, making marks.",
        "Enoch was inside it by lamplight, bent over stretched hides, making marks nobody else could make.",
    ),
    "6/24": (
        "I am writing what I was shown.",
        "I am writing down what I was shown, Enoch said. The names. What is coming, and what comes after.",
    ),
    "6/25": (
        "For whom, Methuselah said. Nobody here can read.",
        "For whom, Methuselah asked. Nobody here can read a word of it.",
    ),
    "6/36": (
        "A column of light stood on the high stone.",
        "A column of pale light stood on the high stone, straight down out of a clear and empty sky.",
    ),
}


def wc(s):
    s = re.sub(r"<[^>]*>|\[[^\]]*\]", " ", s or "")
    return len([t for t in s.split() if re.search(r"[A-Za-z0-9]", t)])


def main() -> int:
    if not MASTER.exists():
        print("FAIL: %s not found" % MASTER)
        return 1
    rows = list(csv.DictReader(MASTER.open()))
    idx = {"%s/%s" % (r["block_id"], r["clip_index"]): r for r in rows}

    # idempotency + anchor check
    applied = all(idx[k]["narration"] == new for k, (old, new) in EDITS.items())
    if applied:
        print("already applied -- no change")
        return 0
    bad = [k for k, (old, new) in EDITS.items() if idx[k]["narration"] not in (old, new)]
    if bad:
        print("FAIL: these beats do not hold their expected pass-1 text: %s" % ", ".join(bad))
        for k in bad:
            print("   %s now: %r" % (k, idx[k]["narration"]))
        return 1

    before = sum(wc(r["narration"]) for r in rows if r["block_id"] == "6")
    for k, (old, new) in EDITS.items():
        idx[k]["narration"] = new
    after = sum(wc(r["narration"]) for r in rows if r["block_id"] == "6")

    # guards
    if "<break" not in idx["6/40"]["narration"]:
        print("FAIL: 6/40 break tag missing -- aborting")
        return 1
    over = [k for k, r in idx.items() if wc(r["narration"]) > 55]
    if over:
        print("FAIL: beats over 55 words: %s" % over)
        return 1

    backup = MASTER.with_suffix(".csv.pre_b6")
    shutil.copy2(MASTER, backup)
    with MASTER.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print("backed up -> %s" % backup)
    print("b06 words %d -> %d (+%d, ~+%.1fs)" % (before, after, after - before, (after - before) * 0.37))
    print("6/40 tag intact: ...%s" % idx["6/40"]["narration"][-28:])
    print("\nNEXT:")
    print("  python ~/Pipeline/build_lego.py normalise --project methuselah")
    print("  python ~/Pipeline/build_lego.py blocks    --project methuselah")
    print("  python -u ~/Pipeline/build_lego.py audio  --project methuselah")
    print("  python ~/Pipeline/build_lego.py calibrate --project methuselah methuselah/voiceover.json")
    print("\nthen CONFIRM 12/36-40 now measure (tail no longer dropping words).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
