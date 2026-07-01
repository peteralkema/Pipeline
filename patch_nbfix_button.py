#!/usr/bin/env python3
"""
patch_nbfix_button.py  --  Mission Control: the per-still "Nano-Banana Fix" button.

WHY: the two existing stills controls (AI Fix, Regenerate) call
restill_from_feedback.generate_still, which is HARD-WIRED to flux arg-shape
(image_size:"landscape_16_9", safety_tolerance, num_inference_steps, guidance_scale)
and has NO reference /edit path. On an all-NB2 channel like QQrew that means every
"fix" silently drops to flux text-to-image -- and a {skeptic} beat loses its
reference lock entirely.

WHAT: adds a THIRD per-still button that re-renders the beat through the engine's
own channel-aware recreation_pipeline.generate_still -- exactly as cmd_stills /
cmd_restill do -- reading the shot's _reference_images straight from storyboard.json:
  - QQrew (image_model:nano_banana, render_mode:reference): {skeptic} beats render
    via NB2 /edit with skeptic_ref.png; crew-absent beats via NB2 text-to-image.
  - any channel: re-renders on that channel's own image_model, flux only on refusal.
No new render code -- it reuses the proven engine path. Additive: the AI Fix and
Regenerate buttons are untouched (they remain the flux-shaped tool).

Five coupled edits to pipeline_server.py:
  1. import  generate_still as _recp_generate_still  from recreation_pipeline
  2. new handler  _handle_nbfix  (backup + engine generate_still + storyboard refs)
  3. button element  <button class="nbfix">Nano-Banana Fix</button>
  4. JS binding      nbfix -> POST /api/nbfix {shot}
  5. route           /api/nbfix -> _handle_nbfix

Idempotent (sentinel no-op), anchor-verified (refuses to half-apply), backs up to
<file>.pre_nbfix_button, py_compiles the result before writing.

RUN ON: LAPTOP, then commit -> push -> BOX git pull --no-edit -> restart
mission-control (NOT while a render is animating).

    python3 patch_nbfix_button.py --file shared/mission_control/pipeline_server.py
"""

from __future__ import annotations
import argparse
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

SENTINEL = "PATCH_NBFIX_BUTTON_APPLIED"
DEFAULT_TARGET = "shared/mission_control/pipeline_server.py"


# --- (1) import the engine's channel-aware generate_still ---------------------
IMPORT_OLD = '''        animate_still as _animate_still,
        ken_burns_still as _ken_burns_still,
        _tiered_kling_count, _tiered_beat_index, _tiered_duration,'''

IMPORT_NEW = '''        animate_still as _animate_still,
        ken_burns_still as _ken_burns_still,
        generate_still as _recp_generate_still,
        _tiered_kling_count, _tiered_beat_index, _tiered_duration,'''


# --- (2) the handler, inserted just before do_POST ---------------------------
HANDLER_OLD = '''        self._json(500, {"ok": False, "error": "fal generation failed after diagnosis",
                         "diagnosis": diagnosis})

    def do_POST(self):'''

