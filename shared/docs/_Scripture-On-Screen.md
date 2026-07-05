# Scripture On Screen — Channel Doctrine
*The single consolidated reference for **Scripture On Screen** — the faithful-canonical Bible channel, sister channel to Sacred Dawn. Load this, with the four `_` system docs, on any session for this channel. Captures positioning, the two-audience thesis, the Sacred Dawn boundary, competitive analysis, the moat, content model, length doctrine, craft spine, packaging doctrine, the episode backlog, config facts, roadmap, and (§12) the reusable batch-runner launch playbook.*
*Drafted 14 June 2026 from the naming-and-scope session. **Updated 18 June 2026: channel LAUNCHED. Esther flagship (~30 min) + Job (Phase-1, 56 beats) shipped; the first 10-video batch is rendering through `run_batch.py`, publishing nightly 19–28 June. Curated Artlist music bed, the `thumbnail`/`music` `channel.json` blocks, and the per-channel batch-inbox design are all live and recorded below.** The `_` prefix floats it to the top of `shared/docs/`. Channel-scoped, load-on-demand — not a system doc.*
*__**Updated 05 July 2026 — v2.0, THE FINAL-HOURS REGISTER SCRUB + THE ELIJAH BLOCKBUSTER PIVOT.**__ This channel inherited the Final Hours dread register (dark, candlelit, Victorian-painterly, chiaroscuro) through build-order bias — the same contamination QQrew and Synthetic were resurrected from (canonical §2B; `_QQrew.md §4`; `_Synthetic2.md §13`). The scrub moves the VISUAL register decisively AWAY from dread-and-dignity and TOWARD bright, high-energy, blockbuster spectacle — while keeping a gritty biblical realism (this is a faithful witness, not a cartoon). The tonal reverence stays in the VOICE and the WRITING; it no longer dictates a dark, low-key grade. §5 (look/motion) is the heart of the surgery; §9a is the config-change record (what to edit, exactly); §5b banks the Bay/Woo biblical grammar imported from Synthetic; §7a absorbs the Elijah four-cut thumbnail doctrine; §14 banks Elijah as the flagship the channel now inherits. Strategy layer (§2 two-audience thesis, Sacred Dawn boundary, §4 expectation-management, §6 length doctrine, face-tier system) is UNCHANGED — it was never contaminated; the scrub is a register operation, not a rewrite.*
*[Naming note: resolved 14 June to **Scripture On Screen** (`@Scripture-On-Screen`, open). Chosen on an expectation-management argument — the name makes a *medium* promise, not a *fidelity* promise, which is the right contract for AI output that will take visual liberties. Rejected: "Biblical Canon" (over-promises textual fidelity → invites the faithful audience to police the gap), "Reimagined" (implies altered), "____ Cinema" (saturated swarm). See §1, §4, §9.]*

---

## 0. What this is, in one paragraph

This is a faceless, fully-AI cinematic channel that renders the **canonical, dramatic narratives of the Bible** — Esther, Job, Ruth, Joseph, David, Daniel, the Flood, the plagues — as cinematic recreations, story by story, faithfully. The pitch in one line: *the Bible's greatest stories, brought to the screen exactly as they were told.* Reverent, dignified, faithful — **not** reimagined, not sensationalised, not "the book they banned." It runs on the same channel-agnostic pipeline as Final Hours, You Had To Be There, and Sacred Dawn — one config file and content, no new code. Its reason to exist as a *separate* channel from Sacred Dawn is the central insight of this doctrine: the Bible audience on YouTube is **two audiences**, and this channel serves the one Sacred Dawn does not.

---

## 1. Positioning

- **Premise:** the canonical dramatic stories of scripture, recreated cinematically and faithfully, one figure / one arc per video.
- **Register — split the two axes cleanly (the scrub's core correction, banked 05 July):** the *voice/writing* register is reverent, warm, dignified, story-first — a trusted storyteller telling a true story straight, not a mystery-monger, not a hype-man; present-tense cinematic witness; never "BANNED / FORBIDDEN / what they're hiding / NOT human." The *visual* register is the OPPOSITE of what "dignified" was allowed to imply: **bright, high-energy, blockbuster-cinematic, kinetic, saturated, spectacular** — Bay/Woo trailer grammar in a biblical grade (desert-gold / lapis / crimson), not Final Hours' candlelit dread. **Reverence is a quality of the NARRATION; it does not license a dark, low-key, shadow-dominant grade.** Gritty biblical realism stays (real dust, real weathered fabric, real ancient-world texture — this is a faithful witness, not a cartoon), but it is realism rendered BRIGHT and dramatic, high-contrast toward light, never toward murk. The one-line target: **Gladiator's warmth and scale + The Prince of Egypt's brightness and colour drama + Bay/Woo's kinetic energy** — Gladiator for grandeur, NOT for its shadow-grade (Scott's light is golden but low-key; chasing it literally drags us back toward dread).
- **Handle:** `@Scripture-On-Screen` (open, 14 June). **Display name:** Scripture On Screen. **Tagline (working):** "The Bible, brought to the screen" — a *medium* promise, not a fidelity promise (see §4: this is deliberate expectation-management; the name pre-authorises visual interpretation rather than claiming textual exactness).
- **Audience:** **Audience A — the faithful / devotional viewer** (see §2). The large, high-RPM, churched-and-adjacent audience that watches for reverence, recognition, and faith affirmation, and wants the *canonical* story told straight.
- **Production tier (the quality bar):** **the "Amazon Prime" of the Bible category** — prestige, streaming-cinematic, vivid and premium, deliberately a tier above the cartoon-animation swarm and the sepia-documentary pack. The bar is "looks like a streaming-series adaptation," not "looks like a YouTube explainer." *Prestige here means BLOCKBUSTER prestige — the big-screen epic, not the solemn art-house muted grade; read "prestige" as spectacle-tier, never as an excuse for restraint-toward-dark.* The disbelief-worthy economics that make this a moat: this prestige tier ships at **~$20 per video** on the Ken-Burns path (a heavy-Kling flagship like Elijah runs 2–3× that — §14). Premium output at slop-tier cost is the asymmetry; the look is where it's spent (see §5).

---

## 2. The thesis — why this channel exists

### The one insight everything hangs on: the Bible niche is two audiences

The "Bible niche" on YouTube is not one audience. It is two, with different intent, different trust thresholds, and different brand voices — and conflating them is the single biggest strategic error available here.

- **Audience A — the faithful / devotional viewer.** Watches for reverence, study, comfort, and faith affirmation. Wants the **canonical** story told straight and dignified. Is often actively *suspicious* of "lost books" / Enoch / Nephilim content — to a bible-believing viewer the Book of Enoch is not scripture, and "the book they banned" framing reads as sensationalist or borderline occult. Pointing a faithful brand at apocrypha doesn't just leave this viewer cold; it **repels** them. **This channel is built for Audience A.**
- **Audience B — the mystery / curiosity viewer.** Overlaps heavily with the ancient-mysteries, forbidden-knowledge, conspiracy-adjacent crowd. This is who drives the Enoch (1.6M) and Nephilim (784K) numbers. It is a mystery audience wearing biblical clothes. **Sacred Dawn is built for Audience B.**

The apocrypha numbers are real, but they belong to a different audience, a different brand voice, and a lower-trust, more conspiracy-tinted register. Chasing them with a faithful brand is taking the wrong audience's bait.

### The Sacred Dawn boundary (the most important operational rule in this doc)

The two channels split the entire Bible cleanly. **Never let this line blur — separate signatures is the whole point of separate channels.**

- **Sacred Dawn** = the primeval, cosmic, mythic, apocryphal edge. The Watchers, the Nephilim, Enoch, the war in heaven, the sons of God, forbidden knowledge. Audience B. Elliot's British-liturgical voice. The cinematic-myth register.
- **This channel** = the canonical, faithful, story-by-story recreation of the Bible's *human* narratives. Esther, Job, Ruth, Joseph, David, Daniel. Audience A. A warmer, accessible storyteller register (see §5). The story told straight.

**The contestable seam — decide it on purpose: Genesis 1–11.** Early Genesis is *primeval* history, arguably Sacred Dawn's territory too. The working ruling: this channel gets the **human-drama** parts of early Genesis (Adam & Eve as a human story, Cain & Abel, the Flood told as Noah's story, Abraham, Isaac, Jacob, Joseph); Sacred Dawn keeps the **cosmic/supernatural** parts (the Watchers, the Nephilim, the sons of God, the war in heaven). A flood video can exist on both channels and not collide, *because the lens differs* — here it's Noah and his family; on Sacred Dawn it's the drowned cosmic order. If a topic can't be told without the supernatural-primeval lens, it's Sacred Dawn's.

### The punchline that makes the split costless

The faithful-canonical lane is the **biggest** lane in the whole niche anyway. The top proven numbers we pulled are *all* canonical: **Esther 2.4M, Job 1.4M, Sodom 1M, Jezebel 968K, Ruth 930K.** We hand Enoch/Nephilim to Sacred Dawn and lose essentially nothing — the canonical dramatic stories already out-demand everything except Enoch itself. This channel does not need apocrypha bait. It stands on the actual Bible.

### The un-referenced-sublime filter, adapted

Sacred Dawn's core principle — *is there a reference the audience can catch us failing against?* — mostly holds here too. No one has footage of the ancient world: Esther's Persian court, Job's devastation, the parting of the Red Sea, the lion's den. The Flux painterly-unreal quality reads as the *ancient/sacred past*, not as a failed photograph. The nuance: some of these stories *do* have prior films (Prince of Egypt, The Ten Commandments), so the audience has a loose visual memory — but **no faithful, photoreal version exists**, and lived ancient-world texture cannot be re-filmed. The filter still passes; we are the only photoreal recreation of these scenes that exists. The faceless/object-rendered craft (ante-machinam Part III) carries it as it does on Sacred Dawn.

