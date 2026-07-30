-- ============================================================================
-- v2.0 PIPELINE SCHEMA -- DRAFT 1 (30 Jul 2026)
-- ============================================================================
-- This file is CODE, not state. It lives in the repo (shared/v2/), travels
-- laptop -> GitHub -> box, and is the single schema definition for the whole
-- operation. The .db files it creates are STATE: one per project, living in
-- <channel>/projects/<slug>/<slug>.db, gitignored, next to the media.
--
-- GOLDEN PRINCIPLE (the test every column answers to): given this database
-- plus the media files it points at, the final video must be
-- deterministically reconstructible with no other input.
--
-- DESIGN RULES applied throughout:
--   * one row per beat, accumulating state; no parallel derived files
--   * beats = current state (the single truth); generations = append-only
--     history (never a second copy of state)
--   * anticipate in the schema, never in the code: future capabilities are
--     nullable columns and new legal values, inert until used
--   * no CHECK-constraint enums on extensible fields (method, model, stage):
--     a new capability must never require a schema migration just to name
--     itself -- validation lives in the code registry
--   * schema changes only ever happen by numbered migration (migrations/NNNN_*.sql),
--     stamped in meta.schema_version; code refuses versions it doesn't know
-- ============================================================================

PRAGMA journal_mode = WAL;          -- safe concurrent read during long stages
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- meta: schema version + engine provenance. One row per key.
-- ----------------------------------------------------------------------------
CREATE TABLE meta (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);
-- required keys at init: schema_version, created_at, engine_commit

