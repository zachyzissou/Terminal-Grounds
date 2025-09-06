# Economic Victory System Integration Example
## Complete Implementation Guide for Terminal Grounds

### System Overview

This document demonstrates how all components of the Economic Victory System work together to provide alternative win paths that reward economic strategy alongside territorial warfare.

### Core Integration Flow

```
Player Actions → Territorial Control → Convoy Routes → Economic Metrics → Victory Progress → Victory Achievement
     ↓                    ↓               ↓               ↓                ↓                ↓
Extraction      Territory Change    Route Control    Economic       Victory Status   Session End
Objectives      Events              Updates          Calculations   Updates         & Cleanup
```

### Component Architecture

#### 1. Subsystem Layer
```cpp
// World Subsystems (Persistent)
UTGEconomicVictorySubsystem    // Victory condition tracking
UTGConvoyEconomySubsystem      // Economic calculations  
UTerritorialSubsystem          // Territory management

// Game Instance Subsystems (Session)
UTGTrustSubsystem             // Faction relationships
UTGCodexSubsystem             // Achievement tracking
```

#### 2. Game Mode Layer
```cpp
ATGEconomicVictoryGameMode extends ATGGameMode
{
    // Session Management
    StartEconomicWarfareSession()
    EndEconomicWarfareSession() 
    HandleEconomicVictory()
    
    // Integration Events
    OnTerritorialControlChanged()
    OnConvoyRouteControlChanged()
    OnExtractionObjectiveCompleted()
}
```

#### 3. UI Layer
```cpp
UTGEconomicVictoryWidget extends UUserWidget
{
    // Real-time Display
    UpdateVictoryProgress()
    ShowThreatWarnings()
    DisplayCounterStrategies()
    
    // User Interaction
    SelectVictoryTarget()
    ApplyCounterStrategy()
}
```

### Victory Condition Examples

#### Example 1: Economic Dominance Victory

**Setup Phase**:
```cpp
// Game mode initializes victory conditions
FEconomicVictoryCondition Dominance;
Dominance.VictoryType = EEconomicVictoryType::EconomicDominance;
Dominance.RequiredThreshold = 0.75f;  // 75% route control
Dominance.TimeRequirement = 120.0f;   // Hold for 2 minutes
EconomicVictorySubsystem->RegisterVictoryCondition(Dominance);
```

**Gameplay Flow**:
1. **Player captures convoy routes** → `OnConvoyRouteControlChanged()` fired
2. **Economic metrics updated** → Route control percentage calculated  
3. **Victory progress tracked** → 75% threshold reached
4. **Time requirement begins** → 2-minute countdown starts
5. **Victory achieved** → `OnEconomicVictoryAchieved()` broadcast
6. **Session ends** → Victory announcement and cleanup

**Real-time Updates**:
```cpp
// Economic metrics calculation
FEconomicMetrics Metrics;
Metrics.RouteControlPercentage = ControlledValue / TotalValue;

// Victory progress update  
Progress.Progress = Metrics.RouteControlPercentage;
Progress.Status = EEconomicVictoryStatus::NearComplete;

// UI notification
OnVictoryProgressUpdated.Broadcast(FactionID, VictoryType, Progress.Progress);
```

#### Example 2: Supply Monopoly Victory

**Strategic Setup**:
```cpp
// Focus on specific resource type
FEconomicVictoryCondition Monopoly;
Monopoly.VictoryType = EEconomicVictoryType::SupplyMonopoly;
Monopoly.TargetResourceType = EResourceType::Intelligence;
Monopoly.RequiredThreshold = 1.0f;    // 100% control
Monopoly.TimeRequirement = 180.0f;    // Hold for 3 minutes
```

**Counter-Strategy Response**:
```cpp
// Enemy faction applies counter-strategy
TArray<FString> CounterStrategies = EconomicVictorySubsystem->GetCounterStrategies(
    EEconomicVictoryType::SupplyMonopoly);
    
// "Develop alternative resource sources"
EconomicVictorySubsystem->ApplyCounterStrategy(
    EnemyFactionID, 
    EEconomicVictoryType::SupplyMonopoly,
    CounterStrategies[0]
);

// This triggers gameplay effects that reduce monopoly effectiveness
```

### Anti-Camping Integration

#### Detection System
```cpp
// Check for passive play
void CheckForEconomicCamping(int32 FactionID)
{
    float EngagementLevel = CalculateEngagementLevel(FactionID);
    
    if (EngagementLevel < MinimumEngagementThreshold)
    {
        // Apply camping penalty
        float Penalty = CampingPenaltyMultiplier;
        ModifyVictoryProgress(FactionID, -Penalty);
        
        // Require specific activities
        TriggerRequiredActivities(FactionID, RequiredActivities);
    }
}
```

#### Required Activities
```cpp
FAntiCampingConfig AntiCamping;
AntiCamping.RequiredActivities = {
    TEXT("Complete extraction objectives"),
    TEXT("Participate in convoy operations"), 
    TEXT("Engage in territorial combat")
};
```

