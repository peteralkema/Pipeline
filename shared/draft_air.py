#!/usr/bin/env python3
"""draft_air.py -- fill `air` + `motion` by MOTION-WANT score under a sliding Kling quota.

Two decisions, separated:

  HOW MANY per block  -- a linear sliding quota, front-loaded: --start (default 0.80) of
                         block 1 animates, falling to --end (0.20) by the last block. The
                         viewer who bails at ninety seconds never reaches block 8, so the
                         spend rides the gate. Blunt, but definitive and cheap to reason about.

  THE FLEX            -- a quota alone starves the back half of a film whose most
                         motion-hungry images are late (this film's deep, the Leviathan in
                         its light shaft, the woman rising). So --score-floor rescues any
                         beat scoring at or above it, in ANY block, on top of its block's
                         quota. The curve still front-loads the spend; the hero motion beats
                         can never be dropped for being late. Set --score-floor 99 to disable.

  WHICH ones          -- within each block, beats are RANKED by how much the picked frame
                         wants to move, and the top N take the quota. Water and the deep,
                         suspended matter, moving cloth, fire, and motion verbs score UP;
                         carved stone, inscriptions, pages and text score DOWN. So the
                         Leviathan animates and the wall relief rides the free floor.

The vocabulary is the doctrine's, not a land film's: `air` in _LEGO.md means literal visible
suspended matter -- dust, smoke, mist, embers, WATER, drifting cloth. An earlier drafter
omitted water entirely, which scored a deep-sea film at zero from block 4 on while distant
cloud in a wide shot scored high. Water is a first-class cue here.

Because it scores the project's own `phenomenon` text, the split is specific to each film with
no per-film configuration -- the benefit of keeping every per-beat decision in a column.

  air    = "kling" -> animate   |  "kb" -> explicit Ken Burns floor
  motion = drafted ONLY on kling beats, and phrased to agree with the `move` already drafted.

Default fills only blank `air` (idempotent, preserves your corrections); --redraft overwrites.
--dry-run prints the per-block quota, the chosen beats, and the BORDERLINE pairs (lowest
chosen vs highest rejected) so the eyeball goes where it matters. Pure stdlib.

    python3 draft_air.py --csv <project>/master.csv --dry-run
    python3 draft_air.py --csv <project>/master.csv
    python3 draft_air.py --csv <project>/master.csv --start 0.8 --end 0.2
"""
import argparse, csv, re, shutil, time
from pathlib import Path

KLING_COST = 0.42

# ---- MOTION-WANT vocabulary -------------------------------------------------------
WATER = re.compile(r"\b(water|sea|seas|ocean|oceanic|deep|depths|surf|wave|waves|swell|tide|"
                   r"current|currents|flood|floodwater|river|stream|torrent|spray|foam|froth|"
                   r"spume|bubbles?|submerged|underwater|sinking|sunken|drown\w*|kelp|shoal|"
                   r"fathomless|meltwater|rain|downpour)\b", re.I)
AIRMATTER = re.compile(r"\b(dust|smoke|mist|cloud|clouds|ash|steam|vapou?r|haze|sand|snow|"
                       r"embers?|sparks?|debris|particles?)\b", re.I)
CLOTH = re.compile(r"\b(cloth|robe|robes|drapery|draped|cloak|banner|sail|veil|hair|"
                   r"wind-swept|windswept|billow\w*|fluttering)\b", re.I)
FIRE = re.compile(r"\b(fire|flame|flames|firelight|burning|blaz\w*|forge-fire|inferno)\b", re.I)
MOVEVERB = re.compile(r"\b(rising|ris(?:e|es)|descend\w*|falling|fall|pouring|streaming|surging|"
                      r"billowing|swirl\w*|churn\w*|spreading|collapsing|erupt\w*|flowing|"
                      r"drift(?:ing)?|receding|crashing|breaking|plunging|hauling|turning|"
                      r"sinking|moving|striding|fleeing|wheeling|advancing|gathering|"
                      r"cascad\w*|rolling|sweeping|climbing|soar\w*)\b", re.I)
LIVING = re.compile(r"\b(figures?|people|men|women|crowd|army|warriors?|birds?|fish|creature|"
                    r"herd|sailors?|divers?|fisherman|fishermen)\b", re.I)
# things that are genuinely inert -- a slow push is the RIGHT language for these
STATIC = re.compile(r"\b(carved|carving|relief|inscription|inscribed|engrav\w*|tablet|"
                    r"bas-relief|stonework|page|pages|book|text|ink|inked|manuscript|"
                    r"vase-painting|scroll|grain|weathered)\b", re.I)
HELD = re.compile(r"\b(still|stillness|motionless|held|frozen|perfectly still|unbroken|calm)\b", re.I)


def motion_want(phenom: str, register: str) -> int:
    """How badly the picked frame wants to move. Higher = animate first."""
    p = phenom or ""
    s = 0
    if WATER.search(p):     s += 3
    if AIRMATTER.search(p): s += 2
    if CLOTH.search(p):     s += 2
    if FIRE.search(p):      s += 2
    if MOVEVERB.search(p):  s += 2
    if LIVING.search(p):    s += 1
    if STATIC.search(p):    s -= 3
    if HELD.search(p):      s -= 2
    return s


