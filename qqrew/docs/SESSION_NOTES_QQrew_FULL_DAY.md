# SESSION NOTES — @Q-Qrew BUILD DAY (full record)
**Date:** 29 Jun 2026 (mammoth single-day session)
**Operator:** Peter Alkema (The Hague) — YouTube Media Flywheel, solo
**Outcome:** A brand-new channel (#12) taken from frustration-with-Final-Hours → designed → cold-open proven → full ~7-min episode authored, variety-passed, rendered true-static → thumbnail system tuned to repeatable → channel named, branded, handle claimed → **SHIPPED**. The "anti-Final-Hours" bet, placed.

> Read alongside the three handover docs that opened the session: `NOTE_final_hours_bias_in_canonical.md`, `crew_character_bible.md`, `_Crew.md`. This doc is the NARRATIVE (what happened, decisions-in-context, features uncovered). The standalone reference is `_QQrew.md` (channel doctrine). The canonical fix is `CANONICAL_PATCH_de_final_hours.md`.

---

## 0. THE PIVOT (why this channel exists)

Today began in frustration with **Final Hours** — a channel fighting distribution despite good craft. The strategic move was NOT to keep grinding it but to **spin the Flywheel into a new lane**: a bright, fast-cut, character-driven, flat-illustrated explainer channel — the deliberate *opposite* of Final Hours' cinematic-slow-faceless-dread. Same pipeline, totally new brand/look/register. This is the Flywheel thesis working as designed: the production system is the moat; any single channel is an experiment; the right answer to a stalled channel is another cheap roll of the dice in an adjacent lane, judged on the 48h signal.

**What today validated:** that the machine can BUILD it (character holds, pipeline renders 7 min, packaging tuned). **What today did NOT validate:** demand — whether *this* lane pulls CTR+AVD for *this* channel. That signal begins ~48h after publish. Doubts are correct and are the entire point of shipping; only the upload resolves them. The roll is cheap (≈ low-double-digit dollars/episode, see §9), which is what makes the bet affordable.

---

## 1. CHRONOLOGICAL ARC OF THE DAY

1. **Design handover** — opened with three docs: the Final-Hours-bias note (the craft-vs-mechanics distinction), the crew character bible (Driver locked, Brain+Skeptic specced), and `_Crew.md` (channel doctrine, pre-render). Driver: young man, denim jacket, tan backpack (signature), dark glasses (accepted, not fought), Evan voice @1.05.
2. **Cold-open proof** — rendered an 11-beat cold open end-to-end. Driver held glance-level consistency across cuts + a setting change + one motion pass. Flat-cel held, no photoreal drift. **Final-Hours bias decisively broken.** Channel PROVEN at the pilot tier.
3. **Two portfolio bugs found + patched** (see §4): the MC/CLI canon divergence, and the silent best-of-2 thumbnail-judge cap.
4. **First full attempt (soap, 53 beats)** rendered to 1:42 — revealed the **length-scoping error**: a cold-open-length script rendered as a full video. Wrong for the lane.
5. **Length correction** — re-authored to the full ~7-min episode (249→238 beats after a variety pass), the session's headline craft finding.
6. **Full render** — 238 beats, true static (after discovering Ken-Burns was too busy over 200+ cuts), 7:22, durations matched, complete.
7. **Thumbnail system tuned** — the longest single thread; took the thumbnail from "fight it every time" to a locked config (see §3).
8. **Channel named + branded** — @Q-Qrew claimed; banner (the crew in an Egyptian hall) + avatar (Driver shocked face) set.
9. **Audio-reset diagnosis** — identified the per-beat voice "seesaw" and its architectural fix (the #1 feature priority, see §5).
10. **Wide-angle insight** — the Roman bath establishing-wide banked as a high-value still class (see §6).
11. **SHIPPED.**

---

## 2. THE EPISODE (soap — "Humans Went 200,000 Years Without Soap")

- **Script:** `soap_full_v2.md`, 238 beats, fast-cut (1-15 words/beat after variety pass), {driver}-tagged (102 tags, 42% presence), 9 sections. Chronological evidence-walk: cold open → prehistory → Egypt (natron) → Babylon (first soap) → Rome (oil+strigil) → medieval collapse (bathing-as-dangerous, perfume-masks-rot) → **Semmelweis (55-beat climax)** → Lister/Pasteur vindication → ring-close.
- **Render path (proven, reuse this):** `ingest.create_project` (zero-spend verify → beats:238) → hand-inject `canon.json` (copy from a prior proven project) + `render_policy.json {kling_count:0}` → `orchestrate.py --unattended`. Then the static re-assemble (§ below) to kill Ken-Burns.
- **Final asset:** `final_video_static.mp4`, 7:22 (441.77s), matched voiceover (442.02s, delta 0.25s). All 238 stills + 238 static clips. **This — not the Ken-Burns `final_video.mp4` — is the keeper.** (Ken-Burns version preserved as `final_video_kenburns.mp4`.)
- **Verdict (Peter, on watch):** "very very very very good." Character holds, near-zero drift, script + visuals work, pace constant, static reads clean. Two issues flagged: the audio seesaw (→ §5 priority) and that Ken-Burns was too much (→ resolved, static).

---

## 3. THUMBNAIL SYSTEM (tuned to repeatable — the longest thread)

The final thumbnail: **"NO SOAP?" (white) / "FOR 200,000 YEARS" (gold)** top-left, over a hugely-shocked Driver pushed hard right, on a flat saturated gold background, full brightness. Curiosity-gap live (no soap in frame). Peter hand-fixed the right-push externally; the config carried the rest.

**Doctrine banked (all proven this session):**
- **Subject = a REACTION beat** (huge shocked/disgust expression), never a calm portrait. Emotion stops scrolls.
- **Character pushed RIGHT, left empty** for the top-left headline.
- **NO ECHO** — image never shows the headline's noun (no soap on screen). Matched image+text = caption consumed, no click. The gap forces the question.
- **Flat saturated pop-background > busy scene.** The clean gold popped far better than any cinematic still. Thumbnail ≠ cinematic still — different job.
- **margin_y: 20** — the proven value across final-hours / you-had-to-be-there / sacred-dawn (all use margin_x:40 / margin_y:20 / title_area_pct:0.52 / title_start_size:150). crew had inherited a WRONG margin_y:48 from success-coach (text floated down). **This was the "boooom" fix.** Reuse the proven block for any new channel; never clone thumbnail config from success-coach.
- **Kill ALL THREE darkening sources for flat-pop backgrounds** — the "house look" is three-deep and stacks: `darken_factor` (global → 1.0), `scrim` (directional gradient → width:0/opacity:0), `vignette_strength` (radial → 0.0). Killing one at a time is whack-a-mole; we hit all three sequentially before the composite matched the raw still. The white headline's own black text-outline carries legibility over flat bright color. **Style-coupled:** these exist for text over BUSY/dark stills and should return for any busy-scene thumbnail. Diagnosis method: A/B the composited thumb vs the raw still; any darkness delta = a house-look layer still firing.
- **MODEL PRIORS ON flux-pro/v1.1 ARE NOT PROMPTABLE.** Tried to remove the beard via subject (3× negation) AND via a rewritten channel candidate_prompt_suffix (positive assertion) — beard survived BOTH. Same for centering ("push right" ignored at suffix level). **When the model has a strong prior (bearded illustrated guy w/ glasses; centered portrait subject), you cannot prompt it away.** Options: design WITH it (accept the beard / make the canon Driver bearded), OR composite from a full-scene video still (those come out clean-shaven — the close-up portrait genre is what summons the beard), OR fix in post. (This is the glasses lesson, re-confirmed.)
- **Repeatable now working automatically:** canon `{driver}` resolves in the thumbnail subject; the vision judge runs when FAL_KEY + ANTHROPIC_API_KEY are in the shell. New-channel thumbnails inherit canon + margin + suffix.

---

## 4. BUGS FOUND + PATCHES WRITTEN THIS SESSION

| Patch | What | Status |
|---|---|---|
| `patch_crew_channel.py` | wrote crew-wip channel.json + rulebook (voice Evan, flat-cel suffix, base_canon driver, category) | applied |
| `patch_thumbnail_canon.py` | (a) expand `{driver}` in thumbnail --subject before Flux; (b) fix silent best-of-2 judge cap (was `candidates[:2]`, winner∈(1,2); now all-N + 1..N) | applied, committed |
| `patch_crew_thumb_margins.py` | margin nudge — **SUPERSEDED** by the margin_y:20 proven-value fix; discard | written, not the keeper |
| `patch_crew_thumb_suffix.py` | rewrote candidate_prompt_suffix clean-shaven/right-push — **DID NOT beat model priors** (see §3); informative failure | applied, didn't win |
| `reassemble_static.py` | post-hoc true-static re-assemble (reads each clip's baked duration, rebuilds still frozen, concat+mux). Zero fal spend. **The seed for Patch B.** | applied, PROVEN |
| margin_y + darken/scrim/vignette | direct channel.json edits (not patch files) — the actual thumbnail fixes | applied |

**Still-broken / banked (the judge):** vision-judge JSONDecodeErrors on the box even with both keys loaded (confirmed set). Falls back to candidate 1 silently — affects ALL ~60 prior portfolio thumbnails. Diagnostic banked: run a bare `anthropic.messages.create(model='claude-sonnet-4-6'…)` on the box to see if it's the model string / SDK version / a non-JSON response. NOT a blocker (candidate-1 is fine), but "best-of-N" has never actually run on this box.

---

## 5. FEATURE PRIORITIES UNCOVERED (the to-do, flagged for the master worklog tomorrow)

**P1 — AUDIO RE-ARCHITECTURE (the "seesaw voice" fix). HIGHEST.**
Root cause: one-beat-one-TTS-call. Every beat is a separate Inworld synthesis with a fresh prosody onset → the voice "jumps back up" at the start of each beat → over 238 beats, 238 little re-attacks. Peter's framing ("multiple stills per beat") is the right goal, inverted mechanism: the fix is FEWER, LONGER audio segments, not more stills. **Synthesize a RUN of beats (a section, or a sentence-group) as ONE continuous Inworld call, then Whisper-align to find each beat's word-timestamps in that continuous audio, and cut the stills to those timestamps.** Voice flows as one breath; visuals still cut fast underneath. This decouples the AUDIO unit from the VISUAL (beat) unit — the beat is a visual unit, not necessarily an audio unit; conflating them is the design flaw. Build sentence-group first (3-5 beats, safer alignment), prove it, then maybe section-level. **Portfolio-wide improvement** (every channel's voice gets more continuous). Touches parse_script.py (group beats into audio-runs), the audio leg (batch synthesis), and the alignment→still-timing map. Fresh-session surgical build.

**P2 — Patch B: TRUE-STATIC native in the pipeline. PROVEN, SEEDED.**
`kling_count:0` still applies Ken-Burns zoompan (`_still_to_held_clip`), not true-static. Static beats Ken-Burns for this fast-cut channel (the cut is the motion; zoompan is noise over 200+ beats). `reassemble_static.py` is the working post-hoc seed. Graduate it: add a no-zoompan `--static` path to `_still_to_held_clip` so static renders natively (no hand-reassemble). It's the channel default now.

**P3 — Patch A: canon + render_policy AUTO-WRITE at create.**
`ingest.create_project` writes NO canon.json (the MC/CLI divergence) and no render_policy. Every project this session needed manual canon-injection + `echo '{"kling_count":0}'`. Closing this removes two manual steps and the raw-`{driver}`-ships risk.

**P4 — Vision-judge JSONDecodeError fix.** (see §4) — portfolio-wide silent fallback; diagnostic banked.

**P5 — Channel-agnostic UPLOAD step + batch exit-gate.** (carried from the session's opening priorities) — single-video jobs auto-upload with per-project metadata (category Education/27 for QQrew, NOT Entertainment/24); batched jobs exit at final_video for manual cut. Until built, uploads are manual.

**P6 — `--unattended` is NOT fully unattended.** It still hits a Mode A stills-review gate (the MC "Ctrl-C then type go" gate), cleared with "go" this session. Either budget a manual gate-clear in batch runs or build a true-unattended flag.

**Lower / banked:** the WIDE-ANGLE establishing-shot still class (§6) as a deliberate authoring pattern; Brain + Skeptic character validation (next characters); decade-look / film_emulate (other channels); multi-project review server.

---

## 6. THE WIDE-ANGLE INSIGHT (new, high-value — Peter flagged on the Roman bath still)

The crowded Roman-bathhouse establishing-wide (no crew in frame) is a **distinct, high-value still class** the channel should use deliberately and often. It works BECAUSE the crew is absent: it's the scale-and-spectacle "establishing shot," the world carrying the beat instead of the character. Three jobs at once:
1. **Variety** — breaks the character-foreground rhythm; the visual exhale between Driver beats.
2. **Drift-relief** — no face in frame = zero character-drift risk on that beat (free consistency).
3. **Production-polish signal** — a rich, populated, cinematic wide reads as "made with care," elevating the channel above flat-stick-figure incumbents.

**Authoring rule banked:** the channel has TWO still classes — (a) character-foreground (Driver carries the beat) and (b) crew-absent establishing-wides (the world carries the beat). Deploy wides at section-openings / scale-reveals / "behold the place" beats. They are NOT a compromise on the recurring-character premise — they're the counterpoint that makes the character beats land. Spec wides explicitly in the script's VISUAL lines (wide aerial / crowd / architecture, no {driver}).

---

## 7. STATE AT SHIP

- **Channel:** @Q-Qrew, handle claimed + available. Banner (crew in Egyptian hall) + avatar (Driver shock face) set. Description: "Big questions, fast answers. The Qrew investigates the strange, the buried, and the unbelievably true." Category: **Education (27)**, not Entertainment.
- **Video:** static 7:22, title "Humans Went 200,000 Years Without Soap. How Did We Survive?", full description w/ chapters (timestamps need a scrub-pass to make exact — built from section structure, approximate), tags.
- **Config locked for the channel:** voice Evan@1.05, flat-cel style_suffix, base_canon driver, thumbnail block (margin_y:20, darken 1.0, scrim 0/0, vignette 0), category 27, static motion default.

---

## 8. NAMING DECISION (banked)

**@Q-Qrew** — double-Q ("lots of Questions"), Qrew = Crew on a Quest, distinctive-earns-a-second-look. Handle confirmed available + claimed. Naming logic: for a **faceless feed-discovered channel, distinctiveness > first-sight sayability** — discovery is the thumbnail in the feed, not verbal word-of-mouth; the handle's job is a distinctive label on the channel page, not a spoken token. (Kurzgesagt/Veritasium precedent: unsayable on sight, distinctive enough to lodge once seen.) The only real risk for a clever handle is reconstruction-ambiguity from sound — mitigated here because nobody types the handle, they click thumbnails. Supersedes the `_Crew.md §9` "name it don't describe it" shortlist (Trove/Kove/Vyse/Fathom etc.) — those were the out-loud-test survivors; Q-Qrew was chosen for distinctiveness over that test, deliberately.

---

## 9. COST (to confirm)

This job: 238 Flux-pro stills + ~7 thumbnail re-roll candidates. NO Kling (static = free ffmpeg). The pipeline does not log cost (render.log has no spend line) — the authoritative source is the **fal.ai dashboard, filtered to 29 Jun**. Estimated bracket (per-image rate not quoted, estimated): **~$8-16 for the night** incl. re-roll overhead. **Get the real number and bank the per-EPISODE unit cost** — that's the figure that governs how freely Peter can experiment (≈$12/episode → 50 experimental videos for ~$600 → the Flywheel "diversify cheaply, cull without sentiment" economics made concrete). Note: tonight included thumbnail re-roll tax (fighting the beard before the config fixes); steady-state per-episode is the clean 238 stills + 1-2 thumbnail candidates, slightly lower.

---

## 10. THE DOCTRINES BANKED TODAY (cross-reference — these graduate to canonical)

1. **Length doctrine:** fast-cut ≠ short. Write MANY fast beats (220+ for a 7-min lane), not few. Each era → its own mini-arc; biggest single arc carries the climax (Semmelweis = 55 beats). Vary beat length (1-2 word punches + 10-15 word breathers) so the cadence syncopates, not drones. Concentrate the recurring character at the bookends; objects carry the dense middle (Driver 75% cold-open / 27% Semmelweis).
2. **Motion doctrine:** true-static is the default for fast-cut; the cut IS the motion; Ken-Burns is noise over 200+ beats.
3. **Thumbnail doctrine:** reaction-subject, character-right, no-echo, flat-pop-background, margin_y:20, all-three-darkening-off, model-priors-not-promptable. (Full in §3.)
4. **Wide-angle still class:** crew-absent establishing-wides as a deliberate counterpoint to character beats. (Full in §6.)
5. **Audio doctrine (to BUILD):** audio segment ≠ visual beat; synthesize runs continuously, Whisper-map stills. (Full in §5/P1.)
6. **The meta-learning:** Final-Hours DNA infected the "channel-agnostic" canonical because it was built first; channel-specific craft (and CODE) leaked into the agnostic layer. (Full in the canonical patch doc.)
