#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/DataTable.h"
#include "GameplayTagContainer.h"
#include "TGConvoyEconomySubsystem.generated.h"

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
    float BaseIntegrityImpact = 0.1f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    float DifficultyMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Route")
    int32 FactionControllerID = 0;

    FConvoyRoute()
    {
        BaseIntegrityImpact = 0.1f;
        DifficultyMultiplier = 1.0f;
        FactionControllerID = 0;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnIntegrityIndexChanged, float, OldValue, float, NewValue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnConvoyOutcome, FName, RouteId, EJobType, JobType, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnIntegrityThresholdReached, float, Threshold);

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

    // Route Queries
    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    FConvoyRoute GetRoute(FName RouteId) const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    TArray<FConvoyRoute> GetAllRoutes() const;

    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    TArray<FConvoyRoute> GetRoutesByFaction(int32 FactionID) const;

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

    // Threshold tracking
    TSet<float> TriggeredThresholds;
    float LastIntegrityValue = 0.5f;

    // Internal systems
    void ProcessIntegrityDecay(float DeltaTime);
    void CheckIntegrityThresholds(float OldValue, float NewValue);
    float CalculateJobTypeMultiplier(EJobType JobType) const;
    void BroadcastIntegrityChange(float OldValue, float NewValue);
};
