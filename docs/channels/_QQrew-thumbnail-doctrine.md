# QQrew Thumbnail Doctrine -- the repeatable layout

The thumbnail is the highest-leverage asset (it decides the click). The LAYOUT is
locked; only a few inputs change per video. Consistency of layout IS the brand.

## THE CONTRACT: invariant layout + per-video inputs

Per-video inputs (the things that change):
  1. SUBJECT STILL   - one flux render of the crew member reacting (pick the
                       candidate that lands right; auto-selector is unreliable)
  2. PROP SUBJECT    - the ONE hero object, chosen by the no-echo rule
                       (deepen the question; never illustrate the title).
                       MUST be a square-ish subject (see prop rule).
  3. HEADLINE        - title (white) + subtitle (gold)
  4. BACKGROUND COLOUR - the pattern-interrupt colour for THIS video's feed.
                       Not fixed to orange. Orange beats the cold-blue Ice Age
                       feed; another episode against another feed may want a
                       different pop colour. Pick the colour that fights the feed
                       this video lands in.
                       NOTE: today the bg colour is baked into the SUBJECT FLUX
                       RENDER (set it in the subject prompt). Phase 2 makes it a
                       true config layer (see bottom).

Everything else below is an invariant layout constant. Never hand-tuned per video.

## LAYER GEOMETRY (fractions of the 1280x720 frame)

Frame thirds (rule-of-thirds spine): vertical guides at x=0.33 and x=0.66.

LAYER 1 - BACKGROUND
  Flat pop colour, chosen per video to interrupt that video's feed (above).
  Currently baked into the subject flux render; Phase 2 -> config bg_color layer.

LAYER 2 - SUBJECT (the crew member)
  Occupies the RIGHT portion: body fills from x~0.58 to the right edge.
  Face/eyeline near x~0.70, headroom at top. Shock + hands-up read.
  Clean-shaven (flux re-adds a beard on tight close-ups; pick the cleanest
  candidate, do not fight it in-prompt). Position is BAKED BY THE SUBJECT PROMPT.

LAYER 3 - PROP (the hero object)  <-- the key spec
  THE RULE, in two parts:
    (a) AUTHORING: choose a SQUARE-ISH prop subject (a standing mammoth, an object
        face-on) -- NOT a wide horizontal object (a long bone). A wide object,
        scaled to a fixed height, becomes very wide and runs rightward into the
        subject. A square object grows DOWNWARD in its corner and stays contained.
        This is the primary lever: pick square subjects.
    (b) COMPOSITOR: the square-ish prop is scaled into a fixed proportional slot:
          corner:       bottom-left
          height:       0.50 of frame height (scale 0.50)
          top anchor:   prop TOP pinned at 0.47 of frame height (nests just under
                        the subtitle), grows downward toward the floor
          left margin:  40px
          width cap:    0.40 of frame width (BACKSTOP only) -- if a prop is still
                        too wide, it scales DOWN to fit the cap rather than invading
                        the subject. The cap is insurance; (a) is the real rule.
    Treatment: rembg knockout + white sticker-border (border_px ~14).

LAYER 4 - TEXT
  Top-left. Anton. Title white [250,250,252], subtitle gold [255,200,60].
  title_area_pct 0.52, anchored top-left, margin_y 20. Heavy stroke + drop shadow.

## CHANNEL.JSON thumbnail.prop CONSTANTS (invariant)
  enabled:           true
  position:          bottom-left
  scale:             0.50          (prop height as fraction of frame height)
  max_w_frac:        0.40          (BACKSTOP width cap; keeps a too-wide prop out
                                    of the subject zone)
  prop_top_frac:     0.47          (prop top pinned here; nests under subtitle)
  margin:            40
  border_px:         14
  border_rgb:        [255,255,255]

## DOES THIS TOUCH OTHER CHANNELS? NO.
  The prop layer + geometry activate ONLY when a channel.json has
  thumbnail.prop.enabled = true. No prop block / not enabled / no prop file ->
  the compositor returns the background untouched. Final Hours, Sacred Dawn,
  Prehistoric Disasters etc. have no prop block, so their thumbnails render
  byte-identical to before. The whole prop system is opt-in per channel; only
  crew-wip has it on.

## PHASE 2 (deliberate, not now)
  - bg_color as a true config layer: knock out the subject, composite it on a flat
    channel-controlled colour + a drop shadow behind it (the shadow Peter liked).
    Makes BACKGROUND COLOUR a clean per-video config input instead of baked into
    the flux render, and makes subject position + shadow systematic.
  - Fix select_thumbnail_still.py vision call (JSONDecodeError fallback -> it never
    actually judges position; currently just takes candidate 1). Until fixed, pick
    the rightmost candidate by eye.
