#!/usr/bin/env python3
"""
draft_moves.py -- fill the Ken Burns `move` column off phenomenon + register.

The `move` column is the trigger the engine's ken_burns_still(move=...) reads: one of
push | pull | crane | settle | static, per beat. This drafts it with the SAME cue
ladder your patch_fill_air_motion.py uses (VERTICAL/SCALE/QUIET regexes), mapped to a
move value instead of a Kling motion prompt. It is a DRAFT you correct by eye -- the
shipped enoch column proves the rule is phenomenon-driven, and no regex nails 100%.

THE LADDER (first match wins) -- matches _LEGO.md §7's precedence:
  1. grief / reflection / quiet   -> settle   (§7 rule 1: aftermath, never push)
  2. vertical force               -> crane    (§7 rule 2: overrides framing)
  3. scale / wide / how-far       -> pull     (§7: the scale reveal in motion)
  4. everything else              -> push     (§7: one overwhelming subject, default)

`static` is NOT auto-assigned -- §7 says use it sparingly for eerie stillness, and it
is not reliably derivable from text (enoch hand-placed ~1 in 6). Draft, then promote
specific held beats to static by eye. --validate reports where the draft and an
existing column disagree, so you can see the static picks and any missed cues.

MODES
  (default)      fill `move` only where blank (idempotent; preserves your edits)
  --redraft      overwrite every `move`
  --dry-run      print the push/pull/crane/settle spread, write nothing
  --validate     compare the draft to the EXISTING `move` column, print match rate +
                 every disagreement (run this on enoch to measure fidelity), write nothing

  python3 draft_moves.py --csv projects/bw-space/master.csv --dry-run
  python3 draft_moves.py --csv .../enoch-moon/beats/moon_master.csv --validate
"""
import argparse, csv, re, time
from pathlib import Path

# --- cue regexes: lifted verbatim from patch_fill_air_motion.py so the drafts agree ---
VERTICAL = re.compile(r"\b(ris(?:e|es|ing)|column|columns|tower(?:ing)?|ascend\w*|upward|up out|"
                      r"pillar|standing up|soars?|erupt\w*|climb\w*|rising|shaft|plume|"
                      r"crane|lift(?:s|ing)?)\b", re.I)
SCALE = re.compile(r"\b(ranked|rank of|limb to limb|entire curve|whole curve|rows?|far beyond|"
                   r"thousands|hundreds of miles|receding|to the horizon|countable|stretch\w*|"
                   r"vast|endless|expanse|sprawl\w*|from above|overhead|the whole)\b", re.I)
QUIET_PHENOM = re.compile(r"\b(grief|mourn\w*|aftermath|silence|silent|empty|unlit|dark|shadow|"
                          r"dead|still|ash|settl\w*|abandoned|ruin\w*|remains?|alone)\b", re.I)
# registers that mean 'quiet / reflective' -> settle, independent of phenomenon wording
QUIET_REGISTER = {"reflection", "grief", "sorrow", "mourning", "lament", "elegy",
                  "requiem", "melancholy", "loss", "stillness"}

MOVES = ("push", "pull", "crane", "settle", "static")


def draft_move(phenomenon: str, register: str) -> str:
    reg = (register or "").strip().lower()
    ph = phenomenon or ""
    # 1. quiet / aftermath -> settle (first, so a grief beat never falls through to push)
    if reg in QUIET_REGISTER or QUIET_PHENOM.search(ph):
        return "settle"
    # 2. vertical -> crane
    if VERTICAL.search(ph):
        return "crane"
    # 3. scale / wide -> pull
    if SCALE.search(ph):
        return "pull"
    # 4. default
    return "push"


def spread(rows, key):
    from collections import Counter
    c = Counter((r.get(key) or "").strip().lower() or "(blank)" for r in rows)
    return "  ".join(f"{m}:{c.get(m,0)}" for m in MOVES) + \
           (f"  (blank):{c.get('(blank)',0)}" if c.get("(blank)") else "")


def main():
    ap = argparse.ArgumentParser(description="Draft the Ken Burns `move` column (phenomenon+register).")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--redraft", action="store_true", help="overwrite every move (default: blanks only)")
    ap.add_argument("--dry-run", action="store_true", help="print the spread, write nothing")
    ap.add_argument("--validate", action="store_true",
                    help="compare draft vs existing move column; report match rate + disagreements; write nothing")
    args = ap.parse_args()

    path = Path(args.csv).expanduser()
    if not path.is_file():
        raise SystemExit(f"CSV not found: {path}")
    rows = list(csv.DictReader(path.open()))
    if not rows:
        raise SystemExit("CSV has no rows.")
    fields = list(rows[0].keys())
    if "phenomenon" not in fields:
        raise SystemExit("no `phenomenon` column -- the move is derived from it.")
    if "move" not in fields:
        fields.append("move")
        for r in rows:
            r.setdefault("move", "")

    # ---- validate: measure the drafter against the column already on disk ----
    if args.validate:
        have = [r for r in rows if (r.get("move") or "").strip()]
        if not have:
            raise SystemExit("`move` column is empty -- nothing to validate against.")
        hits = 0
        disagree = []
        for r in have:
            pred = draft_move(r.get("phenomenon", ""), r.get("register", ""))
            actual = r["move"].strip().lower()
            if pred == actual:
                hits += 1
            else:
                disagree.append((r.get("clip_index", "?"), r.get("block_id", "?"),
                                 (r.get("register") or "").strip(), actual, pred))
        n = len(have)
        print(f"VALIDATE against {n} beats with a move: {hits}/{n} = {100*hits/n:.0f}% match")
        print(f"  actual spread: {spread(have, 'move')}")
        if disagree:
            print(f"\n  {len(disagree)} disagreements (clip/block  register  actual -> drafted):")
            for ci, bi, reg, act, pred in disagree:
                flag = "  <- static (hand-placed, not derivable)" if act == "static" else ""
                print(f"    {str(ci):>3}/{str(bi):<2}  {reg:<12}  {act:<7} -> {pred:<7}{flag}")
        return

    # ---- draft ----
    drafted = 0
    for r in rows:
        if (r.get("move") or "").strip() and not args.redraft:
            continue
        r["move"] = draft_move(r.get("phenomenon", ""), r.get("register", ""))
        drafted += 1

    print(f"drafted {drafted} move(s) | spread: {spread(rows, 'move')}")
    if args.dry_run:
        print("dry-run: nothing written.")
        return

    ts = time.strftime("%Y%m%d-%H%M%S")
    path.with_suffix(path.suffix + ".pre_%s" % ts).write_text(path.read_text())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path} (backup .pre_{ts})")
    print("  eyeball the settle/static beats, then: render_clips.py --dry-run to see the split.")


if __name__ == "__main__":
    main()
