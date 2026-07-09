# _BentleyandWatson.md

Per-channel doctrine. Sits under `__YOUTUBE-MEDIA-FLYWHEEL-canonical-reference.md`. Read the umbrella first; pull `PIPELINE_PLAYBOOK.md`, `ORCHESTRATOR-DEPENDENCY-MAP.md` and the relevant session notes when a task needs them. `_` prefix = channel doctrine (this file). `__` prefix = channel-agnostic system docs. Worklog is the volatile buffer; durable lessons from this channel graduate up into here.

Status: **canon locked; wordless path shipped and proven; stills gate reached.** Identity gate cleared — NB2 `/edit` holds both dogs off real-photo seeds. Five locked canon files in `bentley-and-watson/characters/`: `bentley_ref_clean`, `watson_ref` (faces), `bentley_body_clean`, `watson_body_clean` (proportions), `pair_body` (relative scale). Bentley's six-expression stress test passed; only note is the "alert" ears rendering oversized — a per-shot prompt fix ("ears perked but natural size"), not canon failure. The wordless-spine audio/timing path is built, patched, and verified end to end: 24 two-voice VO clips, 6 silent beats passing legally, assembled to a placeholder cut. Thirty photoreal stills rendered through the reference path. Handle `@BentleyandWatson`, display name **Bentley & Watson**, folder `bentley-and-watson/` (header keeps underscores; the resolver swaps). Still gated: Kling animation, music, and the demand half of the pilot (48h CTR/AVD once the flagship ships). Nothing farms Tier B until that clears. This doc is the plan of record, not a launch order.

Identity tags (final, size word dropped — the reference images carry the medium build; "miniature" was struck as a canon error):
- **Bentley:** chocolate-and-tan long-haired dachshund, liver-brown nose, warm amber eyes, tan eyebrow pips and muzzle, silky feathered chocolate ears and tail; the confident schemer.
- **Watson:** English-cream long-haired dachshund, glossy black nose, dark soulful eyes, honey coat shading darker along ears and spine, heavy silky feathering and plumed tail; the gentle sleepy softie.

---

## 1. One-line thesis

Two real long-haired mini dachshunds — Bentley (chocolate) and Watson (cream) — living an AI-reconstructed daily life on the Dutch coast. Reconstruction is the honest hook, not a hidden trick: real dogs, real life, rebuilt and heightened so they never age, never break the camera, and can stand anywhere. The moat is the same as every other channel in the operation — the production system plus a character canon that a config can reproduce a thousand times without drift. This is not a spike-chase. It is best-execution in an evergreen, demonstrably-served lane, with a specific structural wedge nobody has built.

## 2. Where it sits in the flywheel

This channel is not a detour from the roadmap; it is a stress-test of three things already on the priority list, which is the main reason it earns a slot at all. Wordless visual storytelling is pure per-beat motion, so it exercises the motion-direction control that is priority one. Wordless means the score carries the emotional arc alone, which forces the music decision that is priority two rather than letting it stay deferred. And the parent-episode-plus-harvested-shorts shape is a batched multi-video job, so it is the natural proving ground for the batch exit-gate in the upload step that is priority three. It also reuses two things already banked: the Gettysburg launch proved the parent-video-plus-spread mechanic end to end (main film, shorts cut from its own footage), and Q-Qrew proved character consistency holds through the NanoBanana-2 `/edit` reference path at 13-for-13 where the text path failed. Bentley & Watson is those two proven legs pointed at a two-character cast we happen to own thousands of real reference frames of. Build risk is low precisely because we are re-aiming machinery that already survived a launch, not inventing new machinery.

## 3. The demand read and the three-lane fork

Demand is a clear yes, but "two dachshunds, daily life" forks into three lanes with very different competition, and the fork is the actual finding.

Lane 1 is the real/staged pet daily-life vlog — the concept done with real footage. Massively validated, massively occupied. Gunner and Greta is literally this concept in real footage (two mini dachshunds, farm life, walks, baths): ~875K subs, 663M lifetime views across ~2,497 videos. The staged-eating variant is bigger still — Kiki and Bonbon, a golden-and-lab pair doing "the daily life of a silly dog" feeding vlogs, sits at ~2.87M subs and roughly **3 billion** lifetime views, ~3.7M average per video, ~817 videos at ~7 uploads a week. The format is proven to the moon and the incumbents are entrenched. A cold AI channel walking straight in fights whales with none of the weapon that makes the fight winnable.

