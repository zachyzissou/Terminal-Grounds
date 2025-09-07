#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/DataTable.h"
#include "GameplayTagContainer.h"
#include "HAL/CriticalSection.h"
#include "Async/AsyncWork.h"
#include "TGConvoyEconomySubsystem.generated.h"

// Forward declarations
class UTGTerritorialManager;

UENUM(BlueprintType)
enum class EJobType : uint8
{
    Supply          UMETA(DisplayName = "Supply Run"),
    Extraction      UMETA(DisplayName = "Resource Extraction"),
    Intelligence    UMETA(DisplayName = "Intelligence Gathering"),
    Sabotage        UMETA(DisplayName = "Sabotage Operation"),
    Escort          UMETA(DisplayName = "Convoy Escort"),
    Raid            UMETA(DisplayName = "Supply Raid")
};

USTRUCT(BlueprintType)
struct FTerritorialConnection
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    int32 FromTerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    int32 ToTerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    float Distance;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    float SecurityLevel; // 0.0 = highly contested, 1.0 = secure

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    bool bDirectConnection;

    FTerritorialConnection()
    {
        FromTerritoryId = 0;
        ToTerritoryId = 0;
        Distance = 0.0f;
        SecurityLevel = 0.5f;
        bDirectConnection = false;
    }
};

USTRUCT(BlueprintType)
struct FConvoyRoute
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    FName RouteId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    FString RouteName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    TArray<FVector> Waypoints;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    TArray<int32> TerritorialPath; // Territory IDs in route order

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    int32 ControllingFactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    float BaseIntegrityImpact = 0.1f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    float DifficultyMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    float SecurityRating; // Overall route security (0.0-1.0)

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    float ProfitabilityScore; // Economic value of route

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    float TotalDistance;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    bool bIsActive;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    FDateTime LastValidated;

    UPROPERTY()
    uint32 RouteHash; // For cache invalidation

    FConvoyRoute()
    {
        ControllingFactionId = 0;
        BaseIntegrityImpact = 0.1f;
        DifficultyMultiplier = 1.0f;
        SecurityRating = 0.5f;
        ProfitabilityScore = 0.0f;
        TotalDistance = 0.0f;
        bIsActive = false;
        LastValidated = FDateTime::Now();
        RouteHash = 0;
    }
};

USTRUCT(BlueprintType)
struct FRouteGenerationParameters
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    int32 RequestingFactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    int32 SourceTerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    int32 DestinationTerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    float MinSecurityThreshold;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    int32 MaxHops;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
    bool bRequireDirectControl; // Must control all territories in path

    FRouteGenerationParameters()
    {
        RequestingFactionId = 0;
        SourceTerritoryId = 0;
        DestinationTerritoryId = 0;
        MinSecurityThreshold = 0.3f;
        MaxHops = 5;
        bRequireDirectControl = false;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnIntegrityIndexChanged, float, OldValue, float, NewValue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnConvoyOutcome, FName, RouteId, EJobType, JobType, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnIntegrityThresholdReached, float, Threshold);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnRouteGenerated, FName, RouteId, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnRouteInvalidated, FName, RouteId, FString, Reason);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnRoutesUpdated, int32, FactionId, int32, ActiveRoutesCount, float, TotalProfitability);

/**
 * Convoy Economy Subsystem
 * Manages supply route integrity and its impact on territorial control
 * Tracks convoy operations, supply chain disruptions, and economic warfare
 */
