#include "TGDemoWeapon.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Particles/ParticleSystem.h"
#include "Sound/SoundCue.h"
#include "DrawDebugHelpers.h"
#include "TimerManager.h"

ATGDemoWeapon::ATGDemoWeapon()
{
    PrimaryActorTick.bCanEverTick = true;

    // Create root component
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

    // Create weapon mesh
    WeaponMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WeaponMesh"));
    WeaponMesh->SetupAttachment(RootComponent);

    // Create muzzle location
    MuzzleLocation = CreateDefaultSubobject<USceneComponent>(TEXT("MuzzleLocation"));
    MuzzleLocation->SetupAttachment(WeaponMesh);

    // Create muzzle flash component
    MuzzleFlash = CreateDefaultSubobject<UParticleSystemComponent>(TEXT("MuzzleFlash"));
    MuzzleFlash->SetupAttachment(MuzzleLocation);
    MuzzleFlash->bAutoActivate = false;

    // Set default values
    CurrentAmmo = MaxAmmo;
}

void ATGDemoWeapon::BeginPlay()
{
    Super::BeginPlay();

    // Initialize weapon
    CurrentAmmo = MaxAmmo;
}

void ATGDemoWeapon::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void ATGDemoWeapon::Fire()
{
    if (!CanFire())
    {
        return;
    }

    // Consume ammo
    CurrentAmmo--;

    // Perform line trace
    PerformLineTrace();

    // Play effects
    PlayFireEffects();

    // Set fire rate timer
    GetWorldTimerManager().SetTimer(FireTimerHandle, this, &ATGDemoWeapon::Fire, FireRate, false);
}

void ATGDemoWeapon::Reload()
{
    if (CurrentAmmo >= MaxAmmo)
    {
        return;
    }

    // Play reload effects
    PlayReloadEffects();

    // Reload after delay
    FTimerHandle ReloadTimerHandle;
    GetWorldTimerManager().SetTimer(ReloadTimerHandle, [this]()
    {
        CurrentAmmo = MaxAmmo;
    }, 2.0f, false);
}

void ATGDemoWeapon::StopFiring()
{
    GetWorldTimerManager().ClearTimer(FireTimerHandle);
}

void ATGDemoWeapon::PerformLineTrace()
{
    if (!GetWorld())
    {
        return;
    }

    FVector Start = MuzzleLocation->GetComponentLocation();
    FVector Forward = MuzzleLocation->GetForwardVector();
    FVector End = Start + (Forward * Range);

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

    // Draw debug line
    FColor LineColor = bHit ? FColor::Red : FColor::Green;
    DrawDebugLine(GetWorld(), Start, End, LineColor, false, 1.0f, 0, 1.0f);

    if (bHit)
    {
        // Spawn impact effect
        SpawnImpactEffect(HitResult.Location, HitResult.Normal);

        // Apply damage to hit actor
        AActor* HitActor = HitResult.GetActor();
        if (HitActor)
        {
            // Apply damage using Unreal's damage system
            UGameplayStatics::ApplyDamage(
                HitActor,
                Damage,
                GetInstigatorController(),
                this,
                UDamageType::StaticClass()
            );
        }
    }
}

void ATGDemoWeapon::SpawnImpactEffect(FVector Location, FVector Normal)
{
    if (ImpactEffect)
    {
        UGameplayStatics::SpawnEmitterAtLocation(
            GetWorld(),
            ImpactEffect,
            Location,
            Normal.Rotation()
        );
    }
}

void ATGDemoWeapon::PlayFireEffects()
{
    // Play muzzle flash
    if (MuzzleFlashEffect)
    {
        MuzzleFlash->SetTemplate(MuzzleFlashEffect);
        MuzzleFlash->ActivateSystem();
    }

    // Play fire sound
    if (FireSound)
    {
        UGameplayStatics::PlaySoundAtLocation(
            GetWorld(),
            FireSound,
            MuzzleLocation->GetComponentLocation()
        );
    }
}

void ATGDemoWeapon::PlayReloadEffects()
{
    // Play reload sound
    if (ReloadSound)
    {
        UGameplayStatics::PlaySoundAtLocation(
            GetWorld(),
            ReloadSound,
            GetActorLocation()
        );
    }
}
