#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "Trust/TGTrustSubsystem.h"
#include "TerritorialProgressionSubsystem.generated.h"

// Forward declarations for performance
class UTGTerritorialManager;
class UTGConvoyEconomySubsystem;
class UTGCodexSubsystem;

UENUM(BlueprintType)
enum class EFactionProgressionTier : uint8
{
    Recruit         UMETA(DisplayName = "Recruit"),
    Veteran         UMETA(DisplayName = "Veteran"), 
    Elite           UMETA(DisplayName = "Elite"),
    Commander       UMETA(DisplayName = "Commander"),
    Warlord         UMETA(DisplayName = "Warlord")
};

UENUM(BlueprintType)
enum class ETerritoryResourceType : uint8
{
    Industrial      UMETA(DisplayName = "Industrial"),
    Military        UMETA(DisplayName = "Military"),
    Research        UMETA(DisplayName = "Research"),
    Economic        UMETA(DisplayName = "Economic"),
    Strategic       UMETA(DisplayName = "Strategic")
};

UENUM(BlueprintType)
enum class EFactionAbilityType : uint8
{
    ExtractionBonus     UMETA(DisplayName = "Extraction Bonus"),
    SupplyRouteAccess   UMETA(DisplayName = "Supply Route Access"),
    InfluenceRate       UMETA(DisplayName = "Influence Rate Boost"),
    WeaponUnlock        UMETA(DisplayName = "Weapon Unlock"),
    EquipmentUnlock     UMETA(DisplayName = "Equipment Unlock"),
    TacticalAbility     UMETA(DisplayName = "Tactical Ability")
};

// Performance-optimized faction progression data
USTRUCT(BlueprintType)
struct TGCORE_API FTGFactionProgressionData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    FString FactionName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    int32 FactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    float TotalReputationPoints = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    EFactionProgressionTier CurrentTier = EFactionProgressionTier::Recruit;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    int32 TerritoriesControlled = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    int32 TotalTerritoryHours = 0; // Performance metric for territorial dominance

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    TMap<ETerritoryResourceType, int32> ResourceBonuses;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    TSet<FName> UnlockedAbilities;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    float ExtractionBonusMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    float InfluenceRateMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
    FDateTime LastProgressionUpdate;

    FTGFactionProgressionData()
    {
        FactionId = 0;
        TotalReputationPoints = 0.0f;
        CurrentTier = EFactionProgressionTier::Recruit;
        TerritoriesControlled = 0;
        TotalTerritoryHours = 0;
        ExtractionBonusMultiplier = 1.0f;
        InfluenceRateMultiplier = 1.0f;
        LastProgressionUpdate = FDateTime::Now();
    }
};

// Cached territorial control state for performance
USTRUCT(BlueprintType)
struct TGCORE_API FTGCachedTerritorialState
{
    GENERATED_BODY()

    UPROPERTY()
    int32 TerritoryId;

    UPROPERTY()
    int32 ControllingFactionId;

    UPROPERTY()
    int32 StrategicValue;

    UPROPERTY()
    ETerritoryResourceType ResourceType;

    UPROPERTY()
    float ControlDuration; // Seconds controlled

    UPROPERTY()
    bool bContested;

    FTGCachedTerritorialState()
    {
        TerritoryId = 0;
        ControllingFactionId = 0;
        StrategicValue = 1;
        ResourceType = ETerritoryResourceType::Economic;
        ControlDuration = 0.0f;
        bContested = false;
    }
};

// Faction objective for territorial progression
USTRUCT(BlueprintType)
struct TGCORE_API FTGTerritorialObjective
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    FName ObjectiveId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    FString ObjectiveName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    FString Description;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    int32 TargetFactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    int32 RequiredTerritories = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    ETerritoryResourceType RequiredResourceType;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    float ReputationReward = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    TArray<FName> UnlockRewards;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    bool bCompleted = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Objective")
    FDateTime CompletionTime;

    FTGTerritorialObjective()
    {
        RequiredTerritories = 1;
        ResourceType = ETerritoryResourceType::Economic;
        ReputationReward = 100.0f;
        bCompleted = false;
        CompletionTime = FDateTime::Now();
    }
};

