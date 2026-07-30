"""shared/v2/render.py -- the thin orchestrator. Runs stages 1-6 in order
against one project DB, or one stage via --stage, or reports via --status.
Makes zero decisions: every real decision already lives in the beats rows.

Resume model: each stage is an idempotent pass over rows where its output
columns are NULL (db.pending). Crash anywhere, re-run the same command.
"""
from __future__ import annotations
import argparse
from pathlib import Path

import db as v2db

STAGES = ["audio", "measure", "visuals", "attach", "music", "upload"]


def _stage_audio(con, project_dir: Path):
    import audio
    audio.run(con, project_dir)


def _stage_measure(con, project_dir: Path):
    import measure
    measure.run(con, project_dir)


def _stage_visuals(con, project_dir: Path):
    import visuals
    visuals.run(con, project_dir)


def _stage_attach(con, project_dir: Path):
    import assemble
    assemble.run(con, project_dir)


def _stage_music(con, project_dir: Path):
    print("   (music rides inside stage attach -- assemble.py builds the bed "
          "and ducks it; nothing to do)")


def _stage_upload(con, project_dir: Path):
    import upload
    upload.run(con, project_dir)


RUNNERS = {"audio": _stage_audio, "measure": _stage_measure,
           "visuals": _stage_visuals, "attach": _stage_attach,
           "music": _stage_music, "upload": _stage_upload}


def show_status(con, slug: str):
    st = v2db.status_counts(con)
    n = st["beats"]
    print(f"[{slug}] beats {n} | canon {st['canon']} | edl:main {st['edl_main']} "
          f"| generations {st['generations']}")
    print(f"  1 audio     : {'DONE' if st['voiceover'] else 'pending'}")
    print(f"  2 measure   : {st['measured']}/{n}")
    print(f"  3 visuals   : stills {st['stilled']}/{n}  clips {st['clipped']}/{n}")
    print(f"  4-5 attach+music : {'DONE' if st['final_video'] else 'pending'}")
    print(f"  6 upload    : {'DONE video_id set' if st['uploaded'] else 'pending'}"
          f"  ({st['publish_status']})")


def main():
    ap = argparse.ArgumentParser(description="v2 renderer: DB in, video out")
    ap.add_argument("--project", required=True,
                    help="project dir containing <slug>.db")
    ap.add_argument("--stage", choices=STAGES,
                    help="run one stage only (default: all, in order)")
    ap.add_argument("--status", action="store_true",
                    help="print per-stage progress and exit")
    a = ap.parse_args()

    pdir = Path(a.project).resolve()
    slug = pdir.name
    db_path = pdir / f"{slug}.db"
    con = v2db.connect(db_path)

    if a.status:
        show_status(con, slug)
        return

    stages = [a.stage] if a.stage else STAGES
    for s in stages:
        print(f"== stage: {s} ==")
        RUNNERS[s](con, pdir)
        con.commit()
    show_status(con, slug)


if __name__ == "__main__":
    main()
