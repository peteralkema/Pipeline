#!/usr/bin/env python3
"""
patch_music_dir.py — add a --music-dir (random-N + crossfade + loop) path to
assemble_episode.py, feeding the EXISTING voice+music mux unchanged.

Design (Peter's spec):
  - a per-channel folder of tracks (e.g. prehistoric-disasters/music/*.mp3)
  - pick N random tracks (default 3)
  - crossfade the joins (acrossfade, default 2s) so transitions don't jar
  - loop the crossfaded sequence to cover the voiceover duration
  - hand the result to the SAME amix mux at VOICE_LEVEL / MUSIC_LEVEL (untouched)

It builds a single `music_bed.m4a` in the work dir, then sets music_path to it so
the existing `if music_path:` block muxes it exactly as it muxes a single bed today.
The single-file --music path and --no-music path are both untouched.

New args:  --music-dir DIR   --music-tracks N   --music-crossfade SECONDS
Sentinel: 'def _build_music_bed'.  Backs up to .pre_musicdir. Idempotent.

Run on LAPTOP:  python3 shared/patch_music_dir.py
"""
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "assemble_episode.py"
SENTINEL = "def _build_music_bed"

# 1) the builder fn + its imports — injected just above the main() resolution of music.
HELPER = '''
def _build_music_bed(music_dir, voice_dur, work, n_tracks, crossfade_s, run_fn, probe_fn):
    """Pick n random tracks from music_dir, crossfade the joins, loop to >= voice_dur.
    Returns a Path to the bed (m4a) or None if the dir has no usable tracks.
    run_fn/probe_fn are the module's existing run() and probe() helpers."""
    import random as _random, math as _math
    md = Path(music_dir).expanduser()
    tracks = sorted([p for p in md.glob("*.mp3")] + [p for p in md.glob("*.m4a")]
                    + [p for p in md.glob("*.wav")])
    if not tracks:
        print(f"  !! --music-dir {md} has no audio files; assembling without music")
        return None
    # pick n (or all, if fewer than n exist), in random order
    n = max(1, min(n_tracks, len(tracks)))
    picked = _random.sample(tracks, n)
    print(f"  music-dir: {md.name}/  picked {n} of {len(tracks)} -> "
          + ", ".join(p.name for p in picked))

    # 1) crossfade-chain the picked tracks into one sequence
    if len(picked) == 1:
        seq = picked[0]
    else:
        seq = work / "music_seq.m4a"
        cur = picked[0]
        for k, nxt in enumerate(picked[1:], start=1):
            out = work / f"music_xf_{k}.m4a"
            run_fn(["ffmpeg", "-y", "-i", str(cur), "-i", str(nxt),
                    "-filter_complex",
                    f"[0][1]acrossfade=d={crossfade_s}:c1=tri:c2=tri[a]",
                    "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out)],
                   f"crossfade music {k}")
            cur = out
        seq = cur

    seq_dur = probe_fn(seq)
    if seq_dur <= 0:
        print("  !! music sequence has zero duration; assembling without music")
        return None

    # 2) loop the crossfaded sequence to cover the voiceover
    if seq_dur >= voice_dur:
        return seq
    reps = _math.ceil(voice_dur / seq_dur)
    mlist = work / "music_seq_list.txt"
    mlist.write_text("".join(f"file '{Path(seq).resolve()}'\\n" for _ in range(reps)))
    looped = work / "music_bed.m4a"
    run_fn(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(mlist),
            "-c", "copy", str(looped)], "loop music bed")
    return looped


'''

ANCHOR_HELPER = "def main():"   # inject helper just above main()

# 2) new CLI args — added right after the --no-music arg line
ANCHOR_ARGS = '''    ap.add_argument("--no-music", action="store_true", help="assemble without any music bed")'''
NEW_ARGS = '''    ap.add_argument("--no-music", action="store_true", help="assemble without any music bed")
    ap.add_argument("--music-dir", default=None,
                    help="folder of tracks: pick N random, crossfade, loop to fill (overrides --music)")
    ap.add_argument("--music-tracks", type=int, default=3, help="how many random tracks to cycle (default 3)")
    ap.add_argument("--music-crossfade", type=float, default=2.0, help="crossfade seconds between tracks (default 2)")'''

# 3) resolution: build the bed from --music-dir BEFORE the existing single-file logic.
ANCHOR_RESOLVE = '''        music_path = None
        if not args.no_music:
            cand = Path(args.music).expanduser() if args.music else (project / "music.mp3")
            if cand.exists():
                music_path = cand
            elif args.music:
                print(f"  !! --music {cand} not found; assembling without music")'''
NEW_RESOLVE = '''        music_path = None
        if not args.no_music:
            if args.music_dir:
                music_path = _build_music_bed(
                    args.music_dir, voice_dur, work,
                    args.music_tracks, args.music_crossfade, run, probe)
            else:
                cand = Path(args.music).expanduser() if args.music else (project / "music.mp3")
                if cand.exists():
                    music_path = cand
                elif args.music:
                    print(f"  !! --music {cand} not found; assembling without music")'''


def main():
    if not TARGET.exists():
        sys.exit(f"FAIL: {TARGET} not found.")
    text = TARGET.read_text()
    if SENTINEL in text:
        print(f"OK: already patched ('{SENTINEL}' present).")
        return

    for label, anchor in (("HELPER", ANCHOR_HELPER), ("ARGS", ANCHOR_ARGS),
                          ("RESOLVE", ANCHOR_RESOLVE)):
        if text.count(anchor) != 1:
            sys.exit(f"FAIL: {label} anchor found {text.count(anchor)} times (expected 1) — refusing.")

    new = text.replace(ANCHOR_HELPER, HELPER + ANCHOR_HELPER, 1)
    new = new.replace(ANCHOR_ARGS, NEW_ARGS, 1)
    new = new.replace(ANCHOR_RESOLVE, NEW_RESOLVE, 1)

    if new == text or SENTINEL not in new:
        sys.exit("FAIL: edit produced no change — aborting.")

    backup = TARGET.with_suffix(TARGET.suffix + ".pre_musicdir")
    if not backup.exists():
        backup.write_text(text)
    TARGET.write_text(new)
    print(f"OK: patched {TARGET.name} (backup: {backup.name}).")
    print("    Verify:  grep -n '_build_music_bed\\|music-dir' shared/assemble_episode.py")


if __name__ == "__main__":
    main()
