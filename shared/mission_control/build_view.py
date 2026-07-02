"""
Mission Control — Phase 0 foundation.

Two pure functions over files on disk, plus a self-test CLI. NO server, NO UI.
The point of Phase 0 is to PROVE the per-beat record is correct against real
data (the-daughters) before any web layer exists.

  resolve_paths(channel, slug)  -> canonical paths (kills the proj_paths double-bite)
  build_beats_view(channel, slug) -> the per-beat record the storyboard renders from

Run on the box from repo root:
  python shared/mission_control/build_view.py --channel sacred_dawn --project the-daughters
  python shared/mission_control/build_view.py --channel sacred_dawn --project the-daughters --beat 6
  python shared/mission_control/build_view.py --channel sacred_dawn --project the-daughters --check

Confirmed ground truth (recon, 12 June, the-daughters / 184 beats):
  beats_full.json = {header, beats}; beat.index is 0-BASED; fields:
     index, mode, component, payload, narration, found_line, visual,
     face_hold, silence_after, warnings
  durations.json  = dict keyed by STRING beat index ("6") ->
     {duration, audio_start, source, frames, mode, component}
  _index.json     = dict "engine_shot(1-based str)" -> beat_index(0-based int), e.g. {"7":6}
  storyboard.json = flat list; shot.index is 1-BASED (engine shot number); fields:
     index, narration, image_prompt, motion_prompt   (NO audio_duration)
  voiceover.mp3   lives at the PROJECT ROOT (not under modea/) -- the assemble bug
  stills -> <project>/modea/stills/shot_NNN.png   (NNN = engine shot, 3-digit)
  clips  -> <project>/modea/clips/shot_NNN.mp4

THE HARD RULE: assets join beat->engine_shot through _index.json (inverted),
never by computing index+1. durations join by str(beat_index). Position-join is
a lie the moment a Mode B beat or a dropped TTS beat exists.
"""

from __future__ import annotations
import json
import argparse
from pathlib import Path


# --------------------------------------------------------------------------
# 1. The single path resolver
# --------------------------------------------------------------------------
# Given channel + project slug, return every canonical path. This is the ONE
# resolver orchestrate / finish / the coordinator should all share. It knows the
# real layout (confirmed by recon): voiceover + durations + _index + beats live
# at the PROJECT ROOT; stills/clips/storyboard live under modea/. That split is
# exactly what the proj_paths() double-bite got wrong.

def _repo_root() -> Path:
    # shared/mission_control/build_view.py -> repo root is two parents up.
    return Path(__file__).resolve().parents[2]


def resolve_paths(channel: str, slug: str, repo_root: Path | None = None) -> dict:
    """channel='sacred_dawn', slug='the-daughters' -> canonical paths.

    Channel folder resolution mirrors the orchestrator: try the name as given,
    then swap underscores<->hyphens, use whichever has a channel.json.
    """
    root = repo_root or _repo_root()

    # Resolve the channel FOLDER (hyphen/underscore tolerant, like the orchestrator).
    candidates = [channel, channel.replace("_", "-"), channel.replace("-", "_")]
    chan_dir = None
    for c in candidates:
        d = root / c
        if (d / "channel.json").is_file():
            chan_dir = d
            break
    if chan_dir is None:
        # Fall back to the hyphen form so error messages point somewhere sane.
        chan_dir = root / channel.replace("_", "-")

    project = chan_dir / "projects" / slug
    modea = project / "modea"

    return {
        "repo_root":   root,
        "channel_dir": chan_dir,
        "channel_json": chan_dir / "channel.json",
        "project":     project,
        "modea":       modea,
        # project-root artifacts
        "beats_full":  project / "beats_full.json",
        "beats":       project / "beats.json",
        "durations":   project / "durations.json",
        "index_map":   project / "_index.json",
        "voiceover":   project / "voiceover.mp3",      # NOTE: root, not modea/
        "voiceover_json": project / "voiceover.json",
        "look_json":   project / "look.json",          # may not exist
        # modea artifacts
        "storyboard":  modea / "storyboard.json",
        "stills_dir":  modea / "stills",
        "clips_dir":   modea / "clips",
        "final_video": modea / "final_video.mp4",
    }


# --------------------------------------------------------------------------
# 2. Small helpers
# --------------------------------------------------------------------------

def _load_json(p: Path):
    if not p.is_file():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _invert_index_map(index_map: dict | None) -> dict[int, int]:
    """_index.json is engine_shot(str,1-based) -> beat_index(int,0-based).
    Return the inverse the storyboard actually needs: beat_index -> engine_shot(int).
    """
    out: dict[int, int] = {}
    if not index_map:
        return out
    for engine_shot_str, beat_idx in index_map.items():
        out[int(beat_idx)] = int(engine_shot_str)
    return out


def _resolve_look(paths: dict) -> str:
    """channel-then-project look resolution, reported as a human string."""
    look = _load_json(paths["look_json"])
    if look and look.get("look"):
        return f"{look['look']} (project look.json override)"
    chan = _load_json(paths["channel_json"]) or {}
    if chan.get("style_suffix"):
        return "channel default (channel.json style_suffix)"
    return "unresolved"


