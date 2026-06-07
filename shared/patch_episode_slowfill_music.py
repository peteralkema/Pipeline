#!/usr/bin/env python3
"""
patch_episode_slowfill_music.py — two convergence fixes to assemble_episode.py.

Same in-place, idempotent style as patch_animate_only.py. Run from the repo root:
    python shared/patch_episode_slowfill_music.py

Edits:
  1. SLOW-TO-FILL: when a clip is shorter than its beat slot, slow it (setpts) to
     fill instead of freezing the last frame (tpad clone). Cinematic Mode A reads
     better slowed than frozen. Guards native<=0 (falls back to a held frame).
  2. MUSIC MUX: mix a music bed under the VO at the calibrated levels
     (VOICE 1.15 / MUSIC 0.07), loop-to-cover. Defensive: only if <project>/music.mp3
     (or --music FILE) exists; --no-music skips. No music file -> behaves exactly
     as before. Adds --music / --no-music flags.

Idempotent + self-verifying (ast-parse). Backs up to assemble_episode.py.pre_slowfill_music.
"""
import sys, ast, shutil
from pathlib import Path

TARGET = Path(__file__).parent / "assemble_episode.py"

# ── Edit A: constants (after COLDOPEN_COLOR) ───────────────────────────────
CONST_ANCHOR = 'COLDOPEN_COLOR = "0x000000"\n'
CONST_INSERT = (
    'COLDOPEN_COLOR = "0x000000"\n'
    'VOICE_LEVEL = 1.15   # VO full (calibrated)\n'
    'MUSIC_LEVEL = 0.07   # music bed sits low under narration (Jamendo-calibrated)\n'
)

# ── Edit B: slow-to-fill (replace the freeze branch in make_video_segment) ──
FREEZE_ANCHOR = (
    '    else:\n'
    '        # clip shorter than the slot -> hold the last frame to fill (tpad clone)\n'
    '        vf = f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur - native:.3f}"\n'
    '        run(["ffmpeg", "-y", "-i", str(src),\n'
    '             "-vf", vf, "-t", f"{dur:.3f}",\n'
    '             "-c:v", "libx264", "-preset", "medium", "-crf", "18",\n'
    '             "-pix_fmt", "yuv420p", "-an", str(dst)], f"hold video beat {beat[\'index\']}")\n'
)
SLOWFILL_INSERT = (
    '    else:\n'
    '        # clip shorter than the slot -> SLOW it to fill (slow-to-fill, not freeze).\n'
    '        # setpts factor > 1 slows playback; the fps filter (in scale_pad) resamples\n'
    '        # to constant FPS so it stays smooth. Guard native<=0 (probe failed).\n'
    '        if native <= 0:\n'
    '            vf = f"{scale_pad},tpad=stop_mode=clone:stop_duration={dur:.3f}"\n'
    '        else:\n'
    '            factor = dur / native\n'
    '            if factor > 2.5:\n'
    '                print(f"     beat {beat[\'index\']}: slow-fill {native:.1f}s -> {dur:.1f}s "\n'
    '                      f"({factor:.1f}x — heavy stretch; candidate for more/shorter beats)")\n'
    '            vf = f"setpts=PTS*{factor:.6f},{scale_pad}"\n'
    '        run(["ffmpeg", "-y", "-i", str(src),\n'
    '             "-vf", vf, "-t", f"{dur:.3f}",\n'
    '             "-c:v", "libx264", "-preset", "medium", "-crf", "18",\n'
    '             "-pix_fmt", "yuv420p", "-an", str(dst)], f"slow-fill video beat {beat[\'index\']}")\n'
)

# ── Edit C: argparse flags (after --clips) ─────────────────────────────────
ARG_ANCHOR = '    ap.add_argument("--clips", default=None, help="clips dir (default: <project>/clips)")\n'
ARG_INSERT = (
    '    ap.add_argument("--clips", default=None, help="clips dir (default: <project>/clips)")\n'
    '    ap.add_argument("--music", default=None, help="music bed mp3 (default: <project>/music.mp3 if present)")\n'
    '    ap.add_argument("--no-music", action="store_true", help="assemble without any music bed")\n'
)

