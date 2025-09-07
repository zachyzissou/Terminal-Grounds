#include "TGDemoSetup.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "TGAI/Public/TGEnemyGrunt.h"
#include "TGWeapon.h"
#include "TGCore/Public/TGPlayPawn.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"

ATGDemoSetup::ATGDemoSetup()
{
    PrimaryActorTick.bCanEverTick = false;

    // Set default classes
    EnemyClass = ATGEnemyGrunt::StaticClass();
    WeaponClass = ATGWeapon::StaticClass();
}

void ATGDemoSetup::BeginPlay()
{
    Super::BeginPlay();

    if (bAutoSetupOnBeginPlay)
    {
        // Auto-setup demo after a short delay
        FTimerHandle SetupTimer;
        GetWorld()->GetTimerManager().SetTimer(SetupTimer, this, &ATGDemoSetup::SetupCompleteDemo, 1.0f, false);
    }
}

void ATGDemoSetup::SetupCompleteDemo()
{
    UE_LOG(LogTemp, Log, TEXT("=== TERMINAL GROUNDS DEMO SETUP ==="));

    // Create the demo environment
    if (bCreateCoverObjects)
    {
        CreateCoverObjects();
    }

    if (bCreatePatrolPoints)
    {
        CreatePatrolPoints();
    }

    if (bSetupLighting)
    {
        SetupLighting();
    }

    // Spawn player and weapon
    SpawnPlayer();
    SpawnWeapon();

    // Spawn enemies
    SpawnEnemies();

    LogDemoStatus();
    UE_LOG(LogTemp, Log, TEXT("=== DEMO SETUP COMPLETE ==="));
}

void ATGDemoSetup::SpawnEnemies()
{
    if (!EnemyClass)
    {
        UE_LOG(LogTemp, Warning, TEXT("No enemy class set for demo"));
        return;
    }

    SpawnedEnemies.Empty();

    // Predefined enemy spawn locations for strategic positioning
    TArray<FVector> EnemySpawnLocations = {
        FVector(500, 500, 100),    // Northeast
        FVector(-500, 500, 100),   // Northwest
        FVector(500, -500, 100),   // Southeast
        FVector(-500, -500, 100),  // Southwest
        FVector(0, 800, 100),      // North
        FVector(0, -800, 100),     // South
        FVector(800, 0, 100),      // East
        FVector(-800, 0, 100)      // West
    };

    for (int32 i = 0; i < FMath::Min(NumberOfEnemies, EnemySpawnLocations.Num()); i++)
    {
        FVector SpawnLocation = EnemySpawnLocations[i];
        FRotator SpawnRotation = FRotator(0, FMath::RandRange(0, 360), 0);

        ATGEnemyGrunt* NewEnemy = GetWorld()->SpawnActor<ATGEnemyGrunt>(
            EnemyClass,
            SpawnLocation,
            SpawnRotation
        );

        if (NewEnemy)
        {
            SpawnedEnemies.Add(NewEnemy);
            UE_LOG(LogTemp, Log, TEXT("Spawned enemy %d at location %s"), i+1, *SpawnLocation.ToString());
        }
    }
}

void ATGDemoSetup::SpawnPlayer()
{
    if (!PlayerClass)
    {
        UE_LOG(LogTemp, Warning, TEXT("No player class set for demo"));
        return;
    }

    FVector PlayerLocation = FVector(0, 0, 100);
    FRotator PlayerRotation = FRotator::ZeroRotator;

    PlayerPawn = GetWorld()->SpawnActor<ATGPlayPawn>(
        PlayerClass,
        PlayerLocation,
        PlayerRotation
    );

    if (PlayerPawn)
    {
        UE_LOG(LogTemp, Log, TEXT("Spawned player at location %s"), *PlayerLocation.ToString());
    }
}