# --------------------------------------------------------------------------
# 3. build_beats_view — the per-beat record the storyboard renders from
# --------------------------------------------------------------------------

def build_beats_view(channel: str, slug: str, repo_root: Path | None = None) -> dict:
    """Produce the job-record `beats[]` (plus header + paths) from real artifacts.

    Every asset is joined through _index.json (inverted); durations join by
    str(beat_index); storyboard joins beat->engine_shot through the same map.
    Mode B beats with a parent are folded into the parent's overlays[]; standalone
    Mode B beats remain top-level rows. Pure-Mode-A projects produce empty overlays.
    """
    paths = resolve_paths(channel, slug, repo_root)

    bf = _load_json(paths["beats_full"])
    if bf is None:
        raise SystemExit(f"missing beats_full.json: {paths['beats_full']}")
    header = bf.get("header", {}) if isinstance(bf, dict) else {}
    beats = bf.get("beats") if isinstance(bf, dict) else bf

    durations = _load_json(paths["durations"]) or {}
    index_map = _load_json(paths["index_map"])
    beat_to_shot = _invert_index_map(index_map)     # beat_index -> engine_shot(int)

    storyboard = _load_json(paths["storyboard"]) or []
    # storyboard shot.index is 1-based engine shot; key it that way for lookup.
    shot_by_engine = {int(s["index"]): s for s in storyboard if "index" in s}

    look_resolved = _resolve_look(paths)
    # PATCH_FIXBTN_APPLIED: channel text-to-image model name for the render-path label.
    _channel_model = (_load_json(paths["project"].parent.parent / "channel.json")
                      or {}).get("image_model", "flux")

    # ---- First pass: turn each script beat into a row record (by beat index) ----
    rows: dict[int, dict] = {}
    for b in beats:
        bi = int(b["index"])
        dur = durations.get(str(bi), {})  # durations keyed by string beat index
        engine_shot = beat_to_shot.get(bi)  # may be None if not mapped

        still_path = clip_path = None
        still_exists = clip_exists = False
        if engine_shot is not None:
            still_rel = f"modea/stills/shot_{engine_shot:03d}.png"
            clip_rel = f"modea/clips/shot_{engine_shot:03d}.mp4"
            still_path = still_rel
            clip_path = clip_rel
            still_exists = (paths["project"] / still_rel).is_file()
            clip_exists = (paths["project"] / clip_rel).is_file()

        # The prompt that ACTUALLY rendered (storyboard, post-restill) vs authored (beats.visual).
        shot = shot_by_engine.get(engine_shot) if engine_shot is not None else None
        rendered_prompt = (shot or {}).get("image_prompt")
        motion_prompt = (shot or {}).get("motion_prompt")

        # PATCH_FIXBTN_APPLIED: truthful per-beat render-path label for the MC UI.
        # States the PATH the beat takes (reference /edit vs channel text model),
        # not runtime fallbacks (those aren't recorded anywhere yet).
        _refs = (shot or {}).get("_reference_images") or []
        render_path = (f"NB2 /edit \u00b7 {len(_refs)} ref" if _refs
                       else f"{_channel_model} \u00b7 text")

        # stage: best-effort from what's on disk
        if clip_exists:
            stage = "animated"
        elif still_exists:
            stage = "still"
        else:
            stage = "authored"

        rows[bi] = {
            "index": bi,                       # 0-based spine / join key
            "mode": b.get("mode"),
            "component": b.get("component"),
            "stage": stage,
            "narration": b.get("narration", ""),
            "visual_authored": b.get("visual", ""),       # from beats_full (authored)
            "visual_rendered": rendered_prompt,            # from storyboard (what rendered)
            "motion_prompt": motion_prompt,
            "found_line": b.get("found_line", ""),
            "face_hold": b.get("face_hold", False),
            "duration_s": dur.get("duration"),
            "audio_start": dur.get("audio_start"),
            "duration_source": dur.get("source"),
            "look_resolved": look_resolved,
            "render_path": render_path,
            "payload": b.get("payload", {}),
            "warnings": list(b.get("warnings", [])),
            "overlays": [],                    # filled in pass 2 for Mode B children
            "_parent_index": b.get("parent_index"),  # internal: set if this is a B child
            "assets": {
                "still": {"path": still_path, "engine_shot": engine_shot,
                          "via": "_index.json", "exists": still_exists},
                "clip":  {"path": clip_path, "engine_shot": engine_shot,
                          "via": "_index.json", "exists": clip_exists},
                "audio": {"slice": None, "duration_s": dur.get("duration")},  # slice later
            },
            "source_files": {
                "narration": "beats_full.json",
                "visual_authored": "beats_full.json",
                "visual_rendered": "storyboard.json",
                "duration": "durations.json",
                "index_map": "_index.json",
            },
        }

    # ---- Second pass: fold Mode B children into their parent's overlays[] ----
    # A Mode B beat with parent_index set (parse-time inferred, §5.3) becomes an
    # overlay on its parent, NOT a top-level row. overlay_start/end resolution
    # against Whisper is deferred to when Mode B projects actually exist; here we
    # record the link + the parent's window so the schema is populated correctly.
    top_level: list[dict] = []
    for bi in sorted(rows):
        r = rows[bi]
        parent = r.pop("_parent_index", None)
        if r["mode"] == "B" and parent is not None and int(parent) in rows:
            p = rows[int(parent)]
            p_start = p.get("audio_start")
            p_dur = p.get("duration_s")
            p["overlays"].append({
                "child_index": bi,
                "component": r["component"],
                "phrase": r["narration"],          # the carded phrase = the B beat's words
                "payload": r["payload"],
                # overlay_start/end: Whisper-scoped within parent window — deferred.
                "overlay_start": None,
                "overlay_end": None,
                "parent_window": [p_start,
                                  (p_start + p_dur) if (p_start is not None and p_dur) else None],
                "resolved": False,                 # flips true when Whisper scoping lands
            })
        else:
            # strip the internal key on standalone rows too
            r.pop("_parent_index", None) if "_parent_index" in r else None
            top_level.append(r)

    has_mode_b = any(r["mode"] == "B" for r in rows.values())

    return {
        "channel": channel,
        "project": slug,
        "header": header,
        "has_mode_b": has_mode_b,             # pure-Mode-A -> page shows zero B chrome
        "look_resolved": look_resolved,
        "beat_count": len(beats),
        "row_count": len(top_level),          # < beat_count when B-children fold in
        "paths": {k: str(v) for k, v in paths.items()},
        "beats": top_level,
    }


