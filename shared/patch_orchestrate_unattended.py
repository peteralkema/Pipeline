#!/usr/bin/env python3
"""
patch_orchestrate_unattended.py — add --unattended to the orchestrator.

Three small edits to shared/orchestrate.py:
  1. Add "auto" to the --gate-mode choices (so gate_mode can be 'auto').
  2. Add an --unattended flag.
  3. Right after args are parsed in main(), if --unattended is set, force:
        args.gate_mode = "auto"   (gates auto-resolve to accept; see gate_protocol)
        args.live      = True     (skip the dry/live kickoff prompt)
        args.log       = args.log or "normal"  (skip the verbosity kickoff prompt)
     so kickoff_prompt() bypasses BOTH input() calls and no gate ever blocks.

Depends on patch_gate_auto.py (the 'auto' branch in await_gate). Apply that first.

Idempotent (sentinel: '--unattended'), backs up to .pre_unattended, verifies anchors.

Run on LAPTOP:  python3 shared/patch_orchestrate_unattended.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orchestrate.py"
SENTINEL = "--unattended"

# 1) widen gate-mode choices + add the flag (anchor on the existing --gate-mode block)
ANCHOR_ARGS = '''    ap.add_argument("--gate-mode", choices=["cli", "job"], default="cli",
                    help="cli = terminal input() gates (default, unchanged); "
                         "job = drive gates via the job record (Mission Control)")'''
NEW_ARGS = '''    ap.add_argument("--gate-mode", choices=["cli", "job", "auto"], default="cli",
                    help="cli = terminal input() gates (default, unchanged); "
                         "job = drive gates via the job record (Mission Control); "
                         "auto = unattended, gates auto-resolve to accept")
    ap.add_argument("--unattended", action="store_true",
                    help="fully unattended: forces gate-mode=auto + live + normal "
                         "verbosity, so no gate or kickoff prompt ever blocks (batch runs)")'''

# 3) force the flags right after parse_args() in main(). Anchor on the def main() line
#    and inject as the first statements. We find 'def main():' and the next line.
ANCHOR_MAIN = "def main():"


def _inject_after_parse(text: str) -> str:
    """Insert the unattended-forcing block immediately after `args = parse_args()`
    inside main(). If that exact call isn't found, fall back to top-of-main."""
    needle = "args = parse_args()"
    if needle in text:
        block = (needle + "\n"
                 "    if getattr(args, \"unattended\", False):\n"
                 "        args.gate_mode = \"auto\"\n"
                 "        args.live = True\n"
                 "        args.log = args.log or \"normal\"\n")
        return text.replace(needle, block, 1)
    return text


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return

    for label, anchor in (("ARGS", ANCHOR_ARGS),):
        if text.count(anchor) != 1:
            sys.exit(f"FAIL: {label} anchor found {text.count(anchor)} times (expected 1).")

    if "args = parse_args()" not in text:
        sys.exit("FAIL: could not find 'args = parse_args()' to inject the unattended block. "
                 "Paste the first ~10 lines of main() and I'll adjust the anchor.")

    new = text.replace(ANCHOR_ARGS, NEW_ARGS, 1)
    new = _inject_after_parse(new)

    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change — aborting.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_unattended")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n 'unattended' shared/orchestrate.py")


if __name__ == "__main__":
    main()
