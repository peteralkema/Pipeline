#!/usr/bin/env bash
# create_channel4_structure.sh — scaffold Channel 4 folder structure
#
# Run from inside the Pipeline directory (where final-hours/ and success-coach/ live):
#   cd /Users/peteralkema/.../03.\ Pipeline/
#   bash create_channel4_structure.sh
#
# Creates channel-4/ alongside the existing channels. Matches the proj_paths
# convention so the existing pipeline scripts work when channel-4/ is the CWD.

set -e

CHANNEL_DIR="channel-4"

if [ -d "$CHANNEL_DIR" ]; then
    echo "ERROR: $CHANNEL_DIR already exists. Aborting to avoid overwriting."
    exit 1
fi

echo "Creating Channel 4 folder structure..."

# Core channel directory
mkdir -p "$CHANNEL_DIR"

# Match existing channel convention
mkdir -p "$CHANNEL_DIR/projects"           # production projects (videos)
mkdir -p "$CHANNEL_DIR/beat-scripts"       # pre-written beat scripts
mkdir -p "$CHANNEL_DIR/docs"               # channel-specific docs
mkdir -p "$CHANNEL_DIR/assets"             # branding, thumbnails, voice samples
mkdir -p "$CHANNEL_DIR/research"           # competitive analysis, topic research
mkdir -p "$CHANNEL_DIR/r-and-d"            # R&D work: avatar, lip-sync, character

# R&D subdirectories (the capability work that distinguishes Channel 4)
mkdir -p "$CHANNEL_DIR/r-and-d/avatar-character"
mkdir -p "$CHANNEL_DIR/r-and-d/lip-sync-tests"
mkdir -p "$CHANNEL_DIR/r-and-d/voice-character"
mkdir -p "$CHANNEL_DIR/r-and-d/script-drafts"

# Research subdirectories
mkdir -p "$CHANNEL_DIR/research/competitor-transcripts"
mkdir -p "$CHANNEL_DIR/research/verticals"
mkdir -p "$CHANNEL_DIR/research/thumbnail-studies"

# Create channel.json — placeholder, will be updated when voice is selected
cat > "$CHANNEL_DIR/channel.json" << 'CHANNEL_JSON'
{
  "name": "channel_4",
  "status": "pre-launch",
  "launch_target": "mid-2027 after Lazarus apprenticeship + Hetzner avatar capability",
  "voice_id": "TBD — male voice character to be selected during R&D phase",
  "register": "first-person protagonist with optional second-person address",
  "protagonist": "male AI avatar — recurring character across all videos",
  "style_suffix": "TBD — cinematic photorealistic recreation in the dignified-documentary register adapted for first-person POV protagonist work, period-accurate detail, restrained palette",
  "default_music_prompt": "TBD — to be developed against pilot video",
  "base_canon": {},
  "notes": "Pre-launch. Folder structure created 1 June 2026 during strategic planning session. R&D begins mid-June after Hetzner migration (4 June 2026). First production video targets Q1 2027 after Maltese Falcon ships and Lazarus apprenticeship reaches feature-length proficiency."
}
CHANNEL_JSON

# Create README — the orienting document for future-Peter
cat > "$CHANNEL_DIR/README.md" << 'README_EOF'
# Channel 4 — Pre-Launch

**Status:** Pre-launch. Folder structure created 1 June 2026.

**Launch target:** Mid-2027, after:
1. Lazarus apprenticeship reaches feature-length proficiency (Sredni Vashtar + Maltese Falcon shipped)
2. Hetzner avatar capability built and proven on Lazarus dramatic dialogue
3. Lazarus PD du Maurier launch (1 January 2027) lands successfully

**Strategic position:** Adjacent to the AI cinematic recreation lane currently dominated by Chloe VS History, Esme Time Travels, History Vault Retold. Differentiated by:
- Male AI avatar protagonist (uncontested at scale in this lane)
- Lazarus-trained dramatic script craft (the genuine moat)
- Underserved verticals (military history, maritime exploration, classical world from male perspective, survival/wilderness) — avoiding saturated Pompeii/Titanic/Black Death territory
- Shared capability stack with Lazarus Films (avatar, lip-sync, multi-speaker dialogue, frame-accurate sync)

