# You Had To Be There — Channel Doctrine
*The single consolidated channel reference for You Had To Be There (@you-had-to-be-there). Load this — with the four `_` system docs — on any YHTBT session. Consolidates the launch & operating doc (v1.2), the 9 June gaming-series + pipeline-hardening session, and the 18 June first-batch-through-the-runner session into one comprehensive brief.*
*Updated 18 June 2026. Retires: `you-had-to-be-there_LAUNCH-DOC.md`, the 9 June and 18 June session notes (YHTBT-specific parts). The `_` prefix floats it to the top of `shared/docs/`; channel-scoped, load-on-demand.*

---

## 1. Identity

- **Channel:** You Had To Be There · **Handle:** `@you-had-to-be-there` (clean hyphenated handle matching the spoken name).
- **Repo folder:** `you-had-to-be-there/` · **channel.json `name`:** `you_had_to_be_there`.
- **CRITICAL — two names, don't confuse them:** the **`--channel` flag wants the hyphenated DIR name** (`you-had-to-be-there`), NOT the underscore `name` field. The runner looks for `<channel>/channel.json`; passing `you_had_to_be_there` fails with "channel.json not found." Script headers should also read `channel: you-had-to-be-there` (the header-vs-folder match rule); normalize with a one-line `sed` after staging if they carry underscores.
- **Format:** Long-form (target 8–12 min; the proven cold-start batch runs **tight ~7–8 min** — see §5), **Mode A only** — fully AI cinematic recreation. No stock footage, no Mode B graphics.
- **Voice:** **Vinny** (Inworld) — a dialed-back Brooklyn storyteller. Wry, knowing, warm underneath. The accent and swagger are the seasoning; the nostalgia is the meal.
- **The closer line:** *"If you remember this, you already know. And if you don't… well. You had to be there."* The recurring closer and emotional signature. **Never** a cold-open prefix or branded intro (both hurt retention/CTR) — it earns its weight only at the end.
- **One-sentence positioning:** a guy who was there walks you back through a vanished world — *in motion* — and the audience neither notices nor cares that the world was rebuilt by a machine.

---

## 2. The strategic thesis (why this channel, why this machine)

The pipeline is a **cinematic-recreation engine** (Flux stills → Kling motion → one continuous Inworld voice → ffmpeg). Its native skill is rebuilding a lost world as moving image. Nostalgia is the highest-value subject that skill can point at:

1. **It's the machine's home register.** "Recreate a vanished world, elegiac, present-tense" is exactly what the engine already does for Final Hours — pointed at memory instead of death.
2. **The audience is the most AI-indifferent on the platform.** The 40–70 nostalgia viewer isn't hunting for AI seams. They want the *feeling* of being there, and a generated 1976 street delivers that as well as any archive — better, because it can move.
3. **Motion is a genuine moat — but a conditional one (see §5a).** Incumbents (Memory Trails, American Rewind, Back When) build the feeling with slow Ken Burns pans over *still* vintage photos + spliced archival. Their scripts constantly describe motion they can't show. Our engine *can* show it. BUT motion is also the single highest-defect render leg (warping), so on a first batch we ship all-Ken-Burns and bank motion as a later upgrade, not a launch requirement.

**The bet in one line:** packaging beats production; CTR + AVD in the first 48 hours drive distribution; our unique lever is *motion the photo-pan channels can't match*, under a period grade that doubles as AI camouflage.

### 2a. Why this lane is open (format vs lane)

The "time-travel vlog" trend (e.g. Chloe-vs-history) is a **format**, and formats get cloned to death fast because the novelty *is* the mechanic; it also announces its own artifice. We've built on more durable ground: not a format, a **subject** (vanished everyday life) with flexible delivery. Subjects don't saturate the way mechanics do — near-endless surface (every decade, ritual, object) × multiple delivery angles (list, immersive, Gen-Alpha). Formats fill up; lanes have room.

Two reinforcing structural advantages (rare because they usually trade off):
- **Not committed to expensive hi-fi rendering.** The grain, shake, faded stock aren't a quality ceiling — they're the genre's native language. Nobody wants 4K crispness on a 1976 memory; it breaks the spell.
- **So the cheaper output is also the *better* output.** The imperfect look is more convincing, not less. This is why the all-Ken-Burns / $3-a-video posture (§6a) costs nothing in perceived quality.

