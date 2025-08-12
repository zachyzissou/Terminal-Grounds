#pragma once

#include "Blueprint/UserWidget.h"
#include "Components/Image.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"
#include "CoreMinimal.h"
#include "TGChargeComponent.h"
#include "TGThermalComponent.h"

#include "TGHUDIndicators.generated.h"

/**
 * Widget for displaying heat/charge/EMP/jam indicators on the HUD
 */
UCLASS(BlueprintType, Blueprintable)
class TGUI_API UTGHUDIndicators : public UUserWidget {
  GENERATED_BODY()

public:
  virtual void NativeConstruct() override;

  // Initialization
  UFUNCTION(BlueprintCallable, Category = "Setup")
  void InitializeIndicators(UTGThermalComponent *ThermalComp,
                            UTGChargeComponent *ChargeComp);

  // Heat Indicator
  UFUNCTION(BlueprintImplementableEvent, Category = "Heat")
  void UpdateHeatIndicator(float HeatPercentage, EThermalState ThermalState);

  UFUNCTION(BlueprintImplementableEvent, Category = "Heat")
  void ShowOverheatWarning(bool bShow);

  // Charge Indicator
  UFUNCTION(BlueprintImplementableEvent, Category = "Charge")
  void UpdateChargeIndicator(float ChargePercentage, EChargeState ChargeState);

  UFUNCTION(BlueprintImplementableEvent, Category = "Charge")
  void ShowChargeReady(bool bReady);

  // EMP/Disruption Indicator
  UFUNCTION(BlueprintImplementableEvent, Category = "Disruption")
  void ShowEMPDisruption(bool bDisrupted, float Intensity);

  UFUNCTION(BlueprintImplementableEvent, Category = "Disruption")
  void UpdateJamIndicator(bool bJammed, float JamStrength);

  // Status Updates
  UFUNCTION(BlueprintCallable, Category = "Status")
  void UpdateWeaponStatus(bool bHasHeat, bool bHasCharge, bool bCanJam);

protected:
  // Widget Components (bound in Blueprint)
  UPROPERTY(meta = (BindWidget))
  UProgressBar *HeatProgressBar;

  UPROPERTY(meta = (BindWidget))
  UProgressBar *ChargeProgressBar;

  UPROPERTY(meta = (BindWidget))
  UTextBlock *HeatStatusText;

  UPROPERTY(meta = (BindWidget))
  UTextBlock *ChargeStatusText;

  UPROPERTY(meta = (BindWidget))
  UImage *OverheatWarningIcon;

  UPROPERTY(meta = (BindWidget))
  UImage *EMPDisruptionIcon;

  UPROPERTY(meta = (BindWidget))
  UImage *JamIndicatorIcon;

  // Component references
  UPROPERTY(BlueprintReadOnly, Category = "Components")
  UTGThermalComponent *ThermalComponent;

  UPROPERTY(BlueprintReadOnly, Category = "Components")
  UTGChargeComponent *ChargeComponent;

  // Visual configuration
  UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
  FLinearColor CoolColor = FLinearColor::Blue;

  UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
  FLinearColor WarmColor = FLinearColor::Yellow;

  UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
  FLinearColor HotColor = FLinearColor::Red;

  UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
  FLinearColor ChargeColor = FLinearColor(0.0f, 1.0f, 1.0f, 1.0f); // Cyan

  UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Appearance")
  FLinearColor DisruptionColor =
      FLinearColor(1.0f, 0.0f, 1.0f, 1.0f); // Magenta

private:
  void UpdateHeatDisplay();
  void UpdateChargeDisplay();
  void UpdateDisruptionDisplay();

  // Event handlers
  UFUNCTION()
  void OnThermalStateChanged(EThermalState OldState, EThermalState NewState);

  UFUNCTION()
  void OnChargeStateChanged(EChargeState OldState, EChargeState NewState);

  UFUNCTION()
  void OnOverheatTriggered();

  UFUNCTION()
  void OnChargeDisrupted();

  // Animation timers
  FTimerHandle OverheatFlashTimer;
  FTimerHandle DisruptionFlashTimer;

  bool bOverheatFlashState = false;
  bool bDisruptionFlashState = false;
};
