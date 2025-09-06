#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/DataTable.h"
#include "GameplayTagContainer.h"
#include "TGWorld/Public/Economy/TGConvoyEconomySubsystem.h"
#include "TGEconomicVictorySubsystem.generated.h"

UENUM(BlueprintType)
enum class EEconomicVictoryType : uint8
{
    None                UMETA(DisplayName = "No Victory"),
    EconomicDominance   UMETA(DisplayName = "Economic Dominance"),
    SupplyMonopoly      UMETA(DisplayName = "Supply Monopoly"),
    EconomicCollapse    UMETA(DisplayName = "Economic Collapse"),
    TradeNetwork        UMETA(DisplayName = "Trade Network"),
    ResourceControl     UMETA(DisplayName = "Resource Control"),
    ConvoySupremacy     UMETA(DisplayName = "Convoy Supremacy")
};

UENUM(BlueprintType)
enum class EEconomicVictoryStatus : uint8
{
    NotStarted      UMETA(DisplayName = "Not Started"),
    InProgress      UMETA(DisplayName = "In Progress"),
    NearComplete    UMETA(DisplayName = "Near Complete"),
    Completed       UMETA(DisplayName = "Victory Achieved"),
    Failed          UMETA(DisplayName = "Failed")
};

UENUM(BlueprintType)
enum class EResourceType : uint8
{
    Supplies        UMETA(DisplayName = "Supplies"),
    Intelligence    UMETA(DisplayName = "Intelligence"),
    Technology      UMETA(DisplayName = "Technology"),
    Energy          UMETA(DisplayName = "Energy"),
    Materials       UMETA(DisplayName = "Materials"),
    Personnel       UMETA(DisplayName = "Personnel")
};

USTRUCT(BlueprintType)
struct TGCORE_API FEconomicVictoryCondition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    EEconomicVictoryType VictoryType = EEconomicVictoryType::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    FString ConditionName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    FString Description;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    float RequiredThreshold = 0.75f; // 75% by default

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    float TimeRequirement = 0.0f; // Time in seconds to maintain condition (0 = instant)

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    int32 RequiredTerritories = 0; // Number of territories needed

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    EResourceType TargetResourceType = EResourceType::Supplies;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    TArray<int32> TargetFactions; // Enemy factions to affect

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    int32 Priority = 1; // Lower number = higher priority

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Condition")
    bool bActiveCondition = true;

    FEconomicVictoryCondition()
    {
        VictoryType = EEconomicVictoryType::None;
        RequiredThreshold = 0.75f;
        TimeRequirement = 0.0f;
        RequiredTerritories = 0;
        TargetResourceType = EResourceType::Supplies;
        Priority = 1;
        bActiveCondition = true;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FEconomicVictoryProgress
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    int32 FactionID = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    EEconomicVictoryType VictoryType = EEconomicVictoryType::None;

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    EEconomicVictoryStatus Status = EEconomicVictoryStatus::NotStarted;

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    float Progress = 0.0f; // 0.0 to 1.0

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    float TimeHeld = 0.0f; // Time condition has been satisfied

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    float LastUpdateTime = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    TArray<FString> ActiveRequirements;

    UPROPERTY(BlueprintReadOnly, Category = "Victory Progress")
    TArray<FString> CompletedRequirements;

    FEconomicVictoryProgress()
    {
        FactionID = 0;
        VictoryType = EEconomicVictoryType::None;
        Status = EEconomicVictoryStatus::NotStarted;
        Progress = 0.0f;
        TimeHeld = 0.0f;
        LastUpdateTime = 0.0f;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FEconomicMetrics
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    float TotalRouteValue = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    float ControlledRouteValue = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    float RouteControlPercentage = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    int32 TotalRoutes = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    int32 ControlledRoutes = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    TMap<EResourceType, float> ResourceControlPercentage;

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    TMap<int32, float> EnemyEconomicOutput; // Faction ID -> Economic Output

    UPROPERTY(BlueprintReadOnly, Category = "Economic Metrics")
    float NetworkConnectivity = 0.0f;

    FEconomicMetrics()
    {
        TotalRouteValue = 0.0f;
        ControlledRouteValue = 0.0f;
        RouteControlPercentage = 0.0f;
        TotalRoutes = 0;
        ControlledRoutes = 0;
        NetworkConnectivity = 0.0f;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnEconomicVictoryProgress, int32, FactionID, EEconomicVictoryType, VictoryType, float, Progress);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnEconomicVictoryAchieved, int32, FactionID, EEconomicVictoryType, VictoryType, float, CompletionTime);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnEconomicVictoryThreatened, int32, ThreateningFactionID, EEconomicVictoryType, VictoryType, float, TimeToVictory);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnEconomicMetricsUpdated, int32, FactionID, const FEconomicMetrics&, NewMetrics);

