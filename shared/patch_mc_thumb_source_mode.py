#!/usr/bin/env python3
"""
patch_mc_thumb_source_mode.py — v3.0: the uploaded image is a SOURCE, not the
thumbnail. Iterate source x text freely: still 7 + headline, uploaded poster +
headline, back again — nothing is destroyed, thumbnail.png is always derived.

  - upload now writes <project-root>/thumbnail_source.png (persistent source),
    previews it, and auto-switches the source mode to "Uploaded image"
  - panel gains a source-mode pair (Still # / Uploaded image) in the green
    mode-button pattern; still# greys and stops validating in upload mode
  - Generate branches: --shot N (still mode) vs --still <source> (upload mode)
    — make_thumbnail.py already supports --still, NO engine change needed
  - thumbnail.png remains the single derived artifact upload_episode.py reads

5 anchored edits in shared/mission_control/pipeline_server.py (post-v2.9):
  1. upload handler writes thumbnail_source.png
  2. generate handler branches on body.use_upload (--still vs --shot)
  3. injected panel JS extended: mode row, painter, source preview, auto-switch
  4. thumbgen onclick: mode-aware validation + POST + success message
  5. APP_VERSION v2.9 -> v3.0

No apostrophes in added JS; anchors carry \\u2026 escapes exactly as on disk.

Run from the repo root:  python3 shared/patch_mc_thumb_source_mode.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_thumbsrc")

MARKER = "__THUMB_SRC"

NEW_PANEL_JS = '''
  // v3.0: thumbnail SOURCE modes — still # vs uploaded image. The uploaded
  // file persists as <root>/thumbnail_source.png; thumbnail.png is always the
  // derived composite. Bounce between sources and texts freely.
  window.__THUMB_SRC = window.__THUMB_SRC || "still";
  function paintThumbSrc() {
    const bs = document.getElementById("thumbsrc_still");
    const bu = document.getElementById("thumbsrc_up");
    const shotIn = document.getElementById("thumbshot");
    const up = (window.__THUMB_SRC === "upload");
    if (bs) bs.style.background = up ? "#2a2a36" : "#1c7c4a";
    if (bu) bu.style.background = up ? "#1c7c4a" : "#2a2a36";
    if (shotIn) { shotIn.disabled = up; shotIn.style.opacity = up ? "0.45" : "1"; }
  }
  const tmsgEl = document.getElementById("thumbmsg");
  if (tmsgEl && !document.getElementById("thumbup")) {
    const srcrow = document.createElement("div");
    srcrow.style.cssText = "margin-top:8px;display:flex;gap:8px;align-items:center;";
    srcrow.innerHTML =
      '<span style="color:#8a8a99;font:12px ui-monospace,monospace;">source:</span>' +
      '<button id="thumbsrc_still" style="background:#1c7c4a;color:#e8e6e3;border:1px solid #32323e;' +
      'border-radius:6px;padding:7px 10px;cursor:pointer;font:12px ui-monospace,monospace;">Still #</button>' +
      '<button id="thumbsrc_up" style="background:#2a2a36;color:#e8e6e3;border:1px solid #32323e;' +
      'border-radius:6px;padding:7px 10px;cursor:pointer;font:12px ui-monospace,monospace;">Uploaded image</button>';
    tmsgEl.parentElement.insertBefore(srcrow, tmsgEl);
    const upwrap = document.createElement("div");
    upwrap.style.cssText = "margin-top:8px;display:flex;gap:8px;align-items:center;";
    upwrap.innerHTML =
      '<input type="file" id="thumbfile" accept="image/png,image/jpeg" ' +
      'style="font:12px ui-monospace,monospace;color:#8a8a99;max-width:220px;">' +
      '<button id="thumbup" style="background:#3b5bdb;color:#fff;border:0;border-radius:6px;' +
      'padding:8px 10px;cursor:pointer;font:13px ui-monospace,monospace;">Upload source image</button>';
    tmsgEl.parentElement.insertBefore(upwrap, tmsgEl);
  }
  const bsrc = document.getElementById("thumbsrc_still");
  const busrc = document.getElementById("thumbsrc_up");
  if (bsrc) bsrc.onclick = function() { window.__THUMB_SRC = "still"; paintThumbSrc(); };
  if (busrc) busrc.onclick = function() { window.__THUMB_SRC = "upload"; paintThumbSrc(); };
  paintThumbSrc();
  const tup = document.getElementById("thumbup");
  const tfile = document.getElementById("thumbfile");
  if (tup && tfile) tup.onclick = function() {
    const f = tfile.files && tfile.files[0];
    const tmsg2 = document.getElementById("thumbmsg");
    const timg2 = document.getElementById("thumbimg");
    if (!f) { tmsg2.style.color = "#d46a6a"; tmsg2.textContent = "choose an image first"; return; }
    tmsg2.style.color = "#8a8a99"; tmsg2.textContent = "uploading\\u2026";
    const reader = new FileReader();
    reader.onload = async function() {
      try {
        const r = await api("/api/thumbnail_upload", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: ch, project: pr, data: reader.result})});
        if (r && r.ok) {
          window.__THUMB_SRC = "upload"; paintThumbSrc();
          tmsg2.style.color = "#14a3b8";
          tmsg2.textContent = "source uploaded - add headline and Generate";
          timg2.src = "/video/thumbnail_source.png" + q + "&_t=" + Date.now();
          timg2.style.display = "block";
        } else {
          tmsg2.style.color = "#d46a6a"; tmsg2.textContent = "error: " + ((r && r.error) || "failed");
        }
      } catch (e) { tmsg2.style.color = "#d46a6a"; tmsg2.textContent = "error: " + e; }
    };
    reader.readAsDataURL(f);
  };
'''

OLD_PANEL_JS = '''
  // v2.9: thumbnail upload path — external edit round-trip.
  const tmsgEl = document.getElementById("thumbmsg");
  if (tmsgEl && !document.getElementById("thumbup")) {
    const upwrap = document.createElement("div");
    upwrap.style.cssText = "margin-top:8px;display:flex;gap:8px;align-items:center;";
    upwrap.innerHTML =
      '<input type="file" id="thumbfile" accept="image/png,image/jpeg" ' +
      'style="font:12px ui-monospace,monospace;color:#8a8a99;max-width:220px;">' +
      '<button id="thumbup" style="background:#3b5bdb;color:#fff;border:0;border-radius:6px;' +
      'padding:8px 10px;cursor:pointer;font:13px ui-monospace,monospace;">Upload thumbnail</button>';
    tmsgEl.parentElement.insertBefore(upwrap, tmsgEl);
  }
  const tup = document.getElementById("thumbup");
  const tfile = document.getElementById("thumbfile");
  if (tup && tfile) tup.onclick = function() {
    const f = tfile.files && tfile.files[0];
    const tmsg2 = document.getElementById("thumbmsg");
    const timg2 = document.getElementById("thumbimg");
    if (!f) { tmsg2.style.color = "#d46a6a"; tmsg2.textContent = "choose an image first"; return; }
    tmsg2.style.color = "#8a8a99"; tmsg2.textContent = "uploading\\u2026";
    const reader = new FileReader();
    reader.onload = async function() {
      try {
        const r = await api("/api/thumbnail_upload", {method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({channel: ch, project: pr, data: reader.result})});
        if (r && r.ok) {
          tmsg2.style.color = "#14a3b8"; tmsg2.textContent = "thumbnail uploaded (" + (r.bytes || 0) + " bytes)";
          timg2.src = "/video/thumbnail.png" + q + "&_t=" + Date.now();
          timg2.style.display = "block";
        } else {
          tmsg2.style.color = "#d46a6a"; tmsg2.textContent = "error: " + ((r && r.error) || "failed");
        }
      } catch (e) { tmsg2.style.color = "#d46a6a"; tmsg2.textContent = "error: " + e; }
    };
    reader.readAsDataURL(f);
  };
'''

NEW_GEN_HANDLER = '''        shot = body.get("shot")
        use_upload = bool(body.get("use_upload"))
        title = (body.get("title") or "").strip()
        subtitle = (body.get("subtitle") or "").strip()
        if not use_upload:
            try:
                shot = int(shot)
            except Exception:
                self._json(400, {"ok": False,
                    "error": "shot must be an integer (or switch source to Uploaded image)"}); return
        if not title:
            self._json(400, {"ok": False, "error": "headline (title) is required"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        modea = Path(paths["modea"])
        root = Path(paths["project"])
        if use_upload:
            still = root / "thumbnail_source.png"
            if not still.exists():
                self._json(404, {"ok": False,
                    "error": "no uploaded source - upload an image first"}); return
        else:
            still = modea / "stills" / f"shot_{shot:03d}.png"
            if not still.exists():
                self._json(404, {"ok": False,
                    "error": f"still not found: shot_{shot:03d}.png (check the number)"}); return
        out = root / "thumbnail.png"
        import subprocess as _sp
        cmd = [sys.executable, str(Path(_SHARED) / "make_thumbnail.py"),
               "--project", str(modea),
               "--channel", ch,
               "--title", title,
               "--out", str(out)]
        if use_upload:
            cmd += ["--still", str(still)]
        else:
            cmd += ["--shot", str(shot)]
        if subtitle:
            cmd += ["--subtitle", subtitle]
        try:
            r = _sp.run(cmd, cwd=str(_REPO), capture_output=True, text=True)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"thumbnail failed: {e}"}); return
        if r.returncode != 0 or not out.exists():
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            self._json(500, {"ok": False, "error": " / ".join(tail) or "make_thumbnail failed"}); return
        self._json(200, {"ok": True, "shot": ("upload" if use_upload else shot)}); return'''

OLD_GEN_HANDLER = '''        shot = body.get("shot")
        title = (body.get("title") or "").strip()
        subtitle = (body.get("subtitle") or "").strip()
        try:
            shot = int(shot)
        except Exception:
            self._json(400, {"ok": False, "error": "shot must be an integer"}); return
        if not title:
            self._json(400, {"ok": False, "error": "headline (title) is required"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        modea = Path(paths["modea"])
        root = Path(paths["project"])
        still = modea / "stills" / f"shot_{shot:03d}.png"
        if not still.exists():
            self._json(404, {"ok": False,
                "error": f"still not found: shot_{shot:03d}.png (check the number)"}); return
        out = root / "thumbnail.png"
        import subprocess as _sp
        cmd = [sys.executable, str(Path(_SHARED) / "make_thumbnail.py"),
               "--project", str(modea),
               "--shot", str(shot),
               "--channel", ch,
               "--title", title,
               "--out", str(out)]
        if subtitle:
            cmd += ["--subtitle", subtitle]
        try:
            r = _sp.run(cmd, cwd=str(_REPO), capture_output=True, text=True)
        except Exception as e:
            self._json(500, {"ok": False, "error": f"thumbnail failed: {e}"}); return
        if r.returncode != 0 or not out.exists():
            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
            self._json(500, {"ok": False, "error": " / ".join(tail) or "make_thumbnail failed"}); return
        self._json(200, {"ok": True, "shot": shot}); return'''

NEW_TG = '''  if (tg) tg.onclick = async function() {
    const t = (document.getElementById("thumbtitle").value || "").trim();
    const s = (document.getElementById("thumbsub").value || "").trim();
    const n = parseInt(document.getElementById("thumbshot").value, 10);
    const tmsg = document.getElementById("thumbmsg");
    const timg = document.getElementById("thumbimg");
    const useUp = (window.__THUMB_SRC === "upload");
    if (!t) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a headline"; return; }
    if (!useUp && isNaN(n)) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a still number (or switch source to Uploaded image)"; return; }
    tmsg.style.color = "#8a8a99"; tmsg.textContent = "generating\\u2026";
    try {
      const r = await api("/api/thumbnail", {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({channel: ch, project: pr, shot: (useUp ? null : n),
                              use_upload: useUp, title: t, subtitle: s})});
      if (r && r.ok) {
        tmsg.style.color = "#14a3b8";
        tmsg.textContent = "thumbnail set (" + (r.shot === "upload" ? "uploaded source" : "still " + r.shot) + ")";'''

OLD_TG = '''  if (tg) tg.onclick = async function() {
    const t = (document.getElementById("thumbtitle").value || "").trim();
    const s = (document.getElementById("thumbsub").value || "").trim();
    const n = parseInt(document.getElementById("thumbshot").value, 10);
    const tmsg = document.getElementById("thumbmsg");
    const timg = document.getElementById("thumbimg");
    if (!t) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a headline"; return; }
    if (isNaN(n)) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a still number"; return; }
    tmsg.style.color = "#8a8a99"; tmsg.textContent = "generating\\u2026";
    try {
      const r = await api("/api/thumbnail", {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({channel: ch, project: pr, shot: n, title: t, subtitle: s})});
      if (r && r.ok) {
        tmsg.style.color = "#14a3b8"; tmsg.textContent = "thumbnail set (still " + r.shot + ")";'''

EDITS = [
    # 1. upload writes the persistent source, not the derived artifact
    (
        '''        out = root / "thumbnail.png"
        try:
            from PIL import Image as _Image''',

        '''        out = root / "thumbnail_source.png"
        try:
            from PIL import Image as _Image''',
    ),
    # 2. generate handler branches on source
    (OLD_GEN_HANDLER, NEW_GEN_HANDLER),
    # 3. injected panel JS: mode row + source preview + auto-switch
    (OLD_PANEL_JS, NEW_PANEL_JS),
    # 4. thumbgen onclick: mode-aware
    (OLD_TG, NEW_TG),
    # 5. version bump
    (
        '''APP_VERSION = "v2.9"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.0"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (__THUMB_SRC present) — no-op.")
        return

    if "thumbnail_upload" not in src or 'APP_VERSION = "v2.9"' not in src:
        sys.exit("!! prerequisite missing: thumbnail upload patch (v2.9) — anchors target that text.")

    for i, (old, _new) in enumerate(EDITS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"!! anchor {i} matched {n} times (need exactly 1) — file drifted, NOT patched.\n"
                     f"   anchor starts: {old.splitlines()[0]!r}")

    patched = src
    for old, new in EDITS:
        patched = patched.replace(old, new)

    if "\\'" in patched:
        sys.exit("!! escaped apostrophe found — refusing (JS double-decode doctrine).")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(patched)
        tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        sys.exit(f"!! patched text does not compile — target NOT modified.\n{e}")
    finally:
        Path(tmp).unlink(missing_ok=True)

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(patched, encoding="utf-8")
    print(f"patched {TARGET.name} (backup: {BACKUP.name})")
    print("  upload -> thumbnail_source.png (persistent source, preview, auto-switch)")
    print("  source modes: Still # / Uploaded image; Generate branches --shot / --still")
    print("  APP_VERSION v2.9 -> v3.0")


if __name__ == "__main__":
    main()
