#!/usr/bin/env python3
"""
patch_thumbnail_nobreak.py — stop the thumbnail overlay ever splitting a word.
_fit_text wraps via textwrap.wrap() with no break flags, so a long word (EVERYTHING)
gets chopped mid-word at the char limit. Add break_long_words=False + break_on_hyphens=False
to both wrap calls; the existing shrink-to-fit loop then shrinks the font until the
unbroken word fits the box. Idempotent (sentinel), anchor-verified.

Run on LAPTOP:  python3 shared/patch_thumbnail_nobreak.py
"""
import sys
from pathlib import Path

T = Path(__file__).resolve().parent / "make_thumbnail.py"
SENTINEL = "break_long_words=False"

EDITS = [
 ("main wrap (209)",
  "            lines = textwrap.wrap(text, width=wrap_chars) or [text]",
  "            lines = textwrap.wrap(text, width=wrap_chars, break_long_words=False, break_on_hyphens=False) or [text]"),
 ("fallback wrap (216)",
  "    return _load_font(40, cfg), textwrap.wrap(text, width=20) or [text]",
  "    return _load_font(40, cfg), textwrap.wrap(text, width=20, break_long_words=False, break_on_hyphens=False) or [text]"),
]

def main():
    if not T.exists(): sys.exit(f"FAIL: {T} not found.")
    text = T.read_text()
    original = text
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present)."); return
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            sys.exit(f"FAIL: anchor '{label}' found {n} times (expected 1) — refusing.")
    for label, old, new in EDITS:
        text = text.replace(old, new, 1)
    bak = T.with_suffix(T.suffix + ".pre_nobreak")
    if not bak.exists(): bak.write_text(original)
    T.write_text(text)
    print(f"OK: patched make_thumbnail.py ({len(EDITS)} edits). No word will be split.")

if __name__ == "__main__":
    main()
