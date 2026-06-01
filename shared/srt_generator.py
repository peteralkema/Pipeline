"""
srt_generator.py — Build subtitles.srt from a project's storyboard.

Reads pompeii_v1/storyboard.json (the per-shot narration slices) and the
actual durations of pompeii_v1/clips/shot_NNN.mp4 (since Kling can deliver
slightly different lengths than the requested 5s), and emits a standard SRT
file with timestamps that match the assembled video.

This is timed per-SHOT, not per-word — YouTube reads it for accessibility and
discovery, both of which work fine at shot-level granularity.
"""

import json
import subprocess
from pathlib import Path


def _ffprobe_seconds(video_path: Path) -> float:
    """Get the real duration of a clip in seconds (Kling clips vary slightly)."""
    result = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         str(video_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True,
    )
    return float(result.stdout.strip())


def _fmt_srt_timestamp(seconds: float) -> str:
    """SRT format: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        ms = 0
        s += 1
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _wrap_caption(text: str, max_chars: int = 42) -> str:
    """
    Soft-wrap caption lines so YouTube renders them on at most 2 lines.
    SRT itself doesn't care, but viewers do.
    """
    text = text.strip().replace("\n", " ")
    if len(text) <= max_chars:
        return text
    # Split at nearest space to the midpoint
    mid = len(text) // 2
    left = text.rfind(" ", 0, mid + 10)
    right = text.find(" ", mid - 10)
    split = left if left != -1 else right
    if split == -1 or split == 0:
        return text   # one long word, accept it
    return text[:split].strip() + "\n" + text[split:].strip()


def generate_srt(project_dir: Path) -> Path:
    """
    Build captions whose timing MATCHES the assembled video.

    The assembler plays every clip for z = narration_duration / num_clips seconds
    (even spacing). So the SRT must use the SAME model: each shot's caption spans
    one z-length slot, accumulated uniformly. Using native clip durations here
    (the old bug) made captions drift progressively later than the speech, because
    native clips are ~5s but they actually PLAY at z (~3.72s).
    """
    project = Path(project_dir).expanduser()
    storyboard = json.loads((project / "storyboard.json").read_text())
    clips_dir  = project / "clips"
    voice_path = project / "voiceover.mp3"
    out_path   = project / "subtitles.srt"

    n = len(storyboard)
    if n == 0:
        raise SystemExit("Empty storyboard — nothing to caption.")

    # The master clock is the narration length, same as the assembler.
    voice_seconds = _ffprobe_seconds(voice_path)
    z = voice_seconds / n   # seconds each shot is shown — matches assemble()

    lines = []
    idx = 0
    for i, shot in enumerate(storyboard):
        start = i * z
        end   = (i + 1) * z

        text = _wrap_caption(shot.get("narration", "").strip())
        if not text:
            continue   # skip silent shots if any

        idx += 1
        lines.append(f"{idx}")
        lines.append(f"{_fmt_srt_timestamp(start)} --> {_fmt_srt_timestamp(end)}")
        lines.append(text)
        lines.append("")   # blank line between entries

    out_path.write_text("\n".join(lines))
    return out_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 srt_generator.py <project_dir>")
    path = generate_srt(Path(sys.argv[1]))
    print(f"OK SRT written -> {path}")
