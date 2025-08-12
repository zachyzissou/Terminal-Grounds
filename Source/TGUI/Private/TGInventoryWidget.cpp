#include "TGInventoryWidget.h"
#include "Components/Button.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"

void UTGInventoryWidget::NativeConstruct() {
  Super::NativeConstruct();
  CreateAugmentSlots();
}

void UTGInventoryWidget::InitializeInventory(UTGExosuitComponent *ExosuitComp) {
  ExosuitComponent = ExosuitComp;
  if (!ExosuitComponent)
    return;

  ExosuitComponent->OnExosuitDamageChanged.AddDynamic(
      this, &UTGInventoryWidget::OnExosuitDamageChanged);
  ExosuitComponent->OnAugmentInstalled.AddDynamic(
      this, &UTGInventoryWidget::OnAugmentInstalled);
  ExosuitComponent->OnAugmentRemoved.AddDynamic(
      this, &UTGInventoryWidget::OnAugmentRemoved);

  UpdateExosuitDisplay(ExosuitComponent->GetExosuitData(),
                       ExosuitComponent->GetCurrentDamageStage());
  UpdateExosuitStats(ExosuitComponent->GetEffectiveStats());
}

void UTGInventoryWidget::RequestAugmentInstallation(UTGAugmentData *AugmentData,
                                                    int32 SlotIndex) {
  OnAugmentInstallRequested.Broadcast(AugmentData, SlotIndex);
}

void UTGInventoryWidget::RequestAugmentRemoval(int32 SlotIndex) {
  OnAugmentSlotClicked.Broadcast(SlotIndex);
}

void UTGInventoryWidget::CreateAugmentSlots() {
  // Stub: In a real UI, these would be created from a widget tree or BP
  const int32 Slots =
      ExosuitComponent ? ExosuitComponent->GetAvailableAugmentSlots() : 0;
  AugmentSlotButtons.SetNum(Slots);
  AugmentSlotImages.SetNum(Slots);
}

void UTGInventoryWidget::UpdateAugmentSlotDisplay(int32 SlotIndex,
                                                  UTGAugmentData *AugmentData) {
  // Stub: Assign icon/image if available
}

void UTGInventoryWidget::OnExosuitDamageChanged(EExosuitDamageStage OldStage,
                                                EExosuitDamageStage NewStage) {
  if (!ExosuitComponent)
    return;
  UpdateExosuitDisplay(ExosuitComponent->GetExosuitData(), NewStage);
}

void UTGInventoryWidget::OnAugmentInstalled(UTGAugmentData *AugmentData) {
  // Refresh list
  UpdateAugmentSlots(ExosuitComponent ? ExosuitComponent->GetInstalledAugments()
                                      : TArray<UTGAugmentData *>{});
}

void UTGInventoryWidget::OnAugmentRemoved(UTGAugmentData *AugmentData) {
  // Refresh list
  UpdateAugmentSlots(ExosuitComponent ? ExosuitComponent->GetInstalledAugments()
                                      : TArray<UTGAugmentData *>{});
}

void UTGInventoryWidget::OnAugmentSlotButtonClicked(int32 SlotIndex) {
  OnAugmentSlotClicked.Broadcast(SlotIndex);
}

FText UTGInventoryWidget::FormatStatText(const FString &StatName, float Value,
                                         const FString &Unit) {
  return FText::FromString(FString::Printf(TEXT("%s: %.1f%s"), *StatName, Value,
                                           Unit.Len() ? *Unit : TEXT("")));
}

FLinearColor
UTGInventoryWidget::GetHealthBarColor(EExosuitDamageStage DamageStage) const {
  switch (DamageStage) {
  case EExosuitDamageStage::Pristine:
    return HealthyColor;
  case EExosuitDamageStage::Minor:
    return FLinearColor::Yellow;
  case EExosuitDamageStage::Moderate:
    return FLinearColor::Yellow;
  case EExosuitDamageStage::Heavy:
    return DamagedColor;
  case EExosuitDamageStage::Critical:
    return DamagedColor;
  default:
    return HealthyColor;
  }
}

FLinearColor
UTGInventoryWidget::GetWeightBarColor(float WeightPercentage) const {
  if (WeightPercentage < 0.7f)
    return WeightNormalColor;
  if (WeightPercentage < 0.9f)
    return WeightWarningColor;
  return WeightDangerColor;
}
