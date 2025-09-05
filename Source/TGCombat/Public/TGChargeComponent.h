#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TGChargeComponent.generated.h"

UENUM(BlueprintType)
enum class EChargeState : uint8
{
    Discharged  UMETA(DisplayName = "Discharged"),
    Charging    UMETA(DisplayName = "Charging"),
    Charged     UMETA(DisplayName = "Charged"),
    Overcharged UMETA(DisplayName = "Overcharged"),
    Unstable    UMETA(DisplayName = "Unstable")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnChargeStateChanged, EChargeState, OldState, EChargeState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnFullyCharged);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnOverchargeTriggered);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnChargeDisrupted);

/**
 * Component managing energy charge for Hybrid and Alien technology weapons
 */
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class TGCOMBAT_API UTGChargeComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTGChargeComponent();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

public:
    // Charge Management
    UFUNCTION(BlueprintCallable, Category = "Charge")
    void StartCharging();

    UFUNCTION(BlueprintCallable, Category = "Charge")
    void StopCharging();

    UFUNCTION(BlueprintCallable, Category = "Charge")
    void DischargeWeapon();

    UFUNCTION(BlueprintCallable, Category = "Charge")
    void DrainCharge(float ChargeAmount);

    UFUNCTION(BlueprintCallable, Category = "Charge")
    void ForceOvercharge();

    UFUNCTION(BlueprintPure, Category = "Charge")
    float GetCurrentCharge() const { return CurrentCharge; }

    UFUNCTION(BlueprintPure, Category = "Charge")
    float GetMaxCharge() const { return MaxCharge; }

    UFUNCTION(BlueprintPure, Category = "Charge")
    float GetChargePercentage() const;

    UFUNCTION(BlueprintPure, Category = "Charge")
    EChargeState GetChargeState() const { return CurrentChargeState; }

    UFUNCTION(BlueprintPure, Category = "Charge")
    bool IsCharging() const;

    UFUNCTION(BlueprintPure, Category = "Charge")
    bool IsFullyCharged() const;

    UFUNCTION(BlueprintPure, Category = "Charge")
    bool CanFire() const;

    UFUNCTION(BlueprintPure, Category = "Charge")
    float GetDamageMultiplier() const;

    // Siege Integration
    UFUNCTION(BlueprintCallable, Category = "Charge|Siege")
    void ApplySiegeChargeModifier(float ChargeRateMultiplier, float DamageMultiplier, float Duration);

    UFUNCTION(BlueprintPure, Category = "Charge|Siege")
    float GetSiegeChargeRateMultiplier() const { return SiegeChargeRateMultiplier; }

    UFUNCTION(BlueprintPure, Category = "Charge|Siege")
    float GetSiegeDamageMultiplier() const { return SiegeDamageMultiplier; }

    UFUNCTION(BlueprintPure, Category = "Charge|Siege")
    bool HasSiegeModifiers() const { return SiegeChargeRateMultiplier != 1.0f || SiegeDamageMultiplier != 1.0f; }

    // EMP and Disruption
    UFUNCTION(BlueprintCallable, Category = "Disruption")
    void ApplyEMPDisruption(float DisruptionStrength, float Duration);

    UFUNCTION(BlueprintPure, Category = "Disruption")
    bool IsEMPDisrupted() const { return bIsEMPDisrupted; }

    // Configuration
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetChargeRate(float NewChargeRate);

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetMaxCharge(float NewMaxCharge);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnChargeStateChanged OnChargeStateChanged;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnFullyCharged OnFullyCharged;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnOverchargeTriggered OnOverchargeTriggered;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnChargeDisrupted OnChargeDisrupted;

protected:
    // Current charge state
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    float CurrentCharge;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    EChargeState CurrentChargeState;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    bool bIsCharging;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    bool bIsEMPDisrupted;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    float EMPDisruptionEndTime;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float MaxCharge = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float ChargeRate = 25.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float DischargeRate = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float MinChargeToFire = 20.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float OverchargeThreshold = 95.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float UnstableThreshold = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float ChargedThreshold = 80.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float EMPVulnerability = 1.0f;

    // Siege Modifiers
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    float SiegeChargeRateMultiplier = 1.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    float SiegeDamageMultiplier = 1.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    float SiegeModifierEndTime = 0.0f;

private:
    void UpdateChargeState();
    EChargeState CalculateChargeState() const;
    void HandleOvercharge();
    void ProcessEMPDisruption(float DeltaTime);
};