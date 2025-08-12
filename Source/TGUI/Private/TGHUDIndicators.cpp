#include "TGHUDIndicators.h"
#include "TimerManager.h"

void UTGHUDIndicators::NativeConstruct() {
  Super::NativeConstruct();
  UpdateHeatDisplay();
  UpdateChargeDisplay();
  UpdateDisruptionDisplay();
}

void UTGHUDIndicators::InitializeIndicators(UTGThermalComponent *ThermalComp,
                                            UTGChargeComponent *ChargeComp) {
  ThermalComponent = ThermalComp;
  ChargeComponent = ChargeComp;

  if (ThermalComponent) {
    ThermalComponent->OnThermalStateChanged.AddDynamic(
        this, &UTGHUDIndicators::OnThermalStateChanged);
    ThermalComponent->OnOverheatTriggered.AddDynamic(
        this, &UTGHUDIndicators::OnOverheatTriggered);
  }
  if (ChargeComponent) {
    ChargeComponent->OnChargeStateChanged.AddDynamic(
        this, &UTGHUDIndicators::OnChargeStateChanged);
    ChargeComponent->OnChargeDisrupted.AddDynamic(
        this, &UTGHUDIndicators::OnChargeDisrupted);
  }

  UpdateHeatDisplay();
  UpdateChargeDisplay();
  UpdateDisruptionDisplay();
}

void UTGHUDIndicators::UpdateWeaponStatus(bool bHasHeat, bool bHasCharge,
                                          bool bCanJam) {
  if (HeatProgressBar) {
    HeatProgressBar->SetVisibility(bHasHeat ? ESlateVisibility::Visible
                                            : ESlateVisibility::Collapsed);
  }
  if (ChargeProgressBar) {
    ChargeProgressBar->SetVisibility(bHasCharge ? ESlateVisibility::Visible
                                                : ESlateVisibility::Collapsed);
  }
}

void UTGHUDIndicators::UpdateHeatDisplay() {
  if (!ThermalComponent)
    return;
  const float Pct = ThermalComponent->GetHeatPercentage();
  if (HeatProgressBar) {
    HeatProgressBar->SetPercent(Pct);
    FLinearColor BarColor = CoolColor;
    switch (ThermalComponent->GetThermalState()) {
    case EThermalState::Warm:
      BarColor = WarmColor;
      break;
    case EThermalState::Hot:
      BarColor = HotColor;
      break;
    case EThermalState::Overheated:
      BarColor = HotColor;
      break;
    default:
      break;
    }
    HeatProgressBar->SetFillColorAndOpacity(BarColor);
  }
  UpdateHeatIndicator(Pct, ThermalComponent->GetThermalState());
}

void UTGHUDIndicators::UpdateChargeDisplay() {
  if (!ChargeComponent)
    return;
  const float Pct = ChargeComponent->GetChargePercentage();
  if (ChargeProgressBar) {
    ChargeProgressBar->SetPercent(Pct);
    ChargeProgressBar->SetFillColorAndOpacity(ChargeColor);
  }
  UpdateChargeIndicator(Pct, ChargeComponent->GetChargeState());
}

void UTGHUDIndicators::UpdateDisruptionDisplay() {
  if (!ChargeComponent)
    return;
  const bool bDisrupted = ChargeComponent->IsEMPDisrupted();
  ShowEMPDisruption(bDisrupted, bDisrupted ? 1.0f : 0.0f);
  if (EMPDisruptionIcon) {
    EMPDisruptionIcon->SetColorAndOpacity(DisruptionColor);
    EMPDisruptionIcon->SetVisibility(bDisrupted ? ESlateVisibility::Visible
                                                : ESlateVisibility::Collapsed);
  }
}

void UTGHUDIndicators::OnThermalStateChanged(EThermalState OldState,
                                             EThermalState NewState) {
  ShowOverheatWarning(NewState == EThermalState::Overheated ||
                      NewState == EThermalState::Critical);
  UpdateHeatDisplay();
}

void UTGHUDIndicators::OnChargeStateChanged(EChargeState OldState,
                                            EChargeState NewState) {
  ShowChargeReady(NewState == EChargeState::Charged);
  UpdateChargeDisplay();
}

void UTGHUDIndicators::OnOverheatTriggered() { ShowOverheatWarning(true); }

void UTGHUDIndicators::OnChargeDisrupted() { UpdateDisruptionDisplay(); }
