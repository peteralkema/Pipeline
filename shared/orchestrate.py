#!/usr/bin/env python3
"""
orchestrate.py — the conductor.

Runs the post-script pipeline end to end, so the only human work after script-lock
is: (gate 1) confirm the canon distribution, and (gate 2) review the stills. Every
other step is sequenced automatically.

It does NOT contain any generation logic. It calls the existing scripts as
subprocesses and guards their outputs between phases. If a phase's expected output
is missing or wrong, it halts and tells you — it never barrels on.

INPUTS (the two things only a human/Claude produces):
  - projects/<project>/<project>_script.txt   (pure narration prose)
  - projects/<project>/canon.json             (dict: {token: scene description})

PHASES:
  1 storyboard   recreation_pipeline.py stills --script ... --storyboard-only
  2 audit        audit_storyboard_discipline.py --project ...
  3 canon        build_canon.py --project ... --canon ...
     >>> GATE 1: confirm canon distribution (y/n)
  4 stills       recreation_pipeline.py stills --beats ... --project ...
     (auto silent-reject check)
     >>> GATE 2: review stills in browser, then "continue?" (y/n)
  5 finish       recreation_pipeline.py finish --project ... --no-music
  6 trueup       recreation_pipeline.py finish --project ... --no-music --assemble-only

Usage (from channel root, e.g. final-hours/):
    python ../shared/orchestrate.py --project tay_bridge

    # script/canon at non-default paths:
    python ../shared/orchestrate.py --project tay_bridge \
        --script projects/tay_bridge/tay_bridge_script.txt \
        --canon  projects/tay_bridge/canon.json

    # re-run from a later phase (e.g. after fixing the canon at gate 1):
    python ../shared/orchestrate.py --project tay_bridge --start-phase canon

After it finishes: make the thumbnail in Clickly, write metadata.json, then
    python upload.py --project projects/<project> --privacy unlisted
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parent
PYTHON = sys.executable

PHASES = ["storyboard", "audit", "canon", "stills", "finish", "trueup"]


def die(msg: str):
    print(f"\n!! HALTED: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list, label: str):
    """Run a subprocess, streaming its output. Halt the orchestration if it fails."""
    print(f"\n=== {label} ===")
    print("    " + " ".join(str(c) for c in cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        die(f"{label} exited with code {result.returncode}. Fix it, then re-run "
            f"with --start-phase <this phase>.")


def resolve_project_dir(project_arg: str) -> Path:
    p = Path(project_arg)
    if not p.is_absolute() and len(p.parts) == 1 and Path("projects").is_dir():
        return Path("projects") / p
    return p


def load_shots(path: Path) -> list:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("beats", data.get("shots", []))
    return []


def confirm(question: str) -> bool:
    """Blocking y/n gate. Anything but y/yes is treated as no."""
    try:
        ans = input(f"\n>>> {question} [y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in ("y", "yes")


def main():
    ap = argparse.ArgumentParser(description="Final Hours pipeline orchestrator")
    ap.add_argument("--project", required=True)
    ap.add_argument("--script", default=None, help="narration .txt (default: projects/<p>/<p>_script.txt)")
    ap.add_argument("--canon", default=None, help="canon.json (default: projects/<p>/canon.json)")
    ap.add_argument("--start-phase", choices=PHASES, default="storyboard",
                    help="resume from a later phase (skips earlier ones)")
    ap.add_argument("--model", default="fal-ai/flux-pro/v1.1", help="passed to serve_review reminder only")
    args = ap.parse_args()

    project_dir = resolve_project_dir(args.project)
    name = project_dir.name
    if not project_dir.is_dir():
        die(f"Project dir not found: {project_dir} (create it and place the script + canon.json first)")

    script_path = Path(args.script) if args.script else project_dir / f"{name}_script.txt"
    canon_path = Path(args.canon) if args.canon else project_dir / "canon.json"
    storyboard = project_dir / "storyboard.json"
    audited = project_dir / "storyboard_audited.json"
    beats = Path("beat-scripts") / f"{name}_beats.json"
    stills_dir = project_dir / "stills"
    final_video = project_dir / "final_video.mp4"

    recreation = SHARED / "recreation_pipeline.py"
    audit = SHARED / "audit_storyboard_discipline.py"
    build_canon = SHARED / "build_canon.py"

    start_i = PHASES.index(args.start_phase)

    def active(phase: str) -> bool:
        return PHASES.index(phase) >= start_i

    # ── Phase 0: preflight ────────────────────────────────────────────────
    print("=== preflight ===")
    if active("storyboard"):
        if not script_path.exists() or not script_path.read_text().strip():
            die(f"Script missing or empty: {script_path}")
        print(f"    script:  {script_path} ({len(script_path.read_text().split())} words)")
    if active("canon"):
        if not canon_path.exists():
            die(f"canon.json missing: {canon_path}")
        try:
            cdata = json.loads(canon_path.read_text())
        except Exception as e:
            die(f"canon.json is not valid JSON: {e}")
        if not isinstance(cdata, dict) or not cdata:
            die(f"canon.json must be a non-empty object of token->description: {canon_path}")
        print(f"    canon:   {canon_path} ({len(cdata)} scenes: {list(cdata.keys())})")
    for tool in (recreation, audit, build_canon):
        if not tool.exists():
            die(f"Required tool not found: {tool}")
    print("    preflight OK")

    # ── Phase 1: storyboard ───────────────────────────────────────────────
    if active("storyboard"):
        run([PYTHON, str(recreation), "stills",
             "--script", str(script_path),
             "--project", str(project_dir),
             "--storyboard-only"], "PHASE 1 — storyboard")
        if not storyboard.exists():
            die("storyboard.json was not created.")
        n = len(load_shots(storyboard))
        if n < 5:
            die(f"storyboard.json has only {n} shots — generation likely failed.")
        print(f"    storyboard OK: {n} shots")

    # ── Phase 2: discipline audit ─────────────────────────────────────────
    if active("audit"):
        run([PYTHON, str(audit), "--project", str(project_dir)], "PHASE 2 — discipline audit")
        if not audited.exists():
            die("storyboard_audited.json was not created.")
        print(f"    audit OK -> {audited.name}")

    # ── Phase 3: build canon-aware beats ──────────────────────────────────
    if active("canon"):
        run([PYTHON, str(build_canon),
             "--project", str(project_dir),
             "--canon", str(canon_path)], "PHASE 3 — build canon-aware beats")
        if not beats.exists():
            die(f"beats file was not created: {beats}")
        # GATE 1 — the distribution was printed by build_canon.py above.
        if not confirm("Canon distribution above — does it look right?"):
            print("\nStopped at canon gate. To fix: edit the {token} prefixes in")
            print(f"    {beats}")
            print("then re-run:")
            print(f"    {PYTHON} {recreation.parent.name}/build... or: python ../shared/orchestrate.py "
                  f"--project {name} --start-phase stills")
            print("(Use --start-phase stills to skip straight to generation once the beats are fixed,")
            print(" or --start-phase canon to regenerate the assignment from scratch.)")
            sys.exit(0)

    # ── Phase 4: stills ───────────────────────────────────────────────────
    if active("stills"):
        run([PYTHON, str(recreation), "stills",
             "--beats", str(beats),
             "--project", str(project_dir)], "PHASE 4 — stills generation")
        pngs = sorted(stills_dir.glob("shot_*.png"))
        expected = len(load_shots(beats))
        if len(pngs) < expected:
            die(f"only {len(pngs)}/{expected} stills present — generation incomplete.")
        # Auto silent-reject check. True flux rejects are ~7KB black PNGs; dark
        # night shots can be legitimately small, so only HALT on true blacks
        # (<10KB) and merely REPORT the dark-but-real range.
        true_blacks = [p.name for p in pngs if p.stat().st_size < 10_000]
        dark_fyi = [p.name for p in pngs if 10_000 <= p.stat().st_size < 200_000]
        print(f"    stills OK: {len(pngs)} generated")
        if dark_fyi:
            print(f"    FYI: {len(dark_fyi)} stills are small (<200KB) — likely real dark/night shots, "
                  f"not rejects. Review them in the page.")
        if true_blacks:
            die(f"{len(true_blacks)} stills are <10KB (true safety rejects): {true_blacks[:8]}"
                f"{' ...' if len(true_blacks) > 8 else ''}. "
                f"Restill these (review page Override mode) then re-run --start-phase stills, "
                f"or proceed manually.")

    # ── GATE 2: human review ──────────────────────────────────────────────
    if active("stills"):
        print("\n" + "=" * 60)
        print("STILLS READY FOR REVIEW")
        print("In a separate step, start the review server and open the page:")
        print(f"    python ../shared/serve_review.py --project {project_dir}")
        print("    (ensure your SSH tunnel is up, then open http://localhost:8000)")
        print("Accept / reject / AI-fix / regenerate. Whatever is on disk when you")
        print("continue is what gets animated.")
        print("=" * 60)
        if not confirm("Continue to clips + voiceover + assembly + true-up?"):
            print("\nStopped before finish. Re-run when ready with:")
            print(f"    python ../shared/orchestrate.py --project {name} --start-phase finish")
            sys.exit(0)

    # ── Phase 5: finish (animate + voiceover + whisper align + assemble) ──
    if active("finish"):
        run([PYTHON, str(recreation), "finish",
             "--project", str(project_dir),
             "--no-music"], "PHASE 5 — finish (animate + voiceover + assemble)")
        if not final_video.exists():
            die("final_video.mp4 was not created by finish.")
        print(f"    finish OK -> {final_video.name}")

    # ── Phase 6: true-up (zero-drift re-assemble, $0) ─────────────────────
    if active("trueup"):
        run([PYTHON, str(recreation), "finish",
             "--project", str(project_dir),
             "--no-music", "--assemble-only"], "PHASE 6 — true-up (assemble-only)")
        if not final_video.exists():
            die("final_video.mp4 missing after true-up.")

    # ── Report ────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"DONE — {final_video}")
    try:
        size_mb = final_video.stat().st_size / 1_000_000
        print(f"  size: {size_mb:.1f} MB")
    except OSError:
        pass
    print("\nNext (manual):")
    print("  1. Thumbnail in Clickly (laptop), scp to projects/<p>/thumbnail.png")
    print("  2. Write projects/<p>/metadata.json (title / description / tags)")
    print(f"  3. python upload.py --project projects/{name} --privacy unlisted")
    print("  4. Review the unlisted video, then schedule in Studio.")
    print("=" * 60)


if __name__ == "__main__":
    main()
