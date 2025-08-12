#include "TGExosuitComponent.h"
#include "TGAugmentData.h"

UTGExosuitComponent::UTGExosuitComponent() {
  PrimaryComponentTick.bCanEverTick = true;
  CurrentExosuitData = nullptr;
  CurrentDamageStage = EExosuitDamageStage::Pristine;
  CurrentHealth = 100.0f;
  MaxHealth = 100.0f;
}

void UTGExosuitComponent::BeginPlay() {
  Super::BeginPlay();
  UpdateDamageStage();
}

void UTGExosuitComponent::TickComponent(
    float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction *ThisTickFunction) {
  Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
}

void UTGExosuitComponent::SetExosuitData(UTGExosuitData *NewExosuitData) {
  CurrentExosuitData = NewExosuitData;
}

void UTGExosuitComponent::TakeDamage(float DamageAmount) {
  CurrentHealth = FMath::Clamp(CurrentHealth - FMath::Max(0.0f, DamageAmount),
                               0.0f, MaxHealth);
  UpdateDamageStage();
}

void UTGExosuitComponent::RepairExosuit(float RepairAmount) {
  CurrentHealth = FMath::Clamp(CurrentHealth + FMath::Max(0.0f, RepairAmount),
                               0.0f, MaxHealth);
  UpdateDamageStage();
}

bool UTGExosuitComponent::InstallAugment(UTGAugmentData *AugmentData,
                                         int32 SlotIndex) {
  if (!ValidateAugmentInstallation(AugmentData, SlotIndex)) {
    return false;
  }
  if (InstalledAugments.Num() <= SlotIndex) {
    InstalledAugments.SetNum(SlotIndex + 1);
  }
  InstalledAugments[SlotIndex] = AugmentData;
  OnAugmentInstalled.Broadcast(AugmentData);
  return true;
}

bool UTGExosuitComponent::RemoveAugment(int32 SlotIndex) {
  if (!InstalledAugments.IsValidIndex(SlotIndex)) {
    return false;
  }
  UTGAugmentData *Removed = InstalledAugments[SlotIndex];
  InstalledAugments[SlotIndex] = nullptr;
  OnAugmentRemoved.Broadcast(Removed);
  return true;
}

UTGAugmentData *UTGExosuitComponent::GetAugmentInSlot(int32 SlotIndex) const {
  return InstalledAugments.IsValidIndex(SlotIndex)
             ? InstalledAugments[SlotIndex]
             : nullptr;
}

TArray<UTGAugmentData *> UTGExosuitComponent::GetInstalledAugments() const {
  TArray<UTGAugmentData *> Result;
  for (UTGAugmentData *Aug : InstalledAugments) {
    if (Aug) {
      Result.Add(Aug);
    }
  }
  return Result;
}

int32 UTGExosuitComponent::GetAvailableAugmentSlots() const {
  return CurrentExosuitData ? CurrentExosuitData->BaseStats.AugmentSlots
                            : InstalledAugments.Num();
}

FExosuitStats UTGExosuitComponent::GetEffectiveStats() const {
  FExosuitStats Stats =
      CurrentExosuitData ? CurrentExosuitData->BaseStats : FExosuitStats();
  // Minimal example: could apply modifiers based on damage stage and augments
  return Stats;
}

float UTGExosuitComponent::GetMovementSpeedMultiplier() const {
  return GetEffectiveStats().MovementSpeedMultiplier;
}

float UTGExosuitComponent::GetRecoilReduction() const {
  return GetEffectiveStats().RecoilReductionPercentage;
}

float UTGExosuitComponent::GetArmorRating() const {
  return GetEffectiveStats().ArmorRating;
}

void UTGExosuitComponent::UpdateDamageStage() {
  EExosuitDamageStage OldStage = CurrentDamageStage;
  float HealthPct = MaxHealth > 0.0f ? (CurrentHealth / MaxHealth) : 0.0f;

  if (HealthPct <= CriticalDamageThreshold) {
    CurrentDamageStage = EExosuitDamageStage::Critical;
  } else if (HealthPct <= HeavyDamageThreshold) {
    CurrentDamageStage = EExosuitDamageStage::Heavy;
  } else if (HealthPct <= ModerateDamageThreshold) {
    CurrentDamageStage = EExosuitDamageStage::Moderate;
  } else if (HealthPct <= MinorDamageThreshold) {
    CurrentDamageStage = EExosuitDamageStage::Minor;
  } else {
    CurrentDamageStage = EExosuitDamageStage::Pristine;
  }

  if (OldStage != CurrentDamageStage) {
    OnExosuitDamageChanged.Broadcast(OldStage, CurrentDamageStage);
    UpdateVisualDamage();
  }
}

void UTGExosuitComponent::UpdateVisualDamage() {
  // Stub: could swap materials, play effects, etc.
}

bool UTGExosuitComponent::ValidateAugmentInstallation(
    UTGAugmentData *AugmentData, int32 SlotIndex) const {
  if (!AugmentData) {
    return false;
  }
  if (SlotIndex < 0) {
    return false;
  }
  return true;
}
