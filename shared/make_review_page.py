"""
make_review_page.py — generate an HTML stills review page for any project.

Override prompt: if filled, REPLACES the canon-resolved prompt entirely.
Notes: appended to original prompt as REGENERATION FEEDBACK (if override empty).

Usage:
    python ../shared/make_review_page.py --project projects/tenerife
"""
import argparse
import json
import re
from pathlib import Path


def resolve_canon_tokens(prompt: str, canon: dict) -> str:
    def replace(match):
        key = match.group(1)
        return canon.get(key, match.group(0))
    return re.sub(r"\{(\w+)\}", replace, prompt)


def find_beats_file(project_dir: Path, beats_arg: str | None) -> Path:
    if beats_arg:
        return Path(beats_arg)
    channel_root = project_dir.parent.parent
    project_name = project_dir.name
    candidates = [
        channel_root / "beat-scripts" / f"{project_name}_beats.json",
        project_dir / "storyboard.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"No beats.json or storyboard.json found. Checked: {[str(c) for c in candidates]}"
    )


def build_html(project_name: str, beats: list, canon: dict, stills_dir_rel: str) -> str:
    rows = []
    for shot in beats:
        idx = shot["index"]
        narration = shot.get("narration", "")
        raw_prompt = shot.get("image_prompt", "")
        resolved_prompt = resolve_canon_tokens(raw_prompt, canon)
        rows.append({
            "index": idx,
            "narration": narration,
            "prompt": resolved_prompt,
            "still_path": f"{stills_dir_rel}/shot_{idx:03d}.png",
        })

    shots_json = json.dumps(rows)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Stills Review — {project_name}</title>
