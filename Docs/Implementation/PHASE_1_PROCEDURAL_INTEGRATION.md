# Phase 1 + Procedural System Integration Guide

## Overview

This guide demonstrates how to integrate the Phase 1 playable vertical slice with the completed UTGProceduralWorldSubsystem to create dynamically generated combat environments with faction-specific buildings, details, and vegetation.

## System Integration Architecture

The integration combines:
1. **Phase 1 Combat Systems** - Player, enemies, mission objectives, HUD
2. **UTGProceduralWorldSubsystem** - Runtime generation of faction buildings and environmental details
3. **Existing IEZ Maps** - Base level geometry and navigation

## Completed Procedural System Features

### ✅ **Asset-Populated Generation**
- **Building Selection**: Uses Construction VOL1/2 and kb3d assets based on building type
- **Faction Materials**: Integrates Terminal Grounds faction materials (Human, Hybrid, Alien)
- **Detail Objects**: Spawns crates, containers, and props with faction coloring
- **Vegetation System**: Faction-specific vegetation density and placement

### ✅ **Type System Integration**
- **Canonical Types**: Uses proper `EFactionID` and `EControlPointType` from TerritorialTypes.h
- **Local Interface**: Maintains `ELocalFactionID` for subsystem interface without circular dependencies
- **Automatic Conversion**: Seamless conversion between local and canonical types

### ✅ **Faction-Specific Generation**
- **Directorate**: Clean corporate structures with blue materials
- **Free77**: Improvised resistance structures with red materials  
- **CivicWardens**: Neutral maintenance structures with gray/yellow materials
- **NomadClans**: Organic structures with hybrid materials
- **VulturesUnion**: Scavenged structures with alien materials

## Integration Methods

### Method 1: Console Command Integration

Add procedural generation to any existing level using console commands:

```cpp
// In ATGPlaytestGameMode::BeginPlay() or via console
void ATGPlaytestGameMode::GenerateProceduralEnvironment()
{
    if (UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>())
    {
        FProceduralGenerationRequest Request;
        Request.TerritoryID = 1;
        Request.TerritoryType = ELocalTerritoryType::District;
        Request.DominantFaction = ELocalFactionID::Directorate;
        Request.GenerationType = EProceduralGenerationType::All;
        Request.CenterLocation = FVector(0, 0, 0); // Level center
        Request.GenerationRadius = 5000.0f; // 50m radius
        
        ProceduralSystem->GenerateTerritory(Request);
    }
}
```

### Method 2: Mission-Based Generation

Integrate procedural generation with mission objectives:

```cpp
// In ATGPlaytestGameMode::InitializeMission()
void ATGPlaytestGameMode::InitializeMissionWithProcedural()
{
    // Standard mission setup
    InitializeMission();
    
    // Generate faction presence based on enemy faction
    ELocalFactionID EnemyFaction = DetermineEnemyFaction(); // Based on spawned enemies
    
    if (UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>())
    {
        // Generate enemy territory around enemy spawn points  
        for (int32 i = 0; i < EnemyTerritoryPoints.Num(); i++)
        {
            FProceduralGenerationRequest Request;
            Request.TerritoryID = i + 100; // Unique IDs for mission territories
            Request.DominantFaction = EnemyFaction;
            Request.CenterLocation = EnemyTerritoryPoints[i];
            Request.GenerationRadius = 2000.0f;
            Request.GenerationType = EProceduralGenerationType::Buildings; // Focus on tactical structures
            
            ProceduralSystem->GenerateTerritory(Request);
        }
    }
}
```

### Method 3: Dynamic Faction Control

Link procedural generation to territorial control changes:

```cpp
// Create dynamic territorial shifts during gameplay
void ATGPlaytestGameMode::OnTerritoryControlChanged(int32 TerritoryID, ELocalFactionID NewControllingFaction)
{
    if (UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>())
    {
        // Clear old faction structures
        ProceduralSystem->ClearTerritoryGeneration(TerritoryID, ELocalTerritoryType::ControlPoint);
        
        // Generate new faction structures
        FProceduralGenerationRequest Request;
        Request.TerritoryID = TerritoryID;
        Request.DominantFaction = NewControllingFaction;
        Request.CenterLocation = GetTerritoryCenter(TerritoryID);
        Request.GenerationRadius = 1500.0f;
        Request.GenerationType = EProceduralGenerationType::All;
        
        ProceduralSystem->GenerateTerritory(Request);
    }
}
```

## Level Setup Guide

### Step 1: Prepare IEZ Map
1. Open `Content/TG/Maps/IEZ/IEZ_District_Alpha.umap` or similar
2. Ensure NavMeshBoundsVolume covers entire area
3. Place ATGDemoSetup and ATGPlaytestExtractionZone as per Phase 1 guide
4. Set GameMode to ATGPlaytestGameMode

### Step 2: Add Procedural Generation Trigger
Create a Blueprint or C++ class to trigger generation:

**Blueprint Implementation:**
```blueprint
Event BeginPlay
├─ Get World Subsystem (UTGProceduralWorldSubsystem)
├─ Make ProceduralGenerationRequest
│   ├─ Territory ID: 1
│   ├─ Faction: Directorate
│   ├─ Center Location: (0,0,0)
│   ├─ Radius: 5000
│   └─ Type: All
└─ Generate Territory
```

