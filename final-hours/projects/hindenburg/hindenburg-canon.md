# Hindenburg — Canon Block (FINAL)
*Project: final-hours/projects/hindenburg*
*Script reference: script.md, 8 beats, ~80-100 stills expected*
*Canon mechanism: pipeline resolves {token} references via this file before sending prompts to Flux*

---

## How to use this file

This is a prompt-engineering specification, not a creative brief. Every line in each canon block is here to narrow Flux's interpretive range. The pipeline reads this file once per stills run and substitutes each {token} with the canon's full text.

**Hard rules for editing this file:**

1. Each character canon is ~80-120 words. This length is deliberate — shorter and Flux drifts; longer and Flux ignores the tail.
2. Physical features are stated as facts, never as descriptions. Write "dark brown hair parted to the left side" not "he has dark hair."
3. Wardrobe is always restated in the prompt body per-shot (rule banked from Six Minutes). Canon wardrobe is the baseline; prompt wardrobe is the truth.
4. Negative constraints (anti-prompts) live in each canon, not in a separate file. Flux uses positive prompts only, so we phrase exclusions as positive statements ("clean-shaven" not "no beard").
5. Scene canons follow the same discipline — locked era, locked architecture, locked lighting, locked aspect of period.

**Reference image generation order (do this before any script-driven prompting):**

1. **{hermann}** first — easiest, adult male in 1937 suit, Flux's strongest territory
2. **{matilde}** second — adult woman in period dress, also strong territory
3. **{werner}** third — youngest child, simplest age-bracket prompt
4. **{walter}** fourth — needs to read as visibly older than Werner but still clearly a child
5. **{irene}** last — hardest, adolescent age range, requires extra-specific anatomy and proportion language

Generate 2-3 acceptable reference images per character before moving to the next. The reference images become the visual locked-in for the canon — text descriptions cannot fully control Flux, but text + locked reference images can.

---

## CHARACTER CANONS

### {hermann}

```
Hermann Doehner, a 49-year-old German-Mexican pharmaceutical executive. He is a dignified businessman of moderate build, around 5 feet 10 inches tall. His face is angular and serious, with dark brown eyes set behind round wire-rim glasses with thin silver frames. His dark brown hair is neatly combed back from his forehead, with visible silver at the temples — graying naturally, not white. He is clean-shaven. His skin tone is fair European, weathered slightly from years in the Mexican climate. His expression is composed and thoughtful, the face of a man accustomed to making decisions. He wears the dignified attire of a 1937 European businessman: a charcoal grey three-piece suit with a white dress shirt and a dark patterned tie, leather oxford shoes. His posture is upright and reserved.
```

**Anti-drift notes for prompting Hermann:**
- Flux's default for "businessman 1937" is often a younger man or a man with a moustache. The "clean-shaven, 49, hair graying at temples, wire-rim glasses" combination must always be in the prompt body, not relied on from canon resolution alone.
- Never describe Hermann as "executive" alone — Flux interprets this as American 1980s corporate. "1937 European businessman in a three-piece suit" is the safer phrasing.
- For shots where Hermann holds the movie camera, restate "small 1937 Bell & Howell 8mm movie camera, handheld, leather casing" — Flux will otherwise generate a modern camera.

---

### {matilde}

```
Matilde Doehner, a 41-year-old Argentine-German woman, mother of three. She has a warm but composed face with dark brown almond-shaped eyes, full dark eyebrows, and a softly defined jaw. Her dark brown hair is pinned up in a 1937 European style — gathered at the nape, with soft waves framing her face. Her skin is fair with warm undertones. She is of moderate build, approximately 5 feet 5 inches, neither slim nor heavy — a healthy mother in her early forties. She wears a 1937 travelling dress in muted earth tones: a deep navy or burgundy fitted bodice over a mid-calf skirt, with simple cream collar and cuffs, low-heeled travelling shoes. Her expression carries quiet maternal presence — attentive, capable, the face of a woman who manages three children with care.
```

**Anti-drift notes for prompting Matilde:**
- Flux's default for "1937 woman" is often a glamorous flapper or a Hollywood-styled blonde. Matilde is none of these — she is a serious mother on a family voyage. Always restate "modest 1937 travelling dress, dark hair pinned up European-style, no makeup, motherly composed expression."
- Never describe Matilde as "elegant" or "beautiful" — these trigger Flux's beauty-standard mode and produce thinner, more glamorous faces than canon. Use "dignified," "composed," "maternal."
- For the dining-room and window beats, the dress is in muted earth tones throughout the video — restate this per-prompt because Flux will drift toward black or white.

---

### {irene}

