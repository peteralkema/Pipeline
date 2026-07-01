#!/usr/bin/env python3
"""_QQrew.md §12: remove break #5 (flat-cel). The channel does NOT break from
cinematic style — it SHARES semi-realistic fidelity with Final Hours and
differentiates on register (bright vs dread) + recurring cast (crew vs faceless).
Flat-cel was never the moat.

Idempotent: anchors on the exact break #5 line.
"""
import shutil, sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "docs" / "_QQrew.md"
if not DOC.exists():
    DOC = Path(__file__).resolve().parent.parent / "shared" / "docs" / "_QQrew.md"

OLD = "5. **Photoreal cinematic style** → **flat-cel illustration.**"
NEW = ("5. **Photoreal cinematic style** → ~~flat-cel illustration~~ **NO LONGER A "
       "BREAK (reversed 01 Jul, §4).** QQrew SHARES semi-realistic cinematic "
       "FIDELITY with Final Hours; it differs on REGISTER (bright/funky/high-key "
       "vs dread/candlelit) and CAST (recurring crew vs faceless). The moat is "
       "register + cast, never the art style. Flat-cel was an over-correction "
       "that read as a kids' webcomic.")

def main():
    if not DOC.exists():
        print(f"ERROR: {DOC} not found."); return 1
    t = DOC.read_text()
    if "NO LONGER A BREAK (reversed 01 Jul" in t:
        print("Already patched (§12 #5 shows reversal). No-op."); return 0
    if OLD not in t:
        print("ERROR: §12 break #5 line not found verbatim. Aborting."); return 1
    shutil.copy2(DOC, DOC.with_suffix(".md.bak_s12"))
    DOC.write_text(t.replace(OLD, NEW))
    print("OK §12 break #5 (flat-cel) marked no-longer-a-break.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
