#!/usr/bin/env python3
"""
patch_thumbnail_panel.py  --  Mission Control: thumbnail design panel in the done panel.

Adds a Thumbnail box to the FINAL VIDEO panel: headline + subtitle + still-number
fields and a Generate button. It shells make_thumbnail.py with the channel's LOCKED
thumbnail block doing all the layout (headline placement, font, margins, flat-pop) --
the panel only feeds which-still + text. --project points at modea (so --shot finds
modea/stills/shot_NNN.png); --out writes thumbnail.png at the PROJECT ROOT, exactly
where upload_episode.py auto-attaches it. It is a free PIL re-composite (no fal), so
you can spin through still numbers and headlines instantly, then hit Upload. Preview
is served via the existing /video/thumbnail.png asset route (no new route needed).

If a <project>/thumbnail_prop.png (transparent RGBA) exists, make_thumbnail composites
it as the prop-underneath automatically -- no panel change needed for that.

Idempotent (sentinel PATCH_THUMBNAIL_PANEL_APPLIED), anchor-verified, backs up to
<file>.pre_thumbnail_panel, py_compiles before writing.

RUN ON: LAPTOP -> commit -> push -> BOX git pull --no-edit -> restart mission-control
(not while animating).

    python3 patch_thumbnail_panel.py --file shared/mission_control/pipeline_server.py
"""

from __future__ import annotations
import argparse
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

SENTINEL = "PATCH_THUMBNAIL_PANEL_APPLIED"
DEFAULT_TARGET = "shared/mission_control/pipeline_server.py"