### 2b. The two-audience model (this drives thumbnail strategy)

Nostalgia is **two audiences watching the same video for opposite reasons:**
- **Recognition viewer (40–70):** watches to *remember* — "I lived that." Satisfied because the content is *true*.
- **Discovery viewer (younger):** watches to *find out* — "so THIS is what it was like for my parents." Satisfied because the content is *foreign*.

**Consequence:** one video earns two satisfactions and neither audience is let down — **so the thumbnail can lean bold.** The discovery viewer has no prior memory to betray. The **disappointment-proof shield:** the mundane past IS the drama from their vantage. The Gen-Alpha-vs-boomer concept (§7C) is the *bridge* that makes this explicit — confirmed a likely **core pillar**, not a novelty (the `70s-baffle-gen-alpha` script in batch one is the first test).

**The thumbnail line (nuance):** the latitude is real — be far bolder than the sleepy photo-pan incumbents — but **bold ≠ false.** What craters AVD is promising something the video doesn't contain. Spend the latitude on **intrigue and curiosity gap, not lies.** *Maximally curiosity-gapped but emotionally honest.* (This is encoded verbatim in the channel.json `thumbnail.selection_rules` — see §4.)

---

## 3. The research — Leo criteria & how we got here

Nostalgia chosen against five "Leo criteria" via NexLev: (1) monetized; (2) under 100k subs; (3) ~20k+ avg views; (4) viral in last 6 months; (5) reproducible in our format for an AI-indifferent audience. Sixth criterion added 9 June: **un-filmable lived memory** (§6).

| Niche | Machine fit | AI-indifference | Viral 6mo | Eff. RPM | Verdict |
|---|---|---|---|---|---|
| **Nostalgia (AI-reconstructed)** | Excellent — the machine's twin | Very high (40–70) | Yes | $3.6–5.1 | **CHOSEN** |
| AI animal drama | Excellent | Very high | Hottest | $1.4–3.0 | #2 (banked for batch mode) |
| Money / luxury | Good | Good | Cooler | $3.0–5.8 | #3 — more saturated |
| Personal finance | Poor — nothing to recreate | Lower | Densest | $6.4–10.3 | DROPPED |

**The reframe:** under a pure-AI cinematic pipeline the best niche is one that *demands* generated footage. Finance pays best but has nothing to recreate; nostalgia is dead-center for the machine at a solid RPM.

**Competitive set:** *Professor Blackwood* (proof full-AI cinematic nostalgia monetizes, ~$5.38 RPM, immersive); *American Rewind* (~81k, 3.6M-view list — static photo-pans, the ceiling we leapfrog); *Memory Trails*; *Americana Rewind* (633k on "10 Things '70s Parents Did That Would Be Illegal Today" — direct ancestor of our launch title); *Back When*, *Yesterday's America*, *Nostalgia Calling*.

**Two sub-formats, and our hybrid:** *narrative/immersive* (Blackwood) where motion bites hardest; *list/montage* (American Rewind) gets bigger raw views but is visually static. **We run the hybrid:** list *structure* (proven, searchable, high-CTR) + immersive *cold open* + cinematic *per-item beats*.

---

## 4. Channel config — LIVE schema (everything the pipeline reads)

As of 18 June, `you-had-to-be-there/channel.json` carries `name`, `voice_id`, `style_suffix`, `default_music_prompt`, `base_canon`, **and the now-live `music` + `thumbnail` blocks** below. These two blocks were the missing prerequisite that made `make_thumbnail` and the scored mux work — without them the thumbnail step exits 1 and the bed is silent.

### The `music` block (LIVE — bed confirmed "perfect" on the canary)
```json
"music": { "dir": "music", "tracks": 3, "crossfade_seconds": 2, "level": 0.07 }
```
- Picks **3 random tracks** from `you-had-to-be-there/music/`, crossfades 2s, sits at **level 0.07** under Vinny. 0.07 is the validated level — sits under the narration without ducking it. Nudge to 0.08 only if a future bed feels too quiet.
- **8 curated Artlist tracks** live in `you-had-to-be-there/music/` (`track_01.mp3`…`track_08.mp3`, space-free filenames). The 3-of-8 random pick gives natural variety across a batch. Curated bed beats `make_music.py` for this channel — nostalgia lives or dies on the bed and curated wins.

