#!/usr/bin/env python3
"""
modea_beats.py - Step 4b: translate Synthetic tagged beats -> Final Hours beat-script.

The recreation_pipeline.py `stills --beats` path already accepts a pre-written
shot list (no Claude slicing): a JSON of {narration, image_prompt, motion_prompt},
optionally wrapped in {canon, beats}. Our Synthetic Mode A beats ARE that, already
segmented one-beat-one-shot. So 4b is a TRANSLATOR, not new engine code:

    beats.json (all 62, A+B)
        |
        |  keep only mode == "A"
        v
    synthetic_modeA_beats.json   ({beats:[{narration,image_prompt,motion_prompt}]})
        |
        v
    recreation_pipeline.py stills --beats synthetic_modeA_beats.json --project <p>
        (-> storyboard.json -> stills -> review gate -> Kling clips: shot_001..shot_NNN)

Mapping (one beat = one shot, decided):
    beat.visual     -> image_prompt   (the scene direction IS the prompt)
    beat.narration  -> narration      (verbatim; the engine saves concatenated)
    (none)          -> motion_prompt  (safe default; face-hold beats get a
                                       near-static motion so the engine's
                                       animate step doesn't warp the face)

CRITICAL — the index map. The engine renders Mode A clips CONTIGUOUSLY as
shot_001, shot_002, ... It has no idea beats 27, 38, etc. are Mode B holes.
So we MUST emit a mapping {engine_shot_index -> original_beat_index} alongside
the beat-script, or the dual-mode assemble can't put clips back in true order.
That map is written to synthetic_modeA_index.json and is the keystone for 4c.

Usage:
    python3 modea_beats.py beats.json --out synthetic_modeA_beats.json
"""
import os, sys, json, argparse

DEFAULT_MOTION = "Slow, subtle atmospheric motion. Drifting light, faint air. No fast movement, no camera shake."
FACEHOLD_MOTION = ("Almost completely still. The face does NOT move or speak — hold it like a "
                   "photograph. Only faint ambient motion in the environment (dust, light). "
                   "No lip movement, no head turn.")

def translate(beats):
    """Return (beat_script_dict, index_map). index_map[engine_shot_index] = original beat index."""
    shot_beats = []
    index_map = {}
    engine_idx = 0
    for b in beats:
        if b.get("mode") != "A":
            continue
        engine_idx += 1
        visual = (b.get("visual") or "").strip()
        # strip our authoring markers that aren't part of the scene description
        for marker in ["\u2b50", "FACE-HOLD #1.", "FACE-HOLD #2.", "FACE-HOLD #1", "FACE-HOLD #2"]:
            visual = visual.replace(marker, "").strip()
        narration = (b.get("narration") or "").strip()
        # motion omitted when not face-hold: leave normal beats with NO
        # motion_prompt so cmd_stills falls through to the channel's
        # default_motion (channel.json). Only a real override (face-hold) is
        # written here; the channel owns the default register otherwise.
        shot = {
            "narration": narration,
            "image_prompt": visual,
        }
        # Precedence: authored MOTION: line > face-hold default > blank (inherit
        # channel default_motion). An authored motion is a deliberate per-beat
        # override (TIGHTEN/HOLD/SWING); only when absent do we fall back to the
        # face-hold default or leave it blank for the channel default to win.
        authored_motion = (b.get("motion") or "").strip()
        if authored_motion:
            shot["motion_prompt"] = authored_motion
        elif b.get("face_hold"):
            shot["motion_prompt"] = FACEHOLD_MOTION
        # Directed Ken-Burns floor (29 Jul): carry the `move` column through
        # untouched when present (push|pull|crane|settle|static). Beats with
        # no `move` key -- every Synthetic-Press-schema beat, this
        # translator's original input -- are unaffected: b.get returns None,
        # guarded to "", falsy, skipped. Purely additive.
        _move = (b.get("move") or "").strip()
        if _move:
            shot["move"] = _move
        shot_beats.append(shot)
        index_map[engine_idx] = b["index"]
    return {"beats": shot_beats}, index_map

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--out", default="synthetic_modeA_beats.json")
    ap.add_argument("--map", default=None, help="index map output (default: <out stem>_index.json)")
    ap.add_argument("--channel-config", default=None,
                    help="channel.json; if it has a `canon` block it is emitted alongside "
                         "the beats so the engine can expand {tokens}. Optional: without "
                         "it the output is exactly as before.")
    args = ap.parse_args()

    beats = json.load(open(args.beats_json, encoding="utf-8"))
    beat_script, index_map = translate(beats)

    # [canon] reference-mode channels carry their canon block through to the engine
    # A {token} in a VISUAL attaches the character's reference images AND expands into
    # the prompt. _expand_canon raises on an unknown tag, so a reference-mode channel
    # MUST ship its canon. Absent a config (or a canon block) this is a no-op.
    if args.channel_config:
        try:
            _cfg = json.load(open(args.channel_config, encoding="utf-8"))
        except Exception as _e:
            raise SystemExit(f"--channel-config could not be read ({args.channel_config}): {_e}")
        _canon = _cfg.get("canon") or {}
        if _canon:
            _refmap = _cfg.get("reference_map") or {}
            _missing = sorted(set(_refmap) - set(_canon))
            if _missing:
                raise SystemExit(
                    f"reference_map token(s) with no canon entry: {_missing}. "
                    "Every ref token must expand, or the engine halts at _expand_canon."
                )
            beat_script = {"canon": _canon, "beats": beat_script["beats"]}
            print(f"canon block attached: {sorted(_canon.keys())}")

    map_path = args.map or (os.path.splitext(args.out)[0] + "_index.json")
    json.dump(beat_script, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.dump(index_map, open(map_path, "w", encoding="utf-8"), indent=2)

    n_a = len(beat_script["beats"])
    n_total = len(beats)
    print(f"\n=== Mode A translation ===")
    print(f"{n_total} beats in -> {n_a} Mode A shots out  ({n_total - n_a} Mode B beats skipped)\n")
    print(f"wrote {args.out}")
    print(f"wrote {map_path}  (engine shot index -> original beat index)\n")
    # show the first few + the index map so the contiguity is visible
    print("first 5 shots (engine sees these as shot_001..):")
    for i, s in enumerate(beat_script["beats"][:5], 1):
        face = "  [face-hold motion]" if s.get("motion_prompt") == FACEHOLD_MOTION else ""
        print(f"  shot_{i:03d} (beat {index_map[i]:02d}){face}")
        print(f"     img: {s['image_prompt'][:74]}")
        print(f"     narr: {s['narration'][:74]}{'...' if len(s['narration'])>74 else ''}")
    print(f"\nindex map (first 12): {dict(list(index_map.items())[:12])}")
    # sanity: every face-hold beat carried its motion
    fh = [index_map[i] for i,s in enumerate(beat_script['beats'],1) if s.get('motion_prompt')==FACEHOLD_MOTION]
    print(f"face-hold shots -> original beats {fh}")

if __name__ == "__main__":
    main()
