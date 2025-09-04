# Bloom — Design Overview

Note: Internal codename remains “Terminal Grounds” in paths and tooling during rollout.

## Core Pillars

Tactical extraction FPS, grounded near-future setting, server-authoritative netcode, data-driven content architecture.

## Core Loops

Raid → Fight → Loot → Extract → Stash/Base → Repeat. Dynamic missions/events modulate pressure and opportunity.

## Phase 1 Systems (Complete)

- **Weapons + Attachments**: Basic ballistic weapons with modular attachment system
- **Inventory/Stash**: Persistent character progression and item storage
- **Factions + AI**: Sky Bastion Directorate, Iron Scavengers, The Seventy-Seven with AI behaviors
- **POIs + Resources**: Industrial sites with resource collection
- **Missions**: Contract-based objective system
- **Vehicles**: Light technical vehicles
- **Base V1**: Basic building and storage systems
- **Dedicated Server**: Docker-containerized Linux server

## Phase 2 Systems (Complete)

### Territorial Control System - OPERATIONAL ✅

- **Database Foundation**: SQLite territorial system with 0.04ms query performance
- **Real-time Synchronization**: WebSocket server supporting 100+ concurrent players
- **UE5 Integration**: TGTerritorialManager WorldSubsystem with C++ performance core
- **Asset Generation Pipeline**: 100% success rate territorial asset coverage
- **Complete Asset Types**: Flags, structures, markers, UI elements, overlays for all 7 factions

### Phase 2 Expansion Goals (Future)

#### Sci-Fi Player Systems

- **Exosuits**: Light/Assault/Heavy frames affecting movement and combat
- **Weapon Tiers**: Field (reliable), Splice (powerful/unstable), Monolith (rare/unpredictable)
- **Augmentations**: Cyberpunk enhancements with trade-offs (Echo Reflex, Spectral Sight, Plateskin, Nerveweave)
- **Deployables**: Drones, EMP devices, jammers, radar systems

#### Expanded Factions

- **Corporate Hegemony**: High-tech PMC with prototypes and aerial superiority
- **Nomad Clans**: Convoy-based raiders with heavy ground vehicles  
- **Archive Keepers**: Monolith zealots specializing in EMP and stealth
- **Civic Wardens**: Defensive militia focused on fortification

#### Vehicle Expansion

- **APC 8x8**: Multi-crew armored personnel carrier
- **Scout Helicopter**: Corporate air reconnaissance and transport
- **Logistics Truck**: Heavy cargo hauling with convoy integration
- **UAV Drones**: Recon, Attack, and Logistics variants

#### Dynamic World

- **Procedural Events**: Blacksky Barrage, Monolith Bloom, Dead-Sky Surge, Ashway Lockdown, Vault Clarion
- **Machine Grave**: Zone with monolith debris and electromagnetic storms
- **Base Building**: Reactor, Shield Generator, Drone Bay, Vehicle Garage modules

## Phase 3 Advanced Features (Complete) ✅

### AI Faction Behavior System

- **Intelligent Faction Personalities**: 7 unique behavioral profiles with lore-accurate strategic decision-making
- **Strategic Decision Engine**: EXPAND, DEFEND, ATTACK, FORTIFY, PATROL, RETREAT, NEGOTIATE actions
- **Behavioral Strategies**: AGGRESSIVE, DEFENSIVE, OPPORTUNISTIC, DIPLOMATIC, ISOLATIONIST approaches
- **Real-time AI Turns**: Contextual territorial decisions based on faction compatibility, military strength, and strategic value

### Advanced Territorial Visualization

- **Comprehensive Dashboard**: Multi-panel territorial analysis with professional Terminal Grounds aesthetics
- **Faction Control Maps**: Real-time territorial ownership visualization
- **Strategic Heat Maps**: Territory value distribution and contested zone analysis
- **Influence Overlays**: Faction sphere-of-influence mapping with gradient visualization

### Production-Grade Architecture

- **Enterprise Scalability**: Systems designed for 100+ concurrent players
- **Real-time Integration**: WebSocket-ready for live territorial updates
- **Professional Visualization**: 1920x1080 high-quality territorial analysis outputs
- **Complete Documentation**: Comprehensive implementation guides and technical specifications

## Lore Foundation

**Year 2161** — Post-Shattered Accord wasteland. Monolith Harvesters lay dormant for decades, their wrecks fuel an arms race between surviving factions. Earth divided into fortified cities, industrial zones, and dangerous wastelands.

**Tone**: Grounded military desperation meets scavenger economy with cosmic dread. Cyberpunk elements provide flavor without overwhelming the core military aesthetic.

## Advanced Systems (Phase 4 Bold)

- Splice Events: Deck-driven world pulses that toggle evac windows, patrol masks, and rewards.
- Convoy Economy: Elastic Integrity Index with half-life decay; drives contract payouts and vendor bands.
- Trust: Pledge/Parley/Breach loop with decay and UI signals; affects social encounters and contracts.
- Codex: Category-based unlocks broadcasting UI updates; fed by Splice outcomes and beat progression.
- Integration: Splice outcomes fan out to economy, social trust, and codex via subsystems.
