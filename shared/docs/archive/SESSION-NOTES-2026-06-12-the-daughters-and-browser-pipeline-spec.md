# SESSION NOTES — 12 June 2026
## Sacred Dawn Episode 2 ("The Daughters Born Before the Flood") — research → script → render → review-server bug-fixing → browser-pipeline spec

*Operator: Peter Alkema. Channel: Sacred Dawn (@sacredawn). Box: pipeline-prod (116.202.18.68, SSH port 443, user peter, venv ~/venvs/pipeline). Repo: github.com/peteralkema/Pipeline (~/Pipeline box, ~/Projects/Pipeline laptop). Long session; ended with clips animating and two handoff docs written.*

---

## 0. Headline outcomes

- **Episode 2 script written, parsed, rendered to 184 stills, reviewed, and now animating.** Project slug `the-daughters` under `sacred-dawn/projects/`.
- **Thumbnail A/B locked for Clickly** (3 arms) + title A/B decided.
- **Three review-server bugs diagnosed; the worst (403 on the action buttons) fixed properly** (laptop→GitHub→box, idempotent patch, generator-level fix). The other two banked with root causes.
- **A `finish`/`proj_paths` path-resolution bug found and worked around** to resume the parked render after a lost terminal prompt.
- **Decided and spec'd the next big build: the browser-driven pipeline control panel** — a separate doc (`_SPEC-browser-pipeline-control-panel.md`).

---

## 1. Niche research (NexLev) — the lane behind ep2

Goal: find the biggest recent in-lane outlier for Sacred Dawn (cinematic biblical primeval) and decide ep2.

Ran channel-level `search_niche_finder_channels` (the trusted endpoint; video-level `search_videos` remains the corrupted one — do not trust it). Findings:

