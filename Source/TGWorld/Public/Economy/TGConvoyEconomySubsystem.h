#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "TGConvoyEconomySubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FTGOnIntegrityIndexChanged, float, NewIndex, float, Delta);

/**
 * World-level convoy economy controller.
 * Tracks Integrity Index [0..1], applies mission outcomes, and exposes change events for UI/contracts.
 */
UCLASS(BlueprintType)
class TGWORLD_API UTGConvoyEconomySubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    UTGConvoyEconomySubsystem();

    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** Apply a convoy outcome. Positive Delta moves toward stability when success=true, away when false. Clamped to [0,1]. */
    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void ApplyConvoyOutcome(float Delta, FName RouteId, FName JobType, bool bSuccess);

    /** Force-set the Integrity Index. */
    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void SetIntegrityIndex(float NewValue);

    /** Get the current Integrity Index. */
    UFUNCTION(BlueprintPure, Category = "Convoy Economy")
    float GetIntegrityIndex() const { return IntegrityIndex; }

    /** Decay toward equilibrium using exponential half-life in seconds. */
    UFUNCTION(BlueprintCallable, Category = "Convoy Economy")
    void AdvanceDecay(float DeltaSeconds);

    /** Broadcast when Integrity Index changes. */
    UPROPERTY(BlueprintAssignable, Category = "Convoy Economy")
    FTGOnIntegrityIndexChanged OnIntegrityIndexChanged;

private:
    /** Shared state of the season's convoy stability. [0..1] */
    UPROPERTY(EditAnywhere, Category = "Convoy Economy", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float IntegrityIndex;

    /** Target equilibrium to decay toward. */
    UPROPERTY(EditAnywhere, Category = "Convoy Economy", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float Equilibrium = 0.5f;

    /** Half-life for decay in seconds. */
    UPROPERTY(EditAnywhere, Category = "Convoy Economy", meta = (ClampMin = "1.0"))
    float DecayHalfLifeSeconds = 3600.f;

    /** Recently affected routes for lightweight UI reference. */
    UPROPERTY()
    TSet<FName> ActiveRoutes;

    void BroadcastChange(float OldIndex, float NewIndex);
};