Lane 2 is the AI faceless dog explainer/psychology lane — "what your dog is really thinking." Red-hot cold-start territory right now (Dogunee ~39K subs in two months with videos at 2.4M/2.2M; Mindful Paws one video at 2.7M, outlier ~21). Enormous demand, low barrier — but it is not the daily-life narrative we want, and it is getting crowded fast. Not our primary.

Lane 3 is the AI-reconstructed pet daily-life *narrative* with recurring characters. This matches the actual idea and is barely populated. Koko's Growing Diary proves the shape works for cats: 100% AI-generated, recurring character, "growing diary" daily-life episodes, videos at 1.4M / 602K / 212K, created March 2025. The dog side of this fusion is empty — no AI dachshund daily-life narrative channel surfaced in any search. That is the white space.

**The build order that falls out: start in Lane 3 to build the emotional moat and the subscriber base, then fight into Lane 1's volume as we grow, carrying an audience that is already attached.** More on why that fusion is the whole game in Section 6.

## 4. The structural finding that governs everything: wordless

Pulled the actual transcripts of both proof channels. Koko's 1.4M-view narrative episode ("Gets Robbed," 8+ minutes, full story) transcribes to nothing but `[Music]`, `Yeah`, `Ow`, `Wow`, `Yes` — eight minutes of story told with zero dialogue, carried entirely by visuals, music, and tiny character grunts. Kiki and Bonbon's feeding video returns "Not Available" — no captions at all, fully wordless.

So the narrative whale and the volume whale both win with no language. This is not aesthetic, it is distribution. Wordless means no dubbing, no localization, no language-gated recommendation — the same file is served identically to Jakarta, São Paulo, and Osaka. That borderlessness is a large part of how a channel gets from 100M to 3B: it addresses the whole planet, not the English slice. The moment narration becomes load-bearing, the addressable audience quietly collapses back to the English-comprehending fraction and the 3B ceiling collapses with it.

Consequence for us: the Inworld TTS layer is largely benched on this channel. Picture and score are the spine. Voice, where it appears, is a non-load-bearing top layer (Section 7). This is the inverse of Final Hours, where Victor is the spine and everything hangs off him — and the build-order instinct from the voice-led channels will try to make narration primary here. On this channel that instinct is exactly backwards. Write it down because it will bite otherwise.

## 5. Character canon

The canon is the moat. Lock it the way Q-Qrew crew canon was locked: a short (~20-word) identity tag per character plus a reference sheet built from the real photos, fed through the NB2 `/edit` reference path, verified at artifact on every batch. Canon on a character channel is a short identity tag, not a portrait (inverse of Final Hours place-canon).

The two permanent distinguishing locks are **coat** and **nose**, and both are describable as positive features — which matters because of the Flux-pro diffusion-negation failure (naming a word to exclude can summon it). Build with these anchors positively in every prompt; never prompt "not black nose."

**Bentley — the schemer.**
Identity tag (draft): *"Bentley: chocolate-and-tan long-haired mini dachshund, liver-brown nose, amber eyes, tan eyebrow pips and muzzle, silky feathered ears and tail; the confident schemer."*
Coat chocolate/liver with tan points. **Liver-brown nose. Amber/lighter eyes.** In the reference photos he is the chaos engine: fisheye-close nose on the lens, the slightly wall-eyed intense stare, mid-motion blur, the demented upside-down teeth-grin. This dog has plans. His identity lives in his face and his intent, so his reference sheet is an **expression sheet** — the stares, the grin, the forward drive. That is what his consistency hinges on; tell the pipeline that explicitly.

**Watson — the gentleman.**
Identity tag (draft): *"Watson: English-cream long-haired mini dachshund, black nose, dark soulful eyes, honey coat shading darker along ears and spine, heavy silky feathering and plumed tail; the gentle sleepy softie."*
**Black nose. Dark eyes.** Golden/cream coat, darker shading down the ears and spine — those two anchors are what keep him *Watson* rather than any generic golden fluff, which is the real diffusion risk on a cream long-haired dog. In the photos he is surrender: curled into a comma, nose tucked, the worried-sweet head-tilt, melting into the grey bed. His identity lives in body language and repose, so his reference sheet is a **posture sheet** — curled, tucked, the sleepy tilt.

The asymmetry is deliberate and it is a production instruction, not a flourish: Bentley's consistency is expression-driven and therefore the harder problem; Watson's is posture-driven and therefore the safer lock despite being the harder coat. That is why the pilot gates on Bentley's face, not Watson's shape (Section 12).

