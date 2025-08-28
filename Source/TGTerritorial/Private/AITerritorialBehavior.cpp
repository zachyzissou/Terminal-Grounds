// Copyright Terminal Grounds. All Rights Reserved.

#include "AITerritorialBehavior.h"
#include "Engine/World.h"
#include "TerritorialManager.h"

UAITerritorialBehavior::UAITerritorialBehavior()
{
    FactionID = 0;
    AggressionLevel = 0.5f;
    DefensiveBonus = 1.0f;
    EconomicFocus = 0.5f;
    TechnologicalFocus = 0.5f;
    LastDecisionTime = FDateTime::Now();
}

void UAITerritorialBehavior::UpdateTerritorialAI(const FTerritorialWorldState& WorldState)
{
    // Stub implementation - analyze threats and make decisions
    TArray<FTerritorialThreat> CurrentThreats = AnalyzeThreats(WorldState);
    FTerritorialDecision Decision = MakeStrategicDecisionWithThreats(WorldState, CurrentThreats);
    
    if (!Decision.DecisionType.IsEmpty())
    {
        PendingDecisions.Add(Decision);
    }
    
    LastDecisionTime = FDateTime::Now();
}

TArray<FTerritorialThreat> UAITerritorialBehavior::AnalyzeThreats(const FTerritorialWorldState& WorldState)
{
    TArray<FTerritorialThreat> Threats;
    
    // Stub implementation - basic threat detection
    for (const auto& RegionPair : WorldState.RegionStates)
    {
        const FTerritorialState& RegionState = RegionPair.Value;
        
        // Check if we're losing influence in territories we control
        if (RegionState.DominantFaction == FactionID && RegionState.bIsContested)
        {
            FTerritorialThreat Threat;
            Threat.TargetTerritoryID = RegionPair.Key;
            Threat.TargetTerritoryType = ETerritoryType::Region;
            Threat.ThreatLevel = 70; // High threat for contested controlled territory
            Threat.ThreatType = TEXT("territorial_loss");
            Threat.ThreatDetected = FDateTime::Now();
            Threats.Add(Threat);
        }
    }
    
    return Threats;
}

FTerritorialDecision UAITerritorialBehavior::MakeStrategicDecisionWithThreats(const FTerritorialWorldState& WorldState, const TArray<FTerritorialThreat>& Threats)
{
    FTerritorialDecision Decision;
    
    // Stub implementation - basic decision making
    if (Threats.Num() > 0)
    {
        // Prioritize defending threatened territories
        const FTerritorialThreat& HighestThreat = Threats[0];
        Decision.DecisionType = TEXT("defensive");
        Decision.TargetTerritoryID = HighestThreat.TargetTerritoryID;
        Decision.TargetTerritoryType = HighestThreat.TargetTerritoryType;
        Decision.Priority = HighestThreat.ThreatLevel;
        Decision.ResourcesCommitted = FMath::Clamp(HighestThreat.ThreatLevel, 30, 80);
        Decision.Reasoning = FString::Printf(TEXT("Defending territory %d from %s"), 
                                           HighestThreat.TargetTerritoryID, 
                                           *HighestThreat.ThreatType);
    }
    else if (AggressionLevel > 0.6f)
    {
        // Aggressive expansion when no threats
        Decision.DecisionType = TEXT("expansion");
        Decision.Priority = 40;
        Decision.ResourcesCommitted = FMath::RoundToInt(AggressionLevel * 60.0f);
        Decision.Reasoning = TEXT("Opportunistic expansion");
    }
    
    return Decision;
}

TArray<int32> UAITerritorialBehavior::GetPreferredTargets(const FTerritorialWorldState& WorldState)
{
    TArray<int32> PreferredTargets;
    
    // Stub implementation - return territories adjacent to our controlled ones
    for (const auto& RegionPair : WorldState.RegionStates)
    {
        if (RegionPair.Value.DominantFaction != FactionID && !RegionPair.Value.bIsContested)
        {
            PreferredTargets.Add(RegionPair.Key);
        }
    }
    
    return PreferredTargets;
}

bool UAITerritorialBehavior::ShouldDefendTerritory(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialThreat& Threat)
{
    // Always defend if threat level is high or if we have defensive bonuses
    return Threat.ThreatLevel > 50 || DefensiveBonus > 1.2f;
}

// UAITerritorialManager Implementation
UAITerritorialManager::UAITerritorialManager()
{
    // Initialize AI behaviors for all factions
}

