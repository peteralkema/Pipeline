#!/usr/bin/env python3
"""
patch_ante_machinam_2026-06-17.py — two targeted craft additions banked 17 June:

  1. Runtime calibration (Pacing reality / Constitution SS6): a words-only runtime
     estimate UNDERSHOOTS because the Ken-Burns minimum hold stretches short beats;
     real runtime is beat-floored at ~14s/beat. 88 beats -> 20.7 min measured.

  2. Script-format-from-exemplar (Part VI "What you hand the machine"): author by
     copying a known-good script's exact markup, never from the doc's prose
     description. A wrong format parses to ZERO beats (ZeroDivisionError).

Targeted insertions, NOT a rewrite. Each anchor is verified to occur exactly once;
the patch refuses if an anchor is missing or ambiguous. Sentinel guards re-runs.
Pure ASCII. Backs up to .pre_2026-06-17.

Run on LAPTOP:  python3 shared/docs/patch_ante_machinam_2026-06-17.py
  (or wherever the file lives; the script resolves the doc next to itself, then
   falls back to ./shared/docs/__ante-machinam.md and ./__ante-machinam.md)
"""
import sys
from pathlib import Path

SENTINEL = "Runtime is beat-floored, not words-only"

# Resolve the doc: prefer __ante-machinam.md next to this script, then common spots.
def _find_target():
    here = Path(__file__).resolve().parent
    cands = [
        here / "__ante-machinam.md",
        here / "ante-machinam.md",
        Path.cwd() / "shared/docs/__ante-machinam.md",
        Path.cwd() / "shared/docs/ante-machinam.md",
        Path.cwd() / "__ante-machinam.md",
    ]
    for c in cands:
        if c.exists():
            return c
    return None

# --- Insertion 1: runtime calibration, appended to the IV.6 "write long" paragraph ---
ANCHOR_1 = ("**Inworld renders faster than you plan \u2014 write long.** Measured ~150\u2013190 "
            "wpm against a 135 wpm plan; the rendered cut is ~85\u201390% of the word-count "
            "estimate. Doesn't affect sync (Whisper measures the real audio) but does affect "
            "runtime. Write 10\u201315% more than the target. (The Watchers: 2,716 words \u2192 "
            "17.7 min, ~195 wpm.)")
ADD_1 = (" **But runtime is beat-floored, not words-only (banked 17 June).** The Ken-Burns "
         "minimum hold stretches short beats up to the clip floor, so a words-only estimate "
         "UNDERSHOOTS real runtime. Real runtime \u2248 **beat count \u00d7 ~14s**. Prehistoric "
         "Disasters' Toba: 88 beats \u2192 20.7 min measured (a words-only estimate predicted "
         "~13). A ~28-min words-estimate script lands closer to ~40 min. Sanity-check runtime "
         "from beat count \u00d7 ~14s, not from wpm alone \u2014 the two estimates bracket the "
         "truth, and the beat-count one is the floor.")

# ASCII fallback for ANCHOR_1 in case the live file uses plain hyphens / quotes.
ANCHOR_1_ASCII = ("**Inworld renders faster than you plan -- write long.**")

# --- Insertion 2: script-format-from-exemplar, appended to the Part VI handoff para ---
ANCHOR_2 = ("Numbers spelled out in narration; numerals fine in the header. That is the "
            "entire contract \u2014 get the script right and the machine does the rest.")
ADD_2 = ("\n\n**Author the format by copying a known-good script, never from this "
         "description (banked 17 June).** The shape above is a *description*; the parser "
         "reads *exact markup*. Authoring from the prose \u2014 YAML `---` fences, single-`#` "
         "headers, `NARRATION:`/`VISUAL:` labels \u2014 parsed to ZERO beats and crashed the "
         "build (ZeroDivisionError on the first Toba draft). The reliable method: open a "
         "working `script.md` (e.g. a shipped Sacred Dawn or Final Hours project), copy its "
         "exact structure \u2014 bare `key: value` header lines with NO fences, `## COLD OPEN` / "
         "`## PART \u2026` double-hash section headers, then `[A] <narration on one line>` "
         "followed by `VISUAL: <prompt>` on the next line with a blank line between beats \u2014 "
         "and swap in your content. For bulk-prepping a script written in the wrong shape, a "
         "mechanical reformatter (strip fences, `#`\u2192`##`, reorder any "
         "`NARRATION:`/`VISUAL:` pair into `[A]`+`VISUAL:`) is the converter pattern. **Verify "
         "before spending:** `parse_script.py <md> --json /tmp/b.json --json-full /tmp/f.json` "
         "prints the beat count for free \u2014 a zero or a crash means the format is wrong, not "
         "the content.")


def main():
    target = _find_target()
    if target is None:
        sys.exit("FAIL: could not locate __ante-machinam.md (looked next to the script, "
                 "in ./shared/docs/, and in cwd). Run from the repo or place the script in "
                 "shared/docs/.")
    text = target.read_text()

    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present in {target.name}).")
        return

    # Resolve anchor 1 (unicode form preferred, ASCII fallback).
    a1 = ANCHOR_1 if text.count(ANCHOR_1) == 1 else (
        ANCHOR_1_ASCII if text.count(ANCHOR_1_ASCII) == 1 else None)
    if a1 is None:
        sys.exit("FAIL: 'Inworld renders faster' anchor not found exactly once "
                 f"(unicode={text.count(ANCHOR_1)}, ascii={text.count(ANCHOR_1_ASCII)}) "
                 "\u2014 paste the IV.6 'write long' paragraph and I'll re-cut.")
    if text.count(ANCHOR_2) != 1:
        sys.exit(f"FAIL: Part VI 'entire contract' anchor found {text.count(ANCHOR_2)} "
                 "times (expected 1) \u2014 paste the 'What you hand the machine' paragraph "
                 "and I'll re-cut.")

    new = text.replace(a1, a1 + ADD_1, 1)
    new = new.replace(ANCHOR_2, ANCHOR_2 + ADD_2, 1)

    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change or sentinel missing \u2014 aborting.")

    backup = target.with_suffix(target.suffix + ".pre_2026-06-17")
    if not backup.exists():
        backup.write_text(text)
    target.write_text(new)
    print(f"OK: patched {target.name} (backup: {backup.name}).")
    print("    Two additions: runtime calibration (Pacing reality) + "
          "script-format-from-exemplar (Part VI).")
    print(f"    Verify:  grep -n 'beat-floored\\|copying a known-good script' {target}")


if __name__ == "__main__":
    main()
