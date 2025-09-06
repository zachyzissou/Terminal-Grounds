# Economic Warfare Victory System
## Terminal Grounds Alternative Victory Conditions

### Overview

The Economic Warfare Victory System provides alternative win paths that reward strategic economic play alongside traditional territorial control. This system creates diverse gameplay approaches while maintaining the core extraction shooter experience and preventing economic camping strategies.

### Core Victory Types

#### 1. Economic Dominance
- **Objective**: Control 75% of total convoy route economic value
- **Time Requirement**: 2 minutes sustained control
- **Strategy**: Focus on capturing high-value convoy routes
- **Counter-Strategies**: 
  - Form temporary alliances to share route control
  - Focus on disrupting high-value routes
  - Coordinate simultaneous raids on multiple routes

#### 2. Supply Monopoly
- **Objective**: Control 100% of convoy routes for a specific resource type
- **Time Requirement**: 3 minutes sustained control
- **Strategy**: Specialize in one resource type completely
- **Counter-Strategies**:
  - Develop alternative resource sources
  - Sabotage monopolized supply infrastructure
  - Form coalitions to break monopoly control

#### 3. Economic Collapse
- **Objective**: Reduce enemy faction economic output by 60%
- **Time Requirement**: 1.5 minutes sustained impact
- **Strategy**: Aggressive disruption of enemy economic infrastructure
- **Counter-Strategies**:
  - Diversify economic dependencies
  - Establish protected supply corridors
  - Counter-attack enemy economic infrastructure

#### 4. Trade Network
- **Objective**: Establish profitable routes across 5 territories with 80% connectivity
- **Time Requirement**: 2.5 minutes sustained network
- **Strategy**: Focus on territorial control and route optimization
- **Counter-Strategies**:
  - Target key network connection nodes
  - Establish competing trade networks
  - Control strategic territories to fragment network

#### 5. Resource Control
- **Objective**: Control 85% of a specific resource type
- **Time Requirement**: 2 minutes sustained control
- **Strategy**: Deep specialization in resource control
- **Counter-Strategies**:
  - Shift focus to alternative resource types
  - Develop resource efficiency technologies
  - Form resource-sharing agreements

#### 6. Convoy Supremacy
- **Objective**: Achieve 80% convoy operation supremacy
- **Time Requirement**: 2 minutes sustained supremacy
- **Strategy**: Master convoy operations and protection
- **Counter-Strategies**:
  - Specialize in convoy interception tactics
  - Develop fast-response raid teams
  - Use decoy convoys to confuse operations

### System Architecture

#### Core Components

1. **UTGEconomicVictorySubsystem**
   - World subsystem managing victory condition tracking
   - Real-time economic metrics calculation
   - Victory progress monitoring and events

2. **ATGEconomicVictoryGameMode** 
   - Game mode integration with existing systems
   - Session management and victory handling
   - Integration with territorial and convoy systems

3. **UTGEconomicVictoryWidget**
   - UI component for victory progress display
   - Real-time updates and threat warnings
   - Faction-specific and global views

4. **UTGEconomicVictoryBalance**
   - Developer settings for balance configuration
   - Anti-camping measures configuration
   - Faction-specific balance multipliers

#### Integration Points

**Territorial System Integration**:
- Victory conditions update when territorial control changes
- Route values affected by territorial bonuses
- Network connectivity calculated from territorial control

**Convoy Economy Integration**:
- Real-time tracking of route control and values
- Economic metrics updated on convoy outcomes
- Integrity index impacts victory calculations

**Extraction Objectives Integration**:
- Extraction completions contribute to economic metrics
- Territorial objectives affect route control
- Player actions directly impact victory progress

### Anti-Camping Measures

#### Active Engagement Requirements
- Minimum engagement threshold prevents passive strategies
- Required activities include:
  - Complete extraction objectives
  - Participate in convoy operations  
  - Engage in territorial combat

#### Camping Detection
- Progress monitoring tracks activity levels
- Penalties applied when engagement drops below threshold
- Dynamic objectives adapt to prevent predictable camping

#### Counter-Strategy System
- Each victory type has specific counter-strategies
- Time windows for applying counter-measures
- Effectiveness multipliers encourage active opposition

### Balance Design Principles

#### Diverse Strategic Approaches
- Multiple simultaneous victory paths available
- Different faction strengths favor different victory types
- Resource specialization vs. diversification trade-offs

#### Dynamic Adaptation
- Victory conditions adapt to territorial control changes
- Threat warnings allow for strategic pivots
- Counter-strategies create emergent gameplay

