# Terminal Grounds

Terminal Grounds is an Unreal Engine 5.4 project: a session-based salvage/extraction game set after the Shattered Accord. Explore contested POIs, complete contracts, and extract what you can—alone or with a crew—while factions clash over technology from Human, Hybrid, and Alien origins.

## Status

Work in progress. Active development across gameplay, art, and backend.

## Getting started

- Clone is already set up to this remote.
- Pick your stack and create an entry point under `src/`.
- Use the `docs/` folder for design notes and architecture decisions.

### Suggested stacks (optional)

- Python CLI: create `src/terminal_grounds/main.py` and use `argparse` or `click`.
- Node.js CLI: create `src/index.js` and use `npm init -y` and `commander` or `yargs`.

## Development

- Editor: VS Code with the recommended extensions.
- Style: See `.editorconfig` for base settings.
- Ignore rules: See `.gitignore`.

## Contributing

Open a PR. Small, focused changes are preferred.

## Quickstart (UE5)

- Open `TerminalGrounds.uproject` in UE 5.4+
- Build targets: Game, Editor, and `TerminalGroundsServer`
- Startup Map: Set in `Config/DefaultGame.ini` (IEZ/LookDev maps available)
- Play-in-Editor: Use LookDev/Playable maps under `Content/TG/Maps/`

## Repository map

- `Config/` — Engine, Game, and project DeveloperSettings
- `Content/` — UE assets (Maps, Materials, VFX, UI, ConceptArt, etc.)
- `Data/` — Source-of-truth CSVs for datatables (mirrors subset under Content/DataTables)
- `docs/` — Bibles and guides (Art, VFX, Audio, Lore, Concepts)
- `Plugins/` — Project plugins (TGAttachments, TGModKit)
- `Source/` — C++ modules (TGCore, TGNet, TGCombat, …)
- `Server/` + `Docker/` — Dedicated server packaging and container runtime

## UE asset path index

- Maps
  - Content/TG/Maps/IEZ/ — District lookdev and gameplay maps
  - Content/TG/Maps/TechWastes/ — Wasteland bands and POIs
  - Content/TG/Maps/LookDev/ — Technology tier showcases
