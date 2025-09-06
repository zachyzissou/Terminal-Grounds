# Territorial Splice Event Integration Examples

This document provides examples of how to create splice events that respond to territorial warfare dynamics in Terminal Grounds.

## Overview

The UTGSpliceSubsystem has been extended to automatically trigger narrative events based on territorial control changes. This creates dynamic storytelling that responds to the territorial warfare system.

## New Trigger Types

### OnTerritorialControlChange
Triggered when territory changes hands between factions.

### OnTerritorialContested  
Triggered when a territory becomes contested or resolves from contested state.

### OnFactionDominance
Triggered when a faction gains control of multiple strategic territories in a region.

### OnTerritorialLoss
Triggered when a faction loses strategically important territory (Strategic Value >= 5).

## Context Variables Available

When territorial events trigger, the following context variables are available for splice event constraints:

- `TerritoryId` - Numeric ID of the territory
- `TerritoryName` - Human readable territory name
- `TerritoryType` - Type (region, district, zone, outpost)
- `PreviousControllerFactionId` - ID of previous controlling faction
- `PreviousControllerFactionName` - Name of previous controlling faction
- `NewControllerFactionId` - ID of new controlling faction  
- `NewControllerFactionName` - Name of new controlling faction
- `StrategicValue` - Strategic importance (1-10)
- `ResourceMultiplier` - Economic value multiplier
- `WasContested` - "true" if territory was previously contested
- `IsContested` - "true" if territory is currently contested
- `ConnectedTerritoryIds` - Comma-separated list of connected territory IDs
- `ConnectedTerritoryNames` - Comma-separated list of connected territory names

## Example Splice Event Cards

### Example 1: High-Value Territory Capture

```cpp
// Territory Control Change Event
Card.Id = "territorial_capture_major";
Card.DisplayName = FText::FromString("Strategic Victory");
Card.Description = FText::FromString("Your faction has secured control of a strategically vital territory. This victory will resonate throughout the region.");
Card.Triggers.Add(ETGSpliceTrigger::OnTerritorialControlChange);
Card.Weight = 3;

// Only trigger for high-value territories
Card.Constraints.Add("StrategicValue", "8,9,10");
Card.Constraints.Add("TerritoryType", "region,district");

// Outcomes
FTGSpliceOutcome PositiveOutcome;
PositiveOutcome.OutcomeId = "strategic_morale_boost";
PositiveOutcome.ReputationDelta = 50;
PositiveOutcome.ConvoyIntegrityDelta = 15.0f;
PositiveOutcome.UnlockCodexIds.Add("strategic_tactics_advanced");
Card.Outcomes.Add(PositiveOutcome);
```

### Example 2: Territory Becomes Contested

```cpp
// Contested Territory Event
Card.Id = "territory_contested_supply_lines";
Card.DisplayName = FText::FromString("Supply Lines Under Threat");
Card.Description = FText::FromString("Enemy forces are challenging your control. Supply convoys report increased resistance along this route.");
Card.Triggers.Add(ETGSpliceTrigger::OnTerritorialContested);
Card.Weight = 2;

// Only trigger when territory becomes contested (not when resolved)
Card.Constraints.Add("IsContested", "true");
Card.Constraints.Add("WasContested", "false");

FTGSpliceOutcome SupplyThreat;
SupplyThreat.OutcomeId = "supply_disruption";
SupplyThreat.ConvoyIntegrityDelta = -8.0f;
SupplyThreat.UnlockCodexIds.Add("contested_zone_tactics");
Card.Outcomes.Add(SupplyThreat);
```

### Example 3: Faction Dominance Achievement

```cpp
// Dominance Achievement Event
Card.Id = "regional_dominance_directorate";
Card.DisplayName = FText::FromString("Regional Supremacy");
Card.Description = FText::FromString("The Directorate has established dominance over this sector. Their corporate efficiency is reshaping the local power structure.");
Card.Triggers.Add(ETGSpliceTrigger::OnFactionDominance);
Card.Weight = 1; // Rare event

// Only for Directorate faction achieving dominance
Card.Constraints.Add("NewControllerFactionName", "Directorate");

FTGSpliceOutcome DominanceReward;
DominanceReward.OutcomeId = "corporate_expansion_bonus";
DominanceReward.ReputationDelta = 75;
DominanceReward.ConvoyIntegrityDelta = 20.0f;
DominanceReward.UnlockCodexIds.Add("corporate_hierarchy_advanced");
DominanceReward.UnlockCodexIds.Add("directorate_strategic_doctrine");
Card.Outcomes.Add(DominanceReward);
```

### Example 4: Strategic Territory Loss

```cpp
// Territorial Loss Event
Card.Id = "strategic_territory_lost";
Card.DisplayName = FText::FromString("Strategic Setback");
Card.Description = FText::FromString("The loss of this key position will reverberate through our operational network. Command is reassessing regional strategy.");
Card.Triggers.Add(ETGSpliceTrigger::OnTerritorialLoss);
Card.Weight = 2;

// Constraint to only high-value lost territories
Card.Constraints.Add("StrategicValue", "7,8,9,10");

FTGSpliceOutcome LossConsequence;
LossConsequence.OutcomeId = "strategic_reassessment";
LossConsequence.ReputationDelta = -30;
LossConsequence.ConvoyIntegrityDelta = -12.0f;
LossConsequence.UnlockCodexIds.Add("defensive_tactics_emergency");
Card.Outcomes.Add(LossConsequence);
```

## Integration Setup

### Automatic Integration

The territorial integration happens automatically when the UTGSpliceSubsystem initializes. The system will:

1. Find the UTGTerritorialManager in the current world
2. Bind to territorial control change events
3. Automatically trigger appropriate splice events when territorial changes occur

### Manual Integration Control

If you need to manually control the integration:

```cpp
// Get the splice subsystem
UTGSpliceSubsystem* SpliceSubsystem = GetWorld()->GetSubsystem<UTGSpliceSubsystem>();

// Initialize territorial integration manually
SpliceSubsystem->InitializeTerritorialIntegration();

// Or trigger territorial events directly
FTGTerritorialEventContext Context;
Context.TerritoryId = 123;
Context.TerritoryName = "Metro Junction Alpha";
Context.NewControllerFactionId = 2;
Context.StrategicValue = 8;
SpliceSubsystem->TriggerTerritorialEvents(ETGSpliceTrigger::OnTerritorialControlChange, Context);
```

## Design Principles

### Context-Driven Narrative

Territorial events provide rich context that allows splice events to tell specific, location-aware stories. Use the territory type, strategic value, and faction information to create targeted narratives.

### Cascading Events

The system automatically checks for dominance and loss conditions when territories change hands, creating natural story arcs where one territorial change can trigger multiple narrative events.

### Strategic Storytelling

Focus territorial splice events on the strategic implications of territorial control rather than just tactical combat. This creates a meta-narrative about the broader territorial war.

## Implementation Notes

### Performance Considerations

- The system uses existing TGTerritorialManager queries, so performance scales with the territorial system
- Connected territory calculations cache results where possible
- Event triggering respects existing splice system weighting and constraints

### Faction Integration

- The system works with any faction IDs and names provided by the territorial system
- Faction-specific events should use the faction name constraints for flexibility
- Consider faction personality and lore when designing territorial events

### Territory Hierarchy

- The system understands parent/child relationships between territories
- Connected territory logic considers both hierarchical and spatial relationships
- Use this for events that should cascade through regional control structures

This territorial integration creates a dynamic narrative layer that responds to the strategic gameplay, making each territorial campaign feel unique and story-driven.