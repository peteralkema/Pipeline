#!/usr/bin/env python3
"""
patch_convergence_publish_at.py - make convergence honour a per-project release slot.

WHAT IT DOES (idempotent; sentinel '# [scheduler]'):
  rewrites _maybe_upload() in convergence_leg.py so that, if <proj>/publish.json exists
  and carries a "publish_at" value, the upload shells out with --publish-at <iso>.
  upload_episode.py forces privacy=private whenever --publish-at is set, so the video
  uploads PRIVATE with status.publishAt and YouTube auto-publishes on schedule (never
  public+publishAt, which the API rejects).

  No publish.json (or an unreadable one, or no publish_at) -> unchanged private-immediate
  behaviour. The release slot is written once by run_batch.py at prep and read once here
  at upload; nothing in between touches it (the render_policy.json / thumbnail.json pattern).

Source is pure ASCII: the em-dashes in the matched/produced strings are written as
\u2014 escapes so they still match the original bytes at runtime.

Run on the LAPTOP from the repo root:  python3 shared/patch_convergence_publish_at.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "convergence_leg.py"
SENTINEL = "# [scheduler]"
EM = "\u2014"  # em-dash, matches the bytes already in convergence_leg.py

ANCHOR = (
    '    up = Path(shared) / "upload_episode.py"\n'
    '    if not up.exists():\n'
    '        t.warn(f"upload step skipped ' + EM + ' {up} not found (final_video.mp4 is safe; upload manually).")\n'
    '        return\n'
    '    if dry:\n'
    '        t.info(f"[dry-run] would publish via upload_episode.py --project {proj} (private)")\n'
    '        return\n'
    '    if not _run([py, str(up), "--project", str(proj)], t, "upload_episode", cwd=None, dry_run=False):\n'
    '        t.warn("upload failed ' + EM + ' final_video.mp4 is complete and safe. Re-run:  "\n'
    '               f"python shared/upload_episode.py --project {proj}")\n'
)

NEW = (
    '    up = Path(shared) / "upload_episode.py"\n'
    '    if not up.exists():\n'
    '        t.warn(f"upload step skipped ' + EM + ' {up} not found (final_video.mp4 is safe; upload manually).")\n'
    '        return\n'
    '    # [scheduler] if the batch runner wrote a release slot, upload PRIVATE + publishAt\n'
    '    # (upload_episode.py forces private whenever --publish-at is set). Written once at\n'
    '    # prep, read once here -- nothing in between can corrupt it. No file -> private-immediate.\n'
    '    upload_cmd = [py, str(up), "--project", str(proj)]\n'
    '    _pa = ""\n'
    '    pub_file = Path(proj) / "publish.json"\n'
    '    if pub_file.exists():\n'
    '        try:\n'
    '            _pa = (json.loads(pub_file.read_text()).get("publish_at") or "").strip()\n'
    '        except Exception as e:\n'
    '            _pa = ""\n'
    '            t.warn(f"publish.json unreadable ({e}) ' + EM + ' uploading private-immediate.")\n'
    '        if _pa:\n'
    '            upload_cmd += ["--publish-at", _pa]\n'
    '    sched_note = f" (scheduled publishAt {_pa})" if _pa else ""\n'
    '    if dry:\n'
    '        t.info(f"[dry-run] would publish via upload_episode.py --project {proj} (private){sched_note}")\n'
    '        return\n'
    '    if not _run(upload_cmd, t, "upload_episode", cwd=None, dry_run=False):\n'
    '        t.warn("upload failed ' + EM + ' final_video.mp4 is complete and safe. Re-run:  "\n'
    '               f"python shared/upload_episode.py --project {proj}"\n'
    '               + (f" --publish-at {_pa}" if _pa else ""))\n'
)


def main():
    if not TARGET.exists():
        sys.exit(f"target not found: {TARGET}")
    src = TARGET.read_text()

    if SENTINEL in src:
        print(f"[patch] sentinel present -- {TARGET.name} already patched. No-op.")
        return

    n = src.count(ANCHOR)
    if n != 1:
        sys.exit(f"[patch] ABORT: _maybe_upload anchor found {n} times (expected 1). "
                 f"Source drifted -- inspect before patching.")

    backup = TARGET.with_suffix(".py.pre_publishat")
    if not backup.exists():
        backup.write_text(src)
        print(f"[patch] backup -> {backup.name}")

    out = src.replace(ANCHOR, NEW, 1)
    if SENTINEL not in out:
        sys.exit("[patch] ABORT: sentinel missing after edit -- nothing written.")

    TARGET.write_text(out)
    print(f"[patch] OK -- publish.json -> --publish-at wired into {TARGET.name}")
    print("[patch] verify:  python3 -c \"import ast; ast.parse(open('shared/convergence_leg.py').read())\"")


if __name__ == "__main__":
    main()
