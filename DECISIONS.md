# DECISIONS

## Core Architecture
- **Primary module**: Using TGCore as the primary game module via IMPLEMENT_PRIMARY_GAME_MODULE for simplicity; can split a thin TerminalGrounds module later if desired.
- **Engine**: UE 5.4 baseline. GAS (GameplayAbilitySystem) planned; MassAI/EQS later.
- **Data-driven**: Tables and Primary Data Assets will drive balance/content; placeholder CSVs first.
- **Server model**: Server-authoritative with client prediction and rewind buffers (~200ms target).

## Phase 2 Design Decisions
- **Tech Tiers**: Human (70%), Hybrid (25%), Alien (5%) drop rate distribution to maintain balance
- **Weapon Heat System**: Hybrid weapons use heat mechanics; Alien weapons use charge/phase systems
- **Faction Balance**: Each faction gets 25% spawn weight for Phase 2 content
- **EMP Mechanics**: Ion/EMP damage type affects shields, exosuits, and vehicles with temporary disable
- **Augment Rarity**: Cyberpunk augments are rare and distrusted outside cities (lore-accurate)
- **Vehicle Repair**: Field repair kits for ground vehicles, hangar required for aircraft
- **Power System**: Base modules use hierarchical power consumption (Shield > Drone > Garage > Workbench)
- **Concept Art**: Using neutral IP prompts for Midjourney/Stable Diffusion to avoid copyright issues

## Balance Philosophy
- Phase 1 weapons remain viable and common
- Alien tech is high-risk/high-reward with unpredictable mechanics  
- Hybrid tech bridges human reliability with alien power at cost of complexity
- Factions maintain distinct tactical preferences and equipment bias
