# patch_qqrew_wide_prompts.py
# Hardens TRULY-EMPTY character-free beats in a QQrew storyboard against flux
# cinematic-prior drift. Auto-skips social/crowd beats. Idempotent, anchor-verified,
# backup + JSON-validate before write. Re-render the reported beats with --force after.
import json, sys, shutil, datetime, pathlib

PROJECT = "qqrew/projects/pregnancy1"
SB = pathlib.Path(PROJECT) / "storyboard.json"

# Hard flat-cel directive that LEADS every hardened prompt (the real suffix language,
# not the weak inline "animated flat illustration" tag).
FLAT = ("flat 2D cartoon illustration, bold uniform dark ink outlines, "
        "large areas of flat solid color, hard cel-shadow edges, no gradients, "
        "no soft shading, no glossy highlights, no bloom, no depth of field, "
        "matte, graphic and bold, NOT photorealistic, NOT 3d render, NOT painterly")

# Explicit no-humans guard (flux-legible, unlike "crew-absent").
NOHUMANS = "empty scene, no people, no humans, no figures, no person"

SENTINEL = "bold uniform dark ink outlines"  # presence => already hardened, skip

# Cinematic-prior trigger words to neutralize in the body text.
STRIP = {
    "warm light raking across the letters": "even flat lighting on the letters",
    "warm light raking across": "even flat lighting across",
    "one steady warm light in a dark landscape": "a single simple light shape on a plain landscape",
    "soft golden light": "flat daylight",
    "soft final wide": "wide shot",
    "soft wide": "wide shot",
    "warm light": "flat even light",
    "deep-past dawn landscape": "plain landscape",
    "deep-past horizon": "plain horizon",
    "dark void": "plain dark flat background",
    "crew-absent": "",                  # replaced by NOHUMANS guard
    "animated flat illustration": "",   # weak tag; replaced by FLAT lead
    "soft ": "",
}

# A beat is a CHARACTER beat (leave alone) if any of these appear.
CHAR_TOKENS = ["blonde", "feminine", "woman", "boy", "man", "child",
               "person", "figure", "people"]

# A beat is a CROWD/SOCIAL beat (leave alone -- must NOT get the no-humans guard)
# even if it lacks an explicit character token. These are the ambiguous ones
# like 161's "deep-past gathering".
CROWD_TOKENS = ["gathering", "crowd", "audience", "group", "family",
                "feast", "dinner", "table", "congregation", "village",
                "market", "everyone", "celebration", "party"]

def classify(p):
    pl = p.lower()
    if any(t in pl for t in CHAR_TOKENS):
        return "character"
    if any(t in pl for t in CROWD_TOKENS):
        return "crowd"
    return "empty"

def harden(prompt):
    body = prompt
    for k, v in STRIP.items():
        body = body.replace(k, v)
    while "  " in body:
        body = body.replace("  ", " ")
    body = body.replace(" ,", ",").replace(",,", ",").strip().strip(",").strip()
    return f"{FLAT}. {body}, {NOHUMANS}"

def main():
    if not SB.exists():
        print("ERR storyboard not found:", SB); sys.exit(1)

    data = json.loads(SB.read_text())

    targets, skip_char, skip_crowd, skip_done = [], [], [], []
    for idx, beat in enumerate(data):
        p = beat.get("image_prompt", "")
        if SENTINEL in p:
            skip_done.append(idx + 1); continue
        kind = classify(p)
        if kind == "character":
            skip_char.append(idx + 1)
        elif kind == "crowd":
            skip_crowd.append(idx + 1)
        else:
            targets.append(idx)

    if not targets:
        print("No un-hardened empty beats found. Nothing to do.")
        print("Already hardened:", skip_done or "none")
        return

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = SB.with_suffix(f".json.pre_widepatch_{ts}")
    shutil.copy(SB, bak)

    for idx in targets:
        data[idx]["image_prompt"] = harden(data[idx]["image_prompt"])

    out = json.dumps(data, indent=2)
    json.loads(out)  # validate round-trip before writing
    SB.write_text(out)

    print(f"OK hardened {len(targets)} EMPTY beats")
    print("hardened beat numbers:", [i + 1 for i in targets])
    print("skipped CHARACTER beats (untouched):", len(skip_char))
    print("skipped CROWD/social beats (untouched):", skip_crowd or "none")
    print("skipped already-hardened:", skip_done or "none")
    print("backup:", bak.name)
    print("\nSAMPLE hardened prompt (first target):")
    print(data[targets[0]]["image_prompt"][:320])
    print("\nNext: re-render ONLY these beats with --force, then re-check the spread.")

if __name__ == "__main__":
    main()
