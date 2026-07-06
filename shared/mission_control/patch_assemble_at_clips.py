#!/usr/bin/env python3
"""
patch_assemble_at_clips.py — expose an Assemble button in the clips_ready state.

WHY: killing auto-assemble orphaned the assemble control. The Re-assemble button
lives in the FINAL VIDEO panel, which renders only when has_video is true. With
--stop-after-clips, a run ends at clips_ready with NO final_video.mp4 -> the panel
never shows -> the button that would CREATE the first final_video is hidden behind
the file it makes. Fix: /api/meta also reports has_clips; renderDonePanel shows an
Assemble panel (button -> existing reassemble handler) when has_clips && !has_video.

Idempotent (sentinel: ASSEMBLE_AT_CLIPS_APPLIED). Three anchors, each verified once;
py_compile before write; backup to pipeline_server.py.pre_assembleatclips. Pure ASCII.
No apostrophes in the JS string literals (they cross the Python->JS layer).
"""
import sys, py_compile, tempfile, shutil
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_assembleatclips")
SENTINEL = "ASSEMBLE_AT_CLIPS_APPLIED"

# --- Anchor 1: /api/meta -- add has_clips beside has_video. ---
ANCHOR_META = '''            video = Path(paths["project"]) / "final_video.mp4"
            self._json(200, {
                "ok": True,
                "title": header.get("title", ""),
                "description": header.get("description", ""),
                "tags": tags,
                "has_video": video.exists(),
                "video_name": "final_video.mp4",
            })'''

NEW_META = '''            video = Path(paths["project"]) / "final_video.mp4"
            # ASSEMBLE_AT_CLIPS_APPLIED: report clip presence so the UI can offer
            # Assemble in the clips_ready state (no video yet).
            _clips_dir = Path(paths["project"]) / "modea" / "clips"
            _has_clips = _clips_dir.is_dir() and any(_clips_dir.glob("shot_*.mp4"))
            self._json(200, {
                "ok": True,
                "title": header.get("title", ""),
                "description": header.get("description", ""),
                "tags": tags,
                "has_video": video.exists(),
                "has_clips": bool(_has_clips),
                "video_name": "final_video.mp4",
            })'''

# --- Anchor 2: the JS gate -- branch to an assemble panel when clips exist. ---
ANCHOR_GATE = '''  if (!meta || !meta.has_video) { renderTopPlaceholder(); return; }   // no video -> placeholder'''

NEW_GATE = '''  if (!meta || !meta.has_video) {   // ASSEMBLE_AT_CLIPS_APPLIED
    if (meta && meta.has_clips) { renderAssemblePanel(ch, pr); return; }  // clips_ready -> offer Assemble
    renderTopPlaceholder(); return;   // truly nothing yet -> placeholder
  }'''

# --- Anchor 3: define renderAssemblePanel above renderTopPlaceholder. ---
ANCHOR_FN = '''function renderTopPlaceholder() {'''

NEW_FN = '''function renderAssemblePanel(ch, pr) {
  // ASSEMBLE_AT_CLIPS_APPLIED: clips are on disk but no final_video yet. Offer the
  // deliberate assemble press (reuses the reassemble handler + aligned assembler).
  const slot = document.getElementById("toppanel");
  if (!slot) return;
  const panel = document.createElement("div");
  panel.id = "donepanel";
  panel.className = "panel";
  panel.style.cssText = "border:1px solid #32323e;border-radius:8px;background:#161620;padding:18px;text-align:center;";
  panel.innerHTML =
    "<div style=\\"color:#d4a017;font-size:12px;letter-spacing:.08em;margin-bottom:8px;\\">CLIPS READY</div>" +
    "<div style=\\"color:#c8c8d0;font-size:13px;margin-bottom:12px;\\">Clips are on disk. Assemble to build the final video.</div>" +
    "<button id=\\"reassemblebtn\\" style=\\"background:#d4a017;color:#161620;font-weight:600;padding:9px 16px;font-size:13px;border:none;border-radius:6px;cursor:pointer;\\">Assemble from clips</button>" +
    " <span id=\\"reassemblemsg\\" style=\\"color:#8a8a99;font-size:12px;margin-left:8px;\\"></span>";
  slot.innerHTML = "";
  slot.appendChild(panel);
  const rb = document.getElementById("reassemblebtn");
  if (rb) rb.onclick = function() { reassemble(ch, pr); };
}

function renderTopPlaceholder() {'''


def die(msg):
    print(f"FAIL: {msg}  Nothing written.", file=sys.stderr)
    sys.exit(1)


def main():
    if not TARGET.is_file():
        die(f"target not found: {TARGET}")
    src = TARGET.read_text()
    if SENTINEL in src:
        print("Already applied (sentinel present). No-op.")
        return
    if "\\'" in NEW_FN or "\\'" in NEW_GATE:
        die("apostrophe-in-JS guard tripped in patch source.")
    for label, anchor in (("meta", ANCHOR_META), ("gate", ANCHOR_GATE), ("fn", ANCHOR_FN)):
        n = src.count(anchor)
        if n != 1:
            die(f"anchor '{label}' matched {n} times (need exactly 1) — pipeline_server.py drifted.")
    new = (src.replace(ANCHOR_META, NEW_META, 1)
              .replace(ANCHOR_GATE, NEW_GATE, 1)
              .replace(ANCHOR_FN, NEW_FN, 1)
              .replace('APP_VERSION = "v3.9"', 'APP_VERSION = "v3.9.1"', 1))
    for need in (SENTINEL, "renderAssemblePanel", "has_clips", 'APP_VERSION = "v3.9.1"'):
        if need not in new:
            die(f"post-edit check failed (missing {need}).")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(new); tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        die(f"py_compile failed: {e}")
    finally:
        Path(tmp).unlink(missing_ok=True)
    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(new)
    print(f"OK — patched {TARGET.name}  (Assemble button in clips_ready; v3.9.1)")
    print(f"     backup: {BACKUP.name}")


if __name__ == "__main__":
    main()