**Canon-purity flag.** The credit-card-in-mouth image circulating in the reference pile is **not one of our dogs** — it is the well-known dachshund-with-a-Mastercard meme (the card reads "oxrocard"), and it is a *smooth*-coated dachshund where both our boys are long-haired. Including it injects a wrong coat-length signal and poisons the canon set. Cut it. This is the verify-at-artifact / two-signals discipline applied at the reference layer: a wrong reference is worse than a missing one.

**Setting as canon.** The world is The Hague and it is a free moat no US pet whale has: the Kijkduin dune promenade (the "Pray for Windy Days" kiteboard-school sign, the tiled seafront, the dune scrub), the parkland, and a warm domestic world of parquet floors, a white shaker kitchen with glass knobs, a grey sofa and a grey dog bed. Every incumbent is filmed in a beige American living room. "Two long dogs on the Dutch coast" is texture we own for nothing.

## 5A. Visual register

Derived clean — no Final Hours dread anywhere near it. The rulebook every board, thumbnail, banner, and avatar obeys. Built to match what the dogs and their real world actually look like, at the same photoreal fidelity as the locked canon refs.

**The one-line look:** warm, bright, cozy-cinematic realism — lit like a sunlit afternoon, framed with gentle intention. A Dutch children's-book warmth rendered at photographic quality. North star is *inviting*, never moody.

**Palette.** Built from the dogs and their real world, not imposed on them. Warm neutrals as the base — cream, honey, parquet-wood browns, soft whites. The two dogs are the color anchors: Bentley's chocolate/liver and Watson's honey-cream are the recurring warm tones, so backgrounds stay lighter and cooler than the dogs so they always pop forward. Cool accents from the Dutch coast — dune green, overcast sky-grey, sea-grey — used as contrast against the warm dogs, never dominating. Hard rule: no dark, desaturated, or painterly grading. If a frame reads as "dim" or "muted," it is off-register.

**Light.** Bright and high-key by default, exactly like the canon sheets — soft window light indoors, golden-hour warmth outdoors, overcast-soft on the beach. Shadows stay open and gentle, never crushed. Backlight and rim-light are the signature move for hero shots (Bentley's backlit-troublemaker frame from the real photos is the template) — it reads as *intent* and separates the dog from the background. Emotional exception, used sparingly: the vet/IVDD episode can go softer and cooler for its worried beats, but never dark — it goes *tender*, not dread.

**Framing grammar.** Two heights, deliberately. Low, near-ground eye-level for the dogs' world — the default; it puts the viewer down in dachshund-perspective and is inherently sympathetic and funny (the world towering over two small long dogs). And the extreme close-up for character beats — nose-near-lens for Bentley's schemes, the soft head-tilt for Watson. Wide establishing shots reserved for the Dutch-coast location beats where the setting is the point. The long-low dachshund silhouette is a compositional asset: play the horizontal body against horizontal lines (promenade, skirting board, kitchen counter) so the shape reads.

**The world (setting canon).** The Hague, consistently — the free moat. Kijkduin dune promenade and tiled seafront, the parkland, and the warm domestic interior: parquet floors, white shaker kitchen with glass knobs, grey sofa, grey dog bed, the blue-sprig duvet. Keep locations recurring and recognizable across episodes so the world itself becomes a character. Cozy-Dutch-domestic is home base; the coast is the adventure.

**Thumbnail signature (the CTR asset).** Where register does the most work, so the most rule-bound. The permanent asset is the **chocolate-vs-cream two-dog contrast** — reads at 120px, instantly says "the two dogs," so at least one dog's face is large in almost every thumbnail. Bright high-key background; subject right-massed with clean left negative space for headline text. Curiosity-gap always — the thumbnail poses the question the video answers, never captions the plot (Bentley's guilty face + "he thought no one saw," not "Bentley steals a treat"). One clear focal face, big, with a legible emotion — the emotion *is* the hook. Text lowercase, minimal, high-contrast, a few words at most.

**Banned (the anti-register, to stop build-order drift):** no dark/Victorian/painterly grading; no dread, menace, or melancholy as a default tone; no muddy desaturation; no cluttered backgrounds that fight the dogs; no matched thumbnail/title pairs that kill the curiosity gap; no cool-dominant frames where the warm dogs get lost. Anything trending this way is off-register and gets re-rolled.

## 6. Tier architecture — the fusion that is the whole wedge