### The `thumbnail` block (LIVE — matched to the proven prehistoric-disasters schema)
Composition `low_silhouette`; 2 Flux candidates → Sonnet vision selects the substrate → deterministic Pillow overlay in the locked house look. Warm nostalgia palette (title `[247,241,227]` cream, subtitle `[240,169,75]` amber), left-third scrim (`side:left, width:0.42, opacity:0.55, feather:0.7`), Anton font at `shared/fonts/Anton-Regular.ttf` with DejaVu/Impact fallbacks, uppercase, stroke 12, shadow on. The `candidate_prompt_suffix` pushes "one nostalgic focal subject in the right two-thirds, warm saturated color, dark low-detail left third for the headline, no faces, no people, no text." `selection_rules` encode "boldly nostalgic but emotionally honest — intrigue, not a lie."
- **Substrate rule that matters:** subjects mass on the RIGHT, text negative-space is the LEFT third — the `.thumb.json` `subject` prompts and the suffix must agree on this or the headline lands on clutter. If a scrim reads too light over a busy left third, `scrim.opacity` 0.55 → 0.65 is the one knob.
- **First proven thumbnail:** `80s-after-school` → "GONE TILL DARK" over two BMX bikes at golden hour. Headline legible at phone size, warm palette popped, left scrim clean. Confirmed good.

### The `.thumb.json` per-script spec
`{"subject": "...", "title": "...", "subtitle": "..."}` — `subject` = what the substrate depicts (write it RIGHT-massed, LEFT negative space, no faces/people); `title`/`subtitle` = the locked headline. The runner copies it to `<project>/thumbnail.json` at prep; `make_thumbnail` reads look from channel.json + headline from this. A `.md` with **no sibling `.thumb.json` is SKIPPED** (fail-fast, validated before any project is created).

### The per-job decade look (THIS channel's distinguishing pipeline feature — Phase 1 LIVE)
Look resolves **channel-then-project**: `channel.json` `style_suffix` is the default; a project **`look.json`** (`{"look":"hi8_90s"}`) overrides for that job. `look_resolver.py` (`recreation_pipeline.py:532`) walks up from the still's output path.
- **Registry:** `kodachrome_50s`, `color_60s`, `super8_70s`, `vhs_80s`, `hi8_90s`, `digicam_2000s` (decade aliases work). Each carries a Flux `style_suffix` + a (Phase-2) `grade_preset`.
- **"The channel owns the frame; the job owns the film stock."**
- **Phase 1 = stills look only** (Flux `style_suffix`). **Phase 2 (NOT built) = the grade layer** (`film_emulate.py`, the deterministic ffmpeg pass). Until then the look is the Flux suffix only.
- **Known gap:** `serve_review.py`'s `generate_still` (review-page restill) does NOT pick up the look — only the batch render path is patched.

### Frame decisions
Aspect **16:9 deliberately** — period feel comes from the grade, not the frame shape. Mode A only.

---

## 5. Scripting principles for this niche (hard-won, channel-specific)

**The Vinny register (dialed-back Brooklyn):** wry, knowing, conspiratorial. Swagger as seasoning. Casual contractions throughout. Funny on the "now illegal" turns; **sincere at the close** — the bit drops entirely for the ending, and that's where it lands.

**Structure (the proven batch-one template):** anti-dip cold open → the turn → arc announcement → set-up beat + payoff beat per item → over-deliver coda → sincere close + closer line.

### 5a. The anti-dip cold open (banked from the launch retention curve)
The launch video's one readable retention shape showed **~96% at 5s holding to ~90% at 16s, then a CLIFF to ~76% by ~21s and ~63% by ~31s** — relative-to-peers weakest in the open. **The cold open is the proven leak, not length.** Every batch-one script is built on `_COLD-OPEN-TEMPLATE.md`:
- **First concrete payload by ~0:12** (drop straight into a sensory second-person scene; no throat-clearing).
- **No admin lull at 0:16–0:30** — be inside Number One's world by ~0:25–0:30.
- Cold open = ~6 beats: scene → scene → the turn → thesis seed → arc announcement → recreation acknowledgment ("about ninety percent true, a hundred percent how it felt").

