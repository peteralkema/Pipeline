#!/usr/bin/env python3
"""patch_lego_flat_grid_doc.py  --  document the one-folder / flat-index still naming.

Six edits to shared/docs/_LEGO.md so no stale layout survives anywhere:
  1. PATHS block         -- grid/ + winners/ with flat names
  2. CSV invariants      -- the flat film index is the one number in the visual chain
  3. The variant grid    -- ONE GRID FOLDER, FLAT-INDEX FILENAMES (the why, 3 reasons)
  4. The pick            -- review one folder in beat order; winners/ -> place.py
  5. COMMAND CONTRACT    -- stills renders into grid/, probe uses the same names
  6. CHANGELOG           -- records what was retired and why

Anchor-verified per edit, idempotent, .pre_ backup. Writes unicode (em-dashes, stars)
because _LEGO.md uses them as house style; the ASCII-only rule is for CODE patches.

    cd ~/Projects/Pipeline && python3 shared/patch_lego_flat_grid_doc.py
"""
import argparse, os, sys

EDITS = [
    ('PATHS', 'grid stills:   <channel>/projects/<slug>/grid-b<NN>/{clip:03d}-{variant:02d}.png\nprobe stills:  <channel>/projects/<slug>/grid-probe/{block:02d}-{clip:03d}-{variant:02d}.png\nplaced stills: <channel>/projects/<slug>/stills/shot_NNN.png', 'grid stills:   <channel>/projects/<slug>/grid/{flat:03d}-{variant:02d}.png   <- ALL beats, ONE folder\nprobe stills:  <channel>/projects/<slug>/grid-probe/{flat:03d}-{variant:02d}.png\nwinners:       <channel>/projects/<slug>/winners/{flat:03d}-{variant:02d}.png (the picks, names unchanged)\nplaced stills: <channel>/projects/<slug>/stills/shot_NNN.png', 'ALL beats, ONE folder'),
    ('INVARIANT', "  chosen file to `shot_NNN.png`; that file's existence IS the pick. There is no\n  `picked_variant` column to keep in sync.", "  chosen file to `shot_NNN.png`; that file's existence IS the pick. There is no\n  `picked_variant` column to keep in sync.\n- **One number runs the whole visual chain: the FLAT FILM INDEX (CSV row order, 1..N).** Grid\n  and probe stills are named `{flat}-{variant}.png`, `place.py` parses that flat beat out of the\n  filename, and `render_clips.py` enumerates the same rows for `shot_{i:03d}`. Never name a\n  still by `clip_index` (it repeats in every block) and never block-prefix it (`place.py`'s\n  regex rejects a second dash).", 'One number runs the whole visual chain'),
    ('GRIDNAMING', '(`sum(variants) × $0.08`), visible before you spend. Per-block grid folders are `grid-b<NN>/`,\nfilenames `{clip:03d}-{variant:02d}.png` (clip-only — unique within a block). Probe folders are\n`grid-probe/`, filenames block-PREFIXED `{block:02d}-{clip:03d}-{variant:02d}.png` (clip_index\nrepeats across blocks and would otherwise collide).', '(`sum(variants) × $0.08`), visible before you spend.\n\n> **★ ONE GRID FOLDER, FLAT-INDEX FILENAMES.** Every still of the film lands in a single\n> `grid/` folder named `{flat:03d}-{variant:02d}.png`, where **flat is the FILM INDEX 1..N**.\n> The folder therefore sorts in exact beat order — you scroll the film start to finish. The\n> probe folder uses the same names. Three reasons this is the ONE naming law:\n> - **Unique by construction.** `{clip}-{variant}` repeats in every block, so the winners\n>   collide the moment they share a folder — a silent overwrite that loses most of the picks.\n> - **`place.py`-compatible.** It parses `^(\\d{1,4})-(\\d+)\\.png$` and reads group 1 as the flat\n>   beat; a block-prefixed name (`06-019-03.png`) fails that regex outright.\n> - **Agrees with `render_clips.py`**, which enumerates CSV rows for `shot_{i:03d}`.\n>\n> **FLAT IS CSV ROW ORDER, never `(block−1)×40+clip`.** The formula agrees only while every\n> block holds exactly 40 rows; one short block would silently misalign every beat after it —\n> which you would meet as narration over the wrong image at assembly. `_flat_map()` reads the\n> master and enumerates. `consolidate_grid.py` migrates an older per-block layout (`grid-bNN/`)\n> into the flat folder — a rename, no re-render, dry-run by default.', 'ONE GRID FOLDER, FLAT-INDEX FILENAMES'),
    ('PICK', '100 stills/block → 40 winners. **The pick will never be automated — it is the creative act,\nand the real ceiling on how many shots you take.** `place.py` promotes the chosen file to\n`shot_NNN.png`; hard-fails on a skip-tile pick, gap, or dupe. **Block-at-a-time is a PICK rule\n(visual fatigue over ~800 stills), not a text rule** — enrichment is whole-film in one pass;\nthe pick is one block per sitting.', '~4 stills per beat → ONE winner each (≈1,280 → 320 on an 8-block film). **The pick will never be\nautomated — it is the creative act, and the real ceiling on how many shots you take.**\n\nReview the whole `grid/` folder sorted by name: flat-index names put it in exact beat order, so\nyou scroll the film in sequence and stop wherever. Copy ONE winner per beat into `winners/`\n(filenames unchanged — they are already unique), then place them:\n\n    python3 place.py --winners <project>/winners --out <project>/stills \\\n                     --skip-tile shared/_skip.png\n\n`place.py` parses the flat beat from each filename and writes `shot_{beat:03d}.png`. It\nhard-fails — placing NOTHING — on a skip-tile pick, a doubled beat, or any gap in 1..N, so it\nnames exactly what to re-pick rather than half-placing. **Pace the pick across sittings (visual\nfatigue over ~1,000 stills is real), but that is a PACING rule, not a folder rule** —\nenrichment is whole-film in one pass, and so is the grid.', '~4 stills per beat'),
    ('CMD', '- **`stills [BLOCK...]`** — whole block(s) → `grid-b<NN>/` (unprefixed filenames; pick/place\n  reads these). **`stills beats=b/c,…`** — a manual cross-film sample → `grid-probe/`\n  (block-prefixed filenames). The per-block structural gate runs on block mode and is skipped', '- **`stills [BLOCK...]`** — whole block(s) → the single `grid/` folder, flat-index filenames.\n  **`stills beats=b/c,…`** — a manual cross-film sample → `grid-probe/` (same flat names).\n  The per-block structural gate runs on block mode and is skipped', 'the single `grid/` folder, flat-index filenames'),
    ('CHANGELOG', '- **The pick is a filename, never a `picked_variant` column** (settled the duplicate beat-table).', "- **The pick is a filename, never a `picked_variant` column** (settled the duplicate beat-table).\n- **One grid folder, flat-index filenames** (21 Jul, after the WITW grid). Per-block folders and\n  `{clip}-{variant}` names are retired: clip index repeats in every block, so flattening the\n  winners collided, and the block-prefix fix used on the probe fails `place.py`'s regex. Flat\n  film index (CSV row order) is unique by construction, `place.py`-compatible, and the same\n  number `render_clips.py` uses — one naming law for probe, grid, winners and clips.\n  `consolidate_grid.py` migrates older films.", 'One grid folder, flat-index filenames'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", default=None)
    a = ap.parse_args()
    if a.doc:
        path = os.path.abspath(a.doc)
    else:
        d = os.path.abspath(os.getcwd()); root = None
        while d != os.path.dirname(d):
            if os.path.isdir(os.path.join(d, ".git")): root = d; break
            d = os.path.dirname(d)
        if not root:
            sys.stderr.write("ERROR: no .git found; pass --doc\n"); sys.exit(1)
        path = os.path.join(root, "shared", "docs", "_LEGO.md")
    if not os.path.isfile(path):
        sys.stderr.write("ERROR: not found: %s\n" % path); sys.exit(1)

    src = open(path, encoding="utf-8").read()
    orig = src
    for tag, old, new, marker in EDITS:
        if marker in src:
            print("skip (already applied): %s" % tag); continue
        if old not in src:
            sys.stderr.write("ERROR: anchor not found for %r -- ABORT (no write).\n" % tag); sys.exit(1)
        if src.count(old) != 1:
            sys.stderr.write("ERROR: anchor %r matches %d times (need 1) -- ABORT.\n" % (tag, src.count(old)))
            sys.exit(1)
        src = src.replace(old, new, 1)
        print("applied: %s" % tag)

    if src == orig:
        print("no changes."); return
    bak = path + ".pre_flatgriddoc"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(orig); print("backup:", bak)
    open(path, "w", encoding="utf-8").write(src)
    print("OK: _LEGO.md now documents the one-folder / flat-index naming law.")


if __name__ == "__main__":
    main()