Koko has story but no volume engine (low cadence, slow to farm views). Kiki and Bonbon has a 3-billion-view volume engine but no story — you feel nothing, you watch dogs eat. **Bentley & Watson = Koko's emotional investment feeding Kiki and Bonbon's volume machine.** People fall for the characters in the narrative episodes, then devour the endless short daily-life loops *because they already love these two specific dogs*. That attachment is how you take Lane 1 from the whales: you do not out-volume a faceless eating-loop, you enter its lane already carrying an audience that is attached. Nobody has fused the two — that fusion is the reason this channel is worth building rather than being clone number two hundred.

It maps onto the exit-gate architecture with zero new concepts, which is the tell that it is right:

**Tier A — narrative flagship (Lane 3).** ~5–8 min, wordless (Koko-length), cinematic Mode A. Builds the emotional moat, the subs, the AVD. Low cadence, high craft. Batched multi-video job — parent plus its harvested shorts — that **exits at `final_video.mp4` for manual cutting**, because eyes are wanted on both the flagship and the loops carved from it before anything ships. This is where the cinematic pipeline out-executes the field.

**Tier B — daily-life/food engine (Lane 1).** 20–60s, wordless, Kiki-cadence. The 3-billion-view volume machine, riding on characters people already love. Once in steady state and re-cutting from banked inventory, this is the **single-video auto-upload path with per-project metadata.** This is the whale fight.

Same two dogs, same canon, one pipeline, two gates — which is exactly the single-vs-batch exit-gate split being built in priority three. The channel is the proof case for that upload step.

## 7. Narration design — both voices, layered not fused

Two inner-monologue voices, one per dog. This is not decoration; it is the comedic engine. One shared narrator collapses into a monologue *describing* two dogs; two distinct voices make it a *relationship* — two minds that do not understand each other, and the misunderstanding is the joke. Bentley narrates the heist as a criminal mastermind ("the humans think the counter is safe; the humans are fools"); Watson's rare, slow, deadpan line reveals he has no idea a heist is happening.

The discipline that keeps this from breaking the 3B ceiling: **voice must never be load-bearing.** The story is boarded to be fully legible on mute — carried by staging, motion, and score, exactly as Koko does it. The narration rides on top as flavour a viewer who understands it enjoys, but whose absence costs a non-English viewer nothing. Same episode, two experiences, one file, no lost plot for the global cut. This is *stronger* with two voices, not weaker, because two English inner-monologues is even more English-gated than one — so both voices live almost entirely in Tier A, composited over an already-complete picture-plus-score mix. Tier B stays wordless.

Casting is asymmetric by design: Bentley is the workhorse voice carrying most of the monologue; Watson is the rare voice, used sparingly so it lands. Pick two Inworld voices with real timbral separation — Bentley brighter and faster, Watson lower and slower — so they separate even on a phone speaker in a crowded feed, which is where most of these views happen. Same principle as the chocolate-vs-cream thumbnail reading at 120px: the contrast must survive compression.

**Write order matters and it is inverted from the voice-led channels.** Board the episode funny on mute first, then drop Bentley's commentary and Watson's one line on top. Writing two-dog dialogue first produces episodes that *require* the voice, which re-breaks the borderless cut.

**Testability.** Ship a Tier A episode with and without the inner-monologue track and let 48-hour CTR/AVD say whether voice adds retention or just adds work. Because the muted cut is already complete, that is a clean A/B, not a rebuild. Two independent signals before it becomes doctrine.

## 8. Cadence, sequencing, and harvest

Not a 50/50 schedule — a lead-and-follow. Tier A creates the asset; Tier B amortizes it. Every flagship is a parent that spawns a litter of Tier B shorts cut from its own already-rendered, already-canon-locked footage — near-zero marginal cost because the expensive part (the two dogs rendered consistently in a scene) is already paid for. The real ratio is not a decision, it is a yield: one parent, then squeeze it for every borderless short it contains before the next parent. Tier A sets the heartbeat (a flagship every week or two); Tier B fills the gaps daily from inventory to hold presence and feed the short-form surface that actually farms the volume.

**Launch order is the one place the instinct is backwards. Do not open on Tier B.** A cold channel posting wordless eating loops with no established characters is just another faceless Kiki clone with no reason to attach — entering the whale lane with none of the weapon. The first three or four uploads are Tier A: introduce the boys, establish the odd-couple dynamic, let people fall for the schemer and the softie. Only then do the Tier B loops mean anything, because now they are "oh, it's *Bentley* again" instead of "generic brown dog eats." Attachment first, volume second.

