# SESSION NOTES — 2026-06-11 (Documentation consolidation, 9-June code recovery, the Machina rename, per-channel doctrine docs)

*Destination: `shared/docs/SESSION-NOTES-2026-06-11-doc-consolidation-and-code-recovery.md`*
*Channels touched: all five (Final Hours, Sacred Dawn, You Had To Be There, Synthetic, Lazarus Films). Pipeline-wide infra: the repo itself. Success Coach: explicitly OUT of scope going forward.*
*Type of session: documentation + git hygiene + a significant uncommitted-code recovery. No renders, no fal/Inworld spend.*

---

## 0. ONE-PARAGRAPH SUMMARY

A documentation-consolidation session that turned out to also rescue load-bearing code. We reconciled the whole reference-doc set around the post-Sacred-Dawn reality (canonical reference, README, machina, dependency map), renamed the operational manual from PIPELINE_PLAYBOOK to **Machina** to pair with **Ante Machinam**, and verified the orchestrator dependency map edge-by-edge against the box. Mid-session, a routine `git status` revealed that **the entire 9-June pipeline-hardening session was still uncommitted on the box** — four modified source files (audio-continuity QC, look/era header keys, project-anchored config cache, tunnel-free review server) living in exactly one place with zero git backup. We captured, identified, committed, pushed, and re-synced that work first. Then we built the thing the day was really about: **five consolidated per-channel doctrine docs**, one per channel, each comprehensive, so the morning load-ritual is "four `_` system docs + one `_` channel doc." Everything is committed and synced across laptop → GitHub → box.

---

## 1. WHAT SHIPPED THIS SESSION (committed + synced to box)

### 1a. The reconciled system-doc set (commit `014903f`)
All five with the `_` load-first prefix, in `shared/docs/`:
- **`__PIPELINE-CANONICAL.md`** — umbrella, updated: Sacred Dawn added as live channel #5; the **un-referenced-sublime** filter promoted to a flywheel-level channel-selection test (§9.3b); ante-machinam v2.0 + Constitution §7 (animatable foreground) threaded through; the `voice_id`-snake_case trap, cosmetic-"Victor"-label, tmux + `finish --animate-only` recovery, and corrupted-`search_videos` caveat all banked into §5/§6/§7/§12; current-state + backlog refreshed to 11 June with the corrected motion-direction #1 item.
- **`_ante-machinam.md`** — v2.0 (the pre-machine bible; absorbed the former `script-craft-principles.md` as Part IV; carries the Constitution incl. §7 animatable-foreground, the VISUAL-line patterns, the craft canon, the channel briefs, the threshold). *(Carried in from the prior session; re-confirmed as canonical here.)*
- **`_machina.md`** — the renamed PIPELINE_PLAYBOOK (see §3 below), 752 lines, all four craft-reference edits applied.
- **`_README.md`** — the doc-set map, updated to the flywheel umbrella + ante-machinam-as-bible + Sacred-Dawn-live + script-craft retirement.
- **`_ORCHESTRATOR-DEPENDENCY-MAP.md`** — v3.1, every edge confirmed in source on the box (see §4).

### 1b. The recovered 9-June code (commit `286fb85`) — THE IMPORTANT ONE
Four source files, 79 insertions, that were modified on the box on/around 9 June and **never committed**:
- `shared/audio_leg.py` (+14) — audio-continuity QC wiring (`from audio_qc import audio_continuity_check` at line 158, runs at the audio gate, read-only, fails soft).
- `shared/parse_script.py` (+2/-1) — added `look` and `era` to `HEADER_KEYS` (the decade-look header plumbing).
- `shared/recreation_pipeline.py` (+38) — project-anchored config: `_CHANNEL_CACHE` global → dict keyed by resolved channel dir; `load_channel_config(strict, anchor)`. The root-cause fix for the wrong-voice bug.
- `shared/serve_review.py` (+43) — tunnel-free review server: `--host` / `--key`, `_key_ok()` enforcing the key on all but `/stills/` + `/api/health`, and a guard that **refuses public bind without `--key`** (the server is fal/Claude spend-capable).