void ATGDemoSetup::SpawnWeapon()
{
    if (!WeaponClass || !PlayerPawn)
    {
        UE_LOG(LogTemp, Warning, TEXT("No weapon class or player pawn for demo"));
        return;
    }

    FVector WeaponLocation = PlayerPawn->GetActorLocation() + FVector(50, 0, 0);
    FRotator WeaponRotation = PlayerPawn->GetActorRotation();

    PlayerWeapon = GetWorld()->SpawnActor<ATGWeapon>(
        WeaponClass,
        WeaponLocation,
        WeaponRotation
    );

    if (PlayerWeapon)
    {
        // Attach weapon to player
        PlayerWeapon->AttachToActor(PlayerPawn, FAttachmentTransformRules::KeepWorldTransform);
        UE_LOG(LogTemp, Log, TEXT("Spawned weapon and attached to player"));
    }
}

void ATGDemoSetup::CreateCoverObjects()
{
    CreateBasicCover();
}

void ATGDemoSetup::CreatePatrolPoints()
{
    CreatePatrolWaypoints();
}

void ATGDemoSetup::SetupLighting()
{
    SetupAtmosphericLighting();
}

void ATGDemoSetup::ResetDemo()
{
    // Clear existing enemies
    for (ATGEnemyGrunt* Enemy : SpawnedEnemies)
    {
        if (IsValid(Enemy))
        {
            Enemy->Destroy();
        }
    }
    SpawnedEnemies.Empty();

    // Clear cover objects
    for (AActor* Cover : CoverObjects)
    {
        if (IsValid(Cover))
        {
            Cover->Destroy();
        }
    }
    CoverObjects.Empty();

    // Clear patrol points
    for (AActor* Point : PatrolPoints)
    {
        if (IsValid(Point))
        {
            Point->Destroy();
        }
    }
    PatrolPoints.Empty();

    // Reset player
    if (IsValid(PlayerPawn))
    {
        PlayerPawn->SetActorLocation(FVector(0, 0, 100));
    }

    // Reset weapon
    if (IsValid(PlayerWeapon))
    {
        PlayerWeapon->SetActorLocation(PlayerPawn->GetActorLocation() + FVector(50, 0, 0));
    }
}

FVector ATGDemoSetup::GetRandomSpawnLocation() const
{
    FVector Center = GetActorLocation();
    FVector RandomOffset = FVector(
        FMath::RandRange(-EnemySpawnRadius, EnemySpawnRadius),
        FMath::RandRange(-EnemySpawnRadius, EnemySpawnRadius),
        0
    );

    return Center + RandomOffset;
}

void ATGDemoSetup::LogDemoStatus() const
{
    UE_LOG(LogTemp, Log, TEXT("=== DEMO STATUS ==="));
    UE_LOG(LogTemp, Log, TEXT("Enemies spawned: %d"), SpawnedEnemies.Num());
    UE_LOG(LogTemp, Log, TEXT("Cover objects: %d"), CoverObjects.Num());
    UE_LOG(LogTemp, Log, TEXT("Patrol points: %d"), PatrolPoints.Num());
    UE_LOG(LogTemp, Log, TEXT("Player pawn: %s"), PlayerPawn ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("Player weapon: %s"), PlayerWeapon ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("================"));
}

void ATGDemoSetup::CreateBasicCover()
{
    // Create strategic cover objects
    TArray<FVector> CoverPositions = {
        FVector(300, 300, 0),    // Northeast
        FVector(-300, 300, 0),   // Northwest
        FVector(300, -300, 0),   // Southeast
        FVector(-300, -300, 0),  // Southwest
        FVector(600, 0, 0),      // East
        FVector(-600, 0, 0),     // West
        FVector(0, 600, 0),      // North
        FVector(0, -600, 0)      // South
    };

    for (int32 i = 0; i < CoverPositions.Num(); i++)
    {
        AStaticMeshActor* CoverActor = GetWorld()->SpawnActor<AStaticMeshActor>(
            AStaticMeshActor::StaticClass(),
            CoverPositions[i],
            FRotator::ZeroRotator
        );

        if (CoverActor)
        {
            CoverActor->SetActorLabel(FString::Printf(TEXT("Cover_%d"), i+1));
            UStaticMeshComponent* MeshComp = CoverActor->GetStaticMeshComponent();
            if (MeshComp)
            {
                // Use a basic cube mesh for cover
                MeshComp->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube")));
                MeshComp->SetWorldScale3D(FVector(2, 2, 3)); // Make it tall for cover
                CoverObjects.Add(CoverActor);
                UE_LOG(LogTemp, Log, TEXT("Created cover object %d at %s"), i+1, *CoverPositions[i].ToString());
            }
        }
    }
}

