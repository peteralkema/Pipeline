#!/usr/bin/env python3
"""
review — point the always-on review server at a project and print ONE clickable URL.

The gate calls this. It does the three things that used to be manual:
  1. builds review.html for the project (make_review_page.py)
  2. repoints the stable symlink ~/Pipeline/.review_current -> the project dir
  3. restarts the user service so the server picks up the new project (no sudo)
Then prints the single URL to click. No tunnel, no localhost, no path typing.

The server is a *user* systemd service (systemctl --user) so no sudo is ever needed in
this hot path. The project symlink is what lets one boot-time service follow whatever
episode you're on.

Usage (the gate runs this for you; you can also run it by hand):
    python shared/review.py --project final-hours/projects/gustloff/modea

Env knobs (sane defaults):
    REVIEW_HOST_IP  default 116.202.18.68   (printed in the URL)
    REVIEW_PORT     default 8001
    REVIEW_KEY      default fh2026
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # ~/Pipeline
SYMLINK = REPO / ".review_current"
HOST_IP = os.environ.get("REVIEW_HOST_IP", "116.202.18.68")
PORT = os.environ.get("REVIEW_PORT", "8001")
KEY = os.environ.get("REVIEW_KEY", "fh2026")
PYTHON = "/home/peter/venvs/pipeline/bin/python"


def _run(cmd, **kw):
    return subprocess.run(cmd, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True,
                    help="project modea dir, e.g. final-hours/projects/gustloff/modea")
    ap.add_argument("--no-build", action="store_true",
                    help="skip make_review_page (page already built)")
    args = ap.parse_args()

    project = (REPO / args.project).resolve() if not Path(args.project).is_absolute() \
        else Path(args.project).resolve()

    if not project.is_dir():
        sys.exit(f"ERROR: project dir not found: {project}")
    # containment guard
    if not str(project).startswith(str(REPO)):
        sys.exit(f"ERROR: project must live under {REPO}")

    # 1) build the review page (unless told not to)
    if not args.no_build:
        r = _run([PYTHON, str(REPO / "shared" / "make_review_page.py"),
                  "--project", str(project)])
        if r.returncode != 0:
            sys.exit("ERROR: make_review_page.py failed — see output above.")

    # 2) repoint the stable symlink (atomic swap)
    tmp = REPO / ".review_current.tmp"
    if tmp.is_symlink() or tmp.exists():
        tmp.unlink()
    tmp.symlink_to(project)
    os.replace(tmp, SYMLINK)   # atomic

    # 3) restart the user service so the server re-resolves the symlink (no sudo)
    r = _run(["systemctl", "--user", "restart", "review.service"])
    if r.returncode != 0:
        print("WARN: could not restart review.service via systemctl --user.")
        print("      Is the service installed + enabled? (one-time setup, see runbook)")
        print("      Falling back to printing the URL anyway.")

    # done — print the one thing the human needs
    url = f"http://{HOST_IP}:{PORT}/?key={KEY}"
    print()
    print("  ┌─ STILLS READY ──────────────────────────────────────────────┐")
    print(f"  │  Click:  {url}")
    print(f"  │  Project: {project.relative_to(REPO)}")
    print("  │  Review top→bottom. Reject + note any spell-breakers, then")
    print("  │  come back here and type:  go")
    print("  └─────────────────────────────────────────────────────────────┘")
    print()


if __name__ == "__main__":
    main()
