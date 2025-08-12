#include "TGWeapon.h"
#include "Net/UnrealNetwork.h"
#include "TGWeaponInstance.h"

ATGWeapon::ATGWeapon() {
  bReplicates = true;
  SetReplicateMovement(true);
}

void ATGWeapon::StartFire() {
  HandleFireTick();
  const float Rate =
      WeaponData ? FMath::Max(WeaponData->FireRate, 0.01f) : 0.1f;
  GetWorldTimerManager().SetTimer(FireTimer, this, &ATGWeapon::HandleFireTick,
                                  Rate, true);
}

void ATGWeapon::StopFire() { GetWorldTimerManager().ClearTimer(FireTimer); }

void ATGWeapon::Reload() {}

void ATGWeapon::HandleFireTick() {
  FTGShotParams Params;
  Params.Timestamp = GetWorld()->GetTimeSeconds();
  if (HasAuthority()) {
    // TODO: perform authoritative trace/projectile
  } else {
    ServerFire(Params);
  }
}

void ATGWeapon::ServerFire_Implementation(const FTGShotParams &Params) {
  // TODO: validate against lag compensation and apply damage
}

void ATGWeapon::OnRep_WeaponData() {}

void ATGWeapon::GetLifetimeReplicatedProps(
    TArray<FLifetimeProperty> &OutLifetimeProps) const {
  Super::GetLifetimeReplicatedProps(OutLifetimeProps);
  DOREPLIFETIME(ATGWeapon, WeaponData);
}
