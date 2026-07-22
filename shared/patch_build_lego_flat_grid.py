#!/usr/bin/env python3
"""patch_build_lego_flat_grid.py  --  one flat grid folder, place.py-compatible names.

The pick reviews EVERY still in ONE folder, and place.py parses
  ^(\\d{1,4})-(\\d+)\\.png$  where group 1 is the FLAT FILM INDEX (1..N)
-- the same number render_clips.py uses for shot_{i:03d} (it enumerates CSV rows).
Per-block names ({clip}-{variant}.png) repeat across blocks and collide the moment
they share a folder; a block-prefixed name (06-019-03.png) fails place.py regex.
Flat index satisfies both: globally unique AND place-compatible.

Changes to build_lego.py:
  * new _flat_map(rows) -- (block, clip) -> CSV row order (NOT (block-1)*40+clip)
  * _stills_render takes flat_map instead of prefix_block; names {flat:03d}-{v:02d}.png
  * block mode renders into ONE <project>/grid/ folder (was grid-bNN/ per block)
  * probe keeps its own folder, now with the same flat names

Existing per-block grids are migrated separately by consolidate_grid.py.
Anchor-verified per edit, idempotent, .pre_ backup, py_compile, ASCII-only.

    cd ~/Projects/Pipeline && python3 shared/patch_build_lego_flat_grid.py
"""
import argparse, os, sys, py_compile, tempfile

EDITS = [
    ('sig', 'def _stills_render(cfg, brows, out_dir, prefix_block, label):', 'def _flat_map(rows):\n    """(block, clip) -> FLAT FILM INDEX (CSV row order, 1-based).\n\n    Flat index is row ORDER, never (block-1)*40+clip: the formula only agrees when\n    every block holds exactly 40 rows, and a short block would silently misalign every\n    beat after it. This is the number place.py parses out of {flat}-{variant}.png and\n    the number render_clips.py uses for shot_{i:03d}.\n    """\n    return {(int(r["block_id"]), int(r["clip_index"])): i for i, r in enumerate(rows, 1)}\n\n\ndef _stills_render(cfg, brows, out_dir, flat_map, label):', 'def _flat_map(rows):'),
    ('name', '            name = ("%02d-%03d-%02d.png" % (b, ci, v)) if prefix_block else ("%03d-%02d.png" % (ci, v))', '            name = "%03d-%02d.png" % (flat_map[(b, ci)], v)', 'name = "%03d-%02d.png" % (flat_map[(b, ci)], v)'),
    ('build', '    proj = Path(cfg["_project_dir"])\n    beats = None', '    proj = Path(cfg["_project_dir"])\n    flat_map = _flat_map(rows)\n    beats = None', 'flat_map = _flat_map(rows)\n    beats = None'),
    ('probecall', '        real, index = _stills_render(cfg, brows, proj / "grid-probe", True, "probe")', '        real, index = _stills_render(cfg, brows, proj / "grid-probe", flat_map, "probe")', '_stills_render(cfg, brows, proj / "grid-probe", flat_map, "probe")'),
    ('griddir', '        grid = proj / ("grid-b%02d" % block)', '        grid = proj / "grid"', 'grid = proj / "grid"'),
    ('blockcall', '        real, index = _stills_render(cfg, brows, grid, False, "block %d" % block)', '        real, index = _stills_render(cfg, brows, grid, flat_map, "block %d" % block)', '_stills_render(cfg, brows, grid, flat_map, "block %d" % block)'),
    ('cmdprobe', '    real, index = _stills_render(cfg, picks, proj / "grid-probe", True, "probe")', '    real, index = _stills_render(cfg, picks, proj / "grid-probe", _flat_map(rows), "probe")', '_stills_render(cfg, picks, proj / "grid-probe", _flat_map(rows), "probe")'),
]


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
    orig = src
    for tag, old, new, marker in EDITS:
        if marker in src:
            print("skip (already applied): %s" % tag); continue
        if old not in src:
            sys.stderr.write("ERROR: anchor not found for %r -- ABORT (no write).\n"
                             "Expected the canonical cmd_stills from patch_build_lego_probe_verb.py.\n" % tag)
            sys.exit(1)
        if src.count(old) != 1:
            sys.stderr.write("ERROR: anchor %r matches %d times (need 1) -- ABORT.\n" % (tag, src.count(old)))
            sys.exit(1)
        src = src.replace(old, new, 1)
        print("applied: %s" % tag)

    if src == orig:
        print("no changes."); return

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(src); tmp.close()
    try:
        py_compile.compile(tmp.name, doraise=True)
    except py_compile.PyCompileError as e:
        sys.stderr.write("ERROR: patched source fails to compile -- ABORT:\n%s\n" % e)
        os.unlink(tmp.name); sys.exit(1)
    os.unlink(tmp.name)

    bak = target + ".pre_flatgrid"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(orig); print("backup:", bak)
    open(target, "w", encoding="utf-8").write(src)
    print("OK: stills now render into ONE flat-named grid folder (place.py-compatible).")


if __name__ == "__main__":
    main()