### Why it's durable (the anti-graveyard asset)

The Bible is a fixed, finite, public-domain canon with permanent, non-seasonal demand and billions of adherents who re-engage with the *same* stories for life. You cannot saturate Esther. No spike to chase, no crest to fall off. The only saturation risk is **packaging** (the shock-bait treadmill and the cartoon-animation swarm), which we opt out of by anchoring on the canon and differentiating on photoreal execution — see §4.

---

## 3. Competitive analysis

*All figures from NexLev pulls, 14 June 2026 session. Revenue/RPM are NexLev estimates; treat as directional. The lane is live and beginner-open NOW — channels under a year, some under two months, already at $2–5k/mo — but entrants are pouring in, which is why packaging differentiation and speed matter.*

### Our direct competitive set (faithful-canonical / dramatic recreation)

| Channel | Created | Subs | Est. $/mo | Signature content | Note |
|---|---|---|---|---|---|
| **Bible Chronicles Animation** | Jan 2025 | ~458K | ~$4,900 | Canonical figures, **animated** | The gorilla. Esther **2.4M**, Job **1.4M**, Sodom **1M**, Jezebel **968K**, Ruth **930K**. Our demand-proof — but animation format, not our lane. |
| **GIDEON FILMS** | (2025) | ~197K | — | Photoreal "Visualized" Bible, long-form | **"Book of Genesis… Visualized" 4-hr compilation = 10.9M views.** The aspirational proof: photoreal + canonical + long-form works at the very top. Closest to our actual format. |
| **Christian Bible Animation** | Oct 2025 | ~32.9K | ~$2,000 | Animated figures | Leah **611K**, Nebuchadnezzar 158K, Esau & Jacob 96K, Abigail 90K, Moses 89K. 8 months → $2k/mo. Animation. |
| **Epic Bible Animation** | Jan 2026 | ~10K | ~$725 | Animated, 2 uploads/wk | Adam & Eve 80K, Jezebel 77K, Cain & Abel 54K. Claims "gritty, not cartoons" in bio — **doesn't deliver it.** That unclaimed positioning is our seam. |
| **Immersive Bible Stories** | Apr 2026 | ~29K | ~$2,900 | 60–85 min, documentary-photoreal | **2 months old**, 8.05 outlier. Straddles A/B — leans mystery packaging ("REAL Garden of Eden," Ethiopian Bible). Proof a fresh photoreal channel breaks fast. |

### The mystery cohort (Audience B — this is Sacred Dawn's competitive set, NOT ours)

Logged here only to keep the boundary explicit. **Scripture Origins, Scripture Legacy, Biblical Facts, Bible Hidden, The Bible Seen.** Enoch/Nephilim/Watchers/angels content. If we find ourselves studying these for *topics*, we've drifted into Sacred Dawn's lane — stop. Study them only as Sacred Dawn intel.

### The format read

Demand is split across two formats: **animation** (Bible Chronicles and the swarm beneath it — crowded, cartoon register) and **photoreal** (GIDEON, Immersive — far less crowded). Our entire differentiation is **photoreal cinematic recreation, not cartoons.** Epic Bible Animation *claims* this and delivers stylised animation; the positioning sits unclaimed by anyone executing it well. That gap is the channel.

---

## 4. The moat — faithful best-execution, against two swarms

