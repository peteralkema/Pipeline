# Session Notes — You Had To Be There: Launch Build

**Date:** 2026-06-08 → 09 (evening session, ran into the night)
**Outcome:** Channel "You Had To Be There" launched. First episode authored, voiced, stills reviewed, animation running overnight. A pile of cross-channel pipeline upgrades surfaced and prioritised.

---

## ⏭️ START HERE NEXT SESSION — Prioritised Backlog

> These are the features/fixes that launching this channel surfaced. Most benefit **every** channel, not just this one. All go through the standard workflow: laptop → GitHub → box via idempotent patch scripts, `git pull --no-edit` before push, validate in sandbox first, no hand-editing on the box.

**P1 — Kill the stills-review tunnel friction (with auth).** *Promised as the immediate next build.*
The review step is currently: box server on localhost + SSH `-L` tunnel from laptop + browser to `localhost:8001`. Fragile, bites every video (server dies on window close; stacked tunnels collide on the port; `channel N: connect failed` = tunnel alive but server dead). Fix: bind `serve_review.py` to `0.0.0.0`, browse straight to `http://<box-ip>:8001`, no tunnel.
**Non-negotiable: ship with auth.** The server has `AI fix (claude-sonnet-4-6)` and `fal` Flux wired — an open public port is a *spend-capable* endpoint that port-scanners find within hours. Required: public bind + secret token check (`?key=...`) + open only port 8001 in `ufw` (to home IP if static, else generally). ~20 lines + 2 ufw commands. **Do not ship the public bind without the token.**

**P2 — The "Inworld layer" patch (one careful session on the shared TTS function).**
Three things in `recreation_pipeline.generate_voiceover` (payload built ~lines 627–634, function ~660):
- **Wire `speed`** — currently sends only `voiceId` + text; the `channel.json` `speed` key is ignored. Add to payload, **backward-compatible** (Final Hours has no speed key — must behave exactly as today). Confirm Inworld's speed field name before shipping.
- **Fix voice drift from chunking** — chunks at sentence boundaries → many Inworld calls → Vinny's character re-rolls slightly per chunk → audible drift over a long read (Peter noticed it). Send fewer/larger chunks (Inworld supports long input) and/or pin a seed if exposed. *Ask Peter to paste `generate_voiceover` (≈660+) before patching.*
- **Kill hardcoded gate labels** — gate prints "Victor voiceover" / "Synthetic beats" regardless of channel. Read voice from channel.json. (Channel-agnostic violation; cosmetic but wrong.)

**P3 — fal `safety_tolerance: "5"` on the Flux call.**
Default tolerance silently returns a ~7KB **black PNG** on prompt rejection, no error. Hit shot 003 this session (innocuous beat). Pass `safety_tolerance: "5"` on the Flux call in the still generator. Tiny; ride it along with another box-touching patch.

**P4 — Mode A gate printed-path fix.**
Build-page line is inserted (patch shipped), but the gate still prints the project path *without* the channel prefix (`70s-parents/modea` vs `you-had-to-be-there/projects/70s-parents/modea`). Fix at source in `shared/modea_leg.py` (~lines 191–197). Tiny; fold into any box session.

**P5 — Per-beat MOTION direction (the big feature). Do AFTER watching video one.**
Upgrade the review page from "judge the image" to "judge *and direct* it":
- New `MOTION:` textarea per shot in `make_review_page.py` (alongside Notes/Override).
- Persist per-shot in the exported feedback JSON (rides existing save).
- **Load-bearing piece:** `--animate-only` in `recreation_pipeline.py` reads the per-shot motion text → passes as Kling `prompt`, channel gentle-default when blank.
- **Optional per-shot "preview motion" button** — reuse the on-demand single-shot pattern already in `serve_review.py` (the AI-fix button), pointed at Kling (~$0.15–0.20/render). Worth it for the first-60s shots that decide retention; the rest ride the default.
- *Why after video one:* default gentle motion may be fine for ~80% of shots; seeing the finished cut tells us how much per-shot control is actually needed.

**P6 — Wire `film_emulate()` into `assemble()`.**
Deterministic per-decade grade (`film_emulate.py`: super8_70s / sixteen_mm_50s / vhs_80s) exists, not called. Wire as a **single final ffmpeg pass** over `final_video.mp4` (uniform stock across all beats, cheap) — not per-clip. `assemble()` at `recreation_pipeline.py` ~801; existing `shared/patch_assemble_ffmpeg.py` / `shared/assemble_ffmpeg.py`.

**P7 — Schema extension / assembler silence.** Only if/when routine need appears.
- channel.json `animation`/`look` blocks (Kling motion default, negative prompt, grade preset) — extend the reader only when per-channel control becomes routine. Until then, unread keys are clutter.
- Authored inter-beat silence in the assembler — only if `[pause]` stacking proves insufficient. Touches the no-gaps "Lego rule"; real architecture change.

---

## What We Shipped Tonight

