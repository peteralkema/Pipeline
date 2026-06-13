#!/usr/bin/env python3
"""
patch_mc_gate_body.py — Phase 3f: the stills gate IS the storyboard.

Until now the live stills gate showed a bare panel ("Rich review body lands in
the next phase"). But build_state already attaches state.view at gate_stills, and
beatRow/bindStillControls already exist. This wires them together: when the gate
is the stills gate, render the full five-column storyboard body (text | still |
controls | motion | clip, Mode B strip below) from state.view.beats, with the
controls live, and put Generate Clips / Skip BELOW the body where "approve after
reviewing" belongs.

No re-fetch: the view is already in the polled state, so we render rows directly.
We set window.__SEL_VIEW (channel/project) so bindStillControls posts to the right
project, and call bindStillControls after injecting the rows.

One edit to renderRunning's stills-gate branch (+ a post-render bind hook).

Idempotent (marker), backs up to .pre_gatebody, no escaped newlines in JS.

Run on the box:
  python shared/mission_control/patch_mc_gate_body.py --check
  python shared/mission_control/patch_mc_gate_body.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# --- EDIT 1: stills-gate branch renders the storyboard body from state.view ---
# Replace the bare stills panel with a body + buttons-below. We stash the rows
# HTML and the channel/project on the state so the app.innerHTML assembly (which
# follows) and a post-render bind can use them. Simpler: build gateHtml as the
# body + buttons, then bind after innerHTML is set (see edit 2).
EDITS.append(dict(
    marker="STILLS GATE BODY",
    old='''  } else if (g && g.status === "waiting" && g.name === "stills") {
    const n = (g.payload && g.payload.stills_count) || "?";
    gateHtml = `<div class="panel gate">
      <label>Stills gate</label>
      <div>${n} stills rendered. (Rich review body lands in the next phase.)</div>
      <div class="row">
        <button onclick="gate('go')">Generate Clips (approve stills)</button>
        <button class="secondary" onclick="gate('skip')">Skip</button>
      </div></div>`;
  }''',
    new='''  } else if (g && g.status === "waiting" && g.name === "stills") {
    // STILLS GATE BODY — the gate IS the storyboard. Render the five-column
    // body from the view already attached to state (no re-fetch), controls live.
    const view = state.view || {};
    const beats = view.beats || [];
    const ch = state.channel, pr = state.project;
    window.__SEL_VIEW = ch + "/" + pr;  // so bindStillControls posts to this project
    const n = beats.length || (g.payload && g.payload.stills_count) || "?";
    const head = '<div class="panel gate">' +
      '<label>Stills gate — review before clips</label>' +
      '<div>' + n + ' stills rendered. Review (AI Fix / Regenerate any that break), ' +
      'then approve.</div>' +
      '<div class="row">' +
        '<button onclick="gate(\\'go\\')">Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick="gate(\\'skip\\')">Skip</button>' +
      '</div></div>';
    const body = '<div id="storyboard" class="panel" style="max-width:2400px;">' +
      '<label>Storyboard — ' + pr + ' · ' + n + ' beats</label>' +
      beats.map(b => beatRow(b, ch, pr)).join("") + '</div>';
    // buttons appear BOTH above (quick approve) and the body below them.
    gateHtml = head + body;
    window.__BIND_GATE_BODY = true;  // edit 2 binds controls after innerHTML
  }'''
))

# --- EDIT 2: after app.innerHTML is set in renderRunning, bind the controls ---
EDITS.append(dict(
    marker="if (window.__BIND_GATE_BODY)",
    old='''  app.innerHTML = `<div class="panel">
      <div class="phase">job <code>${state.job_id}</code></div>
      <div class="phase">${state.channel} · ${state.project}</div>
      <div class="phase">phase: <b>${state.phase}</b>
        ${(!g||g.status!=="waiting") ? '<span class="spin"> — working…</span>' : ''}</div>
    </div>` + gateHtml;
}''',
    new='''  app.innerHTML = `<div class="panel">
      <div class="phase">job <code>${state.job_id}</code></div>
      <div class="phase">${state.channel} · ${state.project}</div>
      <div class="phase">phase: <b>${state.phase}</b>
        ${(!g||g.status!=="waiting") ? '<span class="spin"> — working…</span>' : ''}</div>
    </div>` + gateHtml;
  if (window.__BIND_GATE_BODY) {
    window.__BIND_GATE_BODY = false;
    const sb = document.getElementById("storyboard");
    if (sb && typeof bindMotionBoxes === "function") bindMotionBoxes(sb);
  }
}'''
))

# --- EDIT 3: the poll-clobber guard must let the gate body re-render when a
# control changes a still. renderKey already includes __SEL_VIEW; ensure the
# stills-gate view re-renders each poll so a regenerated still refreshes. We add
# the gate's stills view token to renderKey so it doesn't get suppressed.
EDITS.append(dict(
    marker="g.name, g.status, gate_view_token",
    old='''  const g = state.gate || {};
  return [state.phase, state.job_id, g.name, g.status,
          window.__SEL_VIEW || ""].join("|");''',
    new='''  const g = state.gate || {};
  // gate_view_token: at the stills gate, key on stills_count so the body
  // renders once when the gate opens (controls then drive in-place reloads).
  const gate_view_token = (g.name === "stills" && g.payload)
                          ? ("stills:" + (g.payload.stills_count || "")) : "";
  return [state.phase, state.job_id, g.name, g.status,
          window.__SEL_VIEW || "", gate_view_token].join("|");'''
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

    print("=== GATE-BODY PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_gatebody")
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