**Key documents in this folder:**
- `docs/channel-4-hypothesis.md` — the strategic frame and adjacent-positioning thesis
- `docs/competitive-analysis-1-june-2026.md` — operator data on Chloe, Emma, Esme, Mira, History Vault Retold, CHRONVEIL, Woodstock failure
- `docs/vertical-shortlist.md` — candidate verticals with rationale
- `docs/capability-dependencies.md` — what must be built before launch
- `r-and-d/` — avatar character, lip-sync, voice character work
- `research/competitor-transcripts/` — gathered transcripts of viral videos to study
- `research/verticals/` — research on candidate verticals
- `projects/` — production projects (empty until launch)

**Do not start production projects in this folder until:**
1. Hetzner avatar capability is shipped
2. At least one Lazarus dramatic video has shipped using the capability stack
3. Avatar character design is finalized (face, voice, personality, recurring visual identity)
4. First vertical is selected with topic-audience fit validation

**Do not chase format. Build capability. Deploy adjacent.**

README_EOF

# Create the strategic hypothesis document — preserves today's framing
cat > "$CHANNEL_DIR/docs/channel-4-hypothesis.md" << 'HYPOTHESIS_EOF'
# Channel 4 Strategic Hypothesis

**Date framed:** 1 June 2026
**Decision lead time before launch:** ~12-18 months

## The Core Hypothesis

Chasing the current AI-cinematic-recreation format directly is the wrong move. The format is saturated with format-copycats (Mira, Woodstock channel, dozens of small failures), and the channels that succeed at scale (Chloe VS History at 2.1M-view tier) do so on craft-tier capabilities — dramatic script architecture, character introduction discipline, stakes establishment, restrained closer — that are NOT widely distributed among YouTube creators.

The durable position is adjacent to the format with capability advantages competitors cannot match within the format's window.

## Channel 4's Differentiation Axes

1. **Male AI avatar protagonist** — currently uncontested at scale in this lane
2. **First-person protagonist register with optional second-person address** — hybrid between Chloe (pure vlog) and History Vault Retold (pure documentary)
3. **Underserved verticals** — military history embedded witness, maritime exploration, classical world from male POV, survival/wilderness. NOT Pompeii/Titanic/Black Death (saturated)
4. **Lazarus-apprenticeship script craft** — six months of master-writer adaptation discipline before launch, building dramatic instinct that copycats cannot shortcut
5. **Shared capability stack with Lazarus and Final Hours** — Hetzner-deployed avatar, frame-accurate Whisper sync, multi-speaker dialogue, character consistency, dramatic-arc craft

## Why Not Launch Sooner

Launching before the Lazarus apprenticeship produces Mira-tier output — surface-format right, dramatic architecture missing. The data from competitor analysis shows that this failure mode reliably produces declining VPH curves and audience burnout within 4-6 videos.

The Lazarus apprenticeship through Sredni Vashtar (Saki — perfect endings), Maltese Falcon (Hammett — compression and dialogue), and The Loving Spirit (du Maurier — interior register) builds the dramatic taste that Channel 4 will need to operate at Chloe's tier rather than Mira's.

## Why The Lane Will Still Exist

Format-chasers burn through audience trust in weeks. Esme's high-volume operator model survives because she monetizes the playbook itself (ebook + memberships) — but most operators chasing format collapse within months.

Long-form viral-tier competition in this lane is THINNER than aggregate metrics suggest. CHRONVEIL is 95% Shorts. Chloe VS History is 71% Shorts. Pure long-form craft-tier operators are rare and irreplaceable on a competitor timeline shorter than the Lazarus apprenticeship window.

## Compounding Logic

