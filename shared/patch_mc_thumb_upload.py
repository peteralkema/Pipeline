#!/usr/bin/env python3
"""
patch_mc_thumb_upload.py — v2.9: thumbnail UPLOAD path alongside the existing
generate-from-still. Iterate a poster in an external editor and push it back:
file input + Upload button in the thumbnail panel -> base64 JSON POST to
/api/thumbnail_upload -> server validates by decoding with PIL and re-saves as
PNG (JPEG uploads normalize automatically) -> writes <project-root>/thumbnail.png
— the SAME artifact the generate path writes and upload_episode.py reads —
-> preview cache-busts via the same /video/thumbnail.png line.

No multipart parsing (bare http.server): the client reads the file as a
dataURL and ships it in the ordinary JSON body; _read_json has no size cap.

4 anchored edits in shared/mission_control/pipeline_server.py (post-v2.8):
  1. panel JS: file input + Upload button injected beside thumbmsg, wired
  2. _handle_thumbnail_upload before do_POST
  3. POST route after /api/thumbnail
  4. APP_VERSION v2.8 -> v2.9

No apostrophes in added JS (double-decode doctrine); self-checked.

Run from the repo root:  python3 shared/patch_mc_thumb_upload.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_thumbup")

MARKER = "thumbnail_upload"

UPLOAD_JS = '''
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

UPLOAD_HANDLER = '''    def _handle_thumbnail_upload(self, body):
        """Accept an externally edited thumbnail: base64 image in the JSON body
        (dataURL or bare base64), validate by DECODING WITH PIL, re-save as PNG
        to <project-root>/thumbnail.png — the same artifact the generate path
        writes and upload_episode.py reads. JPEG uploads normalize to PNG."""
        import base64 as _b64
        from io import BytesIO as _BytesIO
        data = body.get("data") or ""
        if "," in data[:80]:
            data = data.split(",", 1)[1]  # strip dataURL prefix
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        root = Path(paths["project"])
        try:
            raw = _b64.b64decode(data, validate=True)
        except Exception:
            self._json(400, {"ok": False, "error": "body.data is not valid base64"}); return
        if len(raw) < 1024:
            self._json(400, {"ok": False, "error": "image too small to be a thumbnail"}); return
        out = root / "thumbnail.png"
        try:
            from PIL import Image as _Image
            img = _Image.open(_BytesIO(raw))
            img = img.convert("RGB")
            img.save(out, "PNG")
        except Exception as e:
            self._json(400, {"ok": False, "error": f"not a decodable image: {e}"}); return
        self._json(200, {"ok": True, "bytes": out.stat().st_size}); return

'''

EDITS = [
    # 1. panel JS: inject input + button and wire, inside the panel function scope
    #    (ch, pr, q all in scope), just before its closing brace
    (
        '''    } catch (e) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "error: " + e; }
  };
}

async function uploadVideo(ch, pr) {''',

        '''    } catch (e) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "error: " + e; }
  };
''' + UPLOAD_JS + '''}

async function uploadVideo(ch, pr) {''',
    ),
    # 2. server handler before do_POST
    (
        "    def do_POST(self):",
        UPLOAD_HANDLER + "    def do_POST(self):",
    ),
    # 3. route
    (
        '''        if path == "/api/thumbnail":
            self._handle_thumbnail(body); return''',

        '''        if path == "/api/thumbnail":
            self._handle_thumbnail(body); return
        if path == "/api/thumbnail_upload":
            self._handle_thumbnail_upload(body); return''',
    ),
    # 4. version bump
    (
        '''APP_VERSION = "v2.8"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.9"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (thumbnail_upload present) — no-op.")
        return

    if 'APP_VERSION = "v2.8"' not in src:
        sys.exit("!! prerequisite missing: v2.8 — anchors target that text.")

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
    print("  file input + Upload thumbnail button in the panel")
    print("  /api/thumbnail_upload: PIL-validated, JPEG normalized, writes <root>/thumbnail.png")
    print("  APP_VERSION v2.8 -> v2.9")


if __name__ == "__main__":
    main()