- DataTables
  - Content/DataTables/*.csv — In-project datatables (built from `Data/Tables`)
- Materials
  - Content/TG/Materials/Human/
  - Content/TG/Materials/Hybrid/
  - Content/TG/Materials/Alien/
- VFX
  - Content/TG/VFX/Systems/ — Niagara systems
  - Content/TG/VFX/Materials/ — Effect materials
- Audio
  - Content/TG/Audio/MetaSounds/
  - Content/TG/Audio/SFX/
- UI
  - Content/TG/UI/HUD/
  - Content/TG/UI/Menus/
  - Content/TG/UI/Icons/
- Concept Art (references)
  - Content/TG/ConceptArt/Weapons/
  - Content/TG/ConceptArt/Vehicles/
  - Content/TG/ConceptArt/Biomes/

Screenshot TODO: Insert overview images for each map family.

## Story, World, and Narrative Overview

### Elevator pitch

- You’re a contract operative navigating the ruins of the Shattered Accord—where mega-factions, civic militias, archivists, and scavenger guilds compete to control remnants of dangerous technology. Every operation is a risk: get in, secure objectives, extract alive.

### Setting snapshot

- The Shattered Accord: A failed global compact fractured civil order into faction-ruled enclaves and ungoverned wastes.
- Residual Threats: Experimental systems (“Harvesters” and other anomalous tech) destabilize regions, forcing evacuations and creating lucrative but deadly salvage zones.
- Contested POIs: Power plants, archive vaults, convoy graveyards, and research nodes linked by precarious logistics and evac corridors.

### Core fantasy and pillars

- Salvage under pressure: Tight resource windows, extraction tension, and meaningful choices about what to carry out.
- Faction identity: Seven major factions with distinct visuals, values, and contracts; reputation affects access and risk.
- Technology tiers: Human → Hybrid → Alien with escalating capability and operational risk.
- Persistent consequence: What you recover, lose, or broadcast changes your opportunities and reputation.

### Core game loop (session)

1) Briefing: Accept a contract and review intel (rumors, barks, posters) tied to the target POI.
2) Insertion: Select loadout and approach—quiet infiltration or armored push.
3) Objectives: Recover attachments, data, or artifacts; opportunistically salvage high-value finds.
4) Extraction: Reach an evac corridor or call for pickup; prepare for ambush or environmental spikes.
5) After-action: Resolve outcomes—faction standing, unlocks, repairs, and new rumors/briefings.

### Narrative systems and content sources

- Briefings and Rumors: Drive objectives and world feel (Data/Tables/Briefings.csv, Rumors.csv).
- Barks and Posters: Environmental storytelling and faction tone (Data/Tables/Barks.csv, Posters.csv; Content/TG/Decals/Posters).
- Faction Flavor and Lore Bibles: Canon and tonal guardrails (docs/Lore/*, docs/Art/*).
- POIs: Named locations with micro-stories and encounter seeds (Data/Tables/POIs.csv, Content/TG/Maps/POI/).

See docs/Lore/LORE_BIBLE.md and docs/Lore/Lore_Backbone.md for the deep-dive, plus docs/Art/ART_BIBLE.md for visual/narrative cohesion.

## Phase 4: Visual Identity & World Implementation

### Complete Visual Identity System

Terminal Grounds features a cohesive visual identity across 7 major factions and 3 technology tiers:

#### Technology Tiers

- Human Technology: Military-grade equipment with familiar, reliable aesthetics
- Hybrid Technology: Human engineering enhanced with carefully integrated alien components
- Alien Technology: Otherworldly systems that defy conventional understanding

#### Major Factions

- Directorate: Military precision with navy blue, gunmetal gray, and crisp white
- Vultures Union: Salvage masters with rust red, scrap gray, and warning yellow
- Free 77: Professional mercenaries with desert tan, olive drab, and contractor black
- Corporate Combine: High-tech innovation with corporate blue, chrome silver, and energy purple
- Nomad Clans: Road warriors with road brown, convoy orange, and dust tan
- Vaulted Archivists: Knowledge keepers with archive green, knowledge gold, and mystery purple
- Civic Wardens: Community protectors with emergency blue, medic white, and safety orange

### Art Direction Documentation

#### Complete Style Guides (Docs/Art/)

- Art Bible: Color palettes, PBR parameters, material motifs, lighting standards
- Faction Style Guides: Individual visual identity for each of the 7 factions
- UI/UX Style Guide: Diegetic interface design with faction variants
- VFX Bible: Technology-tier appropriate effects systems
- Audio Vision: Comprehensive sound design and MetaSounds architecture

#### Content Asset Structure (Content/TG/)

- Materials: Master material library with Human/Hybrid/Alien technology tiers
- ConceptArt: Organized concept sheets for weapons, vehicles, characters, and environments
- LookDev: Biome demonstration levels with lighting and weather variants
- Environment: Environmental storytelling and world-building systems
- Playable: Functional playable slice for gameplay validation

### Implementation Features

#### Master Material System

- Procedural Weathering: Rust, wear, dust, and damage layers
- Faction Customization: Dynamic color application with faction-appropriate wear
- Technology Progression: Distinct visual progression from Human to Alien tech
- Performance Optimization: LOD-aware complexity scaling

#### Environmental Storytelling

- Faction Presence: Territory markers, propaganda, and cultural elements
- World History: Evidence of the Shattered Accord and Harvester impact
- Battlefield Narratives: Combat evidence and tactical positioning
- Interactive Elements: Discoverable lore and contextual information

#### UI/UX Integration

- Diegetic Design: Interface elements exist within the game world
- Faction Variants: UI adapts to player faction choice
- Accessibility: Comprehensive support for visual, audio, and motor accessibility
- Performance Scaling: Responsive design across all platforms

See `/Docs/Art/` for complete visual specifications and `/Content/TG/` for implementation examples.
