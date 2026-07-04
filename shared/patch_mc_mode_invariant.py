#!/usr/bin/env python3
"""
patch_mc_mode_invariant.py — v2.6: every beat is always in exactly ONE visibly
active mode (idiot-proof, max craft, min cash):

  KLING   (default, neither toggle on): the motion box is the active control —
          green border; the preset that exactly matches the box text paints
          green (typing custom text un-greens it live). The beat renders its
          own 5s atom and is a SOURCE for inherit chains — the line says so.
  KB      green button; line: free Ken-Burns push on its own still - no atom.
  INHERIT green button; line names the source: "Inheriting beat J - chain of
          N beats on one atom = X.XXs (fits/exceeds)". Red cases name the
          offending source beat.

A Kling beat breaks any chain behind it and starts a new atom — exactly the
render pass walk-back, now painted.

6 anchored edits in shared/mission_control/pipeline_server.py (post-v2.5):
  1. MPRESETS hoisted to global + _applyBeatDisable extended (mode painting)
  2. local MPRESETS removed from the preset wiring (now reads the global)
  3. preset click repaints the cell (match-green updates immediately)
  4. motion box input listener repaints the cell (custom text un-greens)
  5. paintInhSums rewritten: per-mode lines, source-beat display
  6. APP_VERSION v2.5 -> v2.6

No apostrophes in added JS (double-decode doctrine); self-checked.

Run from the repo root:  python3 shared/patch_mc_mode_invariant.py
"""

import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "shared" / "mission_control" / "pipeline_server.py"
BACKUP = TARGET.with_suffix(".py.pre_modeinv")

MARKER = "mode invariant"

NEW_DISABLE = '''const MPRESETS = {
  dynamic: "dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere",
  slowcrane: "slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere"
};
function _applyBeatDisable(cell) {
  // mode invariant: exactly one mode visibly active per beat — Kling (green
  // box border + matching preset green), Ken-Burns (green button), or
  // inherit (green button). KB/inherit beats take no motion direction and
  // must not fire a manual Kling render.
  const dis = cell.dataset.kbon === "1" || cell.dataset.inhon === "1";
  const box = cell.querySelector("textarea.motionbox");
  const anim = cell.querySelector("button.animbtn");
  if (box) {
    box.disabled = dis; box.style.opacity = dis ? "0.45" : "1";
    box.style.border = dis ? "1px solid #32323e" : "1px solid #1c7c4a";
  }
  if (anim) { anim.disabled = dis; anim.style.opacity = dis ? "0.45" : "1"; }
  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    pb.disabled = dis; pb.style.opacity = dis ? "0.45" : "1";
    const match = !dis && box && box.value.trim() === MPRESETS[pb.getAttribute("data-preset")];
    pb.style.background = match ? "#1c7c4a" : "#2a2a36";
  });
}'''

NEW_SUMS = '''
function paintInhSums(wrap) {
  // per-mode status line, mirroring the render pass exactly.
  const arr = [];
  wrap.querySelectorAll(".motioncell").forEach(function(c) { arr.push(c); });
  function beatOf(cell) {
    const bx = cell.querySelector("textarea.motionbox");
    return bx ? parseInt((bx.getAttribute("data-mkey") || "").split("/").pop(), 10) : NaN;
  }
  for (var i = 0; i < arr.length; i++) {
    const el = arr[i].querySelector(".inhsum");
    if (!el) continue;
    if (arr[i].dataset.inhon === "1") {
      var j = i - 1;
      while (j >= 0 && arr[j].dataset.inhon === "1") j--;
      if (j < 0) {
        el.textContent = "no source atom - inherit chain reaches beat 0 (falls back free)";
        el.style.color = "#c0392b"; continue;
      }
      if (arr[j].dataset.kbon === "1") {
        el.textContent = "source beat " + beatOf(arr[j]) + " renders Ken-Burns - no atom to inherit (falls back free)";
        el.style.color = "#c0392b"; continue;
      }
      var d = parseFloat(arr[i].getAttribute("data-dur"));
      var total = d, bad = isNaN(d);
      for (var k = j; k < i && !bad; k++) {
        const dk = parseFloat(arr[k].getAttribute("data-dur"));
        if (isNaN(dk)) bad = true; else total += dk;
      }
      if (bad) {
        el.textContent = "Inheriting beat " + beatOf(arr[j]) + " (durations pending)";
        el.style.color = "#8a8a99"; continue;
      }
      const fits = total <= 5.0;
      el.textContent = "Inheriting beat " + beatOf(arr[j]) + " - chain of " + (i - j + 1) +
                       " beats on one atom = " + total.toFixed(2) + "s " +
                       (fits ? "(fits the 5s atom)" : "(exceeds the 5s atom - tail falls back)");
      el.style.color = fits ? "#1c7c4a" : "#c98a1a";
    } else if (arr[i].dataset.kbon === "1") {
      el.textContent = "free Ken-Burns push on its own still - no atom, nothing to inherit from";
      el.style.color = "#8a8a99";
    } else {
      el.textContent = "renders its own 5s Kling atom - source for inherit chains";
      el.style.color = "#8a8a99";
    }
  }
}'''

