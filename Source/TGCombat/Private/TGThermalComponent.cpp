#include "TGThermalComponent.h"

UTGThermalComponent::UTGThermalComponent() {
  PrimaryComponentTick.bCanEverTick = true;
  CurrentHeat = 0.0f;
  CurrentThermalState = EThermalState::Cool;
  bIsCooling = false;
  CoolingStartTime = 0.0f;
}

void UTGThermalComponent::BeginPlay() {
  Super::BeginPlay();
  UpdateThermalState();
}

void UTGThermalComponent::TickComponent(
    float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction *ThisTickFunction) {
  Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

  float EffectiveCooling = PassiveCoolingRate;
  if (bIsCooling) {
    EffectiveCooling += CoolingRate;
  }

  if (CurrentHeat > 0.0f) {
    CurrentHeat =
        FMath::Clamp(CurrentHeat - EffectiveCooling * DeltaTime, 0.0f, MaxHeat);
    UpdateThermalState();
  }
}

void UTGThermalComponent::AddHeat(float HeatAmount) {
  CurrentHeat =
      FMath::Clamp(CurrentHeat + FMath::Max(0.0f, HeatAmount), 0.0f, MaxHeat);
  UpdateThermalState();
  if (CurrentHeat >= OverheatThreshold) {
    HandleOverheat();
  }
}

void UTGThermalComponent::StartCooling() {
  bIsCooling = true;
  CoolingStartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
}

void UTGThermalComponent::ForceCooldown() {
  bIsCooling = false;
  CurrentHeat = 0.0f;
  UpdateThermalState();
  OnCoolingCompleted.Broadcast();
}

float UTGThermalComponent::GetHeatPercentage() const {
  return (MaxHeat > 0.0f) ? (CurrentHeat / MaxHeat) : 0.0f;
}

bool UTGThermalComponent::IsOverheated() const {
  return CurrentThermalState == EThermalState::Overheated ||
         CurrentThermalState == EThermalState::Critical;
}

bool UTGThermalComponent::CanFire() const { return !IsOverheated(); }

void UTGThermalComponent::SetMaxHeat(float NewMaxHeat) {
  MaxHeat = FMath::Max(0.0f, NewMaxHeat);
  CurrentHeat = FMath::Clamp(CurrentHeat, 0.0f, MaxHeat);
  UpdateThermalState();
}

void UTGThermalComponent::SetCoolingRate(float NewCoolingRate) {
  CoolingRate = FMath::Max(0.0f, NewCoolingRate);
}

void UTGThermalComponent::SetOverheatThreshold(float NewThreshold) {
  OverheatThreshold = FMath::Clamp(NewThreshold, 0.0f, MaxHeat);
}

void UTGThermalComponent::UpdateThermalState() {
  EThermalState OldState = CurrentThermalState;
  CurrentThermalState = CalculateThermalState();
  if (OldState != CurrentThermalState) {
    if (CurrentThermalState == EThermalState::Overheated) {
      OnOverheatTriggered.Broadcast();
    }
    OnThermalStateChanged.Broadcast(OldState, CurrentThermalState);
  }
}

EThermalState UTGThermalComponent::CalculateThermalState() const {
  const float Pct = GetHeatPercentage() * 100.0f;

  if (Pct >= CriticalThreshold) {
    return EThermalState::Critical;
  }
  if (Pct >= OverheatThreshold) {
    return EThermalState::Overheated;
  }
  if (Pct >= HotThreshold) {
    return EThermalState::Hot;
  }
  if (Pct >= WarmThreshold) {
    return EThermalState::Warm;
  }
  return EThermalState::Cool;
}

void UTGThermalComponent::HandleOverheat() { bIsCooling = true; }