```
Irene Doehner, a 14-year-old girl, eldest child of the Doehner family. She is in the awkward physical bracket between child and adolescent — taller than her brothers, approximately 5 feet 3 inches, with the proportions of a young teenager: longer limbs than a child, but still slim, still developing. Her face is recognisably her mother's daughter — dark brown almond-shaped eyes, full dark eyebrows, the same softly defined jawline but younger, rounder. Her skin is fair European with warm undertones. Her dark brown hair is shoulder-length, parted in the centre, sometimes tied back with a simple cream or pale-blue ribbon, sometimes loose. She wears a 1937 girl's travelling outfit appropriate for her age: a knee-length pleated skirt in dark blue or grey, a white blouse with rounded collar, knee-length white socks, and dark leather buckle shoes. Her expression is thoughtful and quiet — a serious girl who reads on long trips.
```

**Anti-drift notes for prompting Irene:**
- Irene is the hardest canon. Flux interprets "14-year-old girl" as either a small child (8-10) or a young woman (16-18). The age-bracket of 14 needs explicit reinforcement every prompt: "fourteen years old, neither child nor young woman, the height and proportions of an early adolescent." Restate every shot.
- Irene must read as clearly Matilde's daughter — same eye shape, same hair colour, same jaw. Restate "resembling her mother Matilde, same dark eyes, same dark hair" in shots where both appear or where Irene is foregrounded.
- For the window-scene beat (Beat 6 of the script), Irene must look heavier than her brothers visibly — taller and more developed than Walter (10) and Werner (8). The script's emotional weight depends on this visual.
- The school-uniform reading of Irene's outfit is wrong. She is on a private airship voyage, not in school. Restate "1937 girl's travelling dress, not a school uniform."

---

### {walter}

```
Walter Doehner, a 10-year-old boy, middle child of the Doehner family. He is the older of the two surviving brothers — visibly taller than Werner and noticeably stockier in build, with the proportions of a fourth-grader rather than a younger child. He has dark brown hair like his father, cut short with a neat parting on the left side, the typical 1937 European schoolboy haircut. His face is round but losing its baby fat, with dark brown eyes and full dark eyebrows. His skin is fair European with warm undertones. He is approximately 4 feet 5 inches tall. He wears typical 1937 European boy's travelling clothes: short trousers ending at the knee in dark grey or brown wool, a tucked-in white shirt with rolled-up sleeves, knee-high grey wool socks, and dark leather lace-up shoes. His expression is curious and energetic — a ten-year-old on the adventure of his life.
```

**Anti-drift notes for prompting Walter:**
- Walter must read clearly older than Werner. Restate "Walter, 10, visibly older and taller than his brother Werner, 8" in shots where both appear.
- "European boy 1937 short trousers" is essential phrasing. Flux's default is American long-trouser look or modern children's wear.
- Walter's hair is short and neatly parted — not the floppy or unkempt look Flux often generates for child characters. Restate "neat short hair, 1937 European schoolboy cut."
- For the window-throw beat (Beat 6), Walter is the first child thrown out. He bounces off the window frame on the way down. The reshoots of this beat will be physical — falling figure, ground impact — and Walter's canon must hold across motion shots.

---

### {werner}

```
Werner Doehner, an 8-year-old boy, youngest child of the Doehner family. He is the smallest of the three children — clearly smaller than his 10-year-old brother Walter and significantly smaller than his 14-year-old sister Irene. Approximately 4 feet 1 inch tall, slim, with the proportions of a second-grader. He has dark brown hair, slightly softer and finer than Walter's, with a similar short parted cut. His face is rounder than Walter's, still carrying childhood softness, with large dark brown eyes that dominate his small face. His skin is fair European with warm undertones. He wears 1937 European boy's clothes nearly identical to Walter's but smaller: short trousers in dark grey or brown wool, a tucked-in white shirt, knee-high grey wool socks, dark leather lace-up shoes. His expression is wide-eyed and observant — a quiet eight-year-old who watches the world carefully.
```

**Anti-drift notes for prompting Werner:**
- Werner must read clearly younger and smaller than Walter. Restate the age and height gap every shot where both appear.
- Werner's face is rounder than Walter's — "still carrying childhood softness" is the key phrase. Flux otherwise produces children who look ageless or who all look the same age.
- "Wide-eyed and observant" is canon expression. Werner is the future-survivor whose entire adult life will be marked by what he saw. The wide-eyed quality is the visual signature.
- Werner is the most-named child in the script (he is the one Matilde throws second, the one who survived, the one who lived until 2019). His canon must be the most rock-solid of the three children. Generate 3-4 acceptable reference images before locking.

---

## SCENE CANONS

### {dining_room}

