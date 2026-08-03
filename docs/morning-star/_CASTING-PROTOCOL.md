# _CASTING-PROTOCOL.md -- reference & canon definition (the director's step)  [2 Aug, v1]
### Thesis: tokens unbundle. IDENTITY (who/what a thing is) migrates to the fal-Assets registry, cast once with Peter's eyes and guaranteed by reference forever. FRAMING (how this beat sees it) stays beat-side. Density laws loosen for cast identities (a protagonist dominating his act is craft, not defect -- density_exempt_tokens); shot-variety within the same identity tightens (never the same framing twice running). The monotony laws were the tax paid for not having references; the registry retires the tax.

## THE SIX STAGES (owner in caps)
S0 SOURCE SCAN -- OPERATOR (supervised): read the sources; list every recurring character, place, prop, and visual DEVICE the story requires (a returning refrain-image is a prop). Output: raw cast longlist with per-entry story role + form arcs (a character whose appearance transforms across the film gets ONE identity with N FORMS, each form its own registry entry: e.g. lightbearer / fallen / dragon).
S1 CASTING SHEET -- SENIOR: for every entry, drafted canon text obeying the visual-grammar law (register suffix drives style; canon never leads with beauty-portrait language), Law 34 (period/realm anchor in-string), negation-clean, wardrobe/material-locked (the Elijah-doc method). Plus staging notes (face-on permitted vs staging-menu) and which forms need refs vs which stay environmental. Output: CASTING-SHEET.md for Peter's sign-off.
S2 THE CASTING SESSION -- PETER: the playground. Each sheet entry generated across the 24-model rig; re-roll until the eye says yes; select 3-5 reference frames per FORM (full-body, profile, 3/4, detail); upload to fal Assets (the proven festival flow). This is the highest-leverage hand-touch in the pipeline: hours per FILM, never per frame. Nothing proceeds until every entry is greenlit -- expected-icon debt (T8) becomes structurally impossible here.
S3 REGISTRY LOCK -- SENIOR: asset ids into <channel>/assets.json (kind, forms, canon, staging_default); CHARACTERS.md written (bio, arc, staging, wardrobe canon); density_exempt_tokens set in the film's chop-config for all cast identities. Committed to git. The cast now exists independent of any one film.
S4 AUTHORING UNDER CAST -- OPERATOR: the river is written AROUND a cast that cannot fail to render. @tokens appear inline in variant/phenomenon text like prose ("medium: @michael at the rampart, spear grounded, host behind"). Beat craft is FRAMING: same @ in adjacent beats must differ in shot grammar (the adjacent-near-dup gate enforces). Uncast material (skies, seas, fire, weather, crowds) continues on the classic text-token system under ALL standing laws including 32b.
S5 GATES -- OPERATOR: full standing chain, plus: every @ in the CSV exists in assets.json (unknown-@ = HARD, ships with the resolver); cast tokens exempt from 32b density, never from adjacency/framing checks.
S6 RENDER -- SENIOR DEPENDENCY: the @-resolver (V2-ASSETS-SPEC Phase B: registry loader, prompt expansion, Seedream-with-refs routing) lands on the box BEFORE this film's visuals stage. Casting and authoring never block on it; the door does.

## MORNING STAR -- CASTING CALL v0 (the pilot instantiation; Peter to approve/edit before S1 drafting)
CHARACTERS (identity / forms):
  @morningstar -- THE lead; three forms: (a) lightbearer (pre-fall radiance beside the throne), (b) the fallen (post-fall, beauty curdled -- design brief: recognizably the SAME face, glory withdrawn), (c) the dragon (final form; creature-scale). The serpent of Eden is staged as form (b) working through the serpent (environmental serpent + @morningstar presence), unless Peter rules the serpent a fourth form.
  @michael -- the general; one form; face-on permitted; the war's other face.
  @watcher_prime -- one named Watcher carrying the descent arc (the two hundred stay environmental host).