### 5b. Warp-safe VISUAL framing (THE major new craft law — 18 June)
Flux warps **hands, fingers, faces, and multi-person interaction worst**, especially in **close-up where the hand fills the frame**. This survives the motion choice — a warped *still* is warped whether it's animated or Ken-Burns. Banked law for every VISUAL line:
- **Drop the lone-hand close-up.** Make the **OBJECT or the SCENE** the subject, in the state the action leaves it. ("a hand dialing a rotary phone, close-up" → "a rotary phone on a table, the dial mid-spin, the handset off the cradle, warm light, no people").
- **Pull to medium/wide with depth.** This both removes the warp magnet AND gives Ken-Burns somewhere to zoom — the two biases point the same way.
- **Prefer "no people," "seen from behind," silhouettes, distant figures.** Faceless-leaning is more period-authentic, safer, AND lower-warp.
- **Warp risk concentrates in object-handling topics** (toys, pocket-change, baffle-Gen-Alpha ran 24–38% warp-prone; danger/outdoor lists ran 9–15%). Food/object still-life topics (e.g. `80s-snacks-gone`) are structurally the safest — no hands or faces by nature.
- **This is a bias, not a guarantee.** Flux is probabilistic; object stills still occasionally warp (extra finger, fused object). The residual is caught at the post-render verdict pass (§6b), not prevented at the prompt.
- A deterministic patch (`patch_warpsafe_visuals.py`, index-keyed, asserts each target is a VISUAL line before rewriting) rewrote 124 lines across the batch-one nine: warp-prone 124 → ~0 with narration untouched. Keep this pattern for future biasing passes.

**Mechanics (the Constitution, applied here):** every beat carries spoken words; one `VISUAL:` per Mode A beat; **numbers spelled out** ("nineteen seventy-six"); ≤55 words/beat; faceless-leaning framing.

**Over-deliver on the count** — title says "10," episode delivers 13 via a *"three more I couldn't leave out"* coda before the close (announced where drop-off is worst = retention hook; under-delivering is the only version that hurts).

**Distinct spine per video** — each script runs its own recurring device so a viewer who watches several never feels the formula: "today, that's a phone call" / "every one's a law now" / "we loved it, that's why it's gone" / "vanished, and we barely noticed" / "a career-ending headline today" / "should've been illegal, somehow we lived" / then-vs-now contrast / the price reveal / "watch them try" / "no helmet, somehow we lived."

**Vinny markup allowlist (banked law):**
- `[laughs]` — **ALLOWED**, performs as a real laugh. Sparingly.
- `[sigh]` — **BANNED**, doesn't perform. Write the wistful exhale into words.
- `[pause]` — at most **TWO**, attached to a beat with real spoken words, never standalone, never at a chunk seam. (Root of the Xennials 44-second silent hole.)

**Length math (measured):** Vinny reads **~195–198 wpm**. A true 10-min episode = ~1,900 spoken words via *more content*, not padding. **But batch one deliberately runs tight ~7–8 min (~1,300–1,550 words)** — for cold-start, 8 min of good Vinny that holds completion beats 11 min of padding, still earns mid-rolls, and renders cheaper. Length is retention-earned, not padded to a benchmark. **Trust `ffprobe`, never the player, for true duration.**

**Dead `speed` key (flag):** `channel.json` `"speed"` does nothing — `generate_voiceover` sends only `voiceId` + text. Pacing = `[pause]` + word count. Backlogged.

---

## 6. Strategic learnings banked

### From the 9 June gaming-series session
1. **Spike-chasing structurally doesn't suit this operation.** Data lags the wave by weeks; the clone swarm follows a breakout in days. "Proven topic with no graveyard" is a unicorn by construction.
2. **The durable edge is best-EXECUTION in permanently-warm, served lanes** — motion + Vinny + deliberate packaging, not an empty topic.
3. **Un-filmable vs. re-watchable filter (the keeper).** Retro gaming as documentary FAILS (games exist in crisp HD). Retro-gaming *lived memory* (Christmas-morning NES, the arcade) PASSES. Sixth niche criterion.
4. **Served vs. searched.** Generational essays are SERVED; retro gaming is SEARCHED (demand floor). Served saturates fast.
5. **Trends "Rising/Breakout" panel** = a DETAIL-mining tool for era artifacts, not a topic-picker.
6. **Title↔thumbnail complement, not echo** — thumbnail carries the "what," title the "why-click."
7. **Batched multi-video jobs are mechanically sound** (beat-based). Constraint: **one look per job** (resolver caches per project) — batch by shared look.

