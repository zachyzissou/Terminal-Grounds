// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "TerritorialTypes.h"
#include "AITerritorialBehavior.generated.h"

USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialWorldState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "World State")
    TMap<int32, FTerritorialState> RegionStates;

    UPROPERTY(BlueprintReadWrite, Category = "World State")
    TMap<int32, FTerritorialState> DistrictStates;

    UPROPERTY(BlueprintReadWrite, Category = "World State")
    TArray<FTerritorialUpdate> RecentUpdates;

    UPROPERTY(BlueprintReadWrite, Category = "World State")
    TArray<float> TotalInfluenceByFaction; // Index 0 unused, 1-7 for factions

    UPROPERTY(BlueprintReadWrite, Category = "World State")
    int32 ContestedTerritories;

    UPROPERTY(BlueprintReadWrite, Category = "World State")
    FDateTime LastUpdated;
};

USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialThreat
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    int32 TargetTerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    ETerritoryType TargetTerritoryType = ETerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    int32 ThreateningFactionID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    int32 ThreatLevel = 0; // 1-100

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    FString ThreatType; // "territorial_loss", "influence_decline", "hostile_expansion"

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    int32 ExpectedInfluenceLoss = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Threat")
    FDateTime ThreatDetected;
};

USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialDecision
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    FString DecisionType; // "offensive", "defensive", "expansion", "consolidation"

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    int32 TargetTerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    ETerritoryType TargetTerritoryType = ETerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    int32 Priority = 50; // 1-100

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    int32 ResourcesCommitted = 0; // 1-100 percentage

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    float ExecutionDelay = 0.0f; // Seconds before execution

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    TArray<FString> RequiredActions; // Specific actions to take

    UPROPERTY(BlueprintReadWrite, Category = "Decision")
    FString Reasoning; // AI decision explanation for debugging
};

USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialAction
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    int32 FactionID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    FString ActionType; // "influence_boost", "territorial_claim", "defensive_fortify"

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    int32 TargetTerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    ETerritoryType TargetTerritoryType = ETerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    int32 InfluenceChange = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    float SuccessProbability = 1.0f; // 0.0-1.0

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    FDateTime ScheduledExecution;

    UPROPERTY(BlueprintReadWrite, Category = "Action")
    FString Description; // Human-readable action description
};

/**
 * Base class for faction AI territorial behavior
 * Each faction inherits from this to implement unique strategies
 */
UCLASS(Abstract, Blueprintable)
class TGTERRITORIAL_API UAITerritorialBehavior : public UObject
{
    GENERATED_BODY()
    
    friend class UAITerritorialManager;

public:
    UAITerritorialBehavior();

    // Core AI decision-making methods (implemented in Blueprint or C++)
    UFUNCTION(BlueprintImplementableEvent, Category = "AI Territorial")
    FTerritorialDecision MakeStrategicDecision(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintImplementableEvent, Category = "AI Territorial")
    FTerritorialDecision RespondToThreat(const FTerritorialThreat& Threat);

    UFUNCTION(BlueprintImplementableEvent, Category = "AI Territorial")
    TArray<FTerritorialAction> PlanTacticalOperations(int32 TerritoryID, ETerritoryType TerritoryType);

