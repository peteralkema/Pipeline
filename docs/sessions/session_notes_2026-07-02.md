# Session Notes — 2026-07-02 — QQrew ep5 "Fire" launch + the anonymous-human failure class + thumbnail method
*Channel #? QQrew (@Q-Qrew). Solo session, evening. Outcome: Fire (ep5) shipped; a whole class of image failures diagnosed and closed at the engine level; a repeatable flat-colour thumbnail method proven; four durable authoring principles banked.*

---

## HEADLINE OUTCOMES
1. **Fire (ep5) is LIVE** — Brain's solo debut, uploaded private to @Q-Qrew. First episode authored *from* doctrine rather than from memory.
2. **The "anonymous-human" failure class is permanently closed** — both by an engine patch AND an authoring gate. This was the single biggest time-sink of the session and its resolution is the most valuable thing banked.
3. **Flat-colour thumbnail method proven** — direct-render-on-colour + text overlay (NOT cutout-and-composite). Matches the reference winners; simpler than the pipeline we started building.
4. **Brain fully specced** — voice (Lauren @1.0 EXPRESSIVE), register (discovery epistemology, inward humour, field-notebook mechanic, grandma-texture), canon warmed against the flat-expression trap.

---

## WHAT SHIPPED
- **Fire / "Why Early Humans Would've Died Without Fire"** — 155 beats, ~6–7 min, Brain solo. Brave open-hook-and-hold spine (cold open on a real unresolved problem — "they should be dead, so how are you here?" — held to the ring-close, Brain visibly changed). 67% Brain presence, ~30 field-notebook teaching beats, diegetic teaching throughout (fingers/sand/twigs/notebook), 5 drone shots, one grandma-texture aside, selfie-style beats. Project dir: `qqrew/projects/fire1/modea` (NOTE the `1` suffix — see "project-naming trap" below).
- Thumbnail shipped with the upload: an in-scene still ("DEAD / WITHOUT IT" over Brain crouched with her notebook in an ice-age river valley). Strong because she's *in the world the video is about*.

---

## THE ANONYMOUS-HUMAN FAILURE CLASS (the core lesson of the session)

### Symptom
~25+ stills in the first Fire render came back as **modern smiling cartoon people** — a beanie kid with a phone in a park, a café guy with predator-eyes out the window, teens at a firepit — with zero relationship to the prompt. In one case (beat 43) the *actual* prehistoric scene rendered correctly but got shoved into a THOUGHT BUBBLE beside a modern cartoon character.

### The (long) diagnosis, and the false trails
It took several wrong turns before the real cause. Banked so we never re-run them:
- **NOT the style_suffix** — confirmed clean/photoreal via `python -c` dump.
- **NOT stale stills / wrong project** — though we DID discover `fire` (v1) and `fire1` (v2) both existed and MC was showing a mix; that was a real confound but not the root cause.
- **NOT a routing bug** — the grep proved all 104 `{brain}` beats resolved their reference correctly and routed `/edit`. Zero Brain beats fell to text. (I had wrongly hypothesised a "Bug A" here; it did not exist.)

### The actual root cause (ONE bug, two contributing faults)
Every failing still was labelled `nano_banana_2 · text` AND depicted a person who was **not a crew member**. On a reference-render channel, a beat reaches the text path only when it has no crew `{token}`. NB2 text-to-image, handed an unanchored human ("a lone figure", "a silhouette", "early-human", "someone", "beyond her"), has one overwhelming prior: **modern smiling cartoon character**. It renders that and discards the scene.

Contributing fault: the rulebook's **`people_directive`** ("...appealing realistic detailed faces where people are present...") was being appended to EVERY text prompt. An earlier phrase-guard only stripped it when the beat literally said "no people / no figures / no crew / no person". Beats worded "no face" (a hand lifting a branch) or "no clear animal" (predator eyes in grass) slipped the guard, kept the directive, and had a cartoon human summoned onto a clean plate.

### The fix — BOTH layers (this is the pattern to remember)
1. **Engine (permanent, cannot be defeated by wording):** `patch_nopeople_default.py` — on a `render_mode: reference` channel, a beat reaching the text path with NO reference images is person-free BY DEFINITION, so strip the people_directive unconditionally. Non-reference channels (Final Hours) untouched — they legitimately want crowds. Committed, live on the box.
2. **Authoring (the gate):** the v2 Fire rewrite removed every anonymous-human beat — each became either a Brain contact/notebook beat (crew `{token}` → `/edit`) or a genuinely person-free landscape (narration carries the humans). This is now doctrine (see `_QQrew.md` visual grammar).

### Why this matters beyond Fire
This is the **moat discipline working**: a failure became a tool-agnostic engine rule AND an authoring principle. Every future QQrew script — and any future reference-render channel — is protected automatically. **Fire is the last script that will ever hit this class of failure.**

---

## THE DIEGETIC-TEACHING UPGRADE (creative win that fell out of the bug)
The abstract flat teaching-graphics (vector clocks, neon guts, stick-figure chains) RENDERED fine but **jarred** — foreign vector-art universe cutting against Brain-in-a-real-place. Peter's instinct, correct: teaching should happen *in the scene*.
- **Diegetic teaching is now default:** Brain's fingers (counting/scale), ground-writing (sand/dirt/ash), found objects (twigs/stones), and ★ **the FIELD NOTEBOOK** — her signature mechanic. She jots a finding and holds the notebook to camera.
- Why the notebook wins: it's her discovery-epistemology made visual (same logic as contact beats); hand-drawn field-notes are *supposed* to be loose, so NB2 text-garble reads as authentic rather than as a bug (the failure mode becomes the aesthetic — PROVEN this session with a gorgeous hand-vs-paw notebook render); period-neutral (a phone would drag a modern object in + re-trigger the modern-person prior — NOTEBOOK over phone always for deep-time).
- Abstract data-graphics demoted to rare deliberate exceptions.