HANDLER_NEW = '''        self._json(500, {"ok": False, "error": "fal generation failed after diagnosis",
                         "diagnosis": diagnosis})

    def _handle_nbfix(self, body):
        """Re-render one beat through the engine's CHANNEL-AWARE generate_still
        (recreation_pipeline), reading the shot's _reference_images from
        storyboard.json -- the same path cmd_stills/cmd_restill use. On QQrew this
        renders {skeptic} beats via NB2 /edit (reference) and crew-absent beats via
        NB2 text-to-image; flux only on refusal. (PATCH_NBFIX_BUTTON_APPLIED)"""
        if not _ANIMATE_OK:
            self._json(503, {"ok": False,
                "error": f"nano-banana fix unavailable: {_ANIMATE_IMPORT_ERR}"}); return
        if not _RESTILL_OK:
            self._json(503, {"ok": False,
                "error": f"restill helpers unavailable: {_RESTILL_IMPORT_ERR}"}); return
        shot_idx = body.get("shot")
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        ctx = _stills_ctx(ch, pr)
        beats_by_idx = ctx["beats_by_idx"]
        if shot_idx not in beats_by_idx:
            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return
        beat = beats_by_idx[shot_idx]
        prompt = (beat.get("image_prompt") or "").strip()
        if not prompt:
            self._json(404, {"ok": False, "error": f"shot {shot_idx} has no image_prompt"}); return
        refs = beat.get("_reference_images") or None
        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        sys.stderr.write(f"[NB fix] shot {shot_idx:03d} re-render on channel model "
                         f"(refs={len(refs) if refs else 0})\\n")
        backup_existing_still(ctx["stills_dir"], shot_idx)
        try:
            res = _recp_generate_still(prompt, out, reference_images=refs)
        except Exception as e:
            self._json(500, {"ok": False,
                "error": f"channel-model render failed: {e}"}); return
        if res:
            self._json(200, {"ok": True, "shot": shot_idx,
                "mode": ("NB2 /edit" if refs else "NB2 text")}); return
        self._json(500, {"ok": False, "error": "channel-model generation failed"})

    def do_POST(self):'''


# --- (3) the button element in the per-still control template ----------------
BTN_OLD = '''        '<button class="regen" style="width:100%;margin-top:8px;background:#3b5bdb;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Regenerate</button>' +'''

BTN_NEW = '''        '<button class="regen" style="width:100%;margin-top:8px;background:#3b5bdb;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Regenerate</button>' +
        '<button class="nbfix" style="width:100%;margin-top:8px;background:#c98a1a;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Nano-Banana Fix</button>' +'''


# --- (4a) the querySelector ---------------------------------------------------
SEL_OLD = '''    const aifix = ctl.querySelector("button.aifix");
    const regen = ctl.querySelector("button.regen");'''

SEL_NEW = '''    const aifix = ctl.querySelector("button.aifix");
    const regen = ctl.querySelector("button.regen");
    const nbfix = ctl.querySelector("button.nbfix");'''


# --- (4b) the click handler ---------------------------------------------------
BIND_OLD = '''    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
  });'''

BIND_NEW = '''    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
    if (nbfix) nbfix.addEventListener("click", function() {
      post("/api/nbfix", {shot: shot}, "Nano-Banana re-render");
    });
  });'''


# --- (5) the POST route -------------------------------------------------------
ROUTE_OLD = '''        if path == "/api/aifix":
            self._handle_aifix(body); return'''

ROUTE_NEW = '''        if path == "/api/aifix":
            self._handle_aifix(body); return
        if path == "/api/nbfix":
            self._handle_nbfix(body); return'''


EDITS = [
    ("import engine generate_still", IMPORT_OLD, IMPORT_NEW),
    ("_handle_nbfix handler", HANDLER_OLD, HANDLER_NEW),
    ("nbfix button element", BTN_OLD, BTN_NEW),
    ("nbfix querySelector", SEL_OLD, SEL_NEW),
    ("nbfix click handler", BIND_OLD, BIND_NEW),
    ("nbfix POST route", ROUTE_OLD, ROUTE_NEW),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_TARGET)
    args = ap.parse_args()

    target = Path(args.file)
    if not target.is_file():
        print(f"ERROR: target not found: {target}", file=sys.stderr)
        return 2

    src = target.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied (sentinel present) -> no-op: {target}")
        return 0

    for label, old, _new in EDITS:
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor for '{label}' found {c} times (need exactly 1). "
                  f"Refusing to half-apply.", file=sys.stderr)
            return 3

    out = src
    for _label, old, new in EDITS:
        out = out.replace(old, new, 1)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(out)
        tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: patched result does not compile:\n{e}", file=sys.stderr)
        tmp.unlink(missing_ok=True)
        return 4
    tmp.unlink(missing_ok=True)

    backup = target.with_suffix(target.suffix + ".pre_nbfix_button")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")
    print(f"OK  patched {target}")
    print(f"    backup  {backup}")
    print(f"    edits   {len(EDITS)} applied, result compiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
