#!/usr/bin/env python3
"""
patch_mc_animate.py — Phase 4: once-off clip render from the motion column.

Adds the motion-direction -> Kling seam Peter wanted: type motion direction in
the column-4 textarea, click "Render this clip", and animate_still runs for that
ONE shot. The batch later skips it (clip.exists() and not --force). Post-batch
re-render works identically.

SERVER edit:
  /api/animate {shot:int, motion_prompt:str, channel, project}
  -> resolves project per-request (active job or body) like /api/restill
  -> imports animate_still(still_path, motion_prompt, out_path) from
     recreation_pipeline (which already owns fal_client + FAL_KEY)
  -> writes clips/shot_NNN.mp4, returns {ok, shot}

PAGE edit:
  a "Render this clip" button under the motion textarea (col 4), which reads the
  textarea's CURRENT value as the motion prompt, shows a spinner (Kling is slow),
  and reloads the clip <video> in place when done.

ALL new JS quotes built via String.fromCharCode (no literal quote/backslash in
the served JS — the lesson from the gate-button breaks). Verify the served page
with node --check before refreshing.

Idempotent (markers), backs up to .pre_animate.

Run on the box:
  python shared/mission_control/patch_mc_animate.py --check
  python shared/mission_control/patch_mc_animate.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# ---- EDIT 1: module import of animate_still (lazy, like the restill import) ----
EDITS.append(dict(
    marker="_ANIMATE_OK",
    old='''_FLUX_MODEL = "fal-ai/flux-pro/v1.1"''',
    new='''try:
    from recreation_pipeline import animate_still as _animate_still
    _ANIMATE_OK = True
except Exception as _ae:
    _ANIMATE_OK = False
    _ANIMATE_IMPORT_ERR = str(_ae)

_FLUX_MODEL = "fal-ai/flux-pro/v1.1"''',
))

# ---- EDIT 2: POST routing — add /api/animate ----
EDITS.append(dict(
    marker='path == "/api/animate"',
    old='''        if path == "/api/restill":
            self._handle_restill(body); return
        if path == "/api/aifix":
            self._handle_aifix(body); return''',
    new='''        if path == "/api/restill":
            self._handle_restill(body); return
        if path == "/api/aifix":
            self._handle_aifix(body); return
        if path == "/api/animate":
            self._handle_animate(body); return''',
))

# ---- EDIT 3: the _handle_animate method (before do_POST, like the others) ----
EDITS.append(dict(
    marker="def _handle_animate",
    old='''    def _handle_restill(self, body):''',
    new='''    def _handle_animate(self, body):
        if not _ANIMATE_OK:
            self._json(503, {"ok": False,
                "error": f"animate unavailable: {_ANIMATE_IMPORT_ERR}"}); return
        shot_idx = body.get("shot")
        motion_prompt = (body.get("motion_prompt") or "").strip()
        if not isinstance(shot_idx, int):
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        if not motion_prompt:
            motion_prompt = ("Slow, subtle atmospheric motion. Drifting light, "
                             "faint air. No fast movement, no camera shake.")
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        ctx = _stills_ctx(ch, pr)
        stills_dir = ctx["stills_dir"]
        still_path = stills_dir / f"shot_{shot_idx:03d}.png"
        if not still_path.exists():
            self._json(404, {"ok": False, "error": f"still not found: {still_path.name}"}); return
        # clips dir is the sibling of stills under modea/
        clips_dir = stills_dir.parent / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        out_path = clips_dir / f"shot_{shot_idx:03d}.mp4"
        sys.stderr.write(f"[Animate] shot {shot_idx:03d} (once-off) ...\\n")
        try:
            _animate_still(still_path, motion_prompt, out_path)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"animate failed: {e}"}); return
        self._json(200, {"ok": True, "shot": shot_idx}); return

    def _handle_restill(self, body):'''
))

# ---- EDIT 4: motion cell gets a "Render this clip" button under the textarea ----
# Anchor: the motionCell definition from the layout patch. We append a button.
EDITS.append(dict(
    marker="Render this clip",
    old='''  const motionCell =
    '<textarea data-mkey="' + mkey + '" class="motionbox" rows="6" ' +
    'placeholder="motion direction (blank = engine default)…" ' +
    'style="width:100%;box-sizing:border-box;background:#1c1c26;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:8px;padding:10px;' +
    'font:13px/1.45 ui-monospace,monospace;resize:vertical;">' +
    escapeHtml(stored) + '</textarea>' +
    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>';''',
    new='''  const _canAnimate = (hasStill && shot != null);
  const motionCell =
    '<div class="motioncell" data-shot="' + (shot==null?'':shot) + '">' +
    '<textarea data-mkey="' + mkey + '" class="motionbox" rows="5" ' +
    'placeholder="motion direction (blank = engine default)…" ' +
    'style="width:100%;box-sizing:border-box;background:#1c1c26;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:8px;padding:10px;' +
    'font:13px/1.45 ui-monospace,monospace;resize:vertical;">' +
    escapeHtml(stored) + '</textarea>' +
    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>' +
    (_canAnimate ?
      ('<button class="animbtn" style="width:100%;margin-top:8px;background:#7a4ddb;' +
       'color:#fff;border:0;border-radius:6px;padding:9px;cursor:pointer;' +
       'font:13px ui-monospace,monospace;font-weight:600;">Render this clip</button>' +
       '<div class="animmsg" style="color:#55556a;font-size:11px;margin-top:6px;min-height:14px;"></div>')
      : '') +
    '</div>';'''
))

# ---- EDIT 5: bind the animate buttons (extend bindStillControls) ----
# Anchor: end of bindStillControls (the regen handler is the last thing). We add
# the animate binding as a sibling pass. All quotes via _SQ-style fromCharCode.
EDITS.append(dict(
    marker="bindAnimateButtons",
    old='''    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
  });
}''',
    new='''    regen.addEventListener("click", function() {
      post("/api/restill", {shot: shot, note: note.value, override: override.value},
           override.value.trim() ? "Regenerating (override)" : "Regenerating");
    });
  });
  bindAnimateButtons(wrap);
}
function bindAnimateButtons(wrap) {
  const CH = (window.__SEL_VIEW || "/").split("/")[0];
  const PR = (window.__SEL_VIEW || "/").split("/").slice(1).join("/");
  wrap.querySelectorAll(".motioncell").forEach(function(cell) {
    const btn = cell.querySelector("button.animbtn");
    if (!btn) return;
    const shot = parseInt(cell.getAttribute("data-shot"), 10);
    const box = cell.querySelector("textarea.motionbox");
    const msg = cell.querySelector(".animmsg");
    btn.addEventListener("click", async function() {
      btn.disabled = true; const label0 = btn.textContent;
      btn.textContent = "Rendering (Kling)…";
      msg.style.color = "#8a8a99"; msg.textContent = "animating — this takes a bit…";
      try {
        const r = await api("/api/animate", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: CH, project: PR, shot: shot,
                                motion_prompt: box.value})});
        if (r.ok) {
          msg.style.color = "#7a4ddb"; msg.textContent = "clip rendered";
          // reload the clip <video> in this row, cache-busted
          const n3 = String(shot).padStart(3, "0");
          const grid = cell.parentElement;  // the 5-col grid
          const vid = grid.querySelector('video[src*="shot_' + n3 + '.mp4"]');
          if (vid) {
            const base = vid.src.split("&_t=")[0];
            vid.src = base + "&_t=" + Date.now(); vid.load();
          } else {
            // no clip cell existed yet (still-only beat) — soft refresh on next poll
            msg.textContent = "clip rendered — refresh to view";
          }
        } else {
          msg.style.color = "#d46a6a"; msg.textContent = "error: " + (r.error || "failed");
        }
      } catch (e) {
        msg.style.color = "#d46a6a"; msg.textContent = "error: " + e;
      }
      btn.disabled = false; btn.textContent = label0;
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

    print("=== ANIMATE PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_animate")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in enumerate(EDITS, 1):
        if i not in to_apply: continue
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart, THEN node --check the served page before refreshing:")
    print("  systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
