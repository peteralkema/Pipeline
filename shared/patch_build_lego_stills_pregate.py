#!/usr/bin/env python3
"""patch_build_lego_stills_pregate.py  --  make a full-grid run safe to leave unattended.

Three changes to cmd_stills in build_lego.py:
  1. PRE-GATE every wanted block BEFORE rendering any of them. Today the gate runs
     just-in-time inside the render loop, so a banned word in block 6 only aborts
     after blocks 1-5 have spent (~$43 on WITW, 21 Jul) -- the run has to be watched.
     All inputs exist up front; validate the whole film, report EVERY failure at once,
     spend nothing. The run now either refuses at second zero or runs to completion.
  2. Flag sub-8KB frames at the end -- fal safety rejects write ~7KB black PNG
     placeholders and do NOT raise, so they silently reach the pick.
  3. Print a completion summary (blocks, real stills, cost) so an unattended run can
     be told "finished" from "died" at a glance.

Anchor-verified, idempotent, .pre_ backup, py_compile before write, ASCII-only.
LAPTOP edit -> commit -> push -> box pull (NOT during a render).

    cd ~/Projects/Pipeline
    python3 shared/patch_build_lego_stills_pregate.py
"""
import argparse, os, sys, py_compile, tempfile

OLD = '    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})\n    for block in wanted:\n        brows = [r for r in rows if int(r["block_id"]) == block]\n        gerrs = gate_block(brows, cfg, load_banned(cfg))\n        if gerrs:\n            print("\\n".join("  GATE FAIL: " + e for e in gerrs)); raise SystemExit(1)\n        grid = proj / ("grid-b%02d" % block)\n        real, index = _stills_render(cfg, brows, grid, False, "block %d" % block)\n        _write_grid_index(grid, index)\n        print("  block %d: grid -> %s | %d real stills ($%.2f) | GRID-INDEX.csv" % (block, grid, real, real * 0.08))\n    print("\\nNEXT: review each grid folder, promote ONE winner per beat to shot_NNN.png (the pick).")'
NEW = '    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})\n    # PRE-GATE THE WHOLE FILM BEFORE ANY SPEND. Gating just-in-time inside the render\n    # loop means a bad beat in block 6 only surfaces after blocks 1-5 have spent -- so\n    # the run cannot be left unattended. Every input needed to validate all N blocks\n    # exists before the first fal call: validate them all, report every failure at once,\n    # spend nothing. An unattended run now either refuses at second zero or completes.\n    banned = load_banned(cfg)\n    pregate = []\n    for block in wanted:\n        brows = [r for r in rows if int(r["block_id"]) == block]\n        for e in gate_block(brows, cfg, banned):\n            pregate.append("block %d: %s" % (block, e))\n    if pregate:\n        print("GATE FAIL -- %d issue(s) across %d block(s). NOTHING RENDERED, $0 spent:"\n              % (len(pregate), len(wanted)))\n        print("\\n".join("  " + e for e in pregate))\n        raise SystemExit(1)\n    print("pre-gate OK: %d block(s) clean -- rendering." % len(wanted))\n\n    total_real = 0\n    checked = []\n    for block in wanted:\n        brows = [r for r in rows if int(r["block_id"]) == block]\n        grid = proj / ("grid-b%02d" % block)\n        real, index = _stills_render(cfg, brows, grid, False, "block %d" % block)\n        _write_grid_index(grid, index)\n        total_real += real\n        for row in index:\n            if row[3] == "real":\n                checked.append(grid / row[4])\n        print("  block %d: grid -> %s | %d real stills ($%.2f) | GRID-INDEX.csv" % (block, grid, real, real * 0.08))\n\n    # fal safety rejects land as ~7KB black placeholders and do NOT raise -- surface them\n    rejects = []\n    for f in checked:\n        try:\n            if f.exists() and f.stat().st_size < 8192:\n                rejects.append(f)\n        except OSError:\n            pass\n    print("\\nDONE: %d block(s) | %d real stills ($%.2f)" % (len(wanted), total_real, total_real * 0.08))\n    if rejects:\n        print("WARNING: %d frame(s) under 8KB -- likely fal safety rejects (black placeholders):" % len(rejects))\n        for f in rejects[:20]:\n            print("  %s" % f)\n        if len(rejects) > 20:\n            print("  ... and %d more" % (len(rejects) - 20))\n        print("  check safety_tolerance, DELETE the listed files, then re-run (resume-safe refill).")\n    print("\\nNEXT: review each grid folder, promote ONE winner per beat to shot_NNN.png (the pick).")'
MARKER = "PRE-GATE THE WHOLE FILM BEFORE ANY SPEND"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=None)
    a = ap.parse_args()
    if a.target:
        target = os.path.abspath(a.target)
    else:
        d = os.path.abspath(os.getcwd()); root = None
        while d != os.path.dirname(d):
            if os.path.isdir(os.path.join(d, ".git")): root = d; break
            d = os.path.dirname(d)
        if not root:
            sys.stderr.write("ERROR: no .git found; pass --target\n"); sys.exit(1)
        target = os.path.join(root, "build_lego.py")
    if not os.path.isfile(target):
        sys.stderr.write("ERROR: not found: %s\n" % target); sys.exit(1)

    src = open(target, encoding="utf-8").read()
    if MARKER in src:
        print("skip (already applied): stills pre-gate"); return
    if OLD not in src:
        sys.stderr.write("ERROR: cmd_stills block-loop anchor not found -- ABORT (no write).\n"
                         "Expected the canonical loop installed by patch_build_lego_probe_verb.py.\n")
        sys.exit(1)
    if src.count(OLD) != 1:
        sys.stderr.write("ERROR: anchor matches %d times (need 1) -- ABORT.\n" % src.count(OLD)); sys.exit(1)

    out = src.replace(OLD, NEW, 1)
    if any(ord(c) > 127 for c in NEW):
        sys.stderr.write("ERROR: non-ASCII in replacement\n"); sys.exit(1)

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(out); tmp.close()
    try:
        py_compile.compile(tmp.name, doraise=True)
    except py_compile.PyCompileError as e:
        sys.stderr.write("ERROR: patched source fails to compile -- ABORT:\n%s\n" % e)
        os.unlink(tmp.name); sys.exit(1)
    os.unlink(tmp.name)

    bak = target + ".pre_pregate"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(src); print("backup:", bak)
    open(target, "w", encoding="utf-8").write(out)
    print("OK: cmd_stills now pre-gates the whole film, flags black rejects, prints a summary.")


if __name__ == "__main__":
    main()
