#!/usr/bin/env python3
"""
patch_fix_button.py -- Mission Control: ONE "Fix this image" button + truthful model labels.

WHAT (two files):

shared/mission_control/pipeline_server.py
  1. Button consolidation at the stills gate. The primary per-still action is now
     a single amber "Fix this image" button = the vision-guided channel-aware path
     (Sonnet inspects the still, names the defect, re-renders the corrected prompt
     on the CHANNEL model with the beat's reference sheet(s)). The old "AI Fix"
     button is REMOVED (vision + a flux-hardwired re-render -- wrong model on
     reference channels, superseded entirely). "Regenerate" stays as the secondary
     (blind re-roll / Notes / Override).
  2. Regenerate REROUTED server-side: /api/restill now renders through
     recreation_pipeline.generate_still (channel-aware, reference-aware) instead of
     the flux-hardwired restill path. The old path silently STRIPPED the character
     reference on every {skeptic}/{driver}/{brain} regenerate. Override still
     bypasses canon (raw prompt) but renders on the channel model with refs.
  3. The hardcoded "Flux still" caption (false on NB2 channels) becomes a truthful
     per-beat render-path label fed by build_view.

shared/mission_control/build_view.py
  4. Each beat row gains "render_path": from the storyboard shot's _reference_images
     + the channel's image_model. States the PATH, not runtime fallbacks (refusal
     fallbacks aren't recorded anywhere yet -- provenance sidecar = follow-up).

/api/aifix endpoint stays (harmless, unreferenced by the UI).

Idempotent (sentinel PATCH_FIXBTN_APPLIED per file), anchor-verified, backs up to
<file>.pre_fixbtn, py_compiles before writing.

RUN ON: LAPTOP -> commit -> push -> BOX git pull --no-edit -> restart
mission-control (NOT while a batch is animating).

    python3 patch_fix_button.py
"""

from __future__ import annotations
import argparse
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

SENTINEL = "PATCH_FIXBTN_APPLIED"

SERVER_EDITS = [['consolidated buttons', '        \'<button class="aifix" style="width:100%;margin-top:8px;background:#14a3b8;color:#fff;\' +\n          \'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">AI Fix</button>\' +\n        \'<button class="regen" style="width:100%;margin-top:8px;background:#3b5bdb;color:#fff;\' +\n          \'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Regenerate</button>\' +\n        \'<button class="nbfix" style="width:100%;margin-top:8px;background:#c98a1a;color:#fff;\' +\n          \'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Nano-Banana Fix</button>\' +', '        \'<button class="nbfix" style="width:100%;margin-top:8px;background:#c98a1a;color:#fff;\' +\n          \'border:0;border-radius:6px;padding:11px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:700;">&#128295; Fix this image</button>\' +\n        \'<button class="regen" style="width:100%;margin-top:8px;background:#3b5bdb;color:#fff;\' +\n          \'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Regenerate</button>\' +'], ['listener defs', '    const aifix = ctl.querySelector("button.aifix");\n    const regen = ctl.querySelector("button.regen");\n    const nbfix = ctl.querySelector("button.nbfix");', '    const regen = ctl.querySelector("button.regen");\n    const nbfix = ctl.querySelector("button.nbfix");'], ['listeners', '    aifix.addEventListener("click", function() {\n      post("/api/aifix", {shot: shot}, "AI Fix diagnosing");\n    });\n    regen.addEventListener("click", function() {\n      post("/api/restill", {shot: shot, note: note.value, override: override.value},\n           override.value.trim() ? "Regenerating (override)" : "Regenerating");\n    });\n    if (nbfix) nbfix.addEventListener("click", function() {\n      post("/api/nbfix", {shot: shot}, "Nano-Banana re-render");\n    });', '    regen.addEventListener("click", function() {\n      post("/api/restill", {shot: shot, note: note.value, override: override.value},\n           override.value.trim() ? "Regenerating (override)" : "Regenerating");\n    });\n    if (nbfix) nbfix.addEventListener("click", function() {\n      post("/api/nbfix", {shot: shot}, "Inspecting &amp; fixing");\n    });'], ['render-path label', '      \'<div>\' + stillCell + \'<div style="color:#55556a;font-size:11px;margin-top:4px;">Flux still</div></div>\' +', '      \'<div>\' + stillCell + \'<div style="color:#55556a;font-size:11px;margin-top:4px;">\' + ((b && b.render_path) || "still") + \'</div></div>\' +'], ['gate hint', "      '<div>' + n + ' stills rendered. Review the body below (AI Fix / Regenerate any that break), then decide.</div>' +", "      '<div>' + n + ' stills rendered. Review the body below (Fix this image on any that break), then decide.</div>' +"], ['regenerate reroute', '        if override:\n            final_prompt = override; mode = "OVERRIDE"; negs = []\n        else:\n            beat = beats_by_idx[shot_idx]\n            resolved = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])\n            final_prompt = (f"{resolved.rstrip(\' .\')}. REGENERATION FEEDBACK: {note}"\n                            if note else resolved)\n            mode = "NORMAL"; negs = ctx["negatives"]\n\n        sys.stderr.write(f"[Regenerate] shot {shot_idx:03d} [{mode}]\\n")\n        backup_existing_still(ctx["stills_dir"], shot_idx)\n        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"\n        ok = generate_still(final_prompt, negs, out, ctx["model"])', '        beat = beats_by_idx[shot_idx]\n        refs = beat.get("_reference_images") or None\n        if override:\n            final_prompt = override; mode = "OVERRIDE"\n        else:\n            resolved = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])\n            final_prompt = (f"{resolved.rstrip(\' .\')}. REGENERATION FEEDBACK: {note}"\n                            if note else resolved)\n            mode = "NORMAL"\n        # PATCH_FIXBTN_APPLIED: channel-aware re-render. Routes through\n        # recreation_pipeline.generate_still so reference beats keep their ref\n        # sheet(s) and every channel renders on its own model (flux only as the\n        # engine\'s own refusal fallback). The old path was flux-hardwired and\n        # silently stripped reference identity on {skeptic}/{driver}/{brain} beats.\n        sys.stderr.write(f"[Regenerate] shot {shot_idx:03d} [{mode}] "\n                         f"(refs={len(refs) if refs else 0})\\n")\n        backup_existing_still(ctx["stills_dir"], shot_idx)\n        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"\n        try:\n            ok = bool(_recp_generate_still(final_prompt, out, reference_images=refs))\n        except Exception as e:\n            self._json(500, {"ok": False, "error": f"channel-model render failed: {e}"}); return']]

