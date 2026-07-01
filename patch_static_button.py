#!/usr/bin/env python3
"""
patch_static_button.py  --  Mission Control: the "All static stills" button.

WHAT IT DOES (three coupled, non-breaking edits to pipeline_server.py):
  1. /api/render_policy POST  -- persist an optional `static` bool alongside
     kling_count, MERGING (a plain N-change no longer clobbers static, and
     setting static no longer clobbers N).
  2. /api/render_policy GET   -- return `static` too, so the page reflects state.
  3. Stills-gate JS           -- a "All static stills (no motion)" button next to
     the Kling-N field. One click => N=0 + static:true persisted to
     render_policy.json. For QQrew this ships a fully static video today (the
     Ken-Burns floor already renders static); the `static` flag is read by the
     native-static render patch (Patch B) when that lands.

SAFE: additive only. Does NOT touch ken_burns_still / finish() / animate routing
(that's the separate render-side patch that needs the tuned-zoom .bak). Idempotent:
re-running is a no-op via the sentinel. Backs up to <file>.pre_static_button.
Verifies every anchor appears exactly once and refuses to half-apply. py_compiles
the result before writing.

RUN ON: LAPTOP (edits the repo), then commit -> push -> BOX `git pull --no-edit`
-> restart mission-control (NOT while a render is animating).

    python3 patch_static_button.py            # default target path
    python3 patch_static_button.py --file <path/to/pipeline_server.py>
"""

from __future__ import annotations
import argparse
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

SENTINEL = "PATCH_STATIC_BUTTON_APPLIED"
DEFAULT_TARGET = "shared/mission_control/pipeline_server.py"


# --- (edit 1) render_policy POST: merge static, don't clobber -----------------
POST_OLD = '''    def _handle_render_policy_post(self, body):
        """Write TIERED RENDER N to render_policy.json at the project root (next to durations.json)."""
        import json as _json
        try:
            kc = max(0, int(body.get("kling_count")))
        except Exception:
            self._json(400, {"ok": False, "error": "kling_count must be a non-negative integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        try:
            rp.write_text(_json.dumps({"kling_count": kc}, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "kling_count": kc}); return'''

POST_NEW = '''    def _handle_render_policy_post(self, body):
        """Write TIERED RENDER policy to render_policy.json at the project root.
        MERGES with any existing file: kling_count and static are each updated
        only when present in the body, so a plain N-change never clobbers static
        and setting static never clobbers N. (PATCH_STATIC_BUTTON_APPLIED)"""
        import json as _json
        try:
            kc = max(0, int(body.get("kling_count")))
        except Exception:
            self._json(400, {"ok": False, "error": "kling_count must be a non-negative integer"}); return
        ch, pr = _resolve_request_project(body)
        if not ch or not pr:
            self._json(400, {"ok": False, "error": "no project (pass channel+project)"}); return
        paths = resolve_paths(ch, pr, _REPO)
        rp = paths["project"] / "render_policy.json"
        existing = {}
        if rp.is_file():
            try:
                existing = _json.loads(rp.read_text()) or {}
            except Exception:
                existing = {}
        policy = dict(existing)
        policy["kling_count"] = kc
        if "static" in (body or {}):
            policy["static"] = bool(body.get("static"))
        try:
            rp.write_text(_json.dumps(policy, indent=2))
        except Exception as e:
            self._json(500, {"ok": False, "error": f"write failed: {e}"}); return
        self._json(200, {"ok": True, "kling_count": kc,
                         "static": bool(policy.get("static", False))}); return'''


# --- (edit 2) render_policy GET: surface static -------------------------------
GET_OLD = '''        rp = paths["project"] / "render_policy.json"
        n = 40
        if rp.is_file():
            try:
                n = int(_json.loads(rp.read_text()).get("kling_count", 40))
            except Exception:
                n = 40
        self._json(200, {"ok": True, "kling_count": n, "default": 40}); return'''

