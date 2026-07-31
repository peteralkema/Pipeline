# v2-PLUMBING.md — THE MACHINE, COMPLETE
### Status: BUILT + PRODUCTION-PROVEN 31 Jul 2026 (Thomas teaser: CSV → private upload in Studio, first real run).
### Purpose: a session that reads THIS document understands the entire v2 machine without opening a single code file.

---

## 0. THE ONE-PARAGRAPH VERSION

v2 is nine files in `shared/v2/` that turn an authored CSV set into an uploaded
video through six ordered stages, with a SQLite database (`<slug>.db`) as the only
truth between them. Measurement precedes generation, so every visual asset is born
at its exact required length — which deletes time-stretching, duration-conform
apparatus, and three drifting file formats *by construction*. Every stage is an
idempotent pass over rows whose output columns are NULL: crash anywhere, re-run the
same command, it continues. The golden principle, enforced from the schema up:
**`<slug>.db` + the media files it points at = the video, deterministically
reconstructible, with no other input.**

## 1. THE TWO INSTRUMENTS AND THE DOOR (categorical statement)

The system has exactly two instruments, one per side of a one-way door:

**The CSV is the AUTHORING instrument (LEGO).** One row per beat; every creative
decision is a column (narration, phenomenon/{token}, subject, scale, move, method
routing via kling_count, weight, topic_class). It is human-readable, diffable,
gate-checkable (`audit_script.py`, `intake.py`), and written by taste — river-first
prose, chopped second. Everything upstream of the door is judgment made legible.

**The `.db` is the MACHINE instrument.** One row per beat; every production fact is
a column (audio_start, audio_duration, word_timestamps, still_path, clip_path,
status), plus project facts (voiceover_path, final_video_path, video_id), a canon
snapshot, an append-only `generations` ledger of every model call (as-sent prompt,
cost, result, kept/refused), and an `edl` table that makes assembly itself data.
Everything downstream of the door is fact made queryable.

**The door is `ingest.py --ingest`: the ONLY place they touch.** A validated CSV set
goes in; `<slug>.db` comes out; the CSV's job ends. The door is one-way by
mechanism, not convention: re-ingest is a polite no-op, `db.create()` refuses to
overwrite, `db.connect()` refuses schema versions it doesn't know. Authoring edits
happen BEFORE the door or via deliberate re-ingest (delete the .db first) — never
by hand-editing the database. Symmetry worth stating: LEGO gave authoring its
instrument; the .db gives the machine its instrument; same philosophy, one per side.

Two practical corollaries, both proven:
- **Method is decided AT THE DOOR** (first `kling_count` beats → method='kling'
  with positional motion-prompt pairing from chop-config.json; rest → 'floor'),
  not at render. Render makes zero decisions.
- **Pre-filled columns are the extension mechanism.** A beat whose `still_path` is
  already set is invisible to the stills pass — hand-made visuals are not a mode or
  a flag, they are pre-filled columns (proven in the e2e: pass A generated zero
  because three hand-made stills were pre-marked). This is the entire technical
  basis of the fal.ai taste-input workflow (see ELIJAH-TASTE-INPUT.md).

## 2. THE SIX STAGES (strict order, and why the order IS the design)

```
audio → measure → visuals → attach → music → upload
```

1. **audio** — one continuous voiceover for the whole script (voice + rate from the
   project row). VOICE IS THE SPINE.
2. **measure** — Whisper + sequence alignment writes `audio_start`,
   `audio_duration`, `word_timestamps` onto every beat. Truth about time now exists
   BEFORE any image is generated.
3. **visuals** — stills + clips, each clip born at exactly `audio_duration`.
4. **attach** — pure concat of the `main` EDL (clips already fit; nothing to
   conform).