We are differentiating against two crowds at once: the **shock-bait mystery** swarm (Audience B's lane) and the **cartoon-animation** swarm (the cheap canonical lane). The moat is the same move that beats both: faithful canonical stories, rendered photoreal, packaged with reverent recognition rather than shock.

- **Faithful, not reimagined.** Every story told straight from a public-domain text (WEB or KJV — WEB for clarity, KJV for cadence; decide per the voice test). The "recreation" is purely *visual* — making the un-filmable visible. We never alter the story. This is the literal promise the tagline makes and the reason a fidelity-signalling name beats a "reimagined" one.
- **Attribution discipline.** Where a detail is interpretive or extra-biblical, it's flagged as such. This is what separates reverent execution from slop, and it protects monetisation (theological-fidelity guard).
- **Photoreal as the visible moat.** The spectacle stories — the Flood, Sodom's fire, the ten plagues, the fiery furnace, the Red Sea — are where photoreal *shows* and cartoons can't follow. Over-invest visually there; those videos are the ones that make a viewer realise this isn't cartoon-tier.
- **The name as tonal filter.** Read a shock title under this channel's name and it should jar; read a reverent-recognition title and it should sing. If a title clashes with the brand, it's a title we shouldn't run.

### The expectation-management principle (banked 14 June 2026)

*A name is a contract; the contract must be one the output can keep.* Photoreal AI recreation **will** take visual liberties — invented faces, clothing, architecture, compressed sequence, dramatised dialogue, the scenes scripture leaves blank. That is the job, not a defect. So the brand must **under-promise on fidelity**, because the gap between promise and delivery is what gets punished — and the *faithful* audience (Audience A) is the single audience most equipped to police that gap against the text and win in the comments.

This is why "Scripture **on Screen**" beats "The Biblical **Canon**": "Canon" promises textual exactness and hangs a fact-check invitation over the door; "on Screen" promises a *medium* (a visual adaptation) and thereby **pre-authorises** the creative liberty — the same license audiences grant any film of scripture (no one accuses *The Prince of Egypt* of heresy for giving Moses a face).

**The calibration nuance (the name carries it, not just the tagline):** the goal is not *zero* fidelity signal — that under-promises so hard it reads cheap ("Bible Flicks") and fails to reassure Audience A that the text is handled seriously. The goal is *calibrated* fidelity signal. "Scripture" supplies the fidelity **anchor** (real sacred source, treated with respect → trust); "on Screen" supplies the liberty **license** (visual adaptation → permission to invent the image). The two words divide the promise cleanly: *faithful source, visual medium.* The deeper distinction is **fidelity-of-intent vs fidelity-of-detail** — "Scripture" claims intent (we are faithfully adapting the actual canon, from a public-domain text), which is true and defensible; "Canon" claims detail (every depicted particular matches the record), which the photoreal liberties make false. Claim the promise that's true. This also means the tagline needn't carry the whole fidelity load — the name already does half of it. The expectation-management discipline (a Udemy course-creation principle: set the bar low, let the product clear it) propagates down the whole brand:
  - **Tagline** makes a medium/experience claim ("brought to the screen," "brought to life"), never a truth claim ("the true account," "exactly as it happened").
  - **Descriptions** carry a light "a cinematic dramatisation of the biblical account" line — managing expectation *and* doubling as the attribution/monetisation guard.
  - **AI disclosure** ("Altered content = Yes") is consistent with the frame, not in tension with it.

The rule generalises to every future channel: *name and package for the promise the machine can actually keep, never for the promise that sounds best.*

The audience is **AI-indifferent but not quality- or reverence-indifferent.** It won't punish the AI look; it *will* punish cheap recreation and sloppy theology. Both cut toward us.

### The banked content pattern: women-led stories over-index

Across the data, female-protagonist stories massively over-index: **Esther 2.4M, Ruth 930K, Jezebel 968K, Leah 611K, Abigail 90K, Keturah 309K.** This is not incidental — the niche's core audience rewards a woman in crisis at the centre of the story. Weight the slate and the packaging toward female leads. Bank as a principle.

---

## 5. The content model

- **Format:** photoreal cinematic recreation, **one canonical figure or arc per video.** Story-by-story, never "book by book" — the audience buys *a person in crisis*, not a book of the Bible. (Leviticus has no protagonist and no thumbnail; it does not get made.)
- **Presentation:** **narrator style** — VO over cinematic stills + motion; no on-screen speaking characters, no lip-sync, for now. **Lip-sync is a deliberate future upgrade** (add once the narrator format is proven and the upload/cadence machine is solid), not a launch feature. Narrator-first keeps the pipeline simple and the cost at the ~$20 tier.
- **Length:** **retention-first, length-earned.** See §6 — this is a doctrine, not a setting.
- **Mode:** **Mode A only** (cinematic recreation; no Mode B graphics). Pipeline path: composition scan skips Mode B → `audio → modeA → convergence`.
- **Voice:** **Ren (selected).** After auditioning warmer storyteller voices against the brief — warm, deep, reverent, late-40s–50s, intimate gravitas, slow, neutral North American, *not* a British cathedral register — the chosen voice is **Ren**. This resolves the earlier Elliot-interim placeholder: Scripture On Screen does **not** share Elliot with Sacred Dawn after all, which is a better state (see look note below). Set `voice_id: "Ren"` in `channel.json` (snake_case — `voiceId` silently falls back to Victor). *Validation, not a blocker:* confirm Ren holds across the full Esther cut — especially the intimate beats ("if I perish, I perish"; the manger hush) where designed/flat voices fatigue over 30 minutes; if Ren reads flat across 119 beats, fall back to a richer stock voice directed warm-and-slow (the realism texture — natural breath and prosody — is load-bearing for this channel's prestige tier).
  - *Note the boundary shift from earlier doctrine: because the voice is now shared with Sacred Dawn, the **look** carries the brand-separation load (see below). That is deliberate, not a compromise.*
- **Source text:** public-domain only — **World English Bible (WEB)** is the default (modern clarity fits the warm, accessible, human-drama register better than KJV's archaism). KJV only where a specific line's cadence earns it. Never NIV/ESV/NASB/NLT — those are enforced.
- **Upload:** manual until the channel-agnostic upload step + batch exit-gate is built. Category = **Entertainment** (`24`), `privacy_status: private` until reviewed. AI-disclosure ("Altered content = Yes") set in Studio.

### Look, motion & production spec

**The look is a primary brand-separator — now reinforced by voice, and SCRUBBED of the FH register (05 July).** Earlier this channel was set to share Elliot with Sacred Dawn, which put the whole separation load on the look. With **Ren** selected here and Elliot on Sacred Dawn, the two channels are now distinct in *both* voice and look — a stronger, cleaner separation. The look still does heavy lifting and remains load-bearing, not aesthetic. Sacred Dawn is ash, storm-grey, weathered gloom; **this channel is the inverse: bright, vivid, jewel-toned, luminous, high-energy.** Think *The Prince of Egypt*'s colour drama and *The Ten Commandments*' technicolor spectacle, with *Gladiator*'s scale and golden warmth — but rendered BRIGHT, high-key toward light, blockbuster-kinetic. The target tier is the **"Amazon Prime" of the Bible category** (§1) — prestige streaming-cinematic, at ~$20/video.

**★ THE FIDELITY-vs-REGISTER SPLIT (the load-bearing lesson, imported from `_QQrew.md §4`).** The style_suffix carries two kinds of word and they must be tuned independently:
  - **FIDELITY words** (KEEP — these are the prestige tier): richly saturated jewel tones, luminous, detailed faces, rich backgrounds, real fabric / real gold / real lapis, photoreal, period-accurate, depth, high production value.
  - **REGISTER words** (this is where the FH contamination hides): the OLD suffix carried **"deep oil-painting colour," "warm dramatic chiaroscuro," "painterly photorealism"** — every one of these is a DREAD-register word that drags the whole channel dark and shadow-dominant, *including facial expression* (a chiaroscuro-lit Esther reads solemn and shadowed, not vivid). "Chiaroscuro" is literally the candlelit-Rembrandt Final Hours signature wearing a "biblical epic" label. **These are STRIPPED.** In their place go the bright/high-energy register words proven on Synthetic and QQrew: *bright vivid exposure with rich detail in shadows, high dynamic range, lots of light and energy, dramatic intense lighting, crisp and dynamic, blockbuster spectacle.*

- **The cartoon trap (still the caution — brightness must not go FLAT):** "bright vivid" must be **photoreal brightness, not flat cartoon saturation** — or it collapses into the animation swarm we're differentiating from. The colour comes from *materials, ornament, and blazing golden-hour / firelit light rendered photoreally* (real fabric, real gold, real lapis), luminous and high-dynamic-range — bright AND detailed, never bright-and-flat, and never dark-and-muddy. This threads between three failure modes at once: Sacred Dawn's gloom (too dark), the cartoon pile (too flat), and the FH dread we just scrubbed (too shadowed). The QQrew rule in one line: **keep the fidelity words, ban the register words, specify light BRIGHT because the model defaults dark when light is unspecified.**

- **`style_suffix` (SCRUBBED — v2.0, live target):**
  > *cinematic biblical blockbuster film still, photorealistic, richly saturated jewel tones, desert gold and lapis and crimson, bright vivid exposure with rich detail in shadows, high dynamic range, blazing golden-hour and firelit light, lush fabrics and gold and lapis ornament, intense dramatic lighting, lots of light and energy, crisp and dynamic, high production value, period-accurate ancient Near East, Egypt and Persia, gritty realistic texture, expressive detailed faces, sharp focus, no text, no letters, no modern elements, 16:9*
  >
  > **Deliberately STRIPPED (the scrub):** "oil-painting," "chiaroscuro," "painterly" (FH register-leak words), plus the Sacred Dawn set already absent ("ash," "storm-grey," "weathered," "muted"). **Deliberately ADDED:** "bright vivid exposure with rich detail in shadows," "high dynamic range," "intense dramatic lighting," "lots of light and energy," "blockbuster," "gritty realistic texture" (the biblical-realism anchor that keeps it from going cartoon). This is the Synthetic epic-cinematic grade (`_Synthetic2.md §6`) re-graded from teal-orange to biblical desert-gold/lapis — visually distinct from Synthetic in a feed, but the same bright-kinetic register family.
  >
  > **★ Verify at the artifact, not the request (canonical §8 / `_Synthetic2.md §6`):** after this suffix lands, RE-RENDER a test still and check the actual output is bright — the style_suffix is the highest-leverage lever on look, and if renders still come out dark, read the ACTUAL suffix on the box first (a stale pull, or the reference-lock bypass below, is the usual culprit). Do not judge the scrub by the config; judge it by a rendered frame.

- **Per-story palette override (operationalise like Lazarus's per-film look overrides):** don't run one flat "vivid" across everything — layer a *story-specific colour world* on the base, so each episode feels authored and each thumbnail pops against the niche's sepia wash. Working set: **Esther** = imperial crimson, gold, lapis (Persian court); **Joseph** = the many-coloured coat against Egyptian ochre, turquoise, gold; **Exodus** = gold, blood-red, Nile-green. (Also a CTR weapon — colourful thumbnails beat the sepia-mystery look everyone else uses.)

- **Motion direction — *per-channel guidance now; per-clip discretion on Mission Control*. SCRUBBED (05 July).** Current design: motion is a **channel-level guidance setting** (the channel's overall pan/zoom character), with **per-clip override discretion available on the Mission Control page**. The OLD default was "slow, intimate push-in" — that is the Final Hours contemplative-drift signature, and it fights the blockbuster register. **New default: dynamic, kinetic, blockbuster camera energy** — powerful momentum, dramatic push-ins and pulls, energetic movement across the scene, the Bay/Woo trailer feel (`_Synthetic2.md §7`). Human biblical drama wants MORE energy than cosmic reverence, not the same or less. Reserve the slow intimate push-in for the rationed quiet beats (the tender turn, the whisper) — it is a per-clip CHOICE for emotional stillness, never the channel default. **Tell the animator what MOVES and what stays** on quiet beats, or the dynamic default invents drama (`_Synthetic2.md §7`).
  - **Banked for later (cross-channel idea, NOT building now):** a **per-beat MOTION vocabulary** mapped to emotional function → Kling prompt in the animate leg — `push_in` (intimacy/focus), `pull_out` (reveal/isolation), `pan` (journey/passage), `tilt_up` (hope/ascent/the divine), `tilt_down` (judgment/the fall), `slow_orbit` (hero moments, sparingly). Map motion to *emotional function*, not randomly. Good thinking for **all** channels — bank it as a future Mission Control upgrade, not a Scripture-on-Screen launch dependency.

- **Face policy — the three-tier rule (character consistency without drift).** The core constraint: **Flux has no character memory.** Every still is an independent generation; "Esther" in beat 4 and "Esther" in beat 40 are two different women sharing a prompt. There is no seed-lock or character-reference in the current still→Kling path, so sustained recurring *recognisable* faces are exactly where drift bites — and viewers read a face that changes between scenes as "AI slop," the tell we're differentiating against. Vivid human drama still needs **expression** (Esther's terror, Joseph's betrayal), so the resolution is to **ration** faces, not ban them:
  - **Tier 1 — hero-face peaks, scarce and spaced.** A small number of full-face frames per video (~3–6, never ~30), each at an *emotional peak* where expression carries the beat. Because they're rare and **far apart in time**, mild drift between them goes unnoticed — the viewer never holds two faces side by side. *Spacing matters more than count:* never two hero-faces in adjacent beats; place them at open / midpoint turn / climax. Single subject only, **always `safety_tolerance: "5"`** (never default, or Flux silently returns ~7KB black PNGs).
  - **Tier 2 — costume/silhouette as the identity carrier (the actual consistency trick).** Lock recognisability onto what Flux *can* hold across generations: fixed costume + ornament + hair tokens in every prompt (Esther = crimson robe, gold circlet, gold-and-lapis jewellery, dark braided hair). The viewer reads the *costume and silhouette* as the character even when the face isn't shown — exactly how film carries a hero by their coat in a wide shot. This lets the **majority** of a character's screen time be back / three-quarter-rear / over-shoulder / partial-profile-in-shadow and still read unmistakably as them.
  - **Tier 3 — faceless default (the Sacred Dawn craft).** Back, far side-profile, silhouette, hands, the turn-away, reaction shown through body not face. Where most screen time lives; also the only safe handling for **3+ figure crowds** (scale, silhouette, backs-of-heads — never a rendered crowd of faces).
  - **The rule in one line:** *face only at peaks, rationed and spaced; identity carried by costume/silhouette everywhere else; faceless by default.* Not "face once" — reserve a face for the two or three later beats that genuinely need one (the climax especially).
  - **Phase-2 upgrade path (NOT a launch dependency):** a character-reference / IP-adapter approach (generate one canonical hero portrait, feed it as an image reference to later generations) would tighten consistency further — but it's a real change to the still leg, adds cost/complexity, and the costume-carrier method gets ~90% of the way for free. Bank it as the upgrade if drift outruns the rationing; do not block launch on it.

- **Music:** **warmer than Sacred Dawn** — melody-and-movement, not drone-and-dread. `default_music_prompt` (live):
  > *warm orchestral storytelling score, emotive strings and woodwinds, hopeful and cinematic, swelling brass on triumph, harp and gentle choir on tender beats, restrained percussion only on deliverance/action beats, no modern instruments*
  >
  > **Decision resolved (18 June): curated Artlist bed, not generated.** The generated-vs-curated question was open at launch; settled in favour of a curated bed for the prestige tier (generated reads thinner than "Amazon Prime of the Bible" demands). **8 tracks** (`track_01.mp3`–`track_08.mp3`, space-free names) live in `scripture-on-screen/music/`; the assembler picks **3 at random**, lays them end-to-end with a **2-second crossfade**, at **`level: 0.07`**, per the `music` block in `channel.json`. **Validated on the Job test (18 June): music choice AND level both correct on the first try — `0.07` confirmed right for a warm melodic bed under Ren, no change needed.** Artlist's license clears YouTube monetisation cleanly (a copyright claim on a faithful Bible channel is exactly the trust/revenue risk we avoid). **Track-selection test when curating:** *"does this sound like Sacred Dawn?"* — if yes, it's the wrong track; this channel must be audibly warmer/melodic to keep the two Bible channels separate at the audio layer (the third separation layer, alongside voice and look). `make_music.py` is fallback-only; not used here.

  - **Music grade note (05 July scrub):** "warmer than Sacred Dawn" still holds, but warm ≠ solemn. On spectacle beats (fire, flood, the sea, the chariot) the bed should SWELL blockbuster-big — brass, percussion, choir — not stay reverent-restrained. The warmth is in the tender beats; the spectacle beats want epic scale. The Sacred-Dawn-separation test is about melody-vs-drone, not about keeping the volume down on the big moments.

---

## 5b · THE BLOCKBUSTER CRAFT GRAMMAR (Bay/Woo, biblical grade — imported from Synthetic, banked 05 July)

*This is the register scrub expressed as positive craft, not just banned words. It is the `_Synthetic2.md` blockbuster doctrine (§5, §13) adapted to faithful biblical narrative — the "what to DO," to sit alongside §5's "what look to render." Load it when authoring any spectacle-forward script (Elijah, the Flood, the Red Sea, Sodom, the plagues, the fiery furnace).*

**The register in one sentence:** the dread comes from FACTS and FACES and the weight of the story, never from murk, shadow, or slow dwelling. Bright, kinetic, operatic, high-contrast-toward-light — and reverent in the WRITING while spectacular in the FRAME.

**Scripting grammar (the page):**
- **Open inside the action, not before it.** Cold open mid-event — the fire already falling, the sea already walling up, the threat already in the room — then "to understand, you have to go back." (This channel's craft spine already does this per §8; the scrub just sharpens it toward spectacle-first.)
- **The story's own clocks are the engine.** Scripture is full of literal ticking clocks — three years of drought, a single day on Carmel, "by this time tomorrow," forty days. Name them; let them drive. A scene without a clock gets one or gets cut.
- **Escalating set-piece ladder.** A spectacle beat every few minutes, each bigger than the last, the finale biggest. Between set-pieces run pressure beats (pursuit, ultimatum, the fall), never idle dwelling.
- **One sincere emotional core, protected.** Every blockbuster runs one true human relationship through the spectacle. The quiet/tender beat (the whisper, the widow, the broom tree) plays absolutely straight, scored down — it is what EARNS the spectacle. This is where the channel's reverence lives, and it is the retention core (competitor comment intel confirms the quiet beat is the emotional anchor viewers cite).
- **Short declaratives, present tense, hard verbs** — trailer-copy prose. The delivery voice (Ren) stays measured and reverent; the PROSE sprints. Pace lives in sentence length, not in read-rate.
- **End each act on a short, quotable button** — the shareable comment-section line.

**Directing grammar (the frame) — the VISUAL vocabulary:**
- **Low-angle hero worship**, subject against a bright sky. **Golden-hour / firelit as default light** — backlit, rim-lit, high-contrast toward LIGHT (this IS the bright-thumbnail fix at the frame level).
- **Scale via foreground/background stacking** — one human small against something vast (the 450, the storm wall, the fire column, the sea). Wide establishing → punch-in.
- **Consequence physics** — spectacle displaces air: shockwaves, embers, robes and dust hit by the pressure wave. Fire that arrives with WIND.
- **Slow-motion at the emotional peak only** — rationed (~5 per film), lives in the MOTION field at the gate, never in the still prompt.
- **Silhouette / backlit act-buttons** — the hero against fire, against the storm, against the light. (This is ALSO the face-drift defence per §5's tier system — the register and the face policy conveniently agree.)

**What we do NOT import from Bay/Woo:** no quips, no comic relief, no irony, no modern idiom — the faithful/devotional audience punishes all of it (§11's tonal test still governs). Keep the ENGINE (clocks, scale, spectacle, the one sincere core) and drop the comedy. The tonal ceiling is *the reverent epic* — Prince of Egypt's spectacle with a straight face, not Bad Boys' banter.

---

## 6. Length doctrine — retention first, length earned

*Banked 14 June 2026. This is the channel's defining production decision; it overrides the temptation to copy the long-form incumbents.*

**Do not open with 30-minute long-form from a cold start.** The constraint on a new channel is watch-time *signal density*, and the algorithm reads AVD as a **percentage**, not raw minutes. A 12-min video held to 60% sends a far stronger "this channel satisfies" signal than a 30-min video that dies at 35%. Every early video is auditioning with zero behavioural history; auditioning with your hardest-to-hold format before you know the hook retains is a mistake.

There's a production-risk leg too: a 30-min script is ~180+ beats — more stills, more Kling, more places to throw a spell-breaker or a pacing sag, and a long loop before you learn anything. At 10–14 min you get 3–4× the at-bats per unit of compute and review attention. **On a new channel, learning velocity beats episode grandeur.**

- **Phase 1 (videos 1–~15): 10–14 minutes.** One clean dramatic arc per video. The goal is not views — it's a **retention baseline**: where the average curve sits, and *where it drops*. The drops are the data. This is the banked-failure-as-principle loop that is the actual moat: we're not making Bible videos, we're calibrating the machine's hook-and-hold on a new audience.
- **Phase 2 (once a video or two holds ≥50% AVD): extend deliberately.** Long-form is now *earned* — format proven, and a subscriber base whose watch history tells YouTube to trust longer uploads. This is where the GIDEON 10.9M "4-hr Genesis Visualized" compilation model becomes available. Long-form is a Phase 2 weapon, not a Phase 1 bet.

**The counter-pressure, on record:** the niche skews long (Immersive runs 60–85 min from near-cold, and long-form stacks ad breaks in a 5–11 RPM niche). But Immersive is documentary narration over loose visuals — cheap per minute, easy to pad. Our format is photoreal recreation, where every minute is expensive. **We cannot out-length a documentary channel on a per-minute-expensive format; we out-execute it on hold rate.** Play our game, not theirs.

**The framing that resolves it:** *length is an output of retention, not an input.* Make each video as long as the story holds and not one beat longer. Let the curve tell you when you've earned the minutes.

**Phase 1 as executed (18 June 2026):** the launch slate shipped at Phase-1 length. Esther stands as the **30-min flagship** (the one deliberate long-form exception, the anchor). The **ten-video batch** runs **~7–13 min each** (28–56 beats; beat-floor runtime ≈ beat count × ~14s, which exceeds the words/153-wpm estimate — count beats, not words). Job (first shipped, 56 beats / ~13 min) sits at the top of the band; the back half runs leaner (Leah 28 beats, Daniel 32, David & Goliath 33, Samson 32). **On record: the leaner back half came in under the 12–14 target and was shipped as-is rather than padded** — consistent with "length is retention-earned, never padded to a benchmark." If Esther's and Job's curves prove longer earns its keep, extend the lean ones in Phase 2; do not pre-pad. The batch deliberately hedged a 10-video commit with shorter/cheaper/more-at-bats rather than ten blind 30-min renders.

**Dark-content handling — fidelity-of-intent, not fidelity-of-detail (banked from the batch).** Several batch stories carry genuinely difficult material (Sodom's mob, the stonings, Jezebel's death and the dogs, Samson's downfall, the temple collapse). The rule applied: **convey the wickedness/horror and its meaning faithfully, but imply rather than depict — no gore, no gratuitous specifics.** Sodom's mob reads as cruelty and threat without sexual specifics or Lot's daughters-offer; deaths are shown by aftermath and restraint ("only her skull, her feet, and the palms of her hands"), never graphically. This keeps the faithful audience's trust and protects monetisation while staying true to the text's intent. **If a story can't be told without graphic depiction, soften the frame, never the truth.**

**Instrumentation (non-negotiable, or Phase 1 teaches nothing):** read the retention graph in Studio per video, log *where* the drops happen (intro runway, midpoint lull, a specific weak beat), feed it back as pacing principles. The length decision and the retention-logging discipline are the same decision.

---

## 7. Title & thumbnail doctrine

**Complement, never echo.** The image carries the *what*; the title carries the *why-click*. They must not repeat the same nouns.

- **Title:** lead with the named figure + the dramatic/recognition hook. "Esther: The Orphan Who Became Queen and Stopped a Genocide." "Job: The Man God Allowed Satan to Destroy." Recognition-first (the name is the search/suggest floor), drama-second.
- **Lean into female leads** (the over-indexing pattern) in both the slate and the thumbnails.
- **Brand mark:** a consistent serif wordmark across banner and thumbnails once the name lands.

### ★ 7a · THE FOUR-CUT THUMBNAIL DOCTRINE (banked 05 July, from the Elijah competitor natural experiment)

*Four full-movie Elijah cuts, ranked by outcome, with title/length/subs varying — read as a strong HYPOTHESIS about strategy, with ONE locked negative. This is the channel's evidentiary thumbnail doctrine, replacing the earlier single-frame guidance.*

**The four cuts and what each thumbnail did:**
- **Power of the Word — 3.0M** — PRESTIGE PORTRAIT. One beautiful cinematic hero face, raven on shoulder, single blood-tear scratch. Wins on craft + emotional loading of a single striking face.
- **Unraveling — 2.7M (TINY CHANNEL)** — STACKED-SPECTACLE POSTER. Flaming chariot in the storm sky + fire column off the altar + ranked black ravens in the rain + Elijah small in the middle. Man dwarfed by spectacle. The image names the same three payoffs as the cold open.
- **Black and White — 763K** — SHOCK-CLAIM TEXT. Cartoonish Ken-Burns art (worst image of the four) but the TEXT does the work: "HE KILLED 450 MEN." A number-driven claim that forces a question. Proves a text-claim can carry a weak image.
- **The Bible Journey — 99K (THE LOSER)** — INERT PORTRAIT. Competent, photoreal man + raven + canyon, nothing happening. A "who," not a "what." No spectacle, no claim, no exceptional craft.

**What the four teach — there is NO single winning composition.** Poster-vs-portrait is the wrong axis. There are **three distinct winning strategies** — spectacle-stack, shock-claim text, prestige-face — and each beats an inert portrait decisively. The dividing line: does the thumbnail contain an unanswered question, a claim of scale, OR an exceptional emotionally-loaded face — versus does it just show a competent figure doing nothing.

**THE ONE LOCKED PRINCIPLE (negative, high-confidence): never ship the inert portrait** — a figure doing nothing, with a label ("ELIJAH / THE MOVIE"), no claim, no stacked event, no prestige grade. It is the single composition in the set that LOST. This replaces the old "a single legible emotional beat" guidance where that beat is inert — a face at a genuine emotional PEAK (terror, resolve, grief) is prestige-face and wins; a calm portrait is the inert loser.

**THE CHANNEL DEFAULT: the Unraveling stacked-spectacle poster.** Chosen deliberately, for operator-fit reasons (matches the Synthetic §13 Elijah pilot decision):
1. Unraveling is the TINY channel that won — the strategy that beats established channels from cold, which is Scripture On Screen's exact position.
2. It's the strategy an AUTOMATED FACTORY builds deterministically. The prestige-face gambles on one flawless portrait landing; the stacked poster is a COMPOSITE OF LAYERS (hero + fire column + chariot-in-sky + ranked ravens + storm grade) — each a beat the pipeline already produces. Assemble a promise out of parts rather than betting on one shot.
3. It aligns with the cold-open: the thumbnail names the same payoffs the narration names in the first 45 seconds. One question, asked three ways, answered only by watching.

**Composition + lighting spec (banked from the Elijah thumbnail prompt iterations):**
- **Stacked payoffs in one frame** — hero + fire column + chariot-in-sky + ranked ravens + storm/weather grade. Weather is free drama: storm, rain, lightning, god-rays. Cinematic-biblical runs STORMY/blazing, not flat daylight.
- **Hero scale is a FEED-SIZE decision, not a big-screen one (banked from the four-thumbnail generation pass).** The "man dwarfed by spectacle" ideal is a big-screen virtue that can HURT legibility at 120px — a commanding mid-frame hero reads at feed size where a tiny one vanishes. On the flagship generations, the arms-wide central hero out-performed the dwarfed one. So: dwarf-by-scale in the WIDE composition, but keep the hero large enough to read at 120px. Judge every candidate shrunk to ~120px — pick the one that survives the feed, never the prettiest at full size.
- **Lighting is the #1 CTR lever — warm/cool split (banked from the Elijah lighting prompt).** The eye stops on the brightest, warmest point in a field of dark thumbnails. Make the hero's lit face and the fire the brightest, warmest things in frame; let the storm go cooler and deeper (blue/violet rain and lightning) around them. "Faces and fire are the brightest points in the frame" + a hot RIM-LIGHT on the hero forces separation from the dark sky. This is the frame-level version of the §5 scrub: bright hero against cooler storm, never a uniformly dark or uniformly muddy frame. Add blockbuster teal-and-orange only as a complementary-contrast nudge (biblical grade: gold hero vs blue storm).
- **Wordmark gets its own dead space — NEVER overlapping the face or the central action (banked from the Elijah generations).** The winning Unraveling thumb kept its wordmark in the clear left third. This is a `make_thumbnail.py` LAYOUT CONSTRAINT, not a prompt instruction: reserve a text zone, composite the hero to avoid it, keep the bottom ~15% clear for the mobile duration stamp / UI chrome. Text-on-thumbnail is deterministic Pillow compositing (canonical §6 — models can't render legible type), not a Flux prompt; the current `figure_right` composition already reserves the left third — hold that.

**make_thumbnail.py consequence (banked as tool design).** The thumbnail is a STRATEGY-SELECTION + COMPOSITION problem, not a spend problem. The tool should support all three winning grammars as modes — (1) stacked-payoff poster [the channel default for spectacle stories], (2) big-claim text overlay [for the number/claim stories — "SHE STOPPED A GENOCIDE"], (3) prestige single-hero grade [for the intimate character stories — Ruth, Leah]. The per-video decision is which the story affords. The hard guard: **never emit an inert figure-with-label.** The moat is the pipeline KNOWING the poster grammar, not any hand-crafted hero shot.

- **Still avoid:** the apocrypha/forbidden register entirely (that's Sacred Dawn / Audience B — "BANNED," "the book they hid," "NOT human"); the sepia "biblical-mystery" wash; cartoon/animation aesthetics; stock reaction-faces and pointing fingers. **The scrub sharpens the anti-sepia point into a positive: don't just avoid the sepia wash — beat it with a bright, warm/cool-split, high-contrast poster that pops against the niche's uniform murk.**

---

## 8. The episode backlog (canonical slate, best-first)

Apocrypha stripped out (that's Sacred Dawn). Canonical only, ordered by a blend of proven demand and cold-start success. Ship the top few fast — you only need one to catch. Best-first ordering: do **not** let channel averages drive sequencing.

**Status as of 18 June 2026 — first 12 of the slate authored; Esther + Job shipped; 10 batching.** Each item is a `<slug>.md` beat-script + `<slug>.thumb.json` pair. Legend: **[SHIPPED]** / **[BATCHING]** (rendering, publishing nightly 19–28 June) / unmarked = backlog.

1. **Esther** — 2.4M proven. The orphan who became queen and stopped a genocide. Female lead. **[SHIPPED — flagship, 119 beats / ~30 min, the one long-form exception. Needed a phone-verified account for the >15-min upload.]**
2. **Job** — 1.4M proven. The man God let Satan destroy to test him. Universal suffering-and-faith. **[SHIPPED — Phase-1, 56 beats / ~13 min; the single-video test that proved upload path + music level on this channel.]**
3. **Sodom & Gomorrah** — 1M proven. Judgment and fire from the sky — photoreal destruction spectacle. **[BATCHING — 47 beats; spine = "do not look back" → Lot's wife → pillar of salt.]**
4. **Jezebel** — 968K proven. The most wicked queen who ever lived. Villain hook, female lead. **[BATCHING — 49 beats; spine = the "dogs will devour her" prophecy → wall of Jezreel, twenty years later.]**
5. **Ruth** — 930K proven. Loyalty and devotion; the foreign widow who became King David's bloodline. **[BATCHING — 37 beats; the warm tonal palette-cleanser; vow on the road → the line of David.]**
6. **Noah's Flood** *(human-drama lens — Noah and family, NOT the cosmic order; that's Sacred Dawn)* — inferred tentpole (GIDEON Genesis 10.9M). **[BATCHING — 34 beats; Watchers/Nephilim deliberately kept OUT per the Genesis-seam ruling; flood cause = general human violence. The spectacle showcase.]**
7. **Joseph** — the coat, the betrayal by his brothers, the rise in Egypt. **[BATCHING — 38 beats; spine = the coat + "you meant it for evil, God meant it for good."]**
8. **David & Goliath** — the shepherd and the giant. Maximum recognition; a single iconic beat. **[BATCHING — 33 beats; spine = "measure the giant against God, not yourself."]**
9. **Daniel: The Lion's Den** — photoreal set-piece. **[BATCHING — 32 beats; spine = the open window. NOTE: authored as the lions' den ALONE, not the den+furnace two-hander the original slate proposed — the den is the tighter single arc; the fiery furnace is now its own future topic (#20).]**
10. **Leah** — 611K proven. The unloved sister nobody chose. Female lead. **[BATCHING — 28 beats, the leanest; spine = the son named in praise (Judah) → the line of kings; "God saw her."]**
11. **Samson & Delilah** — superhuman strength, betrayal, the temple collapse finale. **[BATCHING — 32 beats; spine = "his hair began to grow again."]**
12. **Moses at the Red Sea** — the parting; the single most iconic spectacle in the canon. **[BATCHING — 35 beats; the batch's spectacle capstone; God acts only when they've run out of their own way. PROMOTED from #19 to round out the batch of ten — max recognition + clean Sacred Dawn separation.]**

*Remaining backlog (unbuilt), best-first:*
13. **The Ten Plagues of Egypt** — blood, locusts, darkness, the firstborn. Photoreal gold. *(Note: lightly covered inside Red Sea's Act 1; the standalone can go deeper.)*
14. **Nebuchadnezzar** — 158K proven. The king who went mad and ate grass for seven years.
15. **Cain & Abel** — 54K proven. The first murder; clean dramatic two-hander.
16. **Abraham & Isaac** — the binding; the hardest test of faith in the canon.
17. **Jacob & Esau** — 96K proven. The stolen birthright, the brothers' rupture.
18. **Jonah** — the prophet, the storm, the great fish, the reluctant mission.
19. **Abigail** — 90K proven. The woman who stopped David from a massacre. Female lead.
20. **The Fiery Furnace** — Shadrach, Meshach, Abednego; the fourth man in the fire. *(Split out from the Daniel entry — its own set-piece.)*
21. **The Revelation / end-times cluster** *(canonical — stays here; the devotional audience cares deeply about prophecy)* — its own sub-lane once the channel has trust.

### The 26 June levelling gap-fill — shipped (1 video)

*One Scripture video staged via `stage_batch.py` and run through the batch-of-batches as part of portfolio runway-levelling. Unlike the other channels' tail-extensions, Scripture was already scheduled solid through 09 July — this single video fills the one internal hole on **Sat 04 July** (left when the `jacob-esau` render failed at the stills leg). Published 04 July 01:00 CEST. SHIPPED — do not re-author.*

- **`jericho`** — the fall of Jericho (the march, the trumpets, the walls). New topic, not from the numbered backlog above; chosen to fill the 04 July gap. A clean spectacle set-piece in the channel's lane.

*Status note on `jacob-esau` (#17): the half-built `jacob-esau` project (voiceover banked, failed at stills) is **abandoned** as of this session — `jericho` fills the 04 July slot it would have taken. #17 remains in the backlog as an unbuilt topic if you want to author it fresh later; the old broken project is not being resumed.*

**The craft spine (banked from authoring all ten — the reusable script skeleton).** Every batch script was built on the same structure, and it should be the template for future authoring: **cold open *mid-action*** (the disaster/threat already happening — Sodom opens on the fire and the salt pillar, Jezebel at the window facing her killer, Joseph already in the pit), then "to understand… you have to go back," then the story; a **recurring spine object/phrase planted early and paid off at the climax** (the spines listed per-item above); **face tiers folded into the VISUAL lines** (FACELESS default / identity-by-costume carrier / rationed single hero-face at peaks); a **moralised close** that turns the story to the viewer; a **comment-bait question**; and a **sequel hook chaining to the next video** (Job → Sodom → Jezebel → Ruth…). Numbers spelled out, no beat over ~55 words, one VISUAL per beat.

*Sequence logic: open on Esther (highest proven + female lead), then alternate a recognition draw with a proven mega-drama so you never publish two "quiet" topics back to back. **As executed, the batch publishes in inbox filename-sort order, NOT curated best-first order** (daniel → david-goliath → jezebel → joseph → leah → noahs-flood → red-sea → ruth → samson-delilah → sodom-gomorrah). For evergreen content this doesn't matter; if publish sequence ever matters, control it via slug naming or separate staggered runs. Every topic is evergreen — no timing pressure.*

---

## 9. Channel config & facts

- **Name / handle:** **Scripture On Screen** — `@Scripture-On-Screen` (**created 14 June**). **Channel ID:** `UCTNSGkPgEHGZtXQeFoPvjcQ` (for the YouTube Data API upload step). **URL:** youtube.com/channel/UCTNSGkPgEHGZtXQeFoPvjcQ. **Display name:** Scripture On Screen (note: capital "On", per the live channel). Chosen on the expectation-management argument (§4): a *medium* promise, not a *fidelity* promise — the right contract for output that takes visual liberties. **Rejected and why:** "The Biblical Canon" (open, but over-promises textual fidelity → invites the knowledgeable faithful audience to police the gap); "Biblical Reimagined" / "Screened Scripture" (imply *altered* / *filtered*); "Canon & Cinema" / "Biblical Cinema" / "Canon Cinematic" (the "____ Cinema" root is a saturated swarm — Scripture Cinema TV, Scripture Cinema Films, Bible Cinema, Sacred Cinema — newest-entrant trap); the render-family roots (Rendered Scripture etc.) likewise saturated. **Claim the handle in YouTube Studio now**, before art is ready, to lock it.
- **`channel:` header value:** `scripture_on_screen` → resolves to `scripture-on-screen/` via the underscore→hyphen swap. (When in doubt set to exact folder name.)
- **channel.json schema** (matches live `prehistoric-disasters/channel.json` — the reference carrying both blocks): `name`, **`voice_id`** (snake_case), `style_suffix`, `default_music_prompt`, `base_canon`, `default_motion`, `upload: {category_id, privacy_status}`, **`thumbnail: {...}`** (auto-thumbnail config), **`music: {dir, tracks, crossfade_seconds, level}`**. No resolution key. **`thumbnail` + `music` blocks added 18 June** via `patch_sos_thumbnail_music.py` (idempotent, schema-checked against Prehistoric). Thumbnail block tuned for this channel: `composition: "figure_right"` (figure massed right-two-thirds, left third reserved for the headline), warm-gold `subtitle_color: [240,195,90]`, softened `scrim.opacity: 0.45` (vs Prehistoric's 0.55, so vivid thumbnails aren't crushed to murk), Anton font + proven overlay mechanics kept. `speaking_rate` deliberately **omitted** — Ren runs native (Prehistoric's `0.9` was tuned for Victor; don't copy blindly).
- **Voice:** **`voice_id: "Ren"`** (selected — §5). Model `inworld-tts-1.5-max`.
- **Look (`style_suffix`):** **SCRUBBED 05 July** — bright blockbuster-photoreal, desert-gold/lapis/crimson, high-dynamic-range, "chiaroscuro/oil-painting/painterly" STRIPPED (§5). Per-story palette override layered on top (Esther = crimson/gold/lapis).
- **Motion:** **SCRUBBED 05 July** — dynamic/kinetic blockbuster energy as the default (not the old FH slow-intimate-push-in); slow push-in reserved as a per-clip choice for rationed quiet beats + per-clip discretion on Mission Control. Per-beat MOTION vocabulary is **banked for later**, cross-channel (§5).
- **Face policy:** single expressive hero faces permitted; avoid 3+ crowds; **always `safety_tolerance: "5"`** on Flux (§5).
- **Presentation:** narrator style, no lip-sync (lip-sync is a future upgrade — §5).
- **Music:** warm orchestral storytelling score (§5). **Curated Artlist bed (resolved 18 June)** — 8 tracks in `scripture-on-screen/music/`, assembler picks 3 at random end-to-end, 2s crossfade, `level: 0.07` (validated correct on Job). `make_music.py` is fallback-only.
- **Mode:** Mode A only. **Length:** 10–14 min (Phase 1).
- **Category:** Entertainment (`24`). Tags from the header.
- **Source text:** `base_canon` = WEB default (KJV only where cadence earns it) — §5.
- **Production economics:** ~$20/video target; the "Amazon Prime of the Bible category" quality tier (§1).

**Live `channel.json` (v2.0 SCRUBBED target — `style_suffix` + `default_motion` rewritten 05 July; `default_music_prompt` gains the swell note):**
```json
{
  "name": "scripture_on_screen",
  "voice_id": "Ren",
  "style_suffix": "cinematic biblical blockbuster film still, photorealistic, richly saturated jewel tones, desert gold and lapis and crimson, bright vivid exposure with rich detail in shadows, high dynamic range, blazing golden-hour and firelit light, lush fabrics and gold and lapis ornament, intense dramatic lighting, lots of light and energy, crisp and dynamic, high production value, period-accurate ancient Near East Egypt and Persia, gritty realistic texture, expressive detailed faces, sharp focus, no text, no letters, no modern elements, 16:9",
  "default_music_prompt": "Warm orchestral storytelling score for a cinematic biblical drama. Emotive strings and woodwinds, hopeful and humane, swelling brass on moments of triumph, harp and gentle choir on tender beats, and full epic scale (brass, choir, percussion) on spectacle beats. Melodic but never competing with a narrator. Intimate and grand by turns. No modern instruments.",
  "base_canon": {},
  "upload": { "category_id": "24", "privacy_status": "private" },
  "default_motion": "dynamic cinematic camera movement, powerful momentum, energetic movement across the scene, dramatic push-ins and pulls, natural realistic motion, dramatic atmosphere",
  "thumbnail": { "composition": "figure_right", "candidates": 2, "subtitle_color": [240,195,90], "scrim": {"side":"left","width":0.42,"opacity":0.45,"feather":0.7}, "font": "shared/fonts/Anton-Regular.ttf", "...": "(full overlay block — see live file / patch)" },
  "music": { "dir": "music", "tracks": 3, "crossfade_seconds": 2, "level": 0.07 }
}
```
*Live `name` is `scripture_on_screen` (snake_case, resolves to `scripture-on-screen/`), `base_canon` is `{}` (not `"WEB"`), `privacy_status` is `private` — batch uploads go up private + `publishAt` so YouTube auto-publishes on schedule. Per-story palette (Esther's crimson/gold/lapis) is a prompt-level override on the slug, not baked into `style_suffix`.*

### 9a · THE SCRUB — what to change, exactly (config-code review, 05 July)

**Answer to "is it only the channel.json?" — no, it's THREE places (canonical §2B + `_QQrew.md §4b` teach this):**

**(1) `channel.json` — the primary + immediate fix (three blocks). Config change = `python3 -c` one-liner on the BOX, never a hand-edit.** The `style_suffix` is the single highest-leverage lever on look (canonical §8); this is 90% of the scrub. One-liner (run on BOX, then re-render a test still to verify at the artifact):
```
python -c "import json,io; p='scripture-on-screen/channel.json'; d=json.load(open(p)); d['style_suffix']='cinematic biblical blockbuster film still, photorealistic, richly saturated jewel tones, desert gold and lapis and crimson, bright vivid exposure with rich detail in shadows, high dynamic range, blazing golden-hour and firelit light, lush fabrics and gold and lapis ornament, intense dramatic lighting, lots of light and energy, crisp and dynamic, high production value, period-accurate ancient Near East Egypt and Persia, gritty realistic texture, expressive detailed faces, sharp focus, no text, no letters, no modern elements, 16:9'; d['default_motion']='dynamic cinematic camera movement, powerful momentum, energetic movement across the scene, dramatic push-ins and pulls, natural realistic motion, dramatic atmosphere'; json.dump(d,open(p,'w'),indent=2,ensure_ascii=False); print('scrubbed')"
```
(The `default_music_prompt` swell-edit and any thumbnail-block tweak are optional follow-ups; the suffix + motion are the load-bearing pair.)

**(2) The engine reference-lock — ALREADY channel-overridable (verified in code 05 July, correcting an earlier draft). NO code change needed.** `_generate_still_reference()` in `recreation_pipeline.py` already reads the lock/tail from channel.json with the module constant as fallback:
```
lock = config.get("reference_prompt_lock", REFERENCE_PROMPT_LOCK)
tail = config.get("reference_prompt_tail", REFERENCE_PROMPT_TAIL)
```
So the re-contamination trap (a hardcoded FH-moody lock overriding a bright channel, `_QQrew.md §4b #3`) is **already closed at the call-site** — the per-channel override the QQrew scrub prescribes was already built. **Consequence: giving the Elijah flagship a bright biblical reference lock is a pure `channel.json` CONFIG EDIT, not a code patch** — add `reference_prompt_lock` + `reference_prompt_tail` keys with a bright biblical identity-hold string (the QQrew de-mooding pattern: identity-hold + "bright, vivid, high-key, blazing golden-hour / firelit light, the figure lit bright and heroic — never dark, never shadowed, never murky"). The engine resolves them automatically. **This is NOT a flagship blocker (the mechanism exists); the only work is AUTHORING the bright lock string as a config value when the reference-locked Elijah hero is built. The key names are `reference_prompt_lock` / `reference_prompt_tail` — match them exactly.**

**(3) Portfolio-wide FH code-leakage defaults (canonical §2B list) — confirm, likely already clear.** `_tiered_kling_count` defaults to 40 (Scripture sets kling_count explicitly per batch → not bitten); the thumbnail house-look darkening layers (Scripture's scrim is already softened to 0.45 → not bitten). Confirm both on the box; likely no action.

**The verification rule (do NOT judge the scrub by the config):** after the one-liner + a `git`-free box config edit, RE-RENDER one test still (a spectacle beat) and eyeball it for brightness. The style_suffix reaches only stills generated by processes started AFTER the change, and Mission Control caches — restart the service (only while nothing renders) or launch fresh. Verify at the artifact (canonical §8).

**Batch inbox location (design decision, 18 June) — per-channel, never pipeline-root.** The inbox lives at **`scripture-on-screen/batch_inbox/`**, beside `projects/`, `music/`, `channel.json`. Rationale: multiple channels may batch concurrently; a shared pipeline-root `batch_inbox/` collides on slug names and makes `--channel` ambiguous. The runner takes `--inbox <path>` as a free path, so this needed **no code change** — just `--inbox scripture-on-screen/batch_inbox`. **This is now the standing convention for all channels.** (One trap seen: a `git mv` of the old root inbox dragged the already-published Job along — always `ls` the inbox and eyeball the count before a run.)

---

## 10. Launch state & roadmap

**LAUNCHED — Esther + Job shipped; 10-video batch rendering (as of 18 June 2026).** Everything in the 14 June pre-launch list (positioning, thesis, boundary, length doctrine, expectation-management, slate, name, look/motion/face/music spec, $20 tier, narrator-style, Ren voice) is locked and proven in production.

**What shipped, in order:**
1. `channel.json` stood up (`scripture-on-screen/`); Ren verified working on the box (real synth, no silent Victor fallback). **Done.**
2. **Esther flagship published** — 119 beats / ~30 min, the deliberate long-form anchor (needed a phone-verified account for the >15-min upload).
3. **`thumbnail` + `music` blocks added** to `channel.json` (18 June, `patch_sos_thumbnail_music.py`), tuned for the vivid figure-led look (§9). Curated Artlist bed of 8 tracks dropped into `scripture-on-screen/music/`.
4. **Job single-video test** — run via an isolated inbox at `--kling-count 0` (all Ken Burns, cheap) to validate the two unknowns: **upload path (passed — landed private with auto-thumbnail) and music level (passed — choice and `0.07` both correct first try).** Then published. (Motion not re-tested — proven identical on other channels.)
5. **Per-channel batch-inbox design** adopted — moved the inbox under `scripture-on-screen/` (§9, §12).
6. **Ten-video batch launched** (18 June) via `run_batch.py`, `--kling-count 2`, staggered `--publish-interval-hours 24` from `2026-06-19T01:00:00+02:00`. Publishes nightly 19–28 June. Dry `--plan` confirmed 10 projects, all pairs matched, slots stepping 24h. See §12.

**Open / next, in order:**
1. **Let the batch finish** — sequential, failure-isolated; **do NOT restart `mission-control.service` while it animates** (cgroup teardown kills the in-flight run). Read the manifest (`scripture-on-screen/batch_inbox/_batch_manifest_*.json`) for shipped/failed per slug when done; re-run any failed slug via an isolated inbox.
2. **Read the curves — the actual job now.** Pull **CTR + AVD in the first 48 h** for Esther, then Job, then each batch video as it goes live — **via NexLev MCP from the connected channel, never pasted tables/screenshots** (a scrambled paste once caused a wrong cut recommendation). NexLev AVD field is unreliable for recently-launched channels; compute AVD as `(total watch-minutes × 60) ÷ total views`. Log *where* retention drops (§6).
3. **Decide Phase 2 from the data, not speculation:** does the leaner back half (Leah/Daniel/David ~7–8 min) hold as well as Job's ~13 min? If longer earns its keep, extend the lean ones and/or commit more 30-min flagships. If not, tight Phase-1 length is vindicated. Let the curve speak before authoring the next slate.
4. **Next authoring batch** from the §8 remaining backlog (Ten Plagues, Nebuchadnezzar, Cain & Abel, Abraham & Isaac, Jacob & Esau, Jonah, Abigail, Fiery Furnace), sequenced by which *story type* (female-lead drama / spectacle / quiet) over-performs on THIS channel specifically once the first curves are in.

**Banked for later (not dependencies):** per-beat MOTION vocabulary → Kling (cross-channel Mission Control upgrade, §5); lip-sync (§5); character-reference for tighter face consistency (§5); per-story Kling-count tuning (the batch ran `--kling-count 2` — first two beats Kling, rest Ken Burns; raise for spectacle-heavy stories once curves justify the spend); generated `make_music.py` (fallback only).

**Watch across the batch:** retention curve shape (first-30s runway, act-break transitions), CTR per packaging, whether Ren holds US viewers across the leaner cuts, which *stories* spike (female-lead vs spectacle vs quiet), and whether the figure-led `figure_right` thumbnails out-click the niche's sepia-mystery wash. Data drives the next slate and the length call.

---

## 11. Appendix — the packaging test (faithful vs. shock-bait, as a feed)

The faithful-recognition titles read *coherent* under this channel; the shock/apocrypha titles *jar* (and belong to Sacred Dawn). Run the eye-test before publishing any title.

**Run these (faithful, this channel):** "Esther: The Orphan Who Became Queen" · "Job: The Man Who Lost Everything" · "Ruth: The Foreigner Who Became a King's Bloodline" · "David and Goliath: The Shepherd and the Giant" · "Daniel in the Lions' Den."

**Never run these (shock-bait / apocrypha — wrong audience, wrong channel, monetisation risk):** "The Book They BANNED From the Bible" · "Noah Was NOT Human" · "The TERRIFYING Truth About the Nephilim" · "What the Church is HIDING." *(These are Audience B — if a title like this fits the video, the video belongs on Sacred Dawn.)*

*The line: faithful recognition over manufactured mystery. The canon is the asset; reverent photoreal best-execution is the moat; the two-audience split is the strategy.*

---

## 12. The batch-runner launch playbook (executed 18 June 2026 — the reusable recipe)

*Exactly how the first 10-video batch shipped through `shared/run_batch.py`, banked as the repeatable procedure for every future batch on any channel. The runner takes a folder of `<slug>.md` + `<slug>.thumb.json` pairs and runs each through the FULL pipeline unattended (gates auto-accept; audio → Mode A → convergence → assemble → thumbnail → upload), sequential and failure-isolated, ending in a private upload (+ `publishAt` if scheduled).*

### The pair format (per topic)
- **`<slug>.md`** — the locked beat-script. 4-line header (`channel: scripture_on_screen` / `title:` full SEO title / `description:` ending "Welcome to Scripture On Screen." / `tags:`), then `## SECTION` headers, then beats as an `[A] <narration>` line + a `VISUAL: <prompt>` line. **No beat numbers** — only the `[A]` marker. Face tiers folded into the VISUAL text (FACELESS / identity-by-costume / "single expressive hero face"). Numbers spelled out. One VISUAL per beat. Runtime ≈ beat count × ~14 s.
- **`<slug>.thumb.json`** — `{"subject": <Flux scene, with composition note putting the figure right-two-thirds + left third open for text>, "title": <short punchy thumbnail headline>, "subtitle": <small descriptor>}`. The thumb `title` is **deliberately different** from the SEO `title` in the .md header (§7 complement-never-echo). Dot-naming matters: `<slug>.thumb.json`, not `<slug>_thumb.json`, or the runner silently skips it. A `.md` with no sibling `.thumb.json` is SKIPPED with a warning.

### `run_batch.py` flags (full set)
- `--inbox PATH` (required) — folder of pairs. **Use the per-channel path `scripture-on-screen/batch_inbox` (§9), never pipeline-root.**
- `--channel NAME` (required) — channel dir name, e.g. `scripture-on-screen`.
- `--kling-count N` — tiered render: **first N beats get Kling true-motion, the rest Ken Burns.** `0` = all Ken Burns (cheapest; the Job test path). The batch ran **`2`** (cold-open beats move, rest free).
- `--plan` — prep preview only, **zero spend**, prints the full release calendar. Always run first.
- `--limit N` — process at most N (testing). No per-slug "only this one" flag exists → isolate a single video via a dedicated inbox folder.
- `--publish-start ISO8601+TZ` — `publishAt` for the FIRST video; **timezone offset is mandatory** (naive timestamps rejected). Omit → private-immediate.
- `--publish-interval-hours H` — spacing between successive `publishAt` (default 12). Batch used **24** — wide enough that each video's first-48 h CTR/AVD is legible before the next drops.

### The executed sequence (LAPTOP edits → GitHub → BOX pull-only)
1. **Author** all pairs; copy into `scripture-on-screen/batch_inbox/` in the repo on **LAPTOP**.
2. **Drop the music bed** — 8 space-free-named tracks into `scripture-on-screen/music/`.
3. **Commit + push** (`git add` inbox + music; `git pull --no-edit`; commit; push). **BOX:** `git pull`.
4. **Remove any already-published slug from the inbox** or the runner re-renders it (`ls` and eyeball the count first).
5. **BOX:** `set -a; source .env; set +a`.
6. **BOX dry plan (zero spend):** `python shared/run_batch.py --inbox scripture-on-screen/batch_inbox --channel scripture-on-screen --kling-count 2 --plan --publish-start 2026-06-19T01:00:00+02:00 --publish-interval-hours 24`. Confirm: correct **count**, every `.md` has its `.thumb.json` (no skip warnings), slots step by the interval.
7. **BOX real run, detached:** `nohup python shared/run_batch.py --inbox scripture-on-screen/batch_inbox --channel scripture-on-screen --kling-count 2 --publish-start 2026-06-19T01:00:00+02:00 --publish-interval-hours 24 > ~/sos_batch.log 2>&1 &` then `tail -f ~/sos_batch.log`.

### Hard-won gotchas (bank these)
- **`mission-control.service` restart = death.** Never restart it while a batch animates — cgroup teardown kills in-flight runs. (Backlog: daemonize.)
- **Publish-slot vs render-time.** Each video must finish uploading *before* its `publishAt`, or YouTube publishes immediately on upload (past timestamp). A 01:00 first slot against a multi-hour render is tight — give cushion (later start) if the render might overrun the first slot.
- **Filename-sort publish order, not curated order** — control via slug naming or separate runs if it ever matters.
- **Test the unknowns cheaply first** — one slug via isolated inbox at `--kling-count 0` validates upload + music without Kling spend. Motion didn't need re-testing (proven on other channels).
- **`safety_tolerance: "5"` on Flux** (channel-wide) or stills silently return ~7KB black PNGs.
- **`assemble_episode.py` is the only safe assembler** (honors the beat→shot map); never the alignment-unsafe `finish --assemble-only` path.

---

## 13. Next-session focus (set 18 June 2026)

**The job next chat is to READ THE DATA, not author.** The Phase-1 batch exists to produce curves; the curves are the deliverable.

1. **Confirm the batch shipped clean** — check `_batch_manifest_*.json` for failed slugs; re-run any that errored (failure-isolated, so the rest completed).
2. **Pull CTR + AVD first-48 h via NexLev MCP** (connected channel, never pasted) for Esther → Job → each batch video as it goes live. By next session some videos are live with real numbers and others still pending — **don't read a curve before a video has a genuine 48 h.**
3. **Answer the three questions the data settles:** does the lean back half (~7–8 min) hold like Job's ~13 min (→ length call)? which story type over-performs on this channel (→ slate weighting)? do `figure_right` thumbnails out-click the sepia wash (→ packaging)?
4. **Log where retention drops** per video (§6 instrumentation) → pacing principles.
5. **Only then** author the next backlog batch (§8 #13–20), sequenced by what won.

**Cross-channel promotion owed:** the §12 batch playbook and the per-channel-inbox convention are **not** Scripture-specific — promote them to the canonical reference / `run_batch.py` docstring when those are next touched, so every channel inherits them.

---

## 14 · THE ELIJAH FLAGSHIP (inherited 05 July — the channel's blockbuster tentpole)

*Elijah is scoped as the channel's flagship blockbuster. The full design work — competitor reverse-engineering, spine, packaging, thumbnail — lives in `scripture-on-screen/projects/_Elijah-Blockbuster-Design.md` (design doc v2.0). This section banks the STRATEGIC findings into channel doctrine so they survive as the channel's, not one project's. When the channel goes blockbuster, this is the project it inherits from.*

**Why Elijah, and why it's the flagship (the demand evidence — carry it, never just the conclusion):**
- **Double-validated at the top of the lane:** Elijah did **3.0M (Power of the Word) AND 2.7M (Unraveling the Scriptures)** — two independent operators, same story, both breakout. Two independent signals agreeing is the strongest demand proof this game offers (canonical §9 #19).
- **The controlled pair that proves it's the CUT, not the channel:** Grace For Purpose (large, established) and Unraveling (near-cold) ran the IDENTICAL title, same ~68-min length, same month. Grace got 118K; Unraveling got **2.7M — 23×, with the smaller channel winning.** This kills reach/authority/subs/timing as explanations and isolates the cut + packaging. **This is the single most important competitive datapoint the channel owns: from a cold start, the CUT and the PACKAGING beat an established channel's reach.** It is `_Synthetic2.md §2`'s "rising format wave with multi-winner tolerance" made concrete — the graph feeds the FORMAT, entrant N wins on tier-above craft + cadence, not incumbent weakness.

**Required-to-win, banked as channel doctrine (present in every multi-million cut, absent in the flops):**
- **The trailer cold-open naming all payoffs (fire / whisper / chariot) in the first ~45 seconds.** Confirmed across FOUR independent cuts across a full year — robust cross-time doctrine. The 763K cut does it on cheap Ken-Burns zoom and still won: **the structural move outweighs production polish.** This is the channel's cold-open law for every spectacle story now, not just Elijah.
- **The human-doubt thesis stated up front** — the top performer (3.0M) promises the interior movie too ("his greatest battle was against himself"). Two promises in the cold open: spectacle AND interior.
- **The retention mandate (off the channel's own Revelation curve, IMG_3517):** the Revelation film holds 27.3% AVD lifetime on 70 min — render gate PASSED, long-form holds. But the curve SHAPE is the lesson: a brutal first-minute cliff, then a sticky tail. **Over-engineer the first 90 seconds and first 5 minutes; pull a spectacle beat early (min 2–5); never run a patient drought-build before the first spectacle.** This is now channel doctrine for any long-form cut, inherited from the Revelation feature.

**Incidental (varies freely across the winners — does NOT predict outcome, so don't over-invest here):** length (48/67/90 min all won), delivery speed (106/168 wpm both won), production tier (photoreal-lip-sync AND Ken-Burns both cleared 750K+). **Consequence: the channel does NOT win Elijah by out-photorealing the competitors** (Unraveling already has lip-sync the pipeline can't match). The moat is STRUCTURE + PACKAGING + the cold-open, exactly as canonical §2 insists — a banger is engineered at the cold-open and thumbnail, not bought with Kling spend (Grace For Purpose spent more and lost). This DERISKS the flagship: the expensive render is not where the win comes from.

**Register:** the Bay/Woo blockbuster grammar (§5b), in the channel's bright biblical grade (§5) — and the Final Hours dread register is EXPLICITLY BANNED from this project, as it now is channel-wide. Elijah is the first full expression of the scrubbed register.

**Prerequisites before any Elijah render (on the critical path):**
1. **Bright biblical reference lock — AUTHORING only, no code (§9a #2, verified 05 July).** Elijah is a single recurring hero across ~60 min, rendered via the reference `/edit` path — which BYPASSES the `style_suffix`, so the lock/tail are the only style instruction on hero beats. The engine ALREADY resolves `reference_prompt_lock` / `reference_prompt_tail` from channel.json (fallback to the constant), so this is NOT a code blocker: the work is writing a bright biblical lock string and adding it as a config key. Without it the FH-moody constant renders a dreary Elijah (the pouty-Skeptic bug, `_QQrew.md §4b`); with it, the flagship hero is bright. Author the lock alongside the script.
2. **Parallel-fal semaphore** (`_Synthetic2.md §11 1`) — seven Kling set-pieces at feature length is 6–11h sequential; the bounded-concurrency semaphore cuts it ~5–8×.
3. The thumbnail ships the stacked-spectacle poster (§7a), the channel default.

**Cost:** a heavy-Kling flagship, deliberately 2–3× the ~$20 Ken-Burns floor — justified only because the lane's floor is six figures and its ceiling is 2.7M/3.0M, and because the win comes from the cheap parts (cold-open + packaging), the Kling spend only buying the set-pieces the cold-open promises.

---

*Maintained by Peter + Claude. Update when the name lands, when the voice is chosen, when the first-video retention data is in, and when the competitive cohort shifts. This is the channel's creed: the canonical Bible, told faithfully, rendered photoreal AND BRIGHT (the FH dread register scrubbed 05 July), for the faithful audience Sacred Dawn doesn't serve — the reverent story told straight, on a blockbuster screen.*