<style>
  :root {{
    --bg: #0f1115; --card: #1a1d24; --border: #2a2f3a;
    --text: #e6e8eb; --text-muted: #8a8f99;
    --accept: #2d9d54; --accept-bg: #142a1d;
    --reject: #c94545; --reject-bg: #2a1414;
    --accent: #5b8def;
    --regen: #b87a14;
    --override: #a855f7;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  header {{ position: sticky; top: 0; z-index: 100; background: var(--bg); border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap; }}
  header h1 {{ margin: 0; font-size: 18px; font-weight: 600; }}
  .counters {{ display: flex; gap: 16px; font-size: 14px; color: var(--text-muted); }}
  .counter strong {{ color: var(--text); font-weight: 600; }}
  .counter.accept strong {{ color: var(--accept); }}
  .counter.reject strong {{ color: var(--reject); }}
  .server-status {{ font-size: 12px; padding: 4px 10px; border-radius: 4px; background: var(--card); color: var(--text-muted); }}
  .server-status.live {{ background: var(--accept-bg); color: var(--accept); }}
  button {{ background: var(--accent); color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; font-weight: 500; }}
  button:hover {{ opacity: 0.9; }}
  button:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  button.secondary {{ background: transparent; color: var(--text-muted); border: 1px solid var(--border); }}
  main {{ padding: 24px; max-width: 1600px; margin: 0 auto; }}
  .shot {{ display: grid; grid-template-columns: 360px 1fr 380px; gap: 20px; background: var(--card); border: 2px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 16px; transition: border-color 0.15s, background 0.15s; }}
  .shot.accept {{ border-color: var(--accept); background: var(--accept-bg); }}
  .shot.reject {{ border-color: var(--reject); background: var(--reject-bg); }}
  .shot.regenerating {{ border-color: var(--regen); }}
  .shot.has-override {{ border-color: var(--override); }}
  .shot-image {{ position: relative; background: #000; border-radius: 6px; overflow: hidden; aspect-ratio: 16/9; }}
  .shot-image img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
  .shot-image .missing {{ display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-muted); font-size: 13px; text-align: center; padding: 24px; }}
  .shot-number {{ position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.7); color: white; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: 600; font-family: ui-monospace, monospace; }}
  .regen-overlay {{ position: absolute; inset: 0; background: rgba(0,0,0,0.75); display: none; align-items: center; justify-content: center; color: white; font-size: 13px; flex-direction: column; gap: 12px; }}
  .regen-overlay.visible {{ display: flex; }}
  .spinner {{ width: 32px; height: 32px; border: 3px solid rgba(255,255,255,0.2); border-top-color: var(--regen); border-radius: 50%; animation: spin 1s linear infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .shot-content {{ min-width: 0; }}
  .narration {{ font-size: 14px; color: var(--text); font-style: italic; margin-bottom: 12px; padding: 10px 14px; background: rgba(255,255,255,0.03); border-left: 3px solid var(--accent); border-radius: 4px; }}
  .prompt {{ font-size: 13px; color: var(--text); line-height: 1.6; white-space: pre-wrap; }}
  .actions {{ display: flex; flex-direction: column; gap: 10px; }}
  .action-buttons {{ display: flex; gap: 8px; }}
  .btn-judge {{ flex: 1; padding: 10px; border: 1px solid var(--border); background: transparent; color: var(--text); cursor: pointer; border-radius: 6px; font-size: 13px; font-weight: 500; transition: all 0.15s; }}
  .btn-judge:hover {{ background: rgba(255,255,255,0.05); }}
  .btn-judge.active.accept {{ background: var(--accept); border-color: var(--accept); color: white; }}
  .btn-judge.active.reject {{ background: var(--reject); border-color: var(--reject); color: white; }}
  .btn-regen {{ padding: 10px; background: var(--regen); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: opacity 0.15s; }}
  .btn-regen:hover {{ opacity: 0.9; }}
  .btn-regen:disabled {{ opacity: 0.3; cursor: not-allowed; }}
  .btn-regen.hidden {{ display: none; }}
  .btn-regen.override-active {{ background: var(--override); }}
  textarea {{ width: 100%; min-height: 80px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 10px; font-family: inherit; font-size: 13px; resize: vertical; }}
  textarea:focus {{ outline: none; border-color: var(--accent); }}
  textarea::placeholder {{ color: var(--text-muted); }}
  textarea.override {{ border-color: rgba(168, 85, 247, 0.3); min-height: 90px; }}
  textarea.override:focus {{ border-color: var(--override); }}
  textarea.override.has-content {{ border-color: var(--override); background: rgba(168, 85, 247, 0.05); }}
  .field-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center; }}
  .field-label .label-hint {{ color: var(--override); text-transform: none; letter-spacing: normal; font-size: 11px; font-style: italic; }}
  .prompt-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
  .status-indicator {{ font-size: 11px; color: var(--text-muted); text-align: right; height: 14px; transition: color 0.15s; }}
  .status-indicator.saved {{ color: var(--accept); }}
  .status-indicator.regen-ok {{ color: var(--accept); }}
  .status-indicator.regen-fail {{ color: var(--reject); }}
  .field-group {{ display: flex; flex-direction: column; gap: 4px; }}
  @media (max-width: 1200px) {{ .shot {{ grid-template-columns: 280px 1fr 320px; }} }}
  @media (max-width: 900px) {{ .shot {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>Stills Review — {project_name}</h1>
  <div class="server-status" id="server-status">Static mode</div>
  <div class="counters">
    <span class="counter accept"><strong id="count-accept">0</strong> accept</span>
    <span class="counter reject"><strong id="count-reject">0</strong> reject</span>
    <span class="counter"><strong id="count-pending">0</strong> pending</span>
    <span class="counter">of <strong id="count-total">0</strong> total</span>
  </div>
  <div>
    <button class="secondary" onclick="resetAll()">Reset all</button>
    <button onclick="exportFeedback()">Export JSON</button>
  </div>
</header>
<main id="shots-container"></main>
<script>
const PROJECT = {json.dumps(project_name)};
const SHOTS = {shots_json};
const STORAGE_PREFIX = `review:${{PROJECT}}:`;
const IS_SERVED = window.location.protocol === "http:" || window.location.protocol === "https:";
let SERVER_AVAILABLE = false;

async function checkServer() {{
  if (!IS_SERVED) return;
  try {{
    const res = await fetch("/api/health", {{method: "GET"}});
    if (res.ok) {{
      SERVER_AVAILABLE = true;
      const el = document.getElementById("server-status");
      el.textContent = "Server live — regenerate available";
      el.classList.add("live");
      document.querySelectorAll(".btn-regen").forEach(b => b.classList.remove("hidden"));
    }}
  }} catch (e) {{ }}
}}

function loadJudgment(idx) {{ return localStorage.getItem(`${{STORAGE_PREFIX}}${{idx}}:action`) || ""; }}
function loadNote(idx) {{ return localStorage.getItem(`${{STORAGE_PREFIX}}${{idx}}:note`) || ""; }}
function loadOverride(idx) {{ return localStorage.getItem(`${{STORAGE_PREFIX}}${{idx}}:override`) || ""; }}

function saveJudgment(idx, action) {{
  if (action) localStorage.setItem(`${{STORAGE_PREFIX}}${{idx}}:action`, action);
  else localStorage.removeItem(`${{STORAGE_PREFIX}}${{idx}}:action`);
}}
function saveNote(idx, note) {{
  if (note) localStorage.setItem(`${{STORAGE_PREFIX}}${{idx}}:note`, note);
  else localStorage.removeItem(`${{STORAGE_PREFIX}}${{idx}}:note`);
}}
function saveOverride(idx, override) {{
  if (override) localStorage.setItem(`${{STORAGE_PREFIX}}${{idx}}:override`, override);
  else localStorage.removeItem(`${{STORAGE_PREFIX}}${{idx}}:override`);
}}

function setJudgment(idx, action) {{
  const current = loadJudgment(idx);
  const next = current === action ? "" : action;
  saveJudgment(idx, next);
  updateShotUI(idx);
  updateCounters();
}}

function updateShotUI(idx) {{
  const card = document.getElementById(`shot-${{idx}}`);
  const action = loadJudgment(idx);
  card.classList.remove("accept", "reject");
  if (action) card.classList.add(action);
  card.querySelectorAll(".btn-judge").forEach(btn => {{
    btn.classList.toggle("active", btn.dataset.action === action);
  }});
  const override = loadOverride(idx);
  const overrideTextarea = card.querySelector("textarea.override");
  const regenBtn = card.querySelector(".btn-regen");
  if (override) {{
    card.classList.add("has-override");
    overrideTextarea.classList.add("has-content");
    regenBtn.classList.add("override-active");
    regenBtn.textContent = "Regenerate (USING OVERRIDE)";
  }} else {{
    card.classList.remove("has-override");
    overrideTextarea.classList.remove("has-content");
    regenBtn.classList.remove("override-active");
    regenBtn.textContent = "Regenerate this shot";
  }}
}}

function updateCounters() {{
  let accept = 0, reject = 0;
  SHOTS.forEach(s => {{
    const a = loadJudgment(s.index);
    if (a === "accept") accept++;
    if (a === "reject") reject++;
  }});
  document.getElementById("count-accept").textContent = accept;
  document.getElementById("count-reject").textContent = reject;
  document.getElementById("count-pending").textContent = SHOTS.length - accept - reject;
  document.getElementById("count-total").textContent = SHOTS.length;
}}

function setStatus(el, text, cls) {{
  el.textContent = text;
  el.className = "status-indicator " + (cls || "");
  if (cls === "saved") {{
    clearTimeout(el._timer);
    el._timer = setTimeout(() => {{ el.textContent = ""; el.className = "status-indicator"; }}, 1200);
  }}
}}

async function regenerateShot(idx) {{
  if (!SERVER_AVAILABLE) {{
    alert("Server not running. Start it from the channel root with:\\n\\npython ../shared/serve_review.py --project projects/" + PROJECT);
    return;
  }}
  const card = document.getElementById(`shot-${{idx}}`);
  const overlay = document.getElementById(`overlay-${{idx}}`);
  const regenBtn = card.querySelector(".btn-regen");
  const statusEl = document.getElementById(`status-${{idx}}`);
  const note = loadNote(idx);
  const override = loadOverride(idx);

  card.classList.add("regenerating");
  overlay.classList.add("visible");
  regenBtn.disabled = true;
  setStatus(statusEl, override ? "Regenerating with OVERRIDE..." : "Regenerating...", "");

  try {{
    const res = await fetch("/api/restill", {{
      method: "POST",
      headers: {{"Content-Type": "application/json"}},
      body: JSON.stringify({{shot: idx, note: note, override: override}})
    }});
    const data = await res.json();
    if (data.ok) {{
      const img = card.querySelector(".shot-image img");
      const baseSrc = img.src.split("?")[0];
      img.src = baseSrc + "?v=" + Date.now();
      saveJudgment(idx, "");
      updateShotUI(idx);
      updateCounters();
      setStatus(statusEl, override ? "Regenerated (override)" : "Regenerated", "regen-ok");
      setTimeout(() => setStatus(statusEl, "", ""), 2500);
    }} else {{
      setStatus(statusEl, "Failed: " + (data.error || "unknown"), "regen-fail");
    }}
  }} catch (e) {{
    setStatus(statusEl, "Failed: " + e.message, "regen-fail");
  }} finally {{
    card.classList.remove("regenerating");
    overlay.classList.remove("visible");
    regenBtn.disabled = false;
  }}
}}

function exportFeedback() {{
  const out = [];
  SHOTS.forEach(s => {{
    const action = loadJudgment(s.index);
    const note = loadNote(s.index);
    const override = loadOverride(s.index);
    if (action || note || override) {{
      const entry = {{shot: s.index, action: action || "pending", note: note || ""}};
      if (override) entry.override = override;
      out.push(entry);
    }}
  }});
  const blob = new Blob([JSON.stringify(out, null, 2)], {{type: "application/json"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${{PROJECT}}_feedback.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}

function resetAll() {{
  if (!confirm("Clear all feedback for " + PROJECT + "?")) return;
  SHOTS.forEach(s => {{
    saveJudgment(s.index, "");
    saveNote(s.index, "");
    saveOverride(s.index, "");
  }});
  document.querySelectorAll("textarea").forEach(t => t.value = "");
  SHOTS.forEach(s => updateShotUI(s.index));
  updateCounters();
}}

function renderShots() {{
  const container = document.getElementById("shots-container");
  SHOTS.forEach(shot => {{
    const card = document.createElement("div");
    card.className = "shot";
    card.id = `shot-${{shot.index}}`;
    card.innerHTML = `
      <div class="shot-image">
        <img src="${{shot.still_path}}" alt="Shot ${{shot.index}}"
             onerror="this.outerHTML='<div class=missing>Still not generated yet<br>${{shot.still_path}}</div>'">
        <div class="shot-number">SHOT ${{String(shot.index).padStart(3, '0')}}</div>
        <div class="regen-overlay" id="overlay-${{shot.index}}">
          <div class="spinner"></div>
          <div>Generating new still...</div>
        </div>
      </div>
      <div class="shot-content">
        <div class="narration">"${{shot.narration.replace(/"/g, '&quot;')}}"</div>
        <div class="prompt-label">Image prompt (resolved)</div>
        <div class="prompt">${{shot.prompt.replace(/</g, '&lt;')}}</div>
      </div>
      <div class="actions">
        <div class="action-buttons">
          <button class="btn-judge" data-action="accept" onclick="setJudgment(${{shot.index}}, 'accept')">Accept</button>
          <button class="btn-judge" data-action="reject" onclick="setJudgment(${{shot.index}}, 'reject')">Reject</button>
        </div>
        <button class="btn-regen hidden" onclick="regenerateShot(${{shot.index}})">Regenerate this shot</button>
        <div class="field-group">
          <div class="field-label">Notes (appended to original prompt)</div>
          <textarea id="note-${{shot.index}}" placeholder="Notes — added to existing prompt as REGENERATION FEEDBACK..."></textarea>
        </div>
        <div class="field-group">
          <div class="field-label">
            <span>Override prompt</span>
            <span class="label-hint">if filled, REPLACES the prompt entirely</span>
          </div>
          <textarea class="override" id="override-${{shot.index}}" placeholder="Raw prompt sent directly to fal. Bypasses canon, original prompt, and notes. Leave empty to use Notes mode."></textarea>
        </div>
        <div class="status-indicator" id="status-${{shot.index}}"></div>
      </div>
    `;
    container.appendChild(card);

    const noteEl = card.querySelector(`#note-${{shot.index}}`);
    const overrideEl = card.querySelector(`#override-${{shot.index}}`);

    noteEl.value = loadNote(shot.index);
    noteEl.addEventListener("input", (e) => {{
      saveNote(shot.index, e.target.value);
      setStatus(document.getElementById(`status-${{shot.index}}`), "Saved", "saved");
    }});

    overrideEl.value = loadOverride(shot.index);
    overrideEl.addEventListener("input", (e) => {{
      saveOverride(shot.index, e.target.value);
      updateShotUI(shot.index);
      setStatus(document.getElementById(`status-${{shot.index}}`), "Saved", "saved");
    }});

    updateShotUI(shot.index);
  }});
}}

renderShots();
updateCounters();
checkServer();
</script>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--beats")
    args = parser.parse_args()

    project_dir = Path(args.project)
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Project dir not found: {project_dir}")

    beats_file = find_beats_file(project_dir, args.beats)
    print(f"Reading beats from: {beats_file}")

    data = json.loads(beats_file.read_text())
    if isinstance(data, dict) and "beats" in data:
        canon = data.get("canon", {})
        beats = data["beats"]
    elif isinstance(data, list):
        canon = {}
        beats = data
    else:
        raise ValueError(f"Unrecognized beats file structure in {beats_file}")

    html = build_html(
        project_name=project_dir.name,
        beats=beats,
        canon=canon,
        stills_dir_rel="stills",
    )

    output_path = project_dir / "review.html"
    output_path.write_text(html)
    print(f"Wrote: {output_path}")
    print()
    print(f"Open with server (override prompt + single-click regenerate):")
    print(f"  python ../shared/serve_review.py --project {project_dir}")


if __name__ == "__main__":
    main()