/**
 * Economic Victory Subsystem
 * Manages alternative victory conditions based on economic warfare and supply chain control
 * Integrates with territorial and convoy systems to provide diverse strategic win paths
 */
UCLASS()
class TGCORE_API UTGEconomicVictorySubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;

    // Victory Condition Management
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void RegisterVictoryCondition(const FEconomicVictoryCondition& Condition);

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void RemoveVictoryCondition(EEconomicVictoryType VictoryType);

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void SetVictoryConditionActive(EEconomicVictoryType VictoryType, bool bActive);

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    TArray<FEconomicVictoryCondition> GetActiveVictoryConditions() const;

    // Victory Progress Tracking
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FEconomicVictoryProgress GetFactionVictoryProgress(int32 FactionID, EEconomicVictoryType VictoryType) const;

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    TArray<FEconomicVictoryProgress> GetAllVictoryProgress() const;

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FEconomicVictoryProgress GetClosestVictoryToCompletion() const;

    // Economic Metrics
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FEconomicMetrics GetFactionEconomicMetrics(int32 FactionID) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void UpdateEconomicMetrics(int32 FactionID);

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    float GetRouteControlPercentage(int32 FactionID, EResourceType ResourceType = EResourceType::Supplies) const;

    // Victory Evaluation
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void EvaluateVictoryConditions();

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    bool CheckVictoryCondition(int32 FactionID, const FEconomicVictoryCondition& Condition) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void TriggerEconomicVictory(int32 FactionID, EEconomicVictoryType VictoryType);

    // Counter-Strategy Support
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    TArray<FString> GetCounterStrategies(EEconomicVictoryType VictoryType) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void ApplyCounterStrategy(int32 FactionID, EEconomicVictoryType TargetVictoryType, const FString& Strategy);

    // Game Session Integration
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void StartEconomicVictorySession();

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void EndEconomicVictorySession();

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    bool IsEconomicVictoryEnabled() const { return bEconomicVictoryEnabled; }

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Economic Victory Events")
    FOnEconomicVictoryProgress OnEconomicVictoryProgress;

    UPROPERTY(BlueprintAssignable, Category = "Economic Victory Events")
    FOnEconomicVictoryAchieved OnEconomicVictoryAchieved;

    UPROPERTY(BlueprintAssignable, Category = "Economic Victory Events")
    FOnEconomicVictoryThreatened OnEconomicVictoryThreatened;

    UPROPERTY(BlueprintAssignable, Category = "Economic Victory Events")
    FOnEconomicMetricsUpdated OnEconomicMetricsUpdated;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Config")
    bool bEconomicVictoryEnabled = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Config")
    float VictoryCheckInterval = 5.0f; // Seconds between victory condition checks

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Config")
    float ThreatWarningThreshold = 0.8f; // Warning when victory progress hits this threshold

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Config")
    bool bPreventEconomicCamping = true; // Require active engagement

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Victory Config")
    float MinimumEngagementThreshold = 0.1f; // Minimum activity level to prevent camping

protected:
    virtual void Tick(float DeltaTime) override;
    virtual bool IsTickable() const override { return bEconomicVictoryEnabled; }
    virtual TStatId GetStatID() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UTGEconomicVictorySubsystem, STATGROUP_Tickables); }

private:
    // Core state
    UPROPERTY()
    TArray<FEconomicVictoryCondition> VictoryConditions;

    UPROPERTY()
    TMap<FString, FEconomicVictoryProgress> VictoryProgress; // Key: FactionID_VictoryType

    UPROPERTY()
    TMap<int32, FEconomicMetrics> FactionMetrics;

    UPROPERTY()
    class UTGConvoyEconomySubsystem* ConvoyEconomySubsystem;

    UPROPERTY()
    class UTerritorialManager* TerritorialManager;

    // Timing
    float LastVictoryCheck = 0.0f;
    float SessionStartTime = 0.0f;

    // Internal systems
    void InitializeDefaultVictoryConditions();
    void UpdateVictoryProgress(float DeltaTime);
    void CheckForEconomicCamping(int32 FactionID);
    float CalculateNetworkConnectivity(int32 FactionID) const;
    float CalculateEconomicOutput(int32 FactionID) const;
    bool ValidateVictoryCondition(const FEconomicVictoryCondition& Condition) const;
    FString GenerateProgressKey(int32 FactionID, EEconomicVictoryType VictoryType) const;

    // Victory type specific calculations
    float CalculateEconomicDominance(int32 FactionID) const;
    float CalculateSupplyMonopoly(int32 FactionID, EResourceType ResourceType) const;
    float CalculateEconomicCollapse(int32 FactionID, const TArray<int32>& TargetFactions) const;
    float CalculateTradeNetwork(int32 FactionID) const;
    float CalculateResourceControl(int32 FactionID, EResourceType ResourceType) const;
    float CalculateConvoySupremacy(int32 FactionID) const;
};