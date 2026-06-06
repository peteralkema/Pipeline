# The `--animate-only` engine seam — written against the REAL source

Now that the repo is visible, this patch is matched to the actual `recreation_pipeline.py`
`cmd_finish`, not a described precedent. It is the one real engine change Mode A needs.

## Why it's needed

`cmd_finish` welds four phases: animate -> narrate -> score -> assemble. In the dual-mode
machine, audio is its own leg (runs first, owns VO + durations) and assembly is convergence
(the dual-mode assembler, NOT the engine's assemble()). So Mode A must run the animate
phase only and stop before narrate/score/assemble.

## The precedent, confirmed in the real source

`cmd_finish` already has `--assemble-only`, which returns EARLY after re-stitching, skipping
animate/narrate/score. `--animate-only` is its mirror: do the animate loop, then return
BEFORE narrate/score/assemble. Same gating shape, opposite slice.

## The patch — two edits to recreation_pipeline.py

### Edit 1 — register the flag (in main(), the finish subparser `c`), next to --assemble-only:

    c.add_argument("--animate-only", action="store_true",
                   help="animate stills to clips, then STOP (no narrate/score/assemble)")

### Edit 2 — the early return in cmd_finish, immediately AFTER the animate loop
(the `for s in shots:` loop that fills clip_paths) and BEFORE `print("\nNarrating script (Victor)...")`:

    if getattr(args, "animate_only", False):
        print(f"\nAnimate-only: {len(clip_paths)} clips in {p['clips']}, stopping "
              f"before narrate/score/assemble (audio + assembly are separate legs).")
        return

That's it. Two edits, mirroring --assemble-only. No change to existing finish runs.

## Preserved automatically (the leg's halt messages rely on these)

- Kling content-policy auto-fallback stays intact — it lives inside animate_still
  (_is_content_policy_error -> _still_to_held_clip), which the animate loop already calls.
  --animate-only only changes where cmd_finish STOPS, never how animate behaves.
- Clips land at <project>/clips/shot_NNN.mp4 — exactly where the Mode A leg globs shot_*.mp4.

## After applying

The Mode A leg's animate phase calls:
    recreation_pipeline.py finish --project <engine_project> --animate-only
and expects shot_*.mp4 in <engine_project>/clips/. With these two edits, that call does
precisely the animate-and-stop the orchestrator needs.
