#include "TGWeapon.h"
#include "Net/UnrealNetwork.h"
#include "TGWeaponInstance.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

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
  Params.Origin = GetActorLocation();
  Params.Direction = GetActorForwardVector();
  Params.Timestamp = GetWorld()->GetTimeSeconds();

  if (HasAuthority()) {
    // Perform authoritative trace/projectile
    PerformWeaponTrace(Params);
  } else {
    ServerFire(Params);
  }
}

void ATGWeapon::ServerFire_Implementation(const FTGShotParams &Params) {
  // Validate against lag compensation and apply damage
  PerformWeaponTrace(Params);
}

void ATGWeapon::PerformWeaponTrace(const FTGShotParams& ShotParams) {
  if (!GetWorld()) return;

  FVector Start = ShotParams.Origin;
  FVector End = Start + (ShotParams.Direction * 10000.0f); // 100m range

  FHitResult HitResult;
  FCollisionQueryParams QueryParams;
  QueryParams.AddIgnoredActor(this);
  QueryParams.AddIgnoredActor(GetOwner());

  bool bHit = GetWorld()->LineTraceSingleByChannel(
    HitResult,
    Start,
    End,
    ECollisionChannel::ECC_Visibility,
    QueryParams
  );

  if (bHit) {
    // Apply damage to hit actor
    AActor* HitActor = HitResult.GetActor();
    if (HitActor) {
      UGameplayStatics::ApplyDamage(
        HitActor,
        25.0f, // Base damage
        GetInstigatorController(),
        this,
        UDamageType::StaticClass()
      );
    }
  }
}

void ATGWeapon::OnRep_WeaponData() {}

void ATGWeapon::GetLifetimeReplicatedProps(
    TArray<FLifetimeProperty> &OutLifetimeProps) const {
  Super::GetLifetimeReplicatedProps(OutLifetimeProps);
  DOREPLIFETIME(ATGWeapon, WeaponData);
}
