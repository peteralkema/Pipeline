# ELIJAH-TASTE-INPUT.md — THE FAL.AI HUMAN-TASTE WORKFLOW
### The doctrine for feeding Peter's visual taste into the pipeline UP FRONT, at scripting stage — proven-ready by v2's schema and passes, to be production-proven on THE ELIJAH EPIC (a ~2-hour movie).
### One sentence: the fal.ai UI is the taste instrument Mission Control tried to be; canon is how taste enters the door; pre-filled columns are how it survives to the final frame.

---

## 1. THE THREE SCENARIOS (all three ride existing v2 mechanics)

**A — Provided stills ("here are the first 10 visuals for the cold open").**
Mechanism: pre-filled columns. Stage 3's stills pass is `pending(still_path IS
NULL)` — a beat with a still already on disk is INVISIBLE to generation, and the
clips pass treats your image identically to a generated one (Kling i2v doesn't know
who made the still; the KB floor doesn't either). PROVEN 31 Jul in the e2e: three
hand-made stills pre-marked; pass A generated zero. Pipe: a small sidecar in the
src set (`provided_stills.json`: `{beat_id_or_position: url_or_path}`) → ingest
downloads each and sets `still_path`. This is a ~20-line ingest addition, no schema
change. Cold opens are the natural home: the 10-15 beats where your eye matters
most, hand-picked in the playground, machine fills the other 500.

**B — Characters (@elijah).** Mechanism: text. The fal character feature is
prompt-level — the handle rides inside the prompt string on endpoints that support
it. The canon system already transports exactly this: `{elijah}` in the phenomenon
column expands from the canon table, and the expansion text simply CONTAINS the
handle: `"@elijah -- a weathered prophet in a camel-hair mantle, wind-scoured,
bright blockbuster photoreal"`. Requirements: (1) the character is set up once in
your fal account; (2) the project's `image_model` points at an endpoint that honors
handles. Zero pipeline changes — the door, the DB, and visuals.py never learn that
characters exist. CAVEAT (honest): handle support is endpoint-specific and can
change; before authoring a whole film on a handle, prove it with a 5-still probe
through the API (not just the UI) on the exact endpoint the project row names.

**C — Reference images (the pillar of fire; the seam that needs one small build).**
Mechanism: `canon.reference_paths` (JSON list — in the schema since draft 1) +
provenance URL. When a token carries references, the still generator branches to
the ref-conditioned /edit endpoint with `image_urls=[...]` instead of plain
text-to-image — same registry, one branch, keyed by data presence. This is v1's
`render_mode:"reference"` (the Bentley & Watson car-plates work) reborn per-token
as data instead of a channel-level mode. STATUS: schema present; visuals.py
currently REFUSES ref-carrying tokens loudly by name (deliberate: no silent
wrong-path renders). The wiring = backlog #12, sized ~40 lines: ingest downloads
ref URLs into `<project>/refs/` and fills reference_paths; `_gen_still` branches to
the /edit path (harvest `_generate_still_reference` from recreation_pipeline.py,
the third organ-donation). **This lands as the Elijah project's first act.**

**THE URL RULE ("play on URLs, ship on files"):** fal playground outputs get
persistent fal.media URLs, and both ref-conditioned image endpoints and Kling i2v
accept `image_url` directly — perfect for the taste loop, zero friction. But the
golden principle (DB + media on disk = reconstructible video) makes a CDN URL a
courtesy, not a contract: **the URL is transport + provenance; ingest downloads it
once; the FILE is the truth.** URLs live in canon provenance for the record.

## 2. THE SCENE CONTRACT — how a scene is described so it carries EXACTLY into the final movie

The 24-model pillar test (§3) demonstrates the core problem: one prompt,
twenty-four different STAGING decisions. A prompt under-specifies blocking; the
model's prior fills the gap; and "Elijah, arms raised" put the prophet beside the
altar, on the altar, and INSIDE the fire depending on the model. The fix is not a
longer prompt — it is separating the five things a scene IS, locking each at the
right layer of the existing system:

**Field 1 — VANTAGE** (wide / medium / close / extreme close; ground / aerial /
low-angle). Lives in: the VARIANT's first token (already the audit's shot-scale
input). Playground habit: generate the same scene at 3 vantages; keep the set.

