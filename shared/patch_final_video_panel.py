#!/usr/bin/env python3
"""
patch_final_video_panel.py -- FINAL VIDEO panel in Mission Control (v0.7).

WHY
  When a run reaches `done` the assembled video is just a file on disk. This puts it
  in the page: autoplaying, with its metadata and a working Download button -- the
  first piece of the FINAL VIDEO UPLOAD TO STUDIO panel from the wireframe. The
  UPLOAD button is present but DISABLED (needs auth.py + /api/upload, next session);
  Download needs no auth and works now.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. BACKEND FIX: _serve_asset's "video" base was paths["modea"], but final_video.mp4
     lives at the PROJECT ROOT -> change base to paths["project"] so /video/ serves it.
  2. NEW ROUTE: /api/meta?channel=&project= -> reads beats_full.json header and returns
     {title, description, tags}. Mirrors the render_policy GET pattern. (GET dispatch +
     a _handle_meta_get method.)
  3. PAGE JS: renderDonePanel(state) builds the panel; maybeUpdateBody renders it ABOVE
     the storyboard when phase == "done". Autoplaying <video> via /video/, title/desc/
     tags from /api/meta, a Download button (<a download>), and a disabled UPLOAD stub.
  4. APP_VERSION -> v0.7.

DISCIPLINE
  Pure ASCII. Idempotent (sentinel: `def _handle_meta_get`). Anchors verified once;
  .pre_panel backup; py_compile + JS-shape checks; rollback on any failure. Requires
  v0.6 present (A1 applied first).
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "def _handle_meta_get"

# --- 1. backend: video base -> project root ---------------------------------
OLD_BASE = '''        base = {"stills": paths["stills_dir"], "clips": paths["clips_dir"],
                "video": paths["modea"]}.get(kind)'''
NEW_BASE = '''        base = {"stills": paths["stills_dir"], "clips": paths["clips_dir"],
                "video": paths["project"]}.get(kind)'''

# --- 2a. GET dispatch: add /api/meta (next to render_policy GET) -------------
OLD_GET = '''        if path == "/api/render_policy":
            q = parse_qs(parsed.query)
            self._handle_render_policy_get(q.get("channel", [None])[0],
                                           q.get("project", [None])[0]); return'''
NEW_GET = '''        if path == "/api/render_policy":
            q = parse_qs(parsed.query)
            self._handle_render_policy_get(q.get("channel", [None])[0],
                                           q.get("project", [None])[0]); return
        if path == "/api/meta":
            q = parse_qs(parsed.query)
            self._handle_meta_get(q.get("channel", [None])[0],
                                  q.get("project", [None])[0]); return'''

# --- 2b. the handler: read beats_full.json header ---------------------------
# Insert just before _handle_render_policy_get.
OLD_HANDLER = '''    def _handle_render_policy_get(self, ch, pr):
        """Read TIERED RENDER N for a project: render_policy.json kling_count (default 40)."""'''
NEW_HANDLER = '''    def _handle_meta_get(self, ch, pr):
        """Read the YouTube metadata (title/description/tags) from the project's
        beats_full.json header. Also reports whether final_video.mp4 exists."""
        if not (ch and pr):
            self._json(400, {"error": "channel + project required"}); return
        try:
            paths = resolve_paths(ch, pr, _REPO)
            bf = Path(paths["project"]) / "beats_full.json"
            header = {}
            if bf.exists():
                data = json.load(open(bf))
                header = data.get("header", {}) if isinstance(data, dict) else {}
            tags = header.get("tags", [])
            if isinstance(tags, list):
                tags = ", ".join(str(t) for t in tags)
            video = Path(paths["project"]) / "final_video.mp4"
            self._json(200, {
                "ok": True,
                "title": header.get("title", ""),
                "description": header.get("description", ""),
                "tags": tags,
                "has_video": video.exists(),
                "video_name": "final_video.mp4",
            })
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _handle_render_policy_get(self, ch, pr):
        """Read TIERED RENDER N for a project: render_policy.json kling_count (default 40)."""'''

# --- 3a. page JS: render the done-panel above the storyboard -----------------
OLD_BODY = '''function maybeUpdateBody(state) {
  const t = bodyTarget(state);
  if (!t.ch || !t.pr) { clearStoryboard(); window.__BODY_KEY = "__none__"; return; }
  const sc = (state.gate && state.gate.payload && state.gate.payload.stills_count) || "";
  const key = t.ch + "/" + t.pr + "|" + sc;
  if (window.__BODY_KEY === key) return;   // same project + stills count -> leave the DOM (and typed notes) alone
  window.__BODY_KEY = key;
  window.__SEL_VIEW = t.ch + "/" + t.pr;   // so still/motion controls POST to this project
  renderStoryboard(t.ch, t.pr);
}'''
NEW_BODY = '''function maybeUpdateBody(state) {
  const t = bodyTarget(state);
  if (!t.ch || !t.pr) { clearStoryboard(); removeDonePanel(); window.__BODY_KEY = "__none__"; return; }
  const sc = (state.gate && state.gate.payload && state.gate.payload.stills_count) || "";
  const key = t.ch + "/" + t.pr + "|" + sc + "|" + (state.phase || "");
  if (window.__BODY_KEY === key) return;   // same project + stills count + phase -> leave the DOM alone
  window.__BODY_KEY = key;
  window.__SEL_VIEW = t.ch + "/" + t.pr;   // so still/motion controls POST to this project
  if (state.phase === "done") { renderDonePanel(t.ch, t.pr); } else { removeDonePanel(); }
  renderStoryboard(t.ch, t.pr);
}

function removeDonePanel() {
  const e = document.getElementById("donepanel"); if (e) e.remove();
}

async function renderDonePanel(ch, pr) {
  removeDonePanel();
  const app = document.getElementById("app");
  if (!app) return;
  const q = "?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr) + "&key=" + KEY;
  let meta = {};
  try { meta = await api("/api/meta?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr)); }
  catch (e) { meta = {}; }
  if (!meta || !meta.has_video) return;   // no assembled video -> no panel
  const vsrc = "/video/" + encodeURIComponent(meta.video_name || "final_video.mp4") + q;
  const esc = function(s){ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); };
  const panel = document.createElement("div");
  panel.id = "donepanel";
  panel.className = "panel";
  panel.style.cssText = "max-width:720px;border:1px solid #d4a017;";
  panel.innerHTML =
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">' +
      '<span style="width:8px;height:8px;border-radius:50%;background:#ff0000;display:inline-block;"></span>' +
      '<b style="letter-spacing:.04em;">FINAL VIDEO &mdash; UPLOAD TO STUDIO</b></div>' +
    '<video src="' + vsrc + '" autoplay muted loop playsinline ' +
      'style="width:100%;border-radius:8px;background:#000;display:block;margin-bottom:8px;"></video>' +
    '<div style="margin-bottom:14px;">' +
      '<a href="' + vsrc + '" download style="display:inline-block;background:#2a2a36;color:#e8e6e3;' +
        'text-decoration:none;border-radius:6px;padding:8px 14px;font-weight:600;font-size:13px;">' +
        '&#8595; Download final video</a></div>' +
    '<label>Title</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:8px;">' + esc(meta.title) + '</div>' +
    '<label>Description</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:8px;white-space:pre-wrap;">' + esc(meta.description) + '</div>' +
    '<label>Tags</label><div class="field" style="border:1px solid #32323e;border-radius:6px;' +
      'background:#1c1c26;padding:8px 10px;margin-bottom:14px;">' + esc(meta.tags) + '</div>' +
    '<button disabled title="Upload wiring next session (auth + /api/upload)" ' +
      'style="background:#ff0000;opacity:.4;cursor:not-allowed;">Upload to YouTube Studio</button>' +
    '<div style="color:#8a8a99;font-size:11px;margin-top:6px;">Upload goes live once auth + /api/upload are wired ' +
      '(next session). Download works now.</div>';
  // insert ABOVE the storyboard (or at the end of #app if no storyboard yet)
  const sb = document.getElementById("storyboard");
  if (sb) { app.insertBefore(panel, sb); } else { app.appendChild(panel); }
}'''

# --- 3b. version bump --------------------------------------------------------
OLD_VER = '''APP_VERSION = "v0.6"  # hand-bumped each shipped page change; pairs with the auto git SHA'''
NEW_VER = '''APP_VERSION = "v0.7"  # hand-bumped each shipped page change; pairs with the auto git SHA'''


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found -- run from the repo root on the laptop.")
    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) -- no changes made.")
        return
    if OLD_VER not in src:
        die("APP_VERSION v0.6 anchor not found -- apply patch_a1_heartbeat.py (v0.6) first. Nothing written.")

    edits = [
        ("video base", OLD_BASE, NEW_BASE),
        ("GET dispatch", OLD_GET, NEW_GET),
        ("meta handler", OLD_HANDLER, NEW_HANDLER),
        ("maybeUpdateBody", OLD_BODY, NEW_BODY),
        ("version bump", OLD_VER, NEW_VER),
    ]
    for label, old, _ in edits:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND -- file shape changed; nothing written.")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) -- ambiguous; nothing written.")

    new = src
    for _, old, repl in edits:
        new = new.replace(old, repl)

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_panel")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    chk = TARGET.read_text()
    problems = []
    if MARKER not in chk: problems.append("meta handler missing")
    if "renderDonePanel" not in chk: problems.append("renderDonePanel missing")
    if '"video": paths["project"]' not in chk: problems.append("video base not fixed")
    if 'APP_VERSION = "v0.7"' not in chk: problems.append("version not bumped")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") -- restored.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile -- restored.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   /video/ now serves the project-root final_video.mp4; /api/meta added;")
    print("   done-phase panel with autoplay video + metadata + Download (Upload disabled)")
    print()
    print("AFTER pull on the box: restart, verify v0.7, node-check:")
    print("   systemctl --user restart mission-control.service && sleep 1")
    print("   curl -s \"http://127.0.0.1:8002/api/state?key=fh2026\" | python3 -c \"import sys,json;d=json.load(sys.stdin);print(d.get('version'),d.get('sha'))\"")
    print("   git rev-parse --short HEAD   # must match; version must read v0.7")
    print("   curl -s \"http://127.0.0.1:8002/api/meta?channel=sacred-dawn&project=test-run-line3&key=fh2026\"")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
