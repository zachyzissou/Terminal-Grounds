# Territorial Trust System Integration Guide

## Overview

The enhanced UTGTrustSubsystem now provides comprehensive territorial action tracking that creates emergent social gameplay around territorial control. This system integrates seamlessly with the existing TerritorialExtractionPoint and TGTerritorialManager systems.

## New Territorial Trust Actions

### 1. Territorial Cooperation
**Function**: `RecordTerritorialCooperation(PlayerA, PlayerB, TerritoryID, TrustBonus = 0.08f)`

**When to Use**:
- Players defend each other's controlled territory
- Joint territorial capture operations
- Coordinated territorial defense actions

**Contextual Modifiers**:
- **Contested Territory**: +50% trust bonus (high-risk cooperation)
- **Enemy Territory**: +25% trust bonus (cooperation under adversity)

**Example Integration**:
```cpp
// In TerritorialExtractionPoint when players cooperate during extraction
if (HelperPlayer && ExtractingPlayer)
{
    if (UTGTrustSubsystem* TrustSystem = GetWorld()->GetGameInstance()->GetSubsystem<UTGTrustSubsystem>())
    {
        TrustSystem->RecordTerritorialCooperation(
            HelperPlayer->GetName(), 
            ExtractingPlayer->GetName(), 
            TerritoryID, 
            0.08f
        );
    }
}
```

### 2. Territorial Betrayal
**Function**: `RecordTerritorialBetrayal(PlayerA, PlayerB, TerritoryID, TrustPenalty = 0.6f)`

**When to Use**:
- Player attacks trusted ally within territorial boundaries
- Sabotage of ally's territorial operations
- Breaking territorial agreements

**Contextual Modifiers**:
- **Allied Territory**: +80% penalty severity (betrayal in safe zone)
- **Multiple Betrayals**: Escalating decay rate (up to 5x normal)

**Mechanical Effects**:
- Breaks active pledges immediately
- Increases trust decay rate permanently
- Affects faction relations if players are faction representatives

### 3. Extraction Assistance
**Function**: `RecordExtractionAssistance(Helper, Assisted, ExtractionPointID, TrustBonus = 0.10f)`

**When to Use**:
- Player provides cover during another's extraction
- Shared extraction zone defense
- Emergency extraction rescue operations

**Special Features**:
- **Contested Zones**: Double trust bonus (2x multiplier)
- **Pledge Restoration**: 3+ assists with high trust (>0.5) can restore broken pledges
- **Highest Cooperation Value**: +2.0 cooperation score per assist

**Example Integration**:
```cpp
// In TerritorialExtractionPoint::CompleteExtraction()
if (PlayersWhoHelped.Num() > 0)
{
    for (APawn* Helper : PlayersWhoHelped)
    {
        TrustSystem->RecordExtractionAssistance(
            Helper->GetName(),
            CurrentExtractingPlayer->GetName(),
            TerritoryID,
            0.10f
        );
    }
}
```

### 4. Boundary Respect
**Function**: `RecordBoundaryRespect(PlayerA, PlayerB, NeutralZoneID, TrustGain = 0.04f)`

**When to Use**:
- Players respect neutral zone boundaries
- Non-aggression in designated safe areas
- Honoring territorial agreements

**Design Philosophy**: Small but consistent trust building through respectful behavior.

### 5. Supply Route Protection
**Function**: `RecordSupplyRouteProtection(Protector, Convoy, TrustBonus = 0.06f)`

**When to Use**:
- Escort missions for supply convoys
- Protection during resource transport
- Convoy route security operations

## Territorial Trust Modifiers

### Dynamic Trust Calculation
The system provides contextual trust modifiers based on territorial state:

```cpp
float UTGTrustSubsystem::GetTerritorialTrustModifier(PlayerA, PlayerB, TerritoryID)
```

**Modifier Components**:
- **Base Modifier**: 1.0 + (CooperationScore × 0.1) [10% per cooperation point]
- **Betrayal Penalty**: -15% per territorial betrayal (minimum 30% effectiveness)
- **Extraction Assist Bonus**: +5% per successful extraction assist
- **Final Range**: Clamped between 20% and 300% effectiveness

### Trust Decay System

