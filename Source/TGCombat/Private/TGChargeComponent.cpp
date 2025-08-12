#include "TGChargeComponent.h"

UTGChargeComponent::UTGChargeComponent() {
  PrimaryComponentTick.bCanEverTick = true;
  CurrentCharge = 0.0f;
  CurrentChargeState = EChargeState::Discharged;
  bIsCharging = false;
  bIsEMPDisrupted = false;
  EMPDisruptionEndTime = 0.0f;
}

void UTGChargeComponent::BeginPlay() {
  Super::BeginPlay();
  UpdateChargeState();
}

void UTGChargeComponent::TickComponent(
    float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction *ThisTickFunction) {
  Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

  ProcessEMPDisruption(DeltaTime);

  if (bIsCharging && !bIsEMPDisrupted) {
    CurrentCharge =
        FMath::Clamp(CurrentCharge + (ChargeRate * DeltaTime), 0.0f, MaxCharge);
    UpdateChargeState();
  } else if (!bIsCharging && CurrentCharge > 0.f) {
    CurrentCharge =
        FMath::Max(0.0f, CurrentCharge - (DischargeRate * DeltaTime));
    UpdateChargeState();
  }
}

void UTGChargeComponent::StartCharging() { bIsCharging = true; }

void UTGChargeComponent::StopCharging() { bIsCharging = false; }

void UTGChargeComponent::DischargeWeapon() {
  CurrentCharge = 0.0f;
  UpdateChargeState();
}

void UTGChargeComponent::DrainCharge(float ChargeAmount) {
  CurrentCharge = FMath::Clamp(CurrentCharge - FMath::Max(0.0f, ChargeAmount),
                               0.0f, MaxCharge);
  UpdateChargeState();
}

void UTGChargeComponent::ForceOvercharge() {
  CurrentCharge = MaxCharge;
  EChargeState OldState = CurrentChargeState;
  CurrentChargeState = EChargeState::Overcharged;
  OnOverchargeTriggered.Broadcast();
  OnChargeStateChanged.Broadcast(OldState, CurrentChargeState);
}

float UTGChargeComponent::GetChargePercentage() const {
  return (MaxCharge > 0.0f) ? (CurrentCharge / MaxCharge) : 0.0f;
}

bool UTGChargeComponent::IsCharging() const { return bIsCharging; }

bool UTGChargeComponent::IsFullyCharged() const {
  return CurrentCharge >= ChargedThreshold;
}

bool UTGChargeComponent::CanFire() const {
  return !bIsEMPDisrupted && CurrentCharge >= MinChargeToFire &&
         CurrentChargeState != EChargeState::Overcharged;
}

float UTGChargeComponent::GetDamageMultiplier() const {
  return 1.0f + (GetChargePercentage());
}

void UTGChargeComponent::ApplyEMPDisruption(float DisruptionStrength,
                                            float Duration) {
  const float ClampedStrength =
      FMath::Clamp(DisruptionStrength * EMPVulnerability, 0.0f, 1.0f);
  bIsEMPDisrupted = ClampedStrength > 0.0f;
  if (bIsEMPDisrupted) {
    OnChargeDisrupted.Broadcast();
    EMPDisruptionEndTime =
        GetWorld() ? (GetWorld()->GetTimeSeconds() + Duration) : 0.0f;
  }
}

void UTGChargeComponent::SetChargeRate(float NewChargeRate) {
  ChargeRate = FMath::Max(0.0f, NewChargeRate);
}

void UTGChargeComponent::SetMaxCharge(float NewMaxCharge) {
  MaxCharge = FMath::Max(0.0f, NewMaxCharge);
  CurrentCharge = FMath::Clamp(CurrentCharge, 0.0f, MaxCharge);
  UpdateChargeState();
}

void UTGChargeComponent::UpdateChargeState() {
  EChargeState OldState = CurrentChargeState;
  CurrentChargeState = CalculateChargeState();
  if (OldState != CurrentChargeState) {
    if (CurrentChargeState == EChargeState::Charged) {
      OnFullyCharged.Broadcast();
    } else if (CurrentChargeState == EChargeState::Overcharged) {
      OnOverchargeTriggered.Broadcast();
    }
    OnChargeStateChanged.Broadcast(OldState, CurrentChargeState);
  }
}

EChargeState UTGChargeComponent::CalculateChargeState() const {
  const float Pct = GetChargePercentage() * 100.0f;
  if (Pct >= UnstableThreshold) {
    return EChargeState::Unstable;
  }
  if (Pct >= OverchargeThreshold) {
    return EChargeState::Overcharged;
  }
  if (Pct >= ChargedThreshold) {
    return EChargeState::Charged;
  }
  if (bIsCharging) {
    return EChargeState::Charging;
  }
  return EChargeState::Discharged;
}

void UTGChargeComponent::ProcessEMPDisruption(float DeltaTime) {
  if (bIsEMPDisrupted && GetWorld()) {
    if (GetWorld()->GetTimeSeconds() >= EMPDisruptionEndTime) {
      bIsEMPDisrupted = false;
    }
  }
}