PLACES: @throneroom (the sea of glass, the mountain of God); @eden_gate (garden threshold, guardians); @theabyss (the landing; the prison under the hills).
PROPS/DEVICES: @mosaic -- the refrain: the shattered picture assembled fragment-by-fragment across twelve movements; MUST be one designed object or the device dies. Optional: @thechain (the binding, Rev 20 payoff).
ENVIRONMENTAL (uncast, classic tokens): heavenly host, falling third, flood world, Nephilim silhouettes, war-in-heaven skies, lake of fire.

## THE FAL LEVER MAP (verified against fal docs, 2 Aug)
PLATFORM LAYER (the registry -- persists account-wide, across every film and channel; THE compounding store):
  - assets/characters: the ONE native semantic class. name + @mention identifier + description (2,000 chars, used for SEMANTIC MATCHING -- our canon text lives inside the asset) + 1-20 reference_images + full CRUD API.
  - collections + tags: the organizational primitives. Places and props have NO native class -- they live as reference COLLECTIONS (e.g. collection "throneroom-refs"), consumed by passing their images to reference-capable endpoints.
MODEL LAYER (the levers that consume references, per-endpoint):
  - Image: Seedream v5 multi-input edit; Nano Banana 2 family edit; Flux Kontext Multi; Ideogram character + separate style_reference_images.
  - Video: Kling O1/O3 REFERENCE-TO-VIDEO ("images, elements, and text" -> stable character identity, object details, environment); Kling V3 custom elements; Seedance 2.0 reference-to-video (up to 9 images); Veo 3.1 reference-to-video.
  - Style: register-suffix (our standing channel contract) vs style_reference_images vs LoRA training (heavy; not for this pilot).
RESOLVER IMPLICATION (Phase B spec sharpened): @token -> GET /v1/assets/characters -> reference_images -> injected into the beat's endpoint. The registry is fal-native; assets.json remains our manifest (canon doctrine + form mapping + fal ids).

## S2b -- THE PROBE (new stage, Peter's addition: throwaway, zero plumbing, full-cycle rehearsal)
Purpose: exercise EVERY lever once on real entries before the big render; probe subjects = @michael + the @mosaic prop + the throneroom place (the lead is reserved for the real session). Budget ~$3-5, one sitting, outputs kept as reference stock. The card:
  P1 REGISTER: create michael as a platform character via API (name, @michael, canon text as description, 4 refs from a quick playground set) -- see it appear in the Assets library UI.
  P2 @MENTION: prompt "@michael standing guard on the rampart at dawn" in the playground on Seedream v5 -- does the mention resolve natively? (Festival precedent: yes.)
  P3 API INJECTION: the same scene via API with reference_images passed explicitly to the edit endpoint -- THIS is the resolver's path in miniature; its output quality is Phase B's acceptance test.
  P4 CROSS-SCENE: three scenarios, same character (throne terrace / war sky / abyss dark) -- identity across contexts, the core promise.
  P5 TWO-ENTITY: @michael + mosaic refs in ONE frame via a multi-input endpoint -- character+object composition.
  P6 OBJECT LEVER: mosaic refs alone into two new scenes (collection-as-prop workaround proven).
  P7 PLACE LEVER: throneroom refs -> two NEW ANGLES of the same hall (place-drift check).
  P8 STYLE LEVER: one scene rendered register-suffix-only vs with a style_reference_image -- see what each buys; ruling on which the channel uses stays with the register unless the eye says otherwise.
  P9 MOTION CARRY (the "element" lever you remembered): ONE Kling O3-standard reference-to-video pass with michael refs as elements -- identity surviving into MOTION, which is what cast kling beats will need.
Verdicts recorded per lever (one line each) in PROBE-VERDICTS.md; P3+P9 verdicts gate the resolver design. Then the real casting session proceeds on a rig you have personally proven end to end.

## STANDING RULES
- Casting is per-CHANNEL; films draw from and extend one registry. A form once cast is never redesigned mid-series without a versioned entry.
- The sheet precedes the session; the session precedes the river; the resolver precedes the door. No stage skips.
- Peter is the only approver of reference frames. Senior drafts canon; operator consumes cast; nobody but the director casts.
