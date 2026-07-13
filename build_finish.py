#!/usr/bin/env python3
"""Assemble a Kling finish-project from picked stills. RUN ON THE BOX from ~/Pipeline.

For each montage: copies the 40 chosen shot_NNN.png out of the 160-render stills
folder into a fresh finish project, renamed shot_001..040 in beat order; writes a
40-entry storyboard.json with PER-BEAT motion prompts (assigned by shot type); and
sets render_policy.json {"kling_count": 40}. Then: finish --kling-count 40.

No re-rendering. Image-to-video off the exact frames you picked.

Usage:
  python3 build_finish.py revelation
  python3 build_finish.py catastrophes
"""
import json, sys, shutil, pathlib

# ---- motion vocabulary ----
PUSH   = "slow deliberate push-in, camera easing forward, natural realistic motion, subtle momentum, stable and steady, dramatic atmosphere"
PULL   = "slow pull-back revealing scale, camera easing outward, natural realistic motion, subtle momentum, stable and steady, epic atmosphere"
CRANE  = "slow crane-up, camera rising, natural realistic motion, subtle momentum, stable and steady, towering scale, dramatic atmosphere"
SETTLE = "very slow gentle drift downward and settle, near-locked camera, minimal movement, natural realistic motion, quiet still atmosphere"
LOCKED = "near-locked static camera, almost no camera movement, only ambient motion of smoke dust or water, minimal movement, stable, quiet still atmosphere"
ORBIT  = "very slow subtle orbit, gentle arc, natural realistic motion, minimal movement, stable and steady, dramatic atmosphere"

CONFIG = {
 "revelation": {
   "src": "scripture-on-screen/projects/revelation-3min",
   "dst": "scripture-on-screen/projects/revelation-3min-finish",
   "picks": {1:3,2:8,3:11,4:15,5:18,6:22,7:25,8:31,9:33,10:40,11:43,12:48,13:52,14:53,15:60,
             16:64,17:65,18:69,19:74,20:79,21:84,22:86,23:89,24:93,25:98,26:104,27:105,28:109,
             29:114,30:118,31:123,32:126,33:130,34:133,35:140,36:141,37:148,38:149,39:153,40:157},
   # motion per beat (1..40), by scene type
   "motion": {1:CRANE,2:PUSH,3:PUSH,4:PUSH,5:PUSH,6:PUSH,7:PUSH,8:PULL,9:PUSH,10:PUSH,
              11:PULL,12:PUSH,13:PULL,14:CRANE,15:PUSH,16:PUSH,17:PUSH,18:PUSH,19:CRANE,20:PUSH,
              21:PULL,22:CRANE,23:PUSH,24:CRANE,25:CRANE,26:CRANE,27:PUSH,28:PUSH,29:PUSH,30:PUSH,
              31:PULL,32:PUSH,33:PUSH,34:PULL,35:PUSH,36:PULL,37:PULL,38:PUSH,39:PUSH,40:CRANE},
 },
 "catastrophes": {
   "src": "synthetic/projects/catastrophes-3min",
   "dst": "synthetic/projects/catastrophes-3min-finish",
   "picks": {1:3,2:5,3:10,4:15,5:18,6:22,7:25,8:29,9:34,10:37,11:42,12:46,13:49,14:54,15:58,
             16:63,17:66,18:72,19:75,20:77,21:81,22:87,23:89,24:94,25:99,26:104,27:106,28:112,
             29:114,30:117,31:122,32:127,33:131,34:134,35:137,36:142,37:146,38:151,39:154,40:157},
   # sequence: 1 asteroid,2 Pompeii,3 flood,4 cemetery,5 Krakatoa,6 BlackDeath,7 Permian,8 Napoleon,
   # 9 Lisbon,10 DustBowl,11 Tambora,12 1918flu,13 IceAge,14 GtFireLondon,15 Titanic,16 AralSea,
   # 17 Toba,18 IrishFamine,19 Peshtigo,20 trenches,21 Galveston,22 Justinian,23 Carrington,
   # 24 ChicagoFire,25 Carthage,26 Johnstown,27 Pripyat,28 Tunguska,29 famine,30 Hindenburg,
   # 31 SF1906,32 mine,33 Armada,34 cityRuins,35 NorthSea,36 damFail,37 drownedCity,
   # 38 reclaimed,39 longSilence,40 dawnRecovery
   "motion": {1:PUSH,2:PUSH,3:PULL,4:PULL,5:PUSH,6:LOCKED,7:PULL,8:SETTLE,9:PUSH,10:PUSH,
              11:CRANE,12:LOCKED,13:CRANE,14:PUSH,15:PUSH,16:LOCKED,17:PUSH,18:SETTLE,19:CRANE,20:PULL,
              21:PUSH,22:LOCKED,23:CRANE,24:PUSH,25:PUSH,26:PUSH,27:LOCKED,28:PULL,29:SETTLE,30:PUSH,
              31:PUSH,32:LOCKED,33:PUSH,34:PULL,35:PULL,36:PUSH,37:SETTLE,38:SETTLE,39:PULL,40:SETTLE},
 },
}

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    if which not in CONFIG:
        sys.exit("usage: build_finish.py [revelation|catastrophes]")
    c = CONFIG[which]
    src = pathlib.Path(c["src"]); dst = pathlib.Path(c["dst"])
    src_stills = src / "stills"
    src_sb = json.loads((src / "storyboard.json").read_text())
    by_index = {s["index"]: s for s in src_sb}

    (dst / "stills").mkdir(parents=True, exist_ok=True)
    new_sb = []
    for beat in range(1, 41):
        shot = c["picks"][beat]
        srcpng = src_stills / f"shot_{shot:03d}.png"
        if not srcpng.exists():
            sys.exit(f"MISSING still: {srcpng} (beat {beat})")
        shutil.copy(srcpng, dst / "stills" / f"shot_{beat:03d}.png")
        entry = by_index[shot]
        new_sb.append({
            "index": beat,
            "narration": "",
            "image_prompt": entry["image_prompt"],
            "motion_prompt": c["motion"][beat],
            "_reference_images": [],
        })
    (dst / "storyboard.json").write_text(json.dumps(new_sb, indent=2, ensure_ascii=False) + "\n")
    (dst / "script.md").write_text("# " + which + " montage (finish)\n")
    (dst.parent / "render_policy.json").write_text(json.dumps({"kling_count": 40}) + "\n")
    print(f"[{which}] built {dst}")
    print(f"  40 stills copied + renamed shot_001..040")
    print(f"  storyboard.json written with per-beat motion")
    print(f"  render_policy.json -> kling_count: 40  (at {dst.parent}/render_policy.json)")
    print(f"  motion mix: push={sum(1 for v in c['motion'].values() if v==PUSH)} "
          f"pull={sum(1 for v in c['motion'].values() if v==PULL)} "
          f"crane={sum(1 for v in c['motion'].values() if v==CRANE)} "
          f"settle={sum(1 for v in c['motion'].values() if v==SETTLE)} "
          f"locked={sum(1 for v in c['motion'].values() if v==LOCKED)}")

if __name__ == "__main__":
    main()
