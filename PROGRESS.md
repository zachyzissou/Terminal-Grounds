# PROGRESS

Tracking shipped work and stubs for the vertical slice.

## Phase 1 - Complete
- [x] Repo init: base workspace
- [x] UE5 project file and TGCore module
- [x] Config scaffolding (DefaultEngine/Game, TG settings)
- [x] Module skeletons (TGNet, TGCombat, TGWorld, TGLoot, TGAI, TGMissions, TGBase, TGVehicles, TGUI, TGServer)
- [x] Plugins skeleton (TGAttachments, TGModKit)
- [x] DataTables seeded (weapons, attachments, items, factions, missions, POIs, vehicles)
- [x] Docker runtime + HOWTO-HOST
- [x] CI workflow for LinuxServer build

## Phase 2 - Pass 1: Visual Concepts Foundation
- [x] Created concept documentation structure (/Docs/Concepts/, /Docs/Lore/)
- [x] Updated data table schemas with Phase 2 fields
- [x] Added weapon tier system (Human/Hybrid/Alien) to Weapons.csv
- [x] Implemented new faction data (Combine, Nomads, Archivists, Wardens)
- [x] Created lore documentation (weapon/faction flavor text)
- [x] Added Phase 2 vehicles (APC, ScoutHelo, LogisticsTruck, UAVs)
- [x] Created placeholder mesh directory structure for UE5
- [x] Added concept art prompts and reference materials
- [x] Updated Items.csv with augments and artifacts
- [x] Enhanced POIs and Missions with Phase 2 content

## Phase 2 - Pass 2: Sci-Fi Player Systems  
- [ ] Exosuit component implementation (Light/Assault/Heavy frames)
- [ ] Augment system with workbench installation
- [ ] Hybrid/Alien weapon mechanics (heat, charge, EMP vulnerability)
- [ ] Deployable systems (drones, EMP, jammers, radar)
- [ ] UI updates for heat/charge indicators

## Phase 3 - Foundation & Scaffolding (Current)
- [x] **Kickstart PR - Documentation & Infrastructure**
  - [x] Created doc skeletons (LORE_BIBLE.md, ART_BIBLE.md, VFX_BIBLE.md, AUDIO_VISION.md)
  - [x] Added concept folder README.md placeholders
  - [x] Created Data/Tables/ structure with Phase 3 CSV schemas
  - [x] Organized Server/ folder structure
  - [x] Updated .gitattributes with complete LFS configuration
  - [x] Extended server.yaml with Phase 3 configs (events, factions, accessibility)
  - [x] Created Content/TG/Maps/ structure (IEZ, TechWastes, LookDev)
  - [x] Updated CI workflow for Phase 3 requirements
  - [x] Updated PROGRESS.md with Phase 3 checklist

## Phase 3 - Implementation Passes (Next)
- [ ] **Pass A - Lore/Narrative Drop**
  - [ ] Complete LORE_BIBLE.md with timeline, factions, regions, economy
  - [ ] Seed Barks.csv, Briefings.csv, Rumors.csv, Posters.csv
  - [ ] Hook briefings into mission UI, implement barks router
  - [ ] Seed 12 contract briefs, 6 rival variants, 60 barks, 24 rumors, 14 posters

- [ ] **Pass B - Art Bible & Concepts**
  - [ ] Complete ART_BIBLE.md with palettes, silhouettes, material motifs
  - [ ] Create concept sheets (weapons x24, vehicles x8, POIs x8, exosuits x3)
  - [ ] Build Master Material Suite with PBR + RVT
  - [ ] Create decal library (40 pieces), LUTs, faction emblems

- [ ] **Pass C - VFX & Audio Foundations**
  - [ ] Complete VFX_BIBLE.md and AUDIO_VISION.md
  - [ ] Implement Niagara systems for Human/Hybrid/Alien tiers
  - [ ] Build MetaSounds architecture for weapons and equipment
  - [ ] Create environmental VFX (rust storms, EMI, reactor plumes)

- [ ] **Pass D - World Partition & POIs**
  - [ ] Enable World Partition, define streaming grids
  - [ ] Expand IEZ with 2 districts, Tech Wastes with 1 band
  - [ ] Author 6 POIs with extraction routes and event hooks
  - [ ] Implement traversal mechanics (vault/mantle/slide)

- [ ] **Pass E - Systems Deepening**
  - [ ] Finalize exosuit frames (Light/Assault/Heavy)
  - [ ] Implement augment trees and surgical bay UI
  - [ ] Add Hybrid/Alien heat/charge/overload mechanics
  - [ ] Enhance vehicles v2 and drone systems
  - [ ] Build Mission Director 2.0 and reputation/vendor systems

- [ ] **Pass F - UI/UX Flows**
  - [ ] Implement HUD indicators (heat/charge/EMP/jam)
  - [ ] Build inventory and map interfaces
  - [ ] Create base management UI (power graph, vendors)
  - [ ] Add accessibility features and string tables

- [ ] **Pass G - Online/Services/SDK**
  - [ ] Implement discovery stub and telemetry
  - [ ] Add anti-cheat posture and replay audit hooks
  - [ ] Create TGModKit sample pack
  - [ ] Maintain Linux server + Docker deployment

- [ ] **Pass H - Balance/Perf/QA**
  - [ ] Conduct 12-player soak testing
  - [ ] Verify hitreg parity across technology tiers
  - [ ] Validate vehicle systems and event chains
  - [ ] Meet performance targets (90/120 FPS)
  - [ ] Complete accessibility sweep
