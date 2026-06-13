#!/usr/bin/env python3
"""
patch_mc_gatebody_quoteproof.py — the FINAL fix for the gate-button quotes.

Root cause (now pinned): render_page returns a Python TRIPLE-QUOTED string.
Inside it, \\" and \\' are escape sequences Python resolves at import — the
backslash is GONE by the time the JS is served, so escaped quotes collapse and
collide. Two earlier fixes failed for this exact reason.

Robust fix: build the inner quote characters with String.fromCharCode(39) so
NO literal quote or backslash sits inside the JS string. Nothing for Python to
eat, nothing to mis-nest. Verified against the real triple-quote round-trip with
node --check before shipping.

One edit. Idempotent (marker), backs up to .pre_quoteproof.

Run on the box:
  python shared/mission_control/patch_mc_gatebody_quoteproof.py --check
  python shared/mission_control/patch_mc_gatebody_quoteproof.py
  # then ALWAYS verify the served page before refreshing:
  curl -s "http://127.0.0.1:8002/?key=fh2026" | python3 -c "import sys,re; \\
    m=re.search(r'<script>(.*?)</script>', sys.stdin.read(), re.S); \\
    open('/tmp/mc.js','w').write(m.group(1))" && node --check /tmp/mc.js \\
    && echo "PAGE JS VALID"
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# Anchor: the current broken two-button block (escaped-double version from the
# previous patch). Replace with the fromCharCode build. Marker is unique.
EDITS.append(dict(
    marker="String.fromCharCode(39)",
    old='''      '<div class="row">' +
        "<button onclick='gate(\\"go\\")'>Generate Clips (approve stills)</button>" +
        "<button class=\\"secondary\\" onclick='gate(\\"skip\\")'>Skip</button>" +
      '</div></div>';''',
    new='''      '<div class="row">' +
        '<button onclick=' + _SQ + 'gate(' + _SQ + 'go' + _SQ + ')' + _SQ +
          '>Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick=' + _SQ + 'gate(' + _SQ + 'skip' + _SQ + ')' + _SQ +
          '>Skip</button>' +
      '</div></div>';''',
))

# We also need _SQ defined once near the top of renderRunning. Inject it right
# after the function opens. (Separate edit so it lands regardless.)
EDITS.append(dict(
    marker="var _SQ = String.fromCharCode(39)",
    old='''function renderRunning(state) {
  const app = document.getElementById("app");
  const g = state.gate;''',
    new='''function renderRunning(state) {
  const app = document.getElementById("app");
  var _SQ = String.fromCharCode(39);  // single quote, quote-proof (no literal ' in source)
  const g = state.gate;''',
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

    print("=== GATE-BODY QUOTEPROOF PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_quoteproof")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart, THEN node --check the served page before refreshing:")
    print("  systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
