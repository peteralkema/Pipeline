#!/usr/bin/env python3
"""
patch_nbfix_vision.py  --  make the "Nano-Banana Fix" button INSPECT-then-fix.

The first Nano-Banana Fix build (patch_nbfix_button.py) did a BLIND re-render on the
channel model -- so a warped still (extra hand, melted feature) could come back just
as warped. This patch gives the button the same Claude Sonnet vision diagnosis the
"AI Fix" button uses -- it names the specific flaw -- and then re-renders the
CORRECTED prompt through the channel-aware, reference-aware engine generate_still
(NB2 /edit for {skeptic} beats, NB2 text for wides, flux only on refusal). It also
sharpens the shared art-director system prompt to hunt generative defects
(warped/extra hands, extra fingers, fused limbs, duplicated objects, garbled text),
which improves the AI Fix button too.

REQUIRES patch_nbfix_button.py already applied (it edits that handler).
Idempotent (sentinel PATCH_NBFIX_VISION_APPLIED), anchor-verified, backs up to
<file>.pre_nbfix_vision, py_compiles before writing.

RUN ON: LAPTOP -> commit -> push -> BOX git pull --no-edit -> restart mission-control
(not while animating).

    python3 patch_nbfix_vision.py --file shared/mission_control/pipeline_server.py
"""

from __future__ import annotations
import argparse
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

SENTINEL = "PATCH_NBFIX_VISION_APPLIED"
REQUIRE = "PATCH_NBFIX_BUTTON_APPLIED"
DEFAULT_TARGET = "shared/mission_control/pipeline_server.py"

