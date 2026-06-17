#!/usr/bin/env python3
"""
patch_convergence_thumbnail.py — wire auto-thumbnail into the convergence leg.

Inserts a _maybe_thumbnail() step that runs in convergence BEFORE _maybe_upload():
if the project has a thumbnail.json spec, it generates N candidate stills
(select_thumbnail_still.py), lets Sonnet pick the best on the CTR job, overlays the
locked headline (make_thumbnail.py) -> <proj>/thumbnail.png, which upload_episode.py
already attaches.

Graceful + idempotent by design (must never break an unattended batch):
  - no thumbnail.json           -> skip, upload ships without a custom thumbnail
  - thumbnail.png already exists -> skip (no fal re-spend on re-runs)
  - any sub-step fails           -> warn, ship final_video.mp4 + upload untouched

Edits shared/convergence_leg.py in place. Verifies anchors exist exactly once,
backs up to convergence_leg.py.pre_thumbnail, refuses to half-apply.
Sentinel: '_maybe_thumbnail'.

Run on LAPTOP (never hand-edit the box):
    python3 shared/patch_convergence_thumbnail.py
    git add -A && git commit -m "convergence: auto-thumbnail before upload" && git push
  then on BOX:
    cd ~/Pipeline && git pull --no-edit
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "convergence_leg.py"
SENTINEL = "_maybe_thumbnail"

FUNC_ANCHOR = "def run_convergence_leg(ctx, modea=None):"

CALL_ANCHOR = (
    "    # ── PUBLISH (channel-agnostic upload; private by default) ──\n"
    "    _maybe_upload(ctx, proj, t, py, shared, dry)"
)
CALL_NEW = (
    "    # ── THUMBNAIL (auto-generate + Sonnet-select + overlay; graceful skip) ──\n"
    "    _maybe_thumbnail(ctx, proj, t, py, shared, dry)\n"
    "\n"
    "    # ── PUBLISH (channel-agnostic upload; private by default) ──\n"
    "    _maybe_upload(ctx, proj, t, py, shared, dry)"
)

FUNC = '''
def _maybe_thumbnail(ctx, proj, t, py, shared, dry):
    """Auto thumbnail before upload. If <proj>/thumbnail.json exists, generate
    candidate stills, let Sonnet pick the best on the CTR job, overlay the locked
    headline -> thumbnail.png (upload_episode.py attaches it). Graceful + idempotent:
    a missing spec or any failure ships final_video.mp4 + upload untouched; an existing
    thumbnail.png is left in place (no fal re-spend). channel.json look resolves by
    walk-up from the project dir, same pattern as look_resolver."""
    proj = Path(proj)
    spec_file = proj / "thumbnail.json"
    out_png = proj / "thumbnail.png"
    if out_png.exists():
        t.info(f"thumbnail.png present \u2014 skipping generation ({out_png})")
        return
    if not spec_file.exists():
        t.info("no thumbnail.json \u2014 skipping auto-thumbnail (upload ships without a custom one).")
        return
    if dry:
        t.info(f"[dry-run] would generate + select + overlay thumbnail from {spec_file}")
        return
    try:
        spec = json.loads(spec_file.read_text())
    except Exception as e:
        t.warn(f"thumbnail.json unreadable ({e}) \u2014 skipping thumbnail.")
        return
    subject = (spec.get("subject") or "").strip()
    title = (spec.get("title") or "").strip()
    subtitle = (spec.get("subtitle") or "").strip()
    if not subject or not title:
        t.warn("thumbnail.json missing 'subject' or 'title' \u2014 skipping thumbnail.")
        return
    sel = Path(shared) / "select_thumbnail_still.py"
    mk = Path(shared) / "make_thumbnail.py"
    if not sel.exists() or not mk.exists():
        t.warn("select_thumbnail_still.py / make_thumbnail.py missing \u2014 skipping thumbnail.")
        return
    # 1) generate candidates + Sonnet-select -> <proj>/thumbnail_still.png
    if not _run([py, str(sel), "--project", str(proj), "--subject", subject],
                t, "select_thumbnail_still", cwd=None, dry_run=False):
        t.warn("thumbnail selection failed \u2014 shipping without a custom thumbnail.")
        return
    still = proj / "thumbnail_still.png"
    if not still.exists():
        t.warn("thumbnail_still.png not produced \u2014 skipping overlay.")
        return
    # 2) overlay the locked headline -> <proj>/thumbnail.png
    cmd = [py, str(mk), "--project", str(proj), "--still", str(still), "--title", title]
    if subtitle:
        cmd += ["--subtitle", subtitle]
    if not _run(cmd, t, "make_thumbnail", cwd=None, dry_run=False):
        t.warn("thumbnail overlay failed \u2014 shipping without a custom thumbnail.")
        return
    t.ok(f"thumbnail \u2192 {out_png}")

'''


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found (run from the repo's shared/ dir).")
    text = TARGET.read_text()

    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present) — no change.")
        return

    # Anchors must each appear exactly once.
    for name, anchor in (("FUNC_ANCHOR", FUNC_ANCHOR), ("CALL_ANCHOR", CALL_ANCHOR)):
        n = text.count(anchor)
        if n != 1:
            sys.exit(f"FAIL: {name} found {n} times (expected 1) — refusing to half-apply.")

    new = text

    # Ensure `import json` is present (the new function needs it).
    if "import json" not in new:
        if "import os\n" not in new:
            sys.exit("FAIL: could not find 'import os' to anchor the json import.")
        new = new.replace("import os\n", "import os\nimport json\n", 1)

    # Insert the function just before run_convergence_leg.
    new = new.replace(FUNC_ANCHOR, FUNC.lstrip("\n") + "\n" + FUNC_ANCHOR, 1)

    # Insert the call before _maybe_upload.
    new = new.replace(CALL_ANCHOR, CALL_NEW, 1)

    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change or sentinel missing — aborting.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_thumbnail")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}). Sentinel '{SENTINEL}' present.")
    print("    Verify:  grep -n '_maybe_thumbnail' shared/convergence_leg.py")


if __name__ == "__main__":
    main()
