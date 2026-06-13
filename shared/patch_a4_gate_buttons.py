#!/usr/bin/env python3
"""
patch_a4_gate_buttons.py — make the stills-gate buttons actually fire (A4).

ROOT CAUSE
  The stills-gate buttons were built by string concat using _SQ (single quote)
  for BOTH the HTML attribute delimiter AND the JS call argument:

      '<button onclick=' + _SQ + 'gate(' + _SQ + 'go' + _SQ + ')' + _SQ + '>...'
      => <button onclick='gate('go')'>Generate Clips…</button>

  The onclick attribute closes right after "gate(", so the click runs the
  fragment `gate(` — a SyntaxError that fires no fetch. So the decision never
  reached /api/gate/stills and gate.decision stayed None. The button looked
  dead; it was malformed HTML. (The audio gate works because its buttons sit in
  a backtick template as onclick="gate('keep')" — valid double/single nesting.)

WHAT THIS DOES (one file: shared/mission_control/pipeline_server.py)
  1. Rebuild the two stills-gate buttons with a double-quote attribute delimiter
     and _SQ only for the inner arg -> onclick="gate('go')" (valid nesting).
  2. Relabel "Skip" -> "Stop here (keep stills, no clips)" (A2 backend now
     honours the `skip` decision; the label was misleading).
  3. Make gate() read the response and show a visible toast on success/error,
     so a failed decision-write is never silent again (also confirms the audio
     gate). Adds a small toast() helper.

  After this: Generate Clips approves stills, Stop here writes `skip` (which the
  A2 backend turns into a clean stop, stills preserved), and both gates show a
  confirmation toast.

NOT FIXED HERE (intentionally)
  py_compile only proves the Python file still parses — it does NOT validate the
  embedded JS. After pulling on the box, RESTART the service and run the §5
  node --check guard before trusting the page (commands printed at the end).

DISCIPLINE
  Idempotent (sentinel: `function toast(text)`). Verifies both anchors exist
  exactly once before writing; backs up to a .pre_a4gate sidecar; re-compiles
  and rolls back on failure. Run from the repo root on the LAPTOP, then
  commit/push, then pull on the box, then RESTART the service.
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path("shared/mission_control/pipeline_server.py")
MARKER = "function toast(text)"

OLD_BUTTONS = "\n".join([
    "        '<button onclick=' + _SQ + 'gate(' + _SQ + 'go' + _SQ + ')' + _SQ +",
    "          '>Generate Clips (approve stills)</button>' +",
    "        '<button class=\"secondary\" onclick=' + _SQ + 'gate(' + _SQ + 'skip' + _SQ + ')' + _SQ +",
    "          '>Skip</button>' +",
])

NEW_BUTTONS = "\n".join([
    "        '<button onclick=\"gate(' + _SQ + 'go' + _SQ + ')\">Generate Clips (approve stills)</button>' +",
    "        '<button class=\"secondary\" onclick=\"gate(' + _SQ + 'skip' + _SQ + ')\">Stop here (keep stills, no clips)</button>' +",
])

OLD_GATE = "\n".join([
    'async function gate(decision) {',
    '  const s = await api("/api/state");',
    '  await api("/api/gate/"+ (s.gate?s.gate.name:"") , {method:"POST",',
    '    headers:{"Content-Type":"application/json"},',
    '    body: JSON.stringify({decision})});',
    '  poll();',
    '}',
])

NEW_GATE = "\n".join([
    'async function gate(decision) {',
    '  const s = await api("/api/state");',
    '  const name = s.gate ? s.gate.name : "";',
    '  const r = await api("/api/gate/" + name, {method:"POST",',
    '    headers:{"Content-Type":"application/json"},',
    '    body: JSON.stringify({decision})});',
    '  if (r && r.ok === false) { toast("gate error: " + (r.error || "write failed")); }',
    '  else { toast("decision sent: " + decision); }',
    '  poll();',
    '}',
    'function toast(text) {',
    '  let tt = document.getElementById("mc_toast");',
    '  if (!tt) {',
    '    tt = document.createElement("div");',
    '    tt.id = "mc_toast";',
    '    tt.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);" +',
    '      "background:#1c1c26;color:#e8e6e3;border:1px solid #d4a017;border-radius:8px;" +',
    '      "padding:10px 16px;font-size:13px;z-index:9999;max-width:80vw;box-shadow:0 4px 20px rgba(0,0,0,.5);";',
    '    document.body.appendChild(tt);',
    '  }',
    '  tt.textContent = text;',
    '  tt.style.opacity = "1";',
    '  clearTimeout(window.__toastTimer);',
    '  window.__toastTimer = setTimeout(function(){ tt.style.opacity = "0"; }, 4000);',
    '}',
])


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

    for label, anchor in (("stills-gate buttons", OLD_BUTTONS), ("gate() handler", OLD_GATE)):
        n = src.count(anchor)
        if n == 0:
            die(f"anchor for {label} NOT FOUND — file shape changed; nothing written. "
                f"(Suspect an out-of-sync box or a prior hand-edit of the served page.)")
        if n > 1:
            die(f"anchor for {label} found {n}x (expected 1) — ambiguous; nothing written.")

    new = src.replace(OLD_BUTTONS, NEW_BUTTONS).replace(OLD_GATE, NEW_GATE)
    if new == src:
        die("replace produced no change — nothing written.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_a4gate")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(new)

    check = TARGET.read_text()
    if MARKER not in check or 'onclick="gate(' not in check:
        shutil.copy2(backup, TARGET)
        die("post-write verification failed — restored from backup.")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, TARGET)
        die(f"result does not compile — restored from backup.\n{e}")

    print(f"OK patched {TARGET}")
    print(f"   backup: {backup.name}")
    print("   1) stills-gate buttons: valid onclick nesting (Generate Clips / Stop now fire)")
    print("   2) Skip -> 'Stop here (keep stills, no clips)'")
    print("   3) gate() shows a success/error toast (audio + stills)")
    print()
    print("AFTER you pull on the box, you MUST restart + node-check before trusting it:")
    print("   systemctl --user restart mission-control.service")
    print("   curl -s \"http://127.0.0.1:8002/?key=fh2026\" | python3 -c \"import sys,re; "
          "m=re.search(r'<script>(.*?)</script>', sys.stdin.read(), re.S); "
          "open('/tmp/mc.js','w').write(m.group(1))\" && node --check /tmp/mc.js && echo PAGE_JS_VALID")


if __name__ == "__main__":
    main()
