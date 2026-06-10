#!/usr/bin/env python3
"""
patch_convergence_upload.py — wire the channel-agnostic upload step into convergence.

Idempotent. Verifies its two anchors exist exactly once before writing; refuses to
half-apply; re-running is a no-op. Backs up to a .pre_upload sidecar.

What it does:
  1. Inserts a `_maybe_upload(...)` helper just above `def run_convergence_leg(`.
  2. After assemble succeeds (`t.ok("convergence complete ...")`), calls `_maybe_upload`
     before returning, so a single-video run finishes render → assemble → upload-private.

Upload failure NEVER discards the finished video — it warns and still returns the final
path. Batched jobs (header parts > 1) self-skip inside upload_episode.py.

Run from repo root (laptop), verify the grep it prints, then commit → push → pull on box.
    python3 shared/patch_convergence_upload.py
"""
import sys
from pathlib import Path

TARGET = Path("shared/convergence_leg.py")
MARKER = "_maybe_upload"

HELPER = '''
def _maybe_upload(ctx, proj, t, py, shared, dry):
    """Channel-agnostic publish: shell out to upload_episode.py (header = metadata,
    channel folder = identity). Batch-exit-gate and parts-skip live inside that script.
    An upload FAILURE never discards the finished video — warn and carry on."""
    up = Path(shared) / "upload_episode.py"
    if not up.exists():
        t.warn(f"upload step skipped — {up} not found (final_video.mp4 is safe; upload manually).")
        return
    if dry:
        t.info(f"[dry-run] would publish via upload_episode.py --project {proj} (private)")
        return
    if not _run([py, str(up), "--project", str(proj)], t, "upload_episode", cwd=None, dry_run=False):
        t.warn("upload failed — final_video.mp4 is complete and safe. Re-run:  "
               f"python shared/upload_episode.py --project {proj}")


'''

ANCHOR_DEF = "def run_convergence_leg(ctx, modea=None):"

ANCHOR_RETURN = (
    '    t.ok(f"convergence complete \u2192 {final_out}")\n'
    '    return {"final": str(final_out)}'
)
REPLACE_RETURN = (
    '    t.ok(f"convergence complete \u2192 {final_out}")\n'
    '\n'
    '    # \u2500\u2500 PUBLISH (channel-agnostic upload; private by default) \u2500\u2500\n'
    '    _maybe_upload(ctx, proj, t, py, shared, dry)\n'
    '\n'
    '    return {"final": str(final_out)}'
)


def fail(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found — run from the repo root.")
    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print(f"already patched ({MARKER} present) — no changes. ✓")
        return

    # verify anchors exist exactly once each
    if src.count(ANCHOR_DEF) != 1:
        fail(f"expected exactly one '{ANCHOR_DEF}' (found {src.count(ANCHOR_DEF)}).")
    if src.count(ANCHOR_RETURN) != 1:
        fail("could not find the unique convergence-complete return block "
             f"(found {src.count(ANCHOR_RETURN)}). File may have changed — inspect before patching.")

    patched = src.replace(ANCHOR_DEF, HELPER.lstrip("\n") + "\n" + ANCHOR_DEF, 1)
    patched = patched.replace(ANCHOR_RETURN, REPLACE_RETURN, 1)

    if MARKER not in patched or REPLACE_RETURN not in patched:
        fail("post-write verification failed — not writing.")

    TARGET.with_suffix(".py.pre_upload").write_text(src, encoding="utf-8")
    TARGET.write_text(patched, encoding="utf-8")
    print(f"patched {TARGET}  (backup: {TARGET.with_suffix('.py.pre_upload')}) ✓")
    print("verify:  grep -n '_maybe_upload' shared/convergence_leg.py   # expect 2 hits (def + call)")


if __name__ == "__main__":
    main()
