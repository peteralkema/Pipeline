#!/usr/bin/env python3
"""Cut the Skeptic base_canon from an 89-word photoreal portrait to a ~20-word
identity tag (doctrine §6a).

The long canon is portrait-bait AND realism-bait ("softly feminine", "capable
presence", "never masculine") and, per §6a, drowns the scene when it expands into
a text-to-image prompt. In the current reference-render config, Skeptic beats
render via /edit from skeptic_ref.png and bypass this canon -- BUT if a Skeptic
beat ever falls through to the flux fallback (built this session), this canon is
what would inject a photoreal supermodel portrait. Cutting it to an identity-only
tag makes that fallback safe and matches doctrine.

Driver canon is left untouched (shorter, less realism-coded, and Driver isn't in
this episode).

Idempotent: matches the exact current skeptic string, backs up, validates JSON,
no-ops if already the short tag.
"""
import json
import shutil
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "qqrew" / "channel.json"

OLD = ("a softly feminine young woman, slim athletic build, loose tousled "
       "shoulder-length blonde hair falling past her shoulders, an open-collar "
       "tan camel jacket over a plain white crew-neck t-shirt with thin layered "
       "gold necklaces, a feminine and capable presence, alert and curious with "
       "a dry faintly-amused deadpan expression, engaged and quietly unconvinced, "
       "never tense, never bored, never masculine")

NEW = ("late-twenties woman, blonde tousled shoulder-length hair, tan camel "
       "jacket over white tee, layered gold necklaces, dry deadpan expression")


def main() -> int:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found. Run from shared/ with qqrew/ sibling. Aborting.")
        return 1

    raw = TARGET.read_text()
    cfg = json.loads(raw)  # validate it parses before we touch it

    cur = cfg.get("base_canon", {}).get("skeptic", "")
    if cur == NEW:
        print("Already patched (skeptic canon is the short tag). No-op.")
        return 0
    if cur != OLD:
        print("ERROR: current skeptic canon does not match the expected 89-word string.")
        print(f"Found: {cur[:80]}...")
        print("Aborting -- not overwriting an unexpected value.")
        return 1

    cfg["base_canon"]["skeptic"] = NEW

    backup = TARGET.with_suffix(".json.bak_skeptic_canon")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(json.dumps(cfg, indent=2) + "\n")

    # re-read to confirm valid JSON landed
    json.loads(TARGET.read_text())
    print(f"OK patched {TARGET.name} (backup: {backup.name})")
    print(f"skeptic canon now ({len(NEW.split())} words): {NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
