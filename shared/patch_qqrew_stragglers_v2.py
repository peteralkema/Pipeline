# patch_qqrew_stragglers_v2.py
# Cleanup pass for the 8 straggler beats the first wide-hardening missed
# (false-positive "no people" / "human" substring matches).
#
# Two VERIFIED allow-lists (every beat eyeballed against its rendered still):
#   EMPTY  -> flat-cel directive + atmospheric strip + no-humans guard
#   FIGURE -> flat-cel directive + atmospheric strip, figures PRESERVED, NO guard
#
# Idempotent (skips already-hardened), backup + JSON-validate before write.
# Run AFTER patch_qqrew_wide_prompts.py. Operates on storyboard.json.
import json, sys, shutil, datetime, pathlib

PROJECT = "qqrew/projects/pregnancy1"
SB = pathlib.Path(PROJECT) / "storyboard.json"

# Verified by eye against rendered stills + prompt text this session.
EMPTY  = [4, 23, 84, 125]        # landscape / object / diagram -> guard OK
FIGURE = [99, 144, 157, 161]     # intended silhouettes/figures/crowd -> NO guard

FLAT = ("flat 2D cartoon illustration, bold uniform dark ink outlines, "
        "large areas of flat solid color, hard cel-shadow edges, no gradients, "
        "no soft shading, no glossy highlights, no bloom, no depth of field, "
        "matte, graphic and bold, NOT photorealistic, NOT 3d render, NOT painterly")

NOHUMANS = "empty scene, no people, no humans, no figures, no person"

SENTINEL = "bold uniform dark ink outlines"  # already hardened -> skip

# Cinematic-prior trigger words to neutralize (figures-safe: does NOT remove
# 'figures'/'silhouettes'/'gathering' themselves, only the lighting/atmosphere).
STRIP = {
    "soft wide of a deep-past camp at golden hour": "wide of a camp",
    "soft wide of a deep-past gathering": "wide of a gathering of people indoors",
    "soft wide of faint figures gathered close around one": "wide of faint figures gathered close around one person",
    "deep-past dawn landscape": "plain landscape",
    "golden hour": "flat daylight",
    "warm light": "flat even light",
    "firelight": "a simple warm light shape",
    "soft wide": "wide shot",
    "soft ": "",
    "crew-absent": "",
    "animated flat illustration": "",
}

def strip_body(prompt):
    body = prompt
    for k, v in STRIP.items():
        body = body.replace(k, v)
    while "  " in body:
        body = body.replace("  ", " ")
    body = body.replace(" ,", ",").replace(",,", ",").strip().strip(",").strip()
    return body

def harden_empty(prompt):
    return f"{FLAT}. {strip_body(prompt)}, {NOHUMANS}"

def harden_figure(prompt):
    # flat directive + stripped body, figures kept, NO no-humans guard
    return f"{FLAT}. {strip_body(prompt)}"

def main():
    if not SB.exists():
        print("ERR storyboard not found:", SB); sys.exit(1)
    data = json.loads(SB.read_text())
    n = len(data)

    for idx in EMPTY + FIGURE:
        if idx < 1 or idx > n:
            print(f"ERR beat {idx} out of range (1..{n})"); sys.exit(1)

    did_empty, did_figure, already = [], [], []

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = SB.with_suffix(f".json.pre_stragglers_{ts}")
    shutil.copy(SB, bak)

    for idx in EMPTY:
        p = data[idx-1]["image_prompt"]
        if SENTINEL in p:
            already.append(idx); continue
        data[idx-1]["image_prompt"] = harden_empty(p)
        did_empty.append(idx)

    for idx in FIGURE:
        p = data[idx-1]["image_prompt"]
        if SENTINEL in p:
            already.append(idx); continue
        data[idx-1]["image_prompt"] = harden_figure(p)
        did_figure.append(idx)

    out = json.dumps(data, indent=2)
    json.loads(out)  # validate before write
    SB.write_text(out)

    print(f"OK hardened {len(did_empty)} EMPTY + {len(did_figure)} FIGURE stragglers")
    print("EMPTY (guard applied):", did_empty or "none")
    print("FIGURE (figures kept, no guard):", did_figure or "none")
    print("skipped already-hardened:", already or "none")
    print("backup:", bak.name)
    print("\nSAMPLE empty (beat 4):")
    print(data[3]["image_prompt"][:300])
    print("\nSAMPLE figure (beat 99 - silhouettes must remain):")
    print(data[98]["image_prompt"][:300])

if __name__ == "__main__":
    main()