```
The portside dining room of the airship Hindenburg, 1937. A long room running the length of the airship's midsection on the upper passenger deck. The walls are panelled in light maple wood with art deco geometric inlays in darker walnut. The dominant feature is the panoramic observation windows along the outer wall — large, slightly inward-slanted windows that look down onto the ocean or ground below. The windows have thin metal frames in polished aluminium. The ceiling is white with art deco light fixtures in frosted glass and chrome. Tables are set with white linen tablecloths, formal silverware, fine porcelain marked with the Zeppelin company crest. Chairs are tubular chrome with leather upholstery in muted earth tones. The floor is covered in deep, dense carpet in a geometric art deco pattern of cream and dark blue. The light is soft, filtered through the panoramic windows, with warm interior tones from the art deco fixtures. The room feels elegant but restrained — not Titanic-grand, but precisely engineered modernist luxury.
```

**Anti-drift notes for prompting {dining_room}:**
- Flux's default for "1937 airship dining room" is often confused with Titanic-style Edwardian grandeur. The Hindenburg dining room was Bauhaus-influenced art deco modernism — restate this whenever the canon is ambiguous.
- The panoramic slanted windows are the most distinctive feature. Always restate "panoramic observation windows with slight inward slant, polished aluminium frames" — these are the visual signature of the Hindenburg's passenger decks and Flux will otherwise generate standard square windows.
- For the fire-through-windows shots (Beat 5 and 6), the orange glow must come *through* the panoramic windows, not from inside the room. Restate "orange firelight coming through the panoramic observation windows from outside, dining room interior lit by reflected glow."

---

### {cabin}

```
A passenger cabin aboard the Hindenburg, 1937. A narrow rectangular room, approximately 6 feet wide and 7 feet long. Two narrow bunks stack against one wall, with the lower bunk doubling as daytime seating. The opposite wall holds a small foldable washbasin with a polished metal mirror, and a thin foldable writing desk. Storage is built into the walls — narrow vertical lockers in light maple wood, matching the dining room's palette. There is no porthole — the cabins were interior compartments. Light comes from a single art deco wall fixture in frosted glass and chrome. The floor is carpeted in the same deep cream-and-blue art deco pattern as the public spaces. Linens on the bunks are white with the Zeppelin company crest embroidered in pale blue. The cabin feels efficient and modern, more like a luxury train sleeper than a ship's stateroom.
```

**Anti-drift notes for prompting {cabin}:**
- Flux will default to portholes — restate "no porthole, interior cabin without windows, lit by a single wall fixture."
- The cabin is small. Always restate "narrow, 6 feet wide, two bunks against one wall, washbasin opposite" to prevent Flux from generating a more spacious stateroom.
- This canon is used minimally in the script — only in Beat 5 where Hermann turns to return to his cabin before the fire. Generate 1-2 reference images, not more.

---

### {promenade}

```
The promenade deck observation area of the airship Hindenburg, 1937. A long corridor running along the outer hull on the upper passenger deck, with the famous panoramic observation windows along the entire outer wall. The windows are slightly inward-slanted — the iconic Hindenburg design — with polished aluminium frames at chest height to a tall person, allowing passengers to stand and look down at the ocean or ground far below. The inner wall is panelled in light maple with art deco geometric details. The floor is carpeted in the same deep cream-and-blue art deco pattern. Lighting is provided by art deco wall sconces in frosted glass. The promenade feels open and elegant despite the narrow corridor width — the panoramic windows make it feel like floating above the world. The view through the windows shows either the Atlantic Ocean (during the crossing) or the green New Jersey countryside and Lakehurst field (during the descent).
```

**Anti-drift notes for prompting {promenade}:**
- The panoramic slanted windows are critical. Every prompt referencing the promenade must restate "slanted observation windows, looking downward toward the ground far below."
- Hermann does most of his filming from the promenade. Shots of {hermann} at the promenade window with the movie camera will be the most-repeated visual in the video — 4-6 stills minimum. Lock this canon carefully.

---

### {lakehurst_field}

```
The Naval Air Station Lakehurst landing field, May 6 1937, late evening. A vast open grass field in central New Jersey, with the tall steel lattice mooring mast standing in the centre of the frame — approximately 160 feet high, a triangular framework structure painted matte grey. The grass is short, recently mown, with a slightly damp quality from the afternoon's thunderstorms. The sky is overcast but clearing — grey-blue dusk, with patches of darker cloud and occasional gold from the setting sun breaking through. Around the perimeter of the field are low warehouse-like buildings — the airship hangars and naval station outbuildings, painted dark green or grey. Ground crew in dark navy uniforms with peaked caps are positioned in formation around the mast, prepared to handle the mooring lines. A small crowd of civilian observers — relatives, journalists, photographers — stands at a roped-off distance. The atmosphere is anticipatory but routine — this is the seventeenth scheduled transatlantic flight of the Hindenburg's career, the landing crew has done this many times.
```

