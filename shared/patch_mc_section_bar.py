#!/usr/bin/env python3
"""
patch_mc_section_bar.py — v3.8: sticky section-navigation bar on the
storyboard. One button per stage (COLD OPEN / PART II / ...), built from each
beat's b.stage. Clicking a button renders ONLY that section's beats; an ALL
button renders everything. This is pagination disguised as navigation: at
feature/all-trim scale (1000+ beats) only the visible section's autoplaying
clip videos exist, so the page survives Elijah.

Defaults: ALL when <= 200 beats (small projects unchanged); the first section
when > 200 (never mount 1500 autoplaying videos at once). Beats with an empty
stage fold into a synthetic "—" button so nothing is ever hidden. Active
button uses the green mode-language. Re-render preserves the chosen section.

The cost widget is unaffected in spirit — it sums the visible .motioncell
cells, so under a section filter it reports THIS SECTION's spend; a project
total line is added so both numbers are visible.

4 anchored edits in shared/mission_control/pipeline_server.py (post-v3.7):
  1. renderStoryboard: build the section bar + render the active section only
  2. a module-level current-section store + helper (window.__SB_SECTION)
  3. cost widget: add the "project $Y" line alongside the section figure
  4. APP_VERSION v3.7 -> v3.8

No apostrophes in added JS (double-decode doctrine); self-checked.

Run from the repo root:  python3 shared/patch_mc_section_bar.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_sectionbar")

MARKER = "__SB_SECTION"

# ---- 1. new renderStoryboard body (section-aware) ----
OLD_RENDER = '''  const beats = view.beats || [];
  const head = '<label>Storyboard — ' + pr + ' · ' + beats.length + ' beats · ' +
               (view.has_mode_b ? "dual-mode" : "Mode A") + '</label>';
  wrap.innerHTML = head + beats.map(b => beatRow(b, ch, pr)).join("");
  bindMotionBoxes(wrap);
}'''

NEW_RENDER = '''  const beats = view.beats || [];
  window.__SB_BEATS = beats;
  window.__SB_CTX = {ch: ch, pr: pr, has_mode_b: view.has_mode_b};
  // stage order = first-appearance order; empty stage folds into "—".
  const sections = [];
  beats.forEach(function(b) {
    const s = (b.stage && String(b.stage).trim()) || "\\u2014";
    if (sections.indexOf(s) === -1) sections.push(s);
  });
  // default section: ALL for small projects, the first section for large ones.
  if (window.__SB_SECTION == null || (window.__SB_SECTION !== "__ALL__" &&
      sections.indexOf(window.__SB_SECTION) === -1)) {
    window.__SB_SECTION = (beats.length <= 200 || sections.length <= 1)
      ? "__ALL__" : sections[0];
  }
  renderStoryboardSection(wrap, sections);
}

function renderStoryboardSection(wrap, sections) {
  const beats = window.__SB_BEATS || [];
  const ctx = window.__SB_CTX || {};
  const ch = ctx.ch, pr = ctx.pr;
  const sel = window.__SB_SECTION;
  function sectionOf(b) { return (b.stage && String(b.stage).trim()) || "\\u2014"; }
  const shown = (sel === "__ALL__") ? beats : beats.filter(function(b){ return sectionOf(b) === sel; });
  const btn = function(label, key, count) {
    const on = (sel === key);
    return '<button class="sbtab" data-key="' + key + '" style="margin:0 6px 6px 0;' +
      'background:' + (on ? "#1c7c4a" : "#2a2a36") + ';color:#e8e6e3;border:1px solid #32323e;' +
      'border-radius:6px;padding:6px 10px;cursor:pointer;font:12px ui-monospace,monospace;">' +
      label + ' <span style="color:#8a8a99;">(' + count + ')</span></button>';
  };
  let bar = '<div id="sectionbar" style="position:sticky;top:0;z-index:50;background:#12121a;' +
    'padding:8px 0 2px;margin-bottom:8px;border-bottom:1px solid #1e1e28;display:flex;flex-wrap:wrap;">';
  bar += btn("ALL", "__ALL__", beats.length);
  sections.forEach(function(s) {
    const c = beats.filter(function(b){ return sectionOf(b) === s; }).length;
    bar += btn(s, s, c);
  });
  bar += '</div>';
  const head = '<label>Storyboard — ' + pr + ' · ' + beats.length + ' beats · ' +
               (ctx.has_mode_b ? "dual-mode" : "Mode A") +
               (sel === "__ALL__" ? "" : ' · showing ' + sel + ' (' + shown.length + ')') + '</label>';
  wrap.innerHTML = head + bar + shown.map(function(b){ return beatRow(b, ch, pr); }).join("");
  wrap.querySelectorAll("button.sbtab").forEach(function(t) {
    t.addEventListener("click", function() {
      window.__SB_SECTION = t.getAttribute("data-key");
      renderStoryboardSection(wrap, sections);
    });
  });
  bindMotionBoxes(wrap);
}'''

# ---- 3. cost widget: project total line ----
OLD_WIDGET_TAIL = '''  const total = kling * CLIP_COST;
  const remaining = (kling - done) * CLIP_COST;
  w.style.display = "block";
  w.innerHTML =
    '<div style="color:#d4a017;letter-spacing:.06em;margin-bottom:4px;">ESTIMATED SPEND</div>' +
    '<div><b>' + kling + '</b> Kling &times; $' + CLIP_COST.toFixed(2) + ' = <b>$' + total.toFixed(2) + '</b></div>' +
    '<div style="color:#8a8a99;">' + kb + ' Ken-Burns + ' + inh + ' inherit = free</div>' +
    (done ? '<div style="color:#8a8a99;">' + done + ' already rendered &rarr; remaining ~<b style="color:#e8e6e3;">$' +
            remaining.toFixed(2) + '</b></div>' : '');
}'''

NEW_WIDGET_TAIL = '''  const total = kling * CLIP_COST;
  const remaining = (kling - done) * CLIP_COST;
  // project total across ALL beats (independent of the visible section filter):
  // beats not currently mounted are counted from the full beat list by mode
  // absence -> treated as Kling-eligible under N unless in the policy lists.
  let projTotal = null;
  try {
    const allBeats = window.__SB_BEATS || [];
    const N = (window.__KLING_N != null) ? window.__KLING_N : 40;
    const kbSet = window.__KB_SET || {}, inhSet = window.__INH_SET || {};
    if (allBeats.length && window.__SB_SECTION !== "__ALL__") {
      let pk = 0;
      allBeats.forEach(function(b, idx) {
        const bi = (b.index != null) ? b.index : idx;
        if (inhSet[bi]) return;
        if (kbSet[bi] || !(bi < N)) return;
        pk++;
      });
      projTotal = pk * CLIP_COST;
    }
  } catch (e) { projTotal = null; }
  w.style.display = "block";
  w.innerHTML =
    '<div style="color:#d4a017;letter-spacing:.06em;margin-bottom:4px;">ESTIMATED SPEND</div>' +
    '<div><b>' + kling + '</b> Kling &times; $' + CLIP_COST.toFixed(2) + ' = <b>$' + total.toFixed(2) + '</b>' +
      (projTotal != null ? ' <span style="color:#8a8a99;">(section)</span>' : '') + '</div>' +
    (projTotal != null ? '<div style="color:#8a8a99;">project total ~<b style="color:#e8e6e3;">$' +
      projTotal.toFixed(2) + '</b></div>' : '') +
    '<div style="color:#8a8a99;">' + kb + ' Ken-Burns + ' + inh + ' inherit = free (section)</div>' +
    (done ? '<div style="color:#8a8a99;">' + done + ' already rendered &rarr; remaining ~<b style="color:#e8e6e3;">$' +
            remaining.toFixed(2) + '</b></div>' : '');
}'''

# ---- 2b. capture kb/inherit sets on the GET so the project total is accurate ----
OLD_GET = '''      window.__KLING_N = (r && r.kling_count != null) ? r.kling_count : 40;
      const kbOn = {}, inhOn = {};
      ((r && r.kb_override) || []).forEach(function(b) { kbOn[b] = 1; });
      ((r && r.inherit_prev) || []).forEach(function(b) { inhOn[b] = 1; });'''

NEW_GET = '''      window.__KLING_N = (r && r.kling_count != null) ? r.kling_count : 40;
      const kbOn = {}, inhOn = {};
      ((r && r.kb_override) || []).forEach(function(b) { kbOn[b] = 1; });
      ((r && r.inherit_prev) || []).forEach(function(b) { inhOn[b] = 1; });
      window.__KB_SET = kbOn; window.__INH_SET = inhOn;'''

EDITS = [
    (OLD_RENDER, NEW_RENDER),
    (OLD_GET, NEW_GET),
    (OLD_WIDGET_TAIL, NEW_WIDGET_TAIL),
    (
        '''APP_VERSION = "v3.7"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v3.8"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("already applied (__SB_SECTION present) — no-op.")
        return

    if "costwidget" not in src or 'APP_VERSION = "v3.7"' not in src:
        sys.exit("!! prerequisite missing: cost widget (v3.7) — anchors target that text.")

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
    print("  sticky section bar; renders one part at a time (ALL default <=200 beats)")
    print("  empty stage folds into a — button; cost widget gains project-total line")
    print("  APP_VERSION v3.7 -> v3.8")


if __name__ == "__main__":
    main()
