# CANONICAL_PATCH_de_final_hours.md
*An INSERTABLE section for `_PIPELINE-CANONICAL.md`. Do NOT apply the full rewrite now — that's a large piece of work for a dedicated session. This document (a) is the drop-in section that flags the problem inside the canonical itself, and (b) specs how the rest of the rewrite must proceed. Banked 29 Jun 2026 from the @Q-Qrew build — the day the bias became undeniable because a deliberately-opposite channel had to fight it at every turn.*

---

## >>> INSERT THIS SECTION INTO THE CANONICAL (near the top, after the thesis) <<<

### ⚠ CRITICAL: THIS DOCUMENT CONTAINS FINAL-HOURS BIAS MISLABELLED AS UNIVERSAL LAW

**The problem, stated plainly:** Final Hours was the first channel built. Its craft — cinematic, slow, faceless, dread-and-dignity, photoreal, Kling-animated — got written into this "channel-agnostic" canonical and into `ante-machinam.md` as if it were universal truth. **Much of it is not.** It is *one channel's craft brief* wearing a universal label. Every channel that is not cinematic-slow-faceless-dread has to actively fight this document's gravity — and worse, **channel-specific assumptions leaked into the CODE that is supposed to be channel-agnostic** (see the code-leakage list below).

**The distinction that resolves it — MECHANICS vs CRAFT:**
- **MECHANICS are genuinely universal** and stay: header format, channel-matches-folder, numbers-spelled-out-in-narration, one-VISUAL-per-Mode-A-beat, the leg system, parse-verify-before-spend, `safety_tolerance:"5"`, `base_canon` auto-merge, positive-prompt-is-the-real-lever (negatives are weak on flux-pro), CTR-won-by-package / distribution-by-retention, recognition-is-the-retention-mechanic, nothing-publishes-unreviewed, script-is-king.
- **CRAFT is channel-specific** and must NOT be stated as universal: beat granularity, whether-to-animate, faceless-vs-character, the emotional register, photoreal-vs-illustrated, the cost-floor lane. `ante-machinam.md` Part IV **is the Final-Hours/Sacred-Dawn craft brief, not universal craft.**

**The mandate:** every genuinely different channel needs its OWN craft brief (`_ChannelName.md`) that explicitly states which universal-seeming rules it breaks. The canonical must FLAG each craft rule as "[CRAFT: Final-Hours-derived — channels may break]" rather than presenting it as law. See the per-channel break-lists (`NOTE_final_hours_bias_in_canonical.md`, `_QQrew.md §12`) for the worked examples.