### 1c. The Sacred Dawn creed (recovered + committed)
`shared/docs/sacred-dawn-creed.md` (22,584 bytes) — written launch-night, had never been moved into the repo. Recovered and pushed this session. (Subsequently superseded by the consolidated `_Sacred-Dawn.md` — see §2.)

### 1d. The five consolidated per-channel doctrine docs (BUILT this session; PENDING push — see §6)
In `/mnt/user-data/outputs/`, named per Peter's list, all `_`-prefixed:
- `_Lazarus-Films.md` (168 lines)
- `_Synthetic.md` (185 lines)
- `_Final-Hours.md` (127 lines)
- `_Sacred-Dawn.md` (192 lines)
- `_you-had-to-be-there.md` (181 lines)

---

## 2. THE PER-CHANNEL DOCTRINE DOCS — design decisions (the day's headline deliverable)

**The problem identified:** the five `_` system docs describe how the *machine* works but carry no *channel-specific* state — every session is about a channel, and the system docs don't tell a fresh Claude what's next for the channel in focus. Peter's fix: one consolidated doc per channel, load-on-demand, so the morning ritual is **four system docs + one channel doc**.

**Consolidation rules agreed (via elicitation):**
1. **Merge everything, lose nothing** — where sources overlapped/conflicted (Final Hours had two backlogs; Lazarus two strategy docs; Synthetic four docs), fold all content in rather than prune.
2. **Correct to current reality, flag the change** — stale facts get fixed inline with a `[CORRECTED]` / `[flag]` marker, not silently and not left wrong.
3. **Comprehensive length** (~creed length, 180+ lines target).

**Naming convention banked:** the `_` prefix = "floats to the top of `shared/docs/`." Peter loads **the four system docs + the one relevant channel doc** each morning. (Earlier in the session we'd debated whether channel docs should be un-prefixed; Peter's final call is `_`-prefix ALL of them for the sort-to-top behaviour, and rely on his own discipline to load only the relevant one. Both the system and channel docs therefore share the `_` prefix — the distinction is in his head, not the filename.)

**Each consolidated doc's source → what it retired:**
- **`_Sacred-Dawn.md`** ← the launch-night creed. Already comprehensive single-source; added the convention header and flagged the "film series → cinematic recreation" positioning correction (the live About copy leads with "cinematic recreation").
- **`_you-had-to-be-there.md`** ← the v1.2 launch/operating doc **+** the 9-June gaming-series session notes. Folds in the two-audience model, the Vinny register + markup law, the **decade-look system** (the channel's signature pipeline feature), the measured **~195 wpm**, the batched-job lesson, the 19-title backlog, the strategic learnings (spike-chasing doesn't suit us; un-filmable vs re-watchable; served vs searched).
- **`_Final-Hours.md`** ← `final-hours-strategy.md` **+** both backlogs (30 & 31 May). **Corrected stale facts with flags:** 7-min/84-beat fixed grid → long-form 12–16 min (city-catastrophe 20–32); Kraków → The Hague; box now live; face-never-resolved adopted as default; Troy episode in flight (incl. the beat-107 Laocoön TTS-drop follow-up). Preserved the rulebook/canon/three-attempts moat, the distribution principles, the candidate-topic queue, and the Hindenburg-vs-Pudding-Lane retention experiment.
- **`_Lazarus-Films.md`** ← the festival/PD strategy doc **+** the apprenticeship-curriculum doc. Everything kept: the five-year-curriculum thesis + author→technique table, the eight-question filter, the four-cohort PD taxonomy, the Tony Walker calibration + near-empty-lane finding, the register-expansion roadmap, the three-film sequence (Sredni Vashtar → Maltese Falcon → Loving Spirit), the du Maurier multi-year runway, the "channel owns the frame / film owns the interior" override principle, and the Samuelson framing. Flagged: designed-not-built; Astana 15-Aug deadline to **re-verify**.
- **`_Synthetic.md`** ← four docs: launch-strategy (v4) + OpenAI-series (v3) + Mode-B notes (v1.0) + visual-architecture. The biggest merge. Kept the confluence thesis (doom + exposé neighborhoods, the Hao bridge), the format-gap moat, the packaging doctrine, the full two-mode architecture (six Mode B components, the two-layer timing model, audio-as-truth spine, the Whisper matcher, "the spoken line and its receipt," the archival preference-order), and the complete 6-part OpenAI series with the trial frame + E1 cold open + E1 packaging spectrum. Flagged: launching / 4c-open / no OAuth; the `channel: synthetic` alias trap; and that the 9-component navy/amber palette draft was superseded by the 6-component indigo prototype actually built.

