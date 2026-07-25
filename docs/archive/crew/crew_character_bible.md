# CREW CHARACTER BIBLE — v0.1
*The durable, tool-agnostic IP spec for the crew. THIS is the asset that survives every tooling
generation: renders get thrown away and regenerated (stills → animation → lip-sync → the movie), but
this definition carries through all of it. Built to over-specify, because specificity kills render-
drift and vagueness summons it. Defined as written characters + exact prompt tokens, not as a pile of
Flux outputs — so the crew can be reproduced in ANY future tool.*

*v0.1 — Driver locked for the pilot; Brain + Skeptic specced but not yet probe-validated. Tighten
each character's tokens as renders confirm what holds.*

---

## HOW TO USE THIS BIBLE

- The **base_canon** block in channel.json carries the active character lock(s) — it auto-merges into
  every beat's prompt, which is the channel-level drift-killer.
- Each character has: IDENTITY (the precise visual spec), SIGNATURE (the one unmistakable tell),
  ROLE (what they do in the show), PERSONALITY/VOICE (for writing + future lip-sync), and PROMPT
  TOKENS (the exact string that reproduces them).
- **Signature rule:** each crew member owns ONE unmistakable visual tell, no collisions, distinct at
  thumbnail-silhouette size. Driver = backpack. Brain = glasses. Skeptic = (TBD — needs a visual tell
  beyond "blonde + arms crossed").
- **Faceless-pipeline caveat:** this pipeline drifts on faces (built faceless for Final Hours). These
  are visible characters — the hardest thing the pipeline does. Glance-level consistency is the bar for
  fast-cut stills; tighten toward image-to-image reference-conditioning at the animation/movie tier.

---

## DRIVER — "the guy" (LOCKED FOR PILOT — the only character in early videos)

**ROLE:** Energy / launch engine. Drags the crew (and viewer) into the investigation. "Let's go find
out." Delivers the wry cold-open beats and the dry-humour landings. In the pilot, he carries the
ENTIRE narration as solo-address to the viewer.

**IDENTITY (precise):**
- Young adult man, early twenties.
- Warm light-tan skin.
- Short, tousled brown hair.
- HAS GLASSES (dark frames). *(Note: we stopped fighting the model on this — flux-pro summons glasses
  on this archetype relentlessly and ignores negation. Glasses are now HIS, accepted. The Brain's
  glasses become one tell among several when she arrives.)*
- Clean-featured, friendly, open face. Expressive, a touch wry.
- Slim build.

**WARDROBE:**
- Blue denim jacket over a grey crew-neck t-shirt.
- Dark jeans.
- Brown leather watch.
- Tan canvas backpack, worn evenly on both shoulders.

**SIGNATURE (his unmistakable tell):** the tan canvas backpack. (Plus glasses, though those will be
shared-ish with Brain — the backpack is his alone.)

**PERSONALITY / VOICE:** curious, energetic, irreverent, a touch wry. The one who says "bro they did
NOT—". Voiced by Evan (Inworld) @1.05 — brisk with a dry-humour smirk. He's the channel's voice: a
clever excited friend, not a narrator.

**PROMPT TOKENS (paste verbatim — this is the reproducible spec):**
> "a young adult man, early twenties, warm light-tan skin, short tousled brown hair, dark-framed
> glasses, friendly open face, slim build, wearing a blue denim jacket over a grey crew-neck t-shirt,
> dark jeans, a brown leather watch, and a tan canvas backpack worn evenly on both shoulders; curious
> and expressive, a touch wry"

**CONSISTENCY NOTES:** the most stable of the three in probes (tightly described). Holds at glance-
level across wildly different settings (kid-confirmed: "the same guy" across Aztec/Mughal/etc).
Backpack straps can warp in photoreal renders — flat-cel style mitigates this. Keep him clean-shaven
(stubble drifts in).

---

## BRAIN — the sciency-stylish woman (specced; future video; daughter-locked brief)

**ROLE:** Knowledge engine. "Actually, here's what's true." Carries the evidence, the facts, the
named-researcher beats. The one who knows things.

