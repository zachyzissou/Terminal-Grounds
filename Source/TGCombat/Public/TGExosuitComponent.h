#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameplayTagContainer.h"
#include "TGExosuitData.h"
#include "TGExosuitComponent.generated.h"

class UTGAugmentData;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnExosuitDamageChanged, EExosuitDamageStage, OldStage, EExosuitDamageStage, NewStage);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAugmentInstalled, UTGAugmentData*, AugmentData);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAugmentRemoved, UTGAugmentData*, AugmentData);

/**
 * Component that manages player exosuit configuration and augments
 */
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class TGCOMBAT_API UTGExosuitComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTGExosuitComponent();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

public:
    // Exosuit Management
    UFUNCTION(BlueprintCallable, Category = "Exosuit")
    void SetExosuitData(UTGExosuitData* NewExosuitData);

    UFUNCTION(BlueprintPure, Category = "Exosuit")
    UTGExosuitData* GetExosuitData() const { return CurrentExosuitData; }

    UFUNCTION(BlueprintPure, Category = "Exosuit")
    EExosuitDamageStage GetCurrentDamageStage() const { return CurrentDamageStage; }

    UFUNCTION(BlueprintCallable, Category = "Exosuit")
    void TakeDamage(float DamageAmount);

    UFUNCTION(BlueprintCallable, Category = "Exosuit")
    void RepairExosuit(float RepairAmount);

    // Augment Management
    UFUNCTION(BlueprintCallable, Category = "Augments")
    bool InstallAugment(UTGAugmentData* AugmentData, int32 SlotIndex);

    UFUNCTION(BlueprintCallable, Category = "Augments")
    bool RemoveAugment(int32 SlotIndex);

    UFUNCTION(BlueprintPure, Category = "Augments")
    UTGAugmentData* GetAugmentInSlot(int32 SlotIndex) const;

    UFUNCTION(BlueprintPure, Category = "Augments")
    TArray<UTGAugmentData*> GetInstalledAugments() const;

    UFUNCTION(BlueprintPure, Category = "Augments")
    int32 GetAvailableAugmentSlots() const;

    // Stats Calculation
    UFUNCTION(BlueprintPure, Category = "Stats")
    FExosuitStats GetEffectiveStats() const;

    UFUNCTION(BlueprintPure, Category = "Stats")
    float GetMovementSpeedMultiplier() const;

    UFUNCTION(BlueprintPure, Category = "Stats")
    float GetRecoilReduction() const;

    UFUNCTION(BlueprintPure, Category = "Stats")
    float GetArmorRating() const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnExosuitDamageChanged OnExosuitDamageChanged;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAugmentInstalled OnAugmentInstalled;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAugmentRemoved OnAugmentRemoved;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Exosuit")
    UTGExosuitData* CurrentExosuitData;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Exosuit")
    EExosuitDamageStage CurrentDamageStage;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Exosuit")
    float CurrentHealth;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Exosuit")
    float MaxHealth;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Augments")
    TArray<UTGAugmentData*> InstalledAugments;

    // Health thresholds for damage stages
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Config")
    float MinorDamageThreshold = 0.8f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Config")
    float ModerateDamageThreshold = 0.6f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Config")
    float HeavyDamageThreshold = 0.3f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Config")
    float CriticalDamageThreshold = 0.1f;

private:
    void UpdateDamageStage();
    void UpdateVisualDamage();
    bool ValidateAugmentInstallation(UTGAugmentData* AugmentData, int32 SlotIndex) const;
};