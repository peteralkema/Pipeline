#!/usr/bin/env python3
"""
patch_mc_ingest.py — wire the Create front door + rich dropdown into the server.

Six edits to pipeline_server.py:
  1. import ingest helpers
  2. replace list_projects() with a thin wrapper over ingest.rich_list_projects
  3. /api/projects returns the rich objects (slug/stage/created_label)
  4. add /api/create POST endpoint
  5. renderIdle JS: Create panel (paste + upload + slug) + rich project labels
  6. (no-op marker) — covered by 5

Idempotent: each edit has a marker; skips applied; aborts if any anchor missing.
Backs up pipeline_server.py -> .pre_ingest.

Run on the box from repo root:
  python shared/mission_control/patch_mc_ingest.py --check
  python shared/mission_control/patch_mc_ingest.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"


EDITS = []

# --- 1. import ingest ---
EDITS.append(dict(
    marker="from ingest import",
    old="from build_view import build_beats_view, resolve_paths",
    new="""from build_view import build_beats_view, resolve_paths
from ingest import create_project, rich_list_projects""",
))

# --- 2. rich list_projects ---
EDITS.append(dict(
    marker="return [p[\"slug\"] for p in rich_list_projects",
    old="""def list_projects(channel: str) -> list[str]:
    # channel here is a folder name (hyphen form). projects live under projects/.
    pdir = _REPO / channel / "projects"
    if not pdir.is_dir():
        return []
    return sorted(d.name for d in pdir.iterdir()
                  if d.is_dir() and (d / "beats_full.json").is_file()
                  or (d.is_dir() and (d / "script.md").is_file()))""",
    new="""def list_projects(channel: str) -> list[str]:
    # back-compat: plain slug list (newest-first via rich_list_projects)
    return [p["slug"] for p in rich_list_projects(channel)]""",
))

# --- 3. /api/projects returns rich objects ---
EDITS.append(dict(
    marker='"projects_rich"',
    old="""        if path == "/api/projects":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]
            self._json(200, {"projects": list_projects(ch)}); return""",
    new="""        if path == "/api/projects":
            q = parse_qs(parsed.query)
            ch = q.get("channel", [""])[0]
            rich = rich_list_projects(ch)
            self._json(200, {"projects": [p["slug"] for p in rich],
                             "projects_rich": rich}); return""",
))

# --- 4. /api/create POST endpoint (insert before /api/launch handler) ---
EDITS.append(dict(
    marker='path == "/api/create"',
    old="""        if path == "/api/launch":""",
    new="""        if path == "/api/create":
            script_text = body.get("script", "")
            slug = (body.get("slug") or "").strip()
            if not script_text.strip():
                self._json(400, {"ok": False, "error": "empty script"}); return
            result = create_project(script_text, slug, do_git=True)
            self._json(200 if result.get("ok") else 422, result); return

        if path == "/api/launch":""",
))

# --- 5. renderIdle JS: Create panel + rich labels ---
EDITS.append(dict(
    marker="CREATE PANEL",
    old="""async function renderIdle(state) {
  const app = document.getElementById("app");
  const channels = state.channels || [];
  app.innerHTML = "";
  const panel = el(`<div class="panel">
    <label>Channel</label>
    <select id="chan"></select>
    <label>Project</label>
    <select id="proj"><option>—</option></select>
    <label>Mode</label>
    <select id="mode">
      <option value="dry">Dry-run (plan only, no spend)</option>
      <option value="live">Live (renders — spends fal credits)</option>
    </select>
    <div class="row"><button id="launch" disabled>Launch</button></div>
  </div>`);
  app.appendChild(panel);
  const chan = panel.querySelector("#chan");
  const proj = panel.querySelector("#proj");
  const launch = panel.querySelector("#launch");
  chan.innerHTML = '<option value="">— pick a channel —</option>' +
     channels.map(c=>`<option value="${c}">${c}</option>`).join("");
  chan.onchange = async () => {
    proj.innerHTML = '<option>loading…</option>';
    launch.disabled = true;
    if (!chan.value) { proj.innerHTML='<option>—</option>'; return; }
    const ps = await loadProjects(chan.value);
    proj.innerHTML = '<option value="">— pick a project —</option>' +
      ps.map(p=>`<option value="${p}">${p}</option>`).join("");
  };
  proj.onchange = () => { launch.disabled = !(chan.value && proj.value); };
  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    await api("/api/launch", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({channel:chan.value, project:proj.value, dry: mode==="dry"})});
    poll();
  };
}""",
    new="""async function loadProjectsRich(folder) {
  const r = await api("/api/projects?channel="+encodeURIComponent(folder));
  return r.projects_rich || [];
}
async function renderIdle(state) {
  const app = document.getElementById("app");
  const channels = state.channels || [];
  app.innerHTML = "";

  // ---- CREATE PANEL (paste script.md text OR upload .md, + slug) ----
  const create = el(`<div class="panel">
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
  app.appendChild(create);

  // ---- LAUNCH PANEL (pick existing project) ----
  const panel = el(`<div class="panel">
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
  app.appendChild(panel);

  const chan = panel.querySelector("#chan");
  const proj = panel.querySelector("#proj");
  const launch = panel.querySelector("#launch");
  chan.innerHTML = '<option value="">— pick a channel —</option>' +
     channels.map(c=>`<option value="${c}">${c}</option>`).join("");
  async function refreshProjects(folder, selectSlug) {
    if (!folder) { proj.innerHTML='<option>—</option>'; launch.disabled=true; return; }
    proj.innerHTML = '<option>loading…</option>';
    const ps = await loadProjectsRich(folder);
    proj.innerHTML = '<option value="">— pick a project —</option>' +
      ps.map(p=>`<option value="${p.slug}">${p.slug} · ${p.created_label} · ${p.stage}</option>`).join("");
    if (selectSlug) { proj.value = selectSlug; }
    launch.disabled = !proj.value;
  }
  chan.onchange = () => { launch.disabled = true; refreshProjects(chan.value); };
  proj.onchange = () => { launch.disabled = !(chan.value && proj.value); };
  launch.onclick = async () => {
    launch.disabled = true; launch.textContent = "Launching…";
    const mode = panel.querySelector("#mode").value;
    await api("/api/launch", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({channel:chan.value, project:proj.value, dry: mode==="dry"})});
    poll();
  };

  // ---- Create wiring ----
  const fileInput = create.querySelector("#scriptfile");
  const textArea = create.querySelector("#scripttext");
  fileInput.onchange = async () => {
    const f = fileInput.files[0]; if (!f) return;
    textArea.value = await f.text();
  };
  const slugInput = create.querySelector("#slug");
  const msg = create.querySelector("#createmsg");
  create.querySelector("#create").onclick = async () => {
    msg.textContent = "Creating — parsing + verifying…";
    const r = await api("/api/create", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({script: textArea.value, slug: slugInput.value.trim()})});
    if (!r.ok) {
      let m = "✗ " + (r.error || "create failed") + " (stage: " + (r.stage||"?") + ")";
      if (r.verify) m += "\\n  wordless beats: " + JSON.stringify(r.verify.wordless) +
                         "\\n  Mode A no-VISUAL: " + JSON.stringify(r.verify.no_visual);
      msg.textContent = m; return;
    }
    const v = r.verify;
    let g = r.git && r.git.pushed ? "pushed to GitHub" :
            (r.git && r.git.warn ? ("⚠ " + r.git.warn) : "git skipped");
    msg.textContent = "✓ created " + r.folder + "/projects/" + r.slug +
      "\\n  " + v.beats + " beats · modes " + JSON.stringify(v.modes) +
      "\\n  " + g + "\\n  selected below — pick mode and Launch.";
    // select the channel + new project in the launch panel
    chan.value = r.folder;
    await refreshProjects(r.folder, r.slug);
  };
}"""
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
            plans.append((i, e, "skip-applied")); continue
        n = text.count(e["old"])
        if n == 1:
            plans.append((i, e, "apply"))
        elif n == 0:
            fatal.append(f"edit {i}: ANCHOR NOT FOUND")
        else:
            fatal.append(f"edit {i}: anchor x{n} (must be 1)")

    print("=== INGEST PATCH PLAN ===")
    for i, e, a in plans:
        print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)

    to_apply = [(i, e) for (i, e, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied (idempotent)."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} edit(s) WOULD apply."); return

    bak = T.with_suffix(T.suffix + ".pre_ingest")
    if not bak.exists():
        bak.write_text(text); print(f"  backup -> {bak.name}")
    for i, e in to_apply:
        text = T.read_text()
        if text.count(e["old"]) != 1:
            print(f"  !! edit {i}: anchor changed at write — ABORT"); sys.exit(2)
        T.write_text(text.replace(e["old"], e["new"], 1))
        print(f"  applied -> edit {i}")
    print("\n=== DONE === restart the service to pick it up:")
    print("  systemctl --user restart mission-control.service")


if __name__ == "__main__":
    main()
