# Multi-Genre Script Architecture — Design Principles
*A working design document for the next 1-3 years of pipeline evolution — May 2026*

This document captures the architectural decisions needed to evolve the current pipeline from atmospheric narrated documentary (Final Hours, Success Coach) toward genuine multi-genre support including literary adaptation (Channel 3) and eventually dialogue-driven drama (future channels).

The principle behind every decision below: **design for the most demanding case (a real movie script) but make the simpler cases inherit cleanly and remain trivial to author.** If the architecture handles dialogue-driven drama correctly, narrated documentary becomes a degenerate case where the dialogue list is empty and the structure collapses to a single-narrator flat sequence.

Not a build-this-week document. A bank-the-decisions document for the next 6-18 months of pipeline evolution.

---

## The problem we're solving

The current pipeline assumes uniform-density beats. Every shot is ~5 seconds. Every beat has equal narration weight. The assembler computes `z = narration_duration / clip_count` and trims every clip to z. This works perfectly for atmospheric documentary where each beat carries roughly equal emotional volume; it actively destroys narrative content where pacing is the whole craft.

The salary-negotiation video showed this in microcosm. The beat after Sarah names her number ("She lets the number sit between them. Five seconds. Then ten.") needs to be held. Held silence is the entire dramatic moment. Slicing it into a 5-second clip averaged across the rest of the video kills it. The grid is wrong for narrative; it was always going to be wrong for narrative; we accepted it because Final Hours' atmospheric register tolerates it.

Channel 3 cannot ship on a flat grid. *Sredni Vashtar*'s final image needs duration the viewer feels physically. *The Open Window*'s twist needs the camera to linger on the host's horrified face. Beats are not interchangeable atomic units; they are dramatic moments with native durations the pipeline must honour.

Beyond Channel 3, the longer horizon (literal movie production, 5-10 years out) requires the architecture to support dialogue, coverage, multi-character scenes, and traditional film grammar. Building that architecture now — even if not implementing all of it now — means the slow layers don't break as new capabilities slot in.

---

## The hierarchy

Four levels, distinguished by structural function. Each level can be configured per channel.

**Project.** The whole film. One project = one published video. Holds project-level metadata: title, channel context, target duration, canon block, default values for everything below.

