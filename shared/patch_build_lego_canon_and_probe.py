#!/usr/bin/env python3
"""patch_build_lego_canon_and_probe.py

TWO fixes to build_lego.py, both anchor-verified and idempotent:

  (1) G34 -- canon wiring. load_config never loaded the project canon.json, so
      canon_of(cfg) returned {} and cmd_stills expanded no tokens (every {codex}/
      {witness} rendered literally, or check_tokens aborted). FIX: in load_config,
      after _project_dir is set, load <project>/canon.json and merge the channel
      base_canon UNDERNEATH it (project wins on collision -- same rule as
      recreation_pipeline). Store as cfg["canon"]; canon_of() is unchanged and now
      returns the real tokens for gate_block, cmd_film AND cmd_stills at once.

  (2) G24/G49 -- the probe is not a separate build. cmd_stills scopes by BLOCK
      (positional args = block ids). ADD an optional `--beats a,b,c` (or
      `--beats B/C,...` block/clip form) that renders exactly those clip indices
      across the whole film into one grid-probe folder -- a cross-film register
      sample. Same render loop, gate, reference path. No new command.

Idempotent: each edit checks whether it is already applied and skips it.
.pre_ backup once. py_compile before write. ASCII-only. Pure stdlib.
This edits a BOX code file: run LAPTOP-side, commit, push, box git pull.

    cd ~/Projects/Pipeline
    python3 shared/patch_build_lego_canon_and_probe.py            # or pass --target
"""
import argparse
import os
import py_compile
import sys
import tempfile

# ---- edit 1: canon load in load_config -------------------------------------
ANCHOR_1 = '''    cfg["_channel_dir"] = str(cj.parent)
    cfg["_project_dir"] = str(proj)
    cfg.setdefault("beats_per_block", 40)
    return cfg'''

REPLACE_1 = '''    cfg["_channel_dir"] = str(cj.parent)
    cfg["_project_dir"] = str(proj)
    cfg.setdefault("beats_per_block", 40)
    # canon: project <project>/canon.json layered OVER channel base_canon
    # (project wins on key collision -- same rule as recreation_pipeline). This
    # is what canon_of(cfg) returns; without it token expansion is a silent no-op.
    _merged_canon = dict(cfg.get("base_canon", {}) or {})
    _cj = proj / "canon.json"
    if _cj.is_file():
        try:
            _merged_canon.update(json.loads(_cj.read_text()))
        except Exception as _e:
            raise SystemExit(f"canon.json parse error ({_cj}): {_e}")
    cfg["canon"] = _merged_canon
    return cfg'''

MARKER_1 = 'cfg["canon"] = _merged_canon'

# ---- edit 2: --beats filter in cmd_stills ----------------------------------
ANCHOR_2 = '''    rows = load_master(cfg)
    if not has_col(rows, "phenomenon"):
        raise SystemExit("stills needs a 'phenomenon' column -- author first.")
    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})'''

REPLACE_2 = '''    rows = load_master(cfg)
    if not has_col(rows, "phenomenon"):
        raise SystemExit("stills needs a 'phenomenon' column -- author first.")
    # beats=b/c,b/c  -> cross-film PROBE: render exactly these (block/clip) beats
    # into one grid-probe folder (register/token spread). A DASHLESS positional
    # token (a --flag is eaten by the top-level parser). Matches how calibrate
    # prints beats: block/clip.
    _probe_beats = None
    _bspec = None
    for _a in list(argv):
        if _a.startswith("beats="):
            _bspec = _a.split("=", 1)[1]
            argv = [x for x in argv if x != _a]
            break
    if _bspec is not None:
        _probe_beats = set()
        for _tok in _bspec.split(","):
            _tok = _tok.strip()
            if not _tok:
                continue
            if "/" not in _tok:
                raise SystemExit("beats= needs block/clip pairs, e.g. beats=1/1,2/3,6/20")
            _b, _c = _tok.split("/", 1)
            _probe_beats.add((int(_b), int(_c)))
        if not _probe_beats:
            raise SystemExit("beats= needs block/clip pairs, e.g. beats=1/1,2/3,6/20")
        _have = {(int(r["block_id"]), int(r["clip_index"])) for r in rows}
        _oob = sorted(p for p in _probe_beats if p not in _have)
        if _oob:
            raise SystemExit("beats= not in master: %s"
                             % ", ".join("%d/%d" % p for p in _oob))
    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})'''

MARKER_2 = 'beats= needs block/clip pairs'

# The box currently has the earlier FLAT-INDEX beats= version. Accept that block
# as an alternate anchor -> same REPLACE_2 (now block/clip), so a re-patch heals
# the box instead of aborting.
ALT_ANCHOR_2 = '''    # beats=a,b,c  -> cross-film PROBE: render exactly these FLAT FILM INDICES
    # (1..N over the whole master, master order) into one grid-probe folder. A
    # DASHLESS positional token (a --flag is eaten by the top-level parser before
    # this command sees it). 1-based, matches calibrate.
    _probe_beats = None
    _bspec = None
    for _a in list(argv):
        if _a.startswith("beats="):
            _bspec = _a.split("=", 1)[1]
            argv = [x for x in argv if x != _a]
            break
    if _bspec is not None:
        _probe_beats = set()
        for _tok in _bspec.split(","):
            _tok = _tok.strip()
            if _tok:
                _probe_beats.add(int(_tok))
        if not _probe_beats:
            raise SystemExit("beats= needs film indices 1..N, e.g. beats=1,58,231")
        _nrows = len(rows)
        _oob = sorted(n for n in _probe_beats if n < 1 or n > _nrows)
        if _oob:
            raise SystemExit(f"beats= out of range 1..{_nrows}: {_oob}")
    wanted = [int(a) for a in argv] or sorted({int(r["block_id"]) for r in rows})'''

