#!/usr/bin/env python3
"""
patch_chambers_variety.py -- Step 3 variety sweep for sacred-dawn/chambers-of-the-dead.

Idempotent. Verifies anchors before writing. Backs up to master.csv.pre_variety.
ASCII only. Run from anywhere; resolves the repo root by walking up for .git.

Fixes, all found by the Step 3 audit on the 320-row master:
  1. 'standing' on 92 beats (28.7%) -> ~5% , the 16 chamber beats where the motif
     is MOTIVATED (the dead on their feet) are protected and left alone.
  2. longest human-absent run of 6 beats at the b3/b4 seam -> broken.
  3. noun palette starved: animals 1.2%, plants 1.9%, children 0.6% -> seeded in
     the two terrestrial blocks (b1, b8) where they belong.
  4. VO density RISING into the b8 climax -> trimmed so the dimmer falls.
  5. top near-duplicate pairs (Jaccard 0.71 / 0.61 / 0.55 / 0.53 / 0.52) -> broken.
"""
import csv, os, re, sys, shutil, collections

SLUG    = "chambers-of-the-dead"
CHANNEL = "sacred-dawn"

# ---------------------------------------------------------------- path
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
idx  = {(int(r["block_id"]), int(r["clip_index"])): r for r in rows}

# ---------------------------------------------------------------- anchors
def count_standing():
    return sum(1 for r in rows if "standing" in r["phenomenon"].lower())

if len(rows) != 320:
    sys.exit("FAIL anchor: expected 320 rows, found %d" % len(rows))
if count_standing() <= 40:
    print("ALREADY APPLIED ('standing' on %d beats). Nothing to do." % count_standing())
    sys.exit(0)
if count_standing() != 92:
    print("WARN: expected 92 'standing' beats, found %d -- proceeding" % count_standing())

# ---------------------------------------------------------------- 1. standing sweep
PROTECT = {(6, c) for c in range(25, 33)} | {(7, c) for c in range(17, 33)}

ALT = [
 (r"\bstanding figures\b", ["upright figures", "figures on their feet", "motionless figures",
                            "figures at rest", "unmoving figures"]),
 (r"\bfigures standing still\b", ["figures held motionless", "figures at a dead halt"]),
 (r"\bstanding still with\b", ["motionless with", "halted with"]),
 (r"\bstanding still and\b",  ["motionless and", "held still and"]),
 (r"\bstanding motionless\b", ["at a dead halt"]),
 (r"\bthe standing figures\b", ["the upright figures", "the waiting figures"]),
 (r"\bstanding figure\b", ["upright figure", "figure on its feet"]),
 (r"\bfigure standing before\b", ["figure squared to", "figure planted before", "figure facing"]),
 (r"\bfigure standing alone\b", ["figure alone"]),
 (r"\bstanding at full height\b", ["risen to full height"]),
 (r"\bstanding at the\b", ["at the", "posted at the", "halted at the", "set at the"]),
 (r"\bstanding on dark\b", ["planted on dark", "set on dark"]),
 (r"\bstanding on bare\b", ["planted on bare"]),
 (r"\bstanding in the dark\b", ["held in the dark"]),
 (r"\bstanding in it\b", ["held in it"]),
 (r"\bstanding in warm\b", ["gathered in warm"]),
 (r"\bstanding in a low room\b", ["alone in a low room"]),
 (r"\bstanding together\b", ["gathered together"]),
 (r"\bstanding beside\b", ["set beside"]),
 (r"\bstanding before\b", ["squared to", "facing"]),
 (r"\bstanding above\b", ["spread above", "open above"]),
 (r"\bstanding behind\b", ["spread behind", "open behind"]),
 (r"\bstanding against\b", ["cut against", "ranged against", "set against"]),
 (r"\bstanding far\b", ["ranged far"]),
 (r"\bstanding small\b", ["small"]),
 (r"\bstanding quiet\b", ["gone quiet"]),
 (r"\bstanding perfectly straight\b", ["perfectly straight"]),
 (r"\bstanding straight up\b", ["driven straight up"]),
 (r"\bstanding over\b", ["spread over"]),
 (r"\bstanding water\b", ["still water"]),
 (r"\bstanding flame\b", ["held flame"]),
 (r"\bstanding fire\b", ["sheet of fire"]),
 (r"\bstanding light\b", ["held light"]),
 (r"\bstanding upright\b", ["upright"]),
 (r"\bstanding\b", ["set", "held", "risen", "planted"]),
]

