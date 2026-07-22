#!/usr/bin/env python3
"""
patch_lego_wc_tags.py -- make wc() ignore TTS markup.

WHY
  wc() is the single word counter behind calibrate's stream pointer, the block
  word totals, the film audit and the <=55-word runaway gate. It currently keeps
  any token containing a letter or digit, so an Inworld break tag counts as real
  words:

      <break time="3s"/>        -> 2 phantom words
      <break time="1.5s" />     -> 3 phantom words (note the space)

  Whisper emits nothing for a break, so calibrate's pointer advances too far and
  NEVER RECOVERS -- every beat after the tag reads the wrong timestamps while
  still looking plausible. Same family as the em-dash lesson: .split() counting a
  token that is not a spoken word.

FIX
  Strip anything between < and > BEFORE splitting, rather than filtering tokens
  after. Token filtering misses attributes in the spaced form, because
  time="1.5s" carries no angle bracket. Stripping handles every spelling and any
  future markup.

  Run from anywhere; edits ~/Pipeline/build_lego.py in place.
  Idempotent. Verifies its anchor, backs up to build_lego.py.pre_wc_tags,
  compiles before writing, self-tests after.
"""
import py_compile
import re
import shutil
import sys
import tempfile
from pathlib import Path

TARGET = Path.home() / "Pipeline" / "build_lego.py"

ANCHOR = (
    'def wc(s: str) -> int:\n'
    '    """Standalone punctuation is not a word (em-dashes are prosody, not tokens)."""\n'
    '    return len([t for t in (s or "").split() if re.search(r"[A-Za-z0-9]", t)])\n'
)

REPLACEMENT = (
    'def wc(s: str) -> int:\n'
    '    """Standalone punctuation is not a word (em-dashes are prosody, not tokens).\n'
    '    TTS markup is an instruction, never narration: anything between < and > is\n'
    '    stripped before splitting. Whisper emits no words for a break tag, so\n'
    '    counting one would advance calibrate\'s stream pointer and desync every\n'
    '    downstream beat. Stripping (not token-filtering) is required because the\n'
    '    spaced form <break time="1.5s" /> leaves an attribute carrying no bracket."""\n'
    '    s = re.sub(r"<[^>]*>", " ", s or "")\n'
    '    return len([t for t in s.split() if re.search(r"[A-Za-z0-9]", t)])\n'
)

MARKER = "TTS markup is an instruction, never narration"


def main() -> int:
    if not TARGET.exists():
        print("FAIL: %s not found" % TARGET)
        return 1

    src = TARGET.read_text()

    if MARKER in src:
        print("already applied -- no change")
        return 0

    n = src.count(ANCHOR)
    if n != 1:
        print("FAIL: anchor matched %d times, expected 1" % n)
        print("      wc() has changed. Re-read it before patching:")
        print("      grep -n 'def wc' -A 4 %s" % TARGET)
        return 1

    out = src.replace(ANCHOR, REPLACEMENT)

    tmp = Path(tempfile.gettempdir()) / "build_lego.patched.py"
    tmp.write_text(out)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as exc:
        print("FAIL: patched file does not compile -- nothing written")
        print(exc)
        return 1

    backup = TARGET.with_suffix(".py.pre_wc_tags")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(out)
    print("backed up  -> %s" % backup)
    print("patched    -> %s" % TARGET)

    ns = {}
    exec("import re\n" + REPLACEMENT, {"re": re}, ns)
    wc = ns["wc"]
    checks = [
        ("At the top he sets the stone down on bare rock and says nothing.", 14),
        ('At the top he sets the stone down. <break time="3s"/>', 8),
        ('Then... <break time="1.5s" /> light appeared.', 3),
        ("A word -- and another.", 4),
        ('<break time="1.5s" />', 0),
        ("", 0),
    ]
    ok = True
    print("\nself-test:")
    for text, want in checks:
        got = wc(text)
        if got != want:
            ok = False
        print("  %s %2d (want %2d)  %r" % ("ok " if got == want else "BAD",
                                           got, want, text[:50]))

    if not ok:
        print("\nSELF-TEST FAILED -- restore with:")
        print("  cp %s %s" % (backup, TARGET))
        return 1

    print("\nall good. Word counts are UNCHANGED on tag-free narration, so the")
    print("existing calibrate result stays valid. NEXT (optional, confirms no drift):")
    print("  cd ~/Pipeline/sacred-dawn/projects")
    print("  python ~/Pipeline/build_lego.py calibrate --project methuselah "
          "methuselah/voiceover.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
