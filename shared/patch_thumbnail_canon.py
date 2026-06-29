#!/usr/bin/env python3
"""
patch_thumbnail_canon.py  -  two fixes to shared/select_thumbnail_still.py

FIX 1 (the "repeatable thumbnail" unlock):
  The thumbnail --subject is passed VERBATIM to Flux. So a subject containing a
  canon tag like {driver} ships raw to the image model instead of expanding to the
  locked character tokens. This patch resolves {tags} in --subject against the
  channel's base_canon BEFORE the Flux prompt is built. After this, a thumbnail
  subject can say "{driver}, shrugging, surprised, on the right..." and inherit the
  exact same character lock the video stills use. One definition, two surfaces.

FIX 2 (portfolio-wide quality bug found 29 Jun):
  select_best() hardcodes a 2-candidate judge: it only shows candidates[:2] to
  Sonnet and only accepts winner in (1, 2). So --candidates 3 (or more) renders and
  PAYS for the extra candidates but never judges them, and a correct {"winner": 3}
  is rejected as out-of-range -> silent fallback to candidate 1. This patch makes
  the judge show ALL candidates and accept winner in 1..N.

Idempotent (sentinel checks per edit). Pure ASCII. Anchor-verified: refuses to write
if any anchor is missing or ambiguous. Run on the LAPTOP, then commit -> push -> box
pull -> re-run to verify idempotency.
"""

import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "select_thumbnail_still.py"


# ---- FIX 1: a canon resolver + its call site ------------------------------------

# Inserted helper (sentinel: the def line). Mirrors recreation_pipeline._expand_canon
# semantics: replace {tag} with channel base_canon[tag]; leave unknown tags untouched
# (a thumbnail must never hard-halt an unattended batch -- the whole file's design rule).
RESOLVER_DEF = '''
def _resolve_subject_canon(subject: str, channel_cfg: dict) -> str:
    """Expand {tag} references in the thumbnail subject against the channel's
    base_canon, so a subject can reference recurring characters (e.g. {driver}) and
    inherit the locked tokens -- the same canon the video stills use. Unknown tags
    are left as-is (never halt an unattended thumbnail run)."""
    import re as _re
    canon = (channel_cfg.get("base_canon") or {})
    if not canon:
        return subject
    pattern = _re.compile(r"\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}")
    def _sub(m):
        key = m.group(1)
        return canon.get(key, m.group(0))
    resolved = pattern.sub(_sub, subject)
    if resolved != subject:
        print("   thumbnail subject: canon tags resolved")
    return resolved

'''

# Anchor for inserting the helper: just before _build_prompt's definition.
RESOLVER_ANCHOR = 'def _build_prompt(channel_cfg: dict, subject: str) -> str:'

# Call-site: in main(), resolve the subject right after channel_cfg is loaded and
# before prompt is built. Anchor on the exact existing line.
CALLSITE_ANCHOR = '    prompt = _build_prompt(channel_cfg, args.subject)'
CALLSITE_NEW = (
    '    resolved_subject = _resolve_subject_canon(args.subject, channel_cfg)\n'
    '    prompt = _build_prompt(channel_cfg, resolved_subject)'
)


# ---- FIX 2: un-hardcode the 2-candidate judge -----------------------------------

# 2a: show ALL candidates to the judge, not candidates[:2].
JUDGE_LOOP_OLD = '        for i, path in enumerate(candidates[:2], start=1):'
JUDGE_LOOP_NEW = '        for i, path in enumerate(candidates, start=1):'

# 2b: accept winner in 1..N instead of (1, 2). (The "<1 or 2>" text in the prompt is
# cosmetic model guidance and is left alone; the binding fix is this range check.)
JUDGE_RANGE_OLD = (
    "        if winner not in (1, 2):\n"
    "            return 1, f\"fallback: winner out of range ({winner})\""
)
JUDGE_RANGE_NEW = (
    "        if not (1 <= winner <= len(candidates)):\n"
    "            return 1, f\"fallback: winner out of range ({winner})\""
)


def _verify_anchor(text: str, anchor: str, label: str):
    n = text.count(anchor)
    if n == 0:
        sys.exit(f"ABORT: anchor for {label} NOT FOUND -- nothing written.\n  {anchor!r}")
    if n > 1:
        sys.exit(f"ABORT: anchor for {label} found {n}x (ambiguous) -- nothing written.")


def main():
    if not TARGET.exists():
        sys.exit(f"target not found: {TARGET}")
    src = TARGET.read_text()
    orig = src
    changed = []

    # ---- FIX 1a: helper ----
    if "_resolve_subject_canon" in src:
        print("skip: canon resolver already present")
    else:
        _verify_anchor(src, RESOLVER_ANCHOR, "resolver insert")
        src = src.replace(RESOLVER_ANCHOR, RESOLVER_DEF.lstrip("\n") + "\n" + RESOLVER_ANCHOR, 1)
        changed.append("canon resolver helper")

    # ---- FIX 1b: call site ----
    if "resolved_subject = _resolve_subject_canon" in src:
        print("skip: canon call-site already present")
    else:
        _verify_anchor(src, CALLSITE_ANCHOR, "canon call-site")
        src = src.replace(CALLSITE_ANCHOR, CALLSITE_NEW, 1)
        changed.append("canon call-site")

    # ---- FIX 2a: show all candidates ----
    if JUDGE_LOOP_NEW in src:
        print("skip: judge already shows all candidates")
    elif JUDGE_LOOP_OLD in src:
        _verify_anchor(src, JUDGE_LOOP_OLD, "judge loop")
        src = src.replace(JUDGE_LOOP_OLD, JUDGE_LOOP_NEW, 1)
        changed.append("judge shows all candidates")
    else:
        sys.exit("ABORT: judge loop anchor not found (neither old nor new form).")

    # ---- FIX 2c: range check ----
    if JUDGE_RANGE_NEW in src:
        print("skip: judge range check already 1..N")
    elif JUDGE_RANGE_OLD in src:
        _verify_anchor(src, JUDGE_RANGE_OLD, "judge range check")
        src = src.replace(JUDGE_RANGE_OLD, JUDGE_RANGE_NEW, 1)
        changed.append("judge range 1..N")
    else:
        sys.exit("ABORT: judge range-check anchor not found (neither old nor new form).")

    if src == orig:
        print("\nNo changes -- file already fully patched. Idempotent OK.")
        return

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_thumbcanon")
    if not backup.exists():
        backup.write_text(orig)
        print(f"backup -> {backup.name}")
    TARGET.write_text(src)
    print("patched:", ", ".join(changed))

    # compile check
    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("py_compile OK")
    except py_compile.PyCompileError as e:
        TARGET.write_text(orig)
        sys.exit(f"ABORT: patched file failed to compile, reverted.\n{e}")


if __name__ == "__main__":
    main()
