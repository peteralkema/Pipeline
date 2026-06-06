#!/usr/bin/env python3
"""
serve_modeb_review.py — Piece 2 of the Mode B gate. The local server behind the review page.

Serves:
  GET  /                     -> the review HTML (regenerated fresh each load)
  GET  /clip/<name>.mp4      -> a rendered clip file (autoplay in the page)
Handles button POSTs:
  POST /rerender {index,payload}  -> write edited payload into beats.json, run dispatch --only N,
                                     return {ok, clip} so the page hot-swaps the clip
  POST /flag     {index}          -> record beat N as flagged-for-loopback
  POST /done                      -> signal review complete (server prints, orchestrator continues)

Run on the box; tunnel from the laptop (orchestrator prints the idiot-proof block). Same
pattern as serve_review.py for stills. Re-render is the "magical seconds": edit the data,
click, the one clip regenerates via the PROVEN dispatch.py. Duration is never editable here.

Usage: serve_modeb_review.py --project <dir> --beats <beats.json> --clips <clips_dir>
       [--durations <p>] [--shared <dir>] [--port 8000]
"""
import os, sys, json, argparse, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_modeb_review

STATE = {"flagged": set(), "done": False, "rerendered": []}


class Handler(BaseHTTPRequestHandler):
    cfg = {}  # injected: project, beats, clips, durations, shared, py

    def log_message(self, *a):  # quiet — the orchestrator owns telemetry
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        c = self.cfg
        if self.path == "/" or self.path.startswith("/?"):
            # regenerate the page fresh so re-rendered payloads/clips show on reload
            out = os.path.join(c["project"], "modeb_review.html")
            make_modeb_review.build_page(c["project"], c["beats"], c["clips"], out)
            self._send(200, Path(out).read_text(encoding="utf-8"), "text/html; charset=utf-8")
            return
        if self.path.startswith("/clip/"):
            name = os.path.basename(self.path[len("/clip/"):].split("?")[0])
            # clips may live in the configured clips dir OR repo-root clips/ (current reality)
            for d in (c["clips"], os.path.join(os.path.dirname(c["shared"]), "clips"), "clips"):
                fp = os.path.join(d, name)
                if os.path.isfile(fp):
                    data = open(fp, "rb").read()
                    self._send(200, data, "video/mp4")
                    return
            self._send(404, {"error": f"clip not found: {name}"})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        c = self.cfg
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except Exception:
            data = {}

        if self.path == "/flag":
            idx = int(data.get("index"))
            STATE["flagged"].add(idx)
            print(f"  [gate] beat {idx} FLAGGED for loop-back (audio-affecting / render bug)")
            self._send(200, {"ok": True, "flagged": sorted(STATE["flagged"])})
            return

        if self.path == "/done":
            STATE["done"] = True
            print("  [gate] review submitted by user.")
            self._send(200, {"ok": True})
            return

        if self.path == "/rerender":
            idx = int(data.get("index"))
            new_payload = data.get("payload", {})
            # 1) write the edited payload into beats.json for THIS beat
            beats = json.load(open(c["beats"], encoding="utf-8"))
            comp = None
            for b in beats:
                if b.get("index") == idx:
                    comp = b.get("component")
                    # the page sent EDITED shaped props (editable fields only). Merge them
                    # with the audio-locked fields (re-derived) so the override is complete,
                    # then store as _props_override → renders verbatim (what you edited renders).
                    try:
                        import dispatch as _d
                        full_shaped, _ = _d.shape_props(comp, b.get("payload", {}), b)
                    except Exception:
                        full_shaped = {}
                    merged = dict(full_shaped)      # start from full shaped props (has locked fields)
                    merged.update(new_payload)      # apply the user's edits on top
                    b["_props_override"] = merged
                    break
            if comp is None:
                self._send(200, {"ok": False, "error": f"beat {idx} not found / not Mode B"})
                return
            json.dump(beats, open(c["beats"], "w", encoding="utf-8"), indent=2, ensure_ascii=False)

            # 2) re-render JUST this beat via the proven dispatch.py
            cmd = [c["py"], os.path.join(c["shared"], "dispatch.py"), c["beats"],
                   "--render", "--only", str(idx)]
            if c.get("durations"):
                cmd += ["--durations", c["durations"]]
            print(f"  [gate] re-rendering beat {idx} ({comp}) with edited payload…")
            r = subprocess.run(cmd, capture_output=True, text=True)
            ok = r.returncode == 0 and "=> " in (r.stdout or "")
            clip_name = f"beat_{idx:02d}_B_{comp}.mp4"
            if ok:
                STATE["rerendered"].append(idx)
                print(f"  [gate] ✓ beat {idx} re-rendered → {clip_name}")
                self._send(200, {"ok": True, "clip": f"/clip/{clip_name}"})
            else:
                tail = (r.stdout or r.stderr or "").strip().splitlines()
                msg = tail[-1] if tail else "render failed"
                print(f"  [gate] ✗ beat {idx} re-render failed: {msg}")
                self._send(200, {"ok": False, "error": msg})
            return

        self._send(404, {"error": "unknown POST"})


def serve(project, beats, clips, durations, shared, port):
    Handler.cfg = {"project": project, "beats": beats, "clips": clips,
                   "durations": durations, "shared": shared, "py": sys.executable}
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Mode B review server on :{port}  (project={project})")
    print("  GET / = review page · POST /rerender /flag /done")
    print("  Ctrl-C to stop when done reviewing.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nserver stopped.")
    return STATE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--beats", required=True)
    ap.add_argument("--clips", required=True)
    ap.add_argument("--durations", default=None)
    ap.add_argument("--shared", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    serve(a.project, a.beats, a.clips, a.durations, a.shared, a.port)


if __name__ == "__main__":
    main()
