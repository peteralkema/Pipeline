#!/usr/bin/env python3
"""
build_beat_durations.py — Step 4c / Piece 2c: real per-beat durations for ALL 62 beats.

Reuses the EXISTING, proven align_with_whisper.py rather than reinventing alignment.
That aligner takes a {"beats":[{"narration":...}]} scaffold + a Whisper voiceover.json,
matches narration words to measured word-timestamps, and writes audio_start +
audio_duration into each beat. It is general over beat count (the docstring even
anticipates this dual-mode use). So 2c is a WRAPPER:

  1. From 2a's manifest, build a scaffold of ONLY the spoken beats (the aligner
     aligns by narration words; silent beats have none and would collapse).
     Scaffold preserves original beat index in each entry.
  2. Run align_with_whisper.py against that scaffold + the Whisper voiceover.json.
  3. Read the aligned durations back; merge in the 23 silent beats' default_hold
     from the manifest, keyed by original beat index.
  4. Emit durations.json: {beat_index: {duration, source}} for ALL 62 beats,
     in order — the real timing that replaces estimate_frames()'s word-count guess.

Run AFTER:
  - build_audio_script.py  (writes <out>.manifest.json + <out>.txt)
  - generate the VO        (2b: voiceover.mp3)
  - whisper the VO         (writes voiceover.json with --word_timestamps True)

Usage (from channel root, venv active):
  python ../shared/build_beat_durations.py \
      --manifest /tmp/ep1_audio.manifest.json \
      --whisper projects/ep1-the-promise/voiceover.json \
      --out projects/ep1-the-promise/durations.json \
      --aligner ../shared/align_with_whisper.py
"""
import os, sys, json, argparse, subprocess, tempfile

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="2a's <out>.manifest.json")
    ap.add_argument("--whisper", required=True, help="Whisper voiceover.json (word timestamps)")
    ap.add_argument("--out", required=True, help="durations.json to write")
    ap.add_argument("--aligner", default="../shared/align_with_whisper.py",
                    help="path to the existing align_with_whisper.py")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    manifest = json.load(open(args.manifest, encoding="utf-8"))

    # 1. scaffold of spoken beats only, preserving original index.
    spoken = [m for m in manifest if m.get("spoken")]
    scaffold = {"beats": [{"_beat_index": m["index"], "narration": m["text"]} for m in spoken]}
    scaf_path = tempfile.NamedTemporaryFile("w", suffix="_scaffold.json", delete=False, encoding="utf-8")
    json.dump(scaffold, scaf_path, ensure_ascii=False, indent=2); scaf_path.close()

    # 2. run the EXISTING aligner against scaffold + whisper. It writes durations
    #    back INTO the scaffold file (in place).
    cmd = [sys.executable, args.aligner, "--storyboard", scaf_path.name, "--whisper", args.whisper]
    print(f"running aligner: {' '.join(cmd)}\n")
    r = subprocess.run(cmd, text=True)
    if r.returncode != 0:
        print(f"!! aligner failed (exit {r.returncode}). durations.json NOT written.", file=sys.stderr)
        os.unlink(scaf_path.name)
        sys.exit(1)

    # 3. read aligned scaffold back; build index -> duration for spoken beats.
    aligned = json.load(open(scaf_path.name, encoding="utf-8"))
    aligned_beats = aligned["beats"] if isinstance(aligned, dict) else aligned
    spoken_dur = {}
    for entry in aligned_beats:
        idx = entry["_beat_index"]
        spoken_dur[idx] = {
            "duration": round(float(entry.get("audio_duration", 0.0)), 3),
            "audio_start": round(float(entry.get("audio_start", 0.0)), 3),
            "source": "whisper",
        }
    os.unlink(scaf_path.name)

    # 4. merge: every beat in manifest order. spoken -> measured; silent -> default_hold.
    durations = {}
    for m in manifest:
        idx = m["index"]
        if m.get("spoken"):
            d = spoken_dur.get(idx, {"duration": 0.0, "source": "whisper_MISSING"})
        else:
            d = {"duration": round(float(m.get("default_hold", 2.5)), 3), "source": "silent_hold"}
        d["frames"] = round(d["duration"] * args.fps)
        d["mode"] = m["mode"]
        d["component"] = m.get("component")
        durations[str(idx)] = d

    json.dump(durations, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    total = sum(d["duration"] for d in durations.values())
    n_w = sum(1 for d in durations.values() if d["source"] == "whisper")
    n_s = sum(1 for d in durations.values() if d["source"] == "silent_hold")
    n_miss = sum(1 for d in durations.values() if d["source"] == "whisper_MISSING")
    print(f"\n=== per-beat durations ===")
    print(f"wrote {args.out}")
    print(f"{len(durations)} beats: {n_w} whisper-measured, {n_s} silent-hold"
          + (f", {n_miss} MISSING" if n_miss else ""))
    print(f"total episode length: {total:.1f}s ({total/60:.2f} min)")
    print(f"\nfirst 10 beats:")
    for i in range(min(10, len(manifest))):
        idx = str(manifest[i]["index"])
        d = durations[idx]
        tag = d["mode"] if d["mode"]=="A" else f"B:{d['component']}"
        print(f"  [{idx:>2}] ({tag:<18}) {d['duration']:5.2f}s  {d['frames']:>3}f  [{d['source']}]")
    if n_miss:
        print("\n!! some spoken beats got no Whisper match — alignment drift; check word counts.")

if __name__ == "__main__":
    main()
