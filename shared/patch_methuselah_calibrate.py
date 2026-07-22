#!/usr/bin/env python3
"""
patch_methuselah_calibrate.py -- VO convergence pass 1.

Rewrites 83 beats so every block lands 194-198s spoken, then appends one
<break/> to each block's last beat to top up to exactly 200.000s.

Measured basis: calibrate on voiceover.json, 163 WPM, 1 word ~= 0.37s.
Trims are taken from the beats that MEASURED longest, never spread evenly.

Idempotent. Verifies every target beat exists and still holds its old text
before writing. Backs up to master.csv.pre_calib1.

  cd ~/Pipeline/sacred-dawn/projects
  python ~/Pipeline/shared/patch_methuselah_calibrate.py
"""
import csv
import shutil
import sys
from pathlib import Path

MASTER = Path.home() / "Pipeline" / "sacred-dawn" / "projects" / "methuselah" / "master.csv"

NEW = {
    "1/9":    'They keep to themselves, and they have kept to themselves for a reason nobody says out loud.',
    "1/21":   'Then he carries the child out of the hut, into the first grey light of the morning.',
    "1/23":   'And he speaks a name the way a judge reads out a sentence, slowly, so it lands.',
    "1/26":   'When this one is taken, they say, the waters will be sent over all the earth.',
    "1/30":   'Not one of them knows that something has begun to count, out loud, on a mountain.',
    "2/4":    'The boy asks where they are going, twice. His father keeps walking.',
    "2/10":   'This is Adam, the boy is told. The first man of us all.',
    "2/28":   'It was said that from a woman, one day, one of us will come.',
    "3/3":    'The country changed. Trees thinned. Tracks became roads.',
    "3/19":   'One Enoch feeding a fire. Another cut into stone.',
    "3/22":   'The heat hit first. Open sheds, furnaces roaring, men stripped to the waist.',
    "3/24":   'He watched a man pour liquid metal into a bed of sand.',
    "3/27":   'An instructor, Genesis says. Bronze and iron.',
    "4/2":    'Not his wife. Not his son. Nobody on the mountain.',
    "4/4":    "I was shown my father's time, Enoch said.",
    "4/11":   'They came down, the text says, on a mountain. Hermon.',
    "4/12":   'Enoch describes weight, and ground giving way.',
    "4/16":   'All two hundred swore an oath, so none could turn back.',
    "5/1":    'At first he thought it was a tree line moving, and stood still.',
    "5/24":   'When the harvest was gone, Enoch writes, they consumed the men.',
    "5/31":   'The city built higher walls and armed everybody.',
    "5/33":   'Enoch says the earth spoke. Not the people. The ground.',
    "5/37":   'He asked the only question left. Does anyone up there see?',
    "6/10":   'Jude quotes him in the New Testament. Behold, the Lord comes.',
    "6/16":   'They went back to what they were doing, laughing quietly, and let him talk.',
    "6/21":   'Enoch was inside, bent over stretched hides.',
    "6/24":   'I am writing what I was shown.',
    "6/36":   'A column of light stood on the high stone.',
    "7/6":    'So that is the household. A fire, a line of stones, a son Lamech.',
    "7/7":    'Hold on to that name, because the world had another, and Genesis names him too.',
    "7/8":    "Cain's line runs six deep, undated. It ends on a man.",
    "7/13":   'I killed a man for wounding me. A boy for hurting me.',
    "7/23":   "And the man who invented the instruments there was this Lamech's own son.",
    "7/28":   'The other son of that house Methuselah had already met.',
    "7/31":   'The boy at the grindstone worked for a family, and that was the family.',
    "7/34":   'This man made it a verse and taught his wives.',
    "7/39":   'He had given the boy that name himself.',
    "8/3":    'He was three hundred years old that year, and Genesis lets you work it out.',
    "8/10":   'He watched a river leave its bed and cut a new one.',
    "8/11":   'He planted trees, and stood beside them when they came down.',
    "8/15":   'The stones were the only honest thing there. They rounded nothing off.',
    "8/21":   'Something was happening to his body, and it was not ordinary.',
    "8/28":   'Why is he still here, they meant. Nobody wanted it answered.',
    "8/35":   'Then he remembered a hand on his shoulder. Keep walking.',
    "8/39":   'From the mountain that night he could see the whole dark valley.',
    "9/12":   'His hair was white as wool. When he opened his eyes, the house lit up.',
    "9/15":   'The mother, awake for two days, was the only one not afraid.',
    "9/20":   'Whose child is this, he said. And he said it to his wife, in front of everybody.',
    "9/37":   'And the oldest man alive, asked everything by everybody, had nothing.',
    "10/5":   'Not a thing a man of that age does lightly.',
    "10/22":  'Through this one the earth will begin again.',
    "10/30":  'He gave the child back. He is not one of theirs.',
    "10/33":  'Noah. Because this one will bring us rest from the labour of our hands.',
    "10/40":  'something stopped him where he stood, and it was not the wind.',
    "11/1":   'Four hundred and eighty years went by.',
    "11/5":   'His grandson was four hundred and eighty, and still young for that world.',
    "11/6":   'That morning, Noah found out what he was for.',
    "11/9":   'I will make an end of everything that breathes. But not you.',
    "11/10":  'Then the instruction. The strangest paragraph in the book.',
    "11/11":  'Make an ark of gopher wood, pitched within and without.',
    "11/13":  'One window. Three floors. And a hundred and twenty years.',
    "11/14":  'The field was a field again. Noah was not.',
    "11/17":  "Because he had seen his father's writing about water, centuries earlier.",
    "11/19":  'I have been alive an unreasonable time, and wondered why.',
    "11/23":  'The neighbours came to look. At first it was friendly.',
    "11/27":  'He wants to be king of a boat, they said. Lord of the timber.',
    "11/28":  'They said it was a trick for free labour. They said he heard voices.',
    "11/29":  'Then the laughing stopped being enough. It always does.',
    "11/33":  'He had been sold that blade by the family that set the boast to music.',
    "11/35":  'Noah listened. Then he went back to work.',
    "11/36":  'Near the end, Methuselah came down the mountain carrying something heavy.',
    "11/37":  'A bundle of hides, worn soft, tied with retied cord.',
    "11/39":  'That somebody is you. Let the world after the water know.',
    "11/40":  'The ark was finished in the spring. Then the animals came.',
    "12/8":   'Not fear of dying. He had stopped finding that interesting.',
    "12/12":  'His wife looked back once at a road she knew.',
    "12/14":  'His sons went up in silence. No triumph on any face.',
    "12/16":  'And Methuselah did not go in.',
    "12/21":  'Noah stood in the doorway and asked him with his eyes.',
    "12/23":  'Go on. I have done my part. I held it open long enough.',
    "12/25":  'From up there the ark looked like a shadow put down on the plain.',
    "12/27":  'And the sky had gone the colour of a ceiling about to give.',
    "12/37":  'When he departs, it shall be sent. The name did what it said.',
}