# ---- edit 3: honour _probe_beats in the block loop -------------------------
ANCHOR_3 = '''    for block in wanted:
        brows = [r for r in rows if int(r["block_id"]) == block]
        gerrs = gate_block(brows, cfg, load_banned(cfg))
        if gerrs:
            print("\\n".join("  GATE FAIL: " + e for e in gerrs)); raise SystemExit(1)
        grid = proj / f"grid-b{block:02d}"'''

REPLACE_3 = '''    if _probe_beats is not None:
        wanted = [0]  # single synthetic pass; the probe selects rows by film ordinal
    for block in wanted:
        if _probe_beats is not None:
            brows = [r for r in rows if (int(r["block_id"]), int(r["clip_index"])) in _probe_beats]
        else:
            brows = [r for r in rows if int(r["block_id"]) == block]
        # probe = a cross-film SAMPLE of already-gated beats (repeating clip_index
        # across blocks would false-trip the per-block structural gate). Skip the
        # structural gate here; token expansion + the >7KB black-frame eyeball are
        # the real spend guards for a probe.
        if _probe_beats is None:
            gerrs = gate_block(brows, cfg, load_banned(cfg))
            if gerrs:
                print("\\n".join("  GATE FAIL: " + e for e in gerrs)); raise SystemExit(1)
        grid = (proj / "grid-probe") if _probe_beats is not None else (proj / f"grid-b{block:02d}")'''

MARKER_3 = 'int(r["clip_index"])) in _probe_beats]'

# box currently has the flat-ordinal enumerate version of the row-select; accept
# it as an alternate anchor -> same REPLACE_3 (block/clip pair match).
ALT_ANCHOR_3 = '''    if _probe_beats is not None:
        wanted = [0]  # single synthetic pass; the probe selects rows by film ordinal
    for block in wanted:
        if _probe_beats is not None:
            brows = [r for i, r in enumerate(rows, 1) if i in _probe_beats]
        else:
            brows = [r for r in rows if int(r["block_id"]) == block]
        gerrs = gate_block(brows, cfg, load_banned(cfg))
        if gerrs:
            print("\\n".join("  GATE FAIL: " + e for e in gerrs)); raise SystemExit(1)
        grid = proj / f"grid-b{block:02d}"'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=None, help="path to build_lego.py (default: repo root)")
    args = ap.parse_args()

    if args.target:
        target = os.path.abspath(args.target)
    else:
        d = os.path.abspath(os.getcwd())
        root = None
        while d != os.path.dirname(d):
            if os.path.isdir(os.path.join(d, ".git")):
                root = d
                break
            d = os.path.dirname(d)
        if not root:
            sys.stderr.write("ERROR: no .git found; pass --target path/to/build_lego.py\n")
            sys.exit(1)
        target = os.path.join(root, "build_lego.py")

    if not os.path.isfile(target):
        sys.stderr.write("ERROR: not found: %s\n" % target)
        sys.exit(1)

    src = open(target, "r", encoding="utf-8").read()

    edits = [
        ("canon load in load_config", ANCHOR_1, REPLACE_1, MARKER_1, None),
        ("--beats parse in cmd_stills", ANCHOR_2, REPLACE_2, MARKER_2, ALT_ANCHOR_2),
        ("probe row-select in loop", ANCHOR_3, REPLACE_3, MARKER_3, ALT_ANCHOR_3),
    ]

    for name, anchor, replace, marker, alt in edits:
        if marker in src:
            print("skip (already applied): %s" % name)
            continue
        use = anchor if anchor in src else (alt if (alt and alt in src) else None)
        if use is None:
            sys.stderr.write("ERROR: anchor not found for %r -- ABORT (no write).\n"
                             "The source differs from expected; do not force. "
                             "Paste `grep -nE 'beats=|--beats|_merged_canon|film ordinal' build_lego.py`.\n" % name)
            sys.exit(1)
        if src.count(use) != 1:
            sys.stderr.write("ERROR: anchor for %r matches %d times (need 1) -- ABORT.\n"
                             % (name, src.count(use)))
            sys.exit(1)
        src = src.replace(use, replace)
        print("applied: %s" % name)

    if any(ord(c) > 127 for c in "".join([REPLACE_1, REPLACE_2, REPLACE_3])):
        sys.stderr.write("ERROR: non-ASCII in replacement text\n")
        sys.exit(1)

    # compile the NEW source in a temp file before touching the target
    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(src)
    tmp.close()
    try:
        py_compile.compile(tmp.name, doraise=True)
    except py_compile.PyCompileError as e:
        sys.stderr.write("ERROR: patched source fails to compile -- ABORT (no write):\n%s\n" % e)
        os.unlink(tmp.name)
        sys.exit(1)
    os.unlink(tmp.name)

    bak = target + ".pre_canonprobe"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(open(target, "r", encoding="utf-8").read())
        print("backup: %s" % bak)

    open(target, "w", encoding="utf-8").write(src)
    print("OK: build_lego.py patched (canon load + --beats probe). py_compile passed.")


if __name__ == "__main__":
    main()
