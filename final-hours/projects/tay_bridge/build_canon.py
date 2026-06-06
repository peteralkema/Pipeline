import json, os, sys

PROJ = "projects/tay_bridge"
OUT  = "beat-scripts/tay_bridge_beats.json"

# Prefer the discipline-audited storyboard; fall back to raw with a warning.
audited = os.path.join(PROJ, "storyboard_audited.json")
raw     = os.path.join(PROJ, "storyboard.json")
if os.path.exists(audited):
    src = audited
elif os.path.exists(raw):
    src = raw
    print("WARNING: storyboard_audited.json not found — using raw storyboard.json.")
    print("         Face-never-resolved discipline NOT applied. Consider running the audit first.")
else:
    sys.exit("No storyboard found. Run storyboard generation first.")

print(f"Reading: {src}")
with open(src) as f:
    data = json.load(f)

# storyboard is a flat list of shots; audited may wrap it — handle both
shots = data["shots"] if isinstance(data, dict) and "shots" in data else data
if isinstance(data, dict) and "beats" in data:
    shots = data["beats"]

CANON = {
    "bridge_night": ("The Tay Bridge on the night of 28 December 1879 — a long, low single-track "
        "wrought-iron lattice railway bridge crossing a wide black firth, the central 'high girders' "
        "forming a tall rectangular iron cage where the line runs about seventy feet above the water. "
        "Violent gale, driving rain, deep night, only faint signal lights and distant shore lights. "
        "Victorian wrought-iron engineering, NOT a modern steel or concrete bridge. Bleak, atmospheric, cinematic."),
    "carriage": ("Interior of a North British Railway passenger carriage, 1879 — wooden-panelled "
        "compartment lit by a single dim oil lamp, rain streaming down black windows, night beyond. "
        "Any passengers present only as dark wrapped shapes seen from behind or in deep shadow, faces never "
        "resolved. Period-accurate Victorian railway interior, no modern fittings. Warm lamplight against cold dark."),
    "signal_box": ("A small Victorian railway signal box at the south end of the Tay Bridge, 1879 — cramped "
        "timber cabin with a single oil lamp and signal levers, storm hammering the windows. Any men present "
        "seen only from behind or in silhouette against the lamp, faces never resolved. Night, gale outside. "
        "Period-accurate, no modern equipment."),
    "firth": ("The Firth of Tay at night, 28 December 1879 — a wide expanse of black wind-driven storm water "
        "with whitecaps, the iron bridge above, the scattered lights of Dundee distant on the far shore. "
        "Bleak, cold, cinematic, no modern elements."),
}

# keyword routing — specific interiors first, then water, bridge as default
def assign(prompt):
    p = prompt.lower()
    if any(k in p for k in ["signal box", "signalbox", "barclay", "watt", "lever", "cabin"]):
        return "signal_box"
    if any(k in p for k in ["carriage", "compartment", "passenger", "lamplit", "lamp-lit", "interior", "inside the"]):
        return "carriage"
    if any(k in p for k in ["river", "firth", "water", "riverbed", "wave", "diver", "drown", "below"]):
        return "firth"
    return "bridge_night"  # the bridge is the dominant recurring subject

beats, counts = [], {}
for s in shots:
    ip = s.get("image_prompt", "")
    tok = assign(ip)
    counts[tok] = counts.get(tok, 0) + 1
    b = dict(s)
    b["image_prompt"] = "{" + tok + "} " + ip   # canon token prepended; expands at render
    beats.append(b)

out = {"canon": CANON, "beats": beats}
with open(OUT, "w") as f:
    json.dump(out, f, indent=2)

print(f"\nWrote {len(beats)} beats -> {OUT}")
print("Canon assignment distribution:")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k:14s} {v}")
print("\nReview the distribution above. If a shot is in the wrong scene, edit the token in the JSON before generating stills.")
