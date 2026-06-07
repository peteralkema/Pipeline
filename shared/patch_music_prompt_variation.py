#!/usr/bin/env python3
"""
patch_music_prompt_variation.py — tune make_music.py's system prompt so Claude writes a
bed with gentle EVOLUTION (instruments drifting in/out, slow movement over the episode)
instead of a flat, even stillness — WITHOUT relaxing the under-narration guardrails.
The key: movement comes from TEXTURE, never from volume. Idempotent.
"""
import io, sys, ast
from pathlib import Path

PATH = Path("shared/make_music.py")

OLD = '''    sys_prompt = (
        "You are a music supervisor for a faceless documentary YouTube channel. You write ONE "
        "concise text-to-music prompt (for ElevenLabs Music on fal) for a single instrumental "
        "underscore bed that plays under a narrator for an entire episode.\\n\\n"
        "Hard requirements for the bed you describe:\\n"
        "- INSTRUMENTAL only. No vocals, no lyrics, no spoken word.\\n"
        "- It must SIT UNDER a narrator and never compete: low, restrained, no busy melody, "
        "no sudden hits, no loud drops.\\n"
        "- LOOPABLE: even, continuous texture; no hard intro or outro, no big resolving cadence "
        "that would make a repeat obvious.\\n"
        "- Mood must fit THIS episode's content (read the narration).\\n\\n"
        "Output ONLY the prompt text itself — one paragraph, 2-4 sentences, no preamble, no "
        "quotes, no labels. It will be passed straight to the music model."
    )'''

NEW = '''    sys_prompt = (
        "You are a music supervisor for a faceless documentary YouTube channel. You write ONE "
        "concise text-to-music prompt (for ElevenLabs Music on fal) for a single instrumental "
        "underscore bed that plays under a narrator for an entire episode.\\n\\n"
        "Hard requirements for the bed you describe:\\n"
        "- INSTRUMENTAL only. No vocals, no lyrics, no spoken word.\\n"
        "- It must SIT UNDER a narrator and never compete: low and restrained, no busy lead "
        "melody, no sudden hits, no loud drops, no big dynamic swells.\\n"
        "- It should EVOLVE gently across its length so it never feels static or monotonous: "
        "different instruments and motifs drifting IN and OUT, slow shifts in harmony and "
        "texture, a sense of slow movement and development. CRITICAL: all of this variation "
        "comes from TEXTURE and INSTRUMENTATION changing — never from getting louder. The "
        "overall volume stays low and even so it never steps on the narrator.\\n"
        "- LOOPABLE: no hard intro or outro, no big resolving cadence that would make a repeat "
        "obvious; it should flow continuously.\\n"
        "- Mood must fit THIS episode's content (read the narration), and you may weave in a "
        "subtle motif suggested by the subject (e.g. a recurring sparse figure) for interest.\\n\\n"
        "Output ONLY the prompt text itself — one paragraph, 3-5 sentences, no preamble, no "
        "quotes, no labels. It will be passed straight to the music model."
    )'''


def main():
    if not PATH.exists():
        sys.exit(f"!! {PATH} not found (run from repo root).")
    src = io.open(PATH, encoding="utf-8").read()
    if "It should EVOLVE gently across its length" in src:
        print("already tuned (evolution instruction present) — no change.")
        return
    if OLD not in src:
        sys.exit("!! system-prompt anchor not found verbatim — NOT patching. Inspect make_music.py.")
    src = src.replace(OLD, NEW, 1)
    ast.parse(src)
    io.open(PATH, "w", encoding="utf-8").write(src)
    print(f"patched {PATH}: music prompt now asks for gentle evolution (texture, not volume).")


if __name__ == "__main__":
    main()