VIEW_EDITS = [['render_path compute', '        motion_prompt = (shot or {}).get("motion_prompt")', '        motion_prompt = (shot or {}).get("motion_prompt")\n\n        # PATCH_FIXBTN_APPLIED: truthful per-beat render-path label for the MC UI.\n        # States the PATH the beat takes (reference /edit vs channel text model),\n        # not runtime fallbacks (those aren\'t recorded anywhere yet).\n        _refs = (shot or {}).get("_reference_images") or []\n        render_path = (f"NB2 /edit \\u00b7 {len(_refs)} ref" if _refs\n                       else f"{_channel_model} \\u00b7 text")'], ['render_path row field', '            "look_resolved": look_resolved,\n            "payload": b.get("payload", {}),', '            "look_resolved": look_resolved,\n            "render_path": render_path,\n            "payload": b.get("payload", {}),'], ['channel model load', '    look_resolved = _resolve_look(paths)', '    look_resolved = _resolve_look(paths)\n    # PATCH_FIXBTN_APPLIED: channel text-to-image model name for the render-path label.\n    _channel_model = (_load_json(paths["project"].parent.parent / "channel.json")\n                      or {}).get("image_model", "flux")']]


def apply(target: Path, edits) -> int:
    src = target.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {target}")
        return 0
    for label, old, _new in edits:
        c = src.count(old)
        if c != 1:
            print(f"ERROR [{target.name}]: anchor '{label}' found {c} times "
                  f"(need exactly 1). Refusing to half-apply.", file=sys.stderr)
            return 3
    out = src
    for _label, old, new in edits:
        out = out.replace(old, new, 1)
    if SENTINEL not in out:
        print(f"ERROR [{target.name}]: sentinel missing from result", file=sys.stderr)
        return 4
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR [{target.name}]: patched result does not compile:\n{e}",
              file=sys.stderr)
        tmp.unlink(missing_ok=True); return 5
    tmp.unlink(missing_ok=True)
    backup = target.with_suffix(target.suffix + ".pre_fixbtn")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")
    print(f"OK  patched {target}  (backup {backup.name}, {len(edits)} edits)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="shared/mission_control/pipeline_server.py")
    ap.add_argument("--view", default="shared/mission_control/build_view.py")
    args = ap.parse_args()
    for p in (args.server, args.view):
        if not Path(p).is_file():
            print(f"ERROR: not found: {p}", file=sys.stderr); return 2
    rc = apply(Path(args.server), SERVER_EDITS)
    if rc:
        return rc
    rc = apply(Path(args.view), VIEW_EDITS)
    if rc:
        print("WARNING: server patched but view failed -- restore the server "
              "backup or fix the view before restarting.", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
