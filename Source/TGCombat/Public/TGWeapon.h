#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameplayTagContainer.h"
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

  // Siege & GAS Integration
  UFUNCTION(BlueprintCallable, Category = "Weapon|Siege")
  void StartFireWithTags(const FGameplayTagContainer& SiegeBuffTags);

  UFUNCTION(BlueprintCallable, Category = "Weapon|Siege")
  void ApplySiegeWeaponModifier(float DamageMultiplier, float RateOfFireMultiplier, float Duration);

  UFUNCTION(BlueprintPure, Category = "Weapon|Siege")
  float GetSiegeDamageMultiplier() const { return SiegeDamageMultiplier; }

  UFUNCTION(BlueprintPure, Category = "Weapon|Siege")
  float GetSiegeRateOfFireMultiplier() const { return SiegeRateOfFireMultiplier; }

  UFUNCTION(BlueprintPure, Category = "Weapon|Siege")
  bool HasSiegeModifiers() const { return SiegeDamageMultiplier != 1.0f || SiegeRateOfFireMultiplier != 1.0f; }

  // Weapon functionality
  UFUNCTION(BlueprintCallable, Category = "Weapon")
  void PerformWeaponTrace(const FTGShotParams& ShotParams);

protected:
  UPROPERTY(ReplicatedUsing = OnRep_WeaponData)
  TObjectPtr<UTGWeaponInstance> WeaponData;
  FTimerHandle FireTimer;

  // Siege Modifiers
  UPROPERTY(Replicated, BlueprintReadOnly, Category = "Weapon|Siege")
  float SiegeDamageMultiplier = 1.0f;

  UPROPERTY(Replicated, BlueprintReadOnly, Category = "Weapon|Siege")
  float SiegeRateOfFireMultiplier = 1.0f;

  UPROPERTY(Replicated, BlueprintReadOnly, Category = "Weapon|Siege")
  float SiegeModifierEndTime = 0.0f;

  UPROPERTY(BlueprintReadOnly, Category = "Weapon|Siege")
  FGameplayTagContainer ActiveSiegeTags;

  UFUNCTION() void OnRep_WeaponData();

  UFUNCTION(Server, Reliable) void ServerFire(const FTGShotParams &Params);
  void HandleFireTick();

  virtual void GetLifetimeReplicatedProps(
      TArray<FLifetimeProperty> &OutLifetimeProps) const override;
};
