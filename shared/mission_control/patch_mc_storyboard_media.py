#!/usr/bin/env python3
"""
patch_mc_storyboard_media.py — Phase 3b: bigger media + still AND clip side-by-side.

Two edits to pipeline_server.py:
  1. beatRow(): show Flux still AND Kling clip side-by-side (when both exist),
     large (~520px each), each captioned. Still-only pre-animation; placeholder
     if neither. The still proves the frame; the clip proves the motion — seeing
     both catches a clean still that animated badly, before the expensive stage.
  2. renderStoryboard(): give the storyboard panel a wide max-width (ultra-wide
     monitor) so two large media boxes sit side-by-side comfortably.

Idempotent (markers), backs up to .pre_media, no escaped newlines in JS.

Run on the box:
  python shared/mission_control/patch_mc_storyboard_media.py --check
  python shared/mission_control/patch_mc_storyboard_media.py
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T = REPO / "shared" / "mission_control" / "pipeline_server.py"

EDITS = []

# --- 1. beatRow: still + clip side by side, large, captioned ---
EDITS.append(dict(
    marker="Flux still",
    old='''function beatRow(b, ch, pr) {
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
}''',
    new='''function beatRow(b, ch, pr) {
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
}'''
))

# --- 2. widen the storyboard panel (override the 720px .panel cap) ---
EDITS.append(dict(
    marker='wrap.style.maxWidth',
    old='''  wrap.id = "storyboard";
  wrap.className = "panel";''',
    new='''  wrap.id = "storyboard";
  wrap.className = "panel";
  wrap.style.maxWidth = "1200px";  // ultra-wide: room for still + clip side-by-side''',
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

    print("=== MEDIA PATCH PLAN ===")
    for i, a in plans: print(f"  [{a:<13}] edit {i}")
    if fatal:
        print("\n=== ABORT ==="); [print("  !!", m) for m in fatal]; sys.exit(1)
    to_apply = [i for (i, a) in plans if a == "apply"]
    if not to_apply:
        print("\nNothing to do — all applied."); return
    if args.check:
        print(f"\n--check: {len(to_apply)} would apply."); return

    bak = T.with_suffix(T.suffix + ".pre_media")
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