void UAITerritorialManager::InitializeFactionalAI()
{
    // Create AI behaviors for each faction (1-7)
    FactionAIs.Empty();
    
    for (int32 FactionIndex = 1; FactionIndex <= 7; ++FactionIndex)
    {
        UAITerritorialBehavior* FactionAI = NewObject<UAITerritorialBehavior>(this);
        if (FactionAI)
        {
            // Configure faction-specific AI parameters
            FactionAI->FactionID = FactionIndex;
            
            // Set faction-specific aggression levels (can be configured via data tables later)
            switch (FactionIndex)
            {
                case 1: // Directorate - Moderate aggression
                    FactionAI->AggressionLevel = 0.6f;
                    FactionAI->DefensiveBonus = 1.2f;
                    break;
                case 2: // Free77 - High aggression
                    FactionAI->AggressionLevel = 0.8f;
                    FactionAI->DefensiveBonus = 0.9f;
                    break;
                case 3: // Corporate Combine - Economic focus
                    FactionAI->AggressionLevel = 0.4f;
                    FactionAI->EconomicFocus = 0.8f;
                    break;
                default: // Others - Balanced
                    FactionAI->AggressionLevel = 0.5f;
                    break;
            }
            
            FactionAIs.Add(FactionIndex, FactionAI);
        }
    }
}

void UAITerritorialManager::UpdateAIDecisions(const FTerritorialWorldState& WorldState)
{
    for (auto& FactionAIPair : FactionAIs)
    {
        if (FactionAIPair.Value)
        {
            FactionAIPair.Value->UpdateTerritorialAI(WorldState);
        }
    }
}

void UAITerritorialManager::ProcessAIActions(float DeltaTime)
{
    for (auto& FactionAIPair : FactionAIs)
    {
        UAITerritorialBehavior* FactionAI = FactionAIPair.Value;
        if (!FactionAI) continue;
        
        // Process pending decisions with execution delays
        for (int32 i = FactionAI->PendingDecisions.Num() - 1; i >= 0; --i)
        {
            FTerritorialDecision& Decision = FactionAI->PendingDecisions[i];
            Decision.ExecutionDelay -= DeltaTime;
            
            if (Decision.ExecutionDelay <= 0.0f)
            {
                ExecuteAIDecision(Decision);
                FactionAI->PendingDecisions.RemoveAt(i);
            }
        }
    }
}

void UAITerritorialManager::NotifyTerritorialChange(const FTerritorialUpdate& Update)
{
    // Notify all faction AIs about territorial changes so they can react
    for (auto& FactionAIPair : FactionAIs)
    {
        if (FactionAIPair.Value)
        {
            // AI can analyze this update and adjust its strategy
            // For now, just trigger a re-evaluation on the next update cycle
        }
    }
}

TArray<FTerritorialDecision> UAITerritorialManager::GetPendingAIDecisions()
{
    TArray<FTerritorialDecision> AllDecisions;
    
    for (auto& FactionAIPair : FactionAIs)
    {
        if (FactionAIPair.Value)
        {
            AllDecisions.Append(FactionAIPair.Value->PendingDecisions);
        }
    }
    
    return AllDecisions;
}

UAITerritorialBehavior* UAITerritorialManager::GetFactionAI(int32 FactionID)
{
    UAITerritorialBehavior** FoundAI = FactionAIs.Find(FactionID);
    return FoundAI ? *FoundAI : nullptr;
}

void UAITerritorialManager::ExecuteAIDecision(const FTerritorialDecision& Decision)
{
    // Stub implementation - would interact with territorial manager to execute the decision
    UE_LOG(LogTemp, Log, TEXT("AI Executing Decision: %s for Territory %d"), 
           *Decision.DecisionType, Decision.TargetTerritoryID);
    
    // In a full implementation, this would:
    // 1. Convert AI decision to territorial influence changes
    // 2. Apply those changes through the territorial manager
    // 3. Trigger events for the game systems to respond
}

// Proper implementations for UAITerritorialBehavior functions

float UAITerritorialBehavior::EvaluateTerritorialValue(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState)
{
    float BaseValue = 50.0f;
    
    // Check if this territory is in our region states
    if (const FTerritorialState* State = WorldState.RegionStates.Find(TerritoryID))
    {
        // Higher value if we already control it
        if (State->DominantFaction == FactionID)
        {
            BaseValue += 30.0f;
        }
        
        // Lower value if heavily contested
        if (State->bIsContested)
        {
            BaseValue -= 20.0f;
        }
        
        // Factor in strategic importance based on territory type
        if (TerritoryType == ETerritoryType::Region)
        {
            BaseValue += 20.0f; // Regions are more valuable
        }
    }
    
    // Apply faction-specific modifiers
    BaseValue *= (EconomicFocus + TechnologicalFocus) / 2.0f;
    
    return FMath::Clamp(BaseValue, 10.0f, 100.0f);
}