### From the 18 June first-batch session
**6a. For this lane, render all-Ken-Burns (`--kling-count 0`) on the batch.** Two reasons converge: (1) the 17-June banking that motion is a brand *tiebreaker*, not a cold-start growth driver — packaging/topic/cadence drive distribution; (2) the canary proved motion is the **highest-defect leg** — both visible defects (a garbled-motion still and a blank still) landed on the two Kling beats, while the Ken-Burns beats were clean. So Kling is both the most expendable AND the most failure-prone part of an unattended batch. All-Ken-Burns = **~$3/video**, removes the motion-warp class entirely, and costs nothing in perceived quality (§2a). Bring motion back as a deliberate upgrade once the channel is earning, not before.

**6b. Even warp-safe + Ken-Burns, Flux stills carry residual risk — plan a verdict pass.** Two failure modes survive: **blank/black PNG on a Flux safety reject** (fix: pass `safety_tolerance:"5"` — confirm the *batch* render path sets it, not just the review-page restill) and **occasional object warp**. The runner ships what it can and logs the rest (graceful, non-halting — same as the canary shipping without a thumbnail). So **first batches upload PRIVATE**: eyeball every video for blank/warped stills + thumbnail + bed before any goes public; anything flagged is a **single-beat restill** (`restill_from_feedback.py --project … --feedback '{"shot":N,...}'`, positive re-description leading with the dominant noun), not a re-render. A Sonnet-vision QC sweep over `modea/` stills (flag anatomy/object warping, return beat numbers) is the backlogged automation of this pass.

**6c. The bed strategy is validated.** Curated Artlist tracks at level 0.07, 3-of-N random pick, crossfade 2s = "perfect" under Vinny. This is the channel's music answer; `make_music.py` is not needed here.

**6d. The thumbnail pipeline works end-to-end** once the channel.json `thumbnail` block exists. The canary's `make_thumbnail` exit-1 was purely the missing block, not a code bug. Match new channels' thumbnail blocks to a known-good one (prehistoric-disasters) — colors are RGB arrays, scrim is a sub-object, font is the repo-relative `shared/fonts/Anton-Regular.ttf`.

---

## 6e. THE BATCH RUNBOOK (proven 18 June — `run_batch.py`)

`run_batch.py` runs a folder of `<name>.md` + `<name>.thumb.json` pairs through the full unattended pipeline: prep → audio → (tiered render) → assemble → thumbnail → upload. Gates auto-accept; ships what it can, logs the rest.