OLD_SUMS = '''
function paintInhSums(wrap) {
  // mirrors the inherit render pass: walk each beat back through inherited
  // predecessors to its source atom; red when the source is Ken-Burns or the
  // chain falls off the front; otherwise green/amber by 5s-atom fit.
  const arr = [];
  wrap.querySelectorAll(".motioncell").forEach(function(c) { arr.push(c); });
  for (var i = 0; i < arr.length; i++) {
    const el = arr[i].querySelector(".inhsum");
    if (!el) continue;
    const d = parseFloat(arr[i].getAttribute("data-dur"));
    if (i === 0 || isNaN(d)) { el.textContent = ""; continue; }
    var j = i - 1;
    while (j >= 0 && arr[j].dataset.inhon === "1") j--;
    if (j < 0) {
      el.textContent = "no source atom - inherit chain reaches beat 0 (falls back free)";
      el.style.color = "#c0392b"; continue;
    }
    if (arr[j].dataset.kbon === "1") {
      el.textContent = "previous renders Ken-Burns - no atom to inherit (falls back free)";
      el.style.color = "#c0392b"; continue;
    }
    var total = d, bad = false;
    for (var k = j; k < i; k++) {
      const dk = parseFloat(arr[k].getAttribute("data-dur"));
      if (isNaN(dk)) { bad = true; break; }
      total += dk;
    }
    if (bad) { el.textContent = ""; continue; }
    const fits = total <= 5.0;
    const label = (j === i - 1)
      ? "This beat plus previous beat = "
      : "Chain of " + (i - j + 1) + " beats on one atom = ";
    el.textContent = label + total.toFixed(2) + "s " +
                     (fits ? "(fits the 5s atom)" : "(exceeds the 5s atom - tail falls back)");
    el.style.color = fits ? "#1c7c4a" : "#c98a1a";
  }
}'''

EDITS = [
    # 1. global MPRESETS + extended _applyBeatDisable
    (
        '''function _applyBeatDisable(cell) {
  // a beat that renders nothing of its own (KB or inherit) takes no motion
  // direction and must not fire a manual Kling render.
  const dis = cell.dataset.kbon === "1" || cell.dataset.inhon === "1";
  const box = cell.querySelector("textarea.motionbox");
  const anim = cell.querySelector("button.animbtn");
  if (box) { box.disabled = dis; box.style.opacity = dis ? "0.45" : "1"; }
  if (anim) { anim.disabled = dis; anim.style.opacity = dis ? "0.45" : "1"; }
  cell.querySelectorAll("button.mpreset").forEach(function(pb) {
    pb.disabled = dis; pb.style.opacity = dis ? "0.45" : "1";
  });
}''',
        NEW_DISABLE,
    ),
    # 2. remove the local MPRESETS (global now)
    (
        '''    const MPRESETS = {
      dynamic: "dynamic cinematic camera movement, powerful momentum, natural realistic motion, dramatic atmosphere",
      slowcrane: "slow cinematic camera movement, crane-up to wide angle powerful momentum, natural realistic motion, dramatic atmosphere"
    };
    cell.querySelectorAll("button.mpreset").forEach(function(pb) {''',

        '''    cell.querySelectorAll("button.mpreset").forEach(function(pb) {''',
    ),
    # 3. preset click repaints the cell
    (
        '''        box.value = t;
        window.__MOTION_EDITS[box.getAttribute("data-mkey")] = t;
        saveMotion();''',

        '''        box.value = t;
        window.__MOTION_EDITS[box.getAttribute("data-mkey")] = t;
        saveMotion();
        _applyBeatDisable(cell);''',
    ),
    # 4. typing in the motion box repaints the cell (custom text un-greens the preset)
    (
        '''  wrap.querySelectorAll("textarea.motionbox").forEach(function(t) {
    t.addEventListener("input", function() {
      window.__MOTION_EDITS[t.getAttribute("data-mkey")] = t.value;
    });
  });''',

        '''  wrap.querySelectorAll("textarea.motionbox").forEach(function(t) {
    t.addEventListener("input", function() {
      window.__MOTION_EDITS[t.getAttribute("data-mkey")] = t.value;
      const mc = t.closest(".motioncell");
      if (mc) _applyBeatDisable(mc);
    });
  });''',
    ),
    # 5. mode-aware status lines with source-beat display
    (OLD_SUMS, NEW_SUMS),
    # 6. version bump
    (
        '''APP_VERSION = "v2.5"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
        '''APP_VERSION = "v2.6"  # hand-bumped each shipped page change; pairs with the auto git SHA''',
    ),
]


def main():
    if not TARGET.is_file():
        sys.exit(f"!! target not found: {TARGET} — run from the repo (script lives in shared/)")

    src = TARGET.read_text(encoding="utf-8")

    if "mode invariant" in src:
        print("already applied (mode invariant present) — no-op.")
        return

    if "paintInhSums" not in src or 'APP_VERSION = "v2.5"' not in src:
        sys.exit("!! prerequisite missing: aware-sum patch (v2.5) — anchors target that text.")

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
    print("  mode invariant: Kling (green box + matching preset) / KB / inherit — one always active")
    print("  status line names the source beat; live repaint on preset click and typing")
    print("  APP_VERSION v2.5 -> v2.6")


if __name__ == "__main__":
    main()