**The proof this is real:** @Q-Qrew (channel #12, shipped 29 Jun 2026) was designed as the deliberate OPPOSITE of Final Hours — bright, fast-cut, character-driven, flat-illustrated, static. Building it surfaced the bias at every layer: the docs fought it (six craft rules had to be explicitly broken), AND the code fought it (channel-specific defaults baked into supposedly-agnostic functions — listed below). The bias is not theoretical; it cost real debugging time on the QQrew build.

---

## HOW THE REST OF THE REWRITE MUST PROCEED (spec for the dedicated session)

### 1. Tag every CRAFT rule in the canonical
Walk the canonical + `ante-machinam.md`. For each rule, classify MECHANIC or CRAFT. Tag every CRAFT rule inline: `[CRAFT: Final-Hours-derived — see channel doctrine; channels may break]`. Do NOT delete them (Final Hours still needs them) — RELABEL them so they stop masquerading as universal. Priority targets (the six that QQrew broke):
- Beat granularity (15-35 words / 5-12s) → CRAFT. QQrew: 4-10 words / 1-3s.
- Animatable-foreground requirement → CRAFT. QQrew: static, no foreground-motion need.
- Faceless-by-default / place-canon-not-people → CRAFT. QQrew: recurring visible character.
- Slow-dread register (Part IV whole) → CRAFT. QQrew: bright/wry/propulsive.
- Photoreal-cinematic style → CRAFT. QQrew: flat-cel, negative-the-realism.
- Ken-Burns cost-floor → CRAFT. QQrew: true-static, leaner still.

### 2. CODE LEAKAGE — strip channel-specific assumptions from agnostic code (HIGH PRIORITY — this is the worse half)
The docs are recoverable with relabelling; the CODE leakage causes silent wrong behaviour. Found during the QQrew build:
- **`_tiered_kling_count` defaults to 40** when no render_policy present — a Final-Hours-cinematic assumption (heavy animation). A bright/static channel that forgets render_policy silently gets a $100 Kling job. **Fix:** default should be channel-driven or 0, not 40.
- **`_still_to_held_clip` applies Ken-Burns zoompan even at kling_count:0** — there is NO true-static path. "Static" silently means "Ken-Burns." That's a Final-Hours aesthetic baked in as the floor. **Fix:** add a real no-motion path (Patch B).
- **`ingest.create_project` (MC path) reads ONLY per-project `canon.json`, never channel `base_canon`** — and writes no canon.json. The CLI path reads base_canon; the MC path doesn't. A character-driven channel's lock silently no-ops on the MC path. **Fix:** Patch A — auto-write canon at create, unify the two paths.
- **Thumbnail house-look = three stacked darkening layers** (`darken_factor` + `scrim` + `vignette_strength`) tuned for text-over-busy-cinematic-stills. A flat-pop-background channel gets a muddy thumbnail and must zero all three. The defaults assume Final-Hours-style busy dark imagery. **Fix:** make the house-look opt-in / channel-defaulted, not a baked global.
- **Hardcoded log labels "Victor" and "Kling"** appear regardless of actual voice_id / animation mode — cosmetic but caused a false-alarm kill-scare on the QQrew render. **Fix:** log the actual resolved values.
- **Thumbnail block cloned from success-coach carries wrong margin_y (48 vs the proven 20)** — a per-channel value propagated as a default. **Fix:** the proven margin block (margin_x:40/margin_y:20/title_area_pct:0.52/title_start_size:150) should be the agnostic default, not success-coach's.

### 3. Restructure the canonical into LAYERS
Reorganise so the document physically separates:
- **Layer A — MECHANICS (universal, all channels):** the pipeline contract.
- **Layer B — CRAFT MENU (pick-per-channel):** beat granularity, motion mode, character-vs-faceless, register, style, cost-floor — presented as a MENU of options with the trade-offs, not a single prescribed answer. Each channel doctrine selects from the menu.
- **Layer C — pointers to channel doctrines** (`_ChannelName.md`) for the actual selections.
This kills the "first channel = default" failure permanently: there IS no default craft, only a menu + per-channel selections.

### 4. The meta-principle to enshrine
**BUILD ORDER ENCODES BIAS.** The first instance of anything (channel, prompt, config default) silently becomes the "neutral" default and infects everything claiming to be general. The discipline: when building the FIRST of a kind, ask "is this universal or is this just THIS one's flavour?" and tag accordingly at creation — cheaper than excavating the bias later by hitting it (as the QQrew build did). Generalised mechanics cleanly; craft did not; code leaked craft as mechanics. Watch the code most — docs mislead readers, code silently misbehaves.

---

## WHY NOT REWRITE NOW
This is a large, careful, cross-document refactor (canonical + ante-machinam + the agnostic code modules). Doing it at the end of a mammoth session risks introducing the exact kind of silent error it's meant to remove. **Bank this insertable section, drop the ⚠ block into the canonical so the warning is live immediately, and schedule the full layered rewrite + code-deleakage as its own session** — gated, tested, one module at a time, with the QQrew break-list and the code-leakage list above as the worked checklist.

*The learning was the gift: the bias was found by building its opposite, named at every layer, and is now cheap to avoid — for every future channel that isn't Final Hours.*
