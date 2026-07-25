# _CANONICAL.md — YOUTUBE MEDIA FLYWHEEL
### Crank the handle · Best of both worlds · Rung by rung
*25 Jul 2026. This file REPLACES `_PIPELINE-CANONICAL.md` (move the old file to
`archive/`). It is the root of the documentation tree and the first file loaded in
every session. Everything below is either a law with a receipt, or a pointer to the
doc that holds the detail. If this file exceeds ~300 lines it is failing at its job.*

---

## 0. THE THESIS, IN THREE NAMED IDEAS

**CRANK THE HANDLE.** Outcomes in this lane are heavy-tailed: within a single winning
operator, 6 videos carry 40 and the median does a few hundred views. Per-video results
are near-unpredictable; per-portfolio results are not. Therefore: never pause uploads,
never read single videos (judge cohorts of 40+), never grade a draw — print draws at
near-zero marginal cost and let the tail arrive. Volume beats cadence-tinkering, but
only at constant per-draw quality: topic and packaging span 100–800× within one
operator, cadence spans 2×. Grow the BACKLOG, hold 1/day.

**BEST OF BOTH WORLDS.** LEGO's value is the authoring instrument (package-first,
ledger, dials, audits); PIPELINE's value is the untouched unattended machine. The
bridge compiles one into the other: author in CSV, audit the CSV, compile to the
`.md`+`.thumb.json` pair, machine runs byte-for-byte as always. Zero engine changes.
Proven end to end on `chambers-of-the-dead` (330 beats, ~$43, first film through).

**RUNG BY RUNG.** The scoreboard is the next milestone, never the outlier channels.
Rung 1 (~300 subs) = current run rate held to ~day 110 — pure accumulation, proven by
two age-matched controls. Rung 2 (1,000 subs / monetized) = a regime change: grind
route (143 videos, 8 subs/video) or breakout route (24 long-form universal-question
videos, 304 subs/video). We run the breakout route's shape at the grind route's cost.

---

## 1. THE LAWS (each with its receipt)

1. **Universal beats lore** — within-operator at N=5 channels, including on a winner
   whose Enoch content is its own worst. Gate on every script: *could someone who has
   never heard of the Book of Enoch want this?* Enoch is EVIDENCE, never subject.
   Batch composition ≥70% universal; tag every ledger row; experiment judged at N≥40.
2. **The breakout ticket shape** — a weird specific story everyone half-knows,
   question form, stated payoff, 35–60 min ("Why Did the Demons BEG Jesus for the
   Pigs?" 157K on a 24-video channel).
3. **Length is decided by words-per-beat, not minutes.** Beats cost money; minutes
   don't. Golden-pair density (~45 w/beat ≈ 18s/picture) = ~$32/hour; LEGO density
   (13.5 w/beat ≈ 5s) = ~$104/hour. Slate default: 60 min at golden-pair density,
   title-gated by the ledger — a title that cannot fill ~70 subjects ships at 8
   blocks instead, and that is a pass.
4. **Packaging selects; it does not create.** The 112× "packaging gap" was falsified
   by Covenant Lens (did all the hygiene, sits at our level). What packaging DOES do,
   measured on our own catalogue: a negative retention↔views correlation means the
   title layer promotes the weakest content. Fix titles to select correctly; expect
   lottery odds, not miracles.
5. **Method laws:** no differentiator counts until tested against channels that
   FAILED with it · within-operator comparison beats cross-channel · cohorts are
   frozen at selection (re-picking = survivorship bias) · never trust imputed
   publishDates · operator boredom is a leading indicator (two-signals rule).
6. **Build-order bias is managed by writing it down.** The GOLDEN PAIR
   (bible-they-burned-v2) is the named format authority: format = LAW (header keys,
   `## COLD OPEN`/`## ACT` sections, `[A] narration` + `VISUAL:` + `MOTION:` block
   shape, thumb keys subject/title/subtitle); content = INCIDENTAL (its beat length,
   title grammar — inherit deliberately or not at all). Conformance is mechanical:
   compiled output must pass `parse_script.py` with zero warnings.
7. **Probe before spend, always** — as a throwaway mini-project through the real
   engine (same model, same suffix), ~$1.60, then delete. The chambers probe paid for
   itself 20× in one run (letterbox + armour negatives, now channel rulebook).
8. **Floor-first economics:** every beat Ken Burns free; Kling is additive.
   Batch law = contiguous front-N (`--kling-count 40`) with AUTHORED MOTION lines on
   those beats — the golden pair's own animation pattern. fal `safety_tolerance:"5"`;
   `nano_banana_2` confirmed or stills come back murk.
9. **Thumbnails are hand-made, always.** `select_thumbnail_still` failing is noise,
   not a bug. Titles/tags/thumbnail pushed by `packaging_push.py` when repairing
   live catalogue.
10. **`-src` convention:** the authoring folder is `<slug>-src/`; the machine owns
    `<slug>/` via create_project and refuses if it exists. Compiled pairs go to the
    inbox ONLY. (`--plan` does not hit the exists-guard — banked 25 Jul.)

---

## 2. THE TWO PRODUCT LINES (scope law)

| | **Line B — batch** (the draw machine) | **Line F — feature** (the craft line) |
|---|---|---|
| governs | `_BRIDGE.md` (+ `_SCRIPT-CONTRACT.md` writing passes) | `_LEGO.md` 0–10 + Filmora |
| path | CSV → audit → compile → parse gate → probe → inbox → `run_batch` | grid → human pick → place → render → hand assembly |
| cadence | 1/day drip, scheduler flags | max 1–2/month |
| cost | ~$32–48 per 60-min film | ~$100–160 + sessions |
| human gates | architecture · audit report · cold open · probe stills | the pick (gospel) + all LEGO gates |

Peter's marginal hour goes to **Step 0 across many videos** (topic, title, thumbnail,
cold open) — execution is at ceiling (86/100), architecture and the click are where
outcomes live. Line F gates: universal test + winnability + architecture ≥70 scored
at Step 1 + ten-frames + spectacle ≥30% (a film failing at Step 1 dies at $0).

