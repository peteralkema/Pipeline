#!/usr/bin/env python3
"""
patch_gate_auto.py — add an 'auto' gate-mode to await_gate().

Today await_gate(ctx, ...) branches on ctx["gate_mode"]: "cli" (input()) or "job"
(poll the job record). This adds a third mode, "auto", that resolves every gate
immediately to its ACCEPT decision and returns — no prompt, no poll, no block.
This is what unattended batch runs use to sail through the audio keep/swap gate
and the stills review gate without a human.

Accept decision per gate:
  - explicit ctx["auto_decisions"][name] if provided (e.g. {"stills":"go","audio":"keep"})
  - else the gate's documented accept default mapped from the FIRST option
    (audio -> "keep", stills -> "go"), which is options[0] for both real gates.

We deliberately pick options[0] as the accept default because both live gates list
the proceed option first (["keep","swap"], ["go","skip"]). The per-gate override map
exists so a future gate whose options[0] is NOT the accept path can be made explicit
without code changes.

Edits shared/mission_control/gate_protocol.py. Idempotent (sentinel: 'gate_mode == "auto"'),
backs up to .pre_auto, verifies the anchor appears once.

Run on LAPTOP:  python3 shared/patch_gate_auto.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "mission_control" / "gate_protocol.py"
SENTINEL = 'gate_mode == "auto"'

ANCHOR = """    gate_mode = ctx.get("gate_mode", "cli")
    cli_map = cli_map or {}"""

INJECT = """    gate_mode = ctx.get("gate_mode", "cli")
    cli_map = cli_map or {}

    # ---- AUTO mode: unattended — resolve to the accept default, no prompt/poll ----
    if gate_mode == "auto":
        auto_map = ctx.get("auto_decisions") or {}
        decision = auto_map.get(name)
        if decision not in options:
            decision = options[0]  # accept path is first for all real gates
        return decision"""


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return
    n = text.count(ANCHOR)
    if n != 1:
        sys.exit(f"FAIL: anchor found {n} times (expected 1) — refusing to patch.")
    new = text.replace(ANCHOR, INJECT, 1)
    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change — aborting.")
    backup = TARGET.with_suffix(TARGET.suffix + ".pre_auto")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n 'gate_mode == \"auto\"' shared/mission_control/gate_protocol.py")


if __name__ == "__main__":
    main()
