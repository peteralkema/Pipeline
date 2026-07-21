# -*- coding: utf-8 -*-
# patch_deep_depth.py -- adds a foreground anchor to 15 empty-wide {deep} beats.
# Keyed on each beat's UNIQUE narration fragment so the same-phenomenon duplicates
# elsewhere are never touched. Idempotent: re-running finds the already-new phen and skips.
import re, io, sys

PATH = "beats_data.py"
# (unique narration fragment) -> new phenomenon (full, starts with {deep})
EDITS = {
 "no one can agree how that happened":
   "{deep} a lone ancient fishing boat with one small figure adrift in the near foreground, the vast bright sea stretching past them to the horizon, wide, hard clean light, foreground boat against immense water",
 "a corruption in the water, and a judgment that missed it":  # b3 c16 stays; use c13
   None,
 "the sea does not drown what already lives in it":  # b3 c14 stays empty (payoff pause)
   None,
 "But a flood judges the land":  # b3 c13 target via its narration
   "{deep} a drowned sailor's pale hand and forearm drifting in the near foreground, the calm fathomless deep falling away below, medium, cold-blue radiance, foreground body against the depths",
 "the same figure waits on almost every map":  # b4 c2
   "{deep} an ancient ship's prow and a lone lookout figure cutting the near-left foreground, the vast bright sea running past to the horizon, wide, hard clean light, foreground prow against immense water",
 "a hundred agreeing is something else entirely":  # b4 c32
   "{deep} two fishermen hauling a dripping net over a gunwale in the near foreground, the vast open ocean beyond under a huge bright sky, medium wide, hard light, foreground figures against immense water",
 "Before we go further, the skeptic deserves his say":  # b5 c1
   "{deep} a lone sailor standing at an ancient prow in the near foreground, back to us, gazing over a vast bright sea holding perfectly still, wide, hard clean light, foreground figure against immense water",
 "It is a serious answer - and it explains the frame":  # b5 c7
   "{deep} a helmsman's weathered hands gripping a steering-oar in the near foreground, the vast open ocean beyond under a bright hard sky, medium, hard light, foreground hands against immense water",
 "and it needs no watchers and no giants at all":  # b5 c16
   "{deep} a diver caught mid-plunge breaking the bright surface in the near foreground, the vast ocean stretching to the horizon beyond, wide, hard clean light, foreground figure against immense water",
 "It is an elegant answer, and an honest one":  # b5 c23
   "{deep} a lone figure treading water far below the bright surface seen from above, tiny in the near foreground, the deep held in perfect stillness around him, high angle, cold-blue and luminous, foreground swimmer against the depths",
 "only watch where each is strong, and where each strains":  # b5 c30
   "{deep} an ancient boat drifting with one still figure aboard in the near-right foreground, the open ocean stretching even and immense beyond, wide, hard clean light, foreground boat against the sea",
 "For the ancient writer, the sea was never just water":  # b6 c25
   "{deep} a dark kelp forest rising through cold-blue water in the near foreground, the vast open deep opening beyond, medium, hard clean light, foreground weed against immense water",
 "a knowledge we have lost almost entirely":  # b6 c32
   "{deep} a floating broken mast and tangled spar drifting across the near foreground, the vast sea running to a bright far horizon beyond, wide, hard light, foreground wreck against immense water",
 "back to the deep, and to what the flood never touched":  # b6 c36
   "{deep} a turning shoal of silver fish catching light in the near foreground, the calm untouched deep falling away beneath, medium, cold-blue radiance, foreground life against the depths",
 "it names no verse that follows her into the deep":  # b7 c16
   "{deep} a sunken anchor-stone and a trailing rope descending through the near foreground, the fathomless deep opening downward past it, wide looking down, immense cold-blue glow, foreground line into the dark",
 "Why would that stand among the great promises":  # b8 c10
   "{deep} a lone fisherman silhouetted in an ancient boat in the near foreground, the vast dark sea stretching one last time under a bright sky, wide, hard light, foreground figure against immense water",
 "it was the deep, the abyss, the place order never reached":  # b8 c11
   "{deep} a single figure sinking slowly into the deep, arms out, small in the near foreground, the fathomless deep opening downward past him, wide looking down, immense cold-blue glow, foreground body into the abyss",
}

src = io.open(PATH, encoding="utf-8").read()
lines = src.split("\n")
applied = skipped = 0
for i, line in enumerate(lines):
    for frag, newphen in EDITS.items():
        if newphen is None:
            continue
        if frag in line and '"{deep}' in line:
            if newphen in line:
                skipped += 1
                break
            # replace only the quoted phenomenon field (starts with {deep})
            newline, n = re.subn(r'"\{deep\}[^"]*"', '"' + newphen.replace('\\', '\\\\') + '"', line, count=1)
            if n == 1:
                lines[i] = newline
                applied += 1
            break

out = "\n".join(lines)
# byte-compile sanity before write
compile(out, PATH, "exec")
io.open(PATH, "w", encoding="utf-8").write(out)
print(f"applied={applied}  skipped(idempotent)={skipped}")
