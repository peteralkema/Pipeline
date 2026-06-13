#!/usr/bin/env python3
"""
patch_stills_skip_existing.py — make the stills phase resume-safe.

WHY
  cmd_finish's animate loop already skips clips that exist on disk
  (`if clip.exists() and not args.force`). cmd_stills had NO equivalent guard,
  so a re-launched run re-spends fal on EVERY still already rendered
  (~$0.03 each → ~$2.60 for an 87-beat film). This adds the same skip-existing
  guard to the stills loop, plus a `--force` flag on the `stills` subparser to
  override it, mirroring `finish --force`.

  Effect: after a clean Stop at the stills gate, clicking Launch again skips
  every still already on disk and only renders the missing ones — "resume" with
  zero extra build, no state store, and no wasted spend.

DISCIPLINE
  Idempotent. Verifies each anchor exists exactly once before writing; refuses
  to half-apply; backs up to a .pre_skipstills sidecar; re-compiles the result
  and rolls back on any failure. Unique marker comment (not a substring of any
  other line) so a re-run is a clean no-op — avoids the substring false-positive
  trap. Run from the repo root on the LAPTOP, then commit/push, then pull on box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/recreation_pipeline.py")
MARKER = "# resume-safe: skip stills already on disk"

LOOP_OLD = '''    print(f"\\nGenerating {len(shots)} stills with {IMAGE_MODEL}...")
    for s in shots:
        out = p["stills"] / f"shot_{s['index']:03d}.png"
        print(f"  [{s['index']}/{len(shots)}] {s['image_prompt'][:60]}...")
        generate_still(s["image_prompt"], out)
'''

LOOP_NEW = '''    print(f"\\nGenerating {len(shots)} stills with {IMAGE_MODEL}...")
    force = bool(getattr(args, "force", False))
    for s in shots:
        out = p["stills"] / f"shot_{s['index']:03d}.png"
        if out.exists() and not force:  # resume-safe: skip stills already on disk
            print(f"  [{s['index']}/{len(shots)}] already done, skipping")
            continue
        print(f"  [{s['index']}/{len(shots)}] {s['image_prompt'][:60]}...")
        generate_still(s["image_prompt"], out)
'''

ARG_OLD = '''    a.add_argument("--storyboard-only", action="store_true", help="generate storyboard JSON and stop (no image generation)")
    a.set_defaults(func=cmd_stills)
'''

ARG_NEW = '''    a.add_argument("--storyboard-only", action="store_true", help="generate storyboard JSON and stop (no image generation)")
    a.add_argument("--force", action="store_true", help="re-generate stills even if they already exist on disk")
    a.set_defaults(func=cmd_stills)
'''

VERIFY_SUBSTR = '"--force", action="store_true", help="re-generate stills'


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    # Verify each anchor exists EXACTLY once before touching anything.
    for label, anchor in (("stills loop", LOOP_OLD), ("stills subparser", ARG_OLD)):
        n = src.count(anchor)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Suspect a skipped predecessor patch or an out-of-sync box.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(LOOP_OLD, LOOP_NEW).replace(ARG_OLD, ARG_NEW)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_skipstills")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    # Post-write: confirm both edits landed AND the file still compiles; else roll back.
    check = TARGET.read_text()
    if MARKER not in check or VERIFY_SUBSTR not in check:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup}")
    print("   1) stills loop now skips existing stills unless --force")
    print("   2) `stills` subparser gained --force")
    print("Verify:  grep -n 'resume-safe: skip stills' shared/recreation_pipeline.py")


if __name__ == "__main__":
    main()
