# _QQrew.md — VISUAL GRAMMAR (drop-in section, banked 02 Jul 2026)
*Paste into `_QQrew.md` as a new top-level section (suggest §6b, after the two-still-classes §6). This is the hard authoring doctrine that PREVENTS the whole class of failures the Fire (ep5) probe surfaced. Every one of these is a rule the AUTHORING stage enforces — so the render comes back clean instead of being hand-fixed 25 stills at a time. This is the tool-agnostic principle-banking that is the actual moat: the pipeline didn't change; the way we WRITE for it did.*

---

## THE ROOT LESSON (why this section exists)
Across the 02 Jul Fire render, every single bad still was the same failure wearing different clothes: **the script asked text-to-image (`nano_banana_2 · text`) for a HUMAN it couldn't anchor.** NB2, handed "a lone early-human figure" / "a silhouette" / "one figure gesturing" with no reference image, has one overwhelming prior — *modern smiling cartoon character* — and renders that, relegating the actual scene to a background or a thought-bubble (beat 43 literally put the prehistoric scene in a daydream bubble beside a hoodie kid with a phone). The teaching-graphics failed the same way earlier ("infographic → cartoon presenter"). **The model was never broken. The prompt asked for the one thing this channel's text path cannot do.**

The fixes below are all AUTHORING rules. Bank them; enforce them before every render. Fire is the last QQrew script that will ever have this problem.

---

## RULE 1 — THE ANONYMOUS-HUMAN GATE (hard, absolute)
**On QQrew, a human in frame is EITHER a crew member (Brain/Driver/Skeptic, via the `/edit` reference path) OR the human does not exist. There is no third option. There are no anonymous people.**

- BANNED in any crew-absent (text-path) VISUAL: "figure", "silhouette", "someone", "a person", "early-human", "huddle of figures", "a lone X", "people" (as depicted subjects), "crowd of figures".
- If the story needs a *specific* person → it is a crew member, in the scene, spec'd with their `{token}` so it routes `/edit`.
- If the story needs no specific person → the beat is PERSON-FREE. The fire, the torch on the ground, the fleeing animals, the empty cold plain, the frost, the dropped tool. **Narration carries the humans; the frame does not show them.** (Person-free landscapes rendered flawlessly all through the Fire batch — that is the strong text-path lane.)
- Crowds/reactions that genuinely need many faces (a cheering stadium) are the ONE tolerated exception and only when the many-faces prior HELPS (it renders a crowd fine) — never for "distant early-humans", which reads modern every time.

**Pre-render check:** grep every crew-absent VISUAL for the banned words above. Any hit = rewrite before spending.

---

## RULE 2 — TEACHING IS DIEGETIC BY DEFAULT (the big upgrade, banked 02 Jul)
The flat abstract teaching-graphics (vector clocks, neon gut, stick-figure chains, glowing-surplus power stations) RENDER fine but they **jar** — they are from a different universe than a crew member standing in a real place, and every cut to floating vector-art is an immersion needle-scratch. They fight the show.

**Default teaching mode = DIEGETIC: the explainer happens INSIDE the scene, using the crew member's body and props.** This is homogeneous with the environment AND deepens character (it makes the crew's epistemology physical).