- **Channel created:** You Had To Be There, handle `@you-had-to-be-there` (locked). Folder `you-had-to-be-there/`, channel.json name `you_had_to_be_there`.
- **channel.json** written to the real 5-key schema (name, voice_id, style_suffix, default_music_prompt, base_canon). Voice `Vinny`. Super-8 1970s look baked into `style_suffix` (the wired look layer — why stills came out period-correct first pass). `"speed": 0.9` present but confirmed dead (not read).
- **Script v3** ("10 Things '70s Parents Did That Would Be Illegal Today"): 52 beats, ~1,900 words, scene-setting beat per item, 13-item over-delivery (title says 10), `[pause]` pacing, sparse `[laughs]`/`[sigh]`. Parsed clean.
- **Voiceover:** Vinny, 8.7 min, markups perform correctly, pauses land. Approved at audio gate.
- **Stills:** 52 rendered (~$1.50), reviewed, one black (003) fixed at the gate. Approved.
- **Animation:** Kling kicked off overnight (~$8–10 on 52 beats). Will assemble then stall at upload gate (no OAuth — expected).
- **Two docs:** the channel Launch & Operating doc (now v1.1) and these session notes.

---

## Key Learnings Banked Tonight

**The duration-header trap (cost us real confusion).** The concatenated voiceover MP3 has a malformed duration header — desktop players read ~**double** the truth (real 6:31 showed as 12:42). We briefly celebrated a "12:42 brilliant long read" that didn't exist. **Always trust `ffprobe`** (and Whisper, which agrees): `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voiceover.mp3`. The media player is the liar.

**Vinny reads fast — ~190 wpm.** ~1,900 words → 8.7 min. For a true 10+ min, write ~2,200 words (more *content*, not slower delivery). Don't chase the last 90 seconds — 8–9 min of good Vinny beats 11 min of padding and still earns multiple mid-rolls. (Peter's call: 8.7 is fine for video one. Correct call.)

**`[pause]` works, tested empirically.** One `[pause]` is too short; **four stacked** gives a real breath between items. Single `[pause]` scattered helps rhythm. Markups `[laughs]`/`[sigh]` perform (real laugh/breath), not spoken aloud. The parser passes all markups through as "words" (a lone 4-stack pause-beat did NOT halt the build — good to know).

**The speed knob is not wired.** `generate_voiceover` sends only `voiceId` + text. The `channel.json` speed value does nothing today. Pacing came entirely from pauses + word count. (→ P2.)

**Voice drift is real and it's the chunking.** Sentence-boundary chunking → many calls → per-chunk character re-roll → subtle inconsistency over a long read. Peter heard it. Fix is fewer/larger chunks. (→ P2.)

**Motion-prompt mental model (for P5 and for writing motion later).** The still is the *scene*; the motion prompt is the *direction* — what changes over ~5s. Never re-describe the picture. Name subject-motion AND camera-behaviour separately. Anchor direction to the frame ("away from camera," not "forwards"). Small/slow motion wins twice: most believable AI *and* most period-authentic (home movies were gentle). Punchline beats → near-zero motion; establishing → slow drift; close → gentlest push.

**16:9, not 4:3.** Period feel comes from the grade, not the frame shape. 4:3 would pillarbox and shrink the packaging surface. Squarish channel later = just add width/height to channel.json.

**Over-deliver the count.** Title "10," deliver 13 via a "three more I couldn't leave out" coda before the close. Over-delivery delights and the "I said ten, but…" line is a retention hook right where drop-off is worst. Thumbnail stays "10."

**The closer line** ("you had to be there") is a recurring *sign-off* only — never a cold-open prefix or branded intro (hurts retention/CTR).

---

## Strategy Recap (for continuity)

Picked nostalgia via NexLev against the 5 Leo criteria (monetized, <100k subs, ~20k+ avg views, viral last 6mo, reproducible in our pure-AI cinematic machine for an AI-indifferent audience). Key reframe: the best niche *demands* generated footage. Nostalgia won on fit × payoff × AI-indifference (RPM ~$3.6–5.1, 40–70 audience that doesn't care it's AI, the machine's home register). Our edge over incumbents (Memory Trails, American Rewind — static photo-pans): **motion** they can't match. Proof full-AI works: Professor Blackwood. Direct title ancestor: Americana Rewind's 633k-view "10 Things '70s Parents…" (we wrote our own from scratch). AI animal drama banked as the high-volume #2 for after batch mode; finance dropped (best RPM, nothing cinematic to recreate). Full detail in the Launch doc §3.

---

## Behavioural Note (process, not pipeline)

Peter's instinct to go bolder paid off twice tonight — Vinny over the safer Phil read, and pushing the script past a thin first cut. "I need to learn not to play safe." The safe choice is usually the average one, and average doesn't get noticed. Worth carrying into the next ten decisions.

Also: documentation written *as work is banked*, not after — both docs exist before video one is even uploaded. Keep that discipline; it's what makes channel three faster than channel two.