---

## 3. THE BRIDGE DEPENDENCY MAP (Line B, end to end)

```
package.md ──┐                                      (Step 0: title+thumb+universal gate)
architecture.md ─┐                                  (Step 1: ledger, container, dials-on-ledger)
                 ▼
master.csv + canon.json + sections.json + desc.txt + thumbsubj.txt      [<slug>-src/]
                 │
    packaging/audit_script.py        (dials, dupes, words, safety, topic mix, BILL; exit!=0 blocks)
                 │
    packaging/csv2script.py          (tokens expanded; golden-pair emit; hard-fails)
                 ▼
    <slug>.md + <slug>.thumb.json    (the pair — the ONLY thing the machine sees)
                 │
    shared/parse_script.py           (GATE OF RECORD: beats==rows, zero warnings)
                 │
    PROBE: ~20-beat pair → probe_inbox → run_batch --kling-count 0 → eyeball stills → delete
                 ▼
    <channel>/batch_inbox/  →  shared/run_batch.py --kling-count 40
        └→ create_project (refuses if <slug>/ exists → -src convention)
        └→ render_policy.json + thumbnail.json
        └→ parse → orchestrate → audio (channel voice) → whisper align
        └→ stills (image_model + style_suffix + channel rulebook.json negatives)
        └→ Kling front-N on authored MOTION lines → KB floor on the rest
        └→ assemble → final_video.mp4 → private upload (or --publish-start schedule)
                 │
    hand thumbnail in Studio → publish/schedule → LEDGER ROW (topic_class, line,
    length, title shape) → weekly Studio CTR read → fortnightly _PACKAGING-AUDIT
                 └──────────────── observations feed the next Step 0 ────────────────┘
```

Multi-pair staging: `stage_batch.py --zip` routes zips of pairs into channel inboxes
and can emit a `run_all_batches` plan skeleton — that is the batch-of-batches layer.

---

## 4. THE 20-SLATE BATCH PROCESS (the current campaign)

Source: `sacred-dawn-lineb-slate-01.md` — 40 universal-question packages, 7 pools.
Front-load Pools A (death/afterlife) and B (heaven mechanics): every 40K+ cohort
breakout lives there. First campaign = 20 titles.

Per title: **package → architecture (60-min default, ledger-gated) → CSV authored
block-by-block against the ledger (generation per block, review per film: three
human touchpoints — architecture, audit report, cold open) → audit → compile →
parse gate → probe (only if the title introduces new canon/register; a slate batch
sharing proven tokens can probe once per wave) → pair to inbox.**

Ship: `run_batch` with `--publish-start <ISO+tz> --publish-interval-hours 24` for
the 1/day drip. Ledger row at ship. Read at N≥40 tagged videos, channel level,
fortnightly — never per-video at 48h ("check nothing exploded" is the only 48h job).

Budget: 20 × ~$32–48 ≈ **$650–950** for ~20 hours of catalogue aimed at the proven
ticket shape.

---

## 5. THE RUNG LADDER (frozen cohort controls in cohort.json)

