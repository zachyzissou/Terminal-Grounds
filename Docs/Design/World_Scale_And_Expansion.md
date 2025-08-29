---
title: "World Scale And Expansion"
type: "reference"
domain: "process"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Documentation Team"
tags: []
related_docs: []
---

# World Scale & Expansion Concept

Lore Reference: See canonical region and IEZ details in docs/Lore/LORE_BIBLE.md#world and IDs in docs/Lore/lorebook.yml

## Overview

This document outlines the initial open world footprint, difficulty rings, and the expansion pathway to additional landmasses using in-fiction travel "tunnels" (boat/sub/plane), grounded in canon and designed for UE5 data-driven systems.

## Initial Footprint (v1)

- Regions (IDs from lorebook.yml): REG_IEZ, REG_TECH_WASTES, REG_CRIMSON_DOCKS, REG_METRO_A, REG_SKY_BASTION, REG_BLACK_VAULT
- Hardcore Rings inside IEZ:
  - REG_IEZ_RING_OUTER (H1): Learn-by-doing, reliable Field-grade tech bias
  - REG_IEZ_RING_MEDIAN (H2): Splice pressure, event overlays more frequent
  - REG_IEZ_RING_CORE (H3): Monolith anomalies, Phase Pockets, limited extraction
- Key POIs (cross-ref lorebook.yml/pois): POI_METEOR_SITE, POI_DRONE_HIVE, POI_VAULT_PERIMETER, POI_COMBINE_FORWARD_PAD, POI_NOMAD_CONVOY_CAMP, POI_WARDEN_FORT

## Expansion Model (v1.1+)

- Philosophy: Single-shard feel via world-partitioned hubs + travel tunnels to new maps.
- Travel tunnels (diegetic transitions):
  - Boat: Coastal routes from REG_CRIMSON_DOCKS to offshore wreck fields
  - Submersible: Deep-water sink sites (alien wreck access during EVT_HARMONIC_WINDOW)
  - Plane: Short-hop airlift between secured pads (Sky Bastion Directorate/Trivector Combine permits required)
- Cadence: Each expansion adds 1-2 biomes, 2-3 event variants, 1 secret-faction footprint

## UE5 Implementation Notes

- World Partition/HLODs: Base map uses WP; remote biomes ship as separate persistent levels
- Travel Tunnel Volumes: BP_TravelTunnel with prompt, loading movie, and arrival stubs
- Data Assets (Primary):
  - UDataAsset TG_RegionData: Id (REG_*), Bounds, H-Ring, FactionPresence
  - UPrimaryDataAsset TG_EventDefinition: Id (EVT_*), Triggers, Rewards, Risks
  - UPrimaryDataAsset TG_ExtractionPoint: Id, Conditions, Window (time/event)
- Subsystems:
  - UTGEventManagerSubsystem: schedules EVT_*; bias by region ring and time-of-day
  - UTGTravelSubsystem: resolves travel tunnels, validates permits, performs level switch
  - UTGHardcoreZoneComponent: applies H1/H2/H3 rules via volume overlap
- Tagging:
  - Gameplay Tags: Region.REG_*, Event.EVT_*, Faction.FCT_*, POI.POI_*
  - Asset Metadata: LoreID fields for traceability back to lorebook.yml

## Difficulty & Economy

- H1: Abundant Field-grade tech, low salvage value, lower augmentation risk
- H2: Splice pressure, higher value, misfire chance for unstable gear
- H3: Monolith anomalies, top-tier salvage, extraction scarcity, sanity/physio costs
- Events influence prices and spawn tables; convoy wars peak during EVT_CONVOY_REDLINE

## Faction Presence (examples)

- FCT_DIR at REG_SKY_BASTION (Sky Bastion Directorate: air corridor control; plane tunnels gating)
- FCT_VUL across REG_TECH_WASTES (Iron Vultures: salvage rights skirmishes)
- FCT_F77 as contracts at hot zones; flexible presence (The Seventy-Seven)
- FCT_CCB pilots prototype tunnels; early access to new biomes (Trivector Combine)
- FCT_VAR gatekeep EVT_VAULT_SIREN sites (Obsidian Archive: knowledge risk protocols)
- FCT_NOM control land tunnels (Roadborn Clans: convoy escorts and fees)
- FCT_CWD secure civilian tunnels and emergency corridors (Truce Wardens)
- Secret: FCT_NCH sightings spike during EVT_BLACKOUT_STORM in H2/H3

## Roadmap Hooks

- v1.0: Ship IEZ with three rings, 6 core POIs, baseline events
- v1.1: Add Offshore Wreck Fields (boat) + 2 events; seed Monolith Sentinels
- v1.2: Add Subduction Trench (sub) + Harmonic sub-surface POIs; Archivist arc
- v1.3: Add Highlands Airbridge (plane) + Directorate/Combine treaty crisis arc

## Testing & Validation

- Docs Gate: Link check for REG_*/EVT_*/POI_* IDs; glossary bans enforced
- UE: Automated smoke test spawns volumes and cycles one event per ring

```cpp
// Minimal UE scaffolding sketch (not compiled here)
UCLASS(BlueprintType)
class UTGRegionData : public UDataAsset {
  GENERATED_BODY()
public:
  UPROPERTY(EditDefaultsOnly) FName RegionId; // REG_*
  UPROPERTY(EditDefaultsOnly) FBox Bounds;
  UPROPERTY(EditDefaultsOnly) int32 HardcoreRing; // 1..3
  UPROPERTY(EditDefaultsOnly) TMap<FName,float> FactionPresence; // FCT_* -> 0..1
};

UCLASS(BlueprintType)
class UTGEventDefinition : public UPrimaryDataAsset {
  GENERATED_BODY()
public:
  UPROPERTY(EditDefaultsOnly) FName EventId; // EVT_*
  UPROPERTY(EditDefaultsOnly) TArray<FName> TriggerTags; // time, weather, ring
  UPROPERTY(EditDefaultsOnly) TArray<FName> RewardTags; // loot tables
  UPROPERTY(EditDefaultsOnly) float RiskWeight;
};

UCLASS(Blueprintable, ClassGroup=(TG), meta=(BlueprintSpawnableComponent))
class UTGHardcoreZoneComponent : public UBoxComponent {
  GENERATED_BODY()
public:
  UPROPERTY(EditAnywhere) int32 HardcoreRing; // 1..3
};

UCLASS()
class UTGEventManagerSubsystem : public UGameInstanceSubsystem {
  GENERATED_BODY()
public:
  UFUNCTION(BlueprintCallable) void ScheduleEvents();
};
// Pseudocode generated by codewrx.ai
```