**Flags (confirmed from `--help`):**
- `--inbox INBOX` *(required)* — folder of `.md` + `.thumb.json` pairs. Pairs on `md.with_suffix(".thumb.json")` — **dotted `.thumb.json`, confirmed**.
- `--channel CHANNEL` *(required)* — **hyphenated DIR name** (`you-had-to-be-there`).
- `--kling-count N` — first N beats Kling, rest Ken-Burns; **`0` = all Ken-Burns** (this channel's batch default).
- `--plan` — free dry run: validates pairing + thumb spec, no parse, no spend. Always run first.
- `--limit N` — process at most N (subset testing / the single-video canary).
- `--publish-start ISO+tz` — first video's publishAt, **timezone-aware required** (naive rejected). CET in June = `+02:00`.
- `--publish-interval-hours N` — spacing (default 12; this channel wants **24** for one-a-day).
- **Omit both publish flags = private-immediate** (the first-batch default).

**The exact proven sequence (laptop → box → run):**
1. **LAPTOP** — stage the 20 files (10 `.md` + 10 `.thumb.json`) in one folder; confirm count.
2. **LAPTOP** — make a fresh clean inbox on the box and scp in (`ssh … "rm -rf …/batch_inbox && mkdir -p …/batch_inbox"` then `scp -P 443 …/*.md …/*.thumb.json peter@…:…/batch_inbox/`). **Brace-expansion `{a,b}` fails over scp** — list patterns separately.
3. **BOX** — normalize headers: `sed -i 's/^channel: you_had_to_be_there/channel: you-had-to-be-there/' …/batch_inbox/*.md`. (Mind the prompt — box vs laptop; the `sed`/run all happen on the box.)
4. **BOX** — confirm prereqs: `ls …/music/` (tracks present) + `python -c "...print('thumbnail' in d, 'music' in d)"` → both True.
5. **BOX** — `set -a; source .env; set +a` then `--plan`. Want **N planned, 0 skipped**.
6. **BOX** — real run, long & unattended, under `nohup`: `nohup python shared/run_batch.py --inbox …/batch_inbox --channel you-had-to-be-there --kling-count 0 > batch_run.log 2>&1 &` then `tail -f batch_run.log`.

**Operational cautions:**
- **NEVER `systemctl --user restart mission-control` while a batch runs** — cgroup teardown kills the in-flight run.
- Run long batches under `nohup`/`tmux` so an SSH drop doesn't kill them.
- The manifest (`_batch_manifest_*.json`) lists per-video status — read it for partial failures after the run.
- channel.json is source-of-truth: edit on LAPTOP → push → `git pull --no-edit` on BOX. **Peter works CLI-only — no manual file edits**; use a `python3 - <<'PY'` json-parser block to write config blocks, with a `.pre_*` backup first.

---

## 7. Title backlog

Launch title **"10 Things '70s Parents Did That Would Be Illegal Today"** is the template. **Batch one (10, rendering 18 June)** drew the workhorse list slots:

**Batch one — IN PRODUCTION (all warp-safe VISUALs, anti-dip opens, ~7–8 min, kling_count 0):**
1. `90s-parents-illegal` — 10 Things '90s Parents Did That Would Be Illegal Today
2. `70s-banned-toys` — 12 Toys From the '70s That Are Banned Today (→15)
3. `60s-kitchen-vanished` — 10 Things Every 1960s Kitchen Had That Just Vanished
4. `70s-school-rules` — 10 School Rules From the 1970s That Would End a Teacher's Career Today
5. `80s-fun-illegal` — 13 Things '80s Kids Did for Fun That Should've Been Illegal (→16)
6. `90s-before-internet` — 15 Things '90s Kids Did Before the Internet Changed Everything (→18, rapid-fire)
7. `75-pocket-change` — 10 Things You Could Buy With Pocket Change in 1975
8. `70s-baffle-gen-alpha` — 10 Everyday '70s Things That Would Completely Baffle Gen Alpha (the two-audience bridge)
9. `80s-no-helmet` — 12 Dangerous Things Every '80s Kid Did Without a Single Helmet (→15)
10. `80s-snacks-gone` — 10 Snacks Every '80s Kid Begged For That Are Gone Forever (→13; warp-safest, food still-life)

**Spent canary:** `80s-after-school` ("10 Things '80s Kids Did After School…", "GONE TILL DARK") — rendered solo to prove the unattended path; edited in Studio (first 3 beats cut for warp/blank stills before the warp-safe pass existed). Not in batch one.

**B. Decade-immersive (home-turf register):** What Summer Really Felt Like in 1975 · A Saturday Morning in 1984 · Growing Up in the 1960s — The Last Analog Childhood · What a 1970s Shopping Mall Was Actually Like · The Last Generation That Played Outside Until Dark · A 1980s Family Road Trip.

**C. Gen Alpha vs Boomer-kid (two-audience bridge — likely core pillar):** A Kid From 2025 Tries to Use a 1970s Telephone · Gen Alpha vs the Cassette Tape · If a 10-Year-Old From Today Spent One Day in 1979 · The TV Had Four Channels and No Remote.

**D. Seasonal:** Christmas Morning in 1978 · Halloween in the 1970s.

**Sequencing:** lead with the list format (proven, searchable) to lock the audience and let the algorithm categorize tightly, *then* widen into immersive and Gen-Alpha.

### The 26 June levelling top-up — shipped (2 videos)

*Two YHTBT videos staged via `stage_batch.py` and run through the batch-of-batches to bring the channel to the common 09 July levelling tail. Published 08–09 July at 01:00 CEST, `kling_count 0` (all-Ken-Burns, the channel default). SHIPPED — do not re-author.*

- **`gen-alpha-1979`** — the Gen-Alpha-vs-boomer-kid bridge (category C; a today-kid dropped into 1979). The two-audience pillar in production.
- **`growing-up-60s`** — the decade-immersive "Growing Up in the 1960s / the last analog childhood" register (category B).

*These draw from the immersive (B) and Gen-Alpha (C) lanes rather than the list format (A) — consistent with the widen-after-the-list-locks sequencing once batch one's list slots were live.*

---

## 8. Live state & next-session backlog

**Live state (18 June):**
- **Episode 1** ("10 Things '70s Parents…", `h0_zS8P6p8U`) — live, uploaded manually. Best traction on the channel (~427 views, AVD 183s) but the channel is still pre-distribution.
- **Gaming series** (4-part `hi8_90s` batch) — rendered, cut in Filmora, ready to upload.
- **Canary `80s-after-school`** — proved the unattended batch path end-to-end (audio → tiered render → assemble → private upload); thumbnail + bed both confirmed good after channel.json fix; edited in Studio.
- **Batch one (10 videos)** — **FIRED & RENDERING** via `run_batch.py --inbox you-had-to-be-there/batch_inbox --channel you-had-to-be-there --kling-count 0`, private-immediate, under `nohup`. `--plan` returned a clean **10 planned / 0 skipped**; all prereqs green (8 music tracks in `/music/`, channel.json `thumbnail`+`music` blocks confirmed True). The 10 slugs + the spent canary are in §7. Verdict pass pending on completion.

**Backlog (priority):**
1. **Post-render verdict-pass automation** — Sonnet-vision QC sweep over `modea/` stills, flags warped/blank beats, returns beat numbers → optional auto-`restill_from_feedback.py`. The single highest-value hardening for unattended batches (§6b).
2. **Confirm `safety_tolerance:"5"` on the BATCH render path** (not just the review-page restill) — closes the blank-PNG class. `grep -rn "safety_tolerance" shared/`.
3. **Motion-direction on the stills review** — per-beat MOTION → Kling prompt. Deferred behind 6a (motion is a later upgrade for this lane, not launch).
4. **Decade-look Phase 2** — write+commit `film_emulate.py` grade presets, wire one grade pass into `assemble()`; patch the review-server restill path to resolve the per-job look.
5. **Batch exit-gate for multi-video-from-one-job** — single-video auto-upload works; the one-job-→-many-cut path still must exit at `final_video.mp4`.
6. **Multi-project / daemonized review server** — project-in-URL refactor; and the cgroup-teardown fix so `mission-control` restarts don't kill in-flight runs (`systemd-run --user --scope` or double-fork+setsid).

---

## 9. NEXT CHAT — START HERE

**Primary objective: the verdict pass on batch one.** The 10 finished rendering private-immediate, all Ken-Burns. Judge the output and decide what's publishable, in order:
1. **Read the manifest** — `you-had-to-be-there/batch_inbox/_batch_manifest_*.json` and `batch_run.log`. Confirm 10/10 shipped; note any leg errors.
2. **Eyeball every video** (private uploads, or scp the `final_video.mp4`s down). Per video, check the three things that still slip through: **blank/black stills** (Flux safety reject → blank Ken-Burns), **object warping** despite the warp-safe pass, and **thumbnail + bed** landed.
3. **For anything flagged: single-beat restill, NOT a re-render.** `restill_from_feedback.py --project <p> --feedback '{"shot":N,...}'`, positive re-description leading with the dominant noun. **First confirm `safety_tolerance:"5"` is on the batch render path** (`grep -rn "safety_tolerance" shared/`) — still unconfirmed there; it's the blank-PNG fix.

**Then: publish decision.** Once the clean ones are confirmed, schedule them — by hand in Studio for batch one, or note that the *next* batch runs with `--publish-start <ISO+tz>` + `--publish-interval-hours 24` (one a day).

**The strategic question to open once judged:** did the anti-dip cold open + warp-safe stills move the numbers? Pull the early curve via NexLev on the first published videos — retention shape (did we kill the ~0:20 cliff?), CTR on the bold thumbnails, AVD in the first 48h. **We're at "read the curve"** in the ship-one → read → scale loop; that feedback decides the batch-two template before authoring it.

**Carryover (don't lose):**
- **Push this updated doc to the repo** — laptop `shared/docs/_you-had-to-be-there.md` → commit → push → `git pull --no-edit` on box. (Not yet done.)
- **Confirm `safety_tolerance:"5"` on the batch path** (also backlog #2).
- **Music-video duplication fork still unresolved** — the live `13 Totally Illegal…` music video vs. the session script that duplicates it. Decide: kill / differentiate / merge.

---

*Maintained by Peter + Claude. Bump and note the change whenever a run banks a lesson that changes how this channel is written or configured. Sibling docs: `__PIPELINE-CANONICAL.md` (umbrella), `_ante-machinam.md` (craft), `_machina.md` (operations).*
