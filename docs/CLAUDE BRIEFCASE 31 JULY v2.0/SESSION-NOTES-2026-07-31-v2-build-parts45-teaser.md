# SESSION-NOTES — 31 July 2026 — "V2 BUILD + PARTS IV/V + THE FIRST V2 VIDEO"
### The pivot session. Read with __MASTER-WORKLOG.md (31 Jul RECORD entry) and v2-PLUMBING.md.

---

## What happened, in order

**Movement 1 — Part IV, Book of Giants (v1 spine).** Config authored archetype-native
(first film born under Law 22). Law 22's report fired on its FIRST-EVER run
(fragment_forensics 26.4% over cap — fixed honestly with a genuinely distinct
sealed_cave archetype, not a rename-dodge). Gate loop caught: Sam/Nariman macrons
breaking the ASCII writer (fixed at source), ten beats over the real 55-cap (Law 21
proactive scan), three cross-block boundary runs (tableau, shot-dist, human-absent —
the boundary limitation's full family now documented), and a REAL TOOL BUG in
chop_river.py: the distance-swap guard ran AFTER human-forcing and silently discarded
the forced element — fixed permanently (forcing runs last; every future spoke
inherits). Shipped: 289 beats / 11,519 words / ~70 min / kling-12 / **$29.16**.
AUDIT PASSED, intake GREEN, parse 289=289 exit 0.

**Movement 2 — Part V, Book of Jubilees (v1 spine).** Fifth ledger cold-open shape
(aerial jubilee time-grid → dive → Sinai dictation in medias res). Mastema as the
series' first villain through-line. Best archetype spread of the series (top 14.9%,
entropy 0.964, offender-archetypes at zero by construction). Shipped: 291 beats /
11,509 words / ~70 min / kling-12 / **$29.32**. Both parts launched in one sequential
tmux chain (`batch45`, &&-chained).

**Movement 3 — Diversity metrics computed from shipped CSVs** (III retro-tagged as
baseline): archetype entropy 0.891 → 0.939 → 0.964 monotonic; top-archetype share
26.1% → 20.1% → 14.9%; longest same-archetype run 32 → 22 → 21; phenomenon
uniqueness 24.2% → 42.9% → 39.5%; moves dead-even 25% each, all hard-gate axes at
ceiling in all three. Honest gaps flagged for Part VI Step-1: novelty dial below
its ≥2/block floor in ALL films (avg 1.4–1.6, min 0) and scale escalation
flat-to-negative (nothing enforces it) — both are Step-1 architecture questions,
not launch defects.

**Movement 4 — V2 BUILT.** All nine files written, wired, and compiled in-session
from the standing design docs (schema draft 1, decommission map, scope+backlog).
Acceptance in-container, all green: the one-way door on all three real shipped CSVs
(310/289/291 with kling/motion/canon/EDL verified in SQL); door is genuinely one-way
(re-ingest no-op; create refuses overwrite; connect refuses unknown schema); stage 2
proven against a deliberately corrupted synthetic transcript (188 dropped words,
numbers→digits — 96.2% coverage, zero floors, idempotent); visuals mechanics proven
with real ffmpeg (all five doctrine moves at exact duration; trim / clone-pad / and
THE KILL: 5.0s native + 3.4s KB tail, `setpts` count across all nine files: ZERO);
full e2e systems test produced a real 14.21s movie against a 14.2s voiceover
(diff 0.03s) with hand-made stills correctly skipped by pass A — the playground path
proven before Elijah exists. Landed: commit `2eb6996`, 12 files, 2,084 insertions,
`*.db` gitignore in the same commit. Two schema deltas surfaced by building
(voiceover_path, sections_json) folded into 0001 pre-ship; one code bug caught by
the e2e (queried `ref_path`; schema's real, better column is `reference_paths` —
code fixed to match schema, the correct direction).

**Movement 5 — Jubilees launch FAILED at the box verify gate and taught two laws.**
Beat 17 wordless: narration contained "in a single camera move: the angel's finger…"
and parse_script's MOVE_RE uses `search()` — the parser ate the narration as a MOVE
directive. One colon in 911 beats across four films. Fixed at source (colon→dash),
recompiled (291 beats, zero empties, beat 17 back to 52 words + `settle`),
relaunched (`jubilees2`). Bank: the box's wordless-verify caught what FOUR
session-side gates missed (gate-parity gap → empty-narration + tag-word checks queued
for audit/intake; parse line-anchor patch queued as v1 bugfix). **v2 is immune to
this entire bug class by construction — no .md, no prose-vs-directive ambiguity.**

