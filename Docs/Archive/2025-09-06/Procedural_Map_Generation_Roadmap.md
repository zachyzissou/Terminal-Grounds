# Document Consolidated

> **Note**: This roadmap has been consolidated into the [Master Roadmap](/Docs/MASTER_ROADMAP.md)

---

---
title: "Procedural Map Generation Roadmap"
type: "reference"
domain: "process"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Documentation Team"
tags: []
related_docs: []
---

# Terminal Grounds Procedural Map Generation Roadmap

**Document Version**: 1.0  
**Date**: August 28, 2025  
**Status**: Next Phase Planning (Post Asset Generation Pipeline)  
**Dependencies**: Complete Asset Generation Pipeline, Territorial System Phase 3

## Executive Summary

Terminal Grounds procedural map generation represents a **revolutionary hybrid approach** combining AI-generated assets with territorial warfare-driven world generation. Unlike traditional procedural systems that rely on noise and algorithms alone, our system uses **faction control state** and **AI asset generation** to create meaningful, story-driven environments that respond to player actions.

`★ Insight ─────────────────────────────────────`
This system creates **living, reactive worlds** where territorial control directly shapes the environment. Players see immediate visual feedback from their territorial actions, creating a tight gameplay-narrative loop that's unique in the extraction shooter genre.
`─────────────────────────────────────────────────`

## Phase Positioning

### **CURRENT PHASE**: Asset Generation Pipeline Completion
- Achieving 100% success rate across all asset categories
- Fixing copyright violations and text corruption issues  
- Completing territorial asset production pipeline
- Status: Nearly complete (92%+ success rate achieved)

### **NEXT PHASE**: Procedural Map Generation Implementation
- **Prerequisite**: Completed asset generation pipeline
- **Integration Point**: Proven FLUX1-dev-fp8 parameters and workflows
- **Foundation**: Existing territorial warfare system (Phase 3 complete)

## System Architecture Overview

### **1. Foundation Layer (COMPLETED)**
```cpp
// Core subsystem implemented
UTGProceduralWorldSubsystem* ProceduralSystem;

// Test framework ready
ATGProceduralTestActor* TestActor; 

// Integration points established
UTerritorialManager* TerritorialManager;
```

**Status**: ✅ **Fully Implemented** - Build-ready C++ foundation with UE5 integration

### **2. Content Pipeline Integration (PLANNED)**

#### **AI-Generated Asset Integration**
- **Input**: Territorial control state + faction aesthetics
- **Process**: Use proven FLUX1-dev-fp8 generation pipeline
- **Output**: Faction-specific buildings, props, signage

```python
# Integration with existing proven pipeline
def generate_procedural_building(territory_info, faction_id):
    # Use existing FIXED_faction_vehicle_concepts.py approach
    prompt = f"faction building, {faction_id} architecture, Terminal Grounds"
    return generate_with_flux(prompt, PROVEN_PARAMS)
```

#### **Procedural Placement Algorithm**
```cpp
// Smart building distribution based on territorial data
FVector CalculateBuildingPlacement(const FTerritorialInfo& Territory, 
                                 int32 BuildingIndex, 
                                 ELocalFactionID ControllingFaction);
```

### **3. Real-Time Integration (PLANNED)**

#### **WebSocket Territorial Updates**
- **Connection**: Existing territorial_websocket_server.py (127.0.0.1:8765)
- **Trigger**: Faction control changes
- **Response**: Automatic environment regeneration

```cpp
void UTGProceduralWorldSubsystem::OnTerritorialInfluenceChanged(
    int32 TerritoryID, 
    ELocalTerritoryType TerritoryType, 
    int32 NewDominantFaction)
{
    // Auto-regenerate when faction control shifts
    RegenerateTerritory(TerritoryID, TerritoryType, 
                       (ELocalFactionID)NewDominantFaction);
}
```

## Implementation Phases

### **Phase A: Content Foundation (Week 1-2)**
**Dependencies**: Completed asset generation pipeline

#### **A1: Mesh Libraries**
- [ ] Create basic faction building sets
  - Command posts, checkpoints, watchtowers per faction
  - Initial placeholder or generated meshes
- [ ] Faction material libraries
  - Directorate: Clean corporate (blues/grays)
  - Free77: Gritty resistance (reds/browns)
  - CivicWardens: Neutral maintenance (grays/yellows)

#### **A2: ComfyUI Integration** 
- [ ] Connect procedural system to proven generation scripts
- [ ] Implement on-demand building generation
- [ ] Use existing FLUX1-dev-fp8 success parameters

**Success Criteria**: Can generate and place faction-appropriate buildings in editor

