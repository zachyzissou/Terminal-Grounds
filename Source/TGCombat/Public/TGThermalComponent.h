#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TGThermalComponent.generated.h"

UENUM(BlueprintType)
enum class EThermalState : uint8
{
    Cool        UMETA(DisplayName = "Cool"),
    Warm        UMETA(DisplayName = "Warm"),
    Hot         UMETA(DisplayName = "Hot"),
    Overheated  UMETA(DisplayName = "Overheated"),
    Critical    UMETA(DisplayName = "Critical")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnThermalStateChanged, EThermalState, OldState, EThermalState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnOverheatTriggered);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnCoolingCompleted);

/**
 * Component managing heat buildup for Hybrid technology weapons
 */
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class TGCOMBAT_API UTGThermalComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTGThermalComponent();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

public:
    // Heat Management
    UFUNCTION(BlueprintCallable, Category = "Thermal")
    void AddHeat(float HeatAmount);

    UFUNCTION(BlueprintCallable, Category = "Thermal")
    void StartCooling();

    UFUNCTION(BlueprintCallable, Category = "Thermal")
    void ForceCooldown();

    UFUNCTION(BlueprintPure, Category = "Thermal")
    float GetCurrentHeat() const { return CurrentHeat; }

    UFUNCTION(BlueprintPure, Category = "Thermal")
    float GetMaxHeat() const { return MaxHeat; }

    UFUNCTION(BlueprintPure, Category = "Thermal")
    float GetHeatPercentage() const;

    UFUNCTION(BlueprintPure, Category = "Thermal")
    EThermalState GetThermalState() const { return CurrentThermalState; }

    UFUNCTION(BlueprintPure, Category = "Thermal")
    bool IsOverheated() const;

    UFUNCTION(BlueprintPure, Category = "Thermal")
    bool CanFire() const;

    // Configuration
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetMaxHeat(float NewMaxHeat);

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetCoolingRate(float NewCoolingRate);

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetOverheatThreshold(float NewThreshold);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnThermalStateChanged OnThermalStateChanged;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnOverheatTriggered OnOverheatTriggered;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnCoolingCompleted OnCoolingCompleted;

protected:
    // Current heat state
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    float CurrentHeat;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    EThermalState CurrentThermalState;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    bool bIsCooling;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    float CoolingStartTime;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float MaxHeat = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float CoolingRate = 15.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float PassiveCoolingRate = 5.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float OverheatThreshold = 90.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float CriticalThreshold = 95.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float OverheatCooldownTime = 3.0f;

    // State thresholds
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float WarmThreshold = 25.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float HotThreshold = 60.0f;

private:
    void UpdateThermalState();
    EThermalState CalculateThermalState() const;
    void HandleOverheat();
};