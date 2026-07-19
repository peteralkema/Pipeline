#!/usr/bin/env python3
"""
patch_fill_moves.py -- draft the `move` column render_clips.py reads.

Derives a doctrine move per beat (motion doctrine applied to Ken Burns):
  quiet override:  eerie stillness / bare / empty  -> static
                   reflection / aftermath / grief   -> settle
  vertical phenomenon (rising/column/tower/ascend)  -> crane
  scale / number (ranked / limb to limb / rows)     -> pull
  else (one overwhelming subject; the default)      -> push

It's a DRAFT -- rotate variety in, then correct the misses against the picked frames
(the move is ultimately a per-frame judgment). Writes explicit values; by default
fills only blank `move` cells (idempotent, preserves your edits). --redraft overwrites.
--dry-run reports the distribution, writes nothing.

Run on the LAPTOP:  python3 patch_fill_moves.py --csv beats/master.csv
"""
import argparse, csv, re, time
from pathlib import Path

STATIC = re.compile(r"\b(empty|bare|unbuilt|nothing|deserted|abandoned|silent|silence|"
                    r"unlit|lifeless|motionless|frozen|still|dead)\b", re.I)
SETTLE = re.compile(r"\b(aftermath|dawn|dusk|rest|resting|reflect\w*|grief|mourn\w*|"
                    r"settl\w*|recover\w*|calm|peace\w*|blessing|quiet|elegy|lament)\b", re.I)
VERTICAL = re.compile(r"\b(ris(?:e|es|ing)|column|columns|tower(?:ing)?|ascend\w*|upward|"
                      r"up out|pillar|standing up|soars?|erupt\w*|climb\w*|rear\w* up|"
                      r"streaming up|lifting)\b", re.I)
SCALE = re.compile(r"\b(ranked|rank of|row of|rows|limb to limb|entire curve|whole curve|"
                   r"far beyond|thousands|hundreds|receding|to the horizon|countable|"
                   r"stretch\w*|endless|vast expanse)\b", re.I)


def draft_move(phenom, register):
    p, r = phenom.lower(), (register or "").lower()
    if STATIC.search(r) or STATIC.search(p):
        return "static"
    if SETTLE.search(r) or SETTLE.search(p):
        return "settle"
    if VERTICAL.search(p):
        return "crane"
    if SCALE.search(p):
        return "pull"
    return "push"


def main():
    ap = argparse.ArgumentParser(description="Draft the doctrine `move` column.")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--redraft", action="store_true", help="overwrite existing move values")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    path = Path(args.csv).expanduser()
    if not path.is_file():
        raise SystemExit(f"CSV not found: {path}")
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0].keys())
    if "move" not in fields:
        fields.append("move")
        for r in rows:
            r.setdefault("move", "")

    drafted = 0
    for r in rows:
        if (r.get("move") or "").strip() and not args.redraft:
            continue
        r["move"] = draft_move(r.get("phenomenon", ""), r.get("register", ""))
        drafted += 1

    hist = {}
    for r in rows:
        hist[r["move"]] = hist.get(r["move"], 0) + 1
    print(f"drafted {drafted} rows | moves: " +
          ", ".join(f"{m}:{hist.get(m,0)}" for m in ("push", "pull", "crane", "settle", "static")))
    if args.dry_run:
        print("dry-run: nothing written.")
        return

    ts = time.strftime("%Y%m%d-%H%M%S")
    path.with_suffix(path.suffix + ".pre_%s" % ts).write_text(path.read_text())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path} (backup .pre_{ts})")
    print("  correct the misses, then render_clips.py --floor-only --dry-run to confirm the mix.")


if __name__ == "__main__":
    main()