The diegetic toolkit:
- **Fingers / hands:** "Brain holds up four fingers for four things." Counting, comparing, showing scale with her hands.
- **Ground-writing:** numbers or a simple diagram scratched in sand, dirt, ash, snow. (Loose/rough is authentic, not a defect — dodges NB2 text-garble by design.)
- **Found objects:** twigs arranged to count, stones laid out for a proportion, a line drawn with a stick.
- **★ THE FIELD NOTEBOOK (Brain's signature teaching mechanic):** Brain carries a field notebook. When she has a finding, she **jots it and holds the notebook to camera** — a hand-drawn sketch, a rough timeline, a tally, an arrow. Repeatable signature beat. Reasons it's the right call:
  1. It's her discovery-epistemology made visual (a discovery-learner records findings) — same character-logic as contact beats.
  2. Hand-drawn field-notes are SUPPOSED to be loose, so garbled/approximate numerals read as authentic, not as a render bug. The failure mode becomes the aesthetic.
  3. Period-neutral and timeless — works in any era, unlike a phone (a phone drags a modern object into a prehistoric scene AND re-triggers the modern-person prior; NOTEBOOK over phone, always, for deep-time topics).
  4. It's a brand tell — "the crew member who sketches it in her notebook" is recognisable IP.

**Abstract data-graphics are now the RARE EXCEPTION, not the workhorse.** Allowed occasionally, as a deliberate clean-plate cut, ONLY when the data genuinely needs it (a real labelled timeline, a map). Never as the default way to teach. Default is Brain + notebook / fingers / ground / objects.

---

## RULE 3 — CONTACT BEATS (Brain's immersion signature; already banked, restated here as visual grammar)
A discovery-learner REACHES INTO the scene. Brain crouches, kneels, touches the evidence — fingers in cold river water, palm to a cave wall, sand running through her hand, hand held toward a flame. Triple duty: visual variety, second-person immersion ("feel this"), character-as-visual. Contact beats and diegetic teaching are the same family: **teaching and feeling THROUGH the body, in the world** — never cutting away to abstract-land.

---

## RULE 4 — THE RENDER-PATH MAP (which beat goes where; banked, restated)
- **Crew beat** (has a `{token}`) → `/edit` reference path → clones the photoreal ref sheet → identity + realism hold. The STRONG path.
- **Person-free world/landscape/object beat** → text path → renders clean.
- **Diegetic teaching beat** → it's a CREW beat (Brain + notebook/fingers) → `/edit` path → strong.
- **Abstract data-graphic (rare exception)** → text path → fine, but jars; use sparingly.
- **NEVER:** an anonymous human on the text path. (Rule 1.)

The MC still-label ("NB2 /edit · N ref" vs "nano_banana_2 · text") tells you at a glance which path a beat took — use it to audit that no human beat fell to text.

---

## RULE 5 — OBJECT & LANGUAGE ANCHORS (banked, permanent)
- "football" renders American football on BOTH NB1 and NB2 → always write "soccer ball / round black-and-white soccer ball". Model-independent law.
- Genre-bait words summon their genre: "chalkboard/classroom/teacher/lesson" → cartoon classroom; suppress with "minimalist, just the subject, no classroom, no people" or make it diegetic (Brain's notebook, not a blackboard).
- NB2 renders legible text and BRAND LOGOS crisply → suffix carries "no text, no letters, no logos, no brand names" (a Wilson trademark rendered on a ball in probe two).
- In-world numerals/short labels are PERMITTED on the rare abstract graphic (NB2's text rendering is good) — but diegetic (notebook/sand) is preferred and safer.

---

## RULE 6 — SCRIPT STRUCTURE HYGIENE (banked, bitten twice)
- Parser section grammar is **`COLD OPEN` / `PART ...` / `ACT ...` / `RING CLOSE` ONLY.** Any other `##` header is read aloud as narration and errors the parse. QA labels, thumbnail blocks, notes → NEVER as `##` sections in the script; they live in a SEPARATE file.
- Out-of-band assets (thumbnail candidate poses) stay OUT of script.md entirely — separate file, run standalone — so they can't narrate or assemble. (Option 2, banked.)

---

## ALSO BANKED THIS SESSION (fold into the relevant existing sections)
- **§4b is now actually true:** all-NB2 implemented — worlds moved from NB1 (`nano_banana`) to NB2 text (`nano_banana_2`); the `image_model` was v1 the whole time despite the "all-NB2" note. The `no-people guard` (people_directive skipped on beats declaring "no people/figures/crew") is live in both the text path and flux fallback.
- **Consistency lives in references, not prompts.** Proven by the 5-image crew probe: same descriptions, 5 rolls, 5 different faces on the text path; the `/edit`-on-ref-sheet path holds identity. Canon = the ref sheet, not the words. Group art = NB2 `/edit` conditioned on all three ref sheets (multi-ref), not text.
- **Fix-this-image button:** the primary per-still repair = Sonnet vision inspect → corrected prompt → re-render on the CHANNEL model with the beat's ref. It REPAIRS defects (warps, wrong object, intruders, garbled text) but CANNOT beat a genre prior on the text path (re-rolls cartoon-presenter again) and CANNOT fix your language (renders "football" American even when cleaning the image). Regenerate is now channel-aware too (was flux-hardwired, stripped refs).
- **Crew register (§7):** Brain = discovery epistemology, inward self-deprecating humor, contact beats + field-notebook, grandma-texture (sparingly), Lauren @1.0 EXPRESSIVE. Voice table + flip-before-launch discipline.
- **Park criteria (resolves the §2 vs cold-start contradiction):** do NOT park on 48h of a cold channel (zero-sub = zero browse/suggested is EXPECTED). Judge on the TREND across 8–10 in-cluster videos: is served-CTR improving, is AVD holding near the tight 8–10min bar, is returning-viewer % climbing. Two-to-three-month commitment per the cadence, not 48h. Coherence-first (stay in the death-stakes cluster) buys the audience; breadth (video 15+) spends it.
