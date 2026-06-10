# SESSION NOTES — 2026-06-09 (You Had To Be There: gaming series, decade-look, QC, tunnel-free review)

*Destination: `shared/docs/SESSION-NOTES-2026-06-09-yhtbt-gaming-and-pipeline-hardening.md`*
*Channel in focus: You Had To Be There (cinematic AI nostalgia recreation). Also touched: pipeline-wide infra used by all channels.*

---

## 1. WHAT SHIPPED THIS SESSION (deployed + confirmed on box)

1. **Decade look-override, Phase 1 (stills layer).** Per-job look selection so one channel can render different decades with period-correct stills.
   - NEW `shared/look_resolver.py` — registry of decade looks (`kodachrome_50s`, `color_60s`, `super8_70s`, `vhs_80s`, `hi8_90s`, `digicam_2000s`), each with a Flux `style_suffix` + a (Phase-2) `grade_preset`. Resolves channel-then-project by walking up from the still's `out_path` to find a project `look.json`; falls back to channel `style_suffix` if none. Mirrors `load_channel_config`'s walk-and-cache pattern. Aliases supported (`2000s` → `digicam_2000s`).
   - `shared/patch_decade_look_phase1.py` — swaps `recreation_pipeline.py:529` `config["style_suffix"]` → `resolve_look(out_path, config)["style_suffix"]`; adds `look`/`era` to `parse_script.py` `HEADER_KEYS`.
   - USAGE: drop `{"look": "hi8_90s"}` (or `{"style_suffix":"…","grade_preset":"…"}`) in the project folder as `look.json`. No `look.json` → identical to today (backward-compatible; Final Hours untouched).
   - CONFIRMED: `look_resolver.get_look('hi8_90s')` returns the Hi8 string on box; gaming-series parse showed `look: hi8_90s` in header.
   - SCOPE: Phase 1 = STILLS look only. The GRADE layer (`film_emulate.py`) **does not exist in the repo** (grep confirmed). Phase 2 = write+commit `film_emulate.py` with presets, wire into `assemble()` at `recreation_pipeline.py:801`.
   - KNOWN GAP: `serve_review.py`'s own 4-arg `generate_still` is a SEPARATE function — regenerated stills from the review page do NOT yet pick up the look. Batch render path (line 526/529) IS patched. Follow-up patch needed for the review-server path.

2. **Audio-continuity QC — built into the audio gate.** Turns the Xennials 44-second-hole lesson into an automatic guardrail.
   - NEW `shared/audio_qc.py` — `audio_continuity_check(voiceover_json, threshold=3.0)` scans Whisper segments for inter-segment gaps > threshold; returns `(ok, message)`; READ-ONLY; FAILS SOFT (missing/garbled JSON → "couldn't check", never crashes the gate).
   - `shared/patch_audio_gate_continuity.py` — inserts the check into `audio_leg.py` `audio_gate()` right before `t.gate("AUDIO GATE")`; prints verdict. Reads `artifacts["whisper"]`.
   - CONFIRMED FIRING LIVE on the gaming-series run: printed `✓ continuity check: clean — no silence gaps over 3s` before the gate.
   - The warning message deliberately steers to the RIGHT action: a detected hole = abort + re-run audio, NOT swap (swap is for substituting a human read).

3. **Tunnel-free review server (public bind + token auth).** Kills the SSH-tunnel friction entirely.
   - `shared/patch_serve_review_public.py` — adds `--host` (default `127.0.0.1`) and `--key`; binds `args.host`; REFUSES public bind without `--key` (server is spend-capable: fal + Claude). Key checked at top of `do_GET` and `do_POST`.
   - `shared/patch_serve_review_key_exempt_stills.py` — FIX: exempt `/stills/` and `/api/health` from the key, so the page's own `<img>` requests (which carry no key) load instead of 403ing. Page + spend endpoints still keyed.
   - CONFIRMED: page loads tunnel-free at `http://116.202.18.68:8001/?key=<secret>` after a clean single-server start. One-time `sudo ufw allow 8001/tcp` done.
   - KNOWN FRICTION (still): one project per server start; server dies on window close; port collisions (`lsof -ti :8001 | xargs kill -9`). Mitigate by running in a tmux WINDOW (Ctrl-b c) inside the existing `orch` session. Real fix = multi-project + daemonize (spec written, see §4).