def draft_motion(phenom: str, move: str) -> str:
    """Kling prompt: doctrine camera (from the already-drafted `move`) + what actually moves."""
    p = phenom or ""
    m = (move or "push").strip().lower()
    camera = {"crane": "slow crane up", "pull": "slow pull-back",
              "settle": "near-locked, slow settle", "static": "locked camera",
              "push": "slow push-in"}.get(m, "slow push-in")
    if WATER.search(p):
        matter = "water and suspended particles drifting"
    elif FIRE.search(p):
        matter = "flame and embers rising"
    elif AIRMATTER.search(p):
        matter = "dust and haze drifting"
    elif CLOTH.search(p):
        matter = "cloth and hair moving in wind"
    else:
        matter = "subtle ambient drift only"
    return "%s, %s, subject locked, no other movement" % (camera, matter)


def main():
    ap = argparse.ArgumentParser(description="Draft air+motion: sliding Kling quota, ranked by motion-want.")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--start", type=float, default=0.80, help="Kling fraction in block 1 (default 0.80)")
    ap.add_argument("--end", type=float, default=0.20, help="Kling fraction in the last block (default 0.20)")
    ap.add_argument("--score-floor", type=int, default=4,
                    help="motion-want score at/above which a beat animates in ANY block, "
                         "on top of the quota (default 4; 99 disables)")
    ap.add_argument("--redraft", action="store_true", help="overwrite existing air/motion")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    a = ap.parse_args()

    path = Path(a.csv).expanduser()
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit("CSV has no rows.")
    fields = list(rows[0].keys())
    for col in ("air", "motion"):
        if col not in fields:
            fields.append(col)
    for r in rows:
        r.setdefault("air", "")
        r.setdefault("motion", "")

    blocks = sorted({int(r["block_id"]) for r in rows})
    nb = len(blocks)
    chosen = set()
    report = []
    for bi, b in enumerate(blocks):
        frac = a.start if nb == 1 else a.start + (a.end - a.start) * (bi / (nb - 1))
        brows = [r for r in rows if int(r["block_id"]) == b]
        quota = int(round(frac * len(brows)))
        scored = sorted(
            brows,
            key=lambda r: (-motion_want(r["phenomenon"], r.get("register", "")),
                           0 if r.get("weight") == "hero" else 1,
                           int(r["clip_index"])))
        take = scored[:quota]
        rescued = [r for r in scored[quota:]
                   if motion_want(r["phenomenon"], r.get("register", "")) >= a.score_floor]
        for r in take + rescued:
            chosen.add((int(r["block_id"]), int(r["clip_index"])))
        report.append((b, frac, len(brows), quota, scored, take, rescued))

    kept_edits = 0
    for r in rows:
        key = (int(r["block_id"]), int(r["clip_index"]))
        if (r.get("air") or "").strip() and not a.redraft:
            kept_edits += 1
            continue
        if key in chosen:
            r["air"] = "kling"
            r["motion"] = draft_motion(r["phenomenon"], r.get("move", ""))
        else:
            r["air"] = "kb"
            r["motion"] = ""

    kling = [r for r in rows if (r.get("air") or "").strip().lower() == "kling"]
    n_quota = sum(len(x[6 - 1]) for x in report)          # take
    n_resc = sum(len(x[6]) for x in report)               # rescued
    print("blocks %d | quota %.0f%% -> %.0f%% | floor >=%d"
          % (nb, a.start * 100, a.end * 100, a.score_floor))
    print("  Kling %d = %d quota + %d floor-rescued  ($%.2f) | Ken Burns %d ($0)"
          % (len(kling), n_quota, n_resc, len(kling) * KLING_COST, len(rows) - len(kling)))
    if kept_edits:
        print("  preserved %d row(s) with an existing `air` (use --redraft to overwrite)" % kept_edits)
    print("  Kling by block: " + ", ".join(
        "b%d:%d" % (b, sum(1 for r in kling if int(r["block_id"]) == b)) for b in blocks))

    if a.dry_run:
        print("\n  per-block detail (score in brackets; BORDERLINE = last taken vs first left):")
        for b, frac, n, quota, scored, take, rescued in report:
            print("\n  --- block %d: %.0f%% of %d = %d quota + %d rescued = %d Kling ---"
                  % (b, frac * 100, n, quota, len(rescued), quota + len(rescued)))
            for r in rescued[:4]:
                print("     RESCUE[%2d] %s/%-2s %s" % (motion_want(r["phenomenon"], ""), b,
                                                       r["clip_index"], r["phenomenon"][:64]))
            for r in take[:3]:
                print("     take  [%2d] %s/%-2s %s" % (motion_want(r["phenomenon"], ""), b,
                                                       r["clip_index"], r["phenomenon"][:66]))
            if quota and quota <= len(scored):
                lo = scored[quota - 1]
                print("     ..... [%2d] %s/%-2s %s   <- LAST TAKEN"
                      % (motion_want(lo["phenomenon"], ""), b, lo["clip_index"], lo["phenomenon"][:60]))
            left = [r for r in scored[quota:] if r not in rescued]
            if left:
                hi = left[0]
                print("     ..... [%2d] %s/%-2s %s   <- FIRST LEFT"
                      % (motion_want(hi["phenomenon"], ""), b, hi["clip_index"], hi["phenomenon"][:60]))
        print("\ndry-run: nothing written.")
        return

    bak = path.with_suffix(path.suffix + ".pre_" + time.strftime("%Y%m%d-%H%M%S"))
    shutil.copyfile(path, bak)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("  wrote %s (backup %s)" % (path, bak.name))
    print("  NEXT: render_clips.py --dry-run to confirm the split, then render.")


if __name__ == "__main__":
    main()