- **No pure "Book of Revelation" cinematic-recreation breakout exists** at the under-100k / recent-launch level. "Revelation/end-times/beast" pulls big numbers but only as **clips/commentary** (Battle&Becoming's "THE BEAST: IT IS ALREADY HERE" 907K is a reposted John Lennox talking-head clip — wrong format for our machine), not cinematic recreation. The shock-keyword query also drags in off-lane noise (zombie survival, disaster music, anime/manhwa "reborn as a god" recaps — Lumos at $18.9K/mo, ignore entirely).
- **The converting, in-lane vein is Nephilim / Watchers / female-Nephilim / pre-Flood** — exactly Sacred Dawn's launched lane. Two unrelated channels spiking the same sub-topic in the same weeks = genuinely accelerating, not a one-off:
  - **Scripture Origins** (May 2025, ~42.7K, ~$4.1K/mo): **"Giants Ruled for 1636 Years: Why the Nephilim Were So Dangerous" — 1.5M views, May 2026, 31:39** → the single biggest recent in-lane outlier (~10× the channel's 151,662 avg). Also "Female Nephilim: What the Book of Enoch Says About the Watchers' Daughters" — 900K (~6×).
  - **Scripture Legacy** (Apr 2025, ~17K, ~$4.1K/mo): "Archangel Sent to Destroy the Nephilim" 279K, "Before the Flood: Nephilim and Sons of God" 214K, "Book of Enoch…Soul After Death" 393K.
- **"War in heaven / fall of Lucifer / cosmic judgment" sub-lane** explored separately: **Heavens Lore** (Jun 2025, 7.28 outlier, Google-Trends keyword literally "Lucifer") is the closest format-match and a **proof-of-concept that went dormant** (7 videos, last upload Nov 2025, never monetized) — validated demand, vacant chair, but a **lower ceiling** (50–95K) than the Nephilim cluster (200K–1.5M). Bridge option, not the headline.

**Banked caveats:** the `youtube_channel_outliers` endpoint returned empty even at 1.5× for Scripture Origins despite an obvious ~10× video — it's flaky; compute outlier multiples by hand from the niche-finder `lastUploadedVideos` + channel avg instead.

**Decision:** ep2 = the **Watchers' daughters / female-Nephilim** beat — accelerating sub-vein, pure un-referenced-sublime (no footage to be wrong against), and the **direct continuation of the launched Watchers episode** (the Watchers *are* the fallen angels; the daughters are one step downstream). Builds the Sacred Dawn cosmology spine (rebellion → Watchers → Nephilim → Flood → judgment) rather than scattering. **Hook pattern banked** from the winners: a hard specific number/claim + a threat/secret frame ("Giants Ruled for *1636 Years*"; "*Terrifying* Truth about the *Daughters*"). The exemplar's exact title is spent; the *pattern* is the reusable asset.

---

## 2. Thumbnail iteration + Clickly test (LOCKED)

Iterated in Clickly from ep1's "ANGELS OR GIANTS?" DNA (gold/cream caps, dark silhouette focal subject, god-rays, gold-vs-storm duotone, tiny figure for scale, faceless). Subject became a **female colossus** (robed, wind-thrashed, face turned away — monumental and dreadful, **never sexualized**; that's both on-brand and what converts in this lane).

Iteration path: "FEMALE NEPHILIM" (keyword) → "DID GIANTS HAVE DAUGHTERS?" (question) → tested **highlighter-yellow** on the payload word → **rejected** (reads as lower-tier scripture-channel template, breaks SD premium register, clashes with the warm god-rays) → landed on **ep1 gold/amber** on the second line + white stroke + drop shadow. Final image holds at mobile scale.

**Locked Clickly set** — all on the same female-silhouette base, all under one title:
- Title (all arms): **"The Watchers' Daughters: What the Book of Enoch Hides About the Female Nephilim"** (reverent, forbidden-text curiosity) — *vs.* the header working title (see §3).
- **B2** — "DID GIANTS HAVE / DAUGHTERS?", gold bottom line (predicted CTR winner; inherits ep1's proven question hook).
- **B1** — same, all-white (the control: tells you whether the two-tone gold *earns* its place or just flatters the eye; if B2>B1, two-tone gold becomes a SD thumbnail rule).
- **C** — "FEMALE NEPHILIM", all-white (raw keyword/reach arm).

**Watch CTR *and* impressions separately**, not just headline rank. Likely outcome: B2 wins CTR, C wins impressions → confirms "keyword in title, question on thumbnail," which this pairing already does.

**Banked thumbnail doctrine:** the gold/white condensed-caps + white-stroke + drop-shadow + dark-silhouette + gold-vs-storm-duotone + tiny-scale-figure is now a **reusable Sacred Dawn spec**, codified. The *text system is the brand; the pose is spent* — ep1 and ep2 are both giant-in-the-valley silhouettes (a deliberate ep1↔ep2 rhyme), but **ep3 must break the camera** (low-angle up at the Watchers descending, or daughters at crowd scale) while keeping caps + duotone constant. A third valley-silhouette tips from signature to samey.

---

## 3. The script — `the-daughters` (DELIVERED, RENDERED)

**File:** `sacred-dawn/projects/the-daughters/script.md`. **184 beats · 4,752 words · ~31 min landed** (measured: durations.json reports **33.1 min / 1987s** total after Whisper — slightly over the ~31 estimate, comfortably inside the 30–40 ask).

**Header:** `channel: sacred_dawn`, working title **"The Terrifying Truth About the Daughters Born Before the Flood."**
> **TITLE FLAG:** this working title is the *shock-bait* register that Sacred Dawn doctrine §11 files under *never run* (monetization-guard risk). It is in the header **only as the Clickly Title-2 test arm**. The **script register stays fully reverent regardless** — the title is the lure, the narration is the moat. If the reverent "Watchers' Daughters" title wins the A/B, swap the header `title:` field and nothing in the script changes.

**Craft, built to the explicit brief (more animatable foreground than ep1, short beats, no dead wides):**
- Avg **25.8 words/beat**, max 40, **zero beats over 55**, **zero beats past 3× Kling stretch**, only 1 beat over 12s. Every beat has a VISUAL. No bare digits in narration. (ep1 was 52 beats × ~52 words = ~4× stretch / slow-motion — explicitly fixed here.)
- **Every beat is kinetic, drift-safe foreground**: angels plunging through cloud, forge (molten pour, grindstone sparks, quench-burst), the kohl-rod drawing a single eye, the mirror tilting, a bracelet sliding on, a giant infant's hand sinking into earth, a colossus's foot bursting clay, herds scattering, grain-towers punched open, giants colliding in silhouette, Azazel dragged into the pit on chains of light, water climbing the loom. Faces dodged throughout (single eye, profile, silhouette, back, hands).
- **Spine:** the **bronze mirror + painted eye** (seeded cold open, tightened each act, paid off sinking face-up in the silt). **Thesis:** "it began with a look" (planted open, harvested at close, turned at the viewer's lit screen). **Human throughline:** nameless weaver's daughter → her giant daughter → the grandmother, carried on three drowning objects (loom, blue beads, snapped bronze bracelet); named-absence refrain does the dignity work.
- **Attribution discipline intact** (Genesis says / the Book of Enoch says; canon vs apocrypha distinct; single recreation-acknowledgment line early). **Comment-bait** planted + asked at close ("victims the Watchers stole, or the first the world ever knelt to?"). **Sequel hook** → backlog #2 (the bloodline that survived the Flood).
- Includes the canonical Enoch Ch.10 commissions (Uriel→warns Noah, Raphael→binds Azazel in Dudael, Gabriel→sets the giants on each other, Michael→binds Semjaza), added in the extension pass that took it from ~23 min to ~31.

**Process note:** first draft landed at 142 beats / ~23 min (grain perfect but under the 30–40 target); extended to 184 beats via ~13 idempotent `str_replace` insertions deepening the most animatable acts (gifts, giant-growth, hunger) + the archangel commissions. Verified after each.

---

## 4. The pipeline run (the-daughters) — what happened, in order

1. **Project dir + script→repo→box:** `mkdir -p sacred-dawn/projects/the-daughters`, moved `script.md` in, laptop→GitHub→box (`git pull --no-edit` first), parsed on box.
2. **Parse + verify:** `parse_script.py` → `beats.json` + `beats_full.json`. Verify one-liner: **184 beats, all Mode A, no wordless, no missing VISUAL.** Clean.
3. **Dry-run** (`orchestrate.py --project the-daughters --beats …beats_full.json --dry-run`): green. `channel sacred_dawn · the-daughters`, legs `audio → modeA → convergence` (Mode B skipped). Stills est. **≈ $5.52**.
4. **Live run.** Audio leg: narration assembled (4,752 words) → Inworld voiceover.mp3 (31.8 MB) → Whisper → durations.json (**33.1 min**, continuity clean). **Audio gate → KEEP.** (Gate banner said "Victor" — *cosmetic label only*; synthesis correctly used Elliot, confirmed by the `voice: Elliot [channel: sacred-dawn]` log line. Banked as a cosmetic fix.)
5. **Stills leg:** **184 stills rendered** to `sacred-dawn/projects/the-daughters/modea/stills/` (`shot_001.png`…`shot_184.png`). Run **parked at the Mode A gate** (`go`/`skip`), spending nothing.
6. **Then the review-server saga (§5) and the resume saga (§6).**

**Confirmed pipeline facts learned this run:**
- Kling endpoint: **`fal-ai/kling-video/o3/standard/image-to-video`** (`recreation_pipeline.py:214`), `duration: SHOT_DURATION`, `generate_audio: False` (correct — not paying for Kling audio). Standard (cheap) tier, image-to-video. **Per-clip $ rate not in repo** — get it from fal dashboard: ep1's 52 clips ÷ 52 × 184 = true estimate. Planning band: ~$0.25–0.35/clip → **~$46–64** for the 184-clip leg (CONFIRM against dashboard).
- `animate_still(still_path, motion_prompt, out_path)` at `recreation_pipeline.py:589` — **`motion_prompt` is the 2nd arg**, the exact seam the future per-shot motion-direction feature plugs into.
- **Content-policy auto-fallback** in the animate `except` (lines ~580+): on Kling content-policy refusal ("casts, remains, executions") it converts the still to a **held (unanimated) clip** and continues, rather than crashing. **Watch the animate log for `⚠ content-policy refusal — using held still`** — a cluster in Part Five/Seven (drowning, giants devouring) is the signal to soften those motion_prompts for ep3 (describe water/dust/environment moving, not the body being destroyed — same "catastrophe as environment" discipline that keeps Flux clean).

---

## 5. Review-server bugs — THREE found, ONE fixed properly

### 5a. (FIXED) The 403 on AI Fix / Regenerate / Restill buttons
**Symptom:** AI Fix button → "AI fix failed: Failed to execute 'json' on 'Response': Unexpected end of JSON input." Both action buttons dead.
**Diagnosis path (the lesson: read the actual error first).** Wasted a few turns theorizing (stale model string — *I was wrong, `claude-sonnet-4-6` is valid, verified against live Anthropic docs*; unguarded exception). The `journalctl --user -u review.service` log showed the truth in one line: **`POST /api/aifix HTTP/1.1" 403`.** The handler never ran.
**Root cause:** `_key_ok()` in `serve_review.py` reads the shared key **only from the URL query string**. Page + `<img>` GETs carry `?key=fh2026` so they pass (every still served 200); the button `fetch()` POSTs sent only `Content-Type` and **no key** → blocked before the handler → 403 with empty body → browser's `response.json()` chokes.
**Fix (idempotent, laptop→GitHub→box, generator-level):** `patch_serve_review_authkey.py`:
- `serve_review.py` `_key_ok`: accept the key from an **`X-Review-Key` header OR** the query string (backward-compatible).
- `make_review_page.py` (the **generator**, not the generated file): emit a `REVIEW_KEY` const read from `window.location`, and add `"X-Review-Key": REVIEW_KEY` to both POST headers (matched the **doubled-brace `{{ }}`** f-string form — the subtle bit).
- Then **regenerated** `the-daughters/modea/review.html` from the fixed generator (did NOT hand-edit generated output), `lsof -ti :8001 | xargs kill -9`, restarted server.
**Verified:** both AI Fix and Regenerate now return 200 and work. Permanent — every future project's page is born with the key wired in.

### 5b. (BANKED, not fixed) Stale-server / wrong-project review page — "still not generated"
**Symptom:** review page showed "still not generated" though 184 PNGs were on disk.
**Root cause:** the always-on `serve_review.py` (user systemd `review.service`) takes `--project /home/peter/Pipeline/.review_current` (a symlink) and **resolves it once at process boot, caching it**. The launcher (`review.py`) is supposed to repoint `.review_current` per project, but the running server had already cached the old target. The symlink was correct on disk; the server just hadn't re-read it.
**Workaround used:** `lsof -ti :8001 | xargs kill -9` then relaunch `review.py --project sacred-dawn/projects/the-daughters/modea` to force a fresh resolve; hard-refresh browser.
**Real fix (deferred → folded into the browser-pipeline build):** make the server re-read the active project **per request**, not at boot; and have the Mode A gate **own the server lifecycle** (kill/repoint/spawn/health-check) so the operator never runs a command — just clicks a bookmark. This is the "auto-serve gate" spec, now subsumed by `_SPEC-browser-pipeline-control-panel.md`.

### 5c. (BANKED) Gate prints a command instead of running it
The Mode A gate **prints** the `review.py` command for the human to copy-run, rather than starting the server itself. Combined with 5b, this is the whole "why isn't it click-a-bookmark" problem. Fixed by the browser-pipeline build.

---

## 6. The resume saga — lost prompt + the `proj_paths` bug

Peter lost the orchestrator's `go` prompt (tmux confusion — dislikes tmux; much of the CLI friction was wrong-directory / lost-window, an operator-surface problem, not a pipeline problem). The orchestrator process exited. **Nothing lost** — audio, durations, all 184 reviewed stills on disk.

**Recovery attempt 1 (failed):** `recreation_pipeline.py finish --project the-daughters --animate-only` → `FileNotFoundError: 'the-daughters/clips'`.
**Root cause (BANKED):** `proj_paths()` (`recreation_pipeline.py:1083`) auto-prefixes a bare single-part name with `projects/` **only if a top-level `projects/` dir exists in cwd**. Under the channel-folder architecture (`sacred-dawn/projects/…`) there is no top-level `projects/`, so the prefix never fires and it builds `the-daughters/clips` relative to cwd → crash. It's **legacy single-channel logic** (comment literally references "mary_celeste → projects/mary_celeste") and resolves **differently from `orchestrate.py`** (which took `--project the-daughters` fine). Same class as the no-arg-launcher `(no path)` halt.
**Recovery (worked):** pass the **full path** so the broken auto-prefix is skipped (it only touches single-part names):
```
python shared/recreation_pipeline.py finish --project sacred-dawn/projects/the-daughters/modea --animate-only
```
**Clips are now animating.** (Confirm it found 184 stills / didn't regenerate.)

---

## 7. Decision: the next big build — browser-driven pipeline control panel

Peter's call (correct): the render core is proven; **the operator surface is the problem**, and the fix is to make the whole pipeline browser-driven — channel dropdown → project dropdown → live/dry-run + log level → Launch → gates appear inline as page state → Generate Clips button. No terminal, no cd, no tmux, no paths.

**Decided:** v1 **spins silently then shows the gate** (no live log streaming — simpler build).
**Spec written:** `_SPEC-browser-pipeline-control-panel.md` — includes the architecture (coordinator/job service, gate protocol, state-driven UI, server-truth), growth guidance (5 rules: UI=f(state); panels keyed by phase; generate-don't-hand-edit + split templates early; stable JSON API contract; framework escape-hatch + its trigger), how motion-direction and Mode B fit as pure additions, the code fixes to fold in (proj_paths unification, per-request symlink read, voice-label), and a phased build order.
**It subsumes** four backlog items: Mode A gate auto-serve, proj_paths/launcher path unification, no-arg launcher halt, stale-server review page.

---

## 8. OPEN ITEMS / NEXT ACTIONS (priority order)

1. **Confirm clips animating cleanly** — watch for `⚠ content-policy refusal — using held still` lines; count them (Part Five/Seven). Then convergence → `final_video.mp4`. Upload manual (Entertainment / cat 24 / private) until the channel-agnostic upload step exists.
2. **Get the real Kling per-clip cost** from the fal dashboard (ep1's 52-clip the-watchers run ÷ 52 × 184). Bank the rate for future episode estimates.
3. **Build the browser-pipeline control panel** (`_SPEC-…` doc) — next session, on the laptop, with orchestrate.py / serve_review.py / review.py / make_review_page.py open. Phase 2–3 first (Launch + audio gate + stills gate + Generate Clips); that removes ~90% of today's pain.
4. **Upload ep2 + run the Clickly test** (B2 vs B1 vs C; reverent title vs shock title). Watch CTR **and** impressions; watch act-break retention (31 min is above SD's 17–25 doctrine band — if it holds past 40%, ep3 can run longer).
5. **Code fixes (fold into the build, not as separate patches):** unify `proj_paths`/orchestrator path resolution; server re-reads active project per request; voice-gate label reads `voice_id` (kill cosmetic "Victor").
6. **Banked-deliberate-later:** parallel fal animation (bounded-concurrency semaphore — this 184-clip leg is exactly the volume that justifies it); batch split at the stills-review seam.
7. **ep3 thumbnail must break the camera** (pose is spent; text system is the brand). Soften Part Five/Seven motion prompts if content-policy fallbacks cluster there.

---

## 9. Discipline notes (what went right and wrong, for the record)

- **Right:** read every file before patching the 403; **verified the model string against live docs instead of trusting my own wrong hunch** (it was valid); patched on the laptop through git; regenerated generated output rather than hand-editing; held the laptop→GitHub→box line even under "just fix it now" pressure.
- **Wrong (corrected):** burned a few turns theorizing about model strings / unguarded exceptions before pulling the `journalctl` log that said "403" immediately. **Lesson reinforced: read the actual error first.** The log was worth more than all the code-reading.
- **The deeper pattern:** today's frustration was almost entirely **operator-surface** (CLI, tmux, paths), not core pipeline. The core ran clean. That's exactly why the browser-panel build is the right next move — it attacks the real source of pain.

---

*Maintained by Peter + Claude. Next session: start fresh with `_SPEC-browser-pipeline-control-panel.md` open on the laptop. Episode 2 is rendering; the Clickly test and the control-panel build are the two live threads.*
