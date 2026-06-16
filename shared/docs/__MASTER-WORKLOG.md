# _MASTER-WORKLOG.md — YouTube Media Flywheel

_The one living operational log. Solo operator (Peter, The Hague). All edits LAPTOP → GitHub → box; never hand-edit on box._
_Last updated: 16 June 2026._

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

_Standing read: the system is browser-only end to end, uploads from the browser across five channels on non-expiring auth, and renders at a fixed ~$16.80/video. **The highest-leverage move is shipping real videos and letting first-48h CTR + AVD drive what to fix — not grinding this list.** Most of what's below is optional polish; Tier 1 is the only part that's truly "do next."_

## Live state / pending publish (operational, not backlog)
- **gustloff** (Final Hours) — uploaded **private**, video ID `wiykuEhTY1k`. **ACTION: set Altered content = Yes in Studio before publishing.**
- **Esther** (Scripture on Screen, 119 beats) — rendered + downloaded; needs packaging/thumbnail/publish.
- **Enoch** (Sacred Dawn, 132 beats) — rendered; needs packaging + thumbnail.
- **70smusic** (You Had To Be There, 105 beats) — was `animating` at the 15 June session end. **ACTION: confirm it reached done and is publishable.**

## Tier 1 — Ship & verify (the real work)
1. **Prove dramatic motion end-to-end on a real render.** `cain-abel` (Sacred Dawn, new project, no storyboard yet) is the clean test — the motion root-fix means its front Kling beats should read dramatic with zero hot-fix. First shipped video that demonstrates the fix.
2. **Apply the canonical-update patch** (`patch_canonical_2026-06-16.py`, written this session, pending apply on the laptop) — brings the canonical to 16 June / v1.9. Then the canonical and this worklog agree.
3. **Get the pending-publish videos out** (gustloff disclosure, Esther/Enoch packaging) — they're rendered; the bottleneck is packaging, which is the layer that actually drives distribution.

## Tier 2 — Correctness / safety still genuinely open
4. **Retire or guard `finish --assemble-only`.** It calls the alignment-UNSAFE `recreation_pipeline.assemble()` (positional zip, ignores `_index.json`, drifts). The Mission Control Re-assemble button now uses the aligned `assemble_episode.py`, but the unsafe path is still reachable from the CLI. Either route it through `assemble_episode.py` too, or have it refuse with a pointer.
5. **Confirm `cmd_stills` passes `safety_tolerance:"5"` on the FIRST stills pass.** The restill path does; the batch first-pass was an open question. Without it, ~50% silent ~7KB black-PNG rejects can ship (the 3 June audit found 40/78). *(Per the code read this session, `generate_still` does gate `safety_tolerance:"5"` to flux — verify the batch path actually hits it on pass one and close this.)*
6. **`finish --plan` not side-effect-free** — mkdirs before the early-exit + CWD-relative path (must run from `…/projects`). Tiny.
7. **`proj_paths` auto-prefix latent bug** — auto-prepends `projects/` to a bare name only if a top-level `projects/` exists in cwd; under the channel-folder architecture it builds the wrong path (caused the the-daughters resume crash). Workaround: pass the full path. Unify with orchestrate's resolution.
8. **Inworld model-string reconcile** — canonical/code disagree: doc said `inworld-tts-1.5-max`, code sets `INWORLD_MODEL = "inworld-tts-2"`. Verify against the box, fix whichever is stale.
9. **Inworld chunk-validation guard** — the PREVENTION half of the audio-QC pair (detection shipped 9 June). A failed/empty Inworld chunk should retry or hard-fail, not silently concatenate as dead air (the root of the Xennials 44-second hole).

