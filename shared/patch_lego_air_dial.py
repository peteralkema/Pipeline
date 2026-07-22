#!/usr/bin/env python3
"""patch_lego_air_dial.py  --  integrate the air/Kling spend dial and the Step-8 gate.

Nine edits, woven into the existing sections rather than appended:
  1-2  PROCESS steps 7 and 8   -- draft_air in the pick row; verify_clips as the Step-8 gate
  3    Air section             -> "Air + Kling: the spend dial" (quota x rank x floor,
                                  the medium-vocabulary law, the run-breaking principle)
  4    Motion ladder           -- honest: tools derive from TEXT, you correct from IMAGE
  5    Motion front-load       -- CONFLICT FIX: contiguous front-N kling_count is retired
  6    Ken Burns floor         -- the blank-`move` one-frame-clip trap
  7    COMMAND CONTRACT        -- every reader incl. place.py list mode, draft_air, verify_clips
  8    ENGINE FACTS            -- static branch, untrimmed Kling, per-clip fps derivation
  9    WORKFLOW + CHANGELOG    -- verify tools are tracked; record what was retired

Anchor-verified per edit, idempotent, .pre_ backup. Unicode is house style for this doc.

    cd ~/Projects/Pipeline && python3 shared/patch_lego_air_dial.py
"""
import argparse, os, sys

