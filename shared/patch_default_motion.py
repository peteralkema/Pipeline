#!/usr/bin/env python3
"""
patch_default_motion.py — per-channel default motion direction.

WHY
  The default motion ("Slow, subtle atmospheric motion...") was hardcoded in two
  places and dates from the early-Kling/Final-Hours era when fast motion warped
  faces. Peter's experiments show a dramatic default looks far better on Sacred
  Dawn (faceless by design — nothing to warp). This makes the default a per-channel
  channel.json field with a global fallback, so each channel owns its motion
  signature the way it owns its voice and look.

WHAT THIS DOES (three files)
  shared/recreation_pipeline.py
    - CHANNEL_DEFAULTS gains "default_motion" (the canonical global default).
    - cmd_stills resolves the channel's default_motion for any beat whose script
      did not author a motion_prompt.
  shared/mission_control/pipeline_server.py
    - _GLOBAL_DEFAULT_MOTION + _channel_default_motion(ch, pr) helper.
    - _handle_animate's empty-box fallback now uses the channel's default_motion
      (resolved after ch/pr), instead of a hardcoded string. This also reconciles
      the two slightly-different hardcoded strings into one path.
  sacred-dawn/channel.json
    - default_motion set to Peter's dramatic string (added only if absent).

  Default-only: an authored motion_prompt or a typed motion box always wins.

DISCIPLINE
  Idempotent (sentinel: `_channel_default_motion` in pipeline_server.py). Code
  anchors verified before any write; backs each touched file up to .pre_defaultmotion;
  re-compiles the .py files + revalidates channel.json; rolls back ALL on failure.
  Run from the repo root on the LAPTOP, then commit/push, then pull + restart on box.
"""
import sys
import json
import shutil
import py_compile
from pathlib import Path

RP = Path("shared/recreation_pipeline.py")
PS = Path("shared/mission_control/pipeline_server.py")
CJ = Path("sacred-dawn/channel.json")

PS_MARKER = "_channel_default_motion"
DRAMATIC = ("dramatic motion, maximise elements of movement and interplay on scene, "
            "dramatic lighting effects. zoom in")

# ── recreation_pipeline.py edits ─────────────────────────────────────────────
RP_DEFAULTS_OLD = '''    "base_canon": {},   # auto-merged into every beat-script's canon block'''
RP_DEFAULTS_NEW = '''    "default_motion": (
        "Slow, subtle atmospheric motion. Drifting light, faint air. "
        "No fast movement, no camera shake."
    ),
    "base_canon": {},   # auto-merged into every beat-script's canon block'''

RP_LOOP_OLD = '''        shots = []
        for i, b in enumerate(beats, 1):
            image_prompt = _expand_canon(b["image_prompt"].strip(), canon)
            motion_prompt = _expand_canon(
                b.get("motion_prompt", "Slow, subtle atmospheric motion. Drifting light. No fast movement.").strip(),
                canon,
            )'''
RP_LOOP_NEW = '''        _default_motion = (load_channel_config(strict=False).get("default_motion")
                           or CHANNEL_DEFAULTS["default_motion"])
        shots = []
        for i, b in enumerate(beats, 1):
            image_prompt = _expand_canon(b["image_prompt"].strip(), canon)
            motion_prompt = _expand_canon(
                (b.get("motion_prompt") or _default_motion).strip(),
                canon,
            )'''

# ── pipeline_server.py edits ─────────────────────────────────────────────────
PS_HELPER_OLD = '''def _resolve_request_project(body):'''
PS_HELPER_NEW = '''_GLOBAL_DEFAULT_MOTION = ("Slow, subtle atmospheric motion. Drifting light, "
                          "faint air. No fast movement, no camera shake.")


def _channel_default_motion(ch, pr):
    """The channel's default_motion (channel.json) for an empty motion box,
    falling back to the global default."""
    try:
        import json as _json
        cj = resolve_paths(ch, pr, _REPO)["channel_json"]
        if cj.is_file():
            v = _json.loads(cj.read_text()).get("default_motion")
            if v and str(v).strip():
                return str(v).strip()
    except Exception:
        pass
    return _GLOBAL_DEFAULT_MOTION


def _resolve_request_project(body):'''

