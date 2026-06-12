#!/usr/bin/env python3
"""
patch_mc_pollfix.py — fix the poll-clobber bug in pipeline_server.py's page.

Symptom: selecting a channel resets the dropdown ~2.5s later, because poll()
re-renders the idle view on every tick and wipes the user's in-progress
selection.

Fix: track the last rendered phase in JS; only (re)render when the phase
CHANGES. While idle, the dropdowns build once and the poll leaves them alone.
While running, re-render each tick is fine (no user input to clobber) — but we
still gate it on phase-or-gate change to avoid flespecfan flicker.

Idempotent: verifies the old poll() block exists once; skips if already applied.
Backs up to pipeline_server.py.pre_pollfix.

Run on the box from repo root:
  python shared/mission_control/patch_mc_pollfix.py
  python shared/mission_control/patch_mc_pollfix.py --check
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"

MARKER = "let LAST_RENDER_KEY"

OLD = '''async function poll() {
  const state = await api("/api/state");
  if (state.phase === "idle") renderIdle(state);
  else renderRunning(state);
}
poll();
setInterval(poll, 2500);'''

NEW = '''let LAST_RENDER_KEY = null;
function renderKey(state) {
  // re-render only when something the user SEES changes:
  // phase, or which gate is waiting, or its status.
  const g = state.gate || {};
  return [state.phase, state.job_id, g.name, g.status].join("|");
}
async function poll() {
  const state = await api("/api/state");
  const key = renderKey(state);
  if (key === LAST_RENDER_KEY) return;   // nothing visible changed -> don't clobber the DOM
  LAST_RENDER_KEY = key;
  if (state.phase === "idle") renderIdle(state);
  else renderRunning(state);
}
poll();
setInterval(poll, 2500);'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not TARGET.is_file():
        sys.exit(f"missing: {TARGET}")
    text = TARGET.read_text()

    if MARKER in text:
        print("already applied (idempotent) — nothing to do.")
        return

    n = text.count(OLD)
    if n == 0:
        sys.exit("ANCHOR NOT FOUND — poll() block doesn't match. Aborting (no half-apply).")
    if n != 1:
        sys.exit(f"anchor appears {n}x (must be exactly 1). Aborting.")

    if args.check:
        print("--check: 1 edit WOULD apply (poll-clobber fix). No files written.")
        return

    bak = TARGET.with_suffix(TARGET.suffix + ".pre_pollfix")
    if not bak.exists():
        bak.write_text(text)
        print(f"  backup -> {bak.name}")
    TARGET.write_text(text.replace(OLD, NEW, 1))
    print("  applied -> poll-clobber fix (render only on phase/gate change)")
    print("\nRestart the server to pick it up:")
    print("  (Ctrl-C the running pipeline_server, then re-run it)")


if __name__ == "__main__":
    main()