**Territorial Context Decay Rules**:
- **No Decay**: Recent activity (< 24 hours)
- **Standard Decay**: Base 0.1% per hour after 48 hours inactivity
- **Accelerated Decay**: 
  - Contested territories: +50% decay rate
  - Post-betrayal: Custom escalating rate (up to 5x)
- **Cooperation Protection**: High cooperation (>5.0) reduces decay by 30%

## Integration Points

### 1. TerritorialExtractionPoint Integration

**Key Integration Methods**:
```cpp
// During extraction start
void ATerritorialExtractionPoint::StartExtraction(APawn* Player)
{
    // Apply territorial trust modifiers to extraction time
    float TrustModifier = TrustSystem->GetTerritorialTrustModifier(
        Player->GetName(), 
        GetNearestAlly()->GetName(), 
        TerritoryID
    );
    
    CurrentExtractionTime = BaseExtractionTime / TrustModifier;
}

// During contested extraction
void ATerritorialExtractionPoint::OnContestationBegin()
{
    // Track territorial betrayals
    for (APawn* ContestingPlayer : ContestingPlayers)
    {
        if (IsPlayerBetrayingAlly(ContestingPlayer))
        {
            TrustSystem->RecordTerritorialBetrayal(
                ContestingPlayer->GetName(),
                CurrentExtractingPlayer->GetName(),
                TerritoryID
            );
        }
    }
}
```

### 2. Faction Relations Integration

**Automatic Faction Impact**:
- Territorial betrayals between faction members affect faction relations
- Extraction assistance can strengthen faction alliances
- Cooperation scores influence siege alliance formation

### 3. UI Integration Recommendations

**Trust Display Enhancements**:
- Territorial cooperation badges
- Betrayal warning indicators
- Extraction assist history
- Trust modifier tooltips showing territorial context

## Gameplay Balance Features

### 1. Emergent Social Dynamics
- **Trust Networks**: Players with high cooperation scores become valuable allies
- **Reputation Systems**: Territorial betrayal count becomes public information
- **Alliance Formation**: Extraction assists create natural squad formation incentives

### 2. Risk/Reward Scaling
- **High-Risk Cooperation**: Contested territory cooperation provides maximum trust gain
- **Betrayal Consequences**: Territorial betrayals have lasting mechanical effects
- **Trust Recovery**: Multiple paths for rebuilding damaged relationships

### 3. Faction-Specific Bonuses
The system supports faction-specific territorial trust bonuses (currently placeholder):
- **Directorate**: Bonus trust in corporate territories
- **Free77**: Bonus trust in contested zones
- **NomadClans**: Bonus trust in wasteland territories
- **CivicWardens**: Bonus trust in civilian areas

## Event System

**New Broadcast Events**:
- `OnTerritorialCooperation`: Real-time cooperation notifications
- `OnTerritorialBetrayal`: Betrayal alerts with context
- `OnExtractionAssistance`: Assistance recognition
- `OnBoundaryRespect`: Respect acknowledgment

**Integration with Splice Events**:
These territorial trust actions can trigger Splice Events, creating narrative consequences for player social behavior in territorial contexts.

## Performance Considerations

**Optimization Features**:
- Territorial manager integration uses cached queries
- Trust decay processing batched with existing siege decay
- Contextual modifiers calculated on-demand
- Thread-safe territorial data access

## Future Extensions

**Planned Enhancements**:
1. **AI Faction Behavior**: AI factions respond to player trust patterns
2. **Dynamic Trust Zones**: Trust modifiers shift based on territorial control
3. **Predictive Alliance System**: AI suggests alliance formation based on trust patterns
4. **Cross-Session Persistence**: Trust relationships persist across game sessions

## Testing Integration

**Recommended Testing Scenarios**:
1. **Cooperation Chains**: Multiple players assisting same extraction
2. **Betrayal Cascades**: Trust network collapse from single betrayal
3. **Territory Control Shifts**: Trust modifier changes during territorial capture
4. **Long-term Relationship Evolution**: Trust decay and recovery over extended play

This system creates compelling social gameplay where territorial actions have lasting consequences on player relationships, encouraging both cooperation and strategic betrayal within the Terminal Grounds extraction shooter framework.