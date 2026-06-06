#!/usr/bin/env python3
"""
telemetry.py — the orchestrator's single voice. ONE home for all log formatting.

Altitude: orchestrator-level, not implementation. Every leg reports THROUGH this.
~20 lines visible at a time — phase headers structure the screen; long loops call
step_progress() which rewrites ONE line instead of printing N. Verbosity dial set
at kickoff: quiet | normal | verbose.

Line vocabulary (visually distinct so the screen reads as a story):
  ━━ PHASE ━━   phase()      phase header
  ✓             ok()         step + result (+ metric)
  →             decision()   a choice the orchestrator made (the teaching lines)
  ℹ             info()       a metric / fact
  $             cost()       spend marker
  ⏸             gate()       a human-gate stop
  ⚠             warn()       non-fatal warning
  ✗             halt()       fatal — caller exits after
"""
import sys

LEVELS = {"quiet": 0, "normal": 1, "verbose": 2}

class Telemetry:
    def __init__(self, level="normal"):
        self.level = LEVELS.get(level, 1)
        self.level_name = level

    # --- always shown (every level) ---
    def phase(self, title):
        bar = "━" * max(4, 56 - len(title))
        print(f"\n━━ {title} ━━{bar}")

    def ok(self, msg):
        print(f"  ✓ {msg}")

    def decision(self, msg):
        # the teaching lines — always shown; this is how Peter learns the machine
        print(f"  → {msg}")

    def gate(self, msg):
        print(f"  ⏸ {msg}")

    def warn(self, msg):
        print(f"  ⚠ {msg}")

    def halt(self, msg):
        print(f"  ✗ HALTED: {msg}", file=sys.stderr)

    def cost(self, msg):
        print(f"  $ {msg}")

    # --- normal + verbose ---
    def info(self, msg):
        if self.level >= 1:
            print(f"  ℹ {msg}")

    # --- verbose only (the under-the-surface detail) ---
    def detail(self, msg):
        if self.level >= 2:
            print(f"    · {msg}")

    # --- one updating line for long loops (keeps screen to ~20 lines) ---
    def step_progress(self, msg, done=False):
        end = "\n" if done else "\r"
        print(f"  … {msg}", end=end, flush=True)

    # --- the run-context line under the banner ---
    def context(self, channel, project, n_beats, n_a, n_b, when):
        print(f"  ▸ channel: {channel}   project: {project}   "
              f"beats: {n_beats} (A:{n_a} B:{n_b})   {when}")

    def rule(self):
        print("  " + "─" * 60)
