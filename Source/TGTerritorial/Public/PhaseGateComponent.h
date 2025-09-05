#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Net/UnrealNetwork.h"
#include "PhaseGateComponent.generated.h"

UENUM(BlueprintType)
enum class ESiegePhase : uint8
{
    Probe       UMETA(DisplayName = "Probe"),
    Interdict   UMETA(DisplayName = "Interdict"),
    Dominate    UMETA(DisplayName = "Dominate"),
    Locked      UMETA(DisplayName = "Locked")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnPhaseChanged, ESiegePhase, OldPhase, ESiegePhase, NewPhase);

/**
 * Phase Gate Component
 * Manages the progression through siege phases: Probe -> Interdict -> Dominate -> Locked
 * Server-authoritative phase transitions with client replication
 */
UCLASS(ClassGroup=(TG), meta=(BlueprintSpawnableComponent))
class TGTERRITORIAL_API UPhaseGateComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPhaseGateComponent();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnPhaseChanged OnPhaseChanged;

    // Phase Management
    UFUNCTION(BlueprintCallable, Category = "Siege|Phase", meta = (CallInEditor = "true"))
    bool CanAdvancePhase() const;

    UFUNCTION(BlueprintCallable, Category = "Siege|Phase", BlueprintAuthorityOnly)
    void AdvancePhase();

    UFUNCTION(BlueprintCallable, Category = "Siege|Phase", BlueprintAuthorityOnly)
    void SetPhase(ESiegePhase NewPhase);

    UFUNCTION(BlueprintPure, Category = "Siege|Phase")
    ESiegePhase GetPhase() const { return CurrentPhase; }

    UFUNCTION(BlueprintPure, Category = "Siege|Phase")
    FString GetPhaseName() const;

    UFUNCTION(BlueprintPure, Category = "Siege|Phase")
    float GetPhaseProgress() const { return PhaseProgress; }

    UFUNCTION(BlueprintCallable, Category = "Siege|Phase", BlueprintAuthorityOnly)
    void UpdatePhaseProgress(float Delta);

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    float PhaseProgressThreshold = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    bool bAutoAdvancePhase = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    float LockDurationSeconds = 300.0f; // 5 minutes default

protected:
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(ReplicatedUsing = OnRep_Phase, BlueprintReadOnly, Category = "Siege|State")
    ESiegePhase CurrentPhase;

    UPROPERTY(ReplicatedUsing = OnRep_Progress, BlueprintReadOnly, Category = "Siege|State")
    float PhaseProgress;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege|State")
    FDateTime PhaseStartTime;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege|State")
    FDateTime LockEndTime;

    UFUNCTION()
    void OnRep_Phase(ESiegePhase OldPhase);

    UFUNCTION()
    void OnRep_Progress();

private:
    void BroadcastPhaseChange(ESiegePhase OldPhase, ESiegePhase NewPhase);
    bool IsLocked() const;
};