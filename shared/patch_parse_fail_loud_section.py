#!/usr/bin/env python3
"""
patch_parse_fail_loud_section.py

Make parse_script.py FAIL LOUD when a script body has no recognized section
header (## COLD OPEN / ## PART / ## ACT).

Root cause this fixes (the soak-test header-read-aloud bug, 21 June):
  - A typo'd / non-standard marker like "## OPENING" is not recognized.
  - parse_header() never terminates -> it slurps the entire body into the
    last header key ("tags").
  - parse_script()'s body-start scan finds no "## COLD OPEN|PART", so `start`
    stays 0 and the body parse begins at line 0 -> the key:value header lines
    (channel:/title:/description:) are parsed AS beat-one narration and read
    aloud by Inworld.

The guard: if the body-start scan matches nothing, halt with a clear message
naming the headings that WERE found and the valid markers. Also folds ACT into
the scan so it matches the set parse_header already accepts. A valid script
always opens with COLD OPEN / PART / ACT, so this cannot false-positive on the
existing working scripts.

Idempotent: refuses to half-apply, backs up to a .pre_* sidecar, no-ops on
re-run via a sentinel. Pure ASCII. Run on the LAPTOP, then commit -> push ->
box git pull.
"""

import sys
import py_compile
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "parse_script.py"
SENTINEL = "PARSE HALTED: no recognized section header"

ANCHOR = '''    # Parse only the body: from the first COLD OPEN / PART heading...
    start = 0
    for i, ln in enumerate(lines):
        if re.match(r"^\\s*##\\s+(COLD OPEN|PART )", ln, re.IGNORECASE):
            start = i
            break
'''

REPLACEMENT = '''    # Parse only the body: from the first COLD OPEN / PART / ACT heading...
    # FAIL LOUD (guard, 21 Jun): a valid script body MUST begin with a recognized
    # section header. A non-standard marker (e.g. "## OPENING") otherwise causes
    # parse_header to slurp the body into the last key AND this scan to default
    # start=0, folding the key:value header into beat-one narration -> the
    # narrator reads the metadata aloud. Halt instead of producing bad beats.
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^\\s*##\\s+(COLD OPEN|PART |ACT)", ln, re.IGNORECASE):
            start = i
            break
    if start is None:
        found = [ln.strip() for ln in lines if re.match(r"^\\s*##\\s+\\S", ln)]
        sys.stderr.write(
            "\\nPARSE HALTED: no recognized section header found.\\n"
            "  A script body must begin with '## COLD OPEN' (or '## PART ...' / '## ACT ...').\\n"
            "  Headings found instead: " + (str(found) if found else "(none)") + "\\n"
            "  Rename the section marker to a recognized one. The key:value header\\n"
            "  block was about to be parsed as narration and read aloud by the TTS.\\n\\n"
        )
        raise SystemExit(2)
'''


def main():
    if not TARGET.exists():
        sys.exit("ERROR: parse_script.py not found next to this patch.")

    src = TARGET.read_text(encoding="utf-8")

    if SENTINEL in src:
        print("Already applied (sentinel present). No-op.")
        return

    n = src.count(ANCHOR)
    if n != 1:
        sys.exit(
            "ERROR: anchor found {0} times (expected exactly 1). "
            "Refusing to patch. The body-start scan block may have changed; "
            "re-read parse_script.py before patching.".format(n)
        )

    new = src.replace(ANCHOR, REPLACEMENT)

    backup = TARGET.with_suffix(".py.pre_fail_loud_section")
    backup.write_text(src, encoding="utf-8")

    TARGET.write_text(new, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        TARGET.write_text(src, encoding="utf-8")
        sys.exit("ERROR: py_compile failed, reverted.\\n{0}".format(e))

    print("OK patched parse_script.py (fail-loud on missing section header).")
    print("  backup -> {0}".format(backup.name))
    print("  sentinel -> {0!r}".format(SENTINEL))


if __name__ == "__main__":
    main()