### **Phase B: Territorial Integration (Week 3-4)**
**Dependencies**: Phase A complete + WebSocket territorial system

#### **B1: Real Data Connection**
- [ ] Connect to actual territorial database
- [ ] Replace test data with live TerritorialManager feeds
- [ ] Implement territory change event handling

#### **B2: Dynamic Updates**
- [ ] Real-time regeneration on faction control changes
- [ ] Smooth transition systems between faction aesthetics
- [ ] Performance optimization for large-scale updates

**Success Criteria**: Environment automatically updates when territorial control changes

### **Phase C: Enhanced Generation (Week 5-6)**
**Dependencies**: Phase B operational

#### **C1: Landscape Modification**
- [ ] Faction-specific terrain modifications
  - Directorate: Geometric terraforming  
  - Free77: Industrial scarring/damage
  - CivicWardens: Maintenance attempts
- [ ] Environmental storytelling elements

#### **C2: Detail Systems**
- [ ] Procedural faction signage and propaganda
- [ ] Dynamic lighting systems per faction
- [ ] Resource node placement based on territory type

**Success Criteria**: Rich, detailed environments that tell the territorial story

### **Phase D: Production Optimization (Week 7-8)**
**Dependencies**: Phase C feature-complete

#### **D1: Performance**
- [ ] Async generation to prevent frame drops
- [ ] LOD system for distant procedural content
- [ ] Memory management for large territories

#### **D2: Persistence**
- [ ] Save/load system for generated content
- [ ] Version control for procedural changes
- [ ] Multiplayer synchronization

**Success Criteria**: Production-ready performance for 100+ player servers

## Technical Integration Points

### **Asset Generation Pipeline Integration**
```python
# Leverage existing proven workflows
PROVEN_PARAMS = {
    "sampler": "heun", 
    "scheduler": "normal",
    "cfg": 3.2,
    "steps": 25
}

# Use existing FIXED scripts as foundation
def generate_territorial_asset(faction_id, building_type, territory_data):
    # Building on FIXED_faction_vehicle_concepts.py approach
    # 100% success rate methodology
```

### **Territorial System Integration**
```cpp
// Existing territorial data structures ready for integration
struct FTerritorialInfo {
    int32 TerritoryID;
    ETerritoryType TerritoryType;
    ETerritoryResourceType ResourceType; // Military/Economic/Strategic
    float StrategicValue;
    // Ready for procedural system consumption
};
```

### **UE5 Performance Considerations**
- **World Partition** compatibility for large procedural worlds
- **Nanite** support for high-poly generated buildings  
- **Lumen** integration for dynamic faction lighting
- **Chaos Physics** for destructible procedural elements

## Risk Mitigation

### **Technical Risks**
1. **Asset Generation Dependency**: Procedural system depends on stable asset pipeline
   - **Mitigation**: Use placeholder assets initially, swap to generated assets when ready
   
2. **Performance at Scale**: Large territorial changes could cause hitches
   - **Mitigation**: Async generation, territorial change batching, LOD systems

3. **Content Quality Consistency**: AI-generated content may vary in quality
   - **Mitigation**: Quality validation pipeline, curated asset libraries, fallback systems

### **Integration Risks**
1. **WebSocket Territorial Data**: Dependency on external territorial server
   - **Mitigation**: Offline mode, cached territorial data, graceful degradation

2. **UE5 Version Compatibility**: System depends on specific UE5.6 features
   - **Mitigation**: Version testing, compatibility layers, documentation

## Success Metrics

### **Phase Success Indicators**
- **Phase A**: 95%+ successful building generation and placement
- **Phase B**: Real-time territorial updates working within 500ms
- **Phase C**: Rich environmental detail without performance degradation
- **Phase D**: Production-ready for 100+ concurrent players

### **Player Experience Goals**
- **Immediate Visual Feedback**: Territorial control changes visible within seconds
- **Meaningful Aesthetics**: Faction control creates distinctive environments
- **Performance**: No noticeable impact on extraction shooter gameplay

## Next Actions

### **Immediate (Current Asset Pipeline Phase)**
1. **Complete asset generation pipeline** to 100% success rate
2. **Document proven generation parameters** and workflows
3. **Create asset library structure** for procedural system consumption

### **Phase Transition (Asset Pipeline → Procedural Generation)**
1. **Review this roadmap** with development team
2. **Prioritize Phase A implementation** based on current asset generation status
3. **Prepare test environments** for procedural generation validation

---

**Document Owner**: AI Development Team  
**Review Cycle**: Weekly during active development  
**Next Review**: Upon asset generation pipeline completion