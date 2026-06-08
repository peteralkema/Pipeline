"""
patch_modea_gate_buildpage.py — fix the Mode A gate's STEP 1 instructions.

Root cause: serve_review.py refuses to start unless review.html already exists,
but that file is built by make_review_page.py, which the gate never told the
operator to run. Result: blank page / "server didn't start".

This patch inserts the make_review_page.py build line immediately above the
serve_review.py line inside STEP 1 of modea_leg.py, so the gate prints a
foolproof build-then-serve block.

Idempotent: if the file is already patched, it does nothing and exits 0.
Safe: if the exact anchor is not found verbatim, it refuses to touch the file.

Run on LAPTOP from repo root:
    python shared/patch_modea_gate_buildpage.py
Then: git pull --no-edit && git add shared/modea_leg.py && git commit && git push
Then on BOX: git pull --no-edit
"""
import sys
from pathlib import Path

PATH = Path("shared/modea_leg.py")

ANCHOR = (
    "        source ~/venvs/pipeline/bin/activate\n"
    "        python {os.path.join(shared, 'serve_review.py')} --project {engine_project} --port {port}"
)

REPLACEMENT = (
    "        source ~/venvs/pipeline/bin/activate\n"
    "        python {os.path.join(shared, 'make_review_page.py')} --project {engine_project}\n"
    "        python {os.path.join(shared, 'serve_review.py')} --project {engine_project} --port {port}"
)

MARKER = "make_review_page.py')} --project {engine_project}"


def main():
    if not PATH.exists():
        sys.exit(f"!! {PATH} not found — run from repo root (~/Projects/Pipeline).")

    src = PATH.read_text()

    if MARKER in src:
        print("Already patched — make_review_page build line present. No change.")
        return

    count = src.count(ANCHOR)
    if count == 0:
        sys.exit("!! STEP 1 anchor not found verbatim — NOT patching. "
                 "Inspect shared/modea_leg.py around line 194.")
    if count > 1:
        sys.exit(f"!! anchor found {count} times — ambiguous, NOT patching. Inspect manually.")

    patched = src.replace(ANCHOR, REPLACEMENT, 1)

    if MARKER not in patched or patched.count("serve_review.py')} --project {engine_project}") != 1:
        sys.exit("!! post-patch sanity check failed — file NOT written.")

    PATH.write_text(patched)
    print("Patched shared/modea_leg.py — STEP 1 now builds the page before serving.")
    print("Verify with:  grep -n \"make_review_page\\|serve_review\" shared/modea_leg.py")


if __name__ == "__main__":
    main()