## Tier 3 — Console / cosmetic polish
10. **Tiered-aware strip label** — `phaseStrip` says "Animating clips (Kling)…" regardless of the split (fully wrong when Kling=0, all Ken Burns). Reflect Kling-≤N / Ken-Burns->N using `kling_count`.
11. **Move the Kling-count field into the always-visible controls strip** — currently only at the stills gate, breaking the "everything always visible, just disabled when not usable" rule. Pairs with #10 (both need N on the page).
12. **`voice_id` cosmetic label** — audio gate prints "Victor" / "the channel voice" regardless of the resolved voice; read the real `voice_id`.
13. **Gate-button human/wire split remnants** — convert any remaining `go`/`keep`/`swap`/`skip` onclick verbs to human labels + wire values (keeps CLI tokens out of served HTML — also dodges the quote-break class).
14. **Upload polish** — per-channel `channel.json` `upload` blocks (category/privacy) for the four channels lacking them (default cat-24/private is fine); a schedule/visibility control on the panel (`upload_episode.py` already has `--schedule-cet-1am`/`--publish-at`); **rename the OAuth consent-screen app from "Success Coach Upload Tool" → "Pipeline."**
15. **Retire the redundant per-channel `auth.py` files** (`final-hours/auth.py`, `success-coach/auth.py`) — superseded by `upload_episode.py --auth-only`. Harmless but drift-prone (they've already diverged by hand).

## Tier 4 — Bigger builds (deliberate, when justified by a shipped-video need)
16. **Music — decide + wire.** `make_music.py` exists (Claude writes one loopable instrumental prompt → fal ElevenLabs → `music.mp3`) but is standalone, **not wired into convergence**. Decide generated vs curated Jamendo (Final Hours/Sacred Dawn use Jamendo at VOICE 1.15 / MUSIC 0.07) and wire the chosen path. Matters most on nostalgia/Sacred-Dawn content. (`make_music.py` also needs `load_dotenv()` added when next touched.)
17. **Decade-look Phase 2 — the grade layer.** `film_emulate.py` **does not exist** (Phase 1 stills-look shipped 9 June). Write + commit it with ffmpeg grade presets (`super8_70s`, `sixteen_mm_50s/60s`, `vhs_80s`, `hi8_90s`, `digicam_2000s`), wire a single final grade pass into `assemble()`, fail-soft to ungraded. Gives the VHS/Hi8 texture the Flux `style_suffix` only approximates.
18. **v2 motion routing** — route Kling-vs-Ken-Burns by which beats *earn* motion (duration/action), not the positional first-N split (which can spend Kling on long contemplative holds and floor short kinetic beats).
19. **Parallel fal animation** — bounded-concurrency semaphore (~5–10) could cut animation ~5–8×; matters most on high-beat-count runs (the 184-clip the-daughters leg, the 105-beat 70smusic). Free (box isn't the bottleneck; Kling runs remote).
20. **Batch orchestration split** — split the orchestrator at the stills-review seam into unattended prep (→ stills) + unattended finish (back half), async review between, per-project failure isolation, sequential-unattended (not parallel).
21. **Mode B within-card word-sync** (Synthetic) — the on-screen word lags the spoken word ~3s; the card animates on a hardcoded internal timeline. Whisper `voiceover.json` has each word's exact time — thread each Mode B card the timestamp of its key word and fire the sweep/count/reveal at that frame. Highest-value Mode B quality fix.
22. **Mode B "design-on-page"** — banked big idea: a Mode B beat carries only its spoken words + duration + "this is Mode B" flag; pick the component and finalise content on the review page. Deletes `shape_props`/component-registry from dispatch + `[B:Component]` from parse_script; turns the Mode B review into a design tool.
23. **Synthetic Remotion component gaps** (pre-publish for Synthetic) — NumberCounter countdown (renders 0→44M not $1B→$44M); NumberCounter plainYear (renders "1,997" not 1997); QuoteCard attribution-only/highlight variant (no-karaoke doctrine). None block the pipeline; each makes one beat render as scripted.

## Tier 5 — Authoring discipline (bake into the craft doc, not code)
24. **Beat-granularity bake-in** — "~8–12s/beat, ~90–110 beats for a ~20-min film; hard ceiling ~55 words, split longer." This is the upstream fix for the old Synthetic shot-density problem (a single still can't hold 30s). Belongs in ante-machinam.

## Banked-for-later / low (do not lose, do not prioritise)
- **review-server look patch** — `serve_review.py`'s own 4-arg `generate_still` doesn't apply `resolve_look`; regenerated stills on the legacy :8001 path ignore the per-job look. Largely moot now that Mission Control is the surface; close when the legacy server is formally retired.
- **Multi-project / daemonized review server** (the :8001 legacy) — **effectively superseded by Mission Control (:8002).** Keep the spec only as a reference; don't build.

---
---

# THE RECORD (compressed, newest first)

_Each block: date · what shipped · what it left open (now tracked in THE BACKLOG above). Durable lessons have graduated to the canonical (§-refs) / ante-machinam; this is the index, not the detail. Full dated notes archived where a deeper trace is worth keeping._

### 16 June 2026 — motion root-fix + upload live across five channels
Fixed the `default_motion` dead-default at its true source (`modea_beats.py translate()` now omits motion on normal beats so the channel default fires; sentinel `motion omitted when not face-hold`) — proven `all dramatic: True` on Sacred Dawn. Upload went spec→working: `upload_episode.py` proven on a real private upload (gustloff `wiykuEhTY1k`); 7-day token expiry killed by publishing the OAuth app to **Production**; **five channels authed** (Final Hours, Sacred Dawn, You Had To Be There, Synthetic Press, Scripture On Screen) with bindings verified; Mission Control **Upload button wired** (v1.9, private-only). Banked: the phantom `auth.py` swap bug doesn't exist; "no `modea/` folder = un-rendered project, not broken." Canonical-update patch written (pending apply). → canonical §5.3, §5.5, §5.7, §6, §12.

### 15 June 2026 — Mission Control v1.0 → v1.8 (the big hardening session)
Nine patches. v1.0 audio→stills seam fix + decided-gate stale guard (healthy stills run no longer false-stales). v1.1 Re-assemble button. v1.2 **the drift fix** — Re-assemble routed through the ALIGNED `assemble_episode.py` (banked: two assemblers, only one honors `_index.json`). v1.3/1.4/1.5 FINAL VIDEO panel persistence (incl. the `api()` key-on-querystring 403 fix). v1.6/1.7/1.8 reliability trio A/B/C: freshest-live-run by `started_at`; refuse duplicate launch (409, one live run global); pid-liveness reaping of dead records. Recovered a stranded 70smusic run by hand (the crisis that drove A/B/C). Doc set consolidated to two (canonical + ante-machinam v3.0; machina + README → stubs). → canonical §5.6, §5.7; ante-machinam v3.0.

### 13–15 June 2026 — Mission Control build arc (v0.5 → v1.1) + TIERED RENDER
Built Mission Control from stills-review into the full operator console: live status line, version stamp, A1 heartbeat + false-hang fix, FINAL VIDEO panel (autoplay + Download), two-column top, single-continuous-page refactor (dissolved the dead-run/skip/done display bugs), five-column storyboard gate (text·still·controls·motion·clip), per-request restill/aifix/animate endpoints, fire-and-poll for slow Kling calls, motion-direction field + `/api/motion` persistence. **TIERED RENDER** shipped + proven on Enoch (132 beats): Kling front-N / free Ken-Burns floor, fixed ~$16.80/video at N=40. God-as-light rendered on-doctrine. Banked the front-loaded-effort-curve principle. → canonical §5.1–§5.4, §9.10.

### 12 June 2026 — Sacred Dawn ep2 (the-daughters) + browser-pipeline decision
Episode 2 (184 beats, ~33 min) researched → scripted → 184 stills → reviewed → animated. Clickly thumbnail A/B locked (gold/white caps system = the brand; pose is spent). Fixed the review-server 403 (key only read from querystring; added `X-Review-Key` header). Found the `proj_paths` auto-prefix bug (Tier-2 #7). **Decided the browser-driven pipeline** (became Mission Control). Banked: `search_videos` is corrupted — use `search_niche_finder_channels`; Kling content-policy auto-fallback to held still; un-referenced-sublime as the channel filter.

### 8–9 June 2026 — You Had To Be There launch + pipeline hardening
Channel launched ("10 Things '70s Parents Did…", Vinny, 8.7 min). Shipped: decade look-override Phase 1 (`look_resolver.py`, stills layer); audio-continuity QC at the gate (the 44-second-hole guardrail, detection half); tunnel-free review server (public bind + token auth). Banked the durable strategy laws: spike-chasing doesn't suit this op; un-filmable vs re-watchable; served vs searched; title↔thumbnail complement not echo; Vinny markup allowlist; ffprobe (not the player) for true duration; Inworld ~190–200 wpm. → canonical §9.3–§9.8; ante-machinam.

### 6–7 June 2026 — the orchestrator + first-principles audio reset + second channel + music
Built the channel-agnostic `orchestrate.py` (leg-based: audio → modeB → modeA → convergence), proven on a second channel (Final Hours test) which surfaced the channel-name↔folder hyphen/underscore class bug (fixed). **First-principles reset:** silence is not an object — one continuous protected voice track; Mode B is a transformation of narration, never an addition (the Lego rule). Cleanup patches 1–5 deleted all the hold/silence-fabrication machinery; e2e validated on a 6-beat script. Wired the convergence leg (auto-assemble → final_video). Built Tier-2 music (`make_music.py`, standalone). Banked: resolve-identity-explicitly-fail-loudly (the REMOTION_DIR/node-PATH/voice_id class). → canonical §5 (legs), §5 design law.

### 5 June 2026 — Synthetic Press dual-mode pipeline (Steps 1–4c)
Built + box-proved the dual-mode pipeline: `parse_script.py` (tagged beats + header), `dispatch.py` (A/B routing), real Remotion Mode B render, `modea_beats.py` translator + `_index.json` shot→beat map (the convergence keystone), per-channel resolution, and the whole-episode audio spine + dual-mode `assemble_episode.py`. Decoupled architecture: the two engines meet only at assemble. Banked the shot-density problem (long beats need sub-slicing → now handled by authoring discipline, Tier-5 #24).

### 3 June 2026 — Final Hours #7 (KLM Tenerife) + stills-review infrastructure
Shipped FH#7 (long-form). Built the stills-review system (`make_review_page.py`, `serve_review.py`, `restill_from_feedback.py`) with Notes + Override modes. Banked the foundational discoveries: **Flux silent safety-reject** (default tolerance returns ~7KB black PNGs; pass `safety_tolerance:"5"`; 40/78 stills were silent rejects); the under-200KB audit; trigger-word vocabulary; the httpx `verify=False` monkey-patch (Mac SSL); Override > Notes for hard corrections (Flux early-token bias). Mary Celeste analytics → long-form is the Final Hours format. → canonical §6, §12; ante-machinam (VISUAL patterns).

---

_Older sessions (pre-3 June) and the original `PIPELINE_PLAYBOOK.md` / `script-craft-principles.md` content live in the canonical reference and ante-machinam where they were absorbed; the dated `SESSION-NOTES-*.md` files can be moved to an `archive/` folder — their durable content is captured above and in the two living docs._