**IDENTITY (precise — from Peter's daughter's character-brief + the approved reference):**
- Young adult woman, early twenties.
- Dark hair worn in a messy bun.
- Glasses (her tell).
- Light-to-medium skin.
- Nerdy-but-stylish, focused, composed. "Slightly nerdy, sciency, bit stylish, focused" (the exact
  brief). A character a young woman would want to BE — the smart-and-cool one.

**SIGNATURE:** the glasses + the messy bun (the studious-stylish combination).

**PERSONALITY / VOICE:** focused, precise, a little dry, quietly confident. The one who actually has
the answer. A female Brain is deliberately against the explainer-default (which makes the smart voice
male) — a strong, identifiable character especially for young women. Voice: TBD (own Inworld voice
when she's introduced).

**PROMPT TOKENS (provisional — validate on first probe):**
> "a young adult woman, early twenties, dark hair in a messy bun, dark-framed glasses, light-medium
> skin, nerdy-stylish and focused, composed expression, wearing a denim jacket; smart and cool"

**CONSISTENCY NOTES:** was the DRIFTER in early probes (East-Asian ponytail → Black curly → locked
version) BECAUSE she was under-specified — the lesson that proved "specificity kills drift." The
locked reference (dark messy bun + glasses) is what stops the drift. Lock her tightly before her first
video. Distinct-from-Skeptic check required (two women must read as clearly different people).

---

## SKEPTIC — the blonde (specced; future video)

**ROLE:** Audience stand-in. "Prove it." Dry, unimpressed, doubts everything — and her doubt FORCES
the next piece of evidence (she's the retention engine made into a character: she asks the question
the viewer is thinking, which justifies the next beat).

**IDENTITY (precise):**
- Young adult woman, early twenties.
- Blonde.
- Composed, often arms-crossed, centre-frame.
- Dry, unimpressed default expression.

**SIGNATURE:** NEEDS ONE beyond "blonde + arms-crossed" — those are weak tells that won't read at
thumbnail-silhouette size and risk collision with Brain. OPEN ITEM: give her a distinct visual
signature (a specific jacket colour? a hat? a recurring prop?) before her first video.

**PERSONALITY / VOICE:** dry, sceptical, deadpan, the eye-roll. The one who says "okay but why
though?" Not mean — the smart doubter. Voice: TBD.

**PROMPT TOKENS (provisional — needs a signature added, validate on probe):**
> "a young adult woman, early twenties, blonde, composed with arms crossed, dry unimpressed
> expression, [DISTINCT SIGNATURE TBD]; the sceptic"

**CONSISTENCY NOTES:** must be visually DISTINCT from the Brain (the two-women-blur risk). Her
character-brief should come from Peter's daughter (de-biased rater for female characters), framed as
"the sarcastic one who doubts everything — does she read that way, and is she clearly her own person
next to the sciency one?"

---

## THE UPGRADE LADDER (why the bible matters)

This bible is the IP that rides every tier:
- **Stills (now):** these prompt tokens → Flux flat-cel renders.
- **Animation:** same tokens + same characters → Kling/animation (flip kling_count).
- **Lip-sync:** same characters get talking-to-camera (the solo-address format BENEFITS most from
  lip-sync) — likely needs image-to-image/reference-conditioning to hold faces still enough.
- **"The Movie":** same beloved cast, fully animated, long-form, different channel name.

The renders are disposable; THIS DOCUMENT is the asset. When the tools improve (Altman: "design for
continuous improvement in the models"), the crew survives the jump because they're defined here as
characters + reproducible tokens, not as a folder of PNGs.

---

## OPEN ITEMS

- DRIVER: locked for pilot. Validate consistency across the full 57-beat render (the real test).
- BRAIN: lock the precise tokens; validate distinct-from-Skeptic; assign a voice.
- SKEPTIC: GIVE HER A DISTINCT VISUAL SIGNATURE (the one real gap in the cast); daughter's character-
  brief; assign a voice.
- All three: a full-body reference (current refs are face/upper-body); the eventual image-to-image
  reference frames for the animation tier.
- In-show NAMES for the three (currently role-labels only — they need actual names the audience uses).
