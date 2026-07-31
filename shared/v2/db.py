"""shared/v2/db.py -- the spine. Open, create, migrate, and the one
idempotent-pass helper every stage uses. No v1 imports, ever.

Golden principle this file serves: <slug>.db + the media it points at =
the video, deterministically. Every stage is a pass over rows where its
output columns are NULL; this file provides exactly that and nothing more.
"""
from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 2
_HERE = Path(__file__).resolve().parent


def _apply_migrations(con: sqlite3.Connection, from_ver: int) -> None:
    """Apply numbered migrations from_ver+1 .. SCHEMA_VERSION, in order.
    Migration files: migrations/NNNN_*.sql. The lasts-for-years mechanism."""
    mdir = _HERE / "migrations"
    for v in range(from_ver + 1, SCHEMA_VERSION + 1):
        matches = sorted(mdir.glob(f"{v:04d}_*.sql"))
        if not matches:
            raise SystemExit(f"missing migration {v:04d}_*.sql in {mdir}")
        con.executescript(matches[0].read_text(encoding="utf-8"))
        set_meta(con, "schema_version", str(v))
        con.commit()
        print(f"   migrated schema -> v{v} ({matches[0].name})")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(db_path: Path) -> sqlite3.Connection:
    """Open an existing project DB. Refuses unknown schema versions -- the
    'lasts for years' rule: code never touches a DB it doesn't understand."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise SystemExit(f"no database at {db_path} -- run ingest first")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    ver = get_meta(con, "schema_version")
    if ver is None:
        raise SystemExit(f"{db_path} has no schema_version -- not a v2 project DB")
    if int(ver) > SCHEMA_VERSION:
        raise SystemExit(
            f"{db_path} is schema v{ver}; this code speaks v{SCHEMA_VERSION}. "
            f"Update the code before touching this DB.")
    if int(ver) < SCHEMA_VERSION:
        _apply_migrations(con, int(ver))
    return con


def create(db_path: Path, engine_commit: str = "dev") -> sqlite3.Connection:
    """Create a fresh project DB from migrations/0001_init.sql. Refuses to
    overwrite -- the one-way door never re-opens by accident."""
    db_path = Path(db_path)
    if db_path.exists():
        raise SystemExit(f"{db_path} already exists -- the door is one-way. "
                         f"Delete it deliberately if you truly want a re-ingest.")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    sql = (_HERE / "migrations" / "0001_init.sql").read_text(encoding="utf-8")
    con.executescript(sql)
    set_meta(con, "schema_version", "1")
    _apply_migrations(con, 1)
    set_meta(con, "schema_version", str(SCHEMA_VERSION))
    set_meta(con, "created_at", _now())
    set_meta(con, "engine_commit", engine_commit)
    con.commit()
    return con


def get_meta(con: sqlite3.Connection, key: str):
    try:
        row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    except sqlite3.OperationalError:
        return None
    return row["value"] if row else None


def set_meta(con: sqlite3.Connection, key: str, value: str) -> None:
    con.execute("INSERT INTO meta(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


def pending(con: sqlite3.Connection, output_col: str, extra_where: str = "",
            params: tuple = ()) -> list:
    """THE resumability primitive: beats whose `output_col` is still NULL,
    in id order. Crash anywhere, re-run, this picks up the remainder."""
    q = f"SELECT * FROM beats WHERE {output_col} IS NULL"
    if extra_where:
        q += f" AND ({extra_where})"
    q += " ORDER BY id"
    return con.execute(q, params).fetchall()


def mark(con: sqlite3.Connection, beat_id: int, **cols) -> None:
    """Write output columns onto one beat row and stamp updated_at."""
    sets = ", ".join(f"{k}=?" for k in cols)
    vals = list(cols.values()) + [_now(), beat_id]
    con.execute(f"UPDATE beats SET {sets}, updated_at=? WHERE id=?", vals)


def log_generation(con: sqlite3.Connection, stage: str, model: str,
                   prompt: str = None, params_json: str = None,
                   beat_id: int = None, cost: float = None,
                   result_path: str = None, status: str = "done",
                   kept: int = 1, error: str = None) -> int:
    cur = con.execute(
        "INSERT INTO generations(beat_id,stage,model,prompt,params,cost,"
        "result_path,status,kept,error,submitted_at,completed_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (beat_id, stage, model, prompt, params_json, cost, result_path,
         status, kept, error, _now(), _now() if status == "done" else None))
    return cur.lastrowid


def status_counts(con: sqlite3.Connection) -> dict:
    """Per-stage progress straight from the data -- this IS render.py --status."""
    n = con.execute("SELECT COUNT(*) c FROM beats").fetchone()["c"]
    def cnt(col):
        return con.execute(
            f"SELECT COUNT(*) c FROM beats WHERE {col} IS NOT NULL").fetchone()["c"]
    proj = con.execute("SELECT * FROM project WHERE id=1").fetchone()
    return {
        "beats": n,
        "measured": cnt("audio_duration"),
        "stilled": cnt("still_path"),
        "clipped": cnt("clip_path"),
        "voiceover": bool(proj["voiceover_path"]),
        "final_video": bool(proj["final_video_path"]),
        "uploaded": bool(proj["video_id"]),
        "publish_status": proj["publish_status"],
        "canon": con.execute("SELECT COUNT(*) c FROM canon").fetchone()["c"],
        "edl_main": con.execute(
            "SELECT COUNT(*) c FROM edl WHERE edit_name='main'").fetchone()["c"],
        "generations": con.execute(
            "SELECT COUNT(*) c FROM generations").fetchone()["c"],
    }
