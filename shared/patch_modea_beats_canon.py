#!/usr/bin/env python3
"""
patch_modea_beats_canon.py — let the MC route carry a canon block.

THE GAP
-------
recreation_pipeline.py's --beats path accepts either:
    [ {...beats...} ]                        (legacy, flat list)
    { "canon": {...}, "beats": [...] }       (new; canon expands {tokens})

and _expand_canon() RAISES SystemExit on any {token} without a canon entry
("fails loudly so typos don't silently produce vague prompts").

modea_beats.py — the bridge from an MC-uploaded script.md to the engine — emits only
{"beats": [...]}. So a reference-mode channel whose VISUAL lines carry {bentley} /
{watson} tokens would hard-fail at expansion: the tokens attach reference images
correctly (the regex scans the RAW prompt), but nothing defines what they mean.

THE FIX
-------
modea_beats.py gains an optional --channel-config. If that channel.json carries a
`canon` block, it is merged into the output dict:

    {"canon": {...}, "beats": [...]}

No flag, or a config with no canon -> output is byte-identical to today. Every existing
channel is unaffected. This is channel-agnostic: any reference-mode channel gets its
canon for free; the dogs are simply the first user.

WHY CANON LIVES IN channel.json
-------------------------------
A {token} does double duty in the engine: it attaches the character's reference images
(reference_map) AND expands into the prompt text (canon). Keeping both in channel.json
means a character's identity is defined in exactly ONE place and cannot drift across
thirty hand-typed VISUAL lines. That is the whole point of the canon mechanism.

Discipline: verifies its anchors, py_compiles the result before writing, keeps a .pre_*
backup, idempotent.

Run on the BOX from ~/Pipeline (after git pull):
    python shared/patch_modea_beats_canon.py --dry-run
    python shared/patch_modea_beats_canon.py
"""

from __future__ import annotations

import argparse
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TARGET = Path("shared/modea_beats.py")
MARKER = "# [canon] reference-mode channels carry their canon block through to the engine"

# ── 1. the arg ────────────────────────────────────────────────────────────
ANCHOR_ARG = '    ap.add_argument("--map", default=None, help="index map output (default: <out stem>_index.json)")'
NEW_ARG = ANCHOR_ARG + '''
    ap.add_argument("--channel-config", default=None,
                    help="channel.json; if it has a `canon` block it is emitted alongside "
                         "the beats so the engine can expand {tokens}. Optional: without "
                         "it the output is exactly as before.")'''

# ── 2. merge canon into the emitted dict, just before it is written ───────
ANCHOR_DUMP = '''    map_path = args.map or (os.path.splitext(args.out)[0] + "_index.json")
    json.dump(beat_script, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)'''

NEW_DUMP = '''    # [canon] reference-mode channels carry their canon block through to the engine
    # A {token} in a VISUAL attaches the character's reference images AND expands into
    # the prompt. _expand_canon raises on an unknown tag, so a reference-mode channel
    # MUST ship its canon. Absent a config (or a canon block) this is a no-op.
    if args.channel_config:
        try:
            _cfg = json.load(open(args.channel_config, encoding="utf-8"))
        except Exception as _e:
            raise SystemExit(f"--channel-config could not be read ({args.channel_config}): {_e}")
        _canon = _cfg.get("canon") or {}
        if _canon:
            _refmap = _cfg.get("reference_map") or {}
            _missing = sorted(set(_refmap) - set(_canon))
            if _missing:
                raise SystemExit(
                    f"reference_map token(s) with no canon entry: {_missing}. "
                    "Every ref token must expand, or the engine halts at _expand_canon."
                )
            beat_script = {"canon": _canon, "beats": beat_script["beats"]}
            print(f"canon block attached: {sorted(_canon.keys())}")

    map_path = args.map or (os.path.splitext(args.out)[0] + "_index.json")
    json.dump(beat_script, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)'''


def fail(msg: str) -> int:
    print(f"!! {msg}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--target", default=str(TARGET))
    args = ap.parse_args()

    target = Path(args.target)
    if not target.is_file():
        return fail(f"{target} not found. Run from ~/Pipeline (repo root).")

    src = target.read_text(encoding="utf-8")

    if MARKER in src:
        print(f"OK  already applied (marker present in {target}); nothing to do.")
        return 0

    problems = []
    if ANCHOR_ARG not in src:
        problems.append("--map add_argument anchor not found")
    if ANCHOR_DUMP not in src:
        problems.append("json.dump / map_path anchor not found")
    if problems:
        for p in problems:
            print(f"!! {p}", file=sys.stderr)
        return fail("anchors did not verify — modea_beats.py has moved. "
                    "Re-read it and update this patch. Nothing was written.")
    print("anchors verified: --map arg, json.dump block")

    out = src.replace(ANCHOR_ARG, NEW_ARG, 1)
    out = out.replace(ANCHOR_DUMP, NEW_DUMP, 1)

    if out == src:
        return fail("no change produced — refusing to write.")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out)
        tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        tmp.unlink(missing_ok=True)
        return fail(f"patched source does not compile; nothing written.\n{e}")
    tmp.unlink(missing_ok=True)
    print("py_compile OK on the patched source")

    if args.dry_run:
        print("\n--dry-run: anchors verified, result compiles, nothing written.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f".pre_canon_{stamp}_{target.name}")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")

    print(f"backup -> {backup}")
    print(f"PATCHED -> {target}")
    print("\nVERIFY:")
    print("  grep -n 'channel_config\\|canon' shared/modea_beats.py")
    print("\nThen patch_modea_leg_canon.py so the leg actually passes --channel-config.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
