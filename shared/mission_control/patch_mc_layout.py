#!/usr/bin/env python3
"""
patch_mc_layout.py — Phase 3c: the permanent four-column beat-row layout.

Replaces beatRow() with the production-order row Peter specified:

  COL 1  text spine   : metadata line (beat·shot·stage·duration·mode),
                        narration, rendered prompt (italic), look.
  COL 2  Flux still    : the still, or "not rendered" placeholder.
  COL 3  motion        : editable textarea, pre-filled with the stored
                        motion_prompt, blank-OK. Display+persist only for now
                        (the seam for the future still->Kling re-render). Saved
                        to a per-beat in-memory map keyed by beat index; a
                        backend save endpoint wires in a later phase.
  COL 4  Kling clip    : the clip, or "not rendered" placeholder.

  MODE B strip (full width, BENEATH the row) — ONLY when the beat has an
  overlay. Hard rule: never more than one Mode B per Mode A beat, so we render
  overlays[0] only. Pure-Mode-A beats grow no strip at all (zero Mode B chrome).
  This strip is also where the Remotion edit box will live later.

Media is sized responsive-to-column (each fills its column up to a cap), so on
the right-half of an ultra-wide at 150% the four columns stay readable and the
media is as large as the column allows. Columns wrap gracefully if narrow.

Two edits to pipeline_server.py:
  1. replace beatRow() with the four-column version.
  2. widen the storyboard panel further (1600px) for four columns + media.

Idempotent (markers), backs up to .pre_layout, no escaped newlines in JS.

Run on the box:
  python shared/mission_control/patch_mc_layout.py --check
  python shared/mission_control/patch_mc_layout.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# --- 1. replace beatRow with the four-column production-order layout ---
# Anchor: the entire beatRow from patch_mc_storyboard_media.py (the "Flux still"
# + "Kling motion" side-by-side version). We swap it wholesale.
EDITS.append(dict(
    marker="MOTION DIRECTION",   # unique to the new version
    old='''function beatRow(b, ch, pr) {
  const a = b.assets || {};
  const shot = a.still && a.still.engine_shot;
  const hasStill = a.still && a.still.exists;
  const hasClip = a.clip && a.clip.exists;
  const n3 = String(shot).padStart(3,"0");
  const q = "?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr) +
            "&key=" + KEY;
  const MW = 520;  // media width (px) — large, for an ultra-wide monitor
  function cap(label) {
    return '<div style="color:#55556a;font-size:11px;margin-top:4px;text-align:center;">' + label + '</div>';
  }
  const tiles = [];
  if (hasStill) {
    tiles.push('<div><img src="/stills/shot_' + n3 + '.png' + q +
      '" loading="lazy" style="width:' + MW + 'px;border-radius:8px;background:#000">' +
      cap("Flux still") + '</div>');
  }
  if (hasClip) {
    tiles.push('<div><video src="/clips/shot_' + n3 + '.mp4' + q +
      '" muted loop autoplay playsinline style="width:' + MW + 'px;border-radius:8px;background:#000"></video>' +
      cap("Kling motion") + '</div>');
  }
  let media;
  if (tiles.length) {
    media = '<div style="display:flex;gap:16px;flex-wrap:wrap;">' + tiles.join("") + '</div>';
  } else {
    media = '<div style="width:' + MW + 'px;height:' + Math.round(MW*9/16) +
      'px;border-radius:8px;background:#1c1c26;display:flex;align-items:center;' +
      'justify-content:center;color:#55556a;font-size:13px;">not rendered yet</div>';
  }
  const dur = (b.duration_s != null) ? (b.duration_s.toFixed(2) + "s") : "—";
  const prompt = b.visual_rendered || b.visual_authored || "";
  const rows = [
    '<div style="padding:18px 0;border-bottom:1px solid #1e1e28;">',
    '<div style="color:#d4a017;font-size:12px;margin-bottom:8px;">beat ' + b.index +
      ' · shot ' + (shot==null?"—":shot) + ' · ' + (b.stage||"") +
      ' · ' + dur + ' · ' + (b.mode||"") + '</div>',
    media,
    '<div style="color:#e8e6e3;font-size:14px;margin-top:10px;">' + (b.narration||"") + '</div>',
    '<div style="color:#8a8a99;font-size:12px;margin-top:6px;font-style:italic;">' + prompt + '</div>',
    '<div style="color:#55556a;font-size:11px;margin-top:6px;">look: ' + (b.look_resolved||"") + '</div>',
    '</div>'
  ];
  return rows.join("");
}''',
    new='''// per-beat motion edits held in memory for this session (display+persist seam).
// Keyed by "channel/project/beatIndex". A backend save endpoint wires in later.
window.__MOTION_EDITS = window.__MOTION_EDITS || {};
function motionKey(ch, pr, idx) { return ch + "/" + pr + "/" + idx; }

function beatRow(b, ch, pr) {
  const a = b.assets || {};
  const shot = a.still && a.still.engine_shot;
  const hasStill = a.still && a.still.exists;
  const hasClip = a.clip && a.clip.exists;
  const n3 = String(shot).padStart(3,"0");
  const q = "?channel=" + encodeURIComponent(ch) + "&project=" + encodeURIComponent(pr) +
            "&key=" + KEY;
  const dur = (b.duration_s != null) ? (b.duration_s.toFixed(2) + "s") : "—";
  const prompt = b.visual_rendered || b.visual_authored || "";

  // COL 2 — Flux still (fills its column up to a cap)
  let stillCell;
  if (hasStill) {
    stillCell = '<img src="/stills/shot_' + n3 + '.png' + q +
      '" loading="lazy" style="width:100%;max-width:480px;border-radius:8px;background:#000;display:block;">';
  } else {
    stillCell = '<div style="width:100%;max-width:480px;aspect-ratio:16/9;border-radius:8px;' +
      'background:#1c1c26;display:flex;align-items:center;justify-content:center;' +
      'color:#55556a;font-size:13px;">not rendered</div>';
  }

  // COL 4 — Kling clip
  let clipCell;
  if (hasClip) {
    clipCell = '<video src="/clips/shot_' + n3 + '.mp4' + q +
      '" muted loop autoplay playsinline style="width:100%;max-width:480px;border-radius:8px;background:#000;display:block;"></video>';
  } else {
    clipCell = '<div style="width:100%;max-width:480px;aspect-ratio:16/9;border-radius:8px;' +
      'background:#1c1c26;display:flex;align-items:center;justify-content:center;' +
      'color:#55556a;font-size:13px;">not rendered</div>';
  }

  // COL 3 — MOTION DIRECTION (editable; pre-filled with stored value or prior edit)
  const mkey = motionKey(ch, pr, b.index);
  const stored = (window.__MOTION_EDITS[mkey] != null)
                 ? window.__MOTION_EDITS[mkey]
                 : (b.motion_prompt || "");
  const motionCell =
    '<textarea data-mkey="' + mkey + '" class="motionbox" rows="6" ' +
    'placeholder="motion direction (blank = engine default)…" ' +
    'style="width:100%;box-sizing:border-box;background:#1c1c26;color:#e8e6e3;' +
    'border:1px solid #32323e;border-radius:8px;padding:10px;' +
    'font:13px/1.45 ui-monospace,monospace;resize:vertical;">' +
    escapeHtml(stored) + '</textarea>' +
    '<div style="color:#55556a;font-size:11px;margin-top:4px;">motion direction</div>';

  // COL 1 — TEXT spine
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
    '</div>';

  // MODE B strip — full width, beneath the row, ONLY when an overlay exists.
  // Hard rule: at most one Mode B per Mode A beat -> render overlays[0] only.
  let modeB = "";
  const ov = (b.overlays && b.overlays.length) ? b.overlays[0] : null;
  if (ov) {
    modeB =
      '<div style="margin-top:14px;padding:12px 14px;border-left:3px solid #d4a017;' +
      'background:#16161e;border-radius:0 8px 8px 0;">' +
        '<div style="color:#d4a017;font-size:12px;margin-bottom:6px;">' +
          'Mode B · ' + (ov.component || "card") + ' · overlays beat ' + b.index + '</div>' +
        '<div style="color:#e8e6e3;font-size:13px;">“' + (ov.phrase || "") + '”</div>' +
        '<div style="color:#55556a;font-size:11px;margin-top:6px;">' +
          'Remotion edit box wires in here (later).</div>' +
      '</div>';
  }

  return '<div style="padding:18px 0;border-bottom:1px solid #1e1e28;">' +
         grid + modeB + '</div>';
}

function escapeHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
                  .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}'''
))

# --- 2. widen storyboard panel for four columns ---
EDITS.append(dict(
    marker='maxWidth = "1600px"',
    old='''  wrap.id = "storyboard";
  wrap.className = "panel";
  wrap.style.maxWidth = "1200px";  // ultra-wide: room for still + clip side-by-side''',
    new='''  wrap.id = "storyboard";
  wrap.className = "panel";
  wrap.style.maxWidth = "1600px";  // four columns: text | still | motion | clip''',
))

# --- 3. capture motion-box edits into the in-memory map (persist across re-render) ---
# Anchor: end of renderStoryboard, right after wrap.innerHTML is set.
EDITS.append(dict(
    marker="bindMotionBoxes",
    old='''  wrap.innerHTML = head + beats.map(b => beatRow(b, ch, pr)).join("");
}''',
    new='''  wrap.innerHTML = head + beats.map(b => beatRow(b, ch, pr)).join("");
  bindMotionBoxes(wrap);
}
function bindMotionBoxes(wrap) {
  // Keep typed motion direction in the in-memory map so a poll re-render
  // (or scroll) doesn't wipe it. Backend save endpoint wires in a later phase.
  wrap.querySelectorAll("textarea.motionbox").forEach(function(t) {
    t.addEventListener("input", function() {
      window.__MOTION_EDITS[t.getAttribute("data-mkey")] = t.value;
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

    print("=== LAYOUT PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_layout")
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