#### Satisfying Victory Feel
- Victory achievements feel earned through strategic play
- Time requirements prevent instant victories
- Clear progress indicators maintain engagement

### Configuration System

#### Victory Condition Balance
```cpp
struct FEconomicVictoryBalanceConfig
{
    float RequiredThreshold = 0.75f;    // Victory threshold
    float TimeRequirement = 120.0f;     // Time to hold condition
    int32 Priority = 1;                 // Victory priority
    bool bEnabled = true;               // Active/inactive
    float DifficultyMultiplier = 1.0f;  // Faction balance
    TArray<FString> CounterStrategies;  // Available counters
};
```

#### Anti-Camping Configuration  
```cpp
struct FAntiCampingConfig
{
    bool bEnableAntiCamping = true;
    float MinimumEngagementThreshold = 0.1f;
    float EngagementCheckInterval = 10.0f;
    float CampingPenaltyMultiplier = 0.5f;
    TArray<FString> RequiredActivities;
};
```

#### Faction Balance
- Per-faction difficulty multipliers
- Resource type specialization bonuses
- Victory type affinity settings

### Implementation Status

#### Phase 1: Core System ✅
- [x] Economic victory subsystem
- [x] Victory condition tracking
- [x] Basic UI components
- [x] Game mode integration

#### Phase 2: Balance & Polish ✅  
- [x] Developer settings configuration
- [x] Anti-camping measures
- [x] Counter-strategy system
- [x] Faction-specific balance

#### Phase 3: Integration Testing 🔄
- [ ] Full territorial system integration
- [ ] Convoy economy stress testing
- [ ] Multi-faction balance validation
- [ ] UI polish and optimization

### Usage Examples

#### Basic Victory Condition Setup
```cpp
// Create economic dominance condition
FEconomicVictoryCondition Condition;
Condition.VictoryType = EEconomicVictoryType::EconomicDominance;
Condition.RequiredThreshold = 0.75f;
Condition.TimeRequirement = 120.0f;
EconomicVictorySubsystem->RegisterVictoryCondition(Condition);
```

#### Victory Progress Monitoring
```cpp
// Get faction progress
FEconomicVictoryProgress Progress = EconomicVictorySubsystem->GetFactionVictoryProgress(
    FactionID, EEconomicVictoryType::EconomicDominance);

// Check for threats
FEconomicVictoryProgress ClosestVictory = EconomicVictorySubsystem->GetClosestVictoryToCompletion();
```

#### Counter-Strategy Application
```cpp
// Get available counter-strategies
TArray<FString> Strategies = EconomicVictorySubsystem->GetCounterStrategies(
    EEconomicVictoryType::SupplyMonopoly);

// Apply counter-strategy
EconomicVictorySubsystem->ApplyCounterStrategy(
    FactionID, EEconomicVictoryType::SupplyMonopoly, "Sabotage monopolized supply lines");
```

### Performance Considerations

#### Update Frequency
- Victory conditions checked every 5 seconds (configurable)
- Economic metrics calculated on-demand
- UI updates batched for performance

#### Scalability
- Supports 100+ concurrent players
- Efficient caching of economic metrics
- Minimal network traffic for progress updates

#### Memory Usage
- Victory progress stored per faction/type combination
- Cached economic metrics with invalidation
- Configurable cleanup of stale data

### Future Enhancements

#### Planned Features
- Dynamic victory condition generation
- Seasonal victory campaigns
- Cross-faction diplomatic victory conditions
- AI director for balanced opposition

#### Potential Extensions
- Economic intelligence warfare
- Supply chain sabotage missions
- Trade route diplomacy mechanics
- Economic faction progression systems

### Developer Notes

#### Key Design Decisions
1. **Time-based victories** prevent instant wins and allow counter-play
2. **Multiple simultaneous paths** encourage diverse strategies
3. **Anti-camping measures** require active engagement
4. **Counter-strategy system** ensures dynamic gameplay

#### Common Pitfalls
- Avoid making conditions too easy or too hard
- Balance between territorial and economic focus
- Ensure counter-strategies remain viable
- Test faction balance across all victory types

#### Testing Guidelines
- Multi-faction stress tests required
- Balance validation across 30+ minute sessions
- Counter-strategy effectiveness verification
- Performance testing with full player loads

---

This economic warfare victory system transforms Terminal Grounds from pure territorial warfare into a rich strategic experience where economic mastery provides equally satisfying paths to victory.