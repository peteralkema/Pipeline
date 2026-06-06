#!/usr/bin/env python3
"""
make_modeb_review.py — Piece 1 of the Mode B gate.

Builds ONE scrollable HTML page: every Mode B beat as a card with
  - its clip autoplaying + looping + muted (left)
  - editable payload JSON, read-only spoken line, LOCKED duration, Re-render/Flag (right)

The page is self-contained except for the clip <video> srcs, which the server serves.
Re-render/Flag buttons POST to the server (Piece 2). Duration is shown but NOT editable
(frame count is locked by the audio leg — sync cannot be broken from this gate).

Usage: make_modeb_review.py --project <dir> --beats <beats.json> --clips <clips_dir> [--out review.html]
"""
import os, sys, json, argparse, html
from pathlib import Path

CARD_CSS = """
:root{--navy:#0a1628;--amber:#d4a017;--bone:#f4f1ea;--indigo:#3b5bdb;--rust:#8b3a1e;}
*{box-sizing:border-box}
body{margin:0;background:var(--navy);color:var(--bone);font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;z-index:10;background:#06101d;border-bottom:1px solid #1d2c40;padding:14px 22px}
header h1{margin:0;font-size:18px;color:var(--bone)}
header .sub{color:#7c8aa0;font-size:13px;margin-top:3px}
.beat{display:grid;grid-template-columns:minmax(360px,1fr) minmax(320px,420px);gap:20px;
  padding:20px 22px;border-bottom:1px solid #16243a;align-items:start}
.beat.flagged{background:#2a1410}
video{width:100%;border-radius:8px;background:#000;display:block}
.meta{font-size:12px;color:#7c8aa0;margin-bottom:8px}
.meta b{color:var(--amber)}
.panel label{display:block;font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:#7c8aa0;margin:10px 0 4px}
textarea{width:100%;min-height:130px;background:#0d1b2e;color:var(--bone);border:1px solid #24364f;
  border-radius:6px;padding:10px;font:13px/1.4 ui-monospace,Menlo,monospace;resize:vertical}
.spoken{background:#0d1b2e;border-left:3px solid var(--indigo);padding:8px 10px;border-radius:4px;
  font-style:italic;color:#c7d2e0;min-height:20px}
.locked{background:#0d1b2e;border-left:3px solid var(--amber);padding:8px 10px;border-radius:4px;color:#c7d2e0}
.btns{margin-top:12px;display:flex;gap:10px}
button{font:13px inherit;padding:9px 16px;border-radius:6px;border:0;cursor:pointer}
.rerender{background:var(--indigo);color:#fff}
.flag{background:transparent;color:var(--rust);border:1px solid var(--rust)}
.status{font-size:12px;color:#7c8aa0;margin-top:8px;min-height:16px}
.done{position:sticky;bottom:0;background:#06101d;border-top:1px solid #1d2c40;padding:16px 22px;text-align:center}
.done button{background:var(--amber);color:var(--navy);font-weight:600;padding:12px 28px}
"""

PAGE_JS = """
async function rerender(idx){
  const ta=document.getElementById('payload-'+idx);
  const st=document.getElementById('status-'+idx);
  let payload;
  try{payload=JSON.parse(ta.value);}catch(e){st.textContent='⚠ payload is not valid JSON: '+e.message;return;}
  st.textContent='re-rendering beat '+idx+'… (magical seconds)';
  try{
    const r=await fetch('/rerender',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({index:idx,payload:payload})});
    const j=await r.json();
    if(j.ok){
      const v=document.getElementById('video-'+idx);
      v.src=j.clip+'?t='+Date.now();  // cache-bust so the new clip loads
      v.load();v.play();
      st.textContent='✓ re-rendered at '+new Date().toLocaleTimeString();
    }else{st.textContent='✗ '+(j.error||'render failed — see terminal');}
  }catch(e){st.textContent='✗ request failed: '+e.message;}
}
async function flag(idx){
  const st=document.getElementById('status-'+idx);
  const r=await fetch('/flag',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({index:idx})});
  document.getElementById('beat-'+idx).classList.add('flagged');
  st.textContent='⚑ flagged for loop-back (audio-affecting or render bug)';
}
function finish(){
  fetch('/done',{method:'POST'}).then(()=>{document.getElementById('finishmsg').textContent=
    'Review submitted — return to the terminal and type continue.';});
}
"""

def build_page(project, beats_path, clips_dir, out_path):
    beats = json.load(open(beats_path, encoding="utf-8"))
    durations = {}
    dpath = Path(project) / "durations.json"
    if dpath.exists():
        durations = json.load(open(dpath))
    b_beats = [b for b in beats if b.get("mode") == "B" and b.get("component")]

    cards = []
    for b in b_beats:
        idx = b["index"]
        comp = b["component"]
        payload = b.get("payload", {})
        spoken = b.get("found_line") or b.get("narration") or ""
        spoken_disp = html.escape(spoken) if spoken else "(silent card — no voiceover over this beat)"
        d = durations.get(str(idx), {})
        dur_s = d.get("duration")
        dur_disp = f"{dur_s:.1f}s slot" if isinstance(dur_s, (int, float)) else "slot from audio"
        # find the clip file
        clip = f"beat_{idx:02d}_B_{comp}.mp4"
        payload_json = html.escape(json.dumps(payload, indent=2, ensure_ascii=False))
        cards.append(f"""
<div class="beat" id="beat-{idx}">
  <div>
    <div class="meta">beat <b>{idx:02d}</b> · {comp}</div>
    <video id="video-{idx}" src="/clip/{clip}" autoplay loop muted playsinline></video>
  </div>
  <div class="panel">
    <label>Payload (editable — content only)</label>
    <textarea id="payload-{idx}">{payload_json}</textarea>
    <label>Spoken line (read-only — what Victor says here)</label>
    <div class="spoken">{spoken_disp}</div>
    <label>Duration (LOCKED by audio — fills {dur_disp})</label>
    <div class="locked">card animates its own length; assembler freeze-fills the rest</div>
    <div class="btns">
      <button class="rerender" onclick="rerender({idx})">Re-render this beat</button>
      <button class="flag" onclick="flag({idx})">Flag: audio-affecting / bug</button>
    </div>
    <div class="status" id="status-{idx}"></div>
  </div>
</div>""")

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Mode B review · {html.escape(project)}</title><style>{CARD_CSS}</style></head>
<body>
<header><h1>Mode B review — {len(b_beats)} cards</h1>
<div class="sub">{html.escape(project)} · scroll top→bottom, clips autoplay · edit payload + Re-render to fix · Flag if audio-affecting</div></header>
{''.join(cards)}
<div class="done"><span id="finishmsg" style="color:#7c8aa0;margin-right:16px"></span>
<button onclick="finish()">Done reviewing — submit</button></div>
<script>{PAGE_JS}</script>
</body></html>"""
    Path(out_path).write_text(page, encoding="utf-8")
    return len(b_beats)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--beats", required=True)
    ap.add_argument("--clips", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(a.project, "modeb_review.html")
    n = build_page(a.project, a.beats, a.clips, out)
    print(f"wrote {out} ({n} Mode B cards)")


if __name__ == "__main__":
    main()
