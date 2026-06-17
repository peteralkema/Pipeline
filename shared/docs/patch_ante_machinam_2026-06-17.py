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

SENTINEL = "runtime is beat-floored, not words-only"

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

# --- Insertion 1: runtime calibration, appended after the IV.6 "write long" paragraph ---
# Anchor on a SHORT dash-free substring guaranteed byte-stable (the parenthetical
# Watchers stat ends the paragraph). We append ADD_1 immediately after it.
ANCHOR_1 = "2,716 words"
ANCHOR_1_ASCII = ANCHOR_1  # same; kept for the dual-check shape below
ADD_1_FULL = (" **But runtime is beat-floored, not words-only (banked 17 June).** "
              "The Ken-Burns minimum hold stretches short beats up to the clip floor, so a "
              "words-only estimate UNDERSHOOTS real runtime. Real runtime is roughly "
              "**beat count times ~14s**. Prehistoric Disasters' Toba: 88 beats -> 20.7 min "
              "measured (a words-only estimate predicted ~13). A ~28-min words-estimate script "
              "lands closer to ~40 min. Sanity-check runtime from beat count, not wpm alone.")

# --- Insertion 2: script-format-from-exemplar, appended after the Part VI handoff para ---
# Anchor on a short dash-free unique substring near the end of the paragraph.
ANCHOR_2 = "get the script right and the machine does the rest."
ADD_2_FULL = ("\n\n**Author the format by copying a known-good script, never from this "
              "description (banked 17 June).** The shape above is a *description*; the parser "
              "reads *exact markup*. Authoring from the prose -- YAML `---` fences, single-`#` "
              "headers, `NARRATION:`/`VISUAL:` labels -- parsed to ZERO beats and crashed the "
              "build (ZeroDivisionError on the first Toba draft). The reliable method: open a "
              "working `script.md` (a shipped Sacred Dawn or Final Hours project), copy its "
              "exact structure -- bare `key: value` header lines with NO fences, `## COLD OPEN` "
              "/ `## PART ...` double-hash section headers, then `[A] <narration on one line>` "
              "followed by `VISUAL: <prompt>` on the next line with a blank line between beats "
              "-- and swap in your content. For bulk-prepping a script in the wrong shape, a "
              "mechanical reformatter (strip fences, `#`->`##`, reorder any "
              "`NARRATION:`/`VISUAL:` pair into `[A]`+`VISUAL:`) is the converter pattern. "
              "**Verify before spending:** `parse_script.py <md> --json /tmp/b.json "
              "--json-full /tmp/f.json` prints the beat count for free -- a zero or a crash "
              "means the format is wrong, not the content.")


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

    # Anchor 1: the substring is mid-paragraph; append ADD_1 at the END of the line
    # that contains it (so the addition lands right after the paragraph's last sentence).
    if text.count(ANCHOR_1) != 1:
        sys.exit(f"FAIL: anchor-1 substring '{ANCHOR_1}' found {text.count(ANCHOR_1)} times "
                 "(expected 1) -- paste line 216 and I'll re-cut.")
    lines = text.split("\n")
    idx1 = next((i for i, ln in enumerate(lines) if ANCHOR_1 in ln), None)
    if idx1 is None:
        sys.exit("FAIL: anchor-1 line not found after split -- aborting.")
    lines[idx1] = lines[idx1] + ADD_1_FULL
    text2 = "\n".join(lines)

    # Anchor 2: append ADD_2 immediately after its substring (paragraph end).
    if text2.count(ANCHOR_2) != 1:
        sys.exit(f"FAIL: anchor-2 substring '{ANCHOR_2}' found {text2.count(ANCHOR_2)} times "
                 "(expected 1) -- paste line 289 and I'll re-cut.")
    new = text2.replace(ANCHOR_2, ANCHOR_2 + ADD_2_FULL, 1)

    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change or sentinel missing -- aborting.")

    backup = target.with_suffix(target.suffix + ".pre_2026-06-17")
    if not backup.exists():
        backup.write_text(text)
    target.write_text(new)
    print(f"OK: patched {target.name} (backup: {backup.name}).")
    print("    Two additions: runtime calibration (IV.6) + "
          "script-format-from-exemplar (Part VI).")
    print(f"    Verify:  grep -n 'beat-floored\\|copying a known-good script' {target}")


if __name__ == "__main__":
    main()