---

## THUMBNAIL METHOD (proven, and a deleted detour)
Peter showed the target style (reference thumbs: character on solid colour, pushed right, shocked pose, drop-shadow, two-tier text top-left).
- **We over-engineered first:** built a `solid_color_character` compositor mode (rembg cut + flat fill + subject shadow + positioning). Took 4 patches and still had positioning bugs (subject ran off-canvas — `subject_x_frac` was used as left-edge, pushed a waist-up figure off the right edge leaving only a hand).
- **The reframe (Peter's question "how did the refs get it perfect?"):** the reference thumbnails were **generated directly on the solid colour in one shot** — no cutout, no compositing. The image model paints the character already on flat colour.
- **PROVEN simpler method:** `make_character_ref.py --ref brain_ref.png --prompt "...on a solid flat [colour] background..."` renders the pose ON the colour → then the EXISTING `low_silhouette` thumbnail path (qqrew config already has darken 1.0 / vignette 0 / scrim 0) draws text over it. One render, one text pass. Result was excellent ("DEAD / WITHOUT IT" on orange, shocked Brain). 
- **`solid_color_character` mode + its positioning patch are now DEAD CODE** — harmless, unused, retire in a cleanup. Do NOT build on them.
- **BANK:** flat-colour thumbnails = direct-render-on-colour + text overlay, never cutout-and-composite.

---

## BRAIN — fully specced this session
- **Voice:** Lauren @1.0, deliveryMode EXPRESSIVE (auditioned + accepted; the engine hardcodes EXPRESSIVE — Peter chose to keep it rather than patch a config key).
- **Epistemology / arc engine:** discovery (vs Driver=action, Skeptic=proof). Each crew member's learning style is the arc engine and determines which episodes they narrate best. Within-episode arcs (light, hook→payoff); cross-catalogue growth deferred to video-15+.
- **Humour:** inward / self-deprecating ("that floored me", "total surprise for me guys") vs Skeptic's outward-at-viewer.
- **Contact beats + field notebook:** her immersion + teaching signature.
- **Grandma-texture:** Western-raised, family in a poorer context, quietly proud ("hi grandma") — ONE aside per episode, a texture not a theme.
- **Canon warmed** against the flat-expression trap (the Skeptic-pouty lesson): "warm engaged eyes, gently amused half-smile — never blank, never stern".

---

## ENGINE / CONFIG CHANGES COMMITTED THIS SESSION
- `patch_nb2_text.py` — NB2 text-to-image endpoint (`nano_banana_2` → `fal-ai/nano-banana-2`) + the first (narrow, now-superseded) people-guard. `image_model` flipped to `nano_banana_2`. (The §4b "all-NB2" decision was never actually implemented before this — the model string was still v1.)
- `patch_nopeople_default.py` — the architectural people-directive fix (above). THE important one.
- `update_qqrew_thumbnail_config.py` — added `bg_palette` (5 on-brand colours), `character_ref: brain`, photoreal `pose_prompt_suffix`.
- `patch_thumbnail_solidmode.py` + `patch_solidmode_positioning.py` + `patch_thumbnail_composition_flag.py` — the cutout mode + `--composition`/`--bg-color` CLI overrides. The `--composition`/`--bg-color` flags are USEFUL (keep); the `solid_color_character` mode is DEAD CODE (retire).
- Voice flip to Lauren @1.0 in `qqrew/channel.json`.
- Doctrine drafts committed: `shared/docs/_qqrew_visual_grammar_DRAFT.md`, `shared/docs/_qqrew_brain_register_DRAFT.md`.

---

## OPERATIONAL LESSONS BANKED (tool-agnostic)
- **Project-naming trap:** the suffix-numbered project is the NEWER launch, not the older one (`fire1` was v2, `maracanazo1` before it). NEVER assume by name — **fingerprint by content** (`grep -c "field notebook" .../script.md`). Bit us twice.
- **Anchor patches to LIVE box code, always.** `patch_nopeople_default` v1 REFUSED because it was anchored to a stale uploaded copy that predated an earlier guard. The refusal was the anchor-check working — but the lesson is: `grep`/`sed` the box file before writing the patch, every time. This is already in the working style; tonight proved why it's non-negotiable.
- **The engine loads config + module once at launch and holds them.** A running batch can't see a mid-render patch. Re-render (restill / relaunch) as a FRESH process to pick up an engine change. Never `systemctl restart` the review service mid-render (cgroup teardown kills the in-flight run).
- **`restill --project <dir> --shot N`** takes the ENGINE shot index (storyboard `index`), NOT the MC gate's "beat N" label — they differ. And `--project` must point at the `modea` dir (proj_paths builds paths flat off `<project>`).
- **Fix-this-image repairs defects but can't beat a genre prior on the text path** (re-rolls the same cartoon) and **can't fix your language** (renders "football" American even while cleaning the image). Authoring owns object words.

---

## STATE AT SESSION END
- Fire (ep5): SHIPPED (private).
- Thumbnail: method proven; MC "Generate 5 poses" button NOT yet built (part 3 — next session).
- Salt (ep6): NOT started — held by launch-pair discipline for Fire's 48h CTR+AVD signal, and it inherits the full grammar so it should render clean first-pass.
- Doctrine drafts committed but NOT yet folded into `_QQrew.md` proper (doc-pass pending).
- Dead code to retire: `solid_color_character` mode + positioning patch.