ctr = collections.defaultdict(int)
n_swept = 0
for r in rows:
    key = (int(r["block_id"]), int(r["clip_index"]))
    if key in PROTECT:
        continue
    p = r["phenomenon"]; before = p
    for pat, opts in ALT:
        while re.search(pat, p):
            rep = opts[ctr[pat] % len(opts)]; ctr[pat] += 1
            p = re.sub(pat, rep, p, count=1)
    if p != before:
        r["phenomenon"] = p; n_swept += 1

# ---------------------------------------------------------------- 2-5. targeted edits
# full-cell replacements, each anchored on a unique fragment of the current cell
EDITS = [
 # -- 2. human-absent run at the b3/b4 seam (flat 120-125)
 (4, 3, "phenomenon", "a vast vaulted chamber holding coiled",
  "{windstores} wide interior, {enochman} small at the threshold of a vast vaulted chamber holding "
  "coiled masses of visible moving air stacked in tiers, each one lit from within, cold light along the walls"),
 (4, 6, "phenomenon", "the row of open doorways seen from above",
  "{windstores} wide high angle, the row of open doorways seen from above with air pouring out of two of them "
  "and one small figure on the ground before them, hard light raking the cliff face"),

 # -- 3. noun palette: animals, plants, children in the terrestrial blocks
 (1, 4, "phenomenon", "laid reed roofing seen from below",
  "{enochhome} medium low angle, laid reed roofing seen from below against a bright hard sky, a tethered goat "
  "in the shade beneath it, heat shimmer rising off the flat roofline, timber beams throwing sharp shadow bars"),
 (1, 30, "phenomenon", "in the forecourt at the end of the day",
  "{enochhome} medium, several adults and three small children gathered in the forecourt at the end of the day, "
  "warm low light on their faces, all of them looking the same direction"),
 (8, 9, "phenomenon", "bare pale upland ground with two long dry watercourses",
  "{upland} wide, bare pale upland ground with two long dry watercourses running through it and a few goats "
  "grazing the thin scrub, warm low morning sunlight raking across the surface"),
 (8, 14, "phenomenon", "several small figures running across swept ground",
  "{upland} medium, four children running across swept ground before a low dwelling with a dog cutting across "
  "in front of them, hard bright light and short sharp shadows"),

 # -- 5. near-duplicate breaks
 (5, 17, "phenomenon", "medium two-shot, {enochman} turned toward {guideone} at the rim",
  "{starprison} close from behind, the back of {enochman}'s head and one shoulder against the pit, "
  "{guideone} out of focus beyond him, warm light rising from below onto both"),
 (8, 1, "phenomenon", "medium two-shot, {guidetwo} and {enochman}",
  "{westmountain} wide side angle, {guidetwo} and {enochman} walking out from the base of the rock face "
  "in step with one another, cold hard light across the open ground ahead"),
 (7, 15, "phenomenon", "the cut wall with one hand open at his side",
  "{archface} extreme close low angle, one enormous open bronze-red hand held at rest against the scale of "
  "the cut rock behind it, cold light along the fingers"),
 (7, 22, "phenomenon", "one face lit hard from the side at the edge of the dark",
  "{hollowtwo} close, a pair of hands hanging loose at a figure's sides at the edge of the pale light, "
  "the fingers slack, hard light across the knuckles"),
 (7, 9, "phenomenon", "the face of {guidetwo} in three-quarter view",
  "{archface} extreme close, the mouth and jaw of {guidetwo} as he speaks, cold light off the rock wall "
  "picking out the line of the lower lip"),
 (7, 12, "phenomenon", "cut rock filling the frame with fine working marks",
  "{archface} medium high angle, the base of the cut wall where the tooled face meets bare swept ground, "
  "a clean junction running out of frame, cold light along it"),
 (8, 16, "phenomenon", "a bronze stylus cutting a dense line of script",
  "{upland} close, a stack of finished pale tablets ranged along a low wall in the sun, each face dense with "
  "cut script, bright daylight glancing across all of them"),
 (8, 38, "phenomenon", "one figure held in full silhouette against the cold light of a chamber mouth",
  "{hollowthree} wide, the front rank of the crowd with one gap where a figure has turned away from the "
  "chamber mouth, cold light falling through the space"),

 # -- 4. b8 dimmer: trim beats 31-40 so density falls into the climax
 (8, 31, "narration", "in about forty days", "The seed of Cain is taken off the earth in forty days."),
 (8, 32, "narration", "Which is the exact thing", "Which is exactly what was asked for, in a cave, by a voice."),
 (8, 34, "narration", "Whatever those chambers are", "It does not go in. Those chambers are not in the world the way rock is."),
 (8, 35, "narration", "in the way they were built to", "They fill anyway, from the inside, all at once."),
 (8, 36, "narration", "walks in somewhere along that face", "Everyone who drowned that day walks in along that face."),
 (8, 37, "narration", "the one that was already shut", "The bright one, the two dark ones, and the one already shut."),
 (8, 38, "narration", "a young man from a field stops speaking", "And in the third chamber, a young man stops speaking."),
 (8, 40, "narration", "the mountain goes on", "And the mountain goes on in the west, waiting for the day it was cut for."),
]