TArray<FTerritorialThreat> UAITerritorialBehavior::IdentifyThreats(const FTerritorialWorldState& WorldState)
{
    TArray<FTerritorialThreat> IdentifiedThreats;
    
    // Check all our controlled territories for threats
    for (const auto& RegionPair : WorldState.RegionStates)
    {
        if (RegionPair.Value.DominantFaction == FactionID)
        {
            // Check if territory is being contested
            if (RegionPair.Value.bIsContested)
            {
                FTerritorialThreat Threat;
                Threat.TargetTerritoryID = RegionPair.Key;
                Threat.TargetTerritoryType = ETerritoryType::Region;
                Threat.ThreatLevel = 60; // Medium threat for contested territory
                Threat.ThreatType = TEXT("territorial_contest");
                Threat.ThreatDetected = FDateTime::Now();
                IdentifiedThreats.Add(Threat);
            }
        }
    }
    
    // Sort threats by severity
    IdentifiedThreats.Sort([](const FTerritorialThreat& A, const FTerritorialThreat& B) {
        return A.ThreatLevel > B.ThreatLevel;
    });
    
    return IdentifiedThreats;
}

float UAITerritorialBehavior::CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState)
{
    float Priority = 50.0f;
    
    // Base priority calculation
    Priority += EvaluateTerritorialValue(TerritoryID, TerritoryType, WorldState) * 0.6f;
    
    // Apply aggression level - more aggressive factions prioritize expansion
    Priority += AggressionLevel * 30.0f;
    
    // Apply defensive bonus for territories we already control
    if (const FTerritorialState* State = WorldState.RegionStates.Find(TerritoryID))
    {
        if (State->DominantFaction == FactionID)
        {
            Priority += DefensiveBonus * 20.0f;
        }
    }
    
    return FMath::Clamp(Priority, 10.0f, 100.0f);
}

bool UAITerritorialBehavior::IsViableTerritorialTarget(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState)
{
    const FTerritorialState* State = WorldState.RegionStates.Find(TerritoryID);
    if (!State)
    {
        return false; // Can't target unknown territory
    }
    
    // Don't target our own territories unless they're contested
    if (State->DominantFaction == FactionID)
    {
        return State->bIsContested;
    }
    
    // Low aggression factions are less likely to target well-defended territories
    if (AggressionLevel < 0.4f && !State->bIsContested)
    {
        return false;
    }
    
    return true; // Most territories are viable targets
}

float UAITerritorialBehavior::AssessThreatLevel(const FTerritorialThreat& Threat)
{
    float ThreatScore = static_cast<float>(Threat.ThreatLevel);
    
    // Apply defensive bonus to threat assessment
    ThreatScore /= DefensiveBonus;
    
    // Higher aggression means we're less concerned about threats
    ThreatScore *= (2.0f - AggressionLevel);
    
    return FMath::Clamp(ThreatScore, 10.0f, 100.0f);
}

TArray<FTerritorialAction> UAITerritorialBehavior::GenerateCounterActions(const FTerritorialThreat& Threat)
{
    TArray<FTerritorialAction> CounterActions;
    
    // Generate defensive action
    FTerritorialAction DefensiveAction;
    DefensiveAction.FactionID = FactionID;
    DefensiveAction.ActionType = TEXT("defensive_reinforcement");
    DefensiveAction.TargetTerritoryID = Threat.TargetTerritoryID;
    DefensiveAction.TargetTerritoryType = Threat.TargetTerritoryType;
    DefensiveAction.InfluenceChange = FMath::RoundToInt(Threat.ThreatLevel * DefensiveBonus);
    DefensiveAction.ScheduledExecution = FDateTime::Now() + FTimespan::FromSeconds(60); // 1 minute to execute
    DefensiveAction.Description = FString::Printf(TEXT("Defensive reinforcement for territory %d"), Threat.TargetTerritoryID);
    CounterActions.Add(DefensiveAction);
    
    // If we're aggressive enough, also generate offensive counter-action
    if (AggressionLevel > 0.6f)
    {
        FTerritorialAction OffensiveAction;
        OffensiveAction.FactionID = FactionID;
        OffensiveAction.ActionType = TEXT("counter_offensive");
        OffensiveAction.TargetTerritoryID = Threat.TargetTerritoryID;
        OffensiveAction.TargetTerritoryType = Threat.TargetTerritoryType;
        OffensiveAction.InfluenceChange = FMath::RoundToInt(Threat.ThreatLevel * AggressionLevel);
        OffensiveAction.ScheduledExecution = FDateTime::Now() + FTimespan::FromSeconds(120); // 2 minutes to execute
        OffensiveAction.Description = FString::Printf(TEXT("Counter-offensive against territory %d"), Threat.TargetTerritoryID);
        CounterActions.Add(OffensiveAction);
    }
    
    return CounterActions;
}

// Faction-specific AI implementations

UDirectorateAI::UDirectorateAI()
{
    FactionID = 1; // Directorate
    AggressionLevel = 0.6f; // Moderate aggression
    DefensiveBonus = 1.2f; // Good defensive capabilities
    EconomicFocus = 0.8f; // High economic focus
    TechnologicalFocus = 0.9f; // Very high tech focus
    CorporateEfficiencyBonus = 1.2f;
}