UCLASS()
class TGWORLD_API UTGConvoyEconomySubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;

    // Convoy Operations
    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void ApplyConvoyOutcome(float Delta, FName RouteId, EJobType JobType, bool bSuccess);

    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void RegisterConvoyRoute(const FConvoyRoute& Route);

    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void RemoveConvoyRoute(FName RouteId);

    // Integrity Management
    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    float GetIntegrityIndex() const { return IntegrityIndex; }

    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void SetIntegrityIndex(float NewValue);

    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void ModifyIntegrityIndex(float Delta);

    // Dynamic Route Generation - Performance Critical
    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void GenerateRoutesBetweenTerritories(const FRouteGenerationParameters& Parameters);

    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void RegenerateAllFactionRoutes(int32 FactionId);

    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void InvalidateRoutesInTerritory(int32 TerritoryId);

    // Route Queries
    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    FConvoyRoute GetRoute(FName RouteId) const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    TArray<FConvoyRoute> GetAllRoutes() const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    TArray<FConvoyRoute> GetRoutesByFaction(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    TArray<FConvoyRoute> GetActiveRoutes() const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    float GetFactionTotalProfitability(int32 FactionId) const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    int32 GetActiveRouteCount(int32 FactionId) const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    float GetRouteIntegrityImpact(FName RouteId, EJobType JobType, bool bSuccess) const;

    // Economic Impact
    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void TriggerEconomicEvent(const FString& EventName, float IntegrityDelta);

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    float GetEconomicHealthScore() const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    FString GetIntegrityStatusText() const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy Events")
    FOnIntegrityIndexChanged OnIntegrityIndexChanged;

    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy Events")
    FOnConvoyOutcome OnConvoyOutcome;

    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy Events")
    FOnIntegrityThresholdReached OnIntegrityThresholdReached;

    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy Events")
    FOnRouteGenerated OnRouteGenerated;

    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy Events")
    FOnRouteInvalidated OnRouteInvalidated;

    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy Events")
    FOnRoutesUpdated OnRoutesUpdated;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy Config")
    float IntegrityDecayRate = 0.02f; // Per minute

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy Config")
    float MaxIntegrityIndex = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy Config")
    float MinIntegrityIndex = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy Config")
    TArray<float> IntegrityThresholds = {0.25f, 0.5f, 0.75f, 0.9f};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy Config")
    bool bEnableIntegrityDecay = true;

    // Route Generation Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route Config")
    float RouteUpdateFrequency = 5.0f; // Seconds between route recalculation

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route Config")
    int32 MaxRoutesPerFaction = 20;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route Config")
    float MinRouteSecurityThreshold = 0.2f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route Config")
    bool bEnableAsyncRouteGeneration = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route Config")
    int32 RouteGenerationBatchSize = 5; // Routes generated per batch

protected:
    virtual void Tick(float DeltaTime) override;
    virtual bool IsTickable() const override { return true; }
    virtual TStatId GetStatID() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UTGConvoyEconomySubsystem, STATGROUP_Tickables); }

private:
    // Core state
    UPROPERTY()
    float IntegrityIndex = 0.5f;

    UPROPERTY()
    TMap<FName, FConvoyRoute> RegisteredRoutes;

    // Dynamic route management
    TMap<int32, TArray<FName>> FactionRouteCache; // FactionId -> RouteIds
    TMap<uint32, FName> RouteHashToIdCache; // RouteHash -> RouteId for deduplication
    TMap<int32, TMap<int32, FTerritorialConnection>> TerritorialConnections; // Cached connections
    
    // Performance optimization
    mutable FCriticalSection RouteDataMutex;
    FTimerHandle RouteUpdateTimerHandle;
    
    // Territorial integration
    UPROPERTY()
    UTGTerritorialManager* TerritorialManager;

    // Threshold tracking
    TSet<float> TriggeredThresholds;
    float LastIntegrityValue = 0.5f;
    float LastRouteUpdate = 0.0f;

    // Internal systems
    void ProcessIntegrityDecay(float DeltaTime);
    void CheckIntegrityThresholds(float OldValue, float NewValue);
    float CalculateJobTypeMultiplier(EJobType JobType) const;
    void BroadcastIntegrityChange(float OldValue, float NewValue);
    
    // Route generation internals
    void InitializeTerritorialConnections();
    void UpdateTerritorialConnections();
    void ProcessRouteUpdates();
    TArray<int32> FindOptimalPath(int32 SourceTerritoryId, int32 DestinationTerritoryId, int32 FactionId, int32 MaxHops) const;
    float CalculateRouteProfitability(const FConvoyRoute& Route) const;
    float CalculateRouteSecurityRating(const TArray<int32>& TerritorialPath) const;
    uint32 GenerateRouteHash(const FRouteGenerationParameters& Parameters) const;
    FName GenerateUniqueRouteId(int32 FactionId, int32 SourceId, int32 DestinationId) const;
    
    // Territorial event handlers
    UFUNCTION()
    void OnTerritoryControlChanged(int32 TerritoryId, int32 OldControllerFactionId, int32 NewControllerFactionId);
    
    UFUNCTION()
    void OnTerritoryContested(int32 TerritoryId, bool bContested);
    
    // Cache management
    void InvalidateRouteCache(int32 FactionId);
    void CleanupInactiveRoutes();
};
