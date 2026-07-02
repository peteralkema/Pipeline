#!/usr/bin/env python3
"""
patch_qqrew_doctrine.py -- fold 2026-07-02 session doctrine into _QQrew.md.

Additive + reconciled with existing content (read the live doc first, 02 Jul):
  - §6 gains a new subsection §6b (Visual Grammar: anonymous-human gate + diegetic
    teaching + contact beats) inserted AFTER §6a, BEFORE §7.
  - §8 gains a "DIRECT-RENDER FLAT-COLOUR METHOD (PROVEN 02 Jul)" block appended
    at the end of the existing thumbnail section (extends, does not replace, the
    already-banked locked config).
  - §9 gets a one-line correction: the all-NB2 decision (banked 01 Jul as doctrine)
    was IMPLEMENTED IN CODE 02 Jul (image_model was still v1 until tonight).

Anchored to live headers. Idempotent (_PATCH_QQREW_0702), backup, no py_compile
(markdown) but verifies each anchor is unique before writing.
    python3 patch_qqrew_doctrine.py --file shared/docs/_QQrew.md
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

SENTINEL = "banked 02 Jul 2026 — Fire/ep5"

# --- §6b: insert before the "## 7. THE CREW" header ---
ANCHOR_7 = "## 7. THE CREW (durable IP — full spec in `crew_character_bible.md`)"
SEC_6B = '''### ★ 6b. THE VISUAL GRAMMAR — the anonymous-human gate + diegetic teaching (banked 02 Jul 2026 — Fire/ep5, the cartoon-render day)

*Ep5 (Fire, Brain solo) first-rendered with ~25 stills coming back as MODERN CARTOON PEOPLE (a beanie kid with a phone, cafe strangers, teens at a firepit) with zero relationship to the prompt — one beat even shoved the real scene into a thought-bubble beside a cartoon character. This section is the doctrine that closed the class. It is the character-channel sibling of §6a: §6a is about not letting canon drown the scene; §6b is about not asking the text path for a human it cannot anchor.*

**THE ROOT LAW — a human in frame is a CREW MEMBER or does not exist.** There is no anonymous person on this channel. NB2 text-to-image, handed an unanchored human ("a lone figure / silhouette / someone / early-human / a huddle / people / beyond her"), renders a **modern smiling cartoon character** every time and discards the scene. Enforced on BOTH layers now:
- **Engine (permanent):** on `render_mode:"reference"`, any beat that reaches the TEXT path has no `{tag}` → no reference → it is person-free BY DEFINITION, so the rulebook `people_directive` is stripped unconditionally (`patch_nopeople_default`, live 02 Jul). A text beat can no longer summon a human no matter how it is worded. (The earlier narrow phrase-guard — strip only on "no people/figures/crew" — missed beats worded "no face"/"no clear animal"; the architectural default replaces it.)
- **Authoring (the gate — do this at write time):** BANNED in any crew-absent VISUAL — "figure, silhouette, someone, a person, early-human, huddle, figures, a lone X", depicted "people". If the beat needs a specific person → it is a crew member with their `{tag}` (routes `/edit`). If it needs no specific person → the beat is person-free (the fire, the torch, the fleeing animals, the empty plain); **narration carries the humans.** Pre-render check: grep every crew-absent VISUAL for the banned words. (Person-free landscapes and `/edit` crew beats rendered flawlessly all through Fire; only unanchored-human text beats failed.)

**TEACHING IS DIEGETIC BY DEFAULT (the creative upgrade — proven gorgeous).** Abstract flat teaching-graphics (vector clocks, neon guts, stick-figure chains) render fine but JAR — a foreign vector-art universe cutting against a crew member in a real place. Default teaching mode is now IN-SCENE, via the crew's body and props:
- Fingers (count / scale), ground-writing (numbers/diagrams scratched in sand, dirt, ash, snow), found objects (twigs to count, stones for a proportion), and ★ **Brain's FIELD NOTEBOOK** — she jots a finding and holds it to camera. Her signature mechanic.
- Why the notebook wins: it is discovery-epistemology made visual (same character-logic as contact beats); hand-drawn field-notes are MEANT to be loose, so NB2's text-garble reads as authentic rather than as a bug (**the failure mode becomes the aesthetic** — proven this session, the hand-vs-paw notebook render was a highlight); period-neutral (a phone drags a modern object in AND re-triggers the modern-person prior — NOTEBOOK over phone always for deep-time).
- Abstract data-graphics are now the RARE deliberate exception, never the workhorse.

**CONTACT BEATS (Brain's immersion signature).** A discovery-learner reaches INTO the scene — crouches, touches the evidence (fingers in cold river, palm to cave wall, sand through the hand, hand toward flame). Same family as diegetic teaching: teaching and feeling THROUGH the body, in the world. Routes `/edit`, holds identity across novel postures (proven across 100+ Fire beats).

**Render-path map (audit via the MC still-label):** crew `{tag}` → `/edit` (strong, holds identity); person-free world/object/landscape → text (clean); diegetic teaching → it is a crew beat → `/edit`; NEVER an anonymous human on text. The label "NB2 /edit · N ref" vs "nano_banana_2 · text" tells you the routing at a glance — any human beat reading `text` is a bug.

---

'''

# --- §8: append the direct-render method at the end of the thumbnail section ---
# anchor = the last line of §8 before "## 9." (the Title-vs-headline line)
ANCHOR_8_END = '''**Title (metadata) vs thumbnail headline are DIFFERENT strings** — full SEO title in the header, short punchy headline on the thumbnail.'''
SEC_8_ADD = ANCHOR_8_END + '''

**★ THE DIRECT-RENDER FLAT-COLOUR METHOD (PROVEN 02 Jul 2026 — the pose-picker).** For a reference-crew channel, the scroll-stopping "character on a flat POP colour, pushed right, shocked, headline top-left" thumbnail (the ICE-AGE / NO-SOAP look) is made in ONE render, not by cut-and-composite:
- **Render the pose ON the colour:** `make_character_ref.py --ref <char>_ref.png --prompt "...large and close, [shocked/alarmed expression], on a solid flat [palette-colour] background, high-key studio lighting, photorealistic, no text"`. The image model places the character correctly on the flat colour in a single shot — no rembg, no compositing.
- **Then draw text with the EXISTING path** (`low_silhouette` composition; this channel's block already has darken 1.0 / vignette 0 / scrim 0, so it overlays text without dimming the bright render). Confirms the §8 locked config directly.
- `bg_palette` (5 on-brand colours) lives in the channel.json thumbnail block; pick one per pose. `character_ref` names the reference_map key to clone.
- **A/B lane for every video:** ship the upload with an IN-SCENE still thumbnail (character in the world the video is about — often stronger, more specific); add the flat-colour-pose variant in Studio's Test & Compare as B. (Upload API takes ONE thumbnail; Test & Compare is set in Studio post-upload — likely not API-exposed. CONFIRM when wiring.)
- **DEAD CODE (do not build on):** a `solid_color_character` cut-and-composite mode + its positioning patch were built then abandoned when direct-render proved simpler and cleaner. Retire them. The `--composition` / `--bg-color` CLI flags on `make_thumbnail.py` are useful — keep.
- **OPEN (next session):** the MC "Generate 5 poses" button (5 `make_character_ref` renders on random palette colours, no text → grid → pick 1-5 → existing `/api/thumbnail` draws the headline). Build on the DIRECT-RENDER path.'''

# --- §9: one-line correction on the all-NB2 implementation ---
ANCHOR_9 = '''- **Mode:** all Mode A. No Mode B (yet). No music (yet).'''
SEC_9_ADD = '''- **Mode:** all Mode A. No Mode B (yet). No music (yet).
- **NB2 text endpoint (implemented 02 Jul):** the "all-NB2" decision banked 01 Jul (§4b) was DOCTRINE only — `image_model` was still `nano_banana` (v1) in config until tonight. `patch_nb2_text` added `nano_banana_2` → `fal-ai/nano-banana-2` and flipped the config; crew-absent/text beats now render on NB2 text, matching the `/edit` family. (banked 02 Jul 2026 — Fire/ep5)'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="shared/docs/_QQrew.md")
    a = ap.parse_args()
    t = Path(a.file)
    if not t.is_file():
        print(f"ERROR: not found: {t}", file=sys.stderr); return 2
    src = t.read_text(encoding="utf-8")
    if SENTINEL in src:
        print(f"already applied -> no-op: {t}"); return 0
    checks = [("§7 header (for §6b insert)", ANCHOR_7),
              ("§8 end line", ANCHOR_8_END),
              ("§9 mode line", ANCHOR_9)]
    for label, anc in checks:
        c = src.count(anc)
        if c != 1:
            print(f"ERROR: anchor {label!r} found {c}x (need 1). Refusing.", file=sys.stderr); return 3
    out = src.replace(ANCHOR_7, SEC_6B + ANCHOR_7, 1)
    out = out.replace(ANCHOR_8_END, SEC_8_ADD, 1)
    out = out.replace(ANCHOR_9, SEC_9_ADD, 1)
    b = t.with_suffix(t.suffix + ".pre_0702")
    shutil.copy2(t, b); t.write_text(out, encoding="utf-8")
    print(f"OK patched {t} (backup {b.name}) — §6b added, §8 extended, §9 corrected")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