float UDirectorateAI::CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState)
{
    float BasePriority = Super::CalculateTerritoryPriority(TerritoryID, TerritoryType, WorldState);
    
    // Directorate values technological and economic territories higher
    BasePriority *= (TechnologicalFocus + CorporateEfficiencyBonus) / 2.0f;
    
    // Prefer regions over districts for better strategic control
    if (TerritoryType == ETerritoryType::Region)
    {
        BasePriority *= 1.2f;
    }
    
    return FMath::Clamp(BasePriority, 10.0f, 100.0f);
}

UFree77AI::UFree77AI()
{
    FactionID = 2; // Free77
    AggressionLevel = 0.8f; // High aggression
    DefensiveBonus = 0.9f; // Weaker defense, prefers mobility
    EconomicFocus = 0.4f; // Lower economic focus
    TechnologicalFocus = 0.6f; // Moderate tech focus
    GuerrillaBonus = 1.3f;
    CorporateTargetPriority = 2.0f;
}

float UFree77AI::CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState)
{
    float BasePriority = Super::CalculateTerritoryPriority(TerritoryID, TerritoryType, WorldState);
    
    // Check if this territory is controlled by corporate factions (Directorate = 1, Corporate Combine = 3)
    if (const FTerritorialState* State = WorldState.RegionStates.Find(TerritoryID))
    {
        if (State->DominantFaction == 1 || State->DominantFaction == 3) // Corporate factions
        {
            BasePriority *= CorporateTargetPriority;
        }
    }
    
    // Apply guerrilla bonus for hit-and-run opportunities
    BasePriority *= GuerrillaBonus;
    
    return FMath::Clamp(BasePriority, 10.0f, 100.0f);
}

UNomadClansAI::UNomadClansAI()
{
    FactionID = 4; // Nomad Clans
    AggressionLevel = 0.5f; // Moderate aggression
    DefensiveBonus = 1.1f; // Good environmental defense
    EconomicFocus = 0.7f; // Moderate economic focus
    TechnologicalFocus = 0.3f; // Lower tech focus, prefer traditional methods
    EnvironmentalMastery = 1.4f;
    ResourceFocus = 1.5f;
}

float UNomadClansAI::CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState)
{
    float BasePriority = Super::CalculateTerritoryPriority(TerritoryID, TerritoryType, WorldState);
    
    // Nomads prioritize resource-rich territories
    BasePriority *= ResourceFocus;
    
    // Apply environmental mastery bonus
    BasePriority *= EnvironmentalMastery;
    
    // Prefer districts for better resource access
    if (TerritoryType == ETerritoryType::District)
    {
        BasePriority *= 1.3f;
    }
    
    return FMath::Clamp(BasePriority, 10.0f, 100.0f);
}

// Proper implementation for ProcessTerritorialUpdate
void UTerritorialManager::ProcessTerritorialUpdate(const FString& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Processing territorial update: %s"), *Message);
    
    // Parse JSON message
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Message);
    
    if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to parse territorial update JSON: %s"), *Message);
        return;
    }
    
    // Extract territorial update data
    FTerritorialUpdate Update;
    
    if (JsonObject->HasField(TEXT("territory_id")))
    {
        Update.TerritoryID = JsonObject->GetIntegerField(TEXT("territory_id"));
    }
    
    if (JsonObject->HasField(TEXT("faction_id")))
    {
        Update.FactionID = JsonObject->GetIntegerField(TEXT("faction_id"));
    }
    
    if (JsonObject->HasField(TEXT("influence_change")))
    {
        Update.InfluenceChange = JsonObject->GetIntegerField(TEXT("influence_change"));
    }
    
    if (JsonObject->HasField(TEXT("cause")))
    {
        Update.ChangeCause = JsonObject->GetStringField(TEXT("cause"));
    }
    
    // Apply the territorial update
    if (Update.TerritoryID > 0 && Update.FactionID > 0)
    {
        // Update the territorial influence
        UpdateTerritorialInfluence(Update.TerritoryID, ETerritoryType::Region, Update.FactionID, Update.InfluenceChange, Update.ChangeCause);
        
        // Broadcast the update to any listening systems
        OnTerritorialControlChanged.Broadcast(Update.TerritoryID, ETerritoryType::Region, 0, Update.FactionID);
        
        UE_LOG(LogTemp, Log, TEXT("Applied territorial update: Territory %d, Faction %d, Change %d"), 
               Update.TerritoryID, Update.FactionID, Update.InfluenceChange);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid territorial update data: TerritoryID=%d, FactionID=%d"), 
               Update.TerritoryID, Update.FactionID);
    }
}