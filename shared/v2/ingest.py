"""shared/v2/ingest.py -- the one-way door. A validated LEGO CSV set goes in;
<slug>.db comes out; the CSV's job is done. Authoring edits happen before this
door or via deliberate re-ingest (delete the .db first) -- never by hand-editing
the database.

Reads (from --src, the authored set intake.py validated):
  master.csv       one row per beat (block_id, clip_index, narration, phenomenon,
                   weight, air, topic_class, subject, scale, move, motion)
  canon.json       token -> expansion text (project-level snapshot at ingest)
  chop-config.json optional: kling_count + kling_motion drive the method column
  sections.json    block_id -> chapter title (stored on project for upload chapters)
  desc.txt         upload description
  thumbsubject.txt thumbnail subject text

Method column at ingest (v2 decides at the door, not at render):
  first `kling_count` beats -> method='kling', motion_prompt from kling_motion[i]
  (positional, same pairing csv2script used); everything else -> method='floor'.
"""
from __future__ import annotations
import argparse
import csv as csvmod
import json
from pathlib import Path

import db as v2db


def _channel_defaults(db_path: Path) -> dict:
    """Read the channel's EXISTING channel.json once, at the door (one config
    home, per Peter's ruling 31 Jul). Channel dir = db_path.parent.parent
    (the <channel>/projects/<slug> layout). Missing file -> empty defaults."""
    out = {}
    project_dir = db_path.parent
    cj = None
    for cand in (project_dir.parent.parent, project_dir.parent, project_dir):
        if (cand / "channel.json").is_file():
            cj = cand / "channel.json"
            break
    if cj:
        try:
            data = json.loads(cj.read_text(encoding="utf-8"))
            if data.get("voice_id"):
                out["voice"] = str(data["voice_id"])
            if data.get("speaking_rate") is not None:
                out["speaking_rate"] = float(data["speaking_rate"])
            up = data.get("upload") or {}
            if up.get("category_id") is not None:
                out["category_id"] = str(up["category_id"])
            elif data.get("category_id") is not None:
                out["category_id"] = str(data["category_id"])
        except Exception as e:
            print(f"WARNING: {cj} unreadable ({e}) -- proceeding on defaults")
    return out


def ingest(src: Path, db_path: Path, slug: str, channel: str, title: str,
           tags: str = "", voice: str = None, thumb_title: str = "",
           thumb_subtitle: str = "", engine_commit: str = "dev") -> None:
    src = Path(src)
    db_path = Path(db_path)

    if db_path.exists():
        con = v2db.connect(db_path)
        n = con.execute("SELECT COUNT(*) c FROM beats").fetchone()["c"]
        print(f"already ingested: {db_path} ({n} beats) -- no-op. "
              f"Delete the .db deliberately to re-ingest.")
        return

    rows = list(csvmod.DictReader(open(src / "master.csv", encoding="ascii")))
    if not rows:
        raise SystemExit(f"{src}/master.csv has no rows")
    canon = json.loads((src / "canon.json").read_text(encoding="ascii"))

    ch = _channel_defaults(db_path)
    voice = voice or ch.get("voice", "Elliot")
    speaking_rate = ch.get("speaking_rate", 1.0)
    category_id = ch.get("category_id")

    kling_count, kling_motion = 0, []
    cfg_path = src / "chop-config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="ascii"))
        kling_count = int(cfg.get("kling_count", 0))
        kling_motion = list(cfg.get("kling_motion", []))

    # Placement-by-value (Law 28e): an authored `kling` column in the CSV
    # OVERRIDES front-N entirely. Truthy values: 1/x/kling/yes. Motion for a
    # placed beat comes from that row's own `motion` column (authored per
    # beat), never the positional kling_motion list.
    placement_mode = "kling" in (rows[0].keys() if rows else [])
    placed = set()
    if placement_mode:
        for i, r in enumerate(rows):
            if str(r.get("kling", "")).strip().lower() in ("1", "x", "kling", "yes", "true"):
                placed.add(i)
        if placed:
            print(f"   kling placement column: {len(placed)} beats "
                  f"(front-N kling_count IGNORED)")
        else:
            placement_mode = False

    sections = {}
    if (src / "sections.json").exists():
        sections = json.loads((src / "sections.json").read_text(encoding="ascii"))
    description = ((src / "desc.txt").read_text(encoding="ascii")
                   if (src / "desc.txt").exists() else "")
    thumb_subject = ((src / "thumbsubject.txt").read_text(encoding="ascii").strip()
                     if (src / "thumbsubject.txt").exists() else "")

    con = v2db.create(db_path, engine_commit=engine_commit)
    try:
        con.execute(
            "INSERT INTO project(id,slug,channel,title,description,tags,voice,"
            "speaking_rate,category_id,"
            "thumb_title,thumb_subtitle,thumb_subject,sections_json) "
            "VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?)",
            (slug, channel, title, description, tags, voice,
             speaking_rate, category_id,
             thumb_title, thumb_subtitle, thumb_subject,
             json.dumps(sections, ensure_ascii=True)))

        for i, r in enumerate(rows):
            if placement_mode:
                is_kling = i in placed
                motion = (r.get("motion") or None) if is_kling else (r.get("motion") or None)
            else:
                is_kling = i < kling_count
                motion = (kling_motion[i] if is_kling and i < len(kling_motion)
                          else (r.get("motion") or None))
            method = "kling" if is_kling else "floor"
            con.execute(
                "INSERT INTO beats(id,block_id,clip_index,narration,phenomenon,"
                "subject,weight,topic_class,scale,move,method,motion_prompt) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (i + 1, r["block_id"], int(r["clip_index"]), r["narration"],
                 r["phenomenon"], r.get("subject") or None,
                 r.get("weight") or None, r.get("topic_class") or None,
                 int(r["scale"]) if r.get("scale") else None,
                 r.get("move") or None, method, motion))

        for token, desc in canon.items():
            con.execute(
                "INSERT INTO canon(token,description,channel_scope) VALUES(?,?,?)",
                (token, desc, channel))

        for i in range(len(rows)):
            con.execute(
                "INSERT INTO edl(edit_name,position,beat_id) VALUES('main',?,?)",
                (i, i + 1))

        con.commit()
    except Exception:
        con.close()
        db_path.unlink(missing_ok=True)
        raise
    st = v2db.status_counts(con)
    kn = con.execute("SELECT COUNT(*) c FROM beats WHERE method='kling'").fetchone()["c"]
    kling_count = kn
    print(f"   voice={voice} rate={speaking_rate}"
          + (f" category={category_id}" if category_id else ""))
    print(f"ingested {slug}: {st['beats']} beats "
          f"({kling_count} kling, {st['beats']-kling_count} floor), "
          f"{st['canon']} canon tokens, edl 'main' {st['edl_main']} rows -> {db_path}")


def main():
    ap = argparse.ArgumentParser(description="v2 one-way door: CSV set -> project.db")
    ap.add_argument("--src", required=True, help="authored set dir (post intake GREEN)")
    ap.add_argument("--db", required=True, help="output <slug>.db path")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--channel", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--voice", default=None, help="override channel.json voice_id")
    ap.add_argument("--thumb-title", default="")
    ap.add_argument("--thumb-subtitle", default="")
    a = ap.parse_args()
    ingest(Path(a.src), Path(a.db), a.slug, a.channel, a.title, a.tags,
           a.voice, a.thumb_title, a.thumb_subtitle)


if __name__ == "__main__":
    main()
