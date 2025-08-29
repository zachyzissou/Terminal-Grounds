---
title: "UE5 Territorial Integration Architecture"
type: "spec"
domain: "technical"
status: "approved"
last_reviewed: "2025-08-28"
maintainer: "CTO Team"
tags: ["ue5", "integration", "territorial", "cpp", "blueprint", "websocket"]
related_docs: ["TERRITORY_CONTROL_SYSTEM.md", "TERMINAL_GROUNDS_MASTER_ROADMAP_2025.md", "IMPLEMENTATION_PRIORITY_MATRIX.md"]
---

# UE5 Territorial Integration Architecture

**Status:** READY FOR COMPILATION  
**Last Updated:** August 25, 2025  
**Phase:** Phase 2 - Gameplay Integration Complete

## Overview

The UE5 Territorial Integration provides a complete C++ framework for integrating player actions with the real-time territorial warfare system. The architecture links gameplay objectives to database updates and provides live visual feedback through HUD widgets.

## Module Architecture

### Module Dependencies

```mermaid
TGCore (Gameplay Logic)
    ↓ depends on
TGTerritorial (Database Integration)
    ↓ used by
TGUI (User Interface)
```

**Build Configuration:**

- **TGCore.Build.cs** - Includes "TGTerritorial" dependency
- **TGUI.Build.cs** - Includes "TGTerritorial" dependency
- **TGTerritorial** - Existing CTO Phase 1 module with database integration

## Core Classes

### 1. TerritorialExtractionObjective (TGCore Module)

**Location:** `Source/TGCore/Public/TerritorialExtractionObjective.h`

```cpp
UENUM(BlueprintType)
enum class ETerritorialActionType : uint8
{
    None = 0,
    Sabotage = 1,
    SupplyDelivery = 2,
    IntelligenceGathering = 3,
    InfrastructureAssault = 4
};

UCLASS(BlueprintType, Blueprintable)
class TGCORE_API ATerritorialExtractionObjective : public AActor
{
    GENERATED_BODY()

public:
    ATerritorialExtractionObjective();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    ETerritorialActionType ActionType = ETerritorialActionType::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 TargetTerritoryID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 TargetFaction = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    float InfluenceChange = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    FString ObjectiveDescription = TEXT("Complete territorial objective");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    bool bIsActive = true;

public:
    UFUNCTION(BlueprintCallable, Category = "Territorial Integration")
    void ApplyTerritorialInfluence();

    UFUNCTION(BlueprintCallable, Category = "Territorial Integration")
    bool IsObjectiveComplete() const;

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Integration")
    void OnTerritorialInfluenceApplied(bool bSuccess);

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Integration")
    void OnObjectiveActivated();

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Integration")
    void OnObjectiveCompleted();

private:
    UPROPERTY()
    class UTGTerritorialManager* TerritorialManager;

    bool bObjectiveCompleted = false;
};
```

**Implementation Features:**

- **Direct Database Integration** - Calls TGTerritorialManager for real-time updates
- **Blueprint Events** - Allows designers to hook custom logic
- **Faction-Specific Actions** - Each action type affects territorial influence differently
- **Validation** - Ensures objectives can only be completed once

### 2. TerritorialControlWidget (TGUI Module)

**Location:** `Source/TGUI/Public/TerritorialControlWidget.h`

```cpp
USTRUCT(BlueprintType)
struct TGUI_API FTerritorialDisplayData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    int32 TerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    FString TerritoryName = TEXT("");

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    int32 DominantFactionID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    FString DominantFactionName = TEXT("");

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    float ControlPercentage = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    bool bIsContested = false;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    FLinearColor FactionColor = FLinearColor::White;
};

UCLASS(BlueprintType, Blueprintable)
class TGUI_API UTerritorialControlWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UTerritorialControlWidget(const FObjectInitializer& ObjectInitializer);

protected:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Control")
    FString WebSocketServerURL = TEXT("ws://127.0.0.1:8765");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Control")
    float UpdateInterval = 1.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Territorial Control")
    TArray<FTerritorialDisplayData> TerritorialData;

    UPROPERTY(BlueprintReadOnly, Category = "Territorial Control")
    bool bIsConnectedToServer = false;

public:
    UFUNCTION(BlueprintCallable, Category = "Territorial Control")
    void ConnectToTerritorialServer();

    UFUNCTION(BlueprintCallable, Category = "Territorial Control")
    void DisconnectFromTerritorialServer();

    UFUNCTION(BlueprintCallable, Category = "Territorial Control")
    FTerritorialDisplayData GetTerritoryData(int32 TerritoryID) const;

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Control")
    void OnTerritorialDataUpdated(const TArray<FTerritorialDisplayData>& NewData);

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Control")
    void OnTerritoryControlChanged(int32 TerritoryID, int32 NewControllingFaction);

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Control")
    void OnTerritoryContested(int32 TerritoryID, bool bContested);

private:
    UPROPERTY()
    class UTGTerritorialManager* TerritorialManager;

    FTimerHandle UpdateTimerHandle;

    void UpdateTerritorialData();
    void ProcessWebSocketMessage(const FString& Message);
    FString GetTerritoryName(int32 TerritoryID) const;
    FLinearColor GetFactionColor(int32 FactionID) const;
};
```

**Widget Features:**

