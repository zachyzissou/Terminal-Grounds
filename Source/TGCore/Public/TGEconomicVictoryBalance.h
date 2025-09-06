#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "TGEconomicVictorySubsystem.h"
#include "TGEconomicVictoryBalance.generated.h"

USTRUCT(BlueprintType)
struct TGCORE_API FEconomicVictoryBalanceConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance", meta = (ClampMin = "0.1", ClampMax = "1.0"))
    float RequiredThreshold = 0.75f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance", meta = (ClampMin = "0.0", ClampMax = "600.0"))
    float TimeRequirement = 120.0f; // seconds

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance", meta = (ClampMin = "1", ClampMax = "10"))
    int32 Priority = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    bool bEnabled = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    FString Description;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Counter-Strategy")
    TArray<FString> CounterStrategies;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance", meta = (ClampMin = "0.0", ClampMax = "2.0"))
    float DifficultyMultiplier = 1.0f;

    FEconomicVictoryBalanceConfig()
    {
        RequiredThreshold = 0.75f;
        TimeRequirement = 120.0f;
        Priority = 1;
        bEnabled = true;
        DifficultyMultiplier = 1.0f;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FAntiCampingConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Anti-Camping")
    bool bEnableAntiCamping = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Anti-Camping", meta = (ClampMin = "0.01", ClampMax = "0.5"))
    float MinimumEngagementThreshold = 0.1f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Anti-Camping", meta = (ClampMin = "1.0", ClampMax = "60.0"))
    float EngagementCheckInterval = 10.0f; // seconds

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Anti-Camping", meta = (ClampMin = "0.1", ClampMax = "1.0"))
    float CampingPenaltyMultiplier = 0.5f; // Reduces progress when camping

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Anti-Camping")
    TArray<FString> RequiredActivities;

    FAntiCampingConfig()
    {
        bEnableAntiCamping = true;
        MinimumEngagementThreshold = 0.1f;
        EngagementCheckInterval = 10.0f;
        CampingPenaltyMultiplier = 0.5f;
        RequiredActivities = {
            TEXT("Complete extraction objectives"),
            TEXT("Participate in convoy operations"),
            TEXT("Engage in territorial combat")
        };
    }
};

/**
 * Developer settings for Economic Victory system balance configuration
 * Allows designers to tune victory conditions, balance, and anti-camping measures
 */
UCLASS(Config = Game, DefaultConfig, BlueprintType, meta = (DisplayName = "Economic Victory Balance"))
class TGCORE_API UTGEconomicVictoryBalance : public UDeveloperSettings
{
    GENERATED_BODY()

public:
    UTGEconomicVictoryBalance();

    // UDeveloperSettings interface
    virtual FName GetCategoryName() const override;
    virtual FText GetSectionText() const override;

#if WITH_EDITOR
    virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
#endif

    // Victory Condition Balance Settings
    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Victory Conditions", 
              meta = (ToolTip = "Economic Dominance: Control majority of convoy route value"))
    FEconomicVictoryBalanceConfig EconomicDominanceBalance;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Victory Conditions",
              meta = (ToolTip = "Supply Monopoly: Control all routes of specific resource type"))
    FEconomicVictoryBalanceConfig SupplyMonopolyBalance;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Victory Conditions",
              meta = (ToolTip = "Economic Collapse: Reduce enemy economic output significantly"))
    FEconomicVictoryBalanceConfig EconomicCollapseBalance;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Victory Conditions",
              meta = (ToolTip = "Trade Network: Establish profitable routes across territories"))
    FEconomicVictoryBalanceConfig TradeNetworkBalance;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Victory Conditions",
              meta = (ToolTip = "Resource Control: Dominate specific resource types"))
    FEconomicVictoryBalanceConfig ResourceControlBalance;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Victory Conditions",
              meta = (ToolTip = "Convoy Supremacy: Achieve superiority in convoy operations"))
    FEconomicVictoryBalanceConfig ConvoySupremacyBalance;

    // General Balance Settings
    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "General Balance",
              meta = (ClampMin = "1.0", ClampMax = "30.0", ToolTip = "How often to check victory conditions (seconds)"))
    float VictoryCheckInterval = 5.0f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "General Balance",
              meta = (ClampMin = "0.5", ClampMax = "1.0", ToolTip = "Progress threshold for threat warnings"))
    float ThreatWarningThreshold = 0.8f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "General Balance",
              meta = (ToolTip = "Allow multiple victory types to be active simultaneously"))
    bool bAllowMultipleVictoryTypes = true;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "General Balance",
              meta = (ClampMin = "300.0", ClampMax = "7200.0", ToolTip = "Maximum session duration (seconds)"))
    float MaxSessionDuration = 1800.0f; // 30 minutes

    // Anti-Camping Configuration
    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Anti-Camping",
              meta = (ToolTip = "Configuration to prevent passive victory strategies"))
    FAntiCampingConfig AntiCampingConfig;

    // Faction-Specific Balance
    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Faction Balance",
              meta = (ToolTip = "Per-faction multipliers for victory condition difficulty"))
    TMap<int32, float> FactionVictoryMultipliers;

    // Resource Type Balance
    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Resource Balance",
              meta = (ToolTip = "Balance multipliers for different resource types"))
    TMap<EResourceType, float> ResourceTypeMultipliers;

    // Counter-Strategy Configuration
    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Counter-Strategies",
              meta = (ToolTip = "Effectiveness multipliers for counter-strategies"))
    float CounterStrategyEffectiveness = 1.2f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Counter-Strategies",
              meta = (ToolTip = "Time window for applying counter-strategies (seconds)"))
    float CounterStrategyWindow = 30.0f;

    // Utility Functions
    UFUNCTION(BlueprintPure, Category = "Economic Victory Balance")
    FEconomicVictoryBalanceConfig GetVictoryTypeBalance(EEconomicVictoryType VictoryType) const;

    UFUNCTION(BlueprintPure, Category = "Economic Victory Balance")
    float GetFactionVictoryMultiplier(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Victory Balance")
    float GetResourceTypeMultiplier(EResourceType ResourceType) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Victory Balance")
    void ApplyBalanceToSubsystem(UTGEconomicVictorySubsystem* Subsystem) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Victory Balance")
    void ResetToDefaults();

    UFUNCTION(BlueprintPure, Category = "Economic Victory Balance")
    bool ValidateBalanceConfig() const;

private:
    void InitializeDefaultValues();
    void InitializeDefaultCounterStrategies();
    void InitializeDefaultFactionMultipliers();
    void InitializeDefaultResourceMultipliers();
};