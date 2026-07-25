# _Crew.md — Channel Doctrine (working name: crew-wip)
*The craft + config brief for the bright, fast-cut, character-driven crew explainer channel.
The anti-Final-Hours channel. Single-underscore = channel doctrine (load per channel); the
double-underscore canonical reference is the system. Where this doc and the Final-Hours-derived
craft in `ante-machinam.md` Part IV disagree, THIS DOC WINS for this channel — see §7 the break-list.*

*v0.1 — first version, written at design-complete / pre-render. Bump when a render banks a lesson.*

---

## 1. WHAT THIS CHANNEL IS

A recurring **crew** investigates **the unfilmable** — things no camera could ever capture, across
all of time and space: the deep past, the far future, unreachable places (the ocean floor, the inside
of a volcano, two hundred years from now). The crew is the constant; the topic is the infinite
variable. That breadth is deliberate anti-flood insurance: competitors clone a topic lane in a
weekend, but they can't clone a recurring cast with a register.

**The feeling:** bright, curious, wry, propulsive, playful-on-top with real substance underneath.
"Skibidi-energy" in the delivery, genuine content beneath. The exact opposite of the dread-and-dignity
register. A clever excited friend telling you something wild, not a museum docent.

**The audience:** young-adult coded. NOT Made-For-Kids (revenue death). NOT age-restricted (reach
death). The general-audience middle — edgy-but-not-graphic; the cartoon style lets us handle dark
topics safely.

---

## 2. THE CREW (see crew_character_bible.md for the full IP spec)

Core of THREE, never more (guests are per-episode, never core):
- **DRIVER** — the guy. Energy, launches the investigation, "let's go find out," delivers the wry
  cold-open beats. Backpack signature, glasses. THE PILOT IS DRIVER-ONLY.
- **BRAIN** — the sciency-stylish young woman (glasses = her tell). The knowledge engine, "actually,
  here's what's true."
- **SKEPTIC** — the blonde, composed, dry. The audience stand-in, "prove it" — her doubt forces the
  next piece of evidence.

**Narration architecture (the retention engine — protect this):** the default is ONE crew member
talking DIRECTLY TO THE VIEWER (second person: "right now, you..."). The other two are REACTION
cutaways, NOT a conversation. The moment the crew talk to each other, the viewer becomes a spectator
instead of the person being addressed — which kills the second-person retention spine. Full ensemble
is reserved for tentpoles. The pilot is pure solo-address (Driver to viewer).

---

## 3. STYLE (kid-validated, 4 independent signals)

**PRODUCED FLAT CEL-SHADED ILLUSTRATION.** Clean dark linework, simplified flat color planes,
appealing stylized faces, rich illustrated backgrounds, warm lighting. One tier above the flat-stick-
figure incumbents (Ink/Mack) — the production polish IS the differentiation — but firmly on the
illustrated side.

**EXPLICITLY NOT photorealistic, NOT 3D, NOT realistic-skin.** Photoreal drift is the failure mode:
it reads "Final Hours," it invites AI-realism artifacts (warped straps, stubble), and it's wrong for
the register. The style suffix must steer DECISIVELY flat-cel and negative the realism.

**Backgrounds are a first-class element** — half the appeal (kids confirmed twice). Rich, warm,
detailed, inviting. Never bare. The crew always stands somewhere worth visiting.

**channel.json style_suffix (current):**
> "clean flat 2D cel-shaded illustration, confident dark linework, simplified flat color planes,
> smooth animated-feature style, appealing stylized characters, rich illustrated background, warm
> lighting, vibrant color, NOT photorealistic, NOT 3d render, NOT realistic skin texture, bright and
> inviting, no text, no letters, 16:9"

---

## 4. THE SCRIPT (the moat — script is king)

**Fast-cut rhythm authored into the beat length.** 4-10 spoken words per beat, ~1-3 seconds each.
Many short beats, rapid cuts. The pace is in the WRITING, not in animation. This is the Ink/Mack cut
rate and it is the channel's signature.