Governed, as everything is, by CTR and 48-hour AVD read separately per tier because they answer different questions. Tier A AVD is the attachment signal (are the characters and the wordless grammar landing). Tier B CTR is the volume signal (are the loops travelling on the recommendation surface). Strong A, weak B = a beloved small channel, not a whale — fix is in the shorts' packaging. Strong B, weak A = shallow views with no loyalty base, will plateau. Both green before pouring render budget into cadence, and no ratio moves to doctrine until two independent parents show the same pattern.

## 9. The channel as an evidence machine (why the elements compound)

There is no SEO layer here in the Google sense. YouTube is a recommendation engine; search is ~10–15% of discovery on an entertainment channel. The real job is giving the system unambiguous, repeated evidence that these two dogs reliably satisfy a specific viewer. Every element is either evidence-generation or evidence-amplification, and they only compound in that order.

The atom is the single video's satisfaction loop: thumbnail/title make the click (CTR), the first seconds honour or betray the promise, the body sustains watch percentage, the ending seeds the next view. This is the only thing the algorithm can measure, so it is the only thing that generates evidence. CTR + 48-hour AVD *are* the system because they are the two numbers that say whether promise-and-payoff held. The "funny on mute" rule is therefore CTR-promise integrity, not an aesthetic — a thumbnail that promises comedy and opens on a slow pan betrays the click and teaches the machine to stop serving us.

Packaging is the evidence-*quality* multiplier and it is where the curiosity-gap principle lives: a matched thumbnail/title pair is a caption already consumed with no reason to click; the gap forces the question only the video answers ("he thought no one saw" over Bentley's guilty face). Higher CTR compounds because it earns more impressions, which earn more CTR data, which earn more reach.

Retention architecture is the evidence-*strength* multiplier and it is where the two tiers pay off: the algorithm weights views by satisfaction. Tier A is retention-depth (parasocial attachment → watch-to-end → return), the strongest signal there is. Tier B is retention-breadth (short, borderless, high completion, farmed across the planet). A channel producing both is legible in a way a mono-format channel is not.

The surfaces are amplifiers, not generators, and the ordering is load-bearing: Shorts, community posts, comments do not fix a leaky atom, they multiply a sound one — deploy them before the atom holds and you amplify a "this does not satisfy" verdict, which actively suppresses you. Shorts are their own discovery ocean and the top of the funnel; they must seed curiosity about the characters and world, not just deliver a gag, or they build a Shorts audience that never touches the flagships — which is exactly why harvested-from-Tier-A shorts solve it natively (they are literally clips of the thing you want them to go watch). Community posts are the retention-between-uploads surface and, more importantly, they rehearse the parasocial ritual so the actual video arrives to a pre-warmed audience and the early-engagement signal spikes harder in the 48-hour window ("which one did it?" polls, "Bentley or Watson," guilty-face caption-this). Comments and replies manufacture early velocity — a pinned question plus replying to the first wave lifts comment count and session time in exactly the weighted window, and repliers become returners become the loyal core whose watch-behaviour is the highest-quality evidence you own. Cheap, and most faceless operators skip it, which is why it is edge.

The connective tissue that makes all of this compound rather than merely coexist is one consistent world, two consistent characters, one recognizable packaging signature. When a Short, a thumbnail, a community poll, and a flagship all resolve to the same two dogs, recognition raises CTR → CTR raises reach → reach raises subs → subs raise early-velocity → early-velocity raises distribution, and the loop tightens. A channel where the Shorts feel like a different show breaks the loop and nothing compounds. Consistency here is algorithmic legibility, not branding. Subscribers are the compounding reservoir — a standing pool of high-probability satisfied viewers to serve the next upload to for a fast early read; playlists ("Bentley & Watson: The Complete Chaos") feed session-continuation, which is disproportionately weighted.

Solo-operator discipline: do not treat "all elements firing" as a parallel to-do list. The chain has an order. Get the atom and packaging generating clean positive evidence on three or four Tier A flagships first; only then switch on amplifiers, in funnel order — Shorts to widen the mouth, comments to manufacture velocity, community to warm the reservoir. Lighting them all up on an unproven atom is the single most common way faceless channels teach the algorithm to bury them.

## 10. Leo-criteria validation (honest scorecard)

Leo's criteria are a filter for picking a niche to *copy*; Bentley & Watson is an original-IP play, so they do not map cleanly and where they break, that is information.

- **Monetized / higher RPM (US & Western, English core):** weakest point. Pets/animation is a ~$1.4–2.0 base RPM floor — the whole lane prints pennies per view (the AI dog podcast does ~234K monthly views for ~$360). The Tier A English inner-monologue pulls the flagship's watch audience toward the higher-RPM EN slice while Tier B stays global, but be clear-eyed: this channel's monetization thesis is volume × later merch/brand, not AdSense RPM. **Pass, with the RPM caveat written in blood.** This is the tax paid for a 3B ceiling.
- **Below 100K subs / averaging 20K+ / gone viral in past 6 months:** the adjacent evidence is hot. TaleCraft AI — one flagship at 1.3M off a 5.7K-sub channel. Project: Creature — outlier ~6.4, "raised a Cerberus puppy," 5K subs, videos at 150–490K. Impossible Tales — outlier ~34, 28K subs, ~395K avg on seven uploads. Sub-100K AI-character/narrative channels are throwing off massive per-video outliers right now, months old. **Strong pass.**
- **Simple to reproduce:** pass, and it is *our specific edge*. For the field, "reproduce" means re-prompting from scratch and praying consistency holds — most do one-off "X in real life" transformations precisely *because* recurring-character consistency is hard. We solved it (NB2 `/edit` reference path, pointed at dogs we own thousands of frames of). Our reproduction cost is a config and a canon sheet; theirs is manual prompt-wrangling every video. We meet this from a structurally lower cost base than the field. **Pass, strong.**
- **Aligns with personal goals:** pass. Evergreen (daily pet life never stales), best-execution in a served lane, and it pays rent on the roadmap (motion-direction, music, batch exit-gate) before it pays AdSense.
- **The one it fails — "gone viral in the past 6 months" for the *exact* concept:** we do not have it. The data validates the *ingredients* (Koko: AI pet narrative works; Kiki: two-pet daily-life works; Impossible Tales: AI animal comedy works) but there is **zero signal for the specific combination** of two consistent real-pet characters + wordless narrative daily-life + harvested shorts. Last session that white space read as pure upside; Leo's filter correctly reframes it as risk — a cold channel betting that demonstrated-adjacent demand transfers to an unproven exact-format. Own doctrine says two independent signals before doctrine moves; we have strong signals for the parts and none for the whole.

**Verdict: five of seven pass, one passes with a heavy RPM caveat, one fails on the exact combination and converts to execution risk retired only by shipping. Legitimate go — but a go *conditioned on the pilot*, not an open build order.**

## 11. Spend doctrine

Pipeline cost is Kling count, not beat count — Ken Burns is free, Kling spend is only for beats needing true motion. Under $20 is the ceiling for heavy-Kling jobs. For this channel:

- **Launch episode (the pilot flagship): full beat animation.** One-time investment to put the best possible first impression on the atom and to stress the canon-lock across a full Kling beat range. This is the one episode that justifies the spend, exactly as built for prior launches.
- **After launch: Ken-Burns default with selected / front-loaded Kling** on the beats that carry motion narrative, scaling animation spend up only when reach justifies it. Same pattern already in the pipeline. Do not frame higher-beat scripts as a fal-spend concern — beat count is free; only Kling count costs.
- **Tier B** rides almost entirely on banked footage re-cut from Tier A parents, so its marginal render spend trends toward zero — which is the whole reason the volume machine is economically viable at pets-tier RPM.

Every render gated at the stills-review seam; zero-spend probes (`--storyboard-only`, `--plan`) before any real spend; per-beat narrative-function judgment at the review page rather than a global rule.

## 12. Pipeline integration — what shipped

**Voice map (LOCKED, live).** Character-keyed under `elevenlabs_voices` in `channel.json`. Provider is **ElevenLabs**, a divergence from the Inworld stack every other channel uses.
- **Bentley** (workhorse): `3XOBzXhnDY98yeWQ3GdM`, speed 1.0, stability 0.5, style 0.5.
- **Watson** (rare deadpan): `douDhHvfoViWmZth0cUX`, speed 0.90, stability 0.5, style 0.5.
- The 1.0-vs-0.90 speed gap is intentional: Watson slower is what makes his single line land as the puncture.
- The speaker rides as a tag on the narration line — `[A] [bentley] The humans are fools.` — which `parse_script.py` folds into `beat["narration"]` untouched. A bare `[A]` with only a VISUAL is a legal silent beat.

**The wordless-spine path (NEW, shipped, proven).** `timing_source: "beatsheet"` in `channel.json` selects it. Two new reusable black boxes plus one config-gated branch; nothing else in the pipeline changed.
- `generate_twovoice_vo.py` — renders each tagged line in its character's voice via the *public* `generate_voiceover_elevenlabs`, inheriting chunking, retry, and ffprobe verification for free. Silent beats pass with no warning. Emits `vo_map.json`.
- `build_wordless_audio.py` — writes `durations.json` (`source: "beatsheet"`, always positive) and lays the VO clips onto one full-length `voiceover.mp3` at their beat timecodes.
- `wordless_leg.py` — the audio leg's sibling. Two steps instead of four, and it skips Whisper entirely, so a dog render reaches the stills gate several minutes faster than any other channel.
- `decide_legs()` in `orchestrate.py` gains a config branch: `"narration"` (default, every existing channel, untouched) or `"beatsheet"`.
- **Convergence:** the fork opens at `decide_legs` and closes at two ordinary artifacts — `durations.json` and `voiceover.mp3`. `assemble_episode.py`, the music bed, upload, thumbnails and harvest are all unaware anything unusual happened.

**Reference render mode (LOCKED, live).** `render_mode: "reference"` plus a `reference_map` and a `canon` block. A `{token}` in a VISUAL does double duty: it attaches the character's reference image *and* expands into the prompt text, so identity is defined in exactly one place and cannot drift across thirty hand-typed lines.
- `patch_modea_beats_canon.py` + `patch_modea_leg_canon.py` carry the canon block through the MC route to the engine. Channel-agnostic; any reference-mode channel gets it.
- Token-free beats fall through to text-to-image **and have the people-directive stripped** (Rule 1: person-free by definition). Watch beat 15 — the human feet entering — which may render an empty doorway. If so the fix is to give it a dog, not to fight the rule.

**Folder convention.** The header keeps underscores (`bentley_and_watson`); the folder on disk uses hyphens (`bentley-and-watson/`). `load_resolved_config` swaps `_`↔`-` and finds it, exactly as `final_hours` → `final-hours/`. It does *not* strip separators — the original `bentleywatson/` never resolved. The docstring's alias mechanism (`synthetic_press → synthetic/`) is aspirational; no alias map exists in code.

**Still open.**
- **Kling animation + music.** The launch episode earns full-beat Kling per §11; the caper is Kling-heavy by nature (22 of 30 beats motion-essential), so it sits at the top of the spend band. Music is deferred — but a wordless film with no score is a *motion and canon proof*, not a shippable cut. Judge it accordingly.
- **Pacing.** A flat 6s hold is the deliberate v1 baseline: it produces a complete cut fast, and its metronomic feel is a *diagnostic*. The slapstick collapse (21) and Watson's stretch (26) will be the first two beats to demand different lengths.
- **Upload / batch exit-gate (priority 3).** Tier A = batched job exiting at `final_video.mp4`; Tier B steady-state = single-video auto-upload. Until built, uploads are manual (category = Entertainment, add tags).
- **Harvest step.** How a Tier A run tags and exports its Tier B candidate segments at the stills-review seam.

## 12A. Engine lessons banked (channel-agnostic — graduate these up)

**One reference per token.** Multi-reference `/edit` silently degrades photoreal to illustration. Same prompt, same lock, same tail, same endpoint, same photoreal reference sheet — two refs (face + body) produced a glossy cartoon with a *perfect* liver nose; one ref produced a clean photograph. Identity survives; fidelity does not. `reference_map` values must be plain strings. The code accepts a list (`recreation_pipeline` ~1540) but the model does not reward it. qqrew has always used single strings and has always been photoreal. This is the most maddening possible failure mode, because correct identity makes it look like a prompt problem when it isn't.

**Refs control identity; the lock/tail text controls fidelity.** The module default `REFERENCE_PROMPT_LOCK` literally reads *"Render in a semi-realistic modern animated-feature illustration style."* Any reference-mode channel that omits `reference_prompt_lock` / `reference_prompt_tail` silently inherits a cartoon. `make_character_ref.py`'s docstring claims `/edit` clones the reference's fidelity — it does, but only with a single ref, and only when the prompt doesn't say otherwise.

**Negation is safe on NB2, not on Flux.** "Not an illustration, not a cartoon" is fine on the reasoning-guided `/edit` endpoint (qqrew's working lock uses "never bored, never pouty"). The Flux-negation trap — naming a thing summons it — applies to the diffusion text path.

**"One continuous full-episode narration" is an unstated invariant in at least four places.** Each was correct for the voice-led channels it was written for; each had to defer to a channel that declares otherwise. None was rewritten.
1. `build_audio_script.py` — the no-codified-silence doctrine. **Bypassed** (the wordless leg never calls it).
2. `elevenlabs_tts.py` — a 1.0s floor in `_concat_chunks`, which hard-fails on a legitimate one-word line. **Parameterized** (`min_total_duration`, defaulting to 1.0).
3. `assemble_episode.py` — drops beats with `source == "no_narration"` or `duration <= 0`. **Satisfied** (we emit `source: "beatsheet"` and positive durations; the assembler never knows).
4. `mission_control/ingest.py` — `verify_beats()` refuses wordless beats. **Gated** (`timing_source` consulted; still a hard error everywhere else, and a missing VISUAL stays a hard error for all).

There is almost certainly a fifth. **Wordless is a first-class channel mode, gated on `timing_source`, and every no-silence invariant defers to it.** The next person to find one should recognise the pattern rather than rediscover it.

**A signature is not a scope.** The `min_total_duration` patch changed the public function's signature and the guard — but the guard lived in a *different* function, `_concat_chunks`, called from the last line. `py_compile` passed; every render died with `NameError`. Read the whole call chain before patching. Compile is not proof.

**Script-is-king survives the fork.** The script remains the sole source of truth *and* of timing. Only *where in the script* the timing lives has changed: voice-led channels measure it from narration via Whisper; a wordless channel declares it per beat. `durations.json` is still the single timing-and-structure source.

## 13. Validation — the pilot as a two-gate test

The Great Sausage Heist is not "episode one," it is the validation gate for the one Leo criterion the data cannot satisfy. It has two gates and both must clear before any Tier B farming begins.

- **Technical gate — Bentley face-consistency across the heist beat range.** The hard problem is expression-driven consistency: Bentley must be recognizably the same scheming face across ~30 shots in an ~8-minute wordless episode. Prove Bentley holds through a full Kling beat range and the channel's technical risk is essentially retired. Watson (posture-locked) is the safer half; do not let him mask a Bentley failure at review.
- **Demand gate — 48-hour CTR/AVD on the flagship** as the first real signal that the exact combination transfers. Set explicit thresholds before launch; two independent parents showing the same pattern before anything becomes doctrine.

Two greens flips the white space back from risk to moat. One red and we have spent exactly one pilot's worth of Kling to learn it cheaply — which is the entire point of probing before spend.

## 14. Sample slate

Tier A (narrative, wordless, music-carried, ~5–8 min):
- **The Great Sausage Heist** (pilot). Bentley plots the counter-top treats; Watson is the lookout who falls asleep on duty. Caper structure, home setting. Also the canon-lock and CTR/AVD gate.
- **Watson's First Snow.** Cream dog meets Dutch snow and freezes; Bentley shows him it's fine. Wholesome milestone, seasonal.
- **Something's Wrong With Bentley.** The vet-trip / IVDD-scare episode — real stakes every dachshund owner shares out of fear-recognition; Bentley's bravado cracks, Watson won't leave his side. Retention spike.
- **The Longest Walk in Holland.** A full Kijkduin dune-and-sea day. Location as character; the Dutch texture doing the differentiating.
- **Who Gets the Good Bed.** The eternal territorial war over the grey bed. Pure odd-couple engine, straight out of the reference photos.

Tier B (short, wordless, loopable, the volume machine):
- **Bentley vs. Breakfast** — he inhales it, Watson savours. Food-forward, the whale's exact lane.
- **He stole the bed. Again.** — repeatable gag.
- **Two Noses** — signature close-up bit built on the liver-vs-black distinction; makes the canon itself a running joke.
- **Watson found the sunbeam** — cozy nap ASMR.
- **Dinner on the Dutch coast** — food + place.

## 15. Naming

**Bentley & Watson.** Real names, real dogs — honest and ownable. English-gentleman names that play beautifully against dachshund comedy and read globally. Keep it.

---

### Next artifacts (in order)
1. Final identity-tag strings + the two reference-sheet specs (Bentley-expression, Watson-posture) — the first concrete build, so his face can be generated and reviewed across the heist beat range before any Kling spend.
2. `channel.json` for Bentley & Watson, including the character-keyed voice map and beat-speaker field.
3. Full beat-sheet for The Great Sausage Heist, boarded funny-on-mute first, VO layer second.
4. Harvest-step spec at the stills-review seam.

### Durable principles this channel is banking (graduate up when proven)
- Wordless is a distribution decision, not a style: load-bearing narration caps the global ceiling.
- Voice, where used, is a top layer over a mute-legible spine — inverse of voice-led channels; guard against build-order bias.
- Character consistency hinges on different features per character (Bentley expression, Watson posture); reference the thing that carries the character.
- A wrong reference poisons canon worse than a missing one — verify-at-artifact at the reference layer, not just the render layer.
- Amplifier surfaces multiply the atom's verdict; never switch them on over a leaky atom.