// Performance-optimized batch calculation result
USTRUCT(BlueprintType)
struct TGCORE_API FTGProgressionBatchResult
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<int32> UpdatedFactionIds;

    UPROPERTY()
    TMap<int32, float> ReputationDeltas;

    UPROPERTY()
    TMap<int32, TArray<FName>> NewUnlocks;

    UPROPERTY()
    int32 ProcessedTerritories;

    UPROPERTY()
    float ProcessingTimeMs;

    FTGProgressionBatchResult()
    {
        ProcessedTerritories = 0;
        ProcessingTimeMs = 0.0f;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnFactionProgressionChanged, int32, FactionId, EFactionProgressionTier, NewTier, float, NewReputation);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnFactionAbilityUnlocked, int32, FactionId, FName, AbilityId, EFactionAbilityType, AbilityType);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerritorialObjectiveCompleted, int32, FactionId, FName, ObjectiveId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnResourceBonusChanged, int32, FactionId, ETerritoryResourceType, ResourceType);

/**
 * Territorial Progression Subsystem
 * 
 * HIGH-PERFORMANCE DESIGN FOR 100+ CONCURRENT PLAYERS:
 * - Batch processing every 5 seconds to minimize database load
 * - Cached territorial state to avoid constant spatial queries
 * - Memory-efficient progression tracking with delta compression
 * - Async database operations to prevent gameplay hitches
 * - Lock-free data structures where possible for thread safety
 * 
 * PROGRESSION MECHANICS:
 * - Territory-based faction reputation gains
 * - Unlockable faction abilities through territorial dominance 
 * - Resource bonuses based on controlled territory types
 * - Faction-specific territorial objectives and rewards
 * 
 * PERFORMANCE TARGETS:
 * - <1ms batch processing time per faction
 * - <16ms total update cycle for all 7 factions
 * - <50ms database persistence latency
 * - <8MB memory footprint for progression data
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGTerritorialProgressionSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UTGTerritorialProgressionSubsystem();

    // UGameInstanceSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Core Progression Functions - Optimized for Performance
    UFUNCTION(BlueprintCallable, Category = "Territorial Progression")
    FTGFactionProgressionData GetFactionProgression(int32 FactionId) const;

    UFUNCTION(BlueprintCallable, Category = "Territorial Progression") 
    void UpdateFactionReputation(int32 FactionId, float ReputationDelta, const FString& Source);

    UFUNCTION(BlueprintCallable, Category = "Territorial Progression")
    bool UnlockFactionAbility(int32 FactionId, FName AbilityId, EFactionAbilityType AbilityType);

    UFUNCTION(BlueprintPure, Category = "Territorial Progression")
    bool IsFactionAbilityUnlocked(int32 FactionId, FName AbilityId) const;

    // Territory-Based Bonuses - High Performance Queries
    UFUNCTION(BlueprintPure, Category = "Territorial Progression")
    float GetExtractionBonusMultiplier(int32 FactionId) const;

    UFUNCTION(BlueprintPure, Category = "Territorial Progression")
    float GetInfluenceRateMultiplier(int32 FactionId) const;

    UFUNCTION(BlueprintPure, Category = "Territorial Progression")
    int32 GetResourceBonus(int32 FactionId, ETerritoryResourceType ResourceType) const;

    UFUNCTION(BlueprintPure, Category = "Territorial Progression")
    TArray<FName> GetAvailableSupplyRoutes(int32 FactionId) const;

    // Territorial Objectives System
    UFUNCTION(BlueprintCallable, Category = "Territorial Objectives")
    void RegisterTerritorialObjective(const FTGTerritorialObjective& Objective);

    UFUNCTION(BlueprintCallable, Category = "Territorial Objectives")
    TArray<FTGTerritorialObjective> GetActiveObjectives(int32 FactionId) const;

    UFUNCTION(BlueprintCallable, Category = "Territorial Objectives")
    bool CompleteObjective(int32 FactionId, FName ObjectiveId);

    // Performance Analytics & Debug
    UFUNCTION(BlueprintPure, Category = "Performance")
    FTGProgressionBatchResult GetLastBatchResult() const { return LastBatchResult; }

    UFUNCTION(BlueprintPure, Category = "Performance")
    float GetAverageProcessingTimeMs() const { return AverageProcessingTimeMs; }

    UFUNCTION(BlueprintCallable, Category = "Debug")
    void ForceProgressionUpdate();

    UFUNCTION(BlueprintCallable, Category = "Debug")
    void ClearFactionProgression(int32 FactionId);

    // Events - Performance Optimized Broadcasting
    UPROPERTY(BlueprintAssignable, Category = "Progression Events")
    FOnFactionProgressionChanged OnFactionProgressionChanged;

    UPROPERTY(BlueprintAssignable, Category = "Progression Events")
    FOnFactionAbilityUnlocked OnFactionAbilityUnlocked;

    UPROPERTY(BlueprintAssignable, Category = "Progression Events")
    FOnTerritorialObjectiveCompleted OnTerritorialObjectiveCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Progression Events")
    FOnResourceBonusChanged OnResourceBonusChanged;

    // Configuration - Tuned for 100+ Player Performance
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Config")
    float BatchProcessingInterval = 5.0f; // 5 seconds for optimal performance

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Config")
    float CacheRefreshInterval = 15.0f; // Territorial state cache refresh

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Config")
    int32 MaxBatchSize = 50; // Territories per batch to prevent hitches

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression Config")
    float BaseReputationPerHour = 10.0f; // Base reputation gain per territory per hour

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression Config")
    TMap<EFactionProgressionTier, float> TierThresholds = {
        {EFactionProgressionTier::Recruit, 0.0f},
        {EFactionProgressionTier::Veteran, 1000.0f},
        {EFactionProgressionTier::Elite, 2500.0f},
        {EFactionProgressionTier::Commander, 5000.0f},
        {EFactionProgressionTier::Warlord, 10000.0f}
    };

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression Config")
    TMap<ETerritoryResourceType, float> ResourceTypeMultipliers = {
        {ETerritoryResourceType::Strategic, 2.0f},
        {ETerritoryResourceType::Military, 1.5f},
        {ETerritoryResourceType::Research, 1.5f},
        {ETerritoryResourceType::Industrial, 1.2f},
        {ETerritoryResourceType::Economic, 1.0f}
    };

protected:
    // Performance-Critical Data Structures
    UPROPERTY()
    TMap<int32, FTGFactionProgressionData> FactionProgressionMap;

    UPROPERTY()
    TMap<int32, FTGCachedTerritorialState> TerritorialStateCache;

    UPROPERTY()
    TArray<FTGTerritorialObjective> ActiveObjectives;

    // Performance Tracking
    UPROPERTY()
    FTGProgressionBatchResult LastBatchResult;

    UPROPERTY()
    float AverageProcessingTimeMs = 0.0f;

    UPROPERTY()
    TArray<float> ProcessingTimeHistory;

    // Timer Handles for Batch Processing
    FTimerHandle BatchProcessingTimer;
    FTimerHandle CacheRefreshTimer;

    // Subsystem References - Cached for Performance
    UPROPERTY()
    class UTGTrustSubsystem* TrustSubsystem;

    UPROPERTY()
    class UTGCodexSubsystem* CodexSubsystem;

    // Performance-Optimized Core Functions
    void ProcessProgressionBatch();
    void RefreshTerritorialStateCache();
    void CalculateFactionReputation(int32 FactionId);
    void UpdateFactionTier(int32 FactionId);
    void CheckObjectiveCompletion(int32 FactionId);
    void ApplyTerritoryBonuses(int32 FactionId);

    // Cached Subsystem Access - Avoids GetSubsystem() calls
    UTGTerritorialManager* GetCachedTerritorialManager() const;
    UTGConvoyEconomySubsystem* GetCachedConvoyEconomySubsystem() const;

    // Database Integration - Async for Performance
    void SaveProgressionDataAsync(int32 FactionId);
    void LoadProgressionDataAsync(int32 FactionId);

    // Thread Safety & Performance
    mutable FCriticalSection ProgressionDataMutex;
    void BroadcastProgressionEvents(const TArray<int32>& UpdatedFactionIds);

    // Memory Management
    void CleanupExpiredObjectives();
    void OptimizeMemoryUsage();

private:
    // Cached subsystem pointers to avoid repeated GetSubsystem calls
    mutable class UTGTerritorialManager* CachedTerritorialManager = nullptr;
    mutable class UTGConvoyEconomySubsystem* CachedConvoyEconomySubsystem = nullptr;

    // Performance metrics
    double LastBatchStartTime = 0.0;
    int32 TotalBatchesProcessed = 0;
};