### Balance Configuration

#### Developer Settings Integration
```cpp
// Balance applied at runtime
UTGEconomicVictoryBalance* Balance = GetDefault<UTGEconomicVictoryBalance>();
Balance->ApplyBalanceToSubsystem(EconomicVictorySubsystem);

// Faction-specific multipliers
float FactionMultiplier = Balance->GetFactionVictoryMultiplier(FactionID);
AdjustedThreshold = BaseThreshold * FactionMultiplier;
```

#### Dynamic Difficulty
```cpp
// Resource type affects difficulty
EResourceType TargetResource = EResourceType::Intelligence;
float ResourceMultiplier = Balance->GetResourceTypeMultiplier(TargetResource);

// Intelligence is 20% harder to monopolize
float EffectiveThreshold = RequiredThreshold * ResourceMultiplier; // 1.0 * 1.2 = 1.2
```

### Real-World Gameplay Scenario

#### Faction Strategies

**Directorate (Economic Dominance)**:
- Focuses on capturing high-value convoy routes
- Uses territorial control to secure route bonuses
- Builds defensive positions around key economic zones

**Free77 (Supply Monopoly)**:  
- Specializes in Intelligence resource routes
- Uses mercenary efficiency for rapid route capture
- Employs hit-and-run tactics to disrupt competitors

**CorporateCombine (Trade Network)**:
- Establishes routes across multiple territories
- Uses corporate resources for network coordination
- Focuses on territorial expansion for connectivity

#### Dynamic Opposition

**Counter-Strategy Cycle**:
1. Directorate approaches Economic Dominance (75% progress)
2. System broadcasts threat warning to all factions
3. Free77 and CorporateCombine form temporary alliance
4. They apply "Coordinate simultaneous raids" counter-strategy
5. Directorate's route control drops, resetting victory timer
6. New strategic situation emerges with shifted power balance

### Performance Optimization

#### Update Batching
```cpp
// Victory conditions checked every 5 seconds
void Tick(float DeltaTime)
{
    if (CurrentTime - LastVictoryCheck >= VictoryCheckInterval)
    {
        EvaluateVictoryConditions(); // Batch all calculations
        UpdateAllFactionMetrics();   // Update cached data
        LastVictoryCheck = CurrentTime;
    }
}
```

#### Efficient Calculations
```cpp
// Cache expensive calculations
FEconomicMetrics CalculateMetrics(int32 FactionID)
{
    if (CachedMetrics.Contains(FactionID))
    {
        return CachedMetrics[FactionID]; // Return cached if valid
    }
    
    // Expensive calculation only when needed
    FEconomicMetrics NewMetrics = CalculateFullMetrics(FactionID);
    CachedMetrics.Add(FactionID, NewMetrics);
    return NewMetrics;
}
```

### Testing Scenarios

#### Victory Condition Testing
```cpp
// Test Economic Dominance
void TestEconomicDominance()
{
    // Setup: Give faction 75% route control
    SetFactionRouteControl(TestFactionID, 0.75f);
    
    // Verify: Progress should be at threshold
    FEconomicVictoryProgress Progress = GetVictoryProgress(TestFactionID, EconomicDominance);
    ensure(Progress.Progress >= 0.75f);
    
    // Test time requirement
    AdvanceTime(120.0f);
    ensure(Progress.Status == EEconomicVictoryStatus::Completed);
}
```

#### Balance Testing
```cpp
// Test faction multipliers
void TestFactionBalance()
{
    for (int32 FactionID = 0; FactionID < 7; ++FactionID)
    {
        // Each faction should have viable path to victory
        float TimeToVictory = SimulateOptimalPlay(FactionID);
        ensure(TimeToVictory > 300.0f && TimeToVictory < 900.0f); // 5-15 minutes
    }
}
```

### Integration Checklist

#### Required Dependencies
- [x] TGConvoyEconomySubsystem operational
- [x] TerritorialManager integration complete  
- [x] TerritorialExtractionObjective event binding
- [x] UI widget Blueprint implementation
- [x] Balance configuration in Project Settings

#### Validation Steps
- [x] Victory conditions register correctly
- [x] Economic metrics calculate accurately
- [x] UI updates reflect real-time progress
- [x] Counter-strategies apply appropriate effects
- [x] Anti-camping measures prevent passive play
- [x] Session management handles victory properly

### Conclusion

The Economic Victory System successfully transforms Terminal Grounds into a multi-layered strategic experience where economic mastery provides equally satisfying paths to victory alongside traditional territorial warfare. The system's architecture ensures scalability, balance, and dynamic gameplay while maintaining the core extraction shooter experience.

**Key Success Factors**:
1. **Tight Integration** - All systems work together seamlessly
2. **Balanced Design** - Multiple viable strategies with counters
3. **Active Engagement** - Anti-camping measures ensure dynamic play
4. **Clear Feedback** - Players understand progress and threats
5. **Configurable Balance** - Developers can fine-tune experience