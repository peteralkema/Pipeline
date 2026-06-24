# _MASTER-WORKLOG.md — YouTube Media Flywheel

_The one living operational log. Solo operator (Peter, The Hague). All edits LAPTOP → GitHub → box; never hand-edit on box._
_Last updated: 23 June 2026 (THE 55-VIDEO BATCH-OF-BATCHES + THE FIRST FEATURE FILMS — six channels / 55 videos in one sweep (54/55 clean), then the pipeline's first two feature-length films rendered end-to-end and scheduled: `watchers-the-movie` (74.8 min) + `revelation-the-movie` (69.7 min). The factory proved it scales an order of magnitude — 8-min shorts to 70-min features — with no format-level break. Banked: the runtime estimator's 120wpm floor is wrong (real Inworld delivery ~165–178 wpm); `create_project` verify catches `no_visual` where the cheap gates don't; the three-gate zero-spend pre-flight; the phone-first logging rewrite spec.)_

---

## How to maintain this doc (read once)

This file replaces the pile of dated `SESSION-NOTES-*.md`. It has two halves:

1. **THE BACKLOG (front)** — everything still open, prioritised. Read at the start of a session, edit at the end.
2. **THE RECORD (back)** — a compressed, reverse-chronological list of what shipped each session. A memory aid, not a working doc.

**The discipline that keeps this from rotting:**
- **Durable lessons graduate OUT of here** into the **canonical reference** (the system) or **ante-machinam** (the craft) — not a worklog entry. Before a block ages out of THE RECORD, lift anything still true-and-reusable into the canonical/ante-machinam first, *then* compress the block to a one-liner.
- **THE RECORD is allowed to be lossy.** Once a lesson is in the canonical, its block can shrink to date + headline. Detail you might want later → a dedicated `SESSION-NOTES-<date>-<topic>.md` in an archive folder, linked from the block.
- **The test for "backlog or done?"** — *does the machine already do this for me?* If yes, move it to THE RECORD.

---
---

# THE BACKLOG

_Standing read: the system is browser-only end to end, uploads across the active channels on non-expiring auth, renders at ~$16.80/video (cinematic) or ~$3/video (Ken-Burns), runs a fully-unattended batch path with a read-side verifier (`dump_channel.py --all --cadence`, §5.10), and — proven 23 June — scales cleanly to feature length (70-min films). The **standing pre-flight before any batch** is the three-gate zero-spend check (parse all scripts → slug-collision scan → `run_all_batches --plan`), and for long-form, confirm `create_project` verify clears (the cheap gates do NOT catch `no_visual`). **The highest-leverage move is shipping real videos and letting first-48h CTR + AVD drive what to fix — not grinding this list.** Operating frame (§2A): automate the labour, concentrate craft on the channel showing a vein, gate on review, cull without sentiment._

## Live state / pending publish (operational, not backlog)
- **★★ The two FEATURE FILMS — rendered clean, uploaded, SCHEDULED Sat 27 June 01:00 CEST (Fri 19:00 US prime).** `watchers-the-movie` (sacred-dawn, 360 beats, **74.8 min** confirmed) + `revelation-the-movie` (scripture-on-screen, 355 beats, **69.7 min** confirmed), both `--kling-count 40` front-loaded (~$17 fal each). Both verified COMPLETE not truncated (video-duration == voiceover-duration to the half-second). The pipeline's first feature-length renders — proof the production system spans 8-min shorts to 70-min features with no break. **ACTIONS before Friday:** (1) confirm in Studio both private + scheduled at the 27 June slot, each with its **composed** thumbnail attached (silent thumbnail-set failure has bitten before — flagship thumbnails are the whole shop window); (2) spot-check each cut — cold open (first 90s, AVD-critical), a couple of mid-points, the final beat (feature length compounds any glitch). NB runtime came ~30 min UNDER the ~103-min estimate — NOT short, the estimator was wrong (#29b).
- **★ The 55-video batch-of-batches (23 June) — 54/55 shipped clean.** prehistoric (10), sacred-soak (5), you-had-to-be-there (10, kling 0), cathedral_of_stars (10), scripture-on-screen (10), final-hours (10). One straggler: **`jacob-esau` (scripture) FAILED at the stills leg** (vo + publish.json present, no final_video, 0 stills — transient fal blip, isolated cleanly). Slot 03 July (`2026-07-03T23:00:00Z`), 11 days out — **ACTION (no rush): resume via `orchestrate.py` on the EXISTING project** (voiceover banked, slot preserved), NOT the inbox. sacred-dawn + scripture inboxes swept to `_shipped/` during the feature launch; the other four still hold their 55-run pairs — sweep before their next batch (#11n).
- **★ Satan flagship (Sacred Dawn, `satan-morning-star`, 89 beats, ~26.4 min, 45 Kling) — SCHEDULED 21 June 20:00 CEST.** Worst video rebuilt into strongest film. **ACTIONS:** confirm bottom-left thumbnail + chapters (0.040 re-mux); Altered/AI flag; move pair to `_shipped/`; **DIARISED ~mid-July: pull Satan retention vs the original 15.7%.**
- **gustloff** (Final Hours) — private, `wiykuEhTY1k`. **ACTION: set Altered = Yes before publishing.**
- **★ Lady Be Good bomber (Final Hours, `PCTEasHZjwI`, 6:45) — ORPHAN from 19 June.** Never reviewed, rescheduled 29 June 04:30 CEST. **ACTION before 29 June: open, set Altered/AI = Yes, eyeball, re-time to 01:00 CEST if wanted.**
- **Standing practice (21 June):** after every batch, `dump_channel.py --all --cadence` in Amsterdam time — fill any GAP, scan orphans/collisions.
- **Esther** (Scripture, 119 beats) / **Enoch** (Sacred Dawn, 132 beats) — rendered; need packaging/publish.
- **70smusic** (You Had To Be There, 105 beats) — confirm done + publishable.

## Tier 1 — Ship & verify (the real work)
1. **Read first-48h CTR + AVD as data matures** — prehistoric ep1/ep2, the 55-run wave, and the big one: the two features once live (AVD on a 70-min long-form asset vs Wild Horizons long-doc behaviour; cold-open first-90s is the game).
2. **Close the gaps the runs surfaced** — manifest ✗ check, Studio spot-check (private + 01:00 `+02:00` + thumbnail), sweep inboxes before re-run. **Gaps (Tier 2):** (a) re-ingest auto-archive (#11n); (b) thumbnail-set retry + persist video ID + `set_thumbnail.py`; (c) `--plan` → `validate_slug` + `thumb.json` schema (#11m); (d) `--plan` → `create_project` verify so `no_visual` fails cheap (#11o).
3. **Resume `jacob-esau`** — `orchestrate.py` on the existing project, slot intact.
4. **Prove dramatic motion on a Kling-heavy render** — `cain-abel`. (The features' 40-Kling front-loads are now real evidence the tiered path holds at scale.)
5. **Get pending-publish videos out** (gustloff, Esther/Enoch).

## Tier 2 — Correctness / safety still genuinely open
6. **Retire or guard `finish --assemble-only`** — calls alignment-UNSAFE `recreation_pipeline.assemble()` (drifts). Still CLI-reachable.
7. **Confirm `cmd_stills` passes `safety_tolerance:"5"` on the FIRST stills pass.** Confirm in code, close.
8. **`finish --plan` not side-effect-free** — mkdirs before early-exit + CWD-relative path. Tiny.
9. **`proj_paths` bug — WORSE than documented.** `assemble_episode.py` falls back to hardcoded `projects/ep1-the-promise/` for file lookups AND `mkdtemp` work-dir when `--project` doesn't resolve. **Fix:** `--project` drives ALL derived paths, kill the literal, fail loudly. **Workaround (§13): re-mux needs `--project` AND explicit `--durations/--index/--voiceover/--clips`, OR run from inside the project dir.**
10. **Inworld model-string reconcile** — doc/code drift; live model `inworld-tts-2`, `speakingRate` in `audioConfig` works.
11. **Inworld chunk-validation guard — GENERALISE to all-API retry-with-backoff.** A failed/empty chunk should retry or hard-fail, not silently concatenate dead air. **Re-confirmed TWICE: `lost-human-species` (Inworld, audio) and `jacob-esau` (fal, stills) were both single transient-API blips with no retry. The durable fix is GENERIC retry-with-backoff around EVERY external API call (audio + stills + anim), not just Inworld — at feature length (~360 chunks) the exposure is ~9× a short. Highest-leverage reliability fix on the board.**

## Tier 2.5 — Engine upgrades (Satan flagship session, 20 June)
11b. **Thumbnail `--text-anchor` flag (HIGH).** Add the override + a `text_corner` return from the substrate-selection Sonnet call. Bottom-left = reserved flagship signal. → `_Sacred-Dawn.md` §7.
11c. **Music `level`-key wiring + LUFS-target normalisation (HIGH).** Wire the inert `level` key; replace fixed `MUSIC_LEVEL` with a measured-LUFS target. 0.040 flat is interim. → §5b. **Feature-length note: the two 70-min features used the fixed 0.040 bed — spot-check it holds across 70 min.**
11d. **Chapters/description auto-builder.** `audio_start` → `mm:ss` chapters + template. → §7b. **A 70-min feature NEEDS chapters more than any short — high-value for the two features.**
11e. **Score-aware music placement (horizon).** Whisper timestamps + per-beat energy → intentional scoring.
11f. **rsync over scp for box pulls (§13).** Re-confirmed: inboxes gitignored — pairs by scp/rsync, not git.

## Tier 2.6 — Read-side / cadence upgrades (21 June)
11g. **Cadence: read `batch_inbox/` for TRUE runway** (today only sees Studio-scheduled).
11h. **Runway alarm** — flag any channel whose span ends within N days.
11i. **Golden-hour check** — flag any slot not at 01:00 CEST.
11j. **Auto-run cadence at the tail of `run_all_batches.py`.**
11k. **Read-views over `channel_dump.json`** — `artlist_worklist` + `missing_chapters`.

## Tier 2.7 — Phone-first logging rewrite (23 June)
11l. **Rewrite the orchestrator's visible logging — phone-first, surgical (HIGH).** The current stream is human-gate-era — the **ASCII-art banner** ("Peter's Pipeline Orchestrator") + `phaseStrip` + program-narrating lines. **Scrap all of it, ASCII art included.** Peter monitors multi-hour runs from his phone (Termius); each poll line must answer "where, how far, healthy, do I act" from the LAST VISIBLE LINE ALONE.
   **Principles:** self-contained lines with `[chan N/M · vid N/M slug]` coordinates; fractional progress on looping phases (`voiceover 7/12`, `flux 41/79`, `encode 9m/≈18m`); fixed vocab `AUDIO · STILLS · ANIM · ASSY · THUMB · UPLOAD`; heartbeat-age tail (`·15s ·30s`) as stall signal; emit-on-change; surgical failure lines; channel roll-ups. Keep 15s cadence.
   **Target stream:**
   ```
   [2/6 prehistoric · 6/10 messinian]  ▶ START  79 beats · kling 2 · ~18min est
   [2/6 prehistoric · 6/10 messinian]  AUDIO   voiceover 7/12 chunks                 ·30s
   [2/6 prehistoric · 6/10 messinian]  AUDIO   ✓ done · 18m32s locked · 79 beats timed
   [2/6 prehistoric · 6/10 messinian]  STILLS  flux 41/79 · safety_tol 5             ·45s
   [2/6 prehistoric · 6/10 messinian]  ANIM    kling 2/2 ✓ · ken-burns floor 77/77
   [2/6 prehistoric · 6/10 messinian]  ASSY    ffmpeg encode 9m/≈18m · preset medium ·30s
   [2/6 prehistoric · 6/10 messinian]  THUMB   ✓ cand 2 (clean left col) · headline baked
   [2/6 prehistoric · 6/10 messinian]  UPLOAD  → private + publishAt 06-27 23:00Z
   [2/6 prehistoric · 6/10 messinian]  ✓ DONE  18m32s · publishAt Sat 06-27 01:00 CEST
   ```
   **Where it lives — NOT one file (the key insight).** The line needs three contexts from three layers: batch position (WRAPPERS `run_all_batches.py`/`run_batch.py`), phase (ORCHESTRATOR `orchestrate.py` + legs), loop fraction (ENGINE `recreation_pipeline.py` — the only layer inside the `for chunk/still/clip` loops). No single file has all three — which is why the current logging is dumb. **Fix: a thin shared emitter (`pipeline_log.py`) + a context object threaded wrappers → orchestrator → legs → engine.** Call sites go from `print("generating voiceover")` to `log(phase="AUDIO", n=7, total=12)`.
   **Build step 1 (read-only spec):** grep every `print(`/log call across the four layers; map each to its phase; that trace IS the spec.
   **Known unknown:** the encode fraction needs ffmpeg's `-progress` pipe, which `assemble_episode.py` may not wire — the one phase that may need plumbing. (Earns its keep most on the 70-min features.)
   *One focused build on a non-launch day — touches four layers; don't nibble.*

## Additional gaps surfaced 23 June
11m. **`--plan` does NOT validate `thumb.json` schema — only catches a missing pair (MED).** Cathedral's 10 thumbs were present + paired but missing `subject` → all 10 `prep_failed` at run-time. **Fix: `--plan` asserts `subject` + `title` non-empty.** Workaround = the three-gate pre-flight.
11n. **Auto-archive shipped pairs STILL open (MED — `patch_batch_archive_shipped.py` drafted 19 June, never applied).** Runs leave pairs in `batch_inbox/`; the collision guard is the real protection, but inboxes must be hand-swept to `_shipped/`. Apply on a non-launch day: archive on `ok=True` only.
11o. **`--plan` does NOT run `create_project` verify, so `no_visual` slips to spend-time (MED — NEW, the feature-launch lesson).** `watchers-the-movie` `prep_failed`: 22 of 360 beats had narration but no `VISUAL:` line. `parse_script.py` PASSES these (parsing succeeds) — only `create_project`'s `verify` checks every beat HAS a visual. Same class as #11m. **Fix: `--plan`/a standalone pre-flight should run the `no_visual` scan, BEFORE staging a multi-hour render.** Interim (proven): a `python3` regex scan for beats lacking `VISUAL:`. **Open design question: were the 22 MISSED or authored to hold the prior image?** If the latter recurs, the better fix is a pipeline rule — "inherit previous VISUAL when none given" — rather than hand-writing visuals into every long script.

## Tier 3 — Console / cosmetic polish
12. **Mission Control thumbnail integration** — capture thumbnail text in create flow; show generated thumbnail beside final video with regenerate/accept.
13. **Tiered-aware strip label** — *subsumed by #11l*.
14. **Kling-count field into the always-visible controls strip.**
15. **`voice_id` cosmetic label** (`patch_voice_label.py` drafted).
16. **Gate-button human/wire split remnants.**
17. **Upload polish** — per-channel `upload` blocks; rename OAuth consent app → "Pipeline."

## Tier 4 — Bigger builds
18. **Upload scheduler — SHIPPED 19 June, proven at scale (55 videos) and feature length (2 films).** `--publish-start` + `--publish-interval-hours`; private + publishAt; `--plan` calendar. Day-after-furthest-tail = no-state collision rule; for features hand-set a Friday-US-prime slot (an event, not daily cadence). → §5.9. *(Done; design-of-record.)*
19. **Faster final encode — PROMOTED by feature length.** `-preset medium -crf 18` is the heaviest step (~20 min for a 20-min video; HOURS for 70-min). `-preset fast`/`veryfast` on Ken-Burns lanes ≈ halves it, no visible loss. Biggest throughput lever now 70-min encodes are in the mix. Verify on one video first.
20. **Decade-look Phase 2** — `film_emulate.py` does not exist.
21. **v2 motion routing** — route Kling by which beats EARN motion, not positional first-N. *(Features used positional front-40, authored front-loaded so it held — the latent limit.)*
22. **Parallel fal animation** — bounded-concurrency semaphore; matters on 40-Kling features.
23. **Batch orchestration polish** — re-run story; optional parallelism (sequential now).
24–26. **Synthetic Mode B** — within-card word-sync; design-on-page; Remotion component gaps.

## Tier 5 — Authoring discipline (craft doc, not code)
27. **Beat-granularity calibration** — graduated to ante-machinam §6 (~14s/beat).
28. **Script-format-from-exemplar** — graduated to ante-machinam Part VI.
29. **Slug rule** — `^[a-z0-9][a-z0-9-]{0,60}$`: lowercase, digits, hyphens; NO underscores, NO `NN_`. Numeric prefixes fine with a hyphen (`11-`…`20-`). Bit Cathedral twice. → §12 + ante-machinam.
29b. **Runtime estimator is WRONG for Inworld voices — the feature-length calibration (NEW → ante-machinam §6).** The `max(beats×14s, words/120wpm)` estimate overshot the two features by ~30 min. MEASURED: **watchers 12,391 words / 74.8 min = 165.6 wpm; revelation 12,421 words / 69.7 min = 178.2 wpm** — far above the 120wpm floor (consistent with Inworld ~190–200 raw, slowed to ~165–178 for reverent channels). The floor compounds to ~30-min error at ~12k words. **Author features TO a target at ~165–178 wpm (a 90-min feature ≈ 15,000 words, not 11,000).** The spread (Ren ~178 > Elliot ~166) is per-voice pace. NB ESTIMATE-only: runtime is set by actual narration, so a "short" feature is COMPLETE, just faster — verify via video-duration == voiceover-duration, NOT against the estimate.

## On the shelf — deliberate next analysis (do not lose)
- **Thumbnail packaging audit — the predicted-CTR experiment (TWO stages).** **Stage 1:** sweep every uploaded title+thumbnail pair, score each as the combined unit via Sonnet vision on a PER-CHANNEL rubric, emit a **committed predicted-CTR / predictor score + sub-scores (legibility, subject-text separation, complement-not-echo, register fit, scale-anchor, title curiosity-gap) + rationale** per video. **Freeze it — dated, committed to `shared/audits/thumbnail-audit-<date>.json`, NEVER re-touched once views land.** The frozen-before-outcome prediction is the entire methodology: *it is too easy, consciously or not, to "remember" a thumbnail scored well once you see it performed well.* Record the correlation hypothesis up front (open: relative-rank-within-channel vs absolute-CTR — lean relative-rank). **Stage 2 (weeks later):** pull actual first-48h CTR via NexLev, join by slug, test predicted-rank vs actual-rank AND per-sub-score correlation. Strong → validated instrument, becomes an authoring gate. Weak → our eye and the audience diverge. Unit = **thumbnail + title together**; CTR is the matched outcome; AVD kept separate.

## Banked-for-later / low
- **`.gitignore` for generated artifacts** — `render_policy.json`, `thumbnail_selection.json`, `*.pre_*`, `_index.json`, `channel_dump.json`, `publish.json` (outputs not source).
- **Cleanup pass (23 June):** stray `~/batch_inbox`, `~/batch_rerun_3`, `prehistoric-disasters/inbox/`, `_hold_revelation/` (revelation now rendered — the hold dir can go). Canonical inbox is `<channel>/batch_inbox/` only.
- **review-server / multi-project daemonized review server** — superseded by Mission Control.

---
---

# THE RECORD (compressed, newest first)

### 23 June 2026 — THE 55-VIDEO BATCH-OF-BATCHES + THE FIRST FEATURE FILMS
The biggest production day to date. The factory ran six channels and 55 videos in one unattended sweep, then rendered its first two feature-length films end-to-end — proving the production system scales an order of magnitude with no format-level break.

**The 55-video sweep (one `run_all_batches.py`, `batch_plan.json`-driven).** prehistoric (10), sacred-soak (5), you-had-to-be-there (10, kling 0), cathedral (10), scripture (10), final-hours (10). Each channel's `publish_start` set the day after its furthest-future scheduled tail (via `dump_channel.py --scheduled-only-summary`), 24h interval, kling 2 except YHTBT 0. **54/55 shipped clean, cadence-continuous, zero gaps** across a ~21.4h run. Scheduler proven at portfolio scale; day-after-tail is the no-state collision rule.

**The three-gate zero-spend pre-flight (standing practice → #11m, §5.9).** (1) `parse_script.py` every `.md`; (2) slug-collision scan; (3) `run_all_batches --plan`. NB the deep `create_project` verify is a FOURTH gate the cheap three don't cover (the feature `no_visual` catch).

**Cathedral thumbnail-rescue (caught at the dry run, zero spend).** 10 thumbs present + paired but missing `subject` → all 10 `prep_failed`. Authored the 10 `subject` prompts from Cathedral §7, preserved `title`/`subtitle`, re-staged clean. → #11m. The `NN_`→`NN-` slug trap caught a second time (#29).

**The `jacob-esau` straggler (isolation working as designed).** Failed at the STILLS leg (vo + publish.json, no final_video, 0 stills → transient fal blip). The per-channel `try/except` isolated it; the batch rolled on. Resume via `orchestrate.py`, slot (03 July) intact. **Second data point (after `lost-human-species`/Inworld) that the durable fix is generic retry-with-backoff across ALL APIs → #11.**

**★★ THE FIRST FEATURE FILMS (the headline).** `watchers-the-movie` (sacred-dawn, 360 beats) + `revelation-the-movie` (scripture, 355 beats), ~12,400 words each, both `--kling-count 40` front-loaded (~$17 fal each), scheduled **Sat 27 June 01:00 CEST** (Fri 19:00 US prime — a feature is a weekend long-watch EVENT, slot hand-set, not day-after-tail). Run as a two-channel `run_all_batches` (sequential, per-channel isolation). **Both rendered clean + uploaded.** Confirmed COMPLETE not truncated: **video-duration == voiceover-duration to the half-second** (watchers 4490.5s vid / 4490.6s voice; revelation 4183.2s / 4183.3s). The pipeline spans 8-min shorts to 70-min features with no break — direct proof of the production-system-is-the-moat bet.
  - **The `no_visual` prep-failure + recovery (→ #11o).** First run, watchers `prep_failed`: `verify={'ok': False, 'no_visual': [0,2,4,5,51,56,69,...]}` — 22 of 360 beats had narration but no `VISUAL:`. `parse_script.py` and `--plan` BOTH passed it; only `create_project`'s verify checks. Caught at ZERO spend. Fixed by authoring the 22 visuals (`movies2`), verified locally (0 missing) before re-staging. Open: were they missed, or meant to hold the prior image (→ an inherit-visual rule)?
  - **Runtime came ~30 min UNDER the ~103-min estimate — NOT short, the estimator is wrong (→ #29b).** Both ~70 min (74.8 / 69.7), consistent with each other (the tell it's systematic). Measured 165.6 / 178.2 wpm vs the formula's 120 floor. Calibration banked.

**Banked to backlog:** phone-first logging rewrite (#11l — scrap ASCII-art + `phaseStrip`; shared emitter + context across four layers); `--plan` thumb-schema (#11m); `--plan` `create_project`/`no_visual` verify (#11o); auto-archive re-confirmed (#11n); faster-encode promoted (#19); generic API retry-with-backoff (#11).

**Durable lessons to graduate (pending the canonical edit this session):** three-gate pre-flight + the `create_project`-verify fourth gate → §5.9/§12; the wpm calibration → ante-machinam §6; feature-length proof (system scales to 70 min) → §9/§5; generic-retry-with-backoff as reliability doctrine → §6/§12; the `NN_`→`NN-` slug-prefix rule → §12.

### 21 June 2026 (evening) — THE SACRED SOAK LAUNCH
Stood up **Sacred Soak** (`@SacredSoak`), shipped Vol. 1 (33:28 Book-of-Enoch, 119 beats, Elliot). The thumbnail anchor doctrine (→ §7c + §9 #20): top-left default, bottom-left on collision — per-IMAGE; render both, Sonnet judges collision + legibility, fail to top-left on error. Kling-for-a-soak law (§12.3): gentle drift is free Ken-Burns. **★ THE ANTON FIX** (§6 + §12): no `shared/fonts/` on the box → silent DejaVu fallback portfolio-wide; commit `Anton-Regular.ttf` with `git add -f`. `make_thumb_bottomleft.py` gained `--title2`.

### 21 June 2026 — THE READ-SIDE SESSION
Built `dump_channel.py` — read-only metadata mirror, `--scheduled-only-summary` + `--cadence`. Caught the Lady Be Good orphan + a collision. → §5.10. Banked scale-vs-craft → §2A; analytics laws → §9 #14–#19; Amsterdam-time/golden-hour/Artlist gotchas → §12.

### 20 June 2026 — THE SATAN FLAGSHIP SESSION
Worst video (15.7% AVD) → strongest film. Flagship-rebuild method (§2b/§6b): worst-but-well-clicked = best raw material. MUSIC_LEVEL 0.07→0.040 via LUFS (measure the bed STEM at applied gain vs voice, not the final mix). Bottom-left flagship thumbnail (§7). Chapters from `audio_start`, never estimated. → #11b–#11f.

### 19 June 2026 — the batch-of-batches, music across four channels, thumbnail word-fit
Built `run_all_batches.py`. Music onto four channels (box-local). Thumbnail word-break fixed (`break_long_words=False`). First multi-channel scheduled run. Banked: slug rule; `--plan` doesn't catch slug errors; the `+02:00` summer trap; the render-vs-publish race. → §5.9, §6, §12.

### 17 June 2026 (evening) — audio-chain fixes, Prehistoric live, competitor benchmark
Three audio-chain bugs fixed (undefined `channel_dir`; `normalize=0`; per-channel `speakingRate`, 0.9). Toba + Chicxulub published. Wild Horizons benchmark (~218K floor, ~32-min avg → long-form). Quota now ~100/day. → §6, §9, §12.

### 17 June 2026 (day) — the Prehistoric Disasters channel, end to end
A channel from zero + three permanent pieces: thumbnail pipeline (Flux N=2 → Sonnet → locked overlay, scrim-not-global-darkening); unattended batch runner (`auto` gate + `--unattended` + `run_batch.py`); music into convergence (curated `--music-dir`). → §5.8, §6, §9.

### 16 June 2026 — motion root-fix + upload live across five channels
Fixed `default_motion` at source. Upload working (gustloff `wiykuEhTY1k`); OAuth → Production; five channels authed. → §5.3, §5.5, §5.7, §6, §12.

### 15 June 2026 — Mission Control v1.0 → v1.8
Nine patches. Audio→stills seam; the drift fix; panel persistence; reliability trio. → §5.6, §5.7.

### 13–15 June 2026 — Mission Control build arc + TIERED RENDER
TIERED RENDER proven on Enoch: Kling front-N / free Ken-Burns floor, ~$16.80/video at N=40. → §5.1–§5.4, §9.10.

### 12 June 2026 — Sacred Dawn ep2 + browser-pipeline decision
Ep2 (184 beats). Banked: `search_videos` corrupted — use `search_niche_finder_channels`.

### 8–9 June 2026 — You Had To Be There launch + pipeline hardening
Channel launched. Decade look-override Phase 1. Banked: un-filmable vs re-watchable; served vs searched; title↔thumbnail complement. → §9.

### 6–7 June 2026 — orchestrator + first-principles audio reset + second channel + music
Built `orchestrate.py`. One continuous voice track. Banked: resolve-identity-explicitly-fail-loudly.

### 5 June 2026 — Synthetic Press dual-mode pipeline
Built + box-proved the dual-mode pipeline.

### 3 June 2026 — Final Hours #7 + stills-review infrastructure
Shipped FH#7. Banked: Flux silent safety-reject (`safety_tolerance:"5"`); Override > Notes. → §6, §12.

---

_Older sessions (pre-3 June) live in the canonical reference and ante-machinam where they were absorbed._