A_DOPOST = '    def do_POST(self):'
HANDLER  = '    def _handle_thumbnail(self, body):\n        """Composite a thumbnail from a chosen still + headline/subtitle, using the\n        channel\'s locked thumbnail block (make_thumbnail.py). --project points at\n        modea (so --shot finds modea/stills/shot_NNN.png); --out writes thumbnail.png\n        at the PROJECT ROOT where upload_episode.py looks. Free PIL re-composite:\n        iterate still-number + text as often as you like. (PATCH_THUMBNAIL_PANEL_APPLIED)"""\n        shot = body.get("shot")\n        title = (body.get("title") or "").strip()\n        subtitle = (body.get("subtitle") or "").strip()\n        try:\n            shot = int(shot)\n        except Exception:\n            self._json(400, {"ok": False, "error": "shot must be an integer"}); return\n        if not title:\n            self._json(400, {"ok": False, "error": "headline (title) is required"}); return\n        ch, pr = _resolve_request_project(body)\n        if not ch or not pr:\n            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return\n        paths = resolve_paths(ch, pr, _REPO)\n        modea = Path(paths["modea"])\n        root = Path(paths["project"])\n        still = modea / "stills" / f"shot_{shot:03d}.png"\n        if not still.exists():\n            self._json(404, {"ok": False,\n                "error": f"still not found: shot_{shot:03d}.png (check the number)"}); return\n        out = root / "thumbnail.png"\n        import subprocess as _sp\n        cmd = [sys.executable, str(Path(_SHARED) / "make_thumbnail.py"),\n               "--project", str(modea),\n               "--shot", str(shot),\n               "--channel", ch,\n               "--title", title,\n               "--out", str(out)]\n        if subtitle:\n            cmd += ["--subtitle", subtitle]\n        try:\n            r = _sp.run(cmd, cwd=str(_REPO), capture_output=True, text=True)\n        except Exception as e:\n            self._json(500, {"ok": False, "error": f"thumbnail failed: {e}"}); return\n        if r.returncode != 0 or not out.exists():\n            tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]\n            self._json(500, {"ok": False, "error": " / ".join(tail) or "make_thumbnail failed"}); return\n        self._json(200, {"ok": True, "shot": shot}); return\n\n'
A_ROUTE  = '        if path == "/api/upload":\n            self._handle_upload(body); return'
ROUTE_NEW = '        if path == "/api/upload":\n            self._handle_upload(body); return\n        if path == "/api/thumbnail":\n            self._handle_thumbnail(body); return'
A_BTN    = '    \'<button id="uploadbtn" \' +\n      \'style="background:#ff0000;">Upload to YouTube Studio (private)</button>\' +\n'
BTN_NEW  = '    \'<label>Thumbnail</label>\' +\n    \'<div style="border:1px solid #32323e;border-radius:8px;background:#161620;padding:10px;margin-bottom:14px;">\' +\n      \'<div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap;align-items:center;">\' +\n        \'<input id="thumbtitle" placeholder="Headline (e.g. 200,000 WENT SILENT)" style="flex:2;min-width:170px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">\' +\n        \'<input id="thumbsub" placeholder="Subtitle (optional)" style="flex:1;min-width:110px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">\' +\n        \'<input id="thumbshot" type="number" min="1" placeholder="still #" style="width:78px;background:#1c1c26;color:#e8e6e3;border:1px solid #32323e;border-radius:6px;padding:8px;font-size:13px;">\' +\n        \'<button id="thumbgen" style="background:#d4a017;margin-top:0;padding:8px 14px;font-size:13px;font-weight:600;">Generate</button>\' +\n      \'</div>\' +\n      \'<span id="thumbmsg" style="color:#8a8a99;font-size:12px;"></span>\' +\n      \'<img id="thumbimg" style="display:none;width:100%;border-radius:6px;margin-top:8px;background:#000;">\' +\n    \'</div>\' +\n    \'<button id="uploadbtn" \' +\n      \'style="background:#ff0000;">Upload to YouTube Studio (private)</button>\' +\n'
A_UB     = '  const ub = document.getElementById("uploadbtn");\n  if (ub) ub.onclick = function() { uploadVideo(ch, pr); };\n}'
UB_NEW   = '  const ub = document.getElementById("uploadbtn");\n  if (ub) ub.onclick = function() { uploadVideo(ch, pr); };  const tg = document.getElementById("thumbgen");\n  if (tg) tg.onclick = async function() {\n    const t = (document.getElementById("thumbtitle").value || "").trim();\n    const s = (document.getElementById("thumbsub").value || "").trim();\n    const n = parseInt(document.getElementById("thumbshot").value, 10);\n    const tmsg = document.getElementById("thumbmsg");\n    const timg = document.getElementById("thumbimg");\n    if (!t) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a headline"; return; }\n    if (isNaN(n)) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "enter a still number"; return; }\n    tmsg.style.color = "#8a8a99"; tmsg.textContent = "generating\\u2026";\n    try {\n      const r = await api("/api/thumbnail", {method: "POST",\n        headers: {"Content-Type": "application/json"},\n        body: JSON.stringify({channel: ch, project: pr, shot: n, title: t, subtitle: s})});\n      if (r && r.ok) {\n        tmsg.style.color = "#14a3b8"; tmsg.textContent = "thumbnail set (still " + r.shot + ")";\n        timg.src = "/video/thumbnail.png" + q + "&_t=" + Date.now();\n        timg.style.display = "block";\n      } else {\n        tmsg.style.color = "#d46a6a"; tmsg.textContent = "error: " + ((r && r.error) || "failed");\n      }\n    } catch (e) { tmsg.style.color = "#d46a6a"; tmsg.textContent = "error: " + e; }\n  };\n}'

EDITS = [
    ("_handle_thumbnail handler", A_DOPOST, HANDLER + A_DOPOST),
    ("/api/thumbnail route", A_ROUTE, ROUTE_NEW),
    ("thumbnail UI block", A_BTN, BTN_NEW),
    ("thumbnail JS handler", A_UB, UB_NEW),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_TARGET)
    args = ap.parse_args()
    target = Path(args.file)
    if not target.is_file():
        print(f"ERROR: target not found: {target}", file=sys.stderr); return 2
    src = target.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied (sentinel present) -> no-op: {target}"); return 0
    for label, old, _new in EDITS:
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor for '{label}' found {c} times (need exactly 1). "
                  f"Refusing to half-apply.", file=sys.stderr); return 3
    out = src
    for _label, old, new in EDITS:
        out = out.replace(old, new, 1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(out); tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: patched result does not compile:\n{e}", file=sys.stderr)
        tmp.unlink(missing_ok=True); return 4
    tmp.unlink(missing_ok=True)
    backup = target.with_suffix(target.suffix + ".pre_thumbnail_panel")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")
    print(f"OK  patched {target}")
    print(f"    backup  {backup}")
    print(f"    edits   {len(EDITS)} applied, result compiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