5. **music** — bed picked/crossfaded/looped from `<project>/music/`, sidechain-
   ducked under the voice (rides inside stage 4's file; the stage exists as a slot).
6. **upload** — the DB is the header; video_id written back.

Because measurement precedes generation, v1's whole duration-fitting apparatus
(stretch, KB_TAIL-in-assemble, durations.json, conform) has nothing to do and
therefore does not exist. **THE NEVER-STRETCH LAW (Peter's ruling B, 31 Jul,
permanent):** motion plays as rendered, always; length is met by Ken Burns WITHIN
the beat (native clip in full, then the last frame continues under a KB move —
"motion hands to motion"). The v1 slow-fill branch (setpts variable time remapping —
which gave every beat a DIFFERENT slowdown factor and broke the film's motion
grammar) is DELETED, not deprecated: `setpts` appears zero times in v2. Longer
native kling durations (fal's 10s/15s) are a data knob (`project.video_duration`)
that simply shrinks the tail — ruling B makes them purely additive.

## 3. DEPENDENCY MAP

```
                 CSV set  (master.csv + canon.json + chop-config.json
                           + sections.json + desc.txt + thumbsubject.txt)
                    │
                    ▼
             ingest.py  --ingest        ← THE ONE-WAY DOOR
                    │
                    ▼
               <slug>.db                ← SINGLE SOURCE OF TRUTH
                    │
   ┌────────────────┴──────────────────────────────────────────┐
   │   render.py  (thin orchestrator; --status; --stage)       │
   │   db.py      (the spine under every stage: pending/mark/  │
   │               log_generation/status_counts)               │
   │                                                            │
   │   1 audio.py      → voiceover.mp3, project.voiceover_path │
   │   2 measure.py    → audio_start/duration/word_timestamps  │
   │       └ align_with_whisper.py  (carried VERBATIM)         │
   │   3 visuals.py    → still_path, clip_path (born at length)│
   │   4+5 assemble.py → final_video.mp4 (concat+duck), status │
   │   6 upload.py     → video_id, publish_status, Studio link │
   └────────────────────────────────────────────────────────────┘
                    │
                    ▼
            Video in Studio (private; schedule/publish is Peter's)
```

Every stage both reads and writes the DB (the arrows show sequence; data always
round-trips through `<slug>.db` — no clip-passing between stages). The dashed-box
boundary is the resumability boundary.

## 4. THE NINE FILES — FULL TEARDOWN (read this instead of the code)

**`schema.sql` + `migrations/0001_init.sql`** (identical at v1 of the schema).
Six tables. `meta` (schema_version, created_at, engine_commit). `project` (single
row, `CHECK(id=1)`): slug, channel, title/description/tags, voice,
style_contract (the register as ONE locked paragraph — formalization is backlog #7),
image_model/video_model (endpoint choice as DATA), width/height (default 1280×720),
video_duration ('5'|'10' — the fal knob), thumb_* fields, sections_json (block→
chapter title, for upload chapters), voiceover_path, music_path, thumbnail_path,
final_video_path, video_id, publish_status, published_at. `beats` (one row per
beat, THE data view of the video): authored layer (block_id, clip_index, narration,
phenomenon, subject, weight, topic_class, scale, move, method, motion_prompt,
voice-per-beat override) + measured layer (audio_start, audio_duration,
word_timestamps JSON) + produced layer (still_path, clip_path, status) +
future-proof inert columns (start_frame_source / end_frame_path for chain shots,
resolution). `canon` (project-level SNAPSHOT at ingest: token PK [letters+underscores
only, Law 20], kind, description [v1-compatible text expansion],
**reference_paths** [JSON list — the Elijah seam, present and unused until refs
land], provenance). `generations` (append-only: beat_id?, stage, model, prompt
AS-SENT, params JSON, cost, result_path, status done|refused, kept, error,
timestamps — BOM becomes a query; the learning flywheel formalized; also the future
job queue for fleet operation, backlog #10). `edl` (edit_name, position, beat_id,
trims — assembly as data; 'main' = all beats in order; shorts/trailer = more rows,
backlog #4). Design rule that governs ALL of it: **anticipate in the schema, never
in the code** — capability arrives as columns + numbered migrations; no CHECK-enums
that a new method value would have to fight.

**`db.py` (~125 lines) — the spine.** `create(path)` runs migration 0001, stamps
meta, REFUSES to overwrite. `connect(path)` REFUSES missing DBs and unknown schema
versions (the lasts-for-years rule: code never touches a DB it doesn't understand).
`pending(con, output_col, extra_where)` — THE resumability primitive: beats where
the stage's output column IS NULL, in id order. `mark(beat_id, **cols)` writes
outputs + updated_at. `log_generation(...)` appends the ledger.
`status_counts()` computes per-stage progress straight from the data — this IS
Mission Control's replacement.

**`ingest.py` (~125 lines) — the door.** Reads the six-file src set. Writes the
project row (title/tags/voice from args; description/sections/thumb-subject from
files), all beats (method decided here; kling motion prompts paired positionally,
exactly csv2script's pairing), the canon snapshot, the default `main` EDL. On any
failure it deletes the half-born DB (no half-states). If the DB exists: prints the
beat count and exits 0 — the no-op that makes the door one-way. KNOWN PENDING (fix
queue): voice default should be 'Elliot' (case-exact, Law 26) and a speaking_rate
should be read (channel currently 0.97; v2 ran 1.0 on the teaser).

**`render.py` (~95 lines) — the thin orchestrator.** `--status` prints truth from
`status_counts`. `--stage X` runs one stage; bare run walks all six in order. It
makes ZERO decisions — every decision already lives in rows. Stage functions are a
registry (`RUNNERS`); an unbuilt capability fails loudly BY NAME (proven behavior:
the e2e's downstream stages refused cleanly, `--status` never lied).

**`audio.py` (~110 lines) — stage 1.** `_chunk_text` (sentence-boundary chunking
under 1800 chars) and `_synthesize_chunk` (Inworld JSON+base64 API: voiceId,
modelId inworld-tts-2, audioConfig MP3 + speakingRate, deliveryMode EXPRESSIVE)
carried VERBATIM from recreation_pipeline.py; multi-chunk concat via moviepy,
verbatim pattern. THE one deliberate change: voice comes from the project row —
the channel.json walk is gone; the DB is the truth. Idempotent (project.voiceover_
path set + file exists → no-op). Logs one generation row carrying the FULL as-sent
script (golden principle). Requires INWORLD_API_KEY.

**`align_with_whisper.py` (323 lines) — CARRIED VERBATIM, zero edits.** The
Troy-drift fix (8 Jun): storyboard-token→whisper-token alignment via difflib
SequenceMatcher (autojunk disabled), matched tokens take exact Whisper start times,
unmatched tokens (numbers→digits, dropped fillers) interpolate between anchors so
errors stay LOCAL instead of accumulating (Troy: +46s drift by beat 141 under the
old positional cursor). Exposes three pure functions v2 imports: `normalize`,
`words_in`, `build_sb_time_map`. Its own CLI still works for v1 projects.

**`measure.py` (~160 lines) — stage 2, the wrapper.** Runs the box's proven whisper
CLI (`whisper voiceover.mp3 --model small --output_format json --output_dir <dir>
--word_timestamps True`) if voiceover.json is absent; flattens Whisper output
faithfully to v1's main(); builds the beat token stream; calls the verbatim core;
applies the same per-beat semantics (first beat pinned to 0.0, non-decreasing
starts, duration = next start − start, 0.3s floor with loud counting); computes
coverage (the REAL health metric — <85% warns loudly) — and adds the one thing v1
computed and threw away: **per-word `{w,s,e}` timestamps stored per beat** as
`word_timestamps` JSON (subtitles + lipsync later, backlog #5, zero extra cost).
Idempotent via pending(audio_duration); logs coverage/word-count/floors as a
generation row. PRODUCTION RECEIPT: 98.5% coverage on the teaser's real transcript.
KNOWN PENDING: the voiceover guard must use `is_file()` (Path('') resolved to '.'
and whisper tried to transcribe a directory — teaser catch).

**`visuals.py` (~320 lines) — stage 3, the biggest by design.** Two idempotent
passes. PASS A (stills): pending(still_path) → expand the phenomenon
(`{token} rest` → canon description + rest, + project.style_contract) → `_gen_still`
(flux path verbatim: safety_tolerance "5" [without it flux returns silent black
PNGs], negative_prompt, image_size from project width/height; nano-banana-2 family
handled with aspect_ratio/resolution args; refusal → logged `refused`, still_path
stays NULL for a reworded re-run — the pass model makes restilling free). PASS B
(clips): pending(clip_path WHERE still_path set) → METHOD REGISTRY dispatch:
**floor** → `_kb_still` (ken_burns_still VERBATIM: doctrine moves push/pull/crane/
settle/static; the 29 Jul duration-scaled push/pull fix; the 4×-upscale
anti-judder craft; true-static bypasses zoompan) at exactly audio_duration with the
beat's move. **kling** → `_animate` (verbatim: fal storage upload, endpoint from
project.video_model, duration from project.video_duration, content-policy detection)
→ `_fit_to_duration` (make_video_segment's LAW-COMPLIANT branches carried verbatim:
trim if long; **kb-tail** if ≥0.5s short — native part re-encoded, last frame via
`-sseof -0.25`, tail zoompan on a 2× upscale, concat; clone-pad if <0.5s; the
slow-fill branch DELETED). Kling content-policy refusal falls back to FULL-LENGTH
KB (never v1's held frame — a refusal must not demote a beat below the floor every
other beat gets). Guards: refuses to run before measure ("clips are born at their
measured length" — the whole thesis in one error); refuses ref-carrying tokens BY
NAME until the ref path is wired (see Elijah doc). Every call logged with cost
(still $0.08, kling $0.42) and the FIT LABEL in params — "how often does the tail
fire" is now a query. PRODUCTION RECEIPT: all five moves + all three fit branches
proven at exact duration; teaser rendered 19 floor + 2 kling incl. a long kb-tail.

**`assemble.py` (~185 lines) — stages 4+5.** Guards: all clip_paths present; then
pure concat of the `main` EDL (clips already exact — concat demuxer, re-encode,
FPS-pinned, verbatim from assemble_episode). Music: `<project>/music/` (curated by
rsync — "curate the folder so random is safe"): random-pick N (3), acrossfade the
joins, loop to cover the voice — verbatim `_build_music_bed`. Mux: the sidechain
duck VERBATIM (VOICE 1.15 / MUSIC 0.11; sidechaincompress threshold 0.03, ratio 8,
attack 15, release 350; output PINNED to voice duration — VOICE WINS). No music →
voice-only mux, valid. Writes final_video_path + publish_status='rendered', logs
a generation row with final/voice durations. What v2 DELETED from the donor by
construction: durations.json, the index reverse-map, placeholders, and the entire
make_video_segment fitting apparatus (it lives in visuals.py now, where duration
truth exists).

**`upload.py` (~235 lines) — stage 6.** OAuth (refresh-in-place; headless-dead-token
message tells you the exact laptop re-auth + scp), resumable insert, thumbnail set,
captions insert — ALL VERBATIM from upload_episode.py. What changed: the DB IS the
header (title/description/tags/channel from the project row; v1's beats_full.json
header is gone), and the outcome is WRITTEN BACK (video_id, publish_status=
'uploaded', published_at) so `--status` answers "is it up?" from data. Credentials
stay ON DISK, never in the DB — token.json/client_secret.json resolve by walking up
from the project dir (v1 channel layout `<channel>/projects/<slug>` resolves
naturally), `--creds-dir` overrides. Defaults PRIVATE; `--publish-at` (RFC3339 UTC,
forces private) for scheduling; `--dry-run` prints the exact snippet with no API
call. v1's parts>1 batch-exit-gate is gone by construction: a v2 project is one
video; cuts are EDL rows.

## 5. HOW A PROJECT ACTUALLY RUNS (the whole ceremony)

```
BOX (once per session): cd ~/Pipeline && git pull --no-edit
  && source ~/venvs/pipeline/bin/activate && set -a && source .env && set +a

INGEST:  cd shared/v2 && python ingest.py --src <path>/<slug>-src
           --db <channel>/projects/<slug>/<slug>.db
           --slug <slug> --channel <channel> --title "..." --tags "..."
MUSIC:   mkdir -p <project>/music && cp <channel>/music/*.mp3 <project>/music/
RUN:     python render.py --project <channel>/projects/<slug>          (all six)
   or:   python render.py --project ... --stage audio                  (one at a time)
CHECK:   python render.py --project ... --status                       (anytime)
UPLOAD SCHEDULING: python upload.py --project ... --publish-at 2026-08-01T23:00:00Z
```
Long runs go in tmux. Re-running ANY command after ANY crash is always safe — that
is not a feature, it is the data model.

## 6. WHAT DIED, AND THE ATTIC RULE (the decommission record)

v1 is FEATURE-FROZEN from 31 Jul: bugfix-only, via patch_*.py. Nine engine files
die when their replacement has shipped a real video (csv2script, parse_script,
run_batch, orchestrate, modea legs, draft_moves + the inbox format). Two organ
donors, both fully harvested 31 Jul: recreation_pipeline.py and assemble_episode.py.
select_thumbnail_still: kill now. **Formats die by construction, not deletion** —
.md pair, beats_full.json, storyboard.json, durations.json, render_policy.json,
inboxes, the exists-guard/-src dance: no v2 consumer exists; the teaser shipped
with none of them. **ATTIC RULE (all three required, per file): replacement shipped
a real video + zero grep refs from live code + no active channel needs it.**
Migration order: Sacred Dawn (piloted) → Scripture → Synthetic → parked channels
only on reactivation. Hard rules: shared/v2/ imports NOTHING from v1; no mode flags
anywhere; every schema change is a numbered migration.

## 7. THE BACKLOG (banked 30 Jul, unchanged, each = migration + code, with triggers)

v2.0 = parity with corrected v1 (SHIPPED). Deferred, ranked:
1. **Shot planner (beats → n shots).** Crops/moves over one still as multiple
   shots; cut boundaries snapped to word gaps via word_timestamps (already stored);
   per-block pacing config. Adds `shots` table; EDL orders shots. TRIGGER: first
   project where the long-hold register limits watch-through, or a cold open wants
   faster cutting than one-asset-per-beat allows. Highest-value deferred item.
2. **Scenes layer.** scene_id on beats; per-scene pacing; coverage POOLING; slack
   absorbed at scene boundaries; chain shots never cross scenes; tableau law
   relocates to the scene list. TRIGGER: shot planner shipped + first project
   wanting within-scene dwell on pooled coverage.
3. **Chain shots.** start_frame_source/end_frame_path already in schema; generator
   support + doctrine. TRIGGER: first continuity-driven sequence. (The kb-tail's
   last-frame extraction is a minimal cousin, already shipped.)
4. **Multi-edit EDL.** Shorts/trailer as edit_name rows (make_shorts becomes rows,
   not a tool). TRIGGER: shorts work resumes.
5. **Lip sync.** method='lipsync' + one generator; word_timestamps already kept.
   TRIGGER: first talking-character project.
6. **Multi-voice.** beats.voice present; stage 1 reads per-row. TRIGGER: first
   dialogue project.
7. **Style contract formalization.** Column exists; measured-ingredients extraction
   is doctrine work. TRIGGER: next channel launch or register refresh.
8. **Kling budget by placement** (scene-opening shots, not literal front-N).
   TRIGGER: scenes layer.
9. **Resolution ladder / 4K master.** Column exists. TRIGGER: when wanted.
10. **Fleet/agent operation.** generations table is already the job queue.
    TRIGGER: Claude Code operator lands on the box.
NEW (31 Jul, from the pilot): 10b. **Authored `kling` column at the door** — optional per-beat CSV column replaces blind front-N with placement-by-value (Law 28e); ~10 lines in ingest (method already decided at the door). TRIGGER: the Bible epic's placement map — lands in the fix-commit. 11. **speaking_rate column + read** (fix queue,
near-term, not really backlog). 12. **Reference-conditioned stills** — the Elijah
wiring: canon.reference_paths → the /edit endpoint branch in `_gen_still` (visuals
already refuses loudly by name). TRIGGER: the Elijah project (see
ELIJAH-TASTE-INPUT.md — likely the very next migration).

STANDING DOCTRINE (authoring-side, effective now): get in late leave early;
motion-prompt grammar NOW GOVERNED BY LAW 28 (continuous media only, never contact
physics; witness anchor; events in cuts; kling on phenomena);
objects hold emotion better than faces; unused footage is COVERAGE not waste —
judge spend as cost per second of screen time USED (our 1.4:1 trim ratio is absurdly
efficient against documentary's 20:1–100:1).

## 8. BANNED IN v2, PERMANENTLY
- Time-stretch as a duration fitter, in any form, anywhere (any future slow-motion
  is a per-shot ARTISTIC value in data, never a fitter).
- v1 imports inside shared/v2/. Mode flags selecting v1-vs-v2 inside a file.
- Hand-editing a .db (the door is the only entrance).
- Secrets in the database (tokens stay on disk).