**To retire once the five are on the box (11 source docs):** `final-hours-strategy.md`, `backlog.md`, `final-hours-backlog.md`, `lazarus-films-festival-and-pd-strategy.md`, `lazarus-films-curriculum.md`, `synthetic-launch-strategy.md`, `synthetic-openai-series.md`, `synthetic-press-modeb-notes.md`, `synthetic-press-visual-architecture.md`, `you-had-to-be-there_LAUNCH-DOC.md`, `sacred-dawn-creed.md`.

---

## 3. THE MACHINA RENAME (PIPELINE_PLAYBOOK → machina.md)

**Decision:** the operational manual is renamed **Machina** ("the machine") to pair with **Ante Machinam** ("before the machine"). Clean symmetry: the pre-write bible and the operational machine reference as a matched set.

**The four craft-reference edits applied** (script-craft-principles.md was retired into ante-machinam Part IV at v2.0, so the playbook's pointers had to follow):
1. Top "source of truth" line → declares Machina the *operational* layer, points to ante-machinam Part IV (craft) + Part VI (threshold).
2. Step 3 → references `ante-machinam.md` Part IV (craft canon) + Part V (per-channel register) + the IV.7 pre-lock audit.
3. Architecture tree → `script-craft-principles.md` marked `RETIRED → stub → ante-machinam.md Part IV`.
4. PART 2D Mode B note → points to ante-machinam Part II; corrected "silent cards carry zero" → "silent cards no longer exist (a wordless beat halts the build, Constitution §1)."

Also folded in: the Mode-A leg PROVEN-LIVE status (Sacred Dawn), the `finish --animate-only` recovery + tmux discipline, the voice-sounds-wrong entry with the `voice_id` snake_case trap + cosmetic "Victor" label, and Hetzner-DONE.

**Flagged, not done (bigger reconciliation, banked):** Machina PART 1/2 still stack two eras of workflow — the pre-orchestrator laptop-era 12-step (`recreation_pipeline.py` direct calls, `upload.py`, `channel-3`, venv-named-success-coach) on top of the `orchestrate.py` era (PART 2C/2D). Wants a dedicated reconciliation pass someday.

---

## 4. THE DEPENDENCY MAP — verified edge-by-edge (v3.1)

Updated `_ORCHESTRATOR-DEPENDENCY-MAP.md` from the v2 (7 June) to v3 (convergence proven live, look resolver, audio QC, make_music, review.py rename, Sacred-Dawn reality) — then **confirmed all four inferred edges by grep on the box** and promoted them to v3.1. The greps + findings:

- `grep -rn "look_resolver" shared/*.py` → **imported inside the engine at `recreation_pipeline.py:532`**, NOT in `modea_leg.py`. The look resolves inside the stills step (so any caller of `recreation_pipeline.py stills` gets it for free). I had placed it on the leg; corrected.
- `grep -rn "audio_qc" shared/*.py` → **standalone module, imported by `audio_leg.py:158`**. Confirmed as drawn.
- review server: the live Mode A gate calls **`review.py`** (`modea_leg.py:195`). **`serve_review.py` is NOT dead** — it's the older v1 server still used by the **Mode B gate** (`modea_leg.py:181`) and lingering in **stale comments** (`modea_leg.py:10, 38-39`). Two servers, both live; the stale comments are a cleanup target, not a missing file.
- `grep -rn "make_episode_vo\|narration_assembler"` → **NOT legacy.** Both are the **Synthetic 4c dual-mode audio scaffolding** (file headers: "Piece 2, step 1/2 of Synthetic 4c"). `narration_assembler.py` → `make_episode_vo.py` is the *not-yet-wired dual-mode* sibling of the live single-mode path (`build_audio_script.py` → `generate_episode_vo.py`). Parallel, not dead.

**Result: v3.1 has zero inferred edges** — every program and arrow confirmed in source. §10 carries the #1 coupled backlog change (per-shot motion-direction field across `review.py` + storyboard schema + `animate_still`) with exact read-first commands.

**The trap this verification protects against (banked twice now):** an apparently-orphaned file is often a live parallel path. `serve_review.py` *looked* dead (superseded by `review.py`) but serves Mode B; `make_episode_vo.py` *looked* legacy but is the dual-mode sibling. The map now flags both as live-but-parallel so future-Peter doesn't garbage-collect working code. The one genuine strip remains noted: `categorise_empty` silent-beat detection inside `narration_assembler.py` (silent beats no longer exist per Constitution §1).

---

## 5. THE 9-JUNE CODE RECOVERY (the most important thing that happened) — a process post-mortem

**What happened:** while preparing to push the docs, a `git status` on the box showed four modified source files and HEAD still at `25f1c00` (the Sacred Dawn commit). The docs hadn't been pushed yet — but more importantly, the four modified files were **the entire 9-June pipeline-hardening session, uncommitted.** The docs we'd just written *describe these features as shipped* ("look resolver shipped 9 June," "audio QC built," "project-anchored config") — but the code implementing them had never left the box's working tree. One `git checkout .` and it was gone.

**How we handled it (the right order):**
1. **Capture before analysis** — `git diff … > ~/box_uncommitted_20260611.patch` (227 lines) so the work was safe outside the working tree no matter what git did next.
2. **Identify before committing** — read all four diffs. Confirmed they were real, finished, recognizable feature work (not debug noise): the QC import, the header keys, the cache refactor, the auth'd public server with its spend-guard.
3. **Commit from the box (a justified one-time exception** to laptop→box direction, because the work existed *only* on the box) → push → **pull on the laptop to re-sync.** Commit `286fb85`.

**Why it nearly happened / the systemic lesson:** the 9-June session built and *ran* the code (it works — it's been running on the box for two days), wrote the patch scripts (`patch_decade_look_phase1.py`, `patch_audio_gate_continuity.py`, `patch_serve_review_public.py` are all present), and updated the docs — but never ran the final `git add/commit/push`. The docs silently became the only record. **The discipline banked: anything generated or built that you want to keep gets committed + pushed in the SAME session. Chat output is a draft; the box working tree is a draft; only the pushed repo is truth.** This session hit the same pattern twice more (the Sacred Dawn creed; almost the per-channel docs) — it's a recurring failure mode, not a one-off.

**Side note — `.gitignore` is now justified:** the box's `git status` is noisy with pipeline outputs (`_index.json`, `engine_beats.json` per project) and stray binaries (`sacred-dawn/Presentation4.pptx`, `the-watchers/*.png`). That noise is exactly how uncommitted real work hides. A few ignore lines (`**/_index.json`, `**/engine_beats.json`, `*.pptx`, `**/projects/**/*.png`, `*.bak*`, `*.pre_*`) would make `git status` legible again. Banked, not urgent.

---

## 6. GIT STATE AT SESSION END

- **Laptop, GitHub, box are in sync** through commit `014903f` (docs) on top of `286fb85` (recovered code) on top of `25f1c00` (Sacred Dawn).
- The five `_` system docs + `sacred-dawn-creed.md` are committed and confirmed present on the box (`ls -la shared/docs/_*.md` shows all five; `git ls-files` confirms tracking).
- **PENDING push:** the five consolidated per-channel doctrine docs (`_Lazarus-Films.md`, `_Synthetic.md`, `_Final-Hours.md`, `_Sacred-Dawn.md`, `_you-had-to-be-there.md`) — built this session, sitting in chat outputs, **need the download → laptop → commit → push → box pull cycle.** (Apply the §5 lesson: do it before the next render session, and `git rm` the 11 retired source docs in the same commit.)
- The `box_uncommitted_20260611.patch` safety file remains in `~` on the box — can be deleted once `286fb85` is confirmed (it is).

---

## 7. KEY DECISIONS & PRINCIPLES BANKED THIS SESSION

1. **Per-channel doctrine doc model.** Morning load = four `_` system docs + one `_` channel doc. Each channel doc is the consolidated, comprehensive, current-state-flagged single source for that channel (backlog + competitor strategy + design thinking + the pipeline features specific to it).
2. **Machina / Ante Machinam naming pair.** "The machine" (operations) + "before the machine" (craft). script-craft-principles.md is retired into ante-machinam Part IV.
3. **Commit-in-the-same-session discipline** (the §5 lesson) — the real moat is banking work into the *pushed repo*, not leaving it in working trees or chat outputs.
4. **Apparently-dead files are often live parallel paths** — verify before deleting (`serve_review.py`, `make_episode_vo.py`).
5. **A dependency map must be honest about what it has actually re-read** — flag inferred edges, then settle them with one grep each. v3.1 has none left.
6. **Correct-and-flag over silent-correct** for stale doc facts — the reader sees both the current reality and that it changed (Final Hours' 7-min→long-form, Kraków→The Hague).
7. **Success Coach is out of scope.** Five channels is the deliberate ceiling; no sixth, no immediate Success Coach work. (Noted so future sessions don't re-expand focus.)

---

## 8. NEXT-SESSION TODO (carry-forward)

**Immediate (git hygiene, do first):**
- Push the five consolidated channel docs (download → `~/Projects/Pipeline/shared/docs/` → `git add` → commit → push → box pull).
- In the same commit, `git rm` the 11 retired source docs (§2 list).
- Optional but recommended: add the `.gitignore` (§5) so `git status` stops hiding real work.
- Tiny: patch the creed's §0/§1 "film series" → "cinematic recreation" wording (already flagged in the consolidated doc; the standalone `sacred-dawn-creed.md` is retired anyway).

**Pipeline backlog (unchanged priority — all in the channel docs + machina + dependency map):**
1. **Per-shot motion-direction field** on the stills-review page → Kling prompt (the #1 coupled change; read-first commands in dependency-map §10). Do after seeing default motion on the gaming series.
2. **Music** — decide generated (`make_music.py`, needs `.env` sourcing) vs curated Jamendo; wire into convergence. Matters most for You Had To Be There.
3. **Channel-agnostic upload step + batch exit-gate** — single-video jobs auto-upload; batched jobs exit at `final_video.mp4`. Until built, uploads are manual (category Entertainment, add tags).
4. **Auto-launch the review server** in the Mode A leg (kill stale `:8001`, tear down on `go`); fix the stale tunnel instructions in the gate banner; resolve the per-job look in the review-server restill path.
5. **Decade-look Phase 2** — write+commit `film_emulate.py` grade presets, wire one pass into `assemble()`.
6. **Kill hardcoded voice/gate labels** (the leg prints "Victor" regardless of resolved `voice_id`); wire the dead `speed` key; chunk-validation guard.
7. **Machina PART 1/2 reconciliation** (the two stacked workflow eras).

**Channel-specific next actions (from the consolidated docs):**
- **Final Hours:** Troy morning stills-review gate → `go` → assembly; regenerate beat-107 (Laocoön) voiceover.
- **Sacred Dawn:** watch first-48h CTR on "ANGELS OR GIANTS?" + retention shape → decides episode 2 (recommended E2: "The Giants Who Ruled the Earth Before the Flood"). Add a Sacred Dawn brief to ante-machinam Part V once retention data is in.
- **You Had To Be There:** decide ship-four-~5min vs double-the-scripts for the gaming series; upload the batch manually (Entertainment + tags); episode-2 beat-granularity fix (~2,200 words / split the long stretched beats).
- **Synthetic:** the E1 packaging test (5–6 title/thumbnail concepts across doom→exposé→neutral); re-verify the Musk-verdict facts at scripting time.
- **Lazarus:** gated on Phase 2 (hierarchical scenes + variable shot duration) + the dialogue/lip-sync legs; re-verify the Astana deadline before committing.

---

## 9. WHAT THIS SESSION DID NOT TOUCH

No renders, no fal/Inworld/Kling spend, no script writing, no NexLev pulls. No box code was hand-edited *this* session (the four recovered files were edited on 9 June; we only committed them). The work was entirely documentation reconciliation + git recovery + the per-channel consolidation.

---

*Session end. The documentation layer now matches the machine, the 9-June code is safe in git, the rename loop is closed (Machina/Ante Machinam), the dependency map is fully verified, and each channel has one comprehensive doctrine doc for the morning load-ritual. The single open thread is pushing the five channel docs — first task next session.*