**Field 2 — SUBJECT + ACTION** (who/what + the single verb: "Elijah, arms raised";
"the pillar descends"). Lives in: the variant text; character identity itself in
the CANON expansion (and the @handle / reference set — Field 5's twin).

**Field 3 — STAGING / BLOCKING** (the spatial sentence prompts always omit and
models always improvise: WHERE everyone is relative to everything — "Elijah stands
BESIDE the altar at frame left; the fire strikes the ALTAR, never the man; the
prophets recoil in the foreground shadow, backs to camera"). Lives in: the variant
text, stated as positively-phrased spatial relations. This field is the single
biggest carry-through gain available — it is what the bake-off shows models
disagreeing on most.

**Field 4 — LIGHT / ATMOSPHERE** ("storm-dark sky, the pillar the only light
source, rim-lit crowd"). Lives in: variant text + the channel register.

**Field 5 — REGISTER + IDENTITY LOCKS** (the style contract: "bright blockbuster
photoreal, cultural precision, NOT-X guards"; plus the character's face/costume).
Lives in: `project.style_contract` (one locked paragraph, appended to every prompt
by visuals.py) + canon description + reference_paths/@handle. **Identity carried by
REFERENCE beats identity carried by adjectives** — this is the entire lesson of the
Job ash-heap carousel (the AI re-rolls the actor every still unless something
locks him).

**Hero moments get a sixth field — THE HERO FRAME:** for the ~10-20 beats per film
where the image IS the point (the pillar strike, the chariot, the still small
voice), the contract is not text at all: it is a SELECTED IMAGE from a playground
session, entering as Scenario A (that exact frame becomes the beat's still) or
Scenario C (it becomes the token's reference, conditioning every sibling shot).
Text contracts scale; hero frames anchor. A 2-hour film wants ~15 hero frames and
~600 contracted beats.

**Consistency ladder (weakest → strongest), choose per subject:**
plain prompt < prompt + style_contract < same-model + style_contract <
@handle character < reference images per token < provided still (absolute).
Recurring characters (Elijah, Jezebel, Ahab) sit at handle-or-references.
Recurring PLACES (Carmel's altar, the Kerith ravine, Horeb's cave) also deserve
references — place-drift is as visible as face-drift across 600 beats.

## 3. THE 24-MODEL PILLAR-OF-FIRE BAKE-OFF — what the grid actually teaches

Prompt: *"Epic wide-angle view: divine pillar of fire descends from stormy heavens
onto stone altar. Elijah, arms raised, bathed in radiant light. False prophets
recoil, shielding eyes. A dramatic biblical spectacle."* Read against the contract:

**Finding 1 — staging is the axis of disagreement, not quality.** Roughly half the
models put a figure ON or IN the fire/altar (grok, flux-2/klein, seedream v4.5,
z-image, flux/krea, flux-1/krea, several flux family) — a defensible but WRONG
reading of the brief (the fire consumes the SACRIFICE; Elijah stands apart). The
models that staged it right (nano-banana-2, nano-banana-2-lite, seedream v5 pro,
ideogram v4, gpt-image-2, flux-2-pro with the bull on the altar) are the ones whose
priors filled the blocking gap correctly. Lesson: Field 3 must be EXPLICIT, and the
bake-off is a STAGING audition as much as a style one.

**Finding 2 — our production model failed the ensemble.** flux-pro/v1.1 ($0.040,
5.7s) delivered a gorgeous pillar and NO CROWD — the recoiling prophets, a third of
the brief, absent. For an epic whose register is crowds-witnessing-wonders, that is
disqualifying for hero/ensemble scenes. flux stays excellent for object-first,
landscape, and single-figure beats (most of a film's floor), which suggests:

**Finding 3 — the two-tier model doctrine.** ONE base model per film for the ~95%
(register consistency demands it — mixing models per-scene reads as film-stock
changes); hero/ensemble tokens MAY carry a second, reference-conditioned model via
the per-token seam. Candidates from this grid for the Elijah base: **nano-banana-2**
($0.080, 11.1s — best brief-adherence + photoreal ensemble; the /edit sibling is
also our proven reference endpoint = one family for both tiers) and
**nano-banana-2-lite** ($0.042 — nearly the same staging quality at flux's price);
**seedream v5 pro** ($0.135) as the premium alternate; **flux-2-pro** ($0.030) the
value surprise (altar + sacrifice + crowd, correct staging). ideogram v4's $0.007
is astonishing but its register is illustrative-painterly — wrong for this channel,
worth remembering for any future stylized channel. gpt-image-2: strong, but $0.211
and 192s — 5× cost, 30× latency of the winner; no.

**Finding 4 — the cost spread is 70× and quality is NOT monotone in price**
($0.003 schnell produced a UFO-disc pillar; $0.042 lite beat $0.211 gpt). Model
choice is an EMPIRICAL per-film decision, made exactly the way this grid was made —
which is why the bake-off is now a standing pre-production step (§4, Step 1), and
why `image_model` is a data column, not a constant.

**Finding 5 — aspect drift:** several models returned portrait/square against a
"wide-angle" brief. The API path pins width/height from the project row, so
production is safe — but playground selects should be re-generated at 16:9 via API
before becoming references, or the reference itself teaches the wrong frame.

## 4. THE ELIJAH EPIC — the plan (the test of the whole approach)

**Shape:** ~2 hours ≈ **~18,000 words ≈ ~450-480 beats** at the feature register
(calibrate against real Elliot pace once Part VI ships; 165-law says 19.8k —
plan the river at ~19k and let the chop settle it). Acts (≤12): the drought vow →
Kerith and the ravens → Zarephath (the widow, the flour, the raised son) → the
summons → CARMEL (the contest, the mockery, the water-drenched altar, THE PILLAR —
the film's thumbnail-payoff heart) → the rain returning → Jezebel's threat and the
flight → the desert broom tree → HOREB (wind, earthquake, fire, the still small
voice — the register inversion the whole film aims at) → Naboth's vineyard (the
moral engine) → Elisha's call → the CHARIOT OF FIRE ascension (the closer). Cold
open per the Opening Signature Ledger: a NEW shape (the ledger holds tribunal /
orbital / throne / dream-scale / time-survey) — strong candidate: **rain-vantage**,
opening inside the three-year sky that will not break, the whole land seen through
absence, diving to one man who swore it shut. Dream License available if wanted
for Horeb's theophany. BOM at kling-16-24 on a 470-beat film: 470×$0.08 + 20×$0.42
+ $1 ≈ **$47-49** — over every ceiling; this is a FLAGGED flagship override,
priced consciously as the format's flagship, or trimmed to ~$40 at kling-12.

**Pre-production (the taste phase — Peter in the playground, ~2-3 sessions):**
1. **Model bake-off, done properly:** the pillar grid re-run on THREE contract-
   complete scene briefs (pillar / chariot / still-small-voice-cave) across the
   short-list (nb2, nb2-lite, seedream v5, flux-2-pro) at 16:9 → pick THE base
   model → set `project.image_model`.
2. **@elijah:** build the character in fal (curated set: face, camel-hair mantle,
   leather belt, staff — 2 Kings 1:8 is the costume contract); probe 5 stills via
   API on the chosen endpoint; if handles don't hold on that endpoint, fall back to
   references (same taste work, different transport).
3. **Hero-frame hunt:** ~15 selected frames (pillar strike, ravens at the ravine,
   the cloud like a man's hand, chariot) → URLs recorded → these become Scenario A
   provided-stills (exact beats) and Scenario C token references (siblings).
4. **Place references:** Carmel altar, Horeb cave mouth, the ravine — one reference
   set each.
5. Everything lands in the src set: `canon.json` entries carry reference URLs +
   provenance; `provided_stills.json` maps the hero beats.

**Engineering that gates it (small, first act of the project):** backlog #12 — the
reference wiring (~40 lines: ingest downloads refs; `_gen_still` /edit branch
harvested from v1) + the provided-stills sidecar (~20 lines) + the speaking_rate
fix riding along. One migration if any column is touched (none expected —
`reference_paths` already exists).

**Then the standard process runs unchanged:** river (Kings + the register) → chop →
gates → door → six stages → Studio. The bet being tested, stated for the record:
**that playground taste, entered as canon + references + hero frames at scripting
stage, carries through 470 beats to the final cut with the operator never touching
a render mid-flight** — fal.ai UI as the taste input Mission Control was reaching
for, with the door as the only handoff.

## 5. RISKS, NAMED HONESTLY
- Handle support is endpoint-specific → always API-probe before authoring on it.
- References constrain AND flatten: over-referenced tokens can go same-y — the
  spanning rule (Law 22) applies to reference-conditioned variants too; references
  lock IDENTITY, variants must still vary VANTAGE/staging.
- CDN persistence is not a contract → download at the door, always.
- Two-tier modeling risks register seams → the bake-off must judge the TWO models
  side by side on the same scene before the film commits.
- A 2-hour film doubles every known per-film discipline (archetype caps, ledger,
  three dials) — Step 1 for Elijah must treat 470 beats as two films' worth of
  variety budget, and the novelty-dial/escalation gaps (still open) bite hardest
  exactly here: design them in by hand until the tools enforce them.
