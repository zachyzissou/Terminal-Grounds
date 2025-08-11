#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/Button.h"
#include "Components/ProgressBar.h"
#include "TGExosuitComponent.h"
#include "TGAugmentData.h"
#include "TGInventoryWidget.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAugmentSlotClicked, int32, SlotIndex);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAugmentInstallRequested, UTGAugmentData*, AugmentData, int32, SlotIndex);

/**
 * Widget for inventory management with exosuit/augment slots
 */
UCLASS(BlueprintType, Blueprintable)
class TGUI_API UTGInventoryWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    // Initialization
    UFUNCTION(BlueprintCallable, Category = "Setup")
    void InitializeInventory(UTGExosuitComponent* ExosuitComp);

    // Exosuit Management
    UFUNCTION(BlueprintImplementableEvent, Category = "Exosuit")
    void UpdateExosuitDisplay(UTGExosuitData* ExosuitData, EExosuitDamageStage DamageStage);

    UFUNCTION(BlueprintImplementableEvent, Category = "Exosuit")
    void UpdateExosuitStats(const FExosuitStats& Stats);

    // Augment Management
    UFUNCTION(BlueprintImplementableEvent, Category = "Augments")
    void UpdateAugmentSlots(const TArray<UTGAugmentData*>& InstalledAugments);

    UFUNCTION(BlueprintImplementableEvent, Category = "Augments")
    void ShowAugmentDetails(UTGAugmentData* AugmentData);

    UFUNCTION(BlueprintCallable, Category = "Augments")
    void RequestAugmentInstallation(UTGAugmentData* AugmentData, int32 SlotIndex);

    UFUNCTION(BlueprintCallable, Category = "Augments")
    void RequestAugmentRemoval(int32 SlotIndex);

    // Inventory Display
    UFUNCTION(BlueprintImplementableEvent, Category = "Inventory")
    void UpdateWeightDisplay(float CurrentWeight, float MaxWeight);

    UFUNCTION(BlueprintImplementableEvent, Category = "Inventory")
    void ShowWeightWarning(bool bOverWeight);

    UFUNCTION(BlueprintImplementableEvent, Category = "Inventory")
    void PlayWeightWarningAudio();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAugmentSlotClicked OnAugmentSlotClicked;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAugmentInstallRequested OnAugmentInstallRequested;

protected:
    // Widget Components (bound in Blueprint)
    UPROPERTY(meta = (BindWidget))
    UImage* ExosuitImage;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* ExosuitNameText;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* ExosuitStatsText;

    UPROPERTY(meta = (BindWidget))
    UProgressBar* ExosuitHealthBar;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* MovementSpeedText;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* ArmorRatingText;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* RecoilReductionText;

    UPROPERTY(meta = (BindWidget))
    UProgressBar* WeightProgressBar;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* WeightText;

    // Augment slot buttons (dynamically created)
    UPROPERTY(BlueprintReadOnly, Category = "Augments")
    TArray<UButton*> AugmentSlotButtons;

    UPROPERTY(BlueprintReadOnly, Category = "Augments")
    TArray<UImage*> AugmentSlotImages;

    // Component reference
    UPROPERTY(BlueprintReadOnly, Category = "Components")
    UTGExosuitComponent* ExosuitComponent;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
    FLinearColor HealthyColor = FLinearColor::Green;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
    FLinearColor DamagedColor = FLinearColor::Red;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
    FLinearColor WeightNormalColor = FLinearColor::Blue;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
    FLinearColor WeightWarningColor = FLinearColor::Yellow;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
    FLinearColor WeightDangerColor = FLinearColor::Red;

private:
    void CreateAugmentSlots();
    void UpdateAugmentSlotDisplay(int32 SlotIndex, UTGAugmentData* AugmentData);

    // Event handlers
    UFUNCTION()
    void OnExosuitDamageChanged(EExosuitDamageStage OldStage, EExosuitDamageStage NewStage);

    UFUNCTION()
    void OnAugmentInstalled(UTGAugmentData* AugmentData);

    UFUNCTION()
    void OnAugmentRemoved(UTGAugmentData* AugmentData);

    UFUNCTION()
    void OnAugmentSlotButtonClicked(int32 SlotIndex);

    // Helper functions
    FText FormatStatText(const FString& StatName, float Value, const FString& Unit = "");
    FLinearColor GetHealthBarColor(EExosuitDamageStage DamageStage) const;
    FLinearColor GetWeightBarColor(float WeightPercentage) const;
};