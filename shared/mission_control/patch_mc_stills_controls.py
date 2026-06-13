#!/usr/bin/env python3
"""
patch_mc_stills_controls.py — Phase 3d: still-edit controls + the spend endpoints.

Ports the two PROVEN stills endpoints from serve_review.py into the coordinator,
made PER-REQUEST (no boot-pinned project), and adds the fifth column of controls
to the right of each still.

SERVER (Python) edits to pipeline_server.py:
  1. module setup: lazy imports of restill_from_feedback helpers + Anthropic
     client (process-wide, stateless), VISION_MODEL / AIFIX_SYSTEM_PROMPT, and a
     per-(channel/project) cache builder that loads beats_by_idx + canon +
     negatives fresh on a project switch.
  2. POST routing: add /api/restill and /api/aifix, resolving the project from
     the request (?channel=&project= in the body) or the active job.

PAGE (JS) edits:
  3. beatRow(): add COL 3 = still-controls (Accept/Reject, AI Fix, Regenerate,
     Notes, Override). Five columns: text | still | controls | motion | clip.
     Mode B strip stays below. Wired to {shot, note, override} / {shot}.
  4. control handlers + per-shot judgment state (in-memory, survives re-render).

Contracts (confirmed against serve_review.py):
  /api/restill  {shot:int, note:str, override:str}  shot = ENGINE shot number
  /api/aifix    {shot:int}
  beats_by_idx is keyed by ENGINE shot number (storyboard 1-based index),
  which build_beats_view exposes as assets.still.engine_shot.

Idempotent (markers), backs up to .pre_controls, no escaped newlines in JS.

Run on the box:
  python shared/mission_control/patch_mc_stills_controls.py --check
  python shared/mission_control/patch_mc_stills_controls.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# ---- EDIT 1: module setup (imports, anthropic client, per-project cache) ----
# Anchor: the build_view import line (added in Phase 0). We append the stills-
# endpoint machinery right after it.
EDITS.append(dict(
    marker="_STILLS_CACHE",
    old="from build_view import build_beats_view, resolve_paths",
    new='''from build_view import build_beats_view, resolve_paths

# ---- stills-edit endpoint machinery (ported from serve_review.py) ----------
# These two endpoints (/api/restill, /api/aifix) are the PROVEN stills controls.
# serve_review.py ran them against a boot-pinned single project; here they run
# PER-REQUEST, resolving the project from the active job or ?channel=&project=.
import base64 as _base64

try:
    from restill_from_feedback import (
        resolve_canon_tokens, find_beats_file, load_rulebook_negatives,
        backup_existing_still, generate_still,
    )
    _RESTILL_OK = True
except Exception as _e:
    _RESTILL_OK = False
    _RESTILL_IMPORT_ERR = str(_e)

try:
    from anthropic import Anthropic as _Anthropic
    _ANTHROPIC_AVAILABLE = True
except Exception:
    _ANTHROPIC_AVAILABLE = False

import os as _os
_ANTHROPIC_CLIENT = None
if _ANTHROPIC_AVAILABLE and _os.environ.get("ANTHROPIC_API_KEY"):
    try:
        _ANTHROPIC_CLIENT = _Anthropic(api_key=_os.environ["ANTHROPIC_API_KEY"])
    except Exception:
        _ANTHROPIC_CLIENT = None

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"
_VISION_MODEL = "claude-sonnet-4-6"
_AIFIX_SYSTEM_PROMPT = (
    "You are a strict art director reviewing an AI-generated still against its "
    "intended prompt and brand rules (faceless where required, no spell-breakers, "
    "period-accurate, drift-safe). Respond with STRICT JSON only, no preamble, no "
    "markdown:\\n"
    '{"verdict": "fine" | "fix", "diagnosis": "<one short sentence naming what is '
    'wrong, or why it is fine>", "corrected_prompt": "<the full corrected prompt '
    'if verdict is fix, else empty string>"}'
)

# Per-(channel/project) cache of the restill inputs, so 184 rapid clicks don't
# re-read files 184 times; a project switch loads fresh.
_STILLS_CACHE = {}

def _stills_ctx(channel: str, project: str):
    """Resolve + cache (beats_by_idx, canon, negatives, stills_dir, model) for a
    project, keyed by ENGINE shot number (storyboard index) like serve_review."""
    key = f"{channel}/{project}"
    if key in _STILLS_CACHE:
        return _STILLS_CACHE[key]
    paths = resolve_paths(channel, project, _REPO)
    project_dir = paths["project"]
    beats_file = find_beats_file(project_dir, None)  # storyboard-shaped beats
    import json as _json
    beats_data = _json.loads(Path(beats_file).read_text())
    beats_by_idx = {b["index"]: b for b in beats_data}  # ENGINE shot keyed
    # canon: project data file if present (mirrors serve_review main())
    canon = {}
    canon_file = project_dir / "canon.json"
    if canon_file.is_file():
        try:
            canon = _json.loads(canon_file.read_text()).get("canon", {}) or {}
        except Exception:
            canon = {}
    negatives = load_rulebook_negatives(project_dir)
    ctx = {
        "beats_by_idx": beats_by_idx,
        "canon": canon,
        "negatives": negatives,
        "stills_dir": paths["stills_dir"],
        "model": _FLUX_MODEL,
    }
    _STILLS_CACHE[key] = ctx
    return ctx

def _resolve_request_project(body):
    """Project for a stills POST: explicit channel/project in body, else active job."""
    ch = (body or {}).get("channel")
    pr = (body or {}).get("project")
    if ch and pr:
        return ch, pr
    jid = active_job_id()
    if jid:
        rec = read_job(jid, _REPO)
        return rec.get("channel"), rec.get("project")
    return None, None'''
))

# ---- EDIT 2: POST routing — add /api/restill + /api/aifix ----
EDITS.append(dict(
    marker='path == "/api/restill"',
    old='''        if path.startswith("/api/gate/"):
            name = path[len("/api/gate/"):]
            jid = active_job_id()
            decision = body.get("decision")
            self._json(200, decide_gate(jid, decision)); return''',
    new='''        if path.startswith("/api/gate/"):
            name = path[len("/api/gate/"):]
            jid = active_job_id()
            decision = body.get("decision")
            self._json(200, decide_gate(jid, decision)); return

        if path == "/api/restill":
            self._handle_restill(body); return
        if path == "/api/aifix":
            self._handle_aifix(body); return''',
))

# ---- EDIT 3: the two handler methods (added to Handler class) ----
# Anchor: insert before do_POST so they're methods on the handler.
EDITS.append(dict(
    marker="def _handle_restill",
    old='''    def do_POST(self):
        if not _key_ok(self):
            self.send_response(403); self.end_headers(); return''',
    new='''    def _handle_restill(self, body):
        if not _RESTILL_OK:
            self._json(503, {"ok": False,
                "error": f"restill unavailable: {_RESTILL_IMPORT_ERR}"}); return
        shot_idx = body.get("shot")
        note = (body.get("note") or "").strip()
        override = (body.get("override") or "").strip()
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        ctx = _stills_ctx(ch, pr)
        beats_by_idx = ctx["beats_by_idx"]
        if shot_idx not in beats_by_idx:
            self._json(404, {"ok": False, "error": f"shot {shot_idx} not in beats"}); return

        if override:
            final_prompt = override; mode = "OVERRIDE"; negs = []
        else:
            beat = beats_by_idx[shot_idx]
            resolved = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])
            final_prompt = (f"{resolved.rstrip(' .')}. REGENERATION FEEDBACK: {note}"
                            if note else resolved)
            mode = "NORMAL"; negs = ctx["negatives"]

        sys.stderr.write(f"[Regenerate] shot {shot_idx:03d} [{mode}]\\n")
        backup_existing_still(ctx["stills_dir"], shot_idx)
        out = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        ok = generate_still(final_prompt, negs, out, ctx["model"])
        if ok:
            self._json(200, {"ok": True, "shot": shot_idx, "mode": mode})
        else:
            self._json(500, {"ok": False, "error": "fal generation failed"})

    def _handle_aifix(self, body):
        if not _RESTILL_OK:
            self._json(503, {"ok": False,
                "error": f"restill unavailable: {_RESTILL_IMPORT_ERR}"}); return
        if _ANTHROPIC_CLIENT is None:
            self._json(503, {"ok": False, "error":
                "AI fix unavailable: anthropic not installed or ANTHROPIC_API_KEY not set"}); return
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
        still_path = ctx["stills_dir"] / f"shot_{shot_idx:03d}.png"
        if not still_path.exists():
            self._json(404, {"ok": False, "error": f"still not found: {still_path.name}"}); return

        beat = beats_by_idx[shot_idx]
        intended = resolve_canon_tokens(beat.get("image_prompt", ""), ctx["canon"])
        sys.stderr.write(f"[AI fix] shot {shot_idx:03d} diagnosing...\\n")
        try:
            img = still_path.read_bytes()
            mtype = _sniff_media_type(img[:16])
            b64 = _base64.standard_b64encode(img).decode("ascii")
            resp = _ANTHROPIC_CLIENT.messages.create(
                model=_VISION_MODEL, max_tokens=1024,
                system=_AIFIX_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                        "media_type": mtype, "data": b64}},
                    {"type": "text", "text":
                        f"Intended prompt for this shot:\\n\\n{intended}\\n\\n"
                        f"Judge the image against the brand rules and respond with the JSON object."},
                ]}],
            )
            raw = resp.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`"); raw = raw[raw.find("{"):raw.rfind("}") + 1]
            import json as _json
            verdict = _json.loads(raw)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"vision diagnosis failed: {e}"}); return

        diagnosis = (verdict.get("diagnosis") or "").strip()
        corrected = (verdict.get("corrected_prompt") or "").strip()
        if not (verdict.get("verdict") == "fix" and corrected):
            self._json(200, {"ok": True, "shot": shot_idx, "changed": False,
                "diagnosis": diagnosis or "Image looks consistent with the brand rules."}); return

        backup_existing_still(ctx["stills_dir"], shot_idx)
        ok = generate_still(corrected, [], still_path, ctx["model"])
        if ok:
            self._json(200, {"ok": True, "shot": shot_idx, "changed": True,
                "diagnosis": diagnosis, "corrected_prompt": corrected}); return
        self._json(500, {"ok": False, "error": "fal generation failed after diagnosis",
                         "diagnosis": diagnosis})

    def do_POST(self):
        if not _key_ok(self):
            self.send_response(403); self.end_headers(); return'''
))

# ---- EDIT 4: beatRow — add the still-controls column (5 columns now) ----
# Anchor: the four-column grid template from patch_mc_layout.py. We swap to five
# columns and inject the controls cell. The escapeHtml + motion machinery from
# the layout patch is reused (already present).
EDITS.append(dict(
    marker="still-controls",
    old='''  // COL 1 — TEXT spine
  const textCell =
    '<div style="color:#d4a017;font-size:12px;margin-bottom:8px;">beat ' + b.index +
      ' · shot ' + (shot==null?"—":shot) + ' · ' + (b.stage||"") +
      ' · ' + dur + ' · ' + (b.mode||"") + '</div>' +
    '<div style="color:#e8e6e3;font-size:14px;line-height:1.5;">' + (b.narration||"") + '</div>' +
    '<div style="color:#8a8a99;font-size:12px;margin-top:8px;font-style:italic;line-height:1.45;">' +
      prompt + '</div>' +
    '<div style="color:#55556a;font-size:11px;margin-top:8px;">look: ' + (b.look_resolved||"") + '</div>';

  // Four columns: text | still | motion | clip
  const grid =
    '<div style="display:grid;gap:16px;align-items:start;' +
    'grid-template-columns:minmax(220px,1fr) minmax(240px,1.4fr) minmax(200px,1fr) minmax(240px,1.4fr);">' +
      '<div>' + textCell + '</div>' +
      '<div>' + stillCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">Flux still</div></div>' +
      '<div>' + motionCell + '</div>' +
      '<div>' + clipCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">Kling motion</div></div>' +
    '</div>';''',
    new='''  // COL 1 — TEXT spine
  const textCell =
    '<div style="color:#d4a017;font-size:12px;margin-bottom:8px;">beat ' + b.index +
      ' · shot ' + (shot==null?"—":shot) + ' · ' + (b.stage||"") +
      ' · ' + dur + ' · ' + (b.mode||"") + '</div>' +
    '<div style="color:#e8e6e3;font-size:14px;line-height:1.5;">' + (b.narration||"") + '</div>' +
    '<div style="color:#8a8a99;font-size:12px;margin-top:8px;font-style:italic;line-height:1.45;">' +
      prompt + '</div>' +
    '<div style="color:#55556a;font-size:11px;margin-top:8px;">look: ' + (b.look_resolved||"") + '</div>';

  // COL 3 — STILL CONTROLS (Accept/Reject, AI Fix, Regenerate, Notes, Override).
  // Only meaningful when a still exists and we know the engine shot number.
  let controlsCell;
  if (hasStill && shot != null) {
    const jkey = motionKey(ch, pr, b.index);  // reuse the channel/project/beat key
    const judged = window.__JUDGED && window.__JUDGED[jkey];
    const accSel = judged === "accept" ? "background:#1c7c4a;" : "";
    const rejSel = judged === "reject" ? "background:#7c1c1c;" : "";
    controlsCell =
      '<div class="stillctl" data-shot="' + shot + '" data-jkey="' + jkey + '">' +
        '<div style="display:flex;gap:8px;">' +
          '<button class="jbtn acc" style="flex:1;background:#2a2a36;' + accSel +
            'color:#e8e6e3;border:0;border-radius:6px;padding:8px;cursor:pointer;font:13px ui-monospace,monospace;">Accept</button>' +
          '<button class="jbtn rej" style="flex:1;background:#2a2a36;' + rejSel +
            'color:#e8e6e3;border:0;border-radius:6px;padding:8px;cursor:pointer;font:13px ui-monospace,monospace;">Reject</button>' +
        '</div>' +
        '<button class="aifix" style="width:100%;margin-top:8px;background:#14a3b8;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">AI Fix</button>' +
        '<button class="regen" style="width:100%;margin-top:8px;background:#3b5bdb;color:#fff;' +
          'border:0;border-radius:6px;padding:9px;cursor:pointer;font:13px ui-monospace,monospace;font-weight:600;">Regenerate</button>' +
        '<textarea class="note" rows="2" placeholder="Notes — appended to prompt as regeneration feedback" ' +
          'style="width:100%;box-sizing:border-box;margin-top:8px;background:#1c1c26;color:#e8e6e3;' +
          'border:1px solid #32323e;border-radius:6px;padding:8px;font:12px/1.4 ui-monospace,monospace;resize:vertical;"></textarea>' +
        '<textarea class="override" rows="2" placeholder="Override — raw prompt sent straight to fal, bypasses canon" ' +
          'style="width:100%;box-sizing:border-box;margin-top:6px;background:#1c1c26;color:#e8e6e3;' +
          'border:1px solid rgba(168,85,247,0.4);border-radius:6px;padding:8px;font:12px/1.4 ui-monospace,monospace;resize:vertical;"></textarea>' +
        '<div class="ctlmsg" style="color:#55556a;font-size:11px;margin-top:6px;min-height:14px;"></div>' +
      '</div>';
  } else {
    controlsCell = '<div style="color:#55556a;font-size:11px;">no still yet</div>';
  }

  // Five columns: text | still | controls | motion | clip
  const grid =
    '<div style="display:grid;gap:14px;align-items:start;' +
    'grid-template-columns:minmax(200px,1.1fr) minmax(220px,1.3fr) minmax(190px,0.9fr) minmax(180px,0.9fr) minmax(220px,1.3fr);">' +
      '<div>' + textCell + '</div>' +
      '<div>' + stillCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">Flux still</div></div>' +
      '<div>' + controlsCell + '</div>' +
      '<div>' + motionCell + '</div>' +
      '<div>' + clipCell + '<div style="color:#55556a;font-size:11px;margin-top:4px;">Kling motion</div></div>' +
    '</div>';'''
))

# ---- EDIT 5: control handlers + judgment state, bound after render ----
# Anchor: bindMotionBoxes (from the layout patch). We extend the binder to also
# wire the still-control buttons.
EDITS.append(dict(
    marker="bindStillControls",
    old='''function bindMotionBoxes(wrap) {
  // Keep typed motion direction in the in-memory map so a poll re-render
  // (or scroll) doesn't wipe it. Backend save endpoint wires in a later phase.
  wrap.querySelectorAll("textarea.motionbox").forEach(function(t) {
    t.addEventListener("input", function() {
      window.__MOTION_EDITS[t.getAttribute("data-mkey")] = t.value;
    });
  });
}''',
    new='''function bindMotionBoxes(wrap) {
  // Keep typed motion direction in the in-memory map so a poll re-render
  // (or scroll) doesn't wipe it. Backend save endpoint wires in a later phase.
  wrap.querySelectorAll("textarea.motionbox").forEach(function(t) {
    t.addEventListener("input", function() {
      window.__MOTION_EDITS[t.getAttribute("data-mkey")] = t.value;
    });
  });
  bindStillControls(wrap);
}
function bindStillControls(wrap) {
  window.__JUDGED = window.__JUDGED || {};
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");
  function reloadStill(ctl) {
    // bust the cache so the regenerated still shows immediately
    const shot = ctl.getAttribute("data-shot");
    const n3 = String(shot).padStart(3, "0");
    const row = ctl.closest("div");  // controls cell; the still img is a sibling cell
    const grid = ctl.parentElement.parentElement;  // the 5-col grid
    const img = grid.querySelector('img[src*="shot_' + n3 + '.png"]');
    if (img) {
      const base = img.src.split("&_t=")[0];
      img.src = base + "&_t=" + Date.now();
    }
  }
  wrap.querySelectorAll(".stillctl").forEach(function(ctl) {
    const shot = parseInt(ctl.getAttribute("data-shot"), 10);
    const jkey = ctl.getAttribute("data-jkey");
    const msg = ctl.querySelector(".ctlmsg");
    const note = ctl.querySelector("textarea.note");
    const override = ctl.querySelector("textarea.override");
    const acc = ctl.querySelector("button.acc");
    const rej = ctl.querySelector("button.rej");
    const aifix = ctl.querySelector("button.aifix");
    const regen = ctl.querySelector("button.regen");

    acc.addEventListener("click", function() {
      window.__JUDGED[jkey] = "accept";
      acc.style.background = "#1c7c4a"; rej.style.background = "#2a2a36";
    });
    rej.addEventListener("click", function() {
      window.__JUDGED[jkey] = "reject";
      rej.style.background = "#7c1c1c"; acc.style.background = "#2a2a36";
    });

    async function post(endpoint, payload, label) {
      msg.style.color = "#8a8a99"; msg.textContent = label + "...";
      try {
        const r = await api(endpoint, {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(Object.assign({channel: CH, project: PR}, payload))});
        if (r.ok) {
          if (r.changed === false) {
            msg.style.color = "#8a8a99";
            msg.textContent = "AI: fine — " + (r.diagnosis || "no change");
          } else {
            msg.style.color = "#14a3b8";
            msg.textContent = (r.diagnosis ? ("fixed: " + r.diagnosis) :
                               ("regenerated (" + (r.mode || "ok") + ")"));
            reloadStill(ctl);
          }
        } else {
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (r.error || "failed");
        }
      } catch (e) {
        msg.style.color = "#d46a6a"; msg.textContent = "error: " + e;
      }
    }

    aifix.addEventListener("click", function() {
      post("/api/aifix", {shot: shot}, "AI Fix diagnosing");
    });
    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
  });
}'''
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not T.is_file():
        sys.exit(f"missing: {T}")
    text = T.read_text()

    plans, fatal = [], []
    for i, e in enumerate(EDITS, 1):
        if e["marker"] in text:
            plans.append((i, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1: plans.append((i, "apply"))
        elif n == 0: fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else: fatal.append(f"edit {i}: anchor x{n}")

    print("=== STILLS-CONTROLS PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_controls")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart: systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
