#!/usr/bin/env python3
"""
patch_mc_gatebody_quotefix.py — fix the quote-nesting break in the gate buttons.

node --check found it: the stills-gate buttons
  '<button onclick="gate('go')">...'
have inner single quotes that CLOSE the surrounding single-quoted JS string ->
"SyntaxError: Unexpected identifier 'go'", which breaks the whole <script> so
the page sits on "loading…".

Fix: wrap those two button strings in DOUBLE quotes instead, so the inner
gate('go') / gate('skip') single quotes sit safely inside. (The onclick HTML
attribute then uses single quotes around its value, which is valid HTML.)

One edit. Idempotent (marker), backs up to .pre_quotefix.

Run on the box:
  python shared/mission_control/patch_mc_gatebody_quotefix.py --check
  python shared/mission_control/patch_mc_gatebody_quotefix.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# Switch the two button lines from single-quoted JS strings (broken by the inner
# gate('go') quotes) to double-quoted JS strings, with the onclick attribute
# value using single quotes (valid HTML). Net served HTML is identical-and-valid.
EDITS.append(dict(
    marker="onclick='gate(",
    old='''      '<div class="row">' +
        '<button onclick="gate(\\'go\\')">Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick="gate(\\'skip\\')">Skip</button>' +
      '</div></div>';''',
    new='''      '<div class="row">' +
        "<button onclick='gate(\\"go\\")'>Generate Clips (approve stills)</button>" +
        "<button class=\\"secondary\\" onclick='gate(\\"skip\\")'>Skip</button>" +
      '</div></div>';''',
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not T.is_file():
        sys.exit(f"missing: {T}")
    text = T.read_text()

    plans, fatal = [], []
    for i, e in enumerate(EDITS, 1):
        if e["marker"] in text:
            plans.append((i, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1: plans.append((i, "apply"))
        elif n == 0: fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else: fatal.append(f"edit {i}: anchor x{n}")

    print("=== GATE-BODY QUOTEFIX PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_quotefix")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart: systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
