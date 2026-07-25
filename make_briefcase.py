#!/usr/bin/env python3
"""
make_briefcase.py -- build the fresh-Claude-session briefcase from the LIVE git tree.

Run on the LAPTOP from the repo root:
    python3 make_briefcase.py                    -> ~/Downloads/briefcase-<date>-<sha>.zip
    python3 make_briefcase.py --task lego        -> adds the Line F doc set
    python3 make_briefcase.py --extra path ...   -> adds arbitrary files (e.g. a film's -src CSV)

The zip contains a MANIFEST.txt with the commit hash, date, and dirty-tree warning, so
any Claude session can state exactly which commit it is working from. Upload the ONE
zip at session start; Claude unzips it in its container. Nothing else lives in the
project workspace -- that is how files go stale.

Stdlib only. ASCII only. Fails loudly on any missing file.
"""
import argparse
import datetime
import subprocess
import sys
import zipfile
from pathlib import Path

CORE = [
    # doctrine (4 -- the session's brain)
    "docs/_CANONICAL.md",
    "docs/__MASTER-WORKLOG.md",
    "docs/_BRIDGE.md",
    # tools + the oracle (4 -- read real code, verify against the real parser)
    "packaging/audit_script.py",
    "packaging/csv2script.py",
    "shared/parse_script.py",
    # the format authority (the GOLDEN PAIR -- fix these two paths if the first run reports them missing)
    "packaging/golden/bible-they-burned-v2.md",
    "packaging/golden/bible-they-burned-v2.thumb.json",
    # one worked example of the instrument layer (the only real CSV in existence + its compile inputs)
    "sacred-dawn/projects/chambers-of-the-dead-src/master.csv",
    "sacred-dawn/projects/chambers-of-the-dead-src/canon.json",
    "sacred-dawn/projects/chambers-of-the-dead-src/chambers-sections.json",
]

TASK_SETS = {
    "sacred-dawn": ["docs/channels/_Sacred-Dawn.md"],
    "architecture": [
        "docs/scorecards/METHUSELAH-scorecard.md",
        "sacred-dawn/projects/chambers-of-the-dead-src/architecture.md",
        "sacred-dawn/projects/chambers-of-the-dead-src/package.md",
    ],
    "audit": ["docs/_PACKAGING-AUDIT.md"],
    "packaging": ["packaging/packaging_push.py"],
    "strategy": ["docs/_STRATEGY.md"],
    "slate01": ["docs/slates/sacred-dawn-lineb-slate-01.md"],
    "lego": [
        "docs/_LEGO.md",
        "docs/_LEGO-PART-I.md",
        "docs/_LEGO-FEATURE-FILM.md",
        "docs/_MOTION-DOCTRINE.md",
        "docs/calibration-reference.md",
    ],
}


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=sorted(TASK_SETS), help="add a task doc set")
    ap.add_argument("--extra", nargs="*", default=[], help="additional files to include")
    ap.add_argument("--out-dir", default=str(Path.home() / "Downloads"))
    args = ap.parse_args()

    if not Path(".git").exists():
        print("ABORT: run from the repo root (no .git here)")
        sys.exit(1)

    sha = sh("git rev-parse --short HEAD") or "nogit"
    dirty = sh("git status --porcelain")
    date = datetime.date.today().isoformat()

    wanted = list(CORE) + (TASK_SETS.get(args.task, []) if args.task else []) + list(args.extra)

    files, missing = [], []
    for w in wanted:
        p = Path(w).resolve()
        if p.exists():
            files.append(p)
        else:
            missing.append(w)

    if missing:
        print("ABORT: %d file(s) missing -- fix the manifest or the tree first:" % len(missing))
        for m in missing:
            print("  MISSING  " + m)
        sys.exit(1)

    out = Path(args.out_dir) / ("briefcase-%s-%s.zip" % (date, sha))
    manifest_lines = [
        "BRIEFCASE MANIFEST",
        "built: %s" % datetime.datetime.now().isoformat(timespec="seconds"),
        "commit: %s" % sha,
        "dirty tree: %s" % ("YES -- uncommitted changes present, contents may be ahead of git:" if dirty else "no (tree clean, contents == commit)"),
    ]
    if dirty:
        manifest_lines += ["  " + l for l in dirty.split("\n")]
    manifest_lines.append("")
    manifest_lines.append("files (%d):" % len(files))

    repo = Path.cwd().resolve()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            arc = str(f.relative_to(repo)) if str(f).startswith(str(repo)) else f.name
            z.write(f, arc)
            manifest_lines.append("  " + arc)
        z.writestr("MANIFEST.txt", "\n".join(manifest_lines) + "\n")

    print("briefcase -> %s" % out)
    print("commit %s | %d files | dirty: %s" % (sha, len(files), "YES" if dirty else "no"))
    print("Upload this ONE zip at session start. Claude reads MANIFEST.txt first.")


if __name__ == "__main__":
    main()