# ── Edit D: music mux (replace the final mux block in main) ────────────────
MUX_ANCHOR = (
    '        print("  muxing...")\n'
    '        run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(full_a),\n'
    '             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",\n'
    '             "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out)], "final mux")\n'
)
MUX_INSERT = (
    '        print("  muxing...")\n'
    '        # music bed: <project>/music.mp3 by default, or --music FILE; --no-music skips.\n'
    '        # Defensive: no music file present -> behaves exactly as the VO-only mux below.\n'
    '        music_path = None\n'
    '        if not args.no_music:\n'
    '            cand = Path(args.music).expanduser() if args.music else (project / "music.mp3")\n'
    '            if cand.exists():\n'
    '                music_path = cand\n'
    '            elif args.music:\n'
    '                print(f"  !! --music {cand} not found; assembling without music")\n'
    '        if music_path:\n'
    '            import math as _math\n'
    '            print(f"  music bed: {music_path.name} (VOICE {VOICE_LEVEL} / MUSIC {MUSIC_LEVEL})")\n'
    '            ad = probe(full_a); md = probe(music_path)\n'
    '            music_src = music_path\n'
    '            if md > 0 and md < ad:\n'
    '                reps = _math.ceil(ad / md)\n'
    '                mlist = work / "mlist.txt"\n'
    '                mlist.write_text("".join(f"file \'{music_path.resolve()}\'\\n" for _ in range(reps)))\n'
    '                looped = work / "music_looped.m4a"\n'
    '                run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),\n'
    '                     "-c", "copy", str(looped)], "loop music")\n'
    '                music_src = looped\n'
    '            run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(full_a), "-i", str(music_src),\n'
    '                 "-filter_complex",\n'
    '                 f"[1:a]volume={VOICE_LEVEL}[v];[2:a]volume={MUSIC_LEVEL}[m];"\n'
    '                 f"[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]",\n'
    '                 "-map", "0:v:0", "-map", "[a]",\n'
    '                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],\n'
    '                "mux video+vo+music")\n'
    '        else:\n'
    '            run(["ffmpeg", "-y", "-i", str(silent_v), "-i", str(full_a),\n'
    '                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",\n'
    '                 "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out)], "final mux")\n'
)

EDITS = [
    ("VOICE_LEVEL", CONST_ANCHOR, CONST_INSERT, "constants (VOICE_LEVEL/MUSIC_LEVEL)"),
    ("slow-fill video beat", FREEZE_ANCHOR, SLOWFILL_INSERT, "slow-to-fill branch"),
    ('"--music"', ARG_ANCHOR, ARG_INSERT, "--music/--no-music flags"),
    ("mux video+vo+music", MUX_ANCHOR, MUX_INSERT, "music mux block"),
]


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found. Run from repo root: python shared/patch_episode_slowfill_music.py")
    src = TARGET.read_text()
    original = src
    applied = []
    for marker, anchor, insert, label in EDITS:
        if marker in src:
            print(f"skip: {label} already present.")
            continue
        if anchor not in src:
            sys.exit(f"FAIL: anchor for '{label}' not found — assemble_episode.py changed. Nothing written.")
        if src.count(anchor) != 1:
            sys.exit(f"FAIL: anchor for '{label}' is not unique ({src.count(anchor)} matches). Nothing written.")
        src = src.replace(anchor, insert, 1)
        applied.append(label)

    if src == original:
        print("Already fully patched — no changes. No-op.")
        return

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"FAIL: patched source does not parse ({e}). Nothing written.")

    backup = TARGET.with_suffix(".py.pre_slowfill_music")
    if not backup.exists():
        shutil.copy2(TARGET, backup)
        print(f"Backed up original -> {backup.name}")
    TARGET.write_text(src)
    print(f"OK wrote {TARGET.name} (compiles). Applied: {', '.join(applied)}")


if __name__ == "__main__":
    main()