# --------------------------------------------------------------------------
# 4. Self-test CLI — prove it against real data before any server exists
# --------------------------------------------------------------------------

def _check(view: dict):
    """Loud sanity checks against the alignment invariants."""
    print("\n==================== ALIGNMENT CHECK ====================")
    beats = view["beats"]
    problems = []

    # 1. every Mode A beat that's 'animated' must have BOTH still+clip resolving on disk
    for r in beats:
        if r["mode"] == "A" and r["stage"] == "animated":
            if not r["assets"]["still"]["exists"]:
                problems.append(f"beat {r['index']}: animated but still missing")
            if not r["assets"]["clip"]["exists"]:
                problems.append(f"beat {r['index']}: animated but clip missing")
            if r["assets"]["still"]["engine_shot"] is None:
                problems.append(f"beat {r['index']}: no engine_shot mapping (NOT in _index.json)")

    # 2. durations present for every beat
    no_dur = [r["index"] for r in beats if r["duration_s"] is None]
    if no_dur:
        problems.append(f"{len(no_dur)} beats with no duration: {no_dur[:8]}")

    # 3. authored vs rendered prompt drift (informational, not a problem)
    drift = [r["index"] for r in beats
             if r["visual_rendered"] and r["visual_authored"]
             and r["visual_rendered"].strip() != r["visual_authored"].strip()]

    print(f"beats: {view['beat_count']}  rows: {view['row_count']}  "
          f"has_mode_b: {view['has_mode_b']}")
    print(f"look: {view['look_resolved']}")
    print(f"prompt drift (rendered != authored): {len(drift)} beats"
          f"{' e.g. ' + str(drift[:5]) if drift else ''}")
    if problems:
        print(f"\n  !! {len(problems)} PROBLEM(S):")
        for p in problems[:20]:
            print("   -", p)
    else:
        print("\n  OK — every animated beat joins to a still+clip through _index.json,")
        print("       every beat has a measured duration. Alignment holds.")
    print("========================================================\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--beat", type=int, default=None,
                    help="dump one beat's full record")
    ap.add_argument("--check", action="store_true",
                    help="run alignment sanity checks")
    args = ap.parse_args()

    view = build_beats_view(args.channel, args.project)

    if args.beat is not None:
        match = [r for r in view["beats"] if r["index"] == args.beat]
        if not match:
            print(f"beat {args.beat} not a top-level row "
                  f"(may be a Mode B child folded into a parent's overlays)")
        else:
            print(json.dumps(match[0], indent=2, ensure_ascii=False))
        return

    # default: a compact head + the check
    print(f"channel={view['channel']}  project={view['project']}  "
          f"beats={view['beat_count']}  rows={view['row_count']}  "
          f"has_mode_b={view['has_mode_b']}")
    print(f"header.title: {view['header'].get('title','(none)')}")
    print("\nfirst 3 rows (compact):")
    for r in view["beats"][:3]:
        a = r["assets"]
        print(f"  beat {r['index']:>3} [{r['mode']}] {r['stage']:<9} "
              f"{(r['duration_s'] or 0):>5.2f}s  "
              f"shot={a['still']['engine_shot']}  "
              f"still={'Y' if a['still']['exists'] else '-'} "
              f"clip={'Y' if a['clip']['exists'] else '-'}  "
              f"| {r['narration'][:50]}")

    if args.check:
        _check(view)


if __name__ == "__main__":
    main()
