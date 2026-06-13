#!/usr/bin/env python3
"""
patch_a0_one_page.py — A0: one continuous page (persistent shell, no view-swap).

WHY
  poll() hard-swapped the whole #app between renderIdle() and renderRunning(),
  each doing app.innerHTML=... . renderRunning only handled "waiting at a gate"
  well; running/done/stopped/dead all fell into one else -> "— working…". That
  single catch-all is A3 (done shows working), the stopped-renders-oddly thing,
  and why the page felt like it teleported between screens.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  Replaces the render core (renderIdle, renderRunning, renderKey/LAST_RENDER_KEY,
  poll, clearStoryboard) with a build-once-then-update-in-place shell:
    - ensureShell(state): builds strip + Create/Launch controls + gate bar + body
      ONCE, wires the controls once. Never wiped again.
    - updateStrip / updateGatebar / updateControls / maybeUpdateBody: in-place
      updates each poll. Body re-renders only when project or stills-count changes
      (so typed notes/overrides survive a poll). Controls hide during an active
      run, reappear at idle/done/stopped.
    - poll(): ensureShell -> updateStrip -> updateGatebar -> updateControls ->
      maybeUpdateBody. Wrapped in try/catch so a transient /api/state blip leaves
      the page as-is instead of blanking it.
  gate() and toast() (the A4 forms) are re-included verbatim. Every other helper
  (beatRow, bindMotionBoxes, bindStillControls, bindAnimateButtons,
  renderStoryboard, api, loadProjectsRich, el) is left untouched.

  Phases rendered: idle | running | gate_audio | gate_stills | animating |
  assembling | done | stopped | error/stale. (error/stale render cleanly IF the
  backend sets them — that detection is A1's separate heartbeat patch.)

HOW THE EDIT IS APPLIED
  A splice between two boundary anchors (start of renderIdle, end of
  clearStoryboard). Only the two boundaries must byte-match — not the ~210 lines
  between them — which keeps the patch robust.

NOT VALIDATED BY THIS PATCH
  py_compile only proves the Python file still parses; it does NOT validate the
  embedded JS. After pulling on the box you MUST restart + run the node --check
  guard before trusting the page (commands printed at the end). This rewrites the
  render core, so do not skip it.

DISCIPLINE
  Idempotent (sentinel: `function ensureShell`). Verifies both boundary anchors
  exist exactly once and in order; backs up to .pre_a0onepage; re-compiles and
  rolls back on failure. Run from the repo root on the LAPTOP, then commit/push,
  then pull + restart + node-check on the box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "function ensureShell"

START_ANCHOR = "async function renderIdle(state) {"

CLEARSTORY_OLD = (
    "function clearStoryboard() {\n"
    '  const e = document.getElementById("storyboard"); if (e) e.remove();\n'
    '  window.__SEL_VIEW = "";\n'
    "}\n"
)

NEW_BLOCK = '''// ── A0: one continuous page — persistent shell, per-phase strip, always-visible body ──
// Built ONCE by ensureShell, then only UPDATED in place. The status strip changes
// with phase; the gate bar shows controls when a gate is waiting; the storyboard
// body always shows the selected/running project. Nothing is wiped wholesale, so
// idle/running/gate/done/stopped/stale each render cleanly (no "working…" catch-all).

function selCh() { return (window.__SEL_VIEW || "/").split("/")[0]; }
function selPr() { return (window.__SEL_VIEW || "/").split("/").slice(1).join("/"); }

const ACTIVE_PHASES = ["running", "gate_audio", "gate_stills", "animating", "assembling"];
function isActiveRun(phase) { return ACTIVE_PHASES.indexOf(phase) !== -1; }

function phaseStrip(state) {
  const p = state.phase;
  const g = state.gate;
  if (p === "idle") return {text: "Idle — pick a project and Launch.", color: "#8a8a99"};
  if (g && g.status === "waiting" && g.name === "audio")
    return {text: "Audio gate — review the voiceover, then Accept or Swap.", color: "#d4a017"};
  if (g && g.status === "waiting" && g.name === "stills")
    return {text: "Stills gate — review the stills below, then Generate Clips or Stop.", color: "#d4a017"};
  if (p === "running")    return {text: "Running — audio leg (voiceover + timing)…", color: "#5b9bd5"};
  if (p === "animating")  return {text: "Animating clips (Kling)…", color: "#5b9bd5"};
  if (p === "assembling") return {text: "Assembling the final video…", color: "#5b9bd5"};
  if (p === "done")       return {text: "✓ Complete — final video assembled. Pick a project to launch another.", color: "#1c7c4a"};
  if (p === "stopped")    return {text: "■ Stopped at the stills gate — stills kept on disk. Re-launch to resume (existing stills are skipped).", color: "#b58900"};
  if (p === "error" || p === "stale")
    return {text: "⚠ This run ended unexpectedly. Pick a project and Launch to start fresh.", color: "#d46a6a"};
  return {text: "Phase: " + p, color: "#8a8a99"};
}

function ensureShell(state) {
  let shell = document.getElementById("shell");
  if (shell) return shell;
  const app = document.getElementById("app");
  app.innerHTML = "";
  shell = document.createElement("div");
  shell.id = "shell";
  app.appendChild(shell);

  const strip = el(`<div class="panel" id="strip" style="border-left:4px solid #8a8a99;">
    <div id="stripmain" class="phase" style="font-size:14px;"></div>
    <div id="stripsub" class="phase" style="margin-top:4px;"></div>
  </div>`);
  shell.appendChild(strip);

  const create = el(`<div class="panel" id="createpanel">
    <label>New project — paste your script.md, or upload it</label>
    <textarea id="scripttext" rows="6" placeholder="paste the full script.md here (channel: header included)…"
      style="width:100%;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:10px;font:13px/1.4 ui-monospace,monospace;box-sizing:border-box;"></textarea>
    <div class="row" style="margin-top:8px">
      <input type="file" id="scriptfile" accept=".md,text/markdown,text/plain"
        style="color:#8a8a99;font-size:13px;">
    </div>
    <label>Project slug (folder name — lowercase, hyphens)</label>
    <input id="slug" placeholder="watchers-daughters"
      style="background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px 10px;min-width:280px;">
    <div class="row"><button id="create">Create project</button></div>
    <div id="createmsg" class="phase" style="margin-top:10px;white-space:pre-wrap;"></div>
  </div>`);
  shell.appendChild(create);

  const panel = el(`<div class="panel" id="launchpanel">
    <label>Channel</label>
    <select id="chan"></select>
    <label>Project (newest first)</label>
    <select id="proj"><option>—</option></select>
    <label>Mode</label>
    <select id="mode">
      <option value="dry">Dry-run (plan only, no spend)</option>
      <option value="live">Live (renders — spends fal credits)</option>
    </select>
    <div class="row"><button id="launch" disabled>Launch</button></div>
  </div>`);
  shell.appendChild(panel);

  const gatebar = document.createElement("div");
  gatebar.id = "gatebar";
  shell.appendChild(gatebar);

  const channels = state.channels || [];
  const chan = panel.querySelector("#chan");
  const proj = panel.querySelector("#proj");
  const launch = panel.querySelector("#launch");
  chan.innerHTML = '<option value="">— pick a channel —</option>' +
     channels.map(c => `<option value="${c}">${c}</option>`).join("");
  async function refreshProjects(folder, selectSlug) {
    if (!folder) { proj.innerHTML = '<option>—</option>'; launch.disabled = true; return; }
    proj.innerHTML = '<option>loading…</option>';
    const ps = await loadProjectsRich(folder);
    proj.innerHTML = '<option value="">— pick a project —</option>' +
      ps.map(p => `<option value="${p.slug}">${p.slug} · ${p.created_label} · ${p.stage}</option>`).join("");
    if (selectSlug) { proj.value = selectSlug; }
    launch.disabled = !proj.value;
  }
  chan.onchange = () => {
    launch.disabled = true; window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
    clearStoryboard(); refreshProjects(chan.value);
  };
  proj.onchange = () => {
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      window.__BODY_KEY = chan.value + "/" + proj.value + "|";  // matches idle poll key -> no double render
      renderStoryboard(chan.value, proj.value);
    } else {
      window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__"; clearStoryboard();
    }
    launch.disabled = !(chan.value && proj.value);
  };
  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    await api("/api/launch", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({channel: chan.value, project: proj.value, dry: mode === "dry"})});
    launch.textContent = "Launch";
    poll();
  };

  const fileInput = create.querySelector("#scriptfile");
  const textArea = create.querySelector("#scripttext");
  fileInput.onchange = async () => {
    const f = fileInput.files[0]; if (!f) return;
    textArea.value = await f.text();
  };
  const slugInput = create.querySelector("#slug");
  const msg = create.querySelector("#createmsg");
  create.querySelector("#create").onclick = async () => {
    const NL = String.fromCharCode(10);
    msg.textContent = "Creating — parsing + verifying…";
    const r = await api("/api/create", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({script: textArea.value, slug: slugInput.value.trim()})});
    if (!r.ok) {
      let m = "✗ " + (r.error || "create failed") + " (stage: " + (r.stage || "?") + ")";
      if (r.verify) m += NL + "  wordless beats: " + JSON.stringify(r.verify.wordless) +
                         NL + "  Mode A no-VISUAL: " + JSON.stringify(r.verify.no_visual);
      msg.textContent = m; return;
    }
    const v = r.verify;
    let g = r.git && r.git.pushed ? "pushed to GitHub" :
            (r.git && r.git.warn ? ("⚠ " + r.git.warn) : "git skipped");
    msg.textContent = "✓ created " + r.folder + "/projects/" + r.slug +
      NL + "  " + v.beats + " beats · modes " + JSON.stringify(v.modes) +
      NL + "  " + g + NL + "  selected below — pick mode and Launch.";
    chan.value = r.folder;
    window.__SEL_VIEW = r.folder + "/" + r.slug;
    window.__BODY_KEY = "__none__";
    await refreshProjects(r.folder, r.slug);
  };

  return shell;
}

function updateControls(state) {
  const run = isActiveRun(state.phase);
  const cp = document.getElementById("createpanel");
  const lp = document.getElementById("launchpanel");
  if (cp) cp.style.display = run ? "none" : "";
  if (lp) lp.style.display = run ? "none" : "";
  const chan = document.getElementById("chan");
  const proj = document.getElementById("proj");
  const launch = document.getElementById("launch");
  if (launch) launch.disabled = run || !(chan && proj && chan.value && proj.value);
}

function updateStrip(state) {
  const s = phaseStrip(state);
  const strip = document.getElementById("strip");
  const main = document.getElementById("stripmain");
  const sub = document.getElementById("stripsub");
  if (!strip || !main) return;
  strip.style.borderLeftColor = s.color;
  main.innerHTML = '<b style="color:' + s.color + ';">' + s.text + '</b>';
  if (sub) {
    sub.textContent = state.job_id
      ? ((state.channel || "") + " · " + (state.project || "") + "  ·  phase: " + state.phase)
      : "";
  }
}

function updateGatebar(state) {
  const bar = document.getElementById("gatebar");
  if (!bar) return;
  const g = state.gate;
  const waiting = g && g.status === "waiting";
  const token = waiting ? (g.name + ":" + g.status) : "none";
  if (bar.__token === token) return;   // unchanged — leave it (buttons hold no input)
  bar.__token = token;
  if (!waiting) { bar.innerHTML = ""; return; }
  var _SQ = String.fromCharCode(39);
  if (g.name === "audio") {
    const v = (g.payload && g.payload.voice_id) || "the channel voice";
    const m = (g.payload && g.payload.minutes) || "?";
    bar.innerHTML = `<div class="panel gate">
      <label>Audio gate</label>
      <div>Voiceover produced — measured <b>${m}</b> min, voice: <b>${v}</b>.</div>
      <div class="row">
        <button onclick="gate('keep')">Accept (keep this read)</button>
        <button class="secondary" onclick="gate('swap')">Swap (use my own recording)</button>
      </div></div>`;
  } else if (g.name === "stills") {
    const n = (g.payload && g.payload.stills_count) || "";
    bar.innerHTML = '<div class="panel gate">' +
      '<label>Stills gate — review before clips</label>' +
      '<div>' + n + ' stills rendered. Review the body below (AI Fix / Regenerate any that break), then decide.</div>' +
      '<div class="row">' +
        '<button onclick="gate(' + _SQ + 'go' + _SQ + ')">Generate Clips (approve stills)</button>' +
        '<button class="secondary" onclick="gate(' + _SQ + 'skip' + _SQ + ')">Stop here (keep stills, no clips)</button>' +
      '</div></div>';
  } else {
    bar.innerHTML = "";
  }
}

function bodyTarget(state) {
  // Active run -> body follows the RUN; otherwise -> the dropdown selection,
  // defaulting to the run's project if nothing is selected.
  if (isActiveRun(state.phase)) return {ch: state.channel, pr: state.project};
  return {ch: selCh() || state.channel, pr: selPr() || state.project};
}

function maybeUpdateBody(state) {
  const t = bodyTarget(state);
  if (!t.ch || !t.pr) { clearStoryboard(); window.__BODY_KEY = "__none__"; return; }
  const sc = (state.gate && state.gate.payload && state.gate.payload.stills_count) || "";
  const key = t.ch + "/" + t.pr + "|" + sc;
  if (window.__BODY_KEY === key) return;   // same project + stills count -> leave the DOM (and typed notes) alone
  window.__BODY_KEY = key;
  window.__SEL_VIEW = t.ch + "/" + t.pr;   // so still/motion controls POST to this project
  renderStoryboard(t.ch, t.pr);
}

async function poll() {
  let state;
  try { state = await api("/api/state"); }
  catch (e) { return; }   // transient blip — keep the page as-is, retry next tick
  ensureShell(state);
  updateStrip(state);
  updateGatebar(state);
  updateControls(state);
  maybeUpdateBody(state);
}

function clearStoryboard() {
  const e = document.getElementById("storyboard"); if (e) e.remove();
}

async function gate(decision) {
  const s = await api("/api/state");
  const name = s.gate ? s.gate.name : "";
  const r = await api("/api/gate/" + name, {method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({decision})});
  if (r && r.ok === false) { toast("gate error: " + (r.error || "write failed")); }
  else { toast("decision sent: " + decision); }
  poll();
}
function toast(text) {
  let tt = document.getElementById("mc_toast");
  if (!tt) {
    tt = document.createElement("div");
    tt.id = "mc_toast";
    tt.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);" +
      "background:#1c1c26;color:#e8e6e3;border:1px solid #d4a017;border-radius:8px;" +
      "padding:10px 16px;font-size:13px;z-index:9999;max-width:80vw;box-shadow:0 4px 20px rgba(0,0,0,.5);";
    document.body.appendChild(tt);
  }
  tt.textContent = text;
  tt.style.opacity = "1";
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(function(){ tt.style.opacity = "0"; }, 4000);
}
'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    for label, anchor in (("renderIdle start", START_ANCHOR),
                          ("clearStoryboard end-block", CLEARSTORY_OLD)):
        n = src.count(anchor)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm the A4 patch is applied and the box is in sync.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    i = src.index(START_ANCHOR)
    j = src.index(CLEARSTORY_OLD)
    if i >= j:
        die("anchors out of order (renderIdle should precede clearStoryboard); nothing written.")
    j_end = j + len(CLEARSTORY_OLD)

    new = src[:i] + NEW_BLOCK + src[j_end:]
    if new == src:
        die("splice produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_a0onepage")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("ensureShell missing")
    if "renderRunning" in check:
        problems.append("old renderRunning still present")
    if "renderIdle" in check:
        problems.append("old renderIdle still present")
    if 'onclick="gate(' not in check:
        problems.append("gate buttons missing")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   render core replaced: persistent shell + per-phase strip + always-visible body")
    print("   removed: renderIdle / renderRunning / renderKey whole-view swap")
    print()
    print("AFTER you pull on the box, you MUST restart + node-check before trusting it:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   print(\"script blocks:\", len(b))")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