- **Real-Time Updates** - WebSocket integration for live territorial data
- **Faction Theming** - Automatic color coding based on faction control
- **Designer-Friendly** - Blueprint events for custom UI implementations
- **Performance Optimized** - Configurable update intervals to manage network traffic

## Integration Workflow

### 1. Objective Completion Flow

```mermaid
Player Interaction → TerritorialExtractionObjective → TGTerritorialManager → Database Update → WebSocket Broadcast → All Player HUDs Updated
```

**Step-by-Step:**

1. Player completes objective (Blueprint or C++ trigger)
2. `ApplyTerritorialInfluence()` called on TerritorialExtractionObjective
3. TGTerritorialManager processes database update (0.04ms query)
4. Database change triggers WebSocket server broadcast
5. All connected TerritorialControlWidget instances receive update
6. HUD displays new territorial control state

### 2. Real-Time HUD Updates

```mermaid
WebSocket Message → TerritorialControlWidget → Blueprint Event → UI Update
```

**Message Flow:**

1. WebSocket server broadcasts territorial change
2. TerritorialControlWidget receives and parses message
3. `OnTerritorialDataUpdated` Blueprint event fires
4. Designer-created UI elements update with new data

## Blueprint Integration Guide

### Setting Up Territorial Objectives

1. **Create Blueprint from ATerritorialExtractionObjective:**

```cpp
// In Blueprint Construction Script:
ActionType = ETerritorialActionType::Sabotage;
TargetTerritoryID = 1; // Metro Region
TargetFaction = 1; // Sky Bastion Directorate
InfluenceChange = 15.0f;
ObjectiveDescription = "Sabotage Directorate infrastructure in Metro Region";
```

2. **Implement Completion Logic:**

```cpp
// In Blueprint Event Graph:
Event OnPlayerInteraction → ApplyTerritorialInfluence() → OnTerritorialInfluenceApplied
```

3. **Handle Objective Events:**

```cpp
// Override Blueprint Events:
OnObjectiveActivated → Show objective UI
OnObjectiveCompleted → Hide objective, show success message
OnTerritorialInfluenceApplied → Update mission progress
```

### HUD Widget Implementation

1. **Create Blueprint from UTerritorialControlWidget:**

```cpp
// In Widget Blueprint:
WebSocketServerURL = "ws://127.0.0.1:8765"
UpdateInterval = 2.0f // Update every 2 seconds
```

2. **Implement UI Updates:**

```cpp
// Override Blueprint Events:
OnTerritorialDataUpdated → Update territory control bars
OnTerritoryControlChanged → Show faction change notification
OnTerritoryContested → Display contested territory warning
```

3. **Add to Player HUD:**

```cpp
// In Player Controller BeginPlay:
Create Widget → TerritorialControlWidget → Add to Viewport → ConnectToTerritorialServer
```

## Performance Optimization

### Database Integration

- **Connection Pooling** - TGTerritorialManager maintains persistent database connections
- **Query Optimization** - Pre-compiled prepared statements for common territorial operations
- **Caching** - Territorial data cached with configurable TTL for high-frequency queries

### Network Optimization

- **Update Batching** - Multiple territorial changes batched into single WebSocket messages
- **Delta Updates** - Only changed territorial data transmitted, not full state
- **Compression** - JSON message compression for large territorial updates

### Memory Management

- **Object Pooling** - TerritorialDisplayData structures pooled and reused
- **Weak References** - Widget references to avoid circular dependencies
- **Automatic Cleanup** - WebSocket connections automatically closed on widget destruction

## Testing and Validation

### Unit Testing

```bash
# Compile C++ classes
"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" TerminalGroundsEditor Win64 Development -project="C:\Users\Zachg\Terminal-Grounds\TerminalGrounds.uproject" -rocket -progress
```

### Integration Testing

```bash
# Start territorial server
python Tools/TerritorialSystem/territorial_websocket_server.py

# Run WebSocket connectivity test
python Tools/Testing/simple_websocket_test.py

# Run multiplayer stress test
python Tools/Testing/multiplayer_territorial_sync_test.py
```

### In-Editor Testing

1. **Compile Project** - Verify all C++ classes compile without errors
2. **Create Test Blueprints** - Instantiate TerritorialExtractionObjective and TerritorialControlWidget
3. **Test Objective Completion** - Verify database updates and WebSocket broadcasts
4. **Validate HUD Updates** - Confirm real-time territorial data display

## Troubleshooting

### Common Build Issues

**Missing TGTerritorial Dependency:**

```
Error: 'UTGTerritorialManager' not found
Solution: Add "TGTerritorial" to PublicDependencyModuleNames in .Build.cs files
```

**WebSocket Connection Failures:**

```
Error: Widget cannot connect to ws://127.0.0.1:8765
Solution: Ensure territorial_websocket_server.py is running and accessible
```

**Database Update Failures:**

```
Error: ApplyTerritorialInfluence() returns false
Solution: Verify Database/territorial_system.db exists and has proper permissions
```

## Future Enhancements

### Phase 3 Integration

- **AI Faction Behavior** - Integration with AI decision-making system
- **Advanced Visualization** - Territory heat maps and strategic overlays in UE5
- **Enhanced Networking** - Support for dedicated server deployment
- **Analytics Integration** - Player action tracking and territorial behavior analysis

---

**Architecture Status:** READY FOR COMPILATION AND TESTING  
**Integration Level:** Complete C++ framework with Blueprint support  
**Next Steps:** Compile project and begin in-editor testing
