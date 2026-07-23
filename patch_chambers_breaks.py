#!/usr/bin/env python3
"""
patch_chambers_breaks.py -- block-end break tags for sacred-dawn/chambers-of-the-dead.

Appends <break time="2.0s" /> to the narration of the final beat of blocks 1-7.
Block 8 gets none: the film ends there and a trailing silence is just dead tail.

WHY 2.0s. Methuselah shipped 1.8s to 5.6s, with the two longest (5.5s, 5.6s) at the
b1 and b2 seams -- the exact window where measured retention collapses. Silence at a
seam is an exit ramp. 2.0s is turnable in Filmora; you can always add air in the
timeline, you cannot take baked silence out.

FORMAT is not invented here -- it is the form build_lego.py already handles
(see its docstring ~line 84): spaced, self-closing, stripped before splitting,
and whisper emits no words for it.

CALIBRATE WARNING. calibrate counts the deliberate silence as part of the beat and
reports a 9-11s overrun that is not real. IGNORE every 'cut Nw' on a beat carrying
a break -- that is b1/40 through b7/40. The film is ~60s short of container; after
these tags it will LOOK ~46s short. The real number is 60.

Idempotent. Anchor-verified. Backs up to master.csv.pre_breaks. ASCII only.
"""
import csv, os, re, sys, shutil

SLUG, CHANNEL = "chambers-of-the-dead", "sacred-dawn"
TAG      = ' <break time="2.0s" />'
BLOCKS   = range(1, 8)          # 1..7, NOT 8
LASTBEAT = 40

def repo_root(start=None):
    p = os.path.abspath(start or os.getcwd())
    while p != "/":
        if os.path.isdir(os.path.join(p, ".git")):
            return p
        p = os.path.dirname(p)
    sys.exit("FAIL: no .git found walking up. Pass the repo root as argv[1].")

ROOT = repo_root(sys.argv[1] if len(sys.argv) > 1 else None)
CSVP = os.path.join(ROOT, CHANNEL, "projects", SLUG, "master.csv")
if not os.path.isfile(CSVP):
    sys.exit("FAIL: missing %s" % CSVP)

rows = list(csv.DictReader(open(CSVP, encoding="utf-8")))
COLS = list(rows[0].keys())

if len(rows) != 320:
    sys.exit("FAIL anchor: expected 320 rows, found %d" % len(rows))

existing = [r for r in rows if "<break" in r["narration"]]
if existing:
    print("ALREADY APPLIED (%d rows carry a break tag). Nothing to do." % len(existing))
    for r in existing:
        print("   b%s/%s  %s" % (r["block_id"], r["clip_index"],
                                 re.search(r"<break[^>]*>", r["narration"]).group(0)))
    sys.exit(0)

idx = {(int(r["block_id"]), int(r["clip_index"])): r for r in rows}
applied = 0
for b in BLOCKS:
    r = idx.get((b, LASTBEAT))
    if r is None:
        print("  SKIP b%d/%d -- row missing" % (b, LASTBEAT)); continue
    if "<" in r["narration"]:
        print("  SKIP b%d/%d -- already carries markup" % (b, LASTBEAT)); continue
    r["narration"] = r["narration"].rstrip() + TAG
    applied += 1

shutil.copyfile(CSVP, CSVP + ".pre_breaks")
with open(CSVP, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

def spoken(s):
    s = re.sub(r"<[^>]*>", "", s)
    return len([x for x in s.split() if any(c.isalnum() for c in x)])

print()
print("  backup       : %s.pre_breaks" % os.path.basename(CSVP))
print("  breaks added : %d  (blocks 1-7, beat 40, 2.0s each = %.1fs total)" % (applied, applied * 2.0))
print("  block 8      : none by design (film ends)")
print("  spoken words : %d  (tags excluded -- unchanged by this patch)"
      % sum(spoken(r["narration"]) for r in rows))
for b in BLOCKS:
    r = idx[(b, LASTBEAT)]
    print("   b%d/40  ...%s" % (b, r["narration"][-58:]))
print()
print("  REMINDER: ignore any 'cut Nw' calibrate reports on b1/40 .. b7/40")