**C++ Implementation:**
```cpp
// In level Blueprint or custom actor BeginPlay
void AProceduralTestTrigger::BeginPlay()
{
    Super::BeginPlay();
    
    if (UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>())
    {
        FProceduralGenerationRequest Request;
        Request.TerritoryID = 1;
        Request.DominantFaction = ELocalFactionID::Free77;
        Request.CenterLocation = GetActorLocation();
        Request.GenerationRadius = 3000.0f;
        Request.GenerationType = EProceduralGenerationType::All;
        
        bool bSuccess = ProceduralSystem->GenerateTerritory(Request);
        
        UE_LOG(LogTemp, Log, TEXT("Procedural generation %s"), 
               bSuccess ? TEXT("succeeded") : TEXT("failed"));
    }
}
```

### Step 3: Test Integration
1. **Compile Project** with new procedural system implementation
2. **Launch Level** with both Phase 1 and procedural systems
3. **Verify Generation**:
   - Buildings appear at specified locations
   - Faction materials applied correctly
   - Detail objects scattered appropriately
   - Vegetation density matches faction type
   - Navigation mesh accommodates new geometry

## Console Commands for Testing

Add these console commands for runtime testing:

```cpp
// In ATGPlaytestGameMode or custom developer commands
UFUNCTION(Exec, Category = "Procedural")
void GenerateTestTerritory(int32 TerritoryID = 1, int32 FactionID = 1)
{
    if (UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>())
    {
        FProceduralGenerationRequest Request;
        Request.TerritoryID = TerritoryID;
        Request.DominantFaction = (ELocalFactionID)FactionID;
        Request.CenterLocation = GetActorLocation(); // Player location
        Request.GenerationRadius = 2000.0f;
        Request.GenerationType = EProceduralGenerationType::All;
        
        ProceduralSystem->GenerateTerritory(Request);
    }
}

UFUNCTION(Exec, Category = "Procedural") 
void ClearTerritory(int32 TerritoryID = 1)
{
    if (UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>())
    {
        ProceduralSystem->ClearTerritoryGeneration(TerritoryID, ELocalTerritoryType::District);
    }
}
```

**Usage:**
- `GenerateTestTerritory 1 2` - Generate Free77 territory at ID 1
- `GenerateTestTerritory 2 1` - Generate Directorate territory at ID 2  
- `ClearTerritory 1` - Clear territory ID 1

## Asset Path Configuration

The system uses these asset fallback chains:

### Building Assets (Priority Order)
1. **Construction VOL1/2**: Primary building assets
2. **kb3d Mission to Minerva**: Large industrial structures
3. **Procedural Building Generator**: Modular components
4. **Engine Basic Shapes**: Guaranteed fallback

### Material Assets
1. **Terminal Grounds Materials**: `/Game/TG/Materials/[Human|Hybrid|Alien]/M_TG_*_Master`
2. **Engine Materials**: Basic shape materials and default materials

### Detail/Vegetation Assets
1. **StarterContent Props**: If available
2. **Engine Basic Shapes**: Guaranteed geometric primitives

## Performance Considerations

### Generation Optimization
- **Radius Limits**: Keep generation radius under 10,000 units (100m) for performance
- **Object Counts**: Default 8 buildings, 10-20 details, 10-30 vegetation per territory
- **Cleanup System**: Automatic cleanup when territories regenerate prevents memory leaks

### Integration Performance
- **Async Generation**: Consider making generation async for large territories
- **LOD Integration**: Generated objects should use LOD systems for distance culling
- **Collision Optimization**: Use simplified collision for procedural objects

## Troubleshooting

### Common Issues
1. **No Assets Spawn**: Check asset paths in logs, ensure Construction packs are available
2. **Materials Not Applied**: Verify Terminal Grounds material assets exist
3. **Navigation Issues**: Regenerate NavMesh after procedural generation
4. **Performance Drops**: Reduce generation radius or object counts

### Debug Logging
The system provides extensive logging:
- `LogTemp: Procedural generation succeeded/failed`
- `LogTemp: Selected mesh [path] for faction [ID]`
- `LogTemp: Generated [N] objects for territory [ID]`

Enable verbose logging with:
```cpp
UE_LOG(LogTemp, VeryVerbose, TEXT("Detailed procedural information"));
```

## Next Steps

### Enhanced Integration
1. **Faction UI Integration**: Show procedural territory control in existing HUD
2. **Mission Integration**: Generate objectives around procedural structures
3. **Dynamic Events**: Territorial battles that trigger regeneration
4. **Performance Profiling**: Optimize generation for larger scales

### Asset Enhancement
1. **Custom Faction Assets**: Replace fallbacks with Terminal Grounds-specific models
2. **Material Instances**: Create dynamic material instances with faction colors
3. **Procedural Decals**: Add faction insignia and territorial markers
4. **Sound Integration**: Faction-specific ambient audio

## Summary

The integration of Phase 1 combat systems with the completed UTGProceduralWorldSubsystem creates a powerful foundation for dynamic, faction-influenced environments. The system leverages existing Terminal Grounds assets while providing robust fallbacks, ensuring reliable generation across different asset availability scenarios.

This integration transforms static combat scenarios into dynamic, faction-influenced battlegrounds that can adapt to territorial control changes and provide varied replay experiences within the established Terminal Grounds universe.