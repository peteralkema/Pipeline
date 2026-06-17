# _MASTER-WORKLOG.md — YouTube Media Flywheel

_The one living operational log. Solo operator (Peter, The Hague). All edits LAPTOP → GitHub → box; never hand-edit on box._
_Last updated: 17 June 2026._

---

## How to maintain this doc (read once)

This file replaces the pile of dated `SESSION-NOTES-*.md`. It has two halves:

1. **THE BACKLOG (front)** — everything still open, prioritised. This is the part you read at the start of a session and edit at the end. Move items up/down, tick them off, add new ones.
2. **THE RECORD (back)** — a compressed, reverse-chronological list of what shipped each session. One short block per session. A memory aid, not a working doc.

**The discipline that keeps this from rotting (this is the whole point):**
- **Durable lessons graduate OUT of here.** A reusable principle (a banked bug-class, a ground-truth fact, a strategy law) belongs in the **canonical reference** (the system) or **ante-machinam** (the craft) — not in a worklog entry. Before a session block ages out of THE RECORD, lift anything still true-and-reusable into the canonical/ante-machinam first, *then* compress the block to a one-liner.
- **THE RECORD is allowed to be lossy.** Once a lesson is in the canonical, its worklog block can shrink to a date + headline. Detail you might genuinely want later → spin a dedicated `SESSION-NOTES-<date>-<topic>.md` into an archive folder and link it from the block. That's the "occasional dedicated session note" — the exception, not the rule.
- **The test for "is this backlog or is it done?"** — *does the machine already do this for me?* If yes, it's not backlog; move it to THE RECORD.

---
---

# THE BACKLOG

_Standing read: the system is browser-only end to end, uploads from the browser across five channels on non-expiring auth, renders at a fixed ~$16.80/video (cinematic) or ~$3/video (Ken-Burns-only lanes), and now **runs a fully-unattended batch path** (scripts + thumbnail specs in → private videos out, scored and packaged). **The highest-leverage move is shipping real videos and letting first-48h CTR + AVD drive what to fix — not grinding this list.** Most of what's below is optional polish; Tier 1 is the only part that's truly "do next."_

## Live state / pending publish (operational, not backlog)
- **toba** (Prehistoric Disasters, "10 Prehistoric Disasters That Almost Ended Humanity", 88 beats, ~20.7 min) — rendered + thumbnailed + uploaded private via the batch runner, BUT **YouTube rejected it: "Processing abandoned — video too long."** The channel is unverified (15-min cap). **ACTION: verify the account (youtube.com/verify, phone), delete the abandoned upload, re-assemble with music (the render predated the music wiring), and re-run `upload_episode.py --project prehistoric-disasters/projects/toba`.** Then decide 88-beat vs the expanded ~28-min `toba-full.md` for the real publish.
- **gustloff** (Final Hours) — uploaded **private**, video ID `wiykuEhTY1k`. **ACTION: set Altered content = Yes in Studio before publishing.**
- **Esther** (Scripture on Screen, 119 beats) — rendered + downloaded; needs packaging/thumbnail/publish.
- **Enoch** (Sacred Dawn, 132 beats) — rendered; needs packaging + thumbnail.
- **70smusic** (You Had To Be There, 105 beats) — was `animating` at the 15 June session end. **ACTION: confirm it reached done and is publishable.**

## Tier 1 — Ship & verify (the real work)
1. **Verify the Prehistoric Disasters account + publish Toba** (see live state) — the one external gate between a proven pipeline and a live video. Then ship **Chicxulub as ep2** (slate #1, `prehistoric-slate-19.md`), and **read ep1 + ep2 first-48h CTR + AVD before authoring the other 18.** The machine made each at-bat cheap; let the data pick the batch order. Do NOT author 19 scripts blind.
2. **Prove dramatic motion end-to-end on a real render.** `cain-abel` (Sacred Dawn) is the clean test — the motion root-fix means its front Kling beats should read dramatic with zero hot-fix.
3. **Get the other pending-publish videos out** (gustloff disclosure, Esther/Enoch packaging) — rendered; the bottleneck is packaging, the layer that drives distribution.
4. **Add account-verification to the new-channel setup checklist** — the 15-min cap is a hard gate on EVERY new unverified channel; bake it in so the next channel doesn't hit "Processing abandoned" after a full render.

## Tier 2 — Correctness / safety still genuinely open
5. **Retire or guard `finish --assemble-only`.** It calls the alignment-UNSAFE `recreation_pipeline.assemble()` (positional zip, ignores `_index.json`, drifts). The Mission Control Re-assemble button now uses the aligned `assemble_episode.py`, but the unsafe path is still reachable from the CLI.
6. **Confirm `cmd_stills` passes `safety_tolerance:"5"` on the FIRST stills pass.** The Toba run produced 88 clean stills, which is strong evidence the batch first-pass gates it — but confirm in code and close this. (Without it, ~50% silent ~7KB black-PNG rejects can ship; the 3 June audit found 40/78.)
7. **`finish --plan` not side-effect-free** — mkdirs before the early-exit + CWD-relative path. Tiny.
8. **`proj_paths` auto-prefix latent bug** — auto-prepends `projects/` to a bare name; under the channel-folder architecture it builds the wrong path. Workaround: pass the full path.
9. **Inworld model-string reconcile** — doc said `inworld-tts-1.5-max`, code sets `INWORLD_MODEL = "inworld-tts-2"`. Verify against the box, fix whichever is stale.
10. **Inworld chunk-validation guard** — the PREVENTION half of the audio-QC pair (detection shipped 9 June). A failed/empty chunk should retry or hard-fail, not silently concatenate as dead air.

## Tier 3 — Console / cosmetic polish
11. **Mission Control thumbnail integration (the panel half of the thumbnail system).** Two linked builds: (a) capture thumbnail text (subject/title/subtitle → `thumbnail.json`) in the panel's create flow, alongside the script paste-box — so the panel path matches the batch path (which already pairs `.md` + `.thumb.json`); (b) show the generated thumbnail beside the final video with a regenerate/accept control at review time. Needs a panel grep. This is the manual-review-workflow equivalent of the stills gate and is arguably higher day-to-day value than more batch work.
12. **Tiered-aware strip label** — `phaseStrip` says "Animating clips (Kling)…" regardless of the split (wrong when Kling=0, all Ken Burns, which is now the Prehistoric default). Reflect Kling-≤N / Ken-Burns->N using `kling_count`.
13. **Move the Kling-count field into the always-visible controls strip.** Pairs with #12.
14. **`voice_id` cosmetic label** — audio gate prints "Victor" regardless of the resolved voice; read the real `voice_id`.
15. **Gate-button human/wire split remnants** — convert any remaining `go`/`keep`/`swap`/`skip` onclick verbs to human labels + wire values.
16. **Upload polish** — per-channel `channel.json` `upload` blocks for the channels lacking them; **schedule control: `upload_episode.py` already has `--schedule-cet-1am`/`--publish-at`; the batch runner should pass a per-project `publishAt` (Peter's design: every 6h from the latest video).** Rename the OAuth consent-screen app "Success Coach Upload Tool" → "Pipeline."
17. **Retire the redundant per-channel `auth.py` files** — superseded by `upload_episode.py --auth-only`. Harmless but drift-prone.

## Tier 4 — Bigger builds (deliberate, when justified by a shipped-video need)
18. **Faster final encode** — the Toba run spent ~20 min in the `-preset medium -crf 18` final concat/encode (CPU-bound, no GPU). For Ken-Burns lanes the source is already a soft pan over a still, so `-preset fast`/`veryfast` would roughly halve it with no visible loss. The single biggest batch-throughput lever (20 videos × ~20 min of encode = hours). One-word change in `assemble_episode.py`; tune + verify on one video first.
19. **Decade-look Phase 2 — the grade layer.** `film_emulate.py` does not exist. ffmpeg grade presets, single final grade pass into `assemble()`, fail-soft to ungraded.
20. **v2 motion routing** — route Kling-vs-Ken-Burns by which beats *earn* motion (duration/action), not the positional first-N split.
21. **Parallel fal animation** — bounded-concurrency semaphore (~5–10) could cut animation ~5–8×; matters on high-beat-count cinematic runs (moot on the Ken-Burns lanes).
22. **Batch orchestration polish** — the unattended batch runner SHIPPED (see THE RECORD 17 June). Remaining: per-project `publishAt` scheduling (pairs with #16); a re-run story (`ingest.create_project` refuses if the project already exists — fine as a safety default, but a partially-completed inbox can't be resumed without manual cleanup); optional parallelism (deliberately sequential now — no human watching, don't want N concurrent fal/Inworld bursts).
23. **Mode B within-card word-sync** (Synthetic) — thread each Mode B card its key word's Whisper timestamp.
24. **Mode B "design-on-page"** — banked big idea: a Mode B beat carries only words + duration + flag; pick the component on the review page.
25. **Synthetic Remotion component gaps** — NumberCounter countdown/plainYear; QuoteCard attribution-only variant.

## Tier 5 — Authoring discipline (bake into the craft doc, not code)
26. **Beat-granularity + runtime calibration bake-in** — "~5–12s/beat" stands, but the Toba run gave a REAL data point: 88 beats → 20.7 min, **~14s/beat once the Ken-Burns minimum hold applies** — beats run LONGER than the words-only ~195wpm estimate predicts, because short beats are stretched up to the clip floor. So a words-only runtime estimate UNDERSHOOTS; a ~28-min words-estimate script lands closer to ~40 min. Graduated to ante-machinam §6.
27. **Script-format-from-exemplar discipline** — graduated to ante-machinam Part VI (see THE RECORD 17 June). Author by copying a known-good script's structure, never from the doc's prose description.

## Banked-for-later / low (do not lose, do not prioritise)
- **review-server look patch** — `serve_review.py`'s 4-arg `generate_still` doesn't apply `resolve_look`; moot now Mission Control is the surface.
- **Multi-project / daemonized review server** (the :8001 legacy) — superseded by Mission Control. Keep the spec only as reference.

---
---

# THE RECORD (compressed, newest first)

_Each block: date · what shipped · what it left open (now tracked in THE BACKLOG above). Durable lessons have graduated to the canonical (§-refs) / ante-machinam; this is the index, not the detail._

### 17 June 2026 — the Prehistoric Disasters channel, end to end, fully unattended
A whole channel stood up and proven from zero in one session, plus three pieces of permanent infrastructure.

**Thumbnail pipeline (built, tuned, locked).** `make_thumbnail.py` (channel-resolved rewrite; two composition modes — `centered_subject` and `low_silhouette`), `select_thumbnail_still.py` (renders N=2 Flux candidates, Sonnet-4-6 vision picks the best *substrate* on CTR rules, fail-safe to candidate 1, logs the verdict), and `patch_convergence_thumbnail.py` (inserts `_maybe_thumbnail()` before `_maybe_upload()`). Per-project `thumbnail.json` carries subject/title/subtitle. Tuned by eye on a Sacred Dawn still as scaffold: the **left gradient scrim** replaced global darkening (the fix for the image washing out under the text — bank: darken only where the text lands, never the whole frame), then `darken_factor 1.0` / `vignette 0` (image at full brightness, scrim does the contrast), independent `margin_x`/`margin_y`, asymmetric `candidate_prompt_suffix` (catastrophe right two-thirds, dark empty left). The Sonnet selector picked correctly and for the right reason (clean top-left negative space). **LOCKED.** → canonical §6 (Thumbnails) + §5; durable principles graduated to canonical §9.

**Unattended batch runner (built, applied, proven).** Three patches: `patch_gate_auto.py` (adds a third gate-mode `auto` to `await_gate` — returns the accept default, no prompt/poll), `patch_orchestrate_unattended.py` (`--unattended` flag forces gate-mode=auto + live + normal so no gate or kickoff prompt blocks), and `run_batch.py` (for each `<name>.md` + `<name>.thumb.json` pair in an inbox: calls the REAL `ingest.create_project()` so batch projects are byte-identical to panel projects — incl. the wordless/no-VISUAL verify-refuse guard — then writes `render_policy.json` (`kling_count`) + `thumbnail.json`, runs the orchestrator unattended; sequential, per-project failure isolation, manifest log, `--plan` zero-spend preview). Orchestrator reads channel from the script HEADER, not a flag.

**Music into convergence (decided + wired).** The open Tier-4 decision resolved: **curated per-channel folder, NOT fal-generated.** `patch_music_dir.py` adds a `--music-dir` path to `assemble_episode.py` — picks N random tracks from `<channel>/music/`, crossfades the joins (`acrossfade`, default 2s), loops the sequence to fill the voiceover, feeds the EXISTING amix mux at VOICE 1.15 / MUSIC 0.07 untouched. `patch_convergence_musicdir.py` drives it from a `channel.json` `music` block (`{dir, tracks, crossfade_seconds, level}`). 8 ominous beds loaded; random-3 gives variance across renders. Tuned + approved by ear on the Toba clips. Now every render on a music-configured channel auto-scores.

**The channel.** Created `@PrehistoricDisasters` (display name "Prehistoric Disasters" — keyword-forward beats brandy for a packaging-first channel; repo slug `prehistoric-disasters`). OAuth authed via `upload_episode.py --auth-only` (the `_authstub` project-dir trick to satisfy the `is_dir()` check), correct channel picked at the chooser, token + client_secret scp'd to the box. Banner art generated (full-frame catastrophe collage, baked cracked-stone title — the one case where prompt-baked text won, since it reads as intentional). Locked `channel.json` (Victor voice, prehistoric `style_suffix`, Ken-Burns-only via `kling_count:0`, full thumbnail block, music block). Decided Ken-Burns-only for the lane (~$3/video) — packaging+topic+cadence carry these lanes, not motion.

**The end-to-end run.** Toba script (88 beats) → `--plan` clean → `--limit 1`: create_project → Victor audio → 88 Ken-Burns stills → assemble → Sonnet thumbnail → upload private. Landed in Studio with correct metadata + thumbnail, bound to the right channel. **The whole machine worked; only YouTube's 15-min cap stopped it** (unverified account → "Processing abandoned"). Real runtime: 88 beats = 20.7 min (calibration: ~14s/beat, longer than the words-only estimate — Tier-5 #26).

**Deliverables banked outside the box:** `prehistoric-slate-19.md` (ranked 19-topic authoring queue, deep-dive + listicle mix, silhouette ✅/⚠️ flags for human-era vs pre-human topics, Chicxulub = ep2), `toba-full.md` (expanded ~28-min version, held for the real publish pending the 88-beat-vs-expanded decision).

**Durable lessons graduated this session:**
- **Script-format-from-exemplar** (→ ante-machinam Part VI): author by copying a known-good script's exact structure (bare key:value header, `## COLD OPEN`/`## PART` double-hash sections, `[A] narration` then `VISUAL:` per beat), never from the doc's prose description. The first Toba draft used YAML fences + `#` headers + `NARRATION:` labels → parsed to ZERO beats (ZeroDivisionError). The reusable fix is a mechanical reformatter: keep the words, swap the markup to match a working script.
- **Runtime calibration** (→ ante-machinam §6): words-only runtime estimates undershoot; the Ken-Burns minimum hold stretches short beats, so real ≈ ~14s/beat.
- **The 15-min account cap** (→ canonical §12 + channel-setup): unverified YouTube accounts reject >15-min uploads at processing. Hard gate per new channel.
- **Thumbnail-as-paired-artifact** (→ canonical §6): design the thumbnail WITH the script (one authoring moment), but store it as a separate `thumbnail.json` (not the script header — the YouTube title and the thumbnail headline are different strings). The pair travels together; the separation is the architecture. Text never travels as a passed variable — it's written once at prep, read once at the end; nothing in the middle can corrupt it.
- **Scrim-not-global-darkening** (→ canonical §6): for legible text over a bright image, darken only the text zone with a directional gradient scrim; a global brightness multiply washes out the whole picture.

→ canonical roster (+Prehistoric Disasters), §5 (thumbnail + batch legs), §6 (thumbnails, music decided), §9 (packaging principles), §12 (gotchas).

### 16 June 2026 — motion root-fix + upload live across five channels
Fixed the `default_motion` dead-default at its true source (`modea_beats.py translate()` now omits motion on normal beats so the channel default fires) — proven `all dramatic: True` on Sacred Dawn. Upload went spec→working: `upload_episode.py` proven on a real private upload (gustloff `wiykuEhTY1k`); 7-day token expiry killed by publishing the OAuth app to **Production**; **five channels authed** with bindings verified; Mission Control **Upload button wired** (v1.9, private-only). Banked: the phantom `auth.py` swap bug doesn't exist; "no `modea/` folder = un-rendered project, not broken." → canonical §5.3, §5.5, §5.7, §6, §12.

### 15 June 2026 — Mission Control v1.0 → v1.8 (the big hardening session)
Nine patches. v1.0 audio→stills seam fix + decided-gate stale guard. v1.1 Re-assemble button. v1.2 **the drift fix** — Re-assemble through the ALIGNED `assemble_episode.py` (banked: two assemblers, only one honors `_index.json`). v1.3–1.5 FINAL VIDEO panel persistence (incl. the `api()` key-on-querystring 403 fix). v1.6–1.8 reliability trio: freshest-live-run by `started_at`; refuse duplicate launch (409); pid-liveness reaping. Doc set consolidated to two (canonical + ante-machinam v3.0). → canonical §5.6, §5.7; ante-machinam v3.0.

### 13–15 June 2026 — Mission Control build arc (v0.5 → v1.1) + TIERED RENDER
Built Mission Control into the full operator console. **TIERED RENDER** shipped + proven on Enoch (132 beats): Kling front-N / free Ken-Burns floor, fixed ~$16.80/video at N=40. Banked the front-loaded-effort-curve principle. → canonical §5.1–§5.4, §9.10.

### 12 June 2026 — Sacred Dawn ep2 (the-daughters) + browser-pipeline decision
Episode 2 (184 beats) end to end. Clickly thumbnail A/B locked (gold/white caps = the brand). **Decided the browser-driven pipeline** (became Mission Control). Banked: `search_videos` is corrupted — use `search_niche_finder_channels`; un-referenced-sublime as the channel filter.

### 8–9 June 2026 — You Had To Be There launch + pipeline hardening
Channel launched. Shipped: decade look-override Phase 1; audio-continuity QC at the gate; tunnel-free review server. Banked the durable strategy laws: spike-chasing doesn't suit this op; un-filmable vs re-watchable; served vs searched; title↔thumbnail complement; Vinny markup allowlist; ffprobe for true duration; Inworld ~190–200 wpm. → canonical §9.3–§9.8; ante-machinam.

### 6–7 June 2026 — the orchestrator + first-principles audio reset + second channel + music
Built the channel-agnostic `orchestrate.py`. First-principles reset: one continuous protected voice track; Mode B is a transformation of narration. Wired the convergence leg. Built Tier-2 music (`make_music.py`, standalone — now superseded by the curated `--music-dir` path, 17 June). Banked: resolve-identity-explicitly-fail-loudly. → canonical §5 (legs), §5 design law.

### 5 June 2026 — Synthetic Press dual-mode pipeline (Steps 1–4c)
Built + box-proved the dual-mode pipeline: `parse_script.py`, `dispatch.py`, Remotion Mode B, `modea_beats.py` + `_index.json`, dual-mode `assemble_episode.py`. The two engines meet only at assemble.

### 3 June 2026 — Final Hours #7 (KLM Tenerife) + stills-review infrastructure
Shipped FH#7. Built the stills-review system. Banked: **Flux silent safety-reject** (pass `safety_tolerance:"5"`); Override > Notes for hard corrections. → canonical §6, §12; ante-machinam.

---

_Older sessions (pre-3 June) live in the canonical reference and ante-machinam where they were absorbed; the dated `SESSION-NOTES-*.md` files can be moved to an `archive/` folder._
