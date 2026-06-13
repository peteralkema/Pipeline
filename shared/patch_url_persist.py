#!/usr/bin/env python3
"""
patch_url_persist.py — keep your project across a refresh (URL persistence).

WHY
  The selected project lived only in window.__SEL_VIEW (browser memory), so any
  refresh dropped you to base state. Desired model: refresh = stay in the project,
  Reset = jump out. This persists the selection in the URL (?channel=&project=,
  alongside ?key=) and restores it on load. Reset clears it.

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py — page JS)
  1. Read channel/project from the URL at load; seed __SEL_VIEW from them. Add a
     setUrlProject(ch, pr) helper (history.replaceState; preserves ?key=).
  2. proj.onchange: write the selection to the URL (or clear on deselect).
  3. create handler: write the new project to the URL.
  4. chan.onchange: clear channel/project from the URL.
  5. resetAll: clear channel/project from the URL (so a post-reset refresh stays base).
  6. ensureShell: on first build, if the URL names a project AND no run is active,
     restore the dropdown selection (chan + projects + proj) to match.

  Active runs are unaffected — the job record already drives the page during a run;
  URL persistence only covers the idle/browsing case.

DISCIPLINE
  Idempotent (sentinel: `function setUrlProject`). Six anchors, each verified once;
  backs up to .pre_urlpersist; re-compiles + rolls back on failure. Run from the
  repo root on the LAPTOP, then commit/push, then pull + restart + node-check on box.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "function setUrlProject"

EDITS = []

# 1. Top: read URL channel/project, seed __SEL_VIEW, add setUrlProject()
EDITS.append((
    "url helper + init",
    '''const KEY = new URLSearchParams(location.search).get("key") || "";
const H = KEY ? {"X-Review-Key": KEY} : {};''',
    '''const KEY = new URLSearchParams(location.search).get("key") || "";
const H = KEY ? {"X-Review-Key": KEY} : {};
const _U0 = new URLSearchParams(location.search);
const URL_CH = _U0.get("channel") || "";
const URL_PR = _U0.get("project") || "";
if (URL_CH && URL_PR) { window.__SEL_VIEW = URL_CH + "/" + URL_PR; }
function setUrlProject(ch, pr) {
  const u = new URL(location.href);
  if (ch && pr) { u.searchParams.set("channel", ch); u.searchParams.set("project", pr); }
  else { u.searchParams.delete("channel"); u.searchParams.delete("project"); }
  history.replaceState(null, "", u.toString());
}''',
))

# 2. proj.onchange: write/clear the URL
EDITS.append((
    "proj.onchange",
    '''  proj.onchange = () => {
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      window.__BODY_KEY = chan.value + "/" + proj.value + "|";  // matches idle poll key -> no double render
      renderStoryboard(chan.value, proj.value);
    } else {
      window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__"; clearStoryboard();
    }
    launch.disabled = !(chan.value && proj.value);
  };''',
    '''  proj.onchange = () => {
    if (chan.value && proj.value) {
      window.__SEL_VIEW = chan.value + "/" + proj.value;
      window.__BODY_KEY = chan.value + "/" + proj.value + "|";  // matches idle poll key -> no double render
      setUrlProject(chan.value, proj.value);
      renderStoryboard(chan.value, proj.value);
    } else {
      window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__"; setUrlProject("", ""); clearStoryboard();
    }
    launch.disabled = !(chan.value && proj.value);
  };''',
))

# 3. create handler: write the new project to the URL
EDITS.append((
    "create handler",
    '''    chan.value = r.folder;
    window.__SEL_VIEW = r.folder + "/" + r.slug;
    window.__BODY_KEY = "__none__";
    await refreshProjects(r.folder, r.slug);''',
    '''    chan.value = r.folder;
    window.__SEL_VIEW = r.folder + "/" + r.slug;
    window.__BODY_KEY = "__none__";
    setUrlProject(r.folder, r.slug);
    await refreshProjects(r.folder, r.slug);''',
))

# 4. chan.onchange: clear the URL
EDITS.append((
    "chan.onchange",
    '''  chan.onchange = () => {
    launch.disabled = true; window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
    clearStoryboard(); refreshProjects(chan.value);
  };''',
    '''  chan.onchange = () => {
    launch.disabled = true; window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
    setUrlProject("", ""); clearStoryboard(); refreshProjects(chan.value);
  };''',
))

# 5. resetAll: clear the URL
EDITS.append((
    "resetAll",
    '''  window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
  clearStoryboard();
  const chan = document.getElementById("chan");''',
    '''  window.__SEL_VIEW = ""; window.__BODY_KEY = "__none__";
  setUrlProject("", "");
  clearStoryboard();
  const chan = document.getElementById("chan");''',
))

# 6. ensureShell: restore the dropdown selection from the URL on first build
EDITS.append((
    "ensureShell restore",
    '''  return shell;
}

function updateControls(state) {''',
    '''  if (URL_CH && URL_PR && !isActiveRun(state.phase)) {
    (async function() {
      chan.value = URL_CH;
      await refreshProjects(URL_CH, URL_PR);
      window.__SEL_VIEW = URL_CH + "/" + URL_PR;
      window.__BODY_KEY = "";
      launch.disabled = !(chan.value && proj.value);
    })();
  }

  return shell;
}

function updateControls(state) {''',
))


def die(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    if not TARGET.exists():
        die(f"{TARGET} not found — run this from the repo root on the laptop.")

    src = TARGET.read_text()

    if MARKER in src:
        print(f"Already patched ({MARKER!r} present) — no changes made.")
        return

    for label, old, _ in EDITS:
        c = src.count(old)
        if c == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Confirm A0 + reset patches are applied and the box is in sync.)")
        if c > 1:
            die(f"anchor for {label} found {c}x (expected 1) — ambiguous; nothing written.")

    new = src
    for _, old, repl in EDITS:
        new = new.replace(old, repl)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_urlpersist")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    problems = []
    if MARKER not in check:
        problems.append("setUrlProject missing")
    if "URL_CH && URL_PR && !isActiveRun" not in check:
        problems.append("restore block missing")
    if problems:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed (" + "; ".join(problems) + ") — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   project selection now persists in the URL; refresh keeps your place, Reset clears it")
    print()
    print("AFTER you pull on the box, restart + node-check:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" -o /tmp/mc.html")
    print("   python3 - /tmp/mc.html <<'PY'")
    print("   import re, sys")
    print("   h = open(sys.argv[1]).read()")
    print("   b = re.findall(r\"<script>(.*?)</script>\", h, re.S)")
    print("   open(\"/tmp/mc.js\", \"w\").write(b[-1] if b else \"\")")
    print("   print(\"script blocks:\", len(b))")
    print("   PY")
    print("   node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