| rung | controls | route | our position |
|---|---|---|---|
| now (~85 subs) | Covenant Lens | — | peer |
| ~300 subs | FeelAngels 216/98d · BSHH 319/113d | accumulation at our current rate | on pace, ~day 110 |
| 1,000 / monetized | Sealed Word 1,160/88d (grind) · Bible Academia 7,290/73d (breakout) | breakout = Line F format + universal topics | the slate is aimed here |
| ceiling (model only) | Discernment 10.6K/45d · Enoch Codex · FBS | 6-hits-in-40 lottery | never the scoreboard |

Bars: 1,000 subs (binding) · 4,000 watch-hours (long-form makes this the easy bar).

---

## 6. THE DOCUMENT TREE (all doctrine lives in `docs/`; load order for any session)

**ALWAYS load:** `docs/_CANONICAL.md` (this file) + `docs/__MASTER-WORKLOG.md`.
**Then the task doc:**

| task | doc |
|---|---|
| Line B authoring / compiling / shipping | `docs/_BRIDGE.md` |
| strategy, time allocation, gates | `docs/_STRATEGY.md` |
| fortnightly cohort read | `docs/_PACKAGING-AUDIT.md` (+ frozen `docs/cohort.json`) |
| Line F feature work | `docs/_LEGO.md` (+ the film's `architecture.md`, `package.md` in its `-src/` folder) |
| writing-quality passes, probe mechanics | `docs/_SCRIPT-CONTRACT.md` (§6 genre overlays are STALE — register lives in the channel doc only) |
| channel doctrine | `docs/channels/_Sacred-Dawn.md` / per-channel doc |
| the topic slate | `docs/slates/sacred-dawn-lineb-slate-01.md` |
| per-film verdicts | `docs/scorecards/<film>-scorecard.md` (METHUSELAH-scorecard.md is the rubric template) |
| session records | `docs/sessions/SESSION-<date>.md` |

**RETIRED (`docs/archive/`, never load):** `_PIPELINE-CANONICAL.md` (this file replaces
it), `STARTUP_PACK.md`, `ante-machinam.md`, superseded session notes.

**Placement laws:** doctrine in `docs/` only — never in `shared/` (code), never in
channel folders (channel folders hold config + projects). Film-local authoring docs
(`package.md`, `architecture.md`) live with their film in `<slug>-src/`. Runtime
artifacts (batch manifests) are not docs and get gitignored, not archived.

---

## 7. INFRASTRUCTURE & DISCIPLINE (unchanged, restated once)

- BOX `peter@pipeline-prod` 116.202.18.68, SSH port 443, repo `~/Pipeline`,
  venv `~/venvs/pipeline` (`python`). LAPTOP `~/Projects/Pipeline` (`python3`).
  GitHub `peteralkema/Pipeline` is the sole code transport. Media by rsync/scp,
  gitignored. Project CSVs and pairs ARE git-tracked: **author wherever, but commit
  before the file crosses machines** (banked 25 Jul after a silent divergence).
- Edit on LAPTOP → commit → push → BOX `git pull --no-edit`. Never hand-edit on box.
  Never `git add -A`. Patches are idempotent `patch_*.py` with anchor verification,
  `.pre_*` backups, `py_compile` before write, ASCII only.
- Probe-before-spend; stills gate is the probe on Line B. Never restart
  `mission-control.service` mid-animate.
- Channel pre-flight before ANY render: `style_suffix` present · `image_model`
  correct (`nano_banana_2` for Sacred Dawn) · env propagation live
  (`env=os.environ.copy()` in convergence Popen). Voice log strings may be stale
  fossils (a "Victor" print on an Elliot channel) — trust channel.json + your ears.
- MC is production polish, not the batch path. Batches never require MC or stills
  review; the probe is the eyeball.

---

## 8. THE CHANGE BUDGET (defend against scope creep)

1. **Nothing now.** The bridge ships on standalone tools; the machine stays untouched.
2. **Next sanctioned engine touch:** the ambient fx layer (grain + Artlist overlay
   packs already paid for; per-beat `fx` column; inert when absent). Upgrades the
   ~85% of every film that is free floor.
3. **Deliberate-later:** `audit_script.py --scorecard` mode (spectacle share, spine
   cap, scale placement — the pre-ship table, mechanised) · hero 2-variant re-roll
   (only if stills-gate failure data demands) · parallel fal animation ·
   `make_shorts.py` (cohort says no Shorts — keep parked).

---

## 9. FRESH-SESSION PROTOCOL (for Peter and for Claude)

1. Upload/load: `_CANONICAL.md` + `__MASTER-WORKLOG.md` + the task doc from §6.
2. State the goal in one sentence and the rung it serves.
3. Paste real terminal output and real file heads — Claude reads before proposing;
   Claude never guesses CLI flags, signatures, or file formats (the golden pair
   exists because guessing failed).
4. Full paste-block files, never snippets. Command blocks labeled LAPTOP or BOX in
   prose, no comments inside blocks. One step at a time on multi-step work.
5. Every session that changes doctrine ends with: worklog entry + which doc absorbed
   the lesson. A lesson not written into a doc did not happen.

---

## APPENDIX A — THE PROCESS, AS CLOCKED BY HAND (25 Jul, the whiteboard walk)

Five stations, one loop. Money moves in exactly one box; human judgment in exactly three
moments per film. The hand-drawn version lives beside the desk; photo in `docs/sessions/`.

| station | inputs | what happens | outputs |
|---|---|---|---|
| **DESIGN** | slate line · universal test · winnability | the click is designed before the content exists (title, thumbnail lockup, promise) — then the film is designed AS A TABLE (container, subject ledger, scale budget, spine, dials run ON THE LEDGER) | `package.md` ("the click") + `architecture.md ≥70` ("the table") — both in `<slug>-src/`, both at $0. A film failing here dies free |
| **AUTHOR** | package + architecture | beats written into `master.csv` block-by-block against the ledger (subjects spent once, forbidden after). Columns: narration ≤55w · phenomenon (tokens) · subject (dials) · scale (budgeted) · air/motion (front-40) · topic_class | `master.csv` in `-src/` |
| **GATE** | master.csv | `audit_script` (dials, dupes, words, safety, topic mix, BILL) → `csv2script` (tokens expanded, golden-pair emit) → `parse_script` (GATE OF RECORD: beats==rows, zero warnings) → probe (~20 risk beats, ~$1.60, through the REAL engine, delete after) | a blessed pair + a verdict — total gate cost ~$1.60 |
| **RENDER $** | the pair → `batch_inbox/` | one command (`run_batch --kling-count 40`): voice · whisper · stills · Kling on authored motions · KB floor · music · assemble · private upload. Untouched, unattended. **The only box where money moves** | `final_video.mp4` (~$43 at 27 min / ~$32-48 at 60 min golden-pair density) |
| **OBSERVE** | the private video | hand thumbnail (always) · watch · schedule into the 1/day drip · **one ledger row** (topic_class, line, length, title shape) · weekly 10-min Studio CTR read · fortnightly cohort read · N≥40 campaign verdict | the loop arrow: observations feed the NEXT film's DESIGN. Without the arrow it's a production line; with it, the flywheel |

**Grain:** DESIGN/AUTHOR/GATE per video · **probe per WAVE** (a batch sharing proven
canon/register/suffix probes once — the probe tests the system, not the script) ·
RENDER per batch (N=1 is a batch) · OBSERVE per video for ACTIONS, per cadence for READS.
The split protects against the cardinal sin: reading any single video as a verdict.

**The three human touchpoints per film:** the architecture · the audit report + probe
stills · the cold open. Everything else is the handle turning.

---

## APPENDIX B — START OF A FRESH CLAUDE SESSION (the exact ritual)

**Upload/load, always:** `docs/_CANONICAL.md` (this file) + `docs/__MASTER-WORKLOG.md`.
**Plus exactly ONE task doc:**

| session is about | third doc |
|---|---|
| authoring / compiling / shipping Line B | `docs/_BRIDGE.md` |
| strategy, priorities, where hours go | `docs/_STRATEGY.md` |
| the fortnightly cohort read | `docs/_PACKAGING-AUDIT.md` |
| a LEGO feature | `docs/_LEGO.md` + that film's `-src/` docs |
| channel doctrine | `docs/channels/_Sacred-Dawn.md` (or relevant) |
| picking slate titles | `docs/slates/sacred-dawn-lineb-slate-01.md` |

**The ritual, in order:**
1. State the goal in ONE sentence and the rung it serves.
2. Paste real terminal output and real file heads — never describe from memory.
3. Claude reads actual code/data before proposing; never guesses CLI flags, signatures,
   or formats (the golden pair exists because guessing failed).
4. Full paste-block files, never snippets. Command blocks labeled LAPTOP or BOX in
   prose, no comments inside blocks. Multi-step work one step at a time.
5. The session ends with: a worklog entry + naming which doc absorbed each lesson.
   **A lesson not written into a doc did not happen.**

**The standing next-session briefcase (as of 25 Jul):** canonical · worklog · `_BRIDGE.md`
· the slate → chambers final video (hand thumbnail → schedule → ledger row), then pick
the first eight slate titles and build eight ledgers. Cadence never breaks while you work.