GET_NEW = '''        rp = paths["project"] / "render_policy.json"
        n = 40
        static = False
        if rp.is_file():
            try:
                _rpj = _json.loads(rp.read_text())
                n = int(_rpj.get("kling_count", 40))
                static = bool(_rpj.get("static", False))
            except Exception:
                n = 40; static = False
        self._json(200, {"ok": True, "kling_count": n, "static": static, "default": 40}); return'''


# --- (edit 3a) the button element in the stills-gate innerHTML ----------------
BTN_OLD = ('''        \'<span style="color:#8a8a99;margin-left:8px;">beats \u2014 the rest render free (Ken Burns zoom). <span id="klingmsg" style="color:#14a3b8;"></span></span>\' +
      \'</div>\' +
      \'<div class="row">\' +''')

BTN_NEW = ('''        \'<span style="color:#8a8a99;margin-left:8px;">beats \u2014 the rest render free (Ken Burns zoom). <span id="klingmsg" style="color:#14a3b8;"></span></span>\' +
      \'</div>\' +
      \'<div class="row" style="margin:0 0 8px;align-items:center;">\' +
        \'<button class="secondary" id="allstaticbtn">All static stills (no motion)</button>\' +
        \'<span id="staticmsg" style="color:#8a8a99;margin-left:8px;"></span>\' +
      \'</div>\' +
      \'<div class="row">\' +''')


# --- (edit 3b) the click handler inside the async IIFE -----------------------
HANDLER_OLD = '''          if (msg) msg.textContent = (rr && rr.ok) ? ("saved N=" + rr.kling_count) : "save failed";
        } catch (e) { if (msg) msg.textContent = "save failed"; }
      });
    })();'''

HANDLER_NEW = '''          if (msg) msg.textContent = (rr && rr.ok) ? ("saved N=" + rr.kling_count) : "save failed";
        } catch (e) { if (msg) msg.textContent = "save failed"; }
      });
      const sb = document.getElementById("allstaticbtn");
      if (sb) sb.addEventListener("click", async function() {
        inp.value = 0;
        const smsg = document.getElementById("staticmsg");
        const kmsg = document.getElementById("klingmsg");
        try {
          const rr = await api("/api/render_policy", {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({channel: ch, project: pr, kling_count: 0, static: true})});
          if (smsg) smsg.textContent = (rr && rr.ok) ? "set: all static, no Kling" : "save failed";
          if (kmsg) kmsg.textContent = "saved N=0";
        } catch (e) { if (smsg) smsg.textContent = "save failed"; }
      });
    })();'''


EDITS = [
    ("render_policy POST (merge static)", POST_OLD, POST_NEW),
    ("render_policy GET (surface static)", GET_OLD, GET_NEW),
    ("stills-gate static button element", BTN_OLD, BTN_NEW),
    ("stills-gate static button handler", HANDLER_OLD, HANDLER_NEW),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_TARGET,
                    help="path to pipeline_server.py")
    args = ap.parse_args()

    target = Path(args.file)
    if not target.is_file():
        print(f"ERROR: target not found: {target}", file=sys.stderr)
        return 2

    src = target.read_text(encoding="utf-8")

    if SENTINEL in src:
        print(f"already applied (sentinel present) -> no-op: {target}")
        return 0

    # verify every anchor appears exactly once BEFORE touching anything
    for label, old, _new in EDITS:
        c = src.count(old)
        if c != 1:
            print(f"ERROR: anchor for '{label}' found {c} times (need exactly 1). "
                  f"Refusing to half-apply.", file=sys.stderr)
            return 3

    out = src
    for _label, old, new in EDITS:
        out = out.replace(old, new, 1)

    # compile the candidate in a temp file before writing over the target
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(out)
        tmp = Path(tf.name)
    try:
        py_compile.compile(str(tmp), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"ERROR: patched result does not compile:\n{e}", file=sys.stderr)
        tmp.unlink(missing_ok=True)
        return 4
    tmp.unlink(missing_ok=True)

    backup = target.with_suffix(target.suffix + ".pre_static_button")
    shutil.copy2(target, backup)
    target.write_text(out, encoding="utf-8")
    print(f"OK  patched {target}")
    print(f"    backup  {backup}")
    print(f"    edits   {len(EDITS)} applied, result compiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