SYS_OLD = '_AIFIX_SYSTEM_PROMPT = (\n    "You are a strict art director reviewing an AI-generated still against its "\n    "intended prompt and brand rules (faceless where required, no spell-breakers, "\n    "period-accurate, drift-safe). Respond with STRICT JSON only, no preamble, no "\n    "markdown:\\n"\n    \'{"verdict": "fine" | "fix", "diagnosis": "<one short sentence naming what is \'\n    \'wrong, or why it is fine>", "corrected_prompt": "<the full corrected prompt \'\n    \'if verdict is fix, else empty string>"}\'\n)'
SYS_NEW = '_AIFIX_SYSTEM_PROMPT = (\n    "You are a strict art director reviewing an AI-generated still against its "\n    "intended prompt and brand rules (faceless where required, no spell-breakers, "\n    "period-accurate, drift-safe). Look FIRST for generative defects: warped or "\n    "extra hands, extra or missing fingers, extra or fused limbs, melted or "\n    "asymmetric faces, duplicated or merged objects, floating body parts, and "\n    "garbled text. When you find one, verdict is \\"fix\\" and the corrected_prompt "\n    "must restate the full intended scene AND explicitly demand correct structure "\n    "(e.g. \'exactly two hands, five fingers each, natural anatomy, no extra limbs, "\n    "no duplicated objects\'). Respond with STRICT JSON only, no preamble, no "\n    "markdown:\\n"\n    \'{"verdict": "fine" | "fix", "diagnosis": "<one short sentence naming what is \'\n    \'wrong, or why it is fine>", "corrected_prompt": "<the full corrected prompt \'\n    \'if verdict is fix, else empty string>"}\'\n)'
HANDLER_OLD = '    def _handle_nbfix(self, body):\n        """Re-render one beat through the engine\'s CHANNEL-AWARE generate_still\n        (recreation_pipeline), reading the shot\'s _reference_images from\n        storyboard.json -- the same path cmd_stills/cmd_restill use. On QQrew this\n        renders {skeptic} beats via NB2 /edit (reference) and crew-absent beats via\n        NB2 text-to-image; flux only on refusal. (PATCH_NBFIX_BUTTON_APPLIED)"""\n        if not _ANIMATE_OK:\n            self._json(503, {"ok": False,\n                "error": f"nano-banana fix unavailable: {_ANIMATE_IMPORT_ERR}"}); return\n        if not _RESTILL_OK:\n            self._json(503, {"ok": False,\n                "error": f"restill helpers unavailable: {_RESTILL_IMPORT_ERR}"}); return\n        shot_idx = body.get("shot")\n        if not isinstance(shot_idx, int):\n            self._json(400, {"ok": False, "error": "shot must be an integer"}); return\n        ch, pr = _resolve_request_project(body)\n        if not ch or not pr:\n            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return\n        ctx = _stills_ctx(ch, pr)\n        beats_by_idx = ctx["beats_by_idx"]\n        if shot_idx not in beats_by_idx:\n            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return\n        beat = beats_by_idx[shot_idx]\n        prompt = (beat.get("image_prompt") or "").strip()\n        if not prompt:\n            self._json(404, {"ok": False, "error": f"shot {shot_idx} has no image_prompt"}); return\n        refs = beat.get("_reference_images") or None\n        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"\n        sys.stderr.write(f"[NB fix] shot {shot_idx:03d} re-render on channel model "\n                         f"(refs={len(refs) if refs else 0})\\n")\n        backup_existing_still(ctx["stills_dir"], shot_idx)\n        try:\n            res = _recp_generate_still(prompt, out, reference_images=refs)\n        except Exception as e:\n            self._json(500, {"ok": False,\n                "error": f"channel-model render failed: {e}"}); return\n        if res:\n            self._json(200, {"ok": True, "shot": shot_idx,\n                "mode": ("NB2 /edit" if refs else "NB2 text")}); return\n        self._json(500, {"ok": False, "error": "channel-model generation failed"})'
HANDLER_NEW = '    def _handle_nbfix(self, body):\n        """Nano-Banana Fix: Claude Sonnet vision INSPECTS the still and names the\n        flaw (warped/extra hands, extra fingers, melted or duplicated features, ...),\n        then re-renders the CORRECTED prompt through the engine\'s channel-aware\n        generate_still with the shot\'s _reference_images from storyboard.json -- NB2\n        /edit (reference) for {skeptic} beats on QQrew, NB2 text for wides, flux only\n        on refusal. Not a blind re-roll: the diagnosis targets the warp.\n        (PATCH_NBFIX_BUTTON_APPLIED) (PATCH_NBFIX_VISION_APPLIED)"""\n        if not _ANIMATE_OK:\n            self._json(503, {"ok": False,\n                "error": f"nano-banana fix unavailable: {_ANIMATE_IMPORT_ERR}"}); return\n        if not _RESTILL_OK:\n            self._json(503, {"ok": False,\n                "error": f"restill helpers unavailable: {_RESTILL_IMPORT_ERR}"}); return\n        if _ANTHROPIC_CLIENT is None:\n            self._json(503, {"ok": False, "error":\n                "nano-banana fix needs vision: anthropic not installed or ANTHROPIC_API_KEY not set"}); return\n        shot_idx = body.get("shot")\n        if not isinstance(shot_idx, int):\n            self._json(400, {"ok": False, "error": "shot must be an integer"}); return\n        ch, pr = _resolve_request_project(body)\n        if not ch or not pr:\n            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return\n        ctx = _stills_ctx(ch, pr)\n        beats_by_idx = ctx["beats_by_idx"]\n        if shot_idx not in beats_by_idx:\n            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return\n        beat = beats_by_idx[shot_idx]\n        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"\n        if not out.exists():\n            self._json(404, {"ok": False, "error": f"still not found: {out.name}"}); return\n        intended = (beat.get("image_prompt") or "").strip()\n        refs = beat.get("_reference_images") or None\n\n        # 1. VISION DIAGNOSIS (same art-director pass as AI Fix)\n        sys.stderr.write(f"[NB fix] shot {shot_idx:03d} diagnosing...\\n")\n        try:\n            img = out.read_bytes()\n            mtype = _sniff_media_type(img[:16])\n            b64 = _base64.standard_b64encode(img).decode("ascii")\n            resp = _ANTHROPIC_CLIENT.messages.create(\n                model=_VISION_MODEL, max_tokens=1024,\n                system=_AIFIX_SYSTEM_PROMPT,\n                messages=[{"role": "user", "content": [\n                    {"type": "image", "source": {"type": "base64",\n                        "media_type": mtype, "data": b64}},\n                    {"type": "text", "text":\n                        f"Intended prompt for this shot:\\n\\n{intended}\\n\\n"\n                        f"Judge the image against the brand rules and respond with the JSON object."},\n                ]}],\n            )\n            raw = resp.content[0].text.strip()\n            if raw.startswith("```"):\n                raw = raw.strip("`"); raw = raw[raw.find("{"):raw.rfind("}") + 1]\n            import json as _json\n            verdict = _json.loads(raw)\n        except Exception as e:\n            self._json(500, {"ok": False, "error": f"vision diagnosis failed: {e}"}); return\n\n        diagnosis = (verdict.get("diagnosis") or "").strip()\n        corrected = (verdict.get("corrected_prompt") or "").strip()\n        if not (verdict.get("verdict") == "fix" and corrected):\n            self._json(200, {"ok": True, "shot": shot_idx, "changed": False,\n                "diagnosis": diagnosis or "Image looks consistent with the brand rules."}); return\n\n        # 2. RE-RENDER the corrected prompt on the CHANNEL model, reference-aware\n        sys.stderr.write(f"[NB fix] shot {shot_idx:03d} re-render on channel model "\n                         f"(refs={len(refs) if refs else 0}) -> {diagnosis[:60]}\\n")\n        backup_existing_still(ctx["stills_dir"], shot_idx)\n        try:\n            res = _recp_generate_still(corrected, out, reference_images=refs)\n        except Exception as e:\n            self._json(500, {"ok": False,\n                "error": f"channel-model render failed: {e}", "diagnosis": diagnosis}); return\n        if res:\n            self._json(200, {"ok": True, "shot": shot_idx, "changed": True,\n                "diagnosis": diagnosis,\n                "mode": ("NB2 /edit" if refs else "NB2 text")}); return\n        self._json(500, {"ok": False,\n            "error": "channel-model generation failed after diagnosis", "diagnosis": diagnosis})'

EDITS = [
    ("art-director system prompt (defect focus)", SYS_OLD, SYS_NEW),
    ("_handle_nbfix (blind -> vision+NB2)", HANDLER_OLD, HANDLER_NEW),
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
    if REQUIRE not in src:
        print(f"ERROR: {REQUIRE} not found -- apply patch_nbfix_button.py first.",
              file=sys.stderr)
        return 5

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

    backup = target.with_suffix(target.suffix + ".pre_nbfix_vision")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")
    print(f"OK  patched {target}")
    print(f"    backup  {backup}")
    print(f"    edits   {len(EDITS)} applied, result compiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