applied = skipped = 0
for blk, clip, col, anchor, new in EDITS:
    r = idx.get((blk, clip))
    if r is None:
        print("  SKIP b%d/%d -- row missing" % (blk, clip)); skipped += 1; continue
    if anchor not in r[col]:
        print("  SKIP b%d/%d %s -- anchor not found: %r" % (blk, clip, col, anchor[:40])); skipped += 1; continue
    r[col] = new; applied += 1

# ---------------------------------------------------------------- write
shutil.copyfile(CSVP, CSVP + ".pre_variety")
with open(CSVP, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

# ---------------------------------------------------------------- report
def words(s): return len([x for x in s.split() if any(c.isalnum() for c in x)])
st = count_standing()
neg = [ (r["block_id"], r["clip_index"]) for r in rows
        if re.search(r"\bno |\bnot |\bwithout |\bnever ", r["phenomenon"]) ]
LIT = r"light|lit\b|glow|bright|shadow|sun|glare|silhouett|shimmer|daylight"
unlit = [ (r["block_id"], r["clip_index"]) for r in rows if not re.search(LIT, r["phenomenon"]) ]
b8 = [words(r["narration"]) for r in rows if int(r["block_id"]) == 8]
q  = [sum(b8[i:i+10]) for i in range(0, 40, 10)]

print()
print("  backup      : %s.pre_variety" % os.path.basename(CSVP))
print("  swept       : %d beats de-duplicated on 'standing'" % n_swept)
print("  edits       : %d applied, %d skipped" % (applied, skipped))
print("  'standing'  : 92 -> %d  (%.1f%%)  [16 protected chamber beats kept]" % (st, st / 320.0 * 100))
print("  negations   : %s" % (neg or "none"))
print("  unlit beats : %s" % (unlit or "none"))
print("  b8 dimmer   : %s  %s" % (q, "FALLING" if q[3] < q[0] else "STILL RISING"))
print("  total words : %d" % sum(words(r["narration"]) for r in rows))
print()
print("  next: build_lego normalise, then blocks, then film")
