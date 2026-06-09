#!/usr/bin/env python3
"""
patch_decade_look_phase1.py — wire per-job decade look into the STILL layer.

Idempotent. Two edits:
  1. recreation_pipeline.py: in generate_still(), resolve the look from the
     still's own out_path (walking up to a project look.json) instead of reading
     channel.json's style_suffix directly. No signature change, no call-site edits
     — the resolver self-discovers the project, mirroring load_channel_config.
  2. parse_script.py: add 'look' and 'era' to HEADER_KEYS so a `look:` header
     field parses as a top-level scalar (convenience carrier; orchestrator can
     later write look.json from it). Single-line, no other header behaviour changes.

Backward-compatible: a project with no look.json renders byte-for-byte as today
(resolve_look falls back to channel_config["style_suffix"]).

PREREQUISITE: copy look_resolver.py into shared/ first (the orchestrate/idempotent
deploy step), then run this on the box from the repo root.

Run:  python shared/patch_decade_look_phase1.py
"""

import sys
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RP = REPO / "shared" / "recreation_pipeline.py"
PS = REPO / "shared" / "parse_script.py"

OLD_STILL = '''    config = load_channel_config(strict=False)
    style_suffix = config["style_suffix"]
    people = rb.get("people_directive", "")
    full_prompt = f"{image_prompt}, {people}, {style_suffix}" if people else f"{image_prompt}, {style_suffix}"'''

NEW_STILL = '''    config = load_channel_config(strict=False)
    from look_resolver import resolve_look
    style_suffix = resolve_look(out_path, config)["style_suffix"]
    people = rb.get("people_directive", "")
    full_prompt = f"{image_prompt}, {people}, {style_suffix}" if people else f"{image_prompt}, {style_suffix}"'''

OLD_KEYS = 'HEADER_KEYS = {"channel", "title", "description", "tags"}'
NEW_KEYS = 'HEADER_KEYS = {"channel", "title", "description", "tags", "look", "era"}'


def patch_file(path: Path, old: str, new: str, label: str) -> bool:
    src = path.read_text(encoding="utf-8")
    if new in src:
        print(f"  [skip] {label}: already patched.")
        return True
    if old not in src:
        print(f"  [FAIL] {label}: anchor not found. Aborting (no change written).")
        print(f"         expected to find:\n{old}")
        return False
    if src.count(old) != 1:
        print(f"  [FAIL] {label}: anchor found {src.count(old)}x (expected 1). Aborting.")
        return False
    bak = path.with_suffix(path.suffix + ".pre_decade_look")
    shutil.copy2(path, bak)
    path.write_text(src.replace(old, new, 1), encoding="utf-8")
    print(f"  [ok]   {label}: patched (backup -> {bak.name}).")
    return True


def main():
    if not RP.exists() or not PS.exists():
        print(f"ERROR: run from repo root; expected {RP} and {PS}.")
        sys.exit(1)

    print("Patching decade-look Phase 1 (still layer)...")
    ok1 = patch_file(RP, OLD_STILL, NEW_STILL, "recreation_pipeline.generate_still")
    ok2 = patch_file(PS, OLD_KEYS, NEW_KEYS, "parse_script HEADER_KEYS")

    # verify look_resolver is importable from shared/
    lr = REPO / "shared" / "look_resolver.py"
    if not lr.exists():
        print(f"  [WARN] {lr} not found — copy look_resolver.py into shared/ before rendering.")

    print()
    if ok1 and ok2:
        print("DONE. Verify:")
        print('  grep -n "resolve_look" shared/recreation_pipeline.py')
        print('  grep -n "HEADER_KEYS" shared/parse_script.py')
        print("  python -c \"import sys; sys.path.insert(0,'shared'); "
              "import look_resolver; print(look_resolver.get_look('2000s')['style_suffix'][:50])\"")
    else:
        print("INCOMPLETE — see [FAIL] above. No partial render; fix anchors and re-run.")
        sys.exit(2)


if __name__ == "__main__":
    main()
