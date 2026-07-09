#!/usr/bin/env python3
"""
patch_orchestrator_wordless_leg.py — wire the wordless leg into the orchestrator.

Depends on patch_orchestrator_timing_source.py having run first (it adds the
`timing_source` branch and the cfg parameter to decide_legs). That patch made a
beatsheet channel SKIP the audio leg; this one gives it something to run INSTEAD.

Two edits:
  1. decide_legs()  — on timing_source=beatsheet, append "wordless" to legs.
  2. main()         — dispatch: if "wordless" in legs, call wordless_leg.run_wordless_leg(ctx),
                      mirroring the audio-leg dispatch (same guard, same halt semantics).
  3. imports        — import wordless_leg alongside the other legs.

After this, an MC-uploaded script.md on a beatsheet channel runs:
    parse_script -> beats.json -> WORDLESS LEG (VO clips + durations + voiceover)
                 -> Mode A leg -> convergence -> final_video.mp4

Voice-led channels are untouched: no timing_source key -> "narration" -> audio leg, as always.

Discipline: verifies every anchor before writing, py_compiles the result before it is
allowed near the real file, writes a .pre_* backup, and is idempotent.

Run on the BOX from ~/Pipeline (after git pull):
    python shared/patch_orchestrator_wordless_leg.py --dry-run
    python shared/patch_orchestrator_wordless_leg.py
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
MARKER = "# [wordless] the wordless leg replaces the audio leg as the timing source"

# ── 1. import ─────────────────────────────────────────────────────────────
ANCHOR_IMPORT = "import convergence_leg"
NEW_IMPORT = "import convergence_leg\nimport wordless_leg"

# ── 2. decide_legs: give the beatsheet branch a leg to run ────────────────
ANCHOR_DECIDE = '''    timing_source = (cfg or {}).get("timing_source", "narration")
    if timing_source == "beatsheet":
        legs = []
        t.decision("timing_source=beatsheet → audio leg SKIPPED "
                   "(timing is declared in the beat-sheet; VO is a sparse layer)")'''

NEW_DECIDE = '''    timing_source = (cfg or {}).get("timing_source", "narration")
    if timing_source == "beatsheet":
        # [wordless] the wordless leg replaces the audio leg as the timing source
        legs = ["wordless"]
        t.decision("timing_source=beatsheet → audio leg SKIPPED; WORDLESS leg WILL run "
                   "(timing is declared in the beat-sheet; VO is a sparse layer)")'''

# ── 3. main(): dispatch, mirroring the audio-leg block ────────────────────
ANCHOR_DISPATCH = '''    # ── 3a: AUDIO LEG (wired) ─────────────────────────────────────────────
    if "audio" in legs:'''

NEW_DISPATCH = '''    # ── 3a-w: WORDLESS LEG (wired) — audio leg's sibling for beatsheet channels ──
    if "wordless" in legs:
        if proj_dir is None:
            t.halt("cannot run wordless leg — channel/project unresolved "
                   "(need channel.json + --project).")
            sys.exit(1)
        wl = wordless_leg.run_wordless_leg(ctx)
        if wl is None:
            t.halt("wordless leg halted. Fix the reported issue and re-run.")
            sys.exit(1)

    # ── 3a: AUDIO LEG (wired) ─────────────────────────────────────────────
    if "audio" in legs:'''

# ── 4. the "not yet wired" filter must know about the new leg ─────────────
ANCHOR_PENDING = 'pending = [l for l in legs if l not in ("audio", "modeB", "modeA", "convergence")]'
NEW_PENDING = 'pending = [l for l in legs if l not in ("audio", "wordless", "modeB", "modeA", "convergence")]'


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

    # Hard prerequisite: the timing_source patch must have run.
    if 'timing_source = (cfg or {}).get("timing_source", "narration")' not in src:
        return fail("prerequisite missing: run patch_orchestrator_timing_source.py first "
                    "(this patch extends the branch it adds). Nothing was written.")

    problems = []
    for label, anchor in (("import", ANCHOR_IMPORT),
                          ("decide_legs beatsheet branch", ANCHOR_DECIDE),
                          ("audio-leg dispatch", ANCHOR_DISPATCH),
                          ("pending-legs filter", ANCHOR_PENDING)):
        if anchor not in src:
            problems.append(f"{label} anchor not found")
    if problems:
        for p in problems:
            print(f"!! {p}", file=sys.stderr)
        return fail("anchors did not verify — orchestrate.py has moved. "
                    "Re-read the file and update this patch. Nothing was written.")
    print("anchors verified: import, decide_legs branch, dispatch, pending filter")

    out = src.replace(ANCHOR_IMPORT, NEW_IMPORT, 1)
    out = out.replace(ANCHOR_DECIDE, NEW_DECIDE, 1)
    out = out.replace(ANCHOR_DISPATCH, NEW_DISPATCH, 1)
    out = out.replace(ANCHOR_PENDING, NEW_PENDING, 1)

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
    backup = target.with_name(f".pre_wordless_leg_{stamp}_{target.name}")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")

    print(f"backup -> {backup}")
    print(f"PATCHED -> {target}")
    print("\nVERIFY:")
    print("  grep -n 'wordless' shared/orchestrate.py")
    print("  python -c 'import ast; ast.parse(open(\"shared/orchestrate.py\").read()); print(\"AST OK\")'")
    print("\nThen run an EXISTING channel through Mission Control once more — the default "
          "path must still print 'audio leg WILL run'. Compile is not proof; click the thing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