**Movement 6 — The Thomas teaser: first v2 production run, CSV → Studio.**
21 beats / 802 words authored fresh for the door (no csv2script, no parse_script —
first project in the operation's history with neither). Small-N learnings: a river
with no act headers routes everything to block 0; at 21 beats the 15% tableau cap =
3 beats, so teaser authoring is MONTAGE mode — one route per token (Law 27). Box run
caught three v2 bugs at ≈$0 spend: voice case (`elliot` 404'd Inworld; `Elliot`
worked — Law 26), measure's `Path('')`→`'.'` guard (whisper tried to transcribe a
directory), speaking_rate drift (channel 0.97 not traveled — column pending). Then:
Elliot narrated (5.35 min actual — real pace ≈150 wpm on this register), **real
Whisper + the verbatim Troy-fix core: 98.5% coverage, 21/21, zero floors** on genuine
transcription noise, stills + kling + kb-tail in production, assemble, private
upload — **appeared in Studio. v2 proven end to end on its first real run.**

**Movement 7 — Giants Studio verdict (Peter):** loved it. The dream-frame cold open
banked as a standing mechanism — **Law 24, DREAM LICENSE**: declaring the dream in
the opening pre-forgives render hallucination and apocryphal weirdness (the
Inception effect); the weirder the spectacle the better; giant's-eye close-ups
singled out. The audience wants spectacle, not dusty books on lecterns.

---

## The strategic reading (what this session actually was)

**The pivot:** the operation now runs on a database, not a document format. The
CSV remains the authoring instrument (LEGO — every creative decision a column,
human-readable, gate-checkable); the `.db` is the machine instrument (every
production fact a column, resumable, queryable); the one-way door is the only place
they touch. Plumbing is now deliberately forgettable; the value loop —
Studio → taste → topic → river → CSV — is where all attention compounds, and the
`generations` table is the meters-on-the-pipes that converts taste verdicts into
queryable receipts.

**The proof pattern that made it fast:** build → prove with synthetic hostility →
land → let production find the residue. Every leg was exercised before a paid call
existed; the pilot then found exactly the class of bug synthetic tests can't
(paid-API string exactness, env drift, a guard that only fires on a missing file).
Twenty-one beats bought that at ~$3.

**The learning flywheel turned twice in one session:** Studio verdict → Law 24
(dream license) same day; box failure → Laws 25–26 same day; and the system
surfaced its OWN next inputs (novelty dial, escalation) with no human watching.

---

## Full ledger of laws + fixes banked this session

- **Law 24 — DREAM LICENSE** (Studio receipt, Giants).
- **Law 25 — tag-word narration trap** (`move:`/`visual:`/`motion:` forbidden
  mid-narration until parse is line-anchored) + gate-parity (empty-narration +
  tag-word checks → audit/intake).
- **Law 26 — paid-API resource strings are case-exact** (`Elliot` not `elliot`).
- **Law 27 — small-N montage authoring** (one route per token ≤~25 beats; river
  needs act headers or everything is block 0).
- **chop_river.py ordering fix** (human-forcing runs LAST) — permanent, inherited.
- **Never-stretch made law-by-nonexistence** (ruling B; `setpts` absent from v2).
- Runtime calibration: Elliot ≈150 wpm on teaser register (165 law stands for
  features; note the drift).
- **Law 28 — NEVER SIMULATE CONTACT PHYSICS** (teaser Studio receipt, banked
  post-session: continuous media only; events in cuts; witness grammar + physics
  anchor; dream license scoped; kling on phenomena, placement-by-value).

## Fix-commit queue (engineering, next session)
1. `measure.py`: `is_file()` + explicit-None voiceover guard.
2. `ingest.py`: voice default `Elliot`; add + read `speaking_rate` (project column,
   src file or arg); `audio.py` reads it.
3. `audit_script.py` / `intake.py`: empty-narration HARD gate; tag-word-in-narration
   HARD gate (`(?i)\b(move|visual|motion)\s*:`).
4. `parse_script.py` line-anchor patch (`patch_parse_linestart.py`) — v1 bugfix.
5. chop cross-block boundary unification (one carried state across blocks for
   tableau/dist/human axes) — or keep the documented route-boundary discipline.
6. `select_thumbnail_still`: KILL (decommission map says now).

## Live state at session end
- `batch45` complete: giants SHIPPED (in Studio, verdict in), jubilees prep-failed →
  fixed pair relaunched as `jubilees2` (render in progress at time of writing).
- Thomas teaser: PRIVATE in Studio — v2's first video. Peter to confirm on watch.
- Slate: Parts I–V live/rendering = quarter of the 20-spoke slate; forward-scheduling
  available via v1 `--publish-start` for the v1-rendered spokes.
- Part VI (Thomas full film) is the designated FIRST FULL v2 PRODUCTION — new work
  on new pipes; shipped work stays shipped.
