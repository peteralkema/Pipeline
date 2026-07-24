#!/usr/bin/env python3
"""
patch_chambers_align.py -- block alignment for sacred-dawn/chambers-of-the-dead.

Brings every block to its exact word target, then adds a block-end break to close
the residual. Run AFTER the 0.95 speaking_rate render.

MEASURED BASIS (do not re-derive):
  speaking_rate 0.95 -> Elliot at 158 WPM = 0.380s/word, mp3 1549.0s.
  Container 1600s = 8 blocks x 200s = 8 x 40 clips x 5.000s.
  200s holds 527 words. Reserve 2.0s for a break on b1-b7 -> 198s = 521 words.
  b8 carries no break (the film ends) -> 527 words.

TARGETS      b1-b7 = 521w   b8 = 527w        (film 4174w -> 1585s + 14s = 1599s)

WHAT IS PROTECTED AND WHY
  * b1/40 'It stops being ground.' (4w) -- handoff, deliberately clipped
  * b2/29 'Evening does not come.' (4w) -- the beat is the pause
  * b6/35 'One. Two. Three. Four.' (4w) -- the count
  * b7/14 and b8/39 -- the refrain and its inversion, wording is load-bearing
  * b8/31-40 -- the dimmer. Trimmed on purpose so VO density FALLS into the
    climax. All of b8's words go into beats 1-30. Never refill 31-40.

WHAT THIS IGNORES
  calibrate's per-beat 'add Nw / cut Nw' column. At +-0.5s that is measuring
  TTS noise (+-1.3% run to run) and whisper drops (16 words lost this render).
  Block word totals are sums and survive; per-beat attribution downstream of a
  drop does not. Zero delta is achievable on WORDS, not on delivered seconds.

Idempotent. Anchor-verified. Backs up to master.csv.pre_align. ASCII only.
"""
import csv, os, re, sys, shutil

SLUG, CHANNEL = "chambers-of-the-dead", "sacred-dawn"
TAG      = ' <break time="2.0s" />'
TARGETS  = {1:521, 2:521, 3:521, 4:521, 5:521, 6:521, 7:521, 8:527}

def repo_root(start=None):
    p = os.path.abspath(start or os.getcwd())
    while p != "/":
        if os.path.isdir(os.path.join(p, ".git")): return p
        p = os.path.dirname(p)
    sys.exit("FAIL: no .git found walking up. Pass the repo root as argv[1].")

ROOT = repo_root(sys.argv[1] if len(sys.argv) > 1 else None)
CSVP = os.path.join(ROOT, CHANNEL, "projects", SLUG, "master.csv")
if not os.path.isfile(CSVP): sys.exit("FAIL: missing %s" % CSVP)

rows = list(csv.DictReader(open(CSVP, encoding="utf-8")))
COLS = list(rows[0].keys())
idx  = {(int(r["block_id"]), int(r["clip_index"])): r for r in rows}
def W(s):
    s = re.sub(r"<[^>]*>", "", s)
    return len([x for x in s.split() if any(c.isalnum() for c in x)])

if len(rows) != 320: sys.exit("FAIL anchor: expected 320 rows, found %d" % len(rows))
if any("<break" in r["narration"] for r in rows):
    print("ALREADY APPLIED (break tags present). Nothing to do."); sys.exit(0)

