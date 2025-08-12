#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TGWeapon.generated.h"

class UTGWeaponInstance;

USTRUCT()
struct FTGShotParams {
  GENERATED_BODY()
  UPROPERTY() FVector_NetQuantize10 Origin = FVector::ZeroVector;
  UPROPERTY() FVector_NetQuantizeNormal Direction = FVector::ForwardVector;
  UPROPERTY() float Timestamp = 0.f; // client time for lag compensation
};

UCLASS()
class TGCOMBAT_API ATGWeapon : public AActor {
  GENERATED_BODY()
public:
  ATGWeapon();

  UFUNCTION(BlueprintCallable) void StartFire();
  UFUNCTION(BlueprintCallable) void StopFire();
  UFUNCTION(BlueprintCallable) void Reload();

protected:
  UPROPERTY(ReplicatedUsing = OnRep_WeaponData)
  TObjectPtr<UTGWeaponInstance> WeaponData;
  FTimerHandle FireTimer;

  UFUNCTION() void OnRep_WeaponData();

  UFUNCTION(Server, Reliable) void ServerFire(const FTGShotParams &Params);
  void HandleFireTick();

  virtual void GetLifetimeReplicatedProps(
      TArray<FLifetimeProperty> &OutLifetimeProps) const override;
};
