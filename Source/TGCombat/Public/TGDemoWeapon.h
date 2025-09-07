#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Particles/ParticleSystemComponent.h"
#include "Sound/SoundCue.h"
#include "TGWeapon.h"
#include "TGDemoWeapon.generated.h"

UCLASS()
class TGCOMBAT_API ATGDemoWeapon : public ATGWeapon
{
    GENERATED_BODY()

public:
    ATGDemoWeapon();

protected:
    virtual void BeginPlay() override;

    // Weapon Components
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Weapon")
    UStaticMeshComponent* WeaponMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Weapon")
    USceneComponent* MuzzleLocation;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Weapon")
    UParticleSystemComponent* MuzzleFlash;

    // Weapon Properties
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float Damage = 25.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float Range = 10000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float FireRate = 0.1f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    int32 MaxAmmo = 30;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    int32 CurrentAmmo = 30;

    // Visual Effects
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effects")
    UParticleSystem* MuzzleFlashEffect;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effects")
    UParticleSystem* ImpactEffect;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effects")
    USoundCue* FireSound;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effects")
    USoundCue* ReloadSound;

    // Timers
    FTimerHandle FireTimerHandle;

public:
    virtual void Tick(float DeltaTime) override;

    // Weapon Functions
    UFUNCTION(BlueprintCallable, Category = "Weapon")
    virtual void Fire();

    virtual void Reload();

    UFUNCTION(BlueprintCallable, Category = "Weapon")
    void StopFiring();

    UFUNCTION(BlueprintPure, Category = "Weapon")
    int32 GetCurrentAmmo() const { return CurrentAmmo; }

    UFUNCTION(BlueprintPure, Category = "Weapon")
    int32 GetMaxAmmo() const { return MaxAmmo; }

    UFUNCTION(BlueprintPure, Category = "Weapon")
    bool CanFire() const { return CurrentAmmo > 0 && !GetWorldTimerManager().IsTimerActive(FireTimerHandle); }

protected:
    void PerformLineTrace();
    void SpawnImpactEffect(FVector Location, FVector Normal);
    void PlayFireEffects();
    void PlayReloadEffects();
};