# ---------------------------------------------------------------- edits
# (block, clip, anchor_fragment, new_narration)
E = [
 # ---- b1  +31 ----
 (1, 7,  "what he is shown",        "What he writes down is not his own thinking. It is what he is shown."),
 (1, 14, "Not a bell",              "Not a bell. Not an animal. Not anything with a throat."),
 (1, 17, "ordinary evening",        "It is an ordinary evening, at the end of an ordinary day, when they come."),
 (1, 24, "still in his hand",       "The stone is still in his hand, and the marks are still wet."),
 (1, 26, "has not been slept in",   "The bed has not been slept in, and the lamp has burned itself dry."),
 # ---- b2  +42 ----
 (2, 1,  "Fifty paces",             "Fifty paces further on, the dust gives out and it is glass."),
 (2, 4,  "It is not cold",          "It is not cold. It is not warm either. It has no temperature at all."),
 (2, 8,  "steps out onto it",       "He steps out onto it, and it holds him, and he keeps walking."),
 (2, 15, "follows them onto the glass", "Nothing else follows them onto the glass. Nothing living, and nothing that flies."),
 (2, 16, "Not that day",            "Not that day, and not on any of the days after it."),
 (2, 18, "runs east and meets",     "Behind him the glass runs east until it meets the sky, and that is all."),
 (2, 19, "The hills are not there", "The hills are not there. The upland is not there. The east is not there."),
 (2, 36, "what he should call him", "Enoch asks him, at last, what he is supposed to call him."),
 # ---- b3  +5 ----
 (3, 17, "heat arrives",            "The heat arrives a long time before the sound does."),
 (3, 37, "flattens everything else","The noise of it flattens everything else there is."),
 # ---- b4  -17 ----
 (4, 4,  "the shape of water in a jar", "He can see their shape the way you see water take the shape of a jar."),
 (4, 5,  "changes colour behind it","One is let out while he watches, and the whole sky changes colour behind it."),
 (4, 29, "Three of them stand",     "Three stand to the east, three to the south, and they are not the same colour."),
 (4, 21, "flat on the top of it",   "He puts his hand on it, the way he did on the glass."),
 (4, 37, "the colour of the sky",   "And the seat is a blue he will later call the colour of the deepest sky."),
 # ---- b5  +7 ----
 (5, 1,  "the ground gives out",    "Beyond the seven mountains, the ground simply gives out."),
 (5, 19, "the whole charge",        "That is the whole charge. They came up late, once."),
 (5, 35, "columns of fire, falling", "And going down into it, columns of fire, falling steadily."),
 (5, 27, "for coming up late",      "Ten thousand years, for the crime of coming up late."),
 # ---- b6  +9 ----
 (6, 4,  "the horizon has something", "Then, after a long time, the horizon has something on it."),
 (6, 25, "quietly, are people",     "And standing in that light, quietly and without moving, are people."),
 (6, 38, "the answer is three",     "Raphael answers him, and the answer he gives is three."),
 # ---- b7  -20 ----
 (7, 6,  "None of them has opened", "They are all standing exactly as they were. None has opened his mouth."),
 (7, 15, "from the face of the earth", "It goes on, Raphael says, until the seed of Cain is gone from the earth."),
 (7, 16, "the smoke standing straight up", "Enoch thinks of the wall on the plain, and the smoke behind."),
 (7, 21, "Not one of them was stopped", "Not one was stopped. Not one was made to pay while there was time."),
 (7, 26, "facing the same way",     "It is full, and every one of them faces the opening."),
 (7, 33, "the fourth one last",     "He comes to the fourth last and stops, because it is not an opening."),
 (7, 40, "everyone else will be",   "Because they will not be raised on it. There is a day when everyone else is."),
 # ---- b8  +12, beats 1-30 ONLY (the dimmer) ----
 (8, 2,  "not his to be told",      "It is simply not his to be told, and after a while he stops asking."),
 (8, 8,  "takes no time",           "The walk home takes no time at all that he can account for."),
 (8, 9,  "in the ordinary morning", "They put him down on his own upland in an ordinary morning, in ordinary light."),
 (8, 25, "of a man not yet born",   "The day comes in the six hundredth year of a man not born when Enoch left."),
 (8, 18, "No room left",            "Cut edge to edge. There is no room left on any face of them."),
]

applied = skipped = 0
for blk, clip, anchor, new in E:
    r = idx.get((blk, clip))
    if r is None:
        print("  SKIP b%d/%d row missing" % (blk, clip)); skipped += 1; continue
    if anchor not in r["narration"]:
        print("  SKIP b%d/%d anchor %r not found in: %s" % (blk, clip, anchor, r["narration"][:60]))
        skipped += 1; continue
    r["narration"] = new; applied += 1

# ---------------------------------------------------------------- breaks
for b in range(1, 8):
    r = idx[(b, 40)]
    if "<" not in r["narration"]:
        r["narration"] = r["narration"].rstrip() + TAG

# ---------------------------------------------------------------- verify + write
print("\n  block   words  target  delta   seconds@158wpm")
ok = True
for b in range(1, 9):
    tot = sum(W(r["narration"]) for r in rows if int(r["block_id"]) == b)
    d = tot - TARGETS[b]
    if d: ok = False
    brk = 2.0 if b < 8 else 0.0
    print("   b%d     %4d    %4d   %+4d      %6.1fs" % (b, tot, TARGETS[b], d, tot * 0.380 + brk))
film = sum(W(r["narration"]) for r in rows)
print("\n  film    %4d    %4d   %+4d      %6.1fs   (container 1600.0s)"
      % (film, sum(TARGETS.values()), film - sum(TARGETS.values()), film * 0.380 + 14.0))
over = [(r["block_id"], r["clip_index"], W(r["narration"])) for r in rows if W(r["narration"]) > 55]
print("  edits: %d applied, %d skipped | beats over 55w: %s" % (applied, skipped, over or "none"))

if not ok:
    print("\n  NOT WRITTEN -- a block missed its target. Fix the edit list first.")
    sys.exit(1)

shutil.copyfile(CSVP, CSVP + ".pre_align")
with open(CSVP, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
print("\n  written. backup: %s.pre_align" % os.path.basename(CSVP))
print("  next: normalise, blocks, then audio + ffprobe. Ignore per-beat cut/add.")