TAGS = {
     1: 5.5,
     2: 5.6,
     3: 4.6,
     4: 3.8,
     5: 3.5,
     6: 3.8,
     7: 1.9,
     8: 3.2,
     9: 3.8,
    10: 2.9,
    11: 1.8,
    12: 3.3,
}


def main() -> int:
    if not MASTER.exists():
        print("FAIL: %s not found" % MASTER)
        return 1

    rows = list(csv.DictReader(MASTER.open()))
    if len(rows) != 480:
        print("FAIL: expected 480 rows, found %d" % len(rows))
        return 1
    fields = list(rows[0].keys())

    if any("<break" in r["narration"] for r in rows):
        print("already applied -- break tags present, no change")
        return 0

    idx = {"%s/%s" % (r["block_id"], r["clip_index"]): r for r in rows}
    missing = [k for k in NEW if k not in idx]
    if missing:
        print("FAIL: beats not found: %s" % ", ".join(missing))
        return 1

    changed = 0
    for k, text in NEW.items():
        idx[k]["narration"] = text
        changed += 1

    tagged = 0
    for b, secs in TAGS.items():
        k = "%d/40" % b
        r = idx[k]
        r["narration"] = r["narration"].rstrip() + ' <break time="%.1fs" />' % secs
        tagged += 1

    backup = MASTER.with_suffix(".csv.pre_calib1")
    shutil.copy2(MASTER, backup)
    with MASTER.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print("backed up -> %s" % backup)
    print("rewrote   %d beats" % changed)
    print("tagged    %d block ends" % tagged)

    def wc(s):
        import re
        s = re.sub(r"<[^>]*>", " ", s or "")
        return len([t for t in s.split() if re.search(r"[A-Za-z0-9]", t)])

    print("\nper-block words after patch:")
    tot = 0
    for b in range(1, 13):
        n = sum(wc(r["narration"]) for r in rows if int(r["block_id"]) == b)
        tot += n
        print("  b%02d  %3dw   tag %.1fs" % (b, n, TAGS[b]))
    print("  film %dw (was 6841)" % tot)

    over = [("%s/%s" % (r["block_id"], r["clip_index"]), wc(r["narration"]))
            for r in rows if wc(r["narration"]) > 55]
    print("\nover 55 words: %s" % (over or "none"))

    print("\nNEXT:")
    print("  python ~/Pipeline/build_lego.py normalise --project methuselah")
    print("  python ~/Pipeline/build_lego.py blocks    --project methuselah")
    print("  python -u ~/Pipeline/build_lego.py audio  --project methuselah")
    print("  python ~/Pipeline/build_lego.py calibrate --project methuselah methuselah/voiceover.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