Every capability built for Channel 4 also serves Lazarus and Final Hours:
- Whisper frame-accurate sync (built 1 June 2026 for Mary Celeste) — used by all three channels
- Storyboard discipline auditor (built 31 May 2026) — used by all three channels
- proj_paths convention (fixed 31 May 2026) — pipeline architecture for all three channels
- Lip-sync character consistency (mid-June R&D on Hetzner) — required for Lazarus Maltese Falcon AND Channel 4 protagonist
- Multi-genre script architecture (Phase 2 backlog) — required for Lazarus dialogue AND Channel 4 character beats
- Dramatic-arc script craft (Lazarus apprenticeship) — directly transferable to Channel 4 viral-tier writing

## What Tomorrow's Data Will Inform

Mary Celeste's first 48 hours of retention data will indicate whether protagonist-anchoring framing meaningfully outperforms artifact-anchoring framing. If yes, the Channel 4 thesis strengthens — protagonist storytelling generalizes across registers. If no, the framing for Channel 4 needs revision but the architecture above still holds.

HYPOTHESIS_EOF

# Create the competitive analysis pointer (the full doc lives in shared/docs)
cat > "$CHANNEL_DIR/docs/competitive-analysis-1-june-2026.md" << 'COMP_EOF'
# Competitive Analysis Reference

Full document: `../../shared/docs/channel-lane-analysis-and-channel-4-hypothesis.md`

Quick reference summary of operators studied 1 June 2026:

| Operator | Subs | Long-form Share | Profile | Lesson |
|----------|------|-----------------|---------|--------|
| Chloe VS History | 260K | 29% | Hybrid Shorts+long, 2.1M Titanic viral | Craft tier proof point |
| Esme Time Travels | 20.4K | 74% | High-throughput + ebook | Playbook-as-business model |
| Original Emma | ~10K | unknown | Literary short film, fully AI | First-mover craft |
| Biblical Emma | 306 | n/a | Faith vertical, 3.8x outlier | Format adapts to vertical |
| Mira Was There | 1.6K | n/a | Format without craft | Failure mode |
| History Vault Retold | 1.16K | n/a | Second-person documentary | Alternative register works |
| CHRONVEIL | unknown | 5% | Shorts-dominant | Misclassified as long-form competitor |
| Woodstock channel | unknown | n/a | Format + wrong topic | 45 views in 3 weeks |

Key isolated variable: Chloe Titanic A/B test (i4O5KNnKvBE vs HZRdKlOHogk). Same channel, same topic, 2,000x performance gap. The viral version delivered complete dramatic arc; the flop ended at boarding. Confirms script craft is the leverage point.

COMP_EOF

# Create vertical shortlist — placeholder for ongoing research
cat > "$CHANNEL_DIR/docs/vertical-shortlist.md" << 'VERT_EOF'
# Channel 4 Vertical Shortlist

## Selection Criteria

- Male protagonist must feel natural in the vertical (not pasted on)
- Vertical must have known viral potential (existing high-view content in adjacent formats)
- Topic-audience fit must be strong (avoid Woodstock-style happy-event/distressed-thumbnail mismatch)
- Currently underserved at high production value
- Compatible with Lazarus-trained dramatic register
- Topic supply must be deep (10+ years of content runway)

## Candidates (1 June 2026)

### Tier 1 — Strongest Candidates

