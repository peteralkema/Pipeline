#!/usr/bin/env python3
"""
extract_narration.py — Convert script.md into clean narration .txt

Strips markdown headers, italic stage directions, frontmatter, closing card
title-card text, and trailing meta sections (word count, audit notes, etc.).
Outputs pure spoken prose suitable for feeding to recreation_pipeline.py.

Usage:
    python ../shared/extract_narration.py projects/mary_celeste/script-draft1.md
    
    # Output written to: projects/mary_celeste/mary_celeste_script.txt
    # (derives the project name and output filename from the input path)

Or with explicit output path:
    python ../shared/extract_narration.py <input.md> <output.txt>
"""

import re
import sys
from pathlib import Path


# Section headers that mark the end of narration content
# Anything from these headers onward is meta and gets stripped
TERMINAL_SECTIONS = {
    "word count check",
    "word count",
    "self-audit notes",
    "self-audit",
    "what needs review",
    "production notes",
    "estimated runtime breakdown",
    "estimated runtime",
    "runtime breakdown",
    "decision log",
    "notes",
}


def extract_narration(markdown_text: str) -> str:
    """Extract spoken prose from a script.md, returning clean narration."""
    lines = markdown_text.split("\n")
    narration_blocks = []
    current_paragraph = []
    in_narration = False
    in_closing_card = False

    for line in lines:
        stripped = line.strip()

        # Detect terminal sections (## Word count, ## Self-audit, etc.)
        if stripped.startswith("##"):
            header_text = stripped.lstrip("#").strip().lower()
            # Strip any "—" or "-" suffix from beat headers
            header_normalized = header_text.split("—")[0].split("-")[0].strip()
            
            # Check if this is a terminal meta section
            if any(term in header_text for term in TERMINAL_SECTIONS):
                # Flush any pending paragraph and stop
                if current_paragraph:
                    narration_blocks.append(" ".join(current_paragraph))
                    current_paragraph = []
                break
            
            # Check if this is a Beat header (narration starts/continues)
            if "beat" in header_normalized:
                in_narration = True
                in_closing_card = False
                # Flush previous paragraph
                if current_paragraph:
                    narration_blocks.append(" ".join(current_paragraph))
                    current_paragraph = []
                continue
            
            # Any other ## header — skip silently
            if current_paragraph:
                narration_blocks.append(" ".join(current_paragraph))
                current_paragraph = []
            continue

        # Skip top-level # headers (title, etc.) — they're not narration
        if stripped.startswith("#"):
            continue

        # If we haven't hit the first Beat yet, skip everything
        if not in_narration:
            continue

        # Detect closing card sections — italic lines after "Closing card" marker
        if "closing card" in stripped.lower() and stripped.startswith("*"):
            # Flush current paragraph
            if current_paragraph:
                narration_blocks.append(" ".join(current_paragraph))
                current_paragraph = []
            in_closing_card = True
            continue

        # Skip italic-only lines (stage directions, voice/runtime notes, closing card dates)
        # These are either italic with asterisks at start AND end, or pure italic blocks
        if stripped.startswith("*") and stripped.endswith("*") and stripped.count("*") >= 2:
            continue

        # Skip horizontal rules
        if stripped == "---":
            # End of closing card section if we were in one
            in_closing_card = False
            continue

        # Skip empty lines but use them as paragraph breaks
        if not stripped:
            if current_paragraph:
                narration_blocks.append(" ".join(current_paragraph))
                current_paragraph = []
            continue

        # If we're in a closing card block, skip the content
        if in_closing_card:
            continue

        # Normal prose line — add to current paragraph
        # Strip any inline markdown formatting (bold, italic mid-line)
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", line.strip())  # bold
        cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)  # italic
        cleaned = re.sub(r"`(.+?)`", r"\1", cleaned)  # inline code
        current_paragraph.append(cleaned)

    # Flush final paragraph
    if current_paragraph:
        narration_blocks.append(" ".join(current_paragraph))

    # Join paragraphs with double newlines for readability
    narration = "\n\n".join(narration_blocks)
    
    # Collapse multiple spaces
    narration = re.sub(r" +", " ", narration)
    
    return narration.strip() + "\n"


def derive_output_path(input_path: Path) -> Path:
    """Given projects/mary_celeste/script-draft1.md, return projects/mary_celeste/mary_celeste_script.txt"""
    project_dir = input_path.parent
    project_name = project_dir.name
    return project_dir / f"{project_name}_script.txt"


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_narration.py <input.md> [output.txt]", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = derive_output_path(input_path)

    markdown_text = input_path.read_text(encoding="utf-8")
    narration = extract_narration(markdown_text)
    output_path.write_text(narration, encoding="utf-8")

    word_count = len(narration.split())
    estimated_runtime_seconds = word_count / 135 * 60  # 135 wpm baseline
    minutes = int(estimated_runtime_seconds // 60)
    seconds = int(estimated_runtime_seconds % 60)

    print(f"Extracted {word_count} words → {output_path}")
    print(f"Estimated runtime at 135 wpm: {minutes}:{seconds:02d}")
    print(f"Estimated actual runtime after Inworld ~13% pace acceleration: "
          f"{int(estimated_runtime_seconds * 0.87 // 60)}:"
          f"{int(estimated_runtime_seconds * 0.87 % 60):02d}")


if __name__ == "__main__":
    main()
