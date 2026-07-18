#!/usr/bin/env python3
"""
patch_grid_cmd.py -- add the `grid` command to build_moon.py.

`grid` emits the WHOLE film as one beats.json for the variant-grid render: every
beat carries its `variants` count (4 hero / 2 connective) so render_grid.py knows
how many real re-rolls to fal per beat and how many _skip.png tiles to fill. Also
writes GRID-INDEX.csv mapping the padded beat number (001..320) back to
block/clip/weight/narration, for manual review of the dumped folder.

Idempotent, anchor-verified, .pre_<ts> backup, py_compile, ASCII. Run from the
enoch-moon project dir.
"""
import time
from pathlib import Path

TARGET = Path("build_moon.py")
MARKER = "def cmd_grid(argv):"

FUNC = '''def cmd_grid(argv):
    """$0. Emit the whole film as ONE beats.json for the variant grid, plus a
    review index. Each beat carries its `variants` count (4 hero / 2 connective);
    render_grid.py renders that many real re-rolls and _skip.png-fills to 4.
    Beat number is the 1-based row position (001..N), matching GRID-INDEX.csv."""
    ce = gate_canon()
    if ce:
        print("\\n".join("  CANON FAIL: " + e for e in ce)); raise SystemExit(1)
    rows = load_master()
    beats = []
    for i, r in enumerate(rows, 1):
        check_tokens(r["phenomenon"], f"grid beat {i} (b{r['block_id']}/{r['clip_index']})")
        beats.append({
            "narration": r["narration"],
            "image_prompt": r["phenomenon"],
            "variants": int(r["variants"]),
        })
    out = HERE.parent / "moon-grid-finish"
    out.mkdir(exist_ok=True)
    (out / "beats.json").write_text(
        json.dumps({"canon": CANON, "beats": beats}, indent=2, ensure_ascii=False))
    real = sum(int(r["variants"]) for r in rows)
    total = len(rows) * 4
    idx = HERE / "GRID-INDEX.csv"
    with idx.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["beat", "block", "clip", "weight", "variants", "narration"])
        for i, r in enumerate(rows, 1):
            w.writerow([f"{i:03d}", r["block_id"], r["clip_index"],
                        r["weight"], r["variants"], r["narration"]])
    print(f"  grid: {len(beats)} beats -> {out}/beats.json")
    print(f"  {real} real stills + {total - real} skip tiles = {total} files | ${real * 0.08:.2f}")
    print(f"  review index -> {idx}")


'''

ANCHOR_FUNC = "def cmd_probe(slots=PROBE, out_name=\"moon-probe-finish\", card_name=\"PROBE-CARD.md\"):\n"
ANCHOR_DISPATCH = '    if cmd == "blocks": cmd_blocks(rest)\n'
DISPATCH_LINE = '    elif cmd == "grid": cmd_grid(rest)\n'


def die(msg):
    print("PATCH ABORTED: " + msg)
    raise SystemExit(1)


def main():
    if not TARGET.exists():
        die("build_moon.py not found. Run from the enoch-moon project dir.")
    src = TARGET.read_text()
    if MARKER in src:
        print("Already applied (cmd_grid present). No change.")
        return
    for name, anchor in (("func", ANCHOR_FUNC), ("dispatch", ANCHOR_DISPATCH)):
        if src.count(anchor) != 1:
            die("anchor '%s' found %d times, expected 1." % (name, src.count(anchor)))

    new = src.replace(ANCHOR_FUNC, FUNC + ANCHOR_FUNC, 1)
    new = new.replace(ANCHOR_DISPATCH, ANCHOR_DISPATCH + DISPATCH_LINE, 1)

    if not new.isascii():
        die("result contains non-ASCII bytes.")
    try:
        compile(new, str(TARGET), "exec")
    except SyntaxError as e:
        die("compile check failed: %s" % e)

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_%s" % ts)
    backup.write_text(src)
    TARGET.write_text(new)
    print("Patched build_moon.py")
    print("  backup: %s" % backup.name)
    print("  added: cmd_grid(), dispatch 'grid'")
    print("  run:   python3 build_moon.py grid")


if __name__ == "__main__":
    main()