EDITS = [
    ('step7', '| **7** | **PICK + AIR + MOVE + MOTION** — hand-pick ONE variant per beat; `place` the winners into `shot_NNN.png`; assign `air` (Kling vs Ken Burns) and the doctrine `move` off the PICKED frame; write `motion` only on Kling beats. | `place.py`; `draft_moves.py` | place = N files, no gaps/dupes/skip-tiles; a Kling beat with no `motion` aborts | placed stills + routing plan |', '| **7** | **PICK + AIR + MOVE + MOTION** — hand-pick ONE variant per beat into `winners/`; `place` them into `shot_NNN.png`; `draft_moves` fills `move`; `draft_air` fills `air`+`motion` (sliding quota × motion-want rank × score floor); eye-correct both against the picked frames. | `place.py`; `draft_moves.py`; `draft_air.py` | place = N files, no gaps/dupes/skip-tiles; BOTH drafters `--dry-run` first (a move flatline or a wrong Kling split is free to fix, expensive to render); a Kling beat with no `motion` aborts | placed stills + routing plan |', 'draft_air` fills `air`+`motion`'),
    ('step8', '| **8** | **RENDER CLIPS** — per beat: `air`=Kling → `animate_still(motion)`, else → `ken_burns_still(move)` (the doctrine-varied free floor). | `render_clips.py` (`--floor-only`, `--dry-run`) | `--dry-run` shows split + cost before spend | **`clips/shot_NNN.mp4`** (output #1) |', '| **8** | **RENDER CLIPS + GATE THEM** — per beat: `air`=Kling → `animate_still(motion)`, else → `ken_burns_still(move)` (the doctrine-varied free floor). Then ffprobe EVERY output. | `render_clips.py` (`--floor-only`, `--dry-run`); `verify_clips.py` | `--dry-run` shows split + cost before spend; then **`verify_clips.py --expect N --normalise` must PASS — every clip exactly 5.000s** | **`clips/shot_NNN.mp4`** (output #1) |', 'RENDER CLIPS + GATE THEM'),
    ('airdial', "### Air (Step 7) — read off the picked still, not chosen\n\n**Air means literal, visible, suspended matter** — dust, smoke, mist, embers, water, drifting\ncloth. Not pace, not narration pauses. `visible` → **KLING** (a frozen dust shaft reads as\nwrong before you can say why). `flat` → **KEN BURNS** (a page of Ge'ez, an inscription in\nclose-up — a slow push is documentary language and correct). The line: *any beat with visible\nair is dead as a still.*", '### Air + Kling (Step 7) — the spend dial\n\n**Air means literal, visible, suspended matter** — dust, smoke, mist, embers, **water**,\ndrifting cloth. Not pace, not narration pauses. The line: *any beat with visible air is dead as\na still* — a frozen dust shaft or a motionless sea reads as wrong before you can say why. A\ngenuinely flat beat (a page of Ge\'ez, an inscription in close-up) is CORRECT on the free floor;\na slow push is documentary language.\n\n> **★ THE AIR VOCABULARY MUST MATCH THE FILM\'S MEDIUM.** An earlier drafter\'s air nouns were\n> dust / smoke / cloud / ash with **no water at all** — so a deep-sea film scored ZERO from\n> block 4 on, while a distant "bright parting cloud" in an extreme wide scored high. Water, sea,\n> deep, surf, current, bubbles are first-class air. Read the vocabulary against the film you are\n> actually making before trusting any draft.\n\n`draft_air.py` fills `air` + `motion`, keeping two decisions deliberately separate:\n\n**HOW MANY — the sliding quota.** A linear front-loaded curve: `--start` (default 0.80) of\nblock 1 animates, falling to `--end` (0.20) by the last block. Blunt, but definitive and cheap\nto reason about — and it spends where distribution is decided, since a viewer who bails at\nninety seconds never reaches block 8. On an 8×40 film: 32/29/25/22/18/15/11/8 ≈ 160 beats.\n\n**WHICH ones — motion-want ranking, within each block.** Every beat is scored on how much the\npicked frame wants to move; the top N take the block\'s quota:\n\n| cue in `phenomenon` | score |\n|---|---|\n| water / sea / deep / surf / current / bubbles / kelp | **+3** |\n| suspended matter (dust, smoke, mist, ash, spray, embers) | +2 |\n| cloth, robes, hair, banners, sails in wind | +2 |\n| fire, flame, sparks | +2 |\n| motion verbs (rising, pouring, striding, churning, collapsing, drifting) | +2 |\n| living subjects (figures, crowd, birds, creature, sailors) | +1 |\n| **carved stone, relief, inscription, page, text, ink, manuscript** | **−3** |\n| **held / motionless / perfectly still / calm / unbroken** | **−2** |\n\nSo the Leviathan in its light shaft animates and the wall relief rides the free floor —\nautomatically, off the film\'s own `phenomenon` text, with no per-film configuration. That is\nthe dividend of keeping every per-beat decision in a column: the same tool splits a desert film\nand a deep-sea film differently because the films describe themselves differently.\n\n**THE FLEX — `--score-floor` (default 4).** A quota alone starves the back half of a film whose\nmost motion-hungry images are late. Any beat scoring at or above the floor animates in ANY\nblock, on top of its quota. On *Women in the Water* this rescued 15 beats — ten of them in\nblock 8, whose quota was only 8 — so the finale does not end on a slideshow. The curve still\nfront-loads; a hero motion beat can never be dropped for being late.\n\n> **★ THE MARGINAL KLING DOLLAR BUYS RUN-BREAKING, NOT THE NEXT-HIGHEST SCORE.** The score ranks\n> frames in ISOLATION; the viewer experiences SEQUENCE. A run of six consecutive floor beats\n> reads as a slideshow however well each frame was chosen, and ONE Kling beat dropped into the\n> middle breaks the whole stretch. So when budget is left over, find the longest `air=kb` runs\n> and buy the highest-scoring beat INSIDE each. (This is the same blindness STORY ARC names:\n> distributional measures cannot see monotony-in-sequence. Run length is sequential.)\n\n**Get `air` right BEFORE rendering.** `render_clips.py` skips clips already on disk, so a beat\nupgraded after a full render needs `--force` or a manual delete. Dry-run, tune, then render once.', 'Air + Kling (Step 7) — the spend dial'),
    ('ladder', '**Derivation ladder (first match wins), read off `phenomenon` + `register` of the PICKED\nframe** — drafted by `draft_moves.py`, eye-corrected, never hand-invented per beat:', "**Derivation ladder (first match wins), read off the beat's `phenomenon` + `register`** —\ndrafted by `draft_moves.py`, then eye-corrected against the picked frame. Be honest about the\norder: **the tools derive from TEXT, you correct from the IMAGE.** Never hand-invent per beat:", 'the tools derive from TEXT, you correct from the IMAGE'),
    ('frontload', '**Front-load Kling** — the `kling_count` is a contiguous front-N block until per-beat MOTION\ncontrol; a viewer who bails at 90s never reaches later beats, so animate the gate.', '**Front-loading is now a sliding QUOTA, not a contiguous block.** Per-beat control lives in the\n`air` column, so the old contiguous front-N `kling_count` is retired — see Air + Kling above for\nthe quota, the ranking and the score floor.', 'Front-loading is now a sliding QUOTA'),
    ('blankmove', 'Because the floor is **$0**, iteration is free — render all, eyeball a sample, a bad feel is a\none-number tune + a free re-render. Kling stays available additively: mark a beat `air=kling` +\na `motion` and it upgrades, one beat at a time, only where the retention curve says.', 'Because the floor is **$0**, iteration is free — render all, eyeball a sample, a bad feel is a\none-number tune + a free re-render. Kling stays available additively: mark a beat `air=kling` +\na `motion` and it upgrades, one beat at a time, only where the retention curve says.\n\n> **⚠ NEVER LEAVE `move` BLANK.** `ken_burns_still` treats blank and `static` as the SAME\n> true-static branch, which bypasses zoompan entirely and depends on `-loop 1` being on the\n> ffmpeg input. Without that flag a single PNG yields a **one-frame ~0.04s clip** — and ffmpeg\n> exits 0, so it looks like a successful render. Write `static` explicitly when you mean it, and\n> gate every output (Step 8). `draft_moves.py` fills every row, which is the practical defence.', 'NEVER LEAVE `move` BLANK'),
    ('readers', '**The other readers:** `place.py` (winners folder/list → `shot_NNN.png`; hard-fails on\nskip-tile/gap/dupe) · `render_clips.py` (Kling(`motion`) if `air`, else `ken_burns_still(move)`)\n· `draft_moves.py` (`--csv`, `--dry-run`, `--validate` against a shipped film).', '**The other readers** — all pure-stdlib except the render legs, all `--dry-run` before spend:\n\n- **`place.py`** — winners → `shot_NNN.png`; hard-fails (placing NOTHING) on a skip-tile pick,\n  a doubled beat or any gap in 1..N. `--winners` takes a FOLDER of picks **or a `.txt` list of\n  filenames** plus `--grid` to source the bytes from the grid already on the box — so only the\n  filenames travel, not 1.3GB. `--skip-tile` is required (it byte-compares to reject placeholders).\n- **`draft_moves.py`** — fills `move` (`--csv`, `--dry-run`, `--redraft`, `--validate` against a\n  shipped film). Blanks-only by default, so eye-corrections survive a re-run.\n- **`draft_air.py`** — fills `air` + `motion` (`--csv`, `--start`, `--end`, `--score-floor`,\n  `--dry-run`, `--redraft`). The spend dial; see Air + Kling.\n- **`render_clips.py`** — Kling(`motion`) if `air`, else `ken_burns_still(move)`; `--floor-only`,\n  `--dry-run`, `--force`. Skips clips already on disk (resume-safe).\n- **`verify_clips.py`** — the Step-8 gate: ffprobe every clip, `--expect N`, `--normalise` to\n  trim over-long clips losslessly.\n- **`consolidate_grid.py`** — migrates an older per-block grid into the flat folder.', 'all `--dry-run` before spend'),
    ('enginefacts', '- **The skip-tile is channel-agnostic** — `shared/_skip.png` for all channels; a channel may\n  override with `characters/_skip.png` (resolve shared first).', "- **The skip-tile is channel-agnostic** — `shared/_skip.png` for all channels; a channel may\n  override with `characters/_skip.png` (resolve shared first).\n- **A blank `move` hits `ken_burns_still`'s true-static branch** (blank and `static` share it).\n  It bypasses zoompan and relies on `-loop 1`; without that flag a single PNG produces a\n  ONE-FRAME ~0.04s clip that still exits 0. Write `static` explicitly; gate every output.\n- **`render_clips.py` does NOT trim Kling output.** Ken Burns is exact by construction\n  (`-t 5.000` + `-r 24` → 120 frames); Kling returns a non-deterministic frame count (121 is\n  common). `verify_clips.py` is what actually makes all N clips exactly 5.000s.\n- **Derive the trim frame count PER CLIP as `round(fps × 5.0)` — never hardcode 120.** A 30fps\n  clip trimmed to 120 frames is 4.0 seconds.", "A blank `move` hits `ken_burns_still`'s true-static branch"),
    ('tracked', 'large media). BOX uses `python` in the venv; LAPTOP uses `python3`.', 'large media). BOX uses `python` in the venv; LAPTOP uses `python3`.\n\n**Verify a tool is actually IN the repo before you depend on it.** Two working tools were found\nmisplaced or untracked mid-film — one sat at the repo root while the doc implied a channel\nfolder; another existed only as a loose file in `~/Downloads` and had never been committed at\nall. "Code is GitHub-only" is a rule nothing enforces: `git ls-files --error-unmatch <tool>`\ncosts a second and catches it.', 'Verify a tool is actually IN the repo'),
    ('changelog', '  `consolidate_grid.py` migrates older films.', '  `consolidate_grid.py` migrates older films.\n- **The air/Kling SPEND DIAL** (22 Jul, WITW clips). `draft_air.py` retires both the contiguous\n  front-N `kling_count` and the earlier air drafter: sliding quota (80%→20%) × motion-want\n  ranking × score floor. **Water added to the air vocabulary** — its absence had scored a\n  deep-sea film at zero from block 4 on. Marginal budget goes to RUN-BREAKING, not the next\n  highest score.\n- **Step 8 finally has its gate.** `verify_clips.py` implements the "ffprobe every output,\n  hard-fail anything not 5.000s" rule the doc has always asserted and nothing implemented —\n  plus the Kling trim `render_clips.py` never did, with the frame count derived per clip.', 'The air/Kling SPEND DIAL'),
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
    bak = path + ".pre_airdial"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(orig); print("backup:", bak)
    open(path, "w", encoding="utf-8").write(src)
    print("OK: _LEGO.md upgraded -- air/Kling spend dial integrated, Step-8 gate documented.")


if __name__ == "__main__":
    main()
