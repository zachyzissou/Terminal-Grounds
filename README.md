# Terminal Grounds

A fresh workspace for building a terminal-first application or toolkit. This repo is intentionally minimal so you can choose the tech stack (Python, Node.js, Rust, etc.) and grow from here.

## Status

Work in progress. Initial workspace scaffolding committed.

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

## License

TBD by the repository owner.

---

## UE5 Project (Vertical Slice)

This repository hosts the Unreal Engine 5 project for Terminal Grounds - a tactical extraction FPS with a rich sci-fi military setting.

- Engine: UE 5.4+
- Project: `TerminalGrounds.uproject`
- Modules: TGCore, TGNet, TGCombat, TGLoot, TGWorld, TGAI, TGMissions, TGBase, TGVehicles, TGUI, TGServer
- Plugins: TGAttachments, TGModKit (project plugins)

See DESIGN_OVERVIEW.md, PROGRESS.md, HOWTO-BUILD.md, and HOWTO-HOST.md for details.

## Phase 4: Visual Identity & World Implementation

### Complete Visual Identity System

Terminal Grounds features a cohesive visual identity across **7 major factions** and **3 technology tiers**:

#### Technology Tiers
- **Human Technology**: Military-grade equipment with familiar, reliable aesthetics
- **Hybrid Technology**: Human engineering enhanced with carefully integrated alien components
- **Alien Technology**: Otherworldly systems that defy conventional understanding

#### Major Factions
- **Directorate**: Military precision with navy blue, gunmetal gray, and crisp white
- **Vultures Union**: Salvage masters with rust red, scrap gray, and warning yellow
- **Free 77**: Professional mercenaries with desert tan, olive drab, and contractor black
- **Corporate Combine**: High-tech innovation with corporate blue, chrome silver, and energy purple
- **Nomad Clans**: Road warriors with road brown, convoy orange, and dust tan
- **Vaulted Archivists**: Knowledge keepers with archive green, knowledge gold, and mystery purple
- **Civic Wardens**: Community protectors with emergency blue, medic white, and safety orange

### Art Direction Documentation

#### Complete Style Guides (`Docs/Art/`)
- **Art Bible**: Color palettes, PBR parameters, material motifs, lighting standards
- **Faction Style Guides**: Individual visual identity for each of the 7 factions
- **UI/UX Style Guide**: Diegetic interface design with faction variants
- **VFX Bible**: Technology-tier appropriate effects systems
- **Audio Vision**: Comprehensive sound design and MetaSounds architecture

#### Content Asset Structure (`Content/TG/`)
- **Materials**: Master material library with Human/Hybrid/Alien technology tiers
- **ConceptArt**: Organized concept sheets for weapons, vehicles, characters, and environments
- **LookDev**: Biome demonstration levels with lighting and weather variants
- **Environment**: Environmental storytelling and world-building systems
- **Playable**: Functional playable slice for gameplay validation

### Implementation Features

#### Master Material System
- **Procedural Weathering**: Rust, wear, dust, and damage layers
- **Faction Customization**: Dynamic color application with faction-appropriate wear
- **Technology Progression**: Distinct visual progression from Human to Alien tech
- **Performance Optimization**: LOD-aware complexity scaling

#### Environmental Storytelling
- **Faction Presence**: Territory markers, propaganda, and cultural elements
- **World History**: Evidence of the Shattered Accord and Harvester impact
- **Battlefield Narratives**: Combat evidence and tactical positioning
- **Interactive Elements**: Discoverable lore and contextual information

#### UI/UX Integration
- **Diegetic Design**: Interface elements exist within the game world
- **Faction Variants**: UI adapts to player faction choice
- **Accessibility**: Comprehensive support for visual, audio, and motor accessibility
- **Performance Scaling**: Responsive design across all platforms

See `/Docs/Art/` for complete visual specifications and `/Content/TG/` for implementation examples.