**Military history embedded witness**
- Examples: Gettysburg (Pickett's Charge), Verdun (Fort Douaumont), Stalingrad (House of Pavlov), Hue '68 (Marine perspective), Operation Market Garden (Arnhem)
- Audience: large, predominantly male, currently served by Drachinifel-style talking-head + Indy Neidell's "World War Two" channel
- Underserved at: first-person cinematic AI recreation
- Fit with Lazarus craft: high — military history requires dramatic restraint, stakes establishment, named-character work
- Topic supply: enormous (every major battle of every major war for centuries)

**Maritime exploration / disaster**
- Examples: Shackleton's Endurance, Cook's Resolution, Magellan, Erebus and Terror (Franklin expedition), Whaleship Essex, Indianapolis sinking
- Audience: large engaged niche, currently served by talking-head documentary (Ryan Garcia, Brick Immortar)
- Underserved at: first-person cinematic AI recreation
- Fit with Final Hours brand: very high — adjacency between Final Hours and Channel 4 strongest here
- Topic supply: deep (centuries of maritime history)

### Tier 2 — Worth Investigating

**Classical/Ancient world from male POV**
- Examples: Roman soldier at Cannae, Greek hoplite at Thermopylae, Egyptian scribe, Byzantine merchant
- Audience: large, served by Historia Civilis, Toldinstone
- First-person AI recreation gap: real
- Risk: closest to Chloe/Emma vertical, more direct competition

**Survival/Wilderness**
- Examples: Donner Pass, Andean rugby crash, Yukon gold rush, Klondike, Mawson's Australasian Antarctic Expedition
- Audience: very engaged, currently served by Stokes Twins-tier content
- Topic supply: moderate
- Risk: format may not support character return-each-episode model

### Tier 3 — Skip

**Pompeii / Titanic / Black Death verticals**
- Saturated. Algorithm pairs new entries with established viral hits. New entrants lose.

**Faith/biblical verticals**
- Religiously polarized audience. Content quality bar uneven. Risk of being miscategorized.

## Next Action

When R&D phase begins (mid-June 2026), pull NexLev competitive data for Tier 1 verticals — find what's currently working at scale in military history and maritime exploration to identify the specific topic-format-runtime-thumbnail combinations that win in those spaces.

VERT_EOF

# Create capability dependencies — what must be built before launch
cat > "$CHANNEL_DIR/docs/capability-dependencies.md" << 'CAP_EOF'
# Channel 4 — Capability Dependencies Before Launch

## Hard Dependencies (must be complete before first production video)

### Pipeline Infrastructure
- [x] Whisper-based frame-accurate sync (built 1 June 2026 for Mary Celeste)
- [x] Storyboard discipline auditor (built 31 May 2026)
- [x] proj_paths convention (fixed 31 May 2026)
- [ ] Hetzner VPS deployment (Thursday 4 June 2026)
- [ ] Auto-Whisper alignment baked into finish step (built 1 June 2026, verify on Hetzner)
- [ ] Skip-existing logic in stills command (Phase 2 backlog)
- [ ] fal retry-on-error with backoff (Phase 2 backlog)

### Avatar Capability Stack
- [ ] InstantID or PuLID face consistency across shots
- [ ] Wav2Lip, SadTalker, or Hedra lip-sync at consumer-acceptable quality
- [ ] Voice character selection — male voice with dignified-documentary range
- [ ] Avatar face design — locked recurring character (age, hair, build, period-mobility)
- [ ] Period-mobility wardrobe — character must work in multiple period settings without retraining

### Script Craft
- [ ] Sredni Vashtar (Saki) shipped — proof of concept for character + cruel ending discipline
- [ ] Maltese Falcon (Hammett) shipped — feature-length dialogue and compression
- [ ] At least one Lazarus adaptation with multi-speaker dialogue scenes proven on Hetzner
- [ ] Internalized dramatic-arc skeleton: introduce character + establish stakes + failure-to-warn + sensory peak + restrained closer

### Brand Identity
- [ ] Channel name selected
- [ ] Channel banner + thumbnail visual system
- [ ] Tagline + channel description
- [ ] First five video topic shortlist with thumbnail tests
- [ ] Pinned-comment template

## Soft Dependencies (can be developed in parallel)

- Vertical selection finalized
- First three video scripts written
- Test renders of avatar in 2-3 period settings
- Voiceover sample renders for protagonist character
- Music library or Suno workflow for Channel 4 register

## Launch Readiness Test

Before going live, the channel must pass this proof point: render one complete 10-minute video at Chloe's craft tier (named character + stakes + failure-to-warn + sensory peak + restrained closer) with male AI avatar protagonist, fully synced via Whisper, period-accurate, on Hetzner infrastructure, in a Tier 1 underserved vertical.

If that video can be produced and looks dignified-documentary tier on review, Channel 4 is ready to launch.

If it produces Mira-tier output, return to Lazarus apprenticeship for another 3-6 months.

CAP_EOF

# Create the avatar R&D scratch space
cat > "$CHANNEL_DIR/r-and-d/avatar-character/README.md" << 'AVATAR_EOF'
# Avatar Character R&D

This folder is for developing the male AI avatar protagonist for Channel 4.

## R&D Sequence

1. **Visual identity exploration** — test face options across multiple period settings
2. **Wardrobe library** — period costumes the character can wear without breaking identity
3. **Lip-sync proof of concept** — single 30-second monologue
4. **Multi-shot consistency test** — same character across 5 shots in same period
5. **Multi-period consistency test** — same character in 3 different period settings
6. **Emotional range test** — distress, fear, awe, restraint
7. **Thumbnail face test** — close-up alarmed expression for thumbnail tier

## Key Design Questions

- Age: late 20s to mid-30s seems most period-flexible
- Beard: optional/removable to fit different periods
- Hair: medium length, period-neutral
- Voice character: gravitas-leaning but not deep narrator — closer to Cillian Murphy than Morgan Freeman
- Personality: observant, restrained, slightly haunted — not a wisecracker
- Name: TBD — should be period-flexible (Daniel, Henry, James, Edward work in many eras)

## Critical Constraint

The avatar must be capable of showing thumbnail-grade distress without uncanny valley artifacts. This is the single hardest visual capability. If we cannot solve this, the entire thumbnail strategy degrades and Channel 4 loses its biggest CTR advantage.

AVATAR_EOF

# Create the script drafts scratch space
cat > "$CHANNEL_DIR/r-and-d/script-drafts/README.md" << 'SCRIPT_EOF'
# Script Drafts for Channel 4

Pilot script drafts go here. Drafts should respect the Chloe-tier dramatic skeleton:

1. **Opening hook** — protagonist introduces setting + stakes within 30 seconds
2. **Establishing scenes** — sensory detail of the world that will be lost
3. **Named character introduction** — secondary character with explicit backstory
4. **Promise/stakes statement** — protagonist commits to trying to change something
5. **Building tension** — environmental signals, period detail, growing dread
6. **Failure-to-warn beat** — protagonist tries to intervene and fails (the dramatic centerpiece)
7. **The disaster** — sensory peak with restraint
8. **Aftermath reflection** — restrained closer that honors the gap between event and language

Target runtime: 10-15 minutes. Word count: approximately 1500-2200 words depending on pace.

Drafts before script-craft proficiency is built (i.e., before Maltese Falcon ships) should be considered exercises rather than production scripts.

SCRIPT_EOF

# Create the research subdirectory README
cat > "$CHANNEL_DIR/research/README.md" << 'RESEARCH_EOF'
# Channel 4 Research

This folder holds ongoing competitive intelligence and vertical research.

## Subfolders

- `competitor-transcripts/` — viral video transcripts to study dramatic structure
- `verticals/` — research on candidate verticals (military, maritime, classical, survival)
- `thumbnail-studies/` — thumbnail screenshots and analysis for the lane

## Update Cadence

- Pull a new competitor video to study every 1-2 weeks during R&D phase
- Update vertical research when NexLev surfaces new operator patterns
- Add thumbnail studies whenever a notable thumbnail appears in the lane

RESEARCH_EOF

# Final structure summary
echo ""
echo "Channel 4 folder structure created:"
echo ""
find "$CHANNEL_DIR" -type d | sort
echo ""
echo "Key seed documents:"
echo "  $CHANNEL_DIR/README.md"
echo "  $CHANNEL_DIR/channel.json"
echo "  $CHANNEL_DIR/docs/channel-4-hypothesis.md"
echo "  $CHANNEL_DIR/docs/vertical-shortlist.md"
echo "  $CHANNEL_DIR/docs/capability-dependencies.md"
echo "  $CHANNEL_DIR/r-and-d/avatar-character/README.md"
echo "  $CHANNEL_DIR/r-and-d/script-drafts/README.md"
echo ""
echo "Pre-launch. R&D begins after Hetzner migration (Thursday 4 June 2026)."
