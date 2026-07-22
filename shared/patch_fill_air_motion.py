#!/usr/bin/env python3
"""
patch_fill_air_motion.py -- draft the `air` and `motion` columns render_clips.py reads.

FRONT-LOADED policy: a beat with visible air becomes Kling if it is in an EARLY block
(<= --front-blocks, default 3); in later blocks only STRONG air (streaming/torrent/
driven/pouring) earns Kling -- everything else rides the free Ken Burns floor. This
animates the gate without paying to animate dust deep in the film.

Writes EXPLICIT values so re-runs never clobber your corrections:
  air = "kling"  -> Kling      (render_clips treats this as animate)
  air = "kb"     -> Ken Burns  (explicit floor; NOT in render_clips' truthy set)
  air = ""       -> not yet drafted
`motion` is drafted only on Kling beats (doctrine move by cue); Ken Burns beats stay blank.

By default fills only rows whose `air` is still blank (idempotent, preserves your edits).
--redraft overwrites all. --dry-run reports the split + cost, writes nothing.

Run on the LAPTOP against the master:  python3 patch_fill_air_motion.py --csv beats/master.csv
"""
import argparse, csv, re, time
from pathlib import Path

AIR_NOUN = re.compile(r"\b(dust|smoke|mist|clouds?|wind|spray|embers?|ash|steam|vapou?r|haze|"
                      r"sand|spume|froth|drift(?:ing)?|snow)\b", re.I)
STRONG = re.compile(r"\b(stream(?:ing|ed)?|torrents?|pour(?:ing|ed)?|driven|roaring|blasting|"
                    r"surging|billowing|blowing|hurled|erupting|gushing|cascad\w*|lifting off|"
                    r"torn off|trailing)\b", re.I)
VERTICAL = re.compile(r"\b(ris(?:e|es|ing)|column|columns|tower(?:ing)?|ascend\w*|upward|up out|"
                      r"pillar|standing up|soars?|erupt\w*|climb\w*)\b", re.I)
SCALE = re.compile(r"\b(ranked|rank of|limb to limb|entire curve|whole curve|rows?|far beyond|"
                   r"thousands|hundreds of miles|receding|to the horizon|countable|stretch\w*)\b", re.I)
QUIET = re.compile(r"\b(grief|mourn\w*|aftermath|silence|silent|empty|unlit|dark|shadow|dead|still)\b", re.I)


def draft_motion(phenom, register):
    if VERTICAL.search(phenom):
        return "slow crane up, subject locked"
    if QUIET.search(register) or QUIET.search(phenom):
        return "near-locked, ambient drift only"
    if SCALE.search(phenom):
        return "slow pull-back, subject locked"
    return "slow push-in, subject locked"


def main():
    ap = argparse.ArgumentParser(description="Draft air + motion (front-loaded Kling).")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--front-blocks", type=int, default=3,
                    help="blocks <= this get Kling on ANY air; later blocks need STRONG air")
    ap.add_argument("--redraft", action="store_true", help="overwrite existing air/motion")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    path = Path(args.csv).expanduser()
    if not path.is_file():
        raise SystemExit(f"CSV not found: {path}")
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0].keys())
    for col in ("air", "motion"):
        if col not in fields:
            fields.append(col)
            for r in rows:
                r.setdefault(col, "")

    drafted = 0
    per_block_kling = {}
    for r in rows:
        if (r.get("air") or "").strip() and not args.redraft:
            if r["air"].strip().lower() == "kling":
                per_block_kling[r["block_id"]] = per_block_kling.get(r["block_id"], 0) + 1
            continue
        phenom = r.get("phenomenon", "")
        block = int(r["block_id"])
        has_air = bool(AIR_NOUN.search(phenom))
        strong = has_air and bool(STRONG.search(phenom))
        kling = has_air and (block <= args.front_blocks or strong)
        r["air"] = "kling" if kling else "kb"
        r["motion"] = draft_motion(phenom, r.get("register", "")) if kling else ""
        drafted += 1
        if kling:
            per_block_kling[r["block_id"]] = per_block_kling.get(r["block_id"], 0) + 1

    kling_total = sum(1 for r in rows if r["air"].strip().lower() == "kling")
    print(f"drafted {drafted} rows | Kling {kling_total} (${kling_total*0.42:.2f}) | "
          f"Ken Burns {len(rows)-kling_total} ($0)")
    print("  Kling by block: " + ", ".join(f"b{b}:{per_block_kling.get(b,0)}"
                                            for b in sorted(per_block_kling, key=int)))
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
    print("  CORRECT the misses, then: render_clips.py --dry-run to confirm the split before spend.")


if __name__ == "__main__":
    main()