**The locked format (from the winning Ink/Mack explainers):**
1. Cold open = second-person present-tense gut-punch (viewer implicated in line one: "Right now, you
   smell fine.").
2. The "you'd assume X — but no" pivot inside ~20s (opens the retention loop).
3. Chronological evidence-walk pinned to named researchers/places/dates (the credibility scaffold —
   Semmelweis, Babylon, twenty-eight hundred BC).
4. The inversion payload: "older/weirder/more recent than you think."
5. Ring-close back to "you, right now."
6. ONE thesis, bright-not-morbid, second-person held throughout, no sprawl.

**The idea-gate (score before authoring):** universal behaviour everyone shares + an invertible buried
assumption + a present-day reframe + bright-not-morbid. Spread topics across the scope (past / future /
unreachable) so the algorithm learns the channel goes anywhere.

**Voice:** Evan / inworld-tts-2 / speaking_rate 1.05. Chosen for the dry-humour SMIRK (the deadpan
"Probably" landing). Brisk baseline that can still LAND a punch beat. Record the exact settings; voice
consistency across the catalogue is part of the brand.

---

## 5. PRODUCTION CONFIG (the leanest lane in the portfolio)

- **Stills:** Flux-pro/v1.1, flat-cel style_suffix. `safety_tolerance:"5"`. The only real spend.
- **Animation:** NONE. Static holds per beat (`_still_to_held_clip`). No Kling, no Ken-Burns. (Pan/zoom
  is invisible/janky at a 1-3s cut rate — static cut fast is correct AND cheapest.)
- **Audio:** Inworld Evan @1.05.
- **Mode:** all Mode A. No Mode B (yet). No music (yet).
- **Character determinism:** the Driver lock lives in `base_canon` (auto-merges into every beat) +
  `people_directive` in the rulebook. Specificity kills drift.

**The upgrade ladder (turn these on as the channel earns it — capability already exists in the
pipeline, it's a config flip, not a rebuild):** static stills (now) → per-beat motion (flip
kling_count) → music (add the music block) → Mode B data-graphics (promote data-beats) → lip-sync →
"the Movie" (different name, same crew). The crew bible carries through every tier.

---

## 6. THE CHARACTER DETERMINISM PROBLEM (the channel's hardest thing — be honest about it)

This pipeline was BUILT FACELESS because Flux drifts on faces. This channel's whole premise is a
recurring VISIBLE character. That is the hardest thing this pipeline does, and it's why the probes
fought us. Mitigations: (a) over-specify the character in base_canon (specificity kills drift); (b)
accept the model's strong defaults rather than fight them (the Driver HAS glasses — flux won't remove
them, so we stopped fighting); (c) the durable fix at the animation/movie tier is image-to-image /
reference-conditioning, deferred for now. For fast-cut stills, glance-level consistency is the bar
(nobody freeze-frames to compare faces) and that's achievable.

---

## 7. WHAT THIS CHANNEL BREAKS FROM THE CANONICAL DOCS (the Final-Hours bias)

The canonical craft (`ante-machinam.md` Part IV) is really the Final-Hours/Sacred-Dawn brief — Final
Hours was built first and infected the "channel-agnostic" docs. This channel deliberately breaks:

1. **Beat granularity** (§6 says 15-35 words / 5-12s) → we go 4-10 words / 1-3s. FAST.
2. **Animatable foreground** (§7) → we don't animate; stills are composed pictures, not frames to move.
3. **Faceless default** (Part III) → we have a visible recurring character.
4. **Slow-dread register** (Part IV) → we're bright, wry, propulsive.
5. **Photoreal cinematic style** → flat-cel illustration.
6. **Ken-Burns floor** → pure static holds, one notch leaner.

KEEP (genuinely universal): header format, channel-matches-folder, numbers-spelled-out, one-VISUAL-
per-beat, script-is-king, no-legible-text-in-stills, parse-verify-before-spend, safety_tolerance 5,
base_canon auto-merge, positive-prompt-is-the-lever, recognition-is-the-retention-mechanic,
nothing-publishes-unreviewed.

(Full catalogue: NOTE_final_hours_bias_in_canonical.md.)

---

## 8. PACKAGING

- **Title formula:** the curiosity-gap + the number/time anchor. "200,000 Years Without Soap. How Did
  Humans Survive?" Lead with the gap that only the video answers.
- **Thumbnail:** the Driver's face + a strong single curious subject, flat-cel, bright, high-contrast,
  text in a corner over a darker scrim (reuse the proven thumbnail machinery; swap aesthetic words to
  bright/curious). Two-line punchy headline, NOT the full SEO title. Curiosity-gap rule: image and text
  must NOT echo each other — the gap forces the click.
- **Title (metadata) vs thumbnail headline are different strings** — full SEO title in the header,
  short punchy headline on the thumbnail.

---

## 9. NAMING (deferred)

The pilot will name itself. Working: crew-wip. Principle: NAME it, don't describe it (Mack is just
Mack). Avoid "Curious" (over-crowded). Must pass: kid-say-it-out-loud + handle available + no
collision. Survivors for the out-loud test: Last Seen, The Last Time, Quest, Trove, Kove, Vyse,
Fathom. The wide scope argues for an empty-vessel name (any meaningful name fights half the content).

---

## 10. STATUS

Design complete, not yet rendered. Next: lock the script → finalise channel patch + rulebook → render
the cold open as an in-pipeline test → full render → SHIP → read 48h data → crank or park.