4. **Vinny markup rules (authoring law for You Had To Be There).**
   - `[laughs]` — ALLOWED; performs reliably as a real laugh. Use sparingly, only where Vinny would actually laugh.
   - `[sigh]` — BANNED; does not perform well. Write the wistful exhale into words/rhythm instead.
   - `[pause]` — at most TWO, always attached to a beat with real spoken words, never standalone, never at a chunk seam (write the pause mid-narration with words on both sides). This was the root of the Xennials 44-second hole: a four-stack `[pause]` at a section seam where a failed/empty Inworld chunk concatenated as dead air.

---

## 2. SPECS WRITTEN THIS SESSION (not built — backlog, with detail)

- **`BUILD-SPEC_decade-look-override.md`** — full per-job look system. Phase 1 (stills) shipped; Phase 2 (the `film_emulate.py` grade layer + wiring into `assemble()`) specified, not built. New grade presets needed: `sixteen_mm_60s`, `hi8_90s`, `digicam_2000s` (the others — `super8_70s`, `sixteen_mm_50s`, `vhs_80s` — were referenced as existing but `film_emulate.py` is in fact ABSENT, so all presets get written in Phase 2).
- **`BUILD-SPEC_multiproject-review-server.md`** — the always-on review server. Phase 1: project-in-URL refactor (`…:8001/<slug>/?key=…` + index page + graceful missing-project handling + per-request project resolution) — kills the per-project restart, no new exposure. Phase 2: daemonize via systemd ONLY WITH home-IP firewall lock (it's a spend-capable endpoint).

---

## 3. KEY DECISIONS & STRATEGIC LEARNINGS (banked)

1. **Spike-chasing structurally does not suit this operation — stop doing it.** Three separate Google-Trends/NexLev investigations this session (1970s, Xennial, retro gaming) ALL turned out to be already-crested by the time they were visible in the data. The data lags the wave by weeks; the clone swarm follows a breakout within days. So "find a proven topic with no graveyard" is largely a unicorn by construction — demand and the clone-graveyard are the same signal a few weeks apart.
2. **The durable edge is best-EXECUTION in permanently-warm, served (not searched) lanes — not topic-timing.** Every nostalgia lane is crowded because that's where the whole faceless-AI gold rush points. The differentiator is motion + Vinny + deliberate packaging, NOT an empty topic.
3. **Un-filmable vs. re-watchable filter (the keeper).** The machine's moat is UN-FILMABLE lived memory (the room, the feeling). It is a poor fit for re-watchable media that exists in crisp HD (games, shows) where AI recreation reads as wrong to an AI-sensitive audience. Retro gaming as a documentary topic FAILS this filter; retro-gaming *lived memory* (Christmas-morning-NES, the arcade, the rental store) PASSES it. → Adopt as a sixth niche-selection criterion alongside Leo's five.
4. **Served vs. searched (from the Trends YouTube-Search vs Web-Search panels).** Generational-identity essays are SERVED (nobody searches "gen x nostalgia" — it's pushed). Retro gaming is genuinely SEARCHED (15-yr rising YouTube-search curve). Served topics saturate fast and depend on the algorithm; searched topics have a demand floor. Useful lens for future topic calls.
5. **Google Trends "Rising Queries / Breakout" panel** is a sharper radar than the interest-over-time curves (it surfaces emerging, not crested) — BUT it's noisy and intent-mismatched (products, news bleed, coincidental keyword collisions like "game boy katseye" = a K-pop group). Use it as a DETAIL-mining tool for authentic era artifacts in scripts, not as a topic-picker.
6. **The gaming series reframed from "ride the retro-gaming wave" to "evergreen lived-memory the machine uniquely renders."** Better reason: it doesn't need a spike, works any month, perfect engine fit.
7. **Title↔thumbnail must COMPLEMENT, not echo.** When the thumbnail carries the "what" (the artifact, the era, the joy), the title carries the "why-click" (the emotional/identity hook). Stop repeating the same words across both. (Applied to the Xennials retitle: thumbnail says BORN 1977-1985 / THE LAST KIDS, so the title became the emotional "why you never fit in" hook.)
8. **Batched multi-video jobs are mechanically sound** (pipeline is beat-based; nothing requires 1 script = 1 video). Cut the assembled video into N in Filmora. Constraint: ONE look per job (the resolver caches per project), so batch by shared look — the 4-part gaming series is all `hi8_90s`, one job. The 80s-arcade episode was pulled into the early-90s (Option A) so all four share `hi8_90s` and run as a single batch.
9. **Vinny reads ~195 wpm (measured again this session: 3,829 narration words → 1,161.6s = ~198 wpm).** For a true 10-min episode, write ~1,900 SPOKEN words. The 40-min gaming batch came in at ~19.4 min because the deepened script had ~3,800 spoken words (≈ half what 40 min needs). DECISION PENDING at time of writing: ship four ~5-min episodes vs. double the scripts for ~10-min. (Five minutes is viable; longer = more mid-rolls. Leaning ship-and-learn since the gaming format is unproven.)

---

## 4. NEXT-SESSION BACKLOG (priority order — Peter's stated top items first)

### P1 — Motion-direction feature on the stills review (Peter's #1)
- Add a per-beat MOTION direction control to the stills review page so the reviewer can steer the Kling animation per shot (e.g. "slow push in", "pan left", "static hold"), not just regenerate the still.
- Flow: `MOTION:` textarea per shot in `make_review_page.py` → captured into the feedback JSON → fed into the Kling prompt in the animate leg (`recreation_pipeline.py finish --animate-only`) → optional one-shot preview button reusing the on-demand `serve_review` regenerate pattern.
- Do this AFTER seeing the gaming series' default motion, so we know what actually needs steering. (If default Kling motion is fine on most beats, this becomes lower priority.)

### P2 — Music (still unresolved; decide the model)
- `make_music.py` EXISTS (Claude writes one loopable instrumental prompt → fal ElevenLabs music → `music.mp3`) but is STANDALONE and **not wired into `convergence_leg`** (per ORCHESTRATOR-DEPENDENCY-MAP §5/§8).
- For You Had To Be There specifically: decide whether the nostalgic-warm bed comes from `make_music.py` (generated per-episode) or a curated Jamendo track (the Final Hours approach: `VOICE_LEVEL 1.15` / `MUSIC_LEVEL 0.07`). Nostalgia content lives or dies on the music bed, so this matters more here than on Final Hours.
- Wire chosen path into the assemble step; `--music <file>` override and `--no-music` already exist on the engine assemble. NOTE: `make_music.py` needs shell-sourced `.env` (no `load_dotenv()` yet) — add when next touched.

### P3 — Single channel-agnostic UPLOAD step at end of pipeline — WITH a batch exit-gate
- The publish half of convergence (thumbnail gate, convergence/schedule gate, upload/OAuth) is unbuilt for most channels (ORCHESTRATOR-DEPENDENCY-MAP §8; PLAYBOOK PART 2D convergence row).
- Peter's new constraint: **because batched jobs put MULTIPLE videos in one render, a single auto-upload-at-the-end is WRONG for those jobs** — the one job → one metadata assumption breaks. The pipeline needs an **EXIT GATE OPTION**: a batched job should stop at "assembled, here's the file" and NOT attempt a single upload, because the operator will cut it into N videos in Filmora and upload each with its own title/desc/tags/thumbnail.
- So the upload leg needs a mode switch: single-video jobs → optional auto-upload with per-project metadata; batched jobs → exit at final_video.mp4 (no upload), explicitly. Could be a header flag (e.g. `batch: true` or `parts: 4`) that the orchestrator reads to choose the exit behaviour.
- Until built: all uploads are MANUAL via YouTube Studio. Remember the per-upload manual fixes: category → Entertainment (not People & Blogs); add tags (keywords field); thumbnail.

### P4 — Decade-look Phase 2 (the grade layer)
- Write + COMMIT `shared/film_emulate.py` (it does not exist) with deterministic ffmpeg grade presets: `super8_70s`, `sixteen_mm_50s`, `sixteen_mm_60s`, `vhs_80s`, `hi8_90s`, `digicam_2000s`. Wire a single final grade pass into `assemble()` at `recreation_pipeline.py:801`, using `resolve_look(...).grade_preset`. Gives the VHS/Hi8/digicam TEXTURE (scan lines, chroma bleed) the Flux `style_suffix` only approximates. Fail-soft to ungraded video if the pass errors.

### P5 — Multi-project review server (kill the per-project restart)
- Phase 1: project-in-URL refactor of `serve_review.py` (see `BUILD-SPEC_multiproject-review-server.md`). One server, started once, serves any project by URL + an index page. Phase 2: daemonize (systemd) WITH home-IP firewall lock. (Peter explicitly identified "make the project part of the URL" as the answer.)

### P6 — Stills-gate prompt text fix (now actively wrong)
- The Mode A stills gate still prints the OLD SSH-tunnel instructions. With the tunnel-free server live, those instructions now CONTRADICT the real flow. Update the gate text in `modea_leg.py` to print the `http://<ip>:8001/?key=…` flow (and the `lsof` kill + tmux-window tip) instead of the tunnel dance.

### P7 — review-server look patch (carry the look into the review path)
- `serve_review.py`'s own `generate_still` (4-arg) doesn't apply `resolve_look`, so regenerated/AI-fixed stills ignore the per-job look. Patch it to resolve the look from the project dir like the batch path does.

### Banked-for-later (unchanged from prior sessions)
- **Inworld-layer patch:** wire `speed` (currently dead — payload sends only voiceId+text); fix sentence-chunking voice-drift; **add chunk-validation guard** so a failed Inworld chunk RETRIES or hard-fails instead of silently shipping a hole (the PREVENTION half; the audio-QC we shipped is the DETECTION half). Kill hardcoded "Victor"/"Synthetic" gate labels.
- **Parallel fal animation** (semaphore, bounded concurrency ~5-10) — could cut animation ~5-8×; matters most on high-beat-count episodes like the 72-beat gaming batch.
- **Batch orchestration** formalized (split orchestrator at the stills-review seam into unattended prep + unattended finish).
- **`.gitignore`** for `*.bak* *.pre_* *.backup` clutter (grep keeps tripping over the recreation_pipeline backups).
- fal `safety_tolerance:"5"` on the Flux call (stops silent ~7KB black PNGs).

---

## 5. STATE AT SESSION END
- Gaming series (`you-had-to-be-there/projects/gaming-series`, 4 parts, `hi8_90s`, 72 beats) RENDERING. Audio gate passed (continuity QC clean). Measured ~19.4 min total (~5 min/episode) — length decision pending (ship four ~5-min vs. rewrite to ~10-min).
- Pending when render reaches stills gate: start tunnel-free review server against `gaming-series/modea`, eyeball the Hi8 look reads as early-90s camcorder before approving 72 stills (first full-job test of the look-override).
- After assembly: cut into 4 in Filmora; lock the 4 titles (second-person "you"-led, built to complement the split-frame / artifact-hero thumbnails); build series thumbnails (decide face-consistency: one recurring face vs face-light artifact-hero — currently inconsistent across episodes); manual upload (category=Entertainment, add tags).
- Compare first-day CTR + 30-sec retention across the THREE live formats: list videos vs. Xennials identity-essay vs. gaming-memory. That comparison is the real signal for which direction the channel leans.
