#!/usr/bin/env python3
"""Change the Skeptic canon tag's expression from flat/pouty to bright-engaged.

"dry deadpan expression" renders her bored and pouty on every reference /edit
beat (the canon tag, not the style_suffix, controls her face — /edit beats
bypass the suffix). Swap to a lively-but-not-goofy expression. Identity words
(blonde, tan jacket, gold necklaces) untouched.

Idempotent: matches the exact 18-word tag; no-ops if already updated.
"""
import json, shutil, sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "qqrew" / "channel.json"

OLD = ("late-twenties woman, blonde tousled shoulder-length hair, tan camel "
       "jacket over white tee, layered gold necklaces, dry deadpan expression")

NEW = ("late-twenties woman, blonde tousled shoulder-length hair, tan camel "
       "jacket over white tee, layered gold necklaces, bright engaged "
       "expression with a warm easy half-smile, sharp and lively")


def main() -> int:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found."); return 1
    cfg = json.loads(TARGET.read_text())
    cur = cfg.get("base_canon", {}).get("skeptic", "")
    if cur == NEW:
        print("Already patched (bright expression). No-op."); return 0
    if cur != OLD:
        print("ERROR: current skeptic canon does not match the expected 18-word tag.")
        print(f"Found: {cur}")
        print("Aborting."); return 1
    cfg["base_canon"]["skeptic"] = NEW
    backup = TARGET.with_suffix(".json.bak_skeptic_expr")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(TARGET.read_text())
    print(f"OK skeptic expression updated (backup: {backup.name})")
    print(f"now: {NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