PS_FALLBACK_OLD = '''        if not motion_prompt:
            motion_prompt = ("Slow, subtle atmospheric motion. Drifting light, "
                             "faint air. No fast movement, no camera shake.")
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return'''
PS_FALLBACK_NEW = '''        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        if not motion_prompt:
            motion_prompt = _channel_default_motion(ch, pr)'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    for f in (RP, PS, CJ):
        if not f.exists():
            die(f"{f} not found — run this from the repo root on the laptop.")

    rp_src = RP.read_text()
    ps_src = PS.read_text()
    try:
        cfg = json.loads(CJ.read_text())
    except Exception as e:
        die(f"{CJ} did not parse as JSON: {e}")

    code_applied = PS_MARKER in ps_src
    cj_applied = "default_motion" in cfg

    if code_applied and cj_applied:
        print("Already fully applied — no changes made.")
        return

    backups = {}

    def back_and_write(path, content):
        bak = path.with_suffix(path.suffix + ".pre_defaultmotion")
        shutil.copy2(path, bak)
        backups[path] = bak
        path.write_text(content)

    def rollback(reason):
        for p, b in backups.items():
            shutil.copy2(b, p)
        die(f"{reason} — restored {len(backups)} file(s) from backup.")

    # Code: all-or-nothing. Verify every anchor on the original source first.
    if not code_applied:
        rp_edits = [("RP CHANNEL_DEFAULTS", RP_DEFAULTS_OLD, RP_DEFAULTS_NEW),
                    ("RP cmd_stills loop", RP_LOOP_OLD, RP_LOOP_NEW)]
        ps_edits = [("PS helper", PS_HELPER_OLD, PS_HELPER_NEW),
                    ("PS animate fallback", PS_FALLBACK_OLD, PS_FALLBACK_NEW)]
        for label, old, _ in rp_edits:
            c = rp_src.count(old)
            if c != 1:
                die(f"{label} anchor found {c}x (expected 1) — nothing written.")
        for label, old, _ in ps_edits:
            c = ps_src.count(old)
            if c != 1:
                die(f"{label} anchor found {c}x (expected 1) — nothing written.")
        new_rp = rp_src
        for _, old, repl in rp_edits:
            new_rp = new_rp.replace(old, repl)
        new_ps = ps_src
        for _, old, repl in ps_edits:
            new_ps = new_ps.replace(old, repl)
        back_and_write(RP, new_rp)
        back_and_write(PS, new_ps)
    else:
        print("code already applied — skipping code edits")

    # channel.json: add default_motion only if absent (never clobber a manual value).
    if not cj_applied:
        cfg["default_motion"] = DRAMATIC
        bak = CJ.with_suffix(CJ.suffix + ".pre_defaultmotion")
        shutil.copy2(CJ, bak)
        backups[CJ] = bak
        CJ.write_text(json.dumps(cfg, indent=2) + "\n")
    else:
        print("sacred-dawn/channel.json already has default_motion — leaving it")

    # Verify: compile the .py files we wrote; revalidate channel.json.
    if RP in backups:
        try:
            py_compile.compile(str(RP), doraise=True)
        except py_compile.PyCompileError as e:
            rollback(f"{RP} does not compile\n{e}")
    if PS in backups:
        if PS_MARKER not in PS.read_text():
            rollback("pipeline_server marker missing after write")
        try:
            py_compile.compile(str(PS), doraise=True)
        except py_compile.PyCompileError as e:
            rollback(f"{PS} does not compile\n{e}")
    if CJ in backups:
        try:
            json.loads(CJ.read_text())
        except Exception as e:
            rollback(f"{CJ} invalid JSON after write: {e}")

    print("OK patched:")
    for p, b in backups.items():
        print(f"   {p}   (backup: {b.name})")
    print("Final Hours / others -> global default (unchanged); Sacred Dawn -> dramatic.")
    print()
    print("AFTER you pull on the box, restart Mission Control (the always-on server changed):")
    print("   systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