**Act.** Major structural division of the narrative. Optional for short content (Final Hours, Success Coach typically use one implicit act). Required for long-form (Channel 3's 15-minute literary adaptations probably benefit from explicit acts; future feature-length work demands them). Acts have their own emotional registers, music cues, and pacing arcs.

**Scene.** Single location + time unit. A scene is the natural unit of canon scope — a scene has *one* setting, *one* set of characters present, *one* lighting register. Scene-level canon descriptors (the kitchen, the deck, the meeting room) live here and apply only within the scene. Scenes also carry mood metadata: emotional register, music cue, pacing intent, transition style into the next scene.

**Shot.** The atomic unit of rendering. A shot has an image_prompt (what to render), an explicit duration (how long to hold it), motion intent (how it animates), and an audio assignment (which narration line plays over it, which dialogue, which ambient cues). One shot becomes one rendered clip.

The current "beat" maps to "shot." Renaming the term is honest about what we're modelling — we're not generating beats of music, we're generating shots of cinema. Beat made sense when scripts were poetry-prose; shot makes sense when scripts are cinematography.

---

## The schema, fully

A working JSON shape that supports all current and foreseeable content. Most fields are optional; sensible defaults inherit from above.

```json
{
  "title": "Sredni Vashtar",
  "channel": "channel_3_literary",
  "target_duration_seconds": 900,

  "canon": {
    "conradin": "Conradin, ten years old, frail, dark Edwardian boy's clothes...",
    "the_aunt": "the_aunt, mid-fifties, severe Edwardian dress...",
    "the_ferret_god": "a large polecat-ferret, dark fur, intelligent eyes...",
    "garden_shed": "a weathered Edwardian wooden garden shed..."
  },

  "voices": {
    "narrator": "Reed",
    "conradin": "literary_child_voice_id",
    "the_aunt": "literary_severe_voice_id"
  },

  "acts": [
    {
      "id": "act_01",
      "title": "The boy under the eye",
      "emotional_register": "oppression",
      "music_cue": "controlled_dread_low",

      "scenes": [
        {
          "id": "scene_01_breakfast",
          "title": "Breakfast under the cousin's eye",
          "location_canon": "Edwardian dining room, gas-lit, panelled, oppressive",
          "characters_present": ["conradin", "the_aunt"],
          "mood": "suffocation",
          "ambient_track": "morning_kitchen_quiet",

          "shots": [
            {
              "id": "shot_001",
              "image_prompt": "Wide cinematic shot of {conradin} alone at one end of a polished mahogany breakfast table...",
              "motion_prompt": "Slow gentle motion. Steam rising from the teacup.",
              "duration": 6,
              "audio": {
                "narration": "Conradin was ten years old, and the doctor had told his cousin's wife she could not last another five years.",
                "dialogue": [],
                "sfx": []
              }
            },
            {
              "id": "shot_002",
              "image_prompt": "Close intimate detail of {the_aunt}'s severe face from across the table...",
              "motion_prompt": "Still. The almost imperceptible tightening of her mouth.",
              "duration": 4,
              "audio": {
                "narration": "She, of course, would last forever.",
                "dialogue": [],
                "sfx": []
              }
            }
          ],

          "transition": "cut"
        },

        {
          "id": "scene_02_garden_shed",
          ...
        }
      ]
    }
  ]
}
```

Five things this shape gets right:

**Variable shot duration is explicit and honoured.** Each shot declares its target seconds. The assembler renders the clip at that duration; the narration plays from its own track and lands where its words land, with silence padding allowed inside shot durations longer than the corresponding narration. No more averaging.

**Canon hierarchy still works.** Project-level canon (the recurring characters and key objects) plus scene-level location_canon merges at load time, the same way channel base_canon merges into project canon today. Each shot's prompt uses whichever canon tags apply. The mechanism we already built composes upward.

**Audio is explicit per shot.** Narration is one slot; dialogue is a list (zero or more lines, each assignable to a character voice); sfx is a list (door slamming, glass breaking, the ferret moving in the shed). The mixer handles all three layers separately. Final Hours videos populate only the narration slot and inherit the existing pipeline behaviour.

**Scene-level audio context.** Each scene declares its ambient track (the kitchen morning quiet, the deck wind, the shed silence). The mixer plays the ambience under the entire scene; transitions cross-fade between ambient tracks. This is what makes the audio feel filmic instead of voiceover-over-music.

**Acts carry pacing intent.** The emotional register and music cue at the act level tells the music generator (and eventually the colour grader, and eventually the editor) what register to operate in. Act-level intent cascades down to scenes and shots that don't override.

---

## What stays the same

The moats compound across this evolution. Worth being explicit about which layers don't change.

**The rulebook.** Universal and channel-specific rules apply to every shot's image_prompt regardless of how the script is structured. The text-rendering rule, the eyeline rule, the gravity rule — they all keep working. New rules accumulate as new content categories surface new failure modes.

**The canon mechanism.** Tag substitution and recursive expansion works at every hierarchy level. Project canon, scene canon, channel base canon all merge with the same logic.

**The encapsulation discipline.** Image generation still lives in `generate_still`. Animation still lives in `animate_still`. TTS still lives in `_synthesize_chunk` (or its successor that handles multi-voice). External services still get swapped behind their interface functions.

**The channel config pattern.** `channel.json` grows new fields (multiple voice slots, format declarations, audio track lists) but the walk-up resolution and per-channel layering pattern is identical.

**The diagnose-and-bank failure discipline.** Every reshoot still becomes a candidate rule. Every category of failure still gets named and prevented universally.

The orchestration layer absorbs the new structural complexity; the discipline layer doesn't change at all.

---

## The audio architecture

Genuinely new and worth thinking about separately. Current pipeline mixes two tracks (narration plus music bed). Movie audio requires four to seven.

**Track 1 — Narration.** Single narrator voice (Victor for Final Hours, Reed for Success Coach, TBD for Channel 3). Plays over scenes that need an external voice. Channel 4+ dialogue-led drama may have no narrator at all.

**Track 2 — Dialogue.** Zero or more character voices, each speaking their assigned lines. Each character has a configured Inworld voice (or future TTS model that supports performance direction). Timing-wise, dialogue is positionally placed inside the shot it belongs to. The technical challenge: lip-sync between rendered character faces and TTS dialogue is currently unreliable; near-term workaround is keeping character faces in profile, in shadow, or at distance during dialogue lines (the *Hartley* technique applied to drama).

**Track 3 — Ambience.** Location-specific room tone. The kitchen morning quiet, the deck wind, the shed silence, the city traffic. Generated per scene, looped under the entire scene duration, cross-faded at scene transitions. Cheap to produce (15-second loops × N scenes), enormous contribution to "feels like cinema, not voiceover." Available on fal via ElevenLabs and others.

**Track 4 — Music.** Currently one bed under the whole video. Movie-mode: cue-driven music that responds to act and scene emotional registers. Multiple short cues triggered at scene boundaries, blended with crossfades. The music generator gets prompted per cue, not per project.

**Track 5 — Foley.** Footsteps, doors opening, glass breaking, ferret claws on wood. AI foley generation is improving (specialised models on fal exist as of 2026). Per-shot SFX list specifies which sounds happen and when. This is the layer that turns "AI cinematic video" into "feels like a real movie."

**Track 6 — Score (separate from cue music).** Themed musical motifs that recur across scenes — a character's theme, a place's theme, a recurring danger motif. Reusable across multiple shots within a project or even across multiple projects. Edge case for now; matters at feature length.

**Track 7 — Diegetic music.** Music that exists in the world of the film (the band playing on the Titanic deck, the gramophone in the parlour). Distinct from score because it's part of the scene's reality. Volume modulates with apparent distance from the source.

The mixer's job is to combine these tracks with the right levels, the right ducking (narration ducks under dialogue; dialogue ducks under nothing; music ducks under dialogue), and the right scene-boundary transitions.

For the near term — Channel 3 — Tracks 1, 3, and 4 are essential; Track 2 is occasional (one character speaks one line); Tracks 5-7 are nice-to-have. For full drama (Channel 4+), all seven are load-bearing.

---

## The genre matrix

Five distinct content formats, each requiring a different subset of features. The channel config declares which:

**Narrated documentary (Final Hours).** One narrator, atmospheric imagery, one music bed, occasional ambience. Variable shot durations helpful but not essential. Existing pipeline handles this already.

**Narrated literary adaptation (Channel 3).** One narrator (Reed register), character-driven imagery, scene-specific music cues, scene-specific ambience, occasional character close-ups during dialogue lines (no lip-sync, framing-driven). Variable shot durations *essential*. Layered audio essential.

**Narrative explainer (Success Coach).** One narrator (warm modern register), mixed cinematic + abstract imagery (notebooks, screens, objects), gentle music bed, minimal ambience. Variable shot durations valuable but not essential. Closer to documentary than to film.

**Dialogue-driven drama (future Channel N).** Multiple character voices, no narrator (or rare narrator interludes), cinematic coverage of conversations, full audio stack (dialogue + ambience + music + foley + sometimes diegetic). Variable shot durations essential. Lip-sync technology must mature before this is viable.

**Hybrid documentary-drama (theoretical).** A documentary that includes brief dramatised scenes — historical recreation where the figures briefly speak. The Hartley project leaned this way; never crossed into actual dialogue. Architecturally identical to drama with reduced dialogue density.

The same architecture supports all five. The channel config declares which subset of audio tracks, which shot duration policy, and which voice slots are active.

---

## What channel.json grows into

The config gets richer; the pattern stays the same.

```json
{
  "name": "channel_3_literary",
  "format": "narrated_literary",

  "voices": {
    "narrator": "Reed"
  },

  "shot_policy": {
    "default_duration": 7,
    "min_duration": 3,
    "max_duration": 25,
    "variable_duration_supported": true
  },

  "audio_tracks": ["narration", "music", "ambience"],

  "music_policy": {
    "mode": "per_scene_cues",
    "default_register": "controlled_literary"
  },

  "style_suffix": "...",

  "base_canon": {
    "edwardian_period": "..."
  }
}
```

`format` declares the genre, which determines defaults for everything else. A channel can override individual fields if its content has unusual needs.

The migration path for Final Hours and Success Coach is non-disruptive: they keep their current channel.json shape, get a default `format: "narrated_documentary"` or `"narrative_explainer"`, and the pipeline behaves identically to today. New channels (Channel 3 onward) declare richer configs from the start.

---

## The sequencing — when to build each layer

Five phases over the next 18-24 months, each unblocking specific content capabilities. None must happen on a calendar; each happens when content demands it.

**Phase 1 (now). Flat-beat narrated documentary.** Working. Final Hours and Success Coach ship on this. No changes needed.

**Phase 2 (next 4-8 weeks). Hierarchical scenes plus variable shot duration.** Add scenes-level structure to beat-scripts. Add per-shot explicit duration field. Update the assembler to honour explicit durations and fall back to even-spacing for any shot without one. Update `_load_beats_with_canon` to handle the new hierarchical format (and keep backward compatibility for flat lists). The minimum work needed for Channel 3 to launch cleanly. About 2-3 days of careful pipeline work plus testing.

**Phase 3 (3-6 months). Scene-level ambience tracks.** Add ambient audio generation per scene. The mixer learns to cross-fade ambience at scene boundaries. Channel 3 becomes meaningfully more cinematic. Final Hours can opt in retroactively if a video benefits. Inworld already supports the multi-track audio generation needed; the integration is mostly mixer work.

**Phase 4 (6-12 months). Per-scene music cues replacing single-bed music.** Music generator gets prompted per scene with the scene's emotional register. The mixer blends multi-cue music with cross-fades. Channel 3 videos with strong act structure benefit immediately.

**Phase 5 (9-15 months). Multi-voice TTS with character voice assignments.** Channel.json gets the `voices` dict with per-character voice IDs. The TTS layer routes each dialogue line to its assigned character voice. Lip-sync remains unsolved, so dialogue rendering uses framing tricks (profile, shadow, distance). Enables limited dialogue in Channel 3 and probes the territory for full drama.

**Phase 6 (12-24 months). Foley generation and per-shot SFX.** Per-shot SFX list gets generated via fal or ElevenLabs foley models. The mixer adds Track 5. Production quality crosses into "feels like a real movie" territory. Coincides with general AI video model maturity (video-native sequence generation eclipsing still-then-animate).

**Phase 7 (18-24 months). Full drama with lip-sync.** Either lip-sync technology has matured enough to render character speech directly, or video models like Veo / Sora generate dialogue sequences natively. Channel 4+ launches as full-dialogue drama. Project-level scripts now resemble real screenplays. The pipeline reaches "amateur movie production" territory the strategy doc envisaged.

The phases are sequential by *dependency*, not by *time*. Phase 2 must precede Phase 3; both must precede Phase 4. But each phase unlocks specific content that lets the next phase be designed properly based on real production needs rather than guesses.

---

## What this means for Channel 3 specifically

Channel 3 launches on Phase 2 architecture. The minimum requirements:

Hierarchical scenes plus variable shot duration (Phase 2). Without this, *Sredni Vashtar*'s final reveal doesn't work.

Optional but high-value if Phase 3 ships in time: scene-level ambience. The shed has a different ambient register from the kitchen. Even basic ambience makes the channel feel substantially more cinematic.

Music cues per scene (Phase 4) are nice-to-have for Channel 3 but not essential — a single restrained bed under the entire film works fine for these short stories.

Multi-voice (Phase 5) is needed if you want characters to speak their own dialogue (Saki's stories sometimes have one or two lines of dialogue). Without it, the narrator reads everything. Defensible; not ideal.

Channel 3 doesn't need Phases 6-7. Foley and lip-sync are luxuries for this genre. Literary adaptation is fundamentally narrator-led; the audience accepts the convention.

**So the practical Channel 3 launch readiness checklist:**

Phase 2 done. Final Hours and Success Coach untouched. Hetzner operational. Reviewer onboarded. Avatar problem resolved. Five Saki and James stories scripted in the new hierarchical format. First video (*Sredni Vashtar*) rendered, reviewed, polished, festival-ready.

That's all. Phase 3-7 add capability but don't gate launch.

---

## What this means for Final Hours and Success Coach

Phase 2 helps both channels even if they're not new-genre content. Specifically:

A held silence in Six Minutes (after Sarah names her number) can now be rendered as a 12-second shot rather than an averaged 5-second one. The dramatic beat survives the pipeline.

A long establishing shot at the opening of Final Hours videos — the empty Pompeii boathouse before the families arrive, the empty Anne Boleyn chamber before her women enter — can be held for 8-10 seconds instead of trimmed to the average. The emotional weight builds.

Climactic moments get longer holds. Hartley's violin lifting to his chin before the first note can be the 8-second moment it deserves rather than a 4-second slice.

The retrofit is gentle. Existing beat-scripts keep working. New videos opt into the hierarchy where it adds value. The same architecture serves both atmospheric documentary and narrative work; the channel chooses its register.

---

## Why this design is right

Three honest justifications.

**It maps to how humans actually think about film.** Screenwriters think in acts, scenes, and beats. Directors think in scenes and shots. Editors think in shots and cuts. The current flat-grid forces a unit of thinking — "beats" — that's natural for atmospheric content but unnatural for narrative. Restoring the hierarchy restores the natural creative process. The architecture stops fighting the creator.

**It absorbs new capabilities without breaking old content.** Every phase is additive. Every channel keeps working as new features ship. The pipeline architecture stays compatible with the work already done. This is the same encapsulation discipline that let the Seedream-to-Flux swap happen as a one-line config change — applied to the hierarchy itself.

**It positions the pipeline for the long horizon.** Five years from now, when a 90-minute AI feature is being rendered on a Hetzner VPS overnight, the project-level script that gets fed into the pipeline looks substantially like a real screenplay. Acts. Scenes. Shots. Characters. Dialogue. Audio cues. The architecture you decide on now determines whether you've spent five years building toward that or built five years of work that has to be redone for it.

The Altman principle one more time: don't design for the model, design for continuous improvement in the models. Architecture extends that to *don't design for the genre, design for continuous expansion in the genres*. The pipeline that ships Channel 3 launches an architecture that's already capable of Channel 4, 5, and 6, even though those don't exist yet.

---

## What to bank now

The decision itself, captured. Three concrete commitments:

The next pipeline architectural work is the Phase 2 hierarchy migration, not anything else. Not multi-voice. Not foley. Not lip-sync. Phase 2 first, because it unlocks Channel 3, and Channel 3 is the test that the architecture is real.

The schema above is the target shape. When implementing Phase 2, this is what `_load_beats_with_canon` evolves to accept. The naming might tighten; the structure shouldn't.

The phases are dependency-ordered, not date-ordered. Phase 3 doesn't begin until Phase 2 is shipped, tested, and stable. Phase 4 doesn't begin until Phase 3 is shipped. Adopting them in order prevents the half-built mess that comes from trying to do everything at once.

When the moment comes to actually build Phase 2 — probably alongside the IP-Adapter integration in the same architectural sprint — this document is the working brief. Re-read it then. Update it as decisions reveal themselves through implementation. The principles survive even if the specifics tighten.

That's the design. Not for this week, but for the years ahead.
