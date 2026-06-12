# Final Hours — Channel Doctrine
*The single consolidated channel reference for Final Hours (@FinalHours_history). Load this — with the four `_` system docs — on any Final Hours session. Consolidates `final-hours-strategy.md` (30 May) and both backlogs (`backlog.md` 30 May, `final-hours-backlog.md` 31 May) into one comprehensive brief.*
*Consolidated 11 June 2026. Retires the three source docs. The `_` prefix floats it to the top of `shared/docs/`; channel-scoped, load-on-demand.*
*[Current-reality flags: the source docs predate several shifts and are corrected inline with **[CORRECTED]** markers — the channel moved from a 7-minute / 84-beat fixed grid to **long-form (12–16 min, city-catastrophe 20–32 min)**; Peter relocated **Kraków → The Hague**; the **Hetzner box is live**; the **face-never-resolved** register won the retention test; **Success Coach is out of scope** for this doc.]*

---

## 1. Identity

- **Name:** Final Hours · **Handle:** @FinalHours_history (Brand Account under peteralkema2@gmail.com).
- **Created:** May 2026. **Status:** live, **primary** channel. Has working OAuth/upload.
- **Format:** faceless; Inworld **Victor** narration; photoreal-painterly cinematic stills (fal Flux-pro) animated by fal/Kling; mournful drone-and-strings bed. **[CORRECTED] Long-form 12–16 min** (city-catastrophe sub-series 20–32 min) — *the original "7-minute / 84-beat fixed-grid" spec is retired; Mary Celeste data confirmed long-form earns ~3× the absolute watch time.*
- **Niche:** AI-recreated long-form history — *"the last hours of people and places history remembers."*
- **Repo:** `final-hours/`; `channel:` header `final_hours` → resolves to `final-hours/`.

---

## 2. Thesis

Final Hours is **not a "history channel."** It is a **dread-and-recognition recreation pipeline** — a system for taking one human story inside a catastrophe and rendering it in slow cinematic photoreal form for a few dollars a video. The frame is consistent: **the camera stays with one named (or deliberately unnamed) human while history happens around them.** Anne in her chamber, Hartley on the deck, the families at the Pompeii boathouses. The catastrophe is the *setting*; the dignity-or-cowardice-or-bewilderment of one person is the *subject*.

Three things make it defensible against trivial format-cloners:

**The rulebook.** An accumulating per-channel list of caught spell-breakers — anatomy errors, gravity violations, location drift, instrument drift, character-consistency failures. Every spell-breaker caught in stills review becomes a permanent negative rule. ~31 Final Hours rules in `final-hours/rulebook.json` over ~21 universal rules in `shared/rulebook.json`. Universal rules prevent universal failures (anatomy, gravity, illegible text); channel rules enforce period discipline (Edwardian uniforms render unreliably → default plain black; one ship per frame because the documentary-prior keeps duplicating vessels; image models can't render legible engravings → frame text obliquely).

**The canon mechanism.** A per-video block of named descriptors (`{hartley}`, `{band_deck}`) substituted into prompts wherever the subject recurs, so a character/ensemble can't drift across shots. Rule of thumb: **anything appearing in 3+ shots needs a canon entry** (drift is invisible at 1–2, glaring at 3+). Canon entries can reference each other recursively. Channel-level base canon is auto-merged into every beat-script.

**The beat architecture. [CORRECTED]** Originally "84 equal-length beats of ~13 words on a fixed grid." Now the channel authors against the **ante-machinam Constitution** (beat granularity ~5–12s spoken, ~15–35 words, hard ceiling ~55; one VISUAL per beat; spell out numbers; lock the script first; every beat carries an animatable foreground subject). Beats are no longer a rigid equal-length grid — they're sized to the narration, then assembly holds each clip to audio-measured duration.

Tools (fal Flux + Kling, Inworld, Whisper, ffmpeg, rembg) are commodity. The moat is the three layers above + accumulated production judgment.

---

## 3. Economics

- **Cost per video:** single-digit dollars in fal credits (Kling animation dominates), plus negligible Inworld/Claude. ~30–90 min unattended render, plus 2–4h stills review/reshoots that decrease per video as rulebook + canon expand.
- **Comparison:** Chloe vs History (closest format peer) runs an estimated $2,000–5,000/video. Final Hours runs at a fraction of that. **Dud-tolerance is the whole strategy** — most videos can do nothing, one breakout pays for many. Break-even per video is a few thousand monetised views (history RPM ~$5–8) vs her ~400k+.
- **Portfolio logic:** the pipeline is format-agnostic; Final Hours was the first channel, now one of several on the shared engine. Per-channel canon + rulebook compound independently.

---

## 4. Topic principles

Three filters:
1. **One human story inside a larger catastrophe** — not "the Titanic," but "Wallace Hartley on the Titanic." Anne's waiting, not Tudor politics. The signature framing.
2. **Dread-and-dignity register** — no action, mystery, conspiracy, or breezy explanation. Mournful, considered, slow. If a topic doesn't fit, it's wrong regardless of how interesting.
3. **Render-friendly visual range** — Tudor stone is easy; water at night harder; panicking crowds harder still. But each new era widens the rulebook in a way that compounds (maritime disasters are now much easier post-Hartley — the rulebook knows ships, night water, period uniforms, instrument continuity).

The "final hours" framing is the emotional anchor and should be visible in the title — time-quantified-dread ("one day to escape," "one day to die") or one-human-choice ("He Kept Playing," "She Wouldn't Jump").

---

## 5. Operating principles (banked across videos)

- **Three attempts is the line.** Reshot twice and still misbehaving = the model has a learned prior you're fighting; writing better prompts won't escape it. On attempt three, **reframe the concept** (wide ship shots → detail of funnel/hull lettering; Coach-style polished-male prior → switch models). Change the *technique*, don't negate the prior harder.
- **Canonise anything in 3+ shots** (the Hartley instrument/uniform/character drift lesson — expensive). Mandatory for every video now.
- **Rulebook prevents universal failures; canon enforces per-video continuity.** Don't mix the layers — universal → `shared/rulebook.json`, channel → `<channel>/rulebook.json`, per-video canon → the beat-script.
- **Auto-fallback makes unattended rendering possible.** Kling content-policy refusals (executions, casts, remains, the sinking) silently downgrade to held-still ffmpeg clips and continue; the pipeline doesn't halt mid-render. (Proven overnight on Anne Boleyn.)
- **People are the emotional core.** Broad anatomy negatives ("deformed hands") make models AVOID people (they satisfy the constraint with empty rooms). Use *specific* spell-breakers ("visible ribs through skin") + a positive `people_directive`. Most shots should include human figures; empty atmospheric shots are the exception.
- **Wide establishing shots fight the documentary prior** — reframe to close detail (hands on strings, the ticket on a desk, the violin in lantern light). A craft upgrade disguised as a workaround: detail keeps the camera with the human experience.
- **Image models can't render small legible text** (engravings, signs, numbers). Frame text obliquely, in shadow, or out of frame; tell the model it exists but is illegible; never rely on specific words.
- **Phantom hands** — empty scenes spawn disembodied hands at the edges. Frame tightly on objects; state "no body parts anywhere in the frame."
- **Flux-pro over Seedream** for faces — more ordinary, less catalogue-polished humans; slightly more painterly-cinematic (matches the aesthetic). Slightly higher per-still cost, worth it.
- **fal `safety_tolerance:"5"`** on the Flux call — default safety silently returns ~7KB black-PNG placeholders on rejection with no error.

---

## 6. Distribution principles (banked)

- **Retention-curve *shape* over all other metrics.** Studio AI summaries on small samples are noise; view-count/CTR averages on sub-50-view windows are noise. The curve shape (where viewers drop, where they re-engage) is the real diagnostic. Check at 100+ views minimum.
- **Cross-promote known fires, not new ones.** Let the algorithm cold-test each video 48h before pushing to owned audiences; pushing all videos flattens the signal of which one is worth pushing. Three pushes to the same audience in a week is fatigue.
- **Adjacent owned audiences are higher-signal than personal feeds.** Match the video's framing to the audience that fits (dignity-under-pressure → the old success-coach community; pure spectacle → less so). A portfolio of targeted seed pools, not one broadcast list.
- **Format competition is mostly an illusion on a recommendation platform.** Chloe's Titanic at 2.16M in the same neighbourhood isn't a competitor — it's proven-demand signal. Differentiate by *register* (dread vs vlog) and *length*, not topic avoidance. Same lane = tailwind if packaging is clearly different.
- **Schedule for 01:00 Europe/Warsaw** (~19:00 US Eastern) — puts publish at the start of US prime evening so the first impression-expansion test lands on the next active US evening. Built into `upload.py` (`--schedule-cet-1am`). *(Peter is now in The Hague — same CET window applies.)*

---

## 7. Live state (as of last sync — 31 May → carry forward)

| Video | Status | Signal |
|---|---|---|
| Pompeii v2 | Live (28 May) | **51% retention — channel high-water mark.** Ash closer banked as template. |
| Anne Boleyn | Live (29 May) | Cross-promo to X + SSC FB contaminated the algorithmic read — limited diagnostic value. |
| Hartley (Titanic) | Live (30 May) | First scheduled-publish. ~17% retention; CTR ~2.15%. "He Kept Playing." |
| Hindenburg | Live (30 May) | youtu.be/J1w2JkpG5xU. CTR 2.12% (74% above 1.22% baseline); AVD ~34s = 11.3% retention (lowest of any FH video). A/B thumbnail test (MrBeast-face vs on-brand Matilde). |
| Pudding Lane | Live (1 June) | youtu.be/f1LT9g1un_Y. **First face-never-resolved anonymous-protagonist video.** One canon char + four scene canons. "She Wouldn't Jump." |
| **Troy** | **In flight** | 154-beat, ~25-min episode. Whisper-drift bug fixed (`difflib.SequenceMatcher`); ffmpeg stretch bug fixed. **Pre-existing content bug: beat 107 (Laocoön serpents) silently dropped by TTS → needs voiceover regeneration as a follow-up.** Morning stills-review gate → `go` → full assembly completion. |

**The key open experiment — Hindenburg vs Pudding Lane retention:** named-ensemble + high biographical setup (Hindenburg) vs anonymous single protagonist + face-never-resolved + distributed sensory writing (Pudding Lane). If Pudding Lane retains better → **anonymity + single protagonist + face-never-resolved is the higher-retention register** (cascades into topic selection). If same → the retention problem is cold-open pacing / biographical-vs-tension density / shot rhythm, not anonymity. If worse → viewers may need a named human to bond with. **[CORRECTED/UPDATED] The face-never-resolved register has since been adopted as the default** (it carried into Sacred Dawn and the production-patterns doc) — but confirm against Pudding Lane's actual curve when the data is in.

**A/B thumbnail rule (banked):** stick with the on-brand option even if the MrBeast-face variant wins by 5–10%. Brand is the moat that compounds across all future videos; one video's marginal off-brand advantage is not worth it.

**Outstanding pinned comments:** Hindenburg (Matilde survived 35 more years — "what would you have done in those 34 seconds?"); Pudding Lane (the Monument bears the kings' and architects' names but not the woman who died first — "Hers was never written down").

---

## 8. Video-direction principles & candidate topics

**Choosing the next video:** (1) **build a topical cluster around whichever video shows life** — clusters compound algorithmically far more than topic variety; (2) **use the canon mechanism from inception** (no retrofitting); (3) **apply the banked pacing discipline** — distribute sensory density across 3+ locations (not 1), cap shots per scene canon (~10), audit voiceover duration with `ffprobe` before finish and regenerate if >10% off estimate.

**Candidate topics** (scaffolding, not commitments — pick on signal), flagged by protagonist-register:

*Strong anonymized-protagonist (if the face-never-resolved register validates):*
- **The Lusitania bandmaster** *(Anonymous)* — direct Hartley parallel, unnamed in most records; gives the canon mechanism a real test on an inherited archetype.
- **The Pompeii children at the Stabian baths** *(Anonymous)* — preserved skeletal posture, names lost; single confined location + eruption as environment.
- **The Mary Celeste** *(Anonymous)* — empty ship, ten people gone; protagonists present only by absence. *Possibly the most genuinely Final Hours topic in the backlog* (and the long-form watch-time data point).

*Strong named-protagonist (if named work needs another data point):*
- **The Donner Party** *(Named)* — Sierra Nevada winter, the day of the decision; James Reed as focal point.
- **Pliny the Younger watching Vesuvius** *(Named)* — his letters survive; strong "named witness to disaster."
- **House of Menander, Pompeii** *(Named)* — lavish interior, partially known residents; tests canon on named historical figures with archaeological grounding.

*Wild cards:* **The Wilhelm Gustloff** (9,000+ deaths, freezing Baltic, Jan 1945 — scale-of-tragedy; anonymous or single-protagonist viable); **The Tay Bridge disaster, 1879** (Sunday train, bridge collapse, no survivors). *(Gustloff was worked on — see the 10 June uploader/review-gate session.)*

---

## 9. Channel-specific files & quirks

- `final-hours/channel.json` (voice Victor, style, music), `rulebook.json` (channel rules), `auth.py` / `upload.py` (working OAuth), `client_secret.json` / `token.json`, `beat-scripts/`, `projects/`, `assets/`, `docs/`.
- **OAuth:** working, under peteralkema2@gmail.com / project `youtube-upload-test-497220`. Known `auth.py` CLIENT_SECRET/TOKEN_FILE variable-swap bug; OAuth app in 7-day testing mode → weekly token expiry.
- `grep -c '_expand_canon\|_load_beats_with_canon'` ≈ 6 = canon mechanism present (sanity check).
- `shared/rulebook.json.pre_migration_backup` = pre-multi-channel snapshot.
- Final Hours is the **Mode-A-only reference signature** — a Mode-A-only beats.json stamped `final_hours` runs `audio → modeA → convergence`, no Mode B leg. It's the channel that must keep falling through the orchestrator unchanged as features land.

---

*Maintained by Peter + Claude. Strategic framing, topic principles, audience mechanics, the forward queue, and banked production/distribution lessons all live here now (the former strategy + two backlog docs are merged in). Operational how-to lives in `_machina.md`; craft in `_ante-machinam.md`; the wider operation in `_YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`.*
