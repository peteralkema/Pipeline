"""
prop_stress_test.py -- stress-test the prop geometry doctrine at scale
======================================================================
Runs N props of deliberately varied shape through make_prop.py + make_thumbnail.py
against ONE fixed subject still, so the only variable is the prop. Tests whether the
geometry discipline (width cap, top anchor, square-ish rule) holds under adversarial
shapes -- including wide/tall props that WANT to break the layout.

Outputs <project>/stress/thumb_NN_slug.png for each, plus a stress_results.json log.
Reuses the existing thumbnail_still.png as the subject for every composite (does NOT
re-render the subject -- that is not what we are testing, and it saves fal spend).

The 10 test props: 5 square-ish (should be clean) + 5 shape-stress (must get caught
by the width cap, not collide with the subject).

Usage:
    python3 prop_stress_test.py --project crew-wip/projects/iceage1 --channel crew-wip
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# (slug, headline title, headline subtitle, prop subject, shape-class)
TESTS = [
    ("mammoth",   "YOU WOULDN'T LAST",  "ONE ICE AGE WINTER",   "a single woolly mammoth, side view, full body, shaggy brown fur and curved tusks, walking", "square"),
    ("skull",     "THEY ALL VANISHED",  "NOBODY KNOWS WHY",     "a single human skull, front view, clean and pale, slightly worn", "square"),
    ("longship",  "THE RAIDERS CAME",   "AT FIRST LIGHT",       "a long viking longship, full side profile, single row of shields, dragon prow, sail furled", "wide"),
    ("lighthouse","THE LIGHT WENT OUT",  "THEN THE SHIPS CAME",  "a tall thin lighthouse, full height, narrow tower, lamp at the top", "tall"),
    ("snake",     "ONE BITE",           "SIXTY SECONDS",        "a single coiled snake, compact spiral, head raised, scales detailed", "square"),
    ("pyramid",   "BUILT BY HAND",      "NOBODY KNOWS HOW",     "a single egyptian pyramid, three quarter view, sandstone blocks, desert base", "square"),
    ("sword",     "THE LAST KING",      "DIED HOLDING THIS",    "a single tall vertical sword, blade pointing up, ornate crossguard, standing upright", "tall_thin"),
    ("galleon",   "THE GOLD FLEET",     "NEVER ARRIVED",        "a full spanish galleon at sea, three tall masts with full sails, side profile, ornate hull", "mixed"),
    ("volcano",   "IT ERUPTED ONCE",    "AND ENDED A WORLD",    "a single erupting volcano, conical mountain, lava and ash plume rising, three quarter view", "square"),
    ("croc",      "OLDER THAN TREES",   "STILL HERE",           "a single crocodile, full body stretched out side view, long tail and snout, scaled hide", "very_wide"),
]


def run(cmd):
    print("   $ " + " ".join(cmd[:6]) + " ...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("   STDERR: " + (r.stderr or "")[-400:])
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(description="Prop geometry stress test")
    ap.add_argument("--project", required=True)
    ap.add_argument("--channel", default=None)
    ap.add_argument("--shared", default="shared", help="path to shared/ dir with the scripts")
    args = ap.parse_args()

    project = Path(args.project)
    shared = Path(args.shared)
    subject = project / "thumbnail_still.png"
    if not subject.exists():
        sys.exit("No thumbnail_still.png in project -- need the fixed subject still first.")

    stress = project / "stress"
    stress.mkdir(exist_ok=True)
    backup_subject = stress / "_subject_backup.png"
    shutil.copyfile(subject, backup_subject)

    results = []
    for i, (slug, title, subtitle, prop, shape) in enumerate(TESTS, start=1):
        print("[" + str(i) + "/" + str(len(TESTS)) + "] " + slug + " (" + shape + ")")

        prop_cmd = ["python3", str(shared / "make_prop.py"),
                    "--project", str(project), "--prop", prop]
        if args.channel:
            prop_cmd += ["--channel", args.channel]
        ok_prop = run(prop_cmd)

        out = stress / ("thumb_" + str(i).zfill(2) + "_" + slug + ".png")
        thumb_cmd = ["python3", str(shared / "make_thumbnail.py"),
                     "--project", str(project),
                     "--title", title, "--subtitle", subtitle,
                     "--out", str(out)]
        if args.channel:
            thumb_cmd += ["--channel", args.channel]
        ok_thumb = run(thumb_cmd)

        results.append({
            "n": i, "slug": slug, "shape": shape,
            "prop_ok": ok_prop, "thumb_ok": ok_thumb,
            "out": out.name if ok_thumb else None,
        })

    # restore the original subject still (props left their last render; harmless)
    shutil.copyfile(backup_subject, subject)

    (stress / "stress_results.json").write_text(json.dumps(results, indent=2))
    ok = sum(1 for r in results if r["thumb_ok"])
    print("")
    print("DONE: " + str(ok) + "/" + str(len(TESTS)) + " composited.")
    print("Outputs in " + str(stress) + " -- scp the folder and eyeball each for:")
    print("  1. prop stays in its corner, never crosses into the subject")
    print("  2. text readable, prop nested under subtitle")
    print("  3. on-brand (square props clean; wide/tall props shrunk, not sprawled)")


if __name__ == "__main__":
    main()