void ATGDemoSetup::CreatePatrolWaypoints()
{
    // Create patrol waypoints for AI enemies
    TArray<FVector> WaypointPositions = {
        FVector(200, 200, 0),    // Northeast
        FVector(-200, 200, 0),   // Northwest
        FVector(-200, -200, 0),  // Southwest
        FVector(200, -200, 0),   // Southeast
        FVector(400, 0, 0),      // East
        FVector(-400, 0, 0),     // West
        FVector(0, 400, 0),      // North
        FVector(0, -400, 0)      // South
    };

    for (int32 i = 0; i < WaypointPositions.Num(); i++)
    {
        AStaticMeshActor* WaypointActor = GetWorld()->SpawnActor<AStaticMeshActor>(
            AStaticMeshActor::StaticClass(),
            WaypointPositions[i],
            FRotator::ZeroRotator
        );

        if (WaypointActor)
        {
            WaypointActor->SetActorLabel(FString::Printf(TEXT("PatrolPoint_%d"), i+1));
            UStaticMeshComponent* MeshComp = WaypointActor->GetStaticMeshComponent();
            if (MeshComp)
            {
                // Use a small sphere for waypoints
                MeshComp->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere")));
                MeshComp->SetWorldScale3D(FVector(0.5, 0.5, 0.5));
                MeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                PatrolPoints.Add(WaypointActor);
                UE_LOG(LogTemp, Log, TEXT("Created patrol waypoint %d at %s"), i+1, *WaypointPositions[i].ToString());
            }
        }
    }
}

void ATGDemoSetup::SetupAtmosphericLighting()
{
    // Create main directional light
    ADirectionalLight* MainLight = GetWorld()->SpawnActor<ADirectionalLight>(
        ADirectionalLight::StaticClass(),
        FVector(0, 0, 1000),
        FRotator(45, 45, 0)
    );

    if (MainLight)
    {
        UDirectionalLightComponent* LightComp = MainLight->GetComponent();
        if (LightComp)
        {
            LightComp->SetIntensity(3.0f);
            LightComp->SetLightColor(FLinearColor(1.0f, 0.9f, 0.8f));
        }
        UE_LOG(LogTemp, Log, TEXT("Created main directional light"));
    }

    // Create sky light
    ASkyLight* SkyLight = GetWorld()->SpawnActor<ASkyLight>(
        ASkyLight::StaticClass(),
        FVector(0, 0, 500),
        FRotator::ZeroRotator
    );

    if (SkyLight)
    {
        USkyLightComponent* SkyComp = SkyLight->GetComponent();
        if (SkyComp)
        {
            SkyComp->SetIntensity(1.0f);
        }
        UE_LOG(LogTemp, Log, TEXT("Created sky light"));
    }

    // Create atmospheric fog
    AExponentialHeightFog* Fog = GetWorld()->SpawnActor<AExponentialHeightFog>(
        AExponentialHeightFog::StaticClass(),
        FVector(0, 0, 0),
        FRotator::ZeroRotator
    );

    if (Fog)
    {
        UExponentialHeightFogComponent* FogComp = Fog->GetComponent();
        if (FogComp)
        {
            FogComp->SetFogDensity(0.02f);
            FogComp->SetFogHeightFalloff(0.2f);
            FogComp->SetFogInscatteringColor(FLinearColor(0.8f, 0.9f, 1.0f));
        }
        UE_LOG(LogTemp, Log, TEXT("Created atmospheric fog"));
    }
}
