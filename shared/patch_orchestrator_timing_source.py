#!/usr/bin/env python3
"""
patch_orchestrator_timing_source.py — teach decide_legs() that a channel may source its
timing from the beat-sheet instead of from narration.

THE ONE EDIT TO SHARED CODE for the wordless-spine path. Everything else is new files.

Today decide_legs() hardcodes:

    legs = ["audio"]  # always — timing source

That invariant is correct for every voice-led channel and stays the DEFAULT. This patch
makes it conditional on channel.json's `timing_source`:

    "narration" (or absent) -> existing behaviour, byte-for-byte. Every current channel.
    "beatsheet"             -> audio leg skipped; timing comes from the beat-sheet and the
                               wordless legs (generate_twovoice_vo.py +
                               build_wordless_audio.py) produce durations.json +
                               voiceover.mp3 before convergence.

decide_legs() currently receives only `beats`, so it also gains a `cfg` parameter. Both
call sites are updated. The signature change is additive with a default (cfg=None) so any
other caller keeps working.

Discipline: verifies its anchors before writing, py_compiles the result before committing
it, writes a .pre_* backup, and is safe to run twice (idempotent — detects its own marker
and exits 0 without touching the file).

Run on the BOX from ~/Pipeline (after git pull):
    python shared/patch_orchestrator_timing_source.py
    python shared/patch_orchestrator_timing_source.py --dry-run
"""

from __future__ import annotations

import argparse
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TARGET = Path("shared/orchestrate.py")
MARKER = "# [timing_source] wordless-spine channels skip the audio leg"

ANCHOR_DEF = 'def decide_legs(beats, t):'
ANCHOR_LEGS = '    legs = ["audio"]  # always — timing source\n    t.decision("audio leg WILL run (always — it is the timing source)")'

NEW_DEF = 'def decide_legs(beats, t, cfg=None):'
NEW_LEGS = '''    # [timing_source] wordless-spine channels skip the audio leg
    # "narration" (or absent) -> the audio leg is the timing source, as always.
    # "beatsheet"             -> timing is declared per beat; the wordless legs write
    #                            durations.json + voiceover.mp3. See wordless-vo-wiring-spec.md.
    timing_source = (cfg or {}).get("timing_source", "narration")
    if timing_source == "beatsheet":
        legs = []
        t.decision("timing_source=beatsheet → audio leg SKIPPED "
                   "(timing is declared in the beat-sheet; VO is a sparse layer)")
    else:
        legs = ["audio"]  # always — timing source
        t.decision("audio leg WILL run (always — it is the timing source)")'''

# decide_legs is called with (beats, t); give it cfg. Anchor the CALL SITE exactly —
# note the bare "decide_legs(beats, t)" substring also occurs inside the def line, so we
# anchor on the full assignment to avoid matching the definition.
ANCHOR_CALL = "legs, modes = decide_legs(beats, t)"
NEW_CALL = "legs, modes = decide_legs(beats, t, cfg)"


def fail(msg: str) -> int:
    print(f"!! {msg}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="verify anchors, write nothing")
    ap.add_argument("--target", default=str(TARGET))
    args = ap.parse_args()

    target = Path(args.target)
    if not target.is_file():
        return fail(f"{target} not found. Run from ~/Pipeline (repo root).")

    src = target.read_text(encoding="utf-8")

    # ── idempotence: already applied? ──────────────────────────────────────
    if MARKER in src:
        print(f"OK  already applied (marker present in {target}); nothing to do.")
        return 0

    # ── verify EVERY anchor before touching anything ──────────────────────
    problems = []
    if ANCHOR_DEF not in src:
        problems.append(f"def anchor not found: {ANCHOR_DEF!r}")
    if ANCHOR_LEGS not in src:
        problems.append("legs anchor not found (the 'legs = [\"audio\"]' block)")
    if ANCHOR_CALL not in src:
        problems.append(f"call-site anchor not found: {ANCHOR_CALL!r}")
    if problems:
        for p in problems:
            print(f"!! {p}", file=sys.stderr)
        return fail("anchors did not verify — orchestrate.py has moved. "
                    "Re-read the file and update this patch. Nothing was written.")

    n_calls = src.count(ANCHOR_CALL)
    print(f"anchors verified: def, legs-block, {n_calls} call site(s)")

    # ── build the new source ──────────────────────────────────────────────
    out = src.replace(ANCHOR_DEF, NEW_DEF, 1)
    out = out.replace(ANCHOR_LEGS, NEW_LEGS, 1)
    out = out.replace(ANCHOR_CALL, NEW_CALL)

    if out == src:
        return fail("no change produced — refusing to write.")

    # ── py_compile the RESULT before it is allowed near the real file ─────
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

    # ── backup, then write ────────────────────────────────────────────────
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f".pre_timing_source_{stamp}_{target.name}")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")

    print(f"backup -> {backup}")
    print(f"PATCHED -> {target}")
    print("\nVERIFY:")
    print("  grep -n 'timing_source' shared/orchestrate.py")
    print("  python -c 'import ast,sys; ast.parse(open(\"shared/orchestrate.py\").read())'")
    print("\nThen: load Mission Control and run one existing channel end-to-end. The default "
          "path must be byte-identical in behaviour (compile alone is insufficient — "
          "click the thing).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