-- ----------------------------------------------------------------------------
-- project: exactly one row. The video-level facts.
-- ----------------------------------------------------------------------------
CREATE TABLE project (
    id              INTEGER PRIMARY KEY CHECK (id = 1),   -- enforce single row
    slug            TEXT NOT NULL,
    channel         TEXT NOT NULL,                         -- e.g. sacred_dawn
    title           TEXT NOT NULL,
    description     TEXT,
    tags            TEXT,                                  -- comma list, as shipped to upload
    voice           TEXT,                                  -- default TTS voice (per-beat override on beats.voice)
    style_contract  TEXT,                                  -- ONE locked paragraph prepended to every image/video
                                                           -- prompt. The register ("bright blockbuster photoreal")
                                                           -- formalized as measured ingredients, not vibes.
    image_model     TEXT,                                  -- default still model (per-beat override available)
    width           INTEGER NOT NULL DEFAULT 1280,
    height          INTEGER NOT NULL DEFAULT 720,
    video_duration  TEXT NOT NULL DEFAULT '5',             -- kling native seconds ('5'|'10') -- the fal knob
    video_model     TEXT,                                  -- default motion model
    thumb_title     TEXT,
    thumb_subtitle  TEXT,
    thumb_subject   TEXT,
    thumbnail_path  TEXT,                                  -- produced asset
    music_path      TEXT,
    voiceover_path  TEXT,                                  -- stage-1 output (full narration mp3)
    sections_json   TEXT,                                  -- block_id -> chapter title (upload chapters
                                                           -- are rebuilt from this + beat timestamps)                                  -- chosen/curated track actually used
    final_video_path TEXT,                                 -- the shipped master
    video_id        TEXT,                                  -- platform id after upload
    publish_status  TEXT NOT NULL DEFAULT 'draft',         -- draft|rendering|rendered|uploaded|published
    published_at    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ----------------------------------------------------------------------------
-- beats: one row per beat. THE data view of the final video.
-- Columns in pipeline-stage layers; each stage is an idempotent pass over
-- rows where its output columns are NULL. Resumability IS this table.
-- ----------------------------------------------------------------------------
CREATE TABLE beats (
    id              INTEGER PRIMARY KEY,                   -- global beat order, 1..N
    block_id        TEXT NOT NULL,                         -- act/section id (plain value, never re-parsed
                                                           -- from rendered headings -- the ROMAN-ceiling and
                                                           -- COLD OPEN string-match bugs die here)
    clip_index      INTEGER NOT NULL,                      -- position within block

    -- authored layer (from CSV at intake) ------------------------------------
    narration       TEXT NOT NULL,
    phenomenon      TEXT NOT NULL,                         -- {token} framing, positive statements only
    subject         TEXT,
    weight          TEXT,                                  -- hero|support
    topic_class     TEXT,                                  -- universal|lore
    scale           INTEGER,
    move            TEXT,                                  -- push|pull|crane|settle|static (floor camera)
    method          TEXT NOT NULL DEFAULT 'floor',         -- HOW this beat becomes a clip. Today: floor|kling.
                                                           -- Future: lipsync|... -- a new generator function and
                                                           -- a new value here, zero pipeline changes. (v1 "air",
                                                           -- generalized.)
    motion_prompt   TEXT,                                  -- video-model motion text (kling & successors).
                                                           -- Doctrine: named camera move + in-scene event +
                                                           -- no frozen figures.
    voice           TEXT,                                  -- per-beat override; NULL = project.voice
    image_model     TEXT,                                  -- per-beat override; NULL = project default
    video_model     TEXT,                                  -- per-beat override; NULL = project default

    -- measured layer (stage 2: whisper alignment) ----------------------------
    audio_start     REAL,                                  -- seconds into full voiceover
    audio_duration  REAL,                                  -- real spoken length; stills/clips are generated
                                                           -- AT this length, never stretched to it
    word_timestamps TEXT,                                  -- JSON [{w,s,e},...] -- whisper computes this anyway;
                                                           -- keeping it makes subtitles and lipsync a generator
                                                           -- away instead of a re-alignment away

    -- produced layer (stages 3-4) --------------------------------------------
    still_path      TEXT,
    clip_path       TEXT,
    clip_audio      TEXT,                                  -- NULL|keep|mute|duck -- video models emit native
                                                           -- audio now; per-clip decision at assembly
    start_frame_source INTEGER REFERENCES beats(id),       -- chain shots: seed this beat's generation with
                                                           -- another beat's last frame (continuity without
                                                           -- reloading reference sheets)
    end_frame_path  TEXT,                                  -- extracted last frame, available as a seed
    resolution      TEXT,                                  -- explore low / master once ladder; NULL = project policy

    status          TEXT NOT NULL DEFAULT 'authored',      -- authored|measured|stilled|clipped|failed
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_beats_status ON beats(status);

-- ----------------------------------------------------------------------------
-- canon: PROJECT-LEVEL SNAPSHOT of the tokens this video uses.
-- The living, refined library lives at channel level; intake copies the used
-- entries here with provenance, so this DB alone satisfies the golden
-- principle. Reference images are the consistency mechanism (per-character
-- sheets: front / three-quarter / profile as SEPARATE crops -- grids read as
-- different people to video models; separate sheet per wardrobe/state).
-- ----------------------------------------------------------------------------
CREATE TABLE canon (
    token           TEXT PRIMARY KEY,                      -- letters + underscores ONLY (Law 20)
    kind            TEXT,                                  -- character|place|object|style
    description     TEXT NOT NULL,                         -- the text expansion (v1-compatible)
    reference_paths TEXT,                                  -- JSON list of image paths (nullable: text-only
                                                           -- canon still fully supported)
    state_variant   TEXT,                                  -- e.g. 'robes' vs 'armor' -- one row per state
    source_generation INTEGER,                             -- generations.id that produced the reference
                                                           -- image(s): canon itself is reconstructible
    channel_scope   TEXT,                                  -- channel library key this was snapshotted from
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ----------------------------------------------------------------------------
-- generations: append-only log of EVERY model call. Never state -- history.
-- This is BOM-as-measurement (budget gates become queries), retry/multi-
-- candidate support, provenance for the golden principle, and the session
-- memory that makes production N+1 start from what N learned.
-- Fleet-ready by construction: an agent operator later reads "what is
-- pending/running/failed" straight from here -- the database IS the job queue.
-- ----------------------------------------------------------------------------
CREATE TABLE generations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    beat_id         INTEGER REFERENCES beats(id),          -- NULL for project-level gens (music, thumbnail)
    stage           TEXT NOT NULL,                         -- audio|still|clip|music|thumb|upscale|...
    model           TEXT NOT NULL,
    prompt          TEXT,                                  -- the AS-SENT prompt, canon fully expanded.
                                                           -- (kills the v1 recompile-staleness bug class:
                                                           -- what was sent is recorded, not implied)
    params          TEXT,                                  -- JSON of everything else sent
    cost            REAL,
    result_path     TEXT,
    status          TEXT NOT NULL DEFAULT 'submitted',     -- submitted|running|done|failed|killed
    kept            INTEGER NOT NULL DEFAULT 0,            -- 1 = this candidate won and is live in beats.*_path
    job_id          TEXT,                                  -- provider job handle (polling)
    attempts        INTEGER NOT NULL DEFAULT 1,
    error           TEXT,
    submitted_at    TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT
);
CREATE INDEX idx_gen_beat   ON generations(beat_id);
CREATE INDEX idx_gen_status ON generations(status);

-- ----------------------------------------------------------------------------
-- edl: assembly as data. The main video is simply the default edit (all
-- beats, in order) -- v2.0 ships generating that default automatically, and
-- assembly code reads ONLY this table, never assumes "all beats". A shorts
-- cut, a trailer, a recut = more rows, not more tools.
-- ----------------------------------------------------------------------------
CREATE TABLE edl (
    edit_name       TEXT NOT NULL DEFAULT 'main',
    position        INTEGER NOT NULL,
    beat_id         INTEGER NOT NULL REFERENCES beats(id),
    in_trim         REAL NOT NULL DEFAULT 0.0,             -- seconds trimmed from clip head
    out_trim        REAL NOT NULL DEFAULT 0.0,             -- seconds trimmed from clip tail
    audio_flag      TEXT,                                  -- NULL=inherit beats.clip_audio | keep|mute|duck
    aspect          TEXT,                                  -- NULL=project native | e.g. '9:16' for shorts
    PRIMARY KEY (edit_name, position)
);

-- ============================================================================
-- STAGE MAP (the six steps, as passes over this schema)
--   1 audio    : project.voice + beats.narration        -> voiceover.mp3 (gen logged)
--   2 measure  : voiceover + narration                  -> beats.audio_start/audio_duration/word_timestamps
--   3 stills+clips (method registry: floor|kling|...)   -> beats.still_path/clip_path, AT audio_duration
--   4 attach   : near-concat -- clips are already the right length by construction
--   5 music    : project.music_path + sidechain duck    -> mixed master
--   6 upload   : project.* metadata                     -> project.video_id, publish_status
-- Every stage: SELECT rows WHERE its output IS NULL; crash-safe resume free.
-- ============================================================================