    // Core AI functions
    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    void UpdateTerritorialAI(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    TArray<FTerritorialThreat> AnalyzeThreats(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    FTerritorialDecision MakeStrategicDecisionWithThreats(const FTerritorialWorldState& WorldState, const TArray<FTerritorialThreat>& Threats);

    // Utility functions for AI decision-making
    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    float EvaluateTerritorialValue(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    TArray<FTerritorialThreat> IdentifyThreats(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    TArray<int32> GetPreferredTargets(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintCallable, Category = "AI Territorial")
    bool ShouldDefendTerritory(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialThreat& Threat);

    // Configuration accessors
    UFUNCTION(BlueprintPure, Category = "AI Config")
    int32 GetFactionID() const { return FactionID; }

    UFUNCTION(BlueprintPure, Category = "AI Config")
    float GetAggressionLevel() const { return AggressionLevel; }

    UFUNCTION(BlueprintPure, Category = "AI Config")
    float GetDefensiveBonus() const { return DefensiveBonus; }

protected:
    // Faction-specific behavior parameters
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    int32 FactionID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    float AggressionLevel = 0.5f; // 0.0-1.0, affects expansion vs defense balance

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    float DefensiveBonus = 1.0f; // Multiplier for defensive actions

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    float EconomicFocus = 0.5f; // 0.0-1.0, priority for economic territories

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    float TechnologicalFocus = 0.5f; // 0.0-1.0, priority for tech territories

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    TArray<ETerritoryResourceType> PreferredResources;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    TArray<ETerritoryType> PreferredTerritoryTypes;

    // AI state tracking
    UPROPERTY(BlueprintReadOnly, Category = "AI State")
    FDateTime LastDecisionTime;

public:
    UPROPERTY(BlueprintReadOnly, Category = "AI State")
    TArray<FTerritorialDecision> PendingDecisions;

protected:

    UPROPERTY(BlueprintReadOnly, Category = "AI State")
    TMap<int32, float> TerritoryPriorities; // Territory ID -> Priority score

    // Decision-making helper functions
    virtual float CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState);
    virtual bool IsViableTerritorialTarget(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState);
    virtual float AssessThreatLevel(const FTerritorialThreat& Threat);
    virtual TArray<FTerritorialAction> GenerateCounterActions(const FTerritorialThreat& Threat);
};

/**
 * Directorate AI: Corporate efficiency and technological superiority
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API UDirectorateAI : public UAITerritorialBehavior
{
    GENERATED_BODY()

public:
    UDirectorateAI();

    // Directorate-specific territorial strategy
    virtual float CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState) override;

protected:
    // Directorate-specific parameters
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Directorate AI")
    float CorporateEfficiencyBonus = 1.2f; // Bonus for coordinated operations

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Directorate AI")
    float TechnologicalAdvantage = 1.15f; // Bonus for tech-related territories

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Directorate AI")
    float AntiCorporateHostility = 2.0f; // Increased aggression toward corporate competitors
};

/**
 * Free77 AI: Guerrilla warfare and resistance networks
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API UFree77AI : public UAITerritorialBehavior
{
    GENERATED_BODY()

public:
    UFree77AI();

    virtual float CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState) override;

protected:
    // Free77-specific parameters
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Free77 AI")
    float GuerrillaBonus = 1.3f; // Bonus for hit-and-run operations

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Free77 AI")
    float CorporateTargetPriority = 2.0f; // Increased priority for disrupting corporate factions

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Free77 AI")
    float NetworkCoordination = 1.25f; // Bonus for coordinated resistance operations
};

/**
 * Nomad Clans AI: Environmental mastery and survivalist tactics
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API UNomadClansAI : public UAITerritorialBehavior
{
    GENERATED_BODY()

public:
    UNomadClansAI();

    virtual float CalculateTerritoryPriority(int32 TerritoryID, ETerritoryType TerritoryType, const FTerritorialWorldState& WorldState) override;

protected:
    // Nomad Clans-specific parameters
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nomad AI")
    float EnvironmentalMastery = 1.4f; // Bonus for environmental adaptation

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nomad AI")
    float ResourceFocus = 1.5f; // Increased priority for resource-rich territories

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nomad AI")
    float PackCoordination = 1.2f; // Bonus for group operations
};

/**
 * AI Manager: Controls all faction AIs and coordinates their interactions
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API UAITerritorialManager : public UObject
{
    GENERATED_BODY()

public:
    UAITerritorialManager();

    // AI management functions
    UFUNCTION(BlueprintCallable, Category = "AI Management")
    void InitializeFactionalAI();

    UFUNCTION(BlueprintCallable, Category = "AI Management")
    void UpdateAIDecisions(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintCallable, Category = "AI Management")
    void ProcessAIActions(float DeltaTime);

    UFUNCTION(BlueprintCallable, Category = "AI Management")
    void NotifyTerritorialChange(const FTerritorialUpdate& Update);

    // AI state queries
    UFUNCTION(BlueprintPure, Category = "AI Management")
    TArray<FTerritorialDecision> GetPendingAIDecisions();

    UFUNCTION(BlueprintPure, Category = "AI Management")
    UAITerritorialBehavior* GetFactionAI(int32 FactionID);

protected:
    // AI instances for each faction
    UPROPERTY(BlueprintReadOnly, Category = "AI Management")
    TMap<int32, UAITerritorialBehavior*> FactionAIs;

    // AI update timing
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Timing")
    float StrategicDecisionInterval = 300.0f; // 5 minutes

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Timing")
    float TacticalDecisionInterval = 60.0f; // 1 minute

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Timing")
    float ThreatResponseInterval = 5.0f; // 5 seconds

    // AI state
    UPROPERTY(BlueprintReadOnly, Category = "AI State")
    FDateTime LastStrategicUpdate;

    UPROPERTY(BlueprintReadOnly, Category = "AI State")
    FDateTime LastTacticalUpdate;

private:
    // Internal AI decision execution
    void ExecuteAIDecision(const FTerritorialDecision& Decision);

    TArray<FTerritorialAction> QueuedActions;

private:
    void CreateFactionAI(int32 FactionID);
    void ProcessStrategicDecisions(const FTerritorialWorldState& WorldState);
    void ProcessTacticalDecisions(const FTerritorialWorldState& WorldState);
    void ProcessThreatResponses(const FTerritorialWorldState& WorldState);
};