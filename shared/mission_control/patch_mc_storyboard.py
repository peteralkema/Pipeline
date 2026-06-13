#!/usr/bin/env python3
"""
patch_mc_storyboard.py — Phase 3: the storyboard body (view any project's beats/stills).

Four edits to pipeline_server.py:
  1. _serve_asset accepts ?channel=&project= (browse ANY project's stills/clips,
     not just the active job's) — falls back to active job if absent.
  2. add GET /api/view?channel=&project= -> build_beats_view on demand.
  3. renderKey includes a selected-project token (so picking a project re-renders).
  4. renderIdle: on project select, fetch /api/view and render the beat-row
     storyboard body (still + narration + duration + rendered prompt + provenance).

Idempotent (markers), backs up to .pre_storyboard, refuses half-apply.
NO escaped newlines in JS (uses array.join / template literals only).

Run on the box:
  python shared/mission_control/patch_mc_storyboard.py --check
  python shared/mission_control/patch_mc_storyboard.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# --- 1. _serve_asset: accept channel/project query params ---
EDITS.append(dict(
    marker="def _serve_asset(self, kind: str, rel: str, channel=None, project=None)",
    old='''    def _serve_asset(self, kind: str, rel: str):
        jid = active_job_id()
        if not jid:
            self.send_response(404); self.end_headers(); return
        rec = read_job(jid, _REPO)
        paths = resolve_paths(rec["channel"], rec["project"], _REPO)''',
    new='''    def _serve_asset(self, kind: str, rel: str, channel=None, project=None):
        # Resolve from explicit channel/project (browse any project) or fall
        # back to the active job. No active job + no params -> 404.
        if not (channel and project):
            jid = active_job_id()
            if not jid:
                self.send_response(404); self.end_headers(); return
            rec = read_job(jid, _REPO)
            channel, project = rec["channel"], rec["project"]
        paths = resolve_paths(channel, project, _REPO)''',
))

# --- 2. add /api/view endpoint + pass query params to _serve_asset ---
EDITS.append(dict(
    marker='path == "/api/view"',
    old='''        if path == "/api/state":
            self._json(200, build_state()); return
        if path.startswith("/stills/"):
            self._serve_asset("stills", path[len("/stills/"):]); return
        if path.startswith("/clips/"):
            self._serve_asset("clips", path[len("/clips/"):]); return
        if path.startswith("/video/"):
            self._serve_asset("video", path[len("/video/"):]); return''',
    new='''        if path == "/api/state":
            self._json(200, build_state()); return
        if path == "/api/view":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]; pr = q.get("project", [""])[0]
            if not ch or not pr:
                self._json(400, {"error": "channel + project required"}); return
            try:
                self._json(200, build_beats_view(ch, pr, _REPO))
            except Exception as e:
                self._json(500, {"error": str(e)})
            return
        if path.startswith("/stills/"):
            q = parse_qs(parsed.query)
            self._serve_asset("stills", path[len("/stills/"):],
                              q.get("channel",[None])[0], q.get("project",[None])[0]); return
        if path.startswith("/clips/"):
            q = parse_qs(parsed.query)
            self._serve_asset("clips", path[len("/clips/"):],
                              q.get("channel",[None])[0], q.get("project",[None])[0]); return
        if path.startswith("/video/"):
            q = parse_qs(parsed.query)
            self._serve_asset("video", path[len("/video/"):],
                              q.get("channel",[None])[0], q.get("project",[None])[0]); return''',
))

# --- 3. renderKey includes a selected-project token ---
EDITS.append(dict(
    marker="window.__SEL_VIEW",
    old='''function renderKey(state) {
  // re-render only when something the user SEES changes:
  // phase, or which gate is waiting, or its status.
  const g = state.gate || {};
  return [state.phase, state.job_id, g.name, g.status].join("|");
}''',
    new='''function renderKey(state) {
  // re-render only when something the user SEES changes. Include the idle
  // project selection so picking a project (no job) triggers a body render.
  const g = state.gate || {};
  return [state.phase, state.job_id, g.name, g.status,
          window.__SEL_VIEW || ""].join("|");
}''',
))

# --- 4. renderIdle: render the storyboard body on project select ---
# Anchor: the proj.onchange line inside renderIdle. Replace it with a handler
# that fetches /api/view and renders beat rows below the panels.
EDITS.append(dict(
    marker="renderStoryboard",
    old='''  chan.onchange = () => { launch.disabled = true; refreshProjects(chan.value); };
  proj.onchange = () => { launch.disabled = !(chan.value && proj.value); };''',
    new='''  chan.onchange = () => { launch.disabled = true; clearStoryboard(); refreshProjects(chan.value); };
  proj.onchange = () => {
    launch.disabled = !(chan.value && proj.value);
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      renderStoryboard(chan.value, proj.value);
    } else { clearStoryboard(); }
  };'''
))

# --- 4b. append the storyboard render functions before the closing of <script> ---
# We hook them in by replacing the poll()/setInterval tail with the same tail
# PLUS the new functions (so they exist in scope).
EDITS.append(dict(
    marker="async function renderStoryboard",
    old='''poll();
setInterval(poll, 2500);''',
    new='''function clearStoryboard() {
  const e = document.getElementById("storyboard"); if (e) e.remove();
  window.__SEL_VIEW = "";
}
function beatRow(b, ch, pr) {
  const a = b.assets || {};
  const shot = a.still && a.still.engine_shot;
  const hasStill = a.still && a.still.exists;
  const hasClip = a.clip && a.clip.exists;
  const q = "?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr) +
            "&key=" + KEY;
  let media;
  if (hasClip) {
    media = '<video src="/clips/shot_' + String(shot).padStart(3,"0") + '.mp4' + q +
            '" muted loop autoplay playsinline style="width:160px;border-radius:6px;background:#000"></video>';
  } else if (hasStill) {
    media = '<img src="/stills/shot_' + String(shot).padStart(3,"0") + '.png' + q +
            '" loading="lazy" style="width:160px;border-radius:6px;background:#000">';
  } else {
    media = '<div style="width:160px;height:90px;border-radius:6px;background:#1c1c26;' +
            'display:flex;align-items:center;justify-content:center;color:#55556a;font-size:12px;">not rendered</div>';
  }
  const dur = (b.duration_s != null) ? (b.duration_s.toFixed(2) + "s") : "—";
  const prompt = b.visual_rendered || b.visual_authored || "";
  const rows = [
    '<div style="display:flex;gap:14px;padding:12px 0;border-bottom:1px solid #1e1e28;">',
    '<div style="flex:0 0 160px;">' + media +
      '<div style="color:#55556a;font-size:11px;margin-top:4px;">beat ' + b.index +
      ' · shot ' + (shot==null?"—":shot) + ' · ' + (b.stage||"") + '</div></div>',
    '<div style="flex:1;min-width:0;">',
      '<div style="color:#e8e6e3;font-size:13px;">' + (b.narration||"") + '</div>',
      '<div style="color:#8a8a99;font-size:12px;margin-top:6px;font-style:italic;">' + prompt + '</div>',
      '<div style="color:#55556a;font-size:11px;margin-top:6px;">' + dur +
        ' · ' + (b.mode||"") + ' · look: ' + (b.look_resolved||"") + '</div>',
    '</div>',
    '</div>'
  ];
  return rows.join("");
}
async function renderStoryboard(ch, pr) {
  clearStoryboard();
  const app = document.getElementById("app");
  const wrap = document.createElement("div");
  wrap.id = "storyboard";
  wrap.className = "panel";
  wrap.innerHTML = '<span class="spin">loading storyboard…</span>';
  app.appendChild(wrap);
  let view;
  try {
    view = await api("/api/view?channel=" + encodeURIComponent(ch) +
                     "&project=" + encodeURIComponent(pr));
  } catch (e) { wrap.innerHTML = "view error: " + e; return; }
  if (view.error) { wrap.innerHTML = "view error: " + view.error; return; }
  const beats = view.beats || [];
  const head = '<label>Storyboard — ' + pr + ' · ' + beats.length + ' beats · ' +
               (view.has_mode_b ? "dual-mode" : "Mode A") + '</label>';
  wrap.innerHTML = head + beats.map(b => beatRow(b, ch, pr)).join("");
}
poll();
setInterval(poll, 2500);'''
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

    print("=== STORYBOARD PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_storyboard")
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