**Anti-drift notes for prompting {lakehurst_field}:**
- Flux will default to a brighter, sunnier scene — restate "late evening, overcast, dusk light, May 1937 New Jersey." The actual landing was at 7:25 PM on a stormy day.
- The mooring mast is the signature visual. Always restate "tall steel lattice triangular mooring mast, approximately 160 feet high, matte grey." Flux will otherwise generate any tall structure.
- For the post-fire shots (Beat 7), the field becomes a chaotic scene with ambulances and rescue activity. Restate per-prompt: "twisted burning wreckage, ambulances at the field edge, ground crew running, evening light now nearly dark, fire glow illuminating the field."

---

## EXPLICIT NEGATIVE GUIDANCE (across all canons)

These are the failure modes the Six Minutes session taught us. Restate the positive alternative per-prompt where these are likely:

- Flux defaults to **modern wardrobe** when era is ambiguous → always restate "1937 European" and the specific garment
- Flux defaults to **glamorous beauty standards** for women → restate "modest, maternal, no makeup" for Matilde; "schoolgirl, age-appropriate" for Irene
- Flux defaults to **modern photography aesthetic** for historical scenes → restate "period photograph aesthetic, slightly desaturated colours, soft grain"
- Flux defaults to **multiple subjects in group shots** even when prompted for single → frame all multi-character shots as deliberate compositions ("Matilde in foreground, two children in soft focus behind") rather than group portraits
- Flux defaults to **smiling expressions** for any character including in tense moments → restate the canon expression baseline ("composed, thoughtful," "wide-eyed observant," etc.) every prompt
- Flux struggles with **canonical recurring detail accuracy** across stills — Hermann's wire-rim glasses, Matilde's pinned-up hair, Werner's smaller size — these must all be restated per-prompt, not relied on from canon resolution alone

---

## WARDROBE RESTATEMENT RULE (banked from Six Minutes)

Wardrobe details defined in canon are not reliably honoured prompt-to-prompt. Every shot prompt must restate the wardrobe details that matter for that frame:

- For Hermann: "charcoal grey three-piece suit, white dress shirt, dark patterned tie, wire-rim glasses"
- For Matilde: "muted earth-tone 1937 travelling dress, dark hair pinned up European-style"
- For Irene: "1937 girl's travelling outfit, knee-length pleated skirt, white blouse with rounded collar, hair tied with simple ribbon"
- For Walter: "1937 European boy's short trousers in dark grey wool, tucked-in white shirt, knee-high grey socks, leather lace-up shoes"
- For Werner: "1937 European boy's short trousers in dark grey wool, tucked-in white shirt, knee-high grey socks, leather lace-up shoes — visibly smaller than Walter"

---

## TWO-CHARACTER COMPOSITION RULE (banked from Six Minutes)

Two-character shots overwhelm Flux. From the Six Minutes work we learned to frame as:
- Back-of-camera shots (one character foregrounded, other suggested by back of head or shoulder)
- No-people detail shots (the wedding ring beat, the camera beat, the clock beat — these carry emotional weight without requiring character generation)
- Single-character close-ups with the other character implied by context (Matilde at window, "her three children visible only as silhouettes behind her")

For the five-character Doehner family, NEVER prompt for a group portrait of all five together. The cold-open boarding shot must be framed as a backs-walking-toward-airship composition where individual faces are not visible. The dining room scene must be framed as Matilde-foregrounded with children in soft focus.

---

## EXPECTED RESHOOT RATES (planning estimate)

Based on Six Minutes data and the new child-character canon complexity:

- {hermann}: 15-20% reshoot rate (adult male in suit, Flux's strength)
- {matilde}: 20-25% reshoot rate (adult woman in period dress)
- {walter}: 30-40% reshoot rate (10-year-old boy, harder age bracket)
- {werner}: 30-40% reshoot rate (8-year-old boy)
- {irene}: 40-50% reshoot rate (14-year-old, hardest age bracket)
- Multi-character shots involving children: 50%+ reshoot rate, plan for adjacent-shot duplication as fallback

Total stills budget: assume 80 successful stills require ~110-120 generations to achieve. Pipeline cost expectation: $25-35 in fal credits.

---

## NEXT STEP AFTER THIS FILE IS LOCKED

1. Generate {hermann} reference images first (2-3 acceptable images) — easiest canon, locks the visual vocabulary for the family
2. Generate {matilde} reference images second
3. Generate {werner}, {walter}, {irene} in that order
4. Generate scene canons {dining_room}, {promenade}, {lakehurst_field} (skip {cabin} unless time allows — minimal use in script)
5. Run stills generation against the script's beat structure
6. Stills review with explicit attention to child-character canon drift
7. Music selection — critical because of six silent beats
8. Finish, thumbnail, schedule, publish with pinned comment

The canon block is the spec. The stills generation is the build. The review is where the canon either holds or teaches us what to bank for the next video.
