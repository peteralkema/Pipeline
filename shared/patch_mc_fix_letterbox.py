#!/usr/bin/env python3
"""
patch_mc_fix_letterbox.py — v3.1: "Analyse + fix stills" button. Scans every
stills/shot_*.png for BAKED-IN letterbox bars (the fal dimension-clamp family:
flux returns a letterboxed frame inside the requested canvas — enforce_16x9
cannot see these because the canvas is already correct).

DETECTION (strict, protects dark cinematography): a bar row/column must be
near-uniform pure black (max luminance < 24, mean < 10) and the run must be
at least 2% of the dimension. Flux letterbox is dead black; real night scenes
carry highlights.

FIX: crop the live region, cover-resize back to the original canvas (LANCZOS,
center crop), overwrite the still. Originals backed up ONCE per shot to
stills/_pre_letterbox_fix/ — a SUBDIR so nothing globbing stills/shot_*.png
ever matches a backup. Response lists fixed shots and flags any that already
have a rendered clip (fixing the still does not fix the clip).

5 anchored edits in shared/mission_control/pipeline_server.py (post-v3.0):
  1. button next to "All static stills"
  2. click wiring (reports fixed shots + clip warnings in klingmsg)
  3. _handle_fix_letterbox before do_POST
  4. POST route after /api/thumbnail_upload
  5. APP_VERSION v3.0 -> v3.1

Run from the repo root:  python3 shared/patch_mc_fix_letterbox.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_fixbars")

MARKER = "fix_letterbox"

HANDLER = '''    def _handle_fix_letterbox(self, body):
        """Detect + repair baked-in letterbox bars across all stills. Strict
        detection (near-uniform pure black runs >= 2% of the dimension) so dark
        cinematography is never touched. Crop live region, cover-resize back to
        the original canvas, overwrite; one-time backups in _pre_letterbox_fix/.
        Returns {"fixed": [...], "have_clips": [...], "scanned": N}."""
        from PIL import Image as _Image, ImageStat as _Stat
        import math as _math
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        stills_dir = Path(paths["modea"]) / "stills"
        clips_dir = Path(paths["modea"]) / "clips"
        if not stills_dir.is_dir():
            self._json(404, {"ok": False, "error": f"no stills dir: {stills_dir}"}); return
        backup_dir = stills_dir / "_pre_letterbox_fix"

        def _bar_run(g, horizontal, from_start):
            W, H = g.size
            limit = H if horizontal else W
            n = 0
            rng = range(limit) if from_start else range(limit - 1, -1, -1)
            for i in rng:
                strip = g.crop((0, i, W, i + 1)) if horizontal else g.crop((i, 0, i + 1, H))
                lo, hi = strip.getextrema()
                if hi < 24 and _Stat.Stat(strip).mean[0] < 10:
                    n += 1
                else:
                    break
            return n

        fixed, have_clips = [], []
        scanned = 0
        for still in sorted(stills_dir.glob("shot_*.png")):
            scanned += 1
            try:
                im = _Image.open(still).convert("RGB")
            except Exception:
                continue
            W, H = im.size
            g = im.convert("L")
            top = _bar_run(g, True, True)
            bot = _bar_run(g, True, False)
            left = _bar_run(g, False, True)
            right = _bar_run(g, False, False)
            min_h = max(8, int(H * 0.02))
            min_w = max(8, int(W * 0.02))
            ct = top if top >= min_h else 0
            cb = bot if bot >= min_h else 0
            cl = left if left >= min_w else 0
            cr = right if right >= min_w else 0
            if not (ct or cb or cl or cr):
                continue
            live = im.crop((cl, ct, W - cr, H - cb))
            if live.width < W * 0.5 or live.height < H * 0.5:
                continue  # implausible: refuse to crop away most of the frame
            scale = max(W / live.width, H / live.height)
            nw = int(_math.ceil(live.width * scale))
            nh = int(_math.ceil(live.height * scale))
            r = live.resize((nw, nh), _Image.LANCZOS)
            x = (nw - W) // 2
            y = (nh - H) // 2
            out = r.crop((x, y, x + W, y + H))
            backup_dir.mkdir(exist_ok=True)
            bak = backup_dir / still.name
            if not bak.exists():
                shutil.copy2(still, bak)
            out.save(still, "PNG")
            fixed.append(still.name)
            if (clips_dir / (still.stem + ".mp4")).exists():
                have_clips.append(still.name)
        self._json(200, {"ok": True, "scanned": scanned,
                         "fixed": fixed, "have_clips": have_clips}); return

'''

WIRING = '''      const fb = document.getElementById("fixbarsbtn");
      if (fb) fb.onclick = async function() {
        const kmsg2 = document.getElementById("klingmsg");
        fb.disabled = true; fb.textContent = "Analysing stills\\u2026";
        try {
          const r = await api("/api/fix_letterbox", {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({channel: ch, project: pr})});
          if (r && r.ok) {
            if (kmsg2) {
              let t = "scanned " + r.scanned + ", fixed " + r.fixed.length +
                      (r.fixed.length ? ": " + r.fixed.join(", ") : "");
              if (r.have_clips && r.have_clips.length) {
                t += "  \\u26a0 already-rendered clips need re-render: " + r.have_clips.join(", ");
              }
              kmsg2.textContent = t;
            }
          } else if (kmsg2) {
            kmsg2.textContent = "fix failed: " + ((r && r.error) || "error");
          }
        } catch (e) { if (kmsg2) kmsg2.textContent = "fix failed: " + e; }
        fb.disabled = false; fb.textContent = "Analyse + fix stills";
      };
'''

EDITS = [
    # 1. button next to All static stills
    (
        """        '<button class="secondary" id="allstaticbtn">All static stills (no motion)</button>' +""",

        """        '<button class="secondary" id="allstaticbtn">All static stills (no motion)</button>' +
        '<button class="secondary" id="fixbarsbtn" title="Detect and crop baked-in black letterbox bars across all stills (originals backed up)">Analyse + fix stills</button>' +""",
    ),
    # 2. wiring just before the allstatic wiring
    (
        """      const sb = document.getElementById("allstaticbtn");""",

        WIRING + """      const sb = document.getElementById("allstaticbtn");""",
    ),
    # 3. handler before do_POST
    (
        "    def do_POST(self):",
        HANDLER + "    def do_POST(self):",
    ),
    # 4. route
    (
        '''        if path == "/api/thumbnail_upload":
            self._handle_thumbnail_upload(body); return''',

        '''        if path == "/api/thumbnail_upload":
            self._handle_thumbnail_upload(body); return
        if path == "/api/fix_letterbox":
            self._handle_fix_letterbox(body); return''',
    ),
    # 5. version bump
    (
        '''APP_VERSION = "v3.0"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.1"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (fix_letterbox present) — no-op.")
        return

    if 'APP_VERSION = "v3.0"' not in src:
        sys.exit("!! prerequisite missing: v3.0 — anchors target that text.")

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
    print("  Analyse + fix stills button; /api/fix_letterbox handler + route")
    print("  strict bar detection; backups in stills/_pre_letterbox_fix/; clip warnings")
    print("  APP_VERSION v3.0 -> v3.1")


if __name__ == "__main__":
    main()
