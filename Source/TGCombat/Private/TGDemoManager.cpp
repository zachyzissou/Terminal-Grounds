#include "TGDemoManager.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "TGEnemyGrunt.h"
#include "TGWeapon.h"
#include "TGCore/Public/TGPlayPawn.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

ATGDemoManager::ATGDemoManager()
{
    PrimaryActorTick.bCanEverTick = false;
    
    // Set default classes
    EnemyClass = ATGEnemyGrunt::StaticClass();
    WeaponClass = ATGWeapon::StaticClass();
}

void ATGDemoManager::BeginPlay()
{
    Super::BeginPlay();
    
    // Auto-setup demo after a short delay
    FTimerHandle SetupTimer;
    GetWorld()->GetTimerManager().SetTimer(SetupTimer, this, &ATGDemoManager::SetupDemo, 1.0f, false);
}

void ATGDemoManager::SetupDemo()
{
    UE_LOG(LogTemp, Log, TEXT("Setting up Terminal Grounds Demo"));
    
    // Create the demo environment
    CreateCoverObjects();
    CreatePatrolPoints();
    
    // Spawn player and weapon
    SpawnPlayer();
    SpawnWeapon();
    
    // Spawn enemies
    SpawnEnemies();
    
    UE_LOG(LogTemp, Log, TEXT("Demo setup complete!"));
}

void ATGDemoManager::SpawnEnemies()
{
    if (!EnemyClass)
    {
        UE_LOG(LogTemp, Warning, TEXT("No enemy class set for demo"));
        return;
    }
    
    SpawnedEnemies.Empty();
    
    for (int32 i = 0; i < NumberOfEnemies; i++)
    {
        FVector SpawnLocation = GetRandomSpawnLocation();
        FRotator SpawnRotation = FRotator(0, FMath::RandRange(0, 360), 0);
        
        ATGEnemyGrunt* NewEnemy = GetWorld()->SpawnActor<ATGEnemyGrunt>(
            EnemyClass, 
            SpawnLocation, 
            SpawnRotation
        );
        
        if (NewEnemy)
        {
            SpawnedEnemies.Add(NewEnemy);
            UE_LOG(LogTemp, Log, TEXT("Spawned enemy %d at location %s"), i, *SpawnLocation.ToString());
        }
    }
}

void ATGDemoManager::SpawnPlayer()
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

void ATGDemoManager::SpawnWeapon()
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

void ATGDemoManager::CreateCoverObjects()
{
    CreateBasicCover();
}

void ATGDemoManager::CreatePatrolPoints()
{
    CreatePatrolWaypoints();
}

FVector ATGDemoManager::GetRandomSpawnLocation() const
{
    FVector Center = GetActorLocation();
    FVector RandomOffset = FVector(
        FMath::RandRange(-EnemySpawnRadius, EnemySpawnRadius),
        FMath::RandRange(-EnemySpawnRadius, EnemySpawnRadius),
        0
    );
    
    return Center + RandomOffset;
}

void ATGDemoManager::ResetDemo()
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

void ATGDemoManager::CreateBasicCover()
{
    // Create some basic cover objects using static meshes
    TArray<FVector> CoverPositions = {
        FVector(500, 500, 0),
        FVector(-500, 500, 0),
        FVector(500, -500, 0),
        FVector(-500, -500, 0),
        FVector(0, 800, 0),
        FVector(0, -800, 0),
        FVector(800, 0, 0),
        FVector(-800, 0, 0)
    };
    
    for (const FVector& Position : CoverPositions)
    {
        AStaticMeshActor* CoverActor = GetWorld()->SpawnActor<AStaticMeshActor>(
            AStaticMeshActor::StaticClass(),
            Position,
            FRotator::ZeroRotator
        );
        
        if (CoverActor)
        {
            // Set a basic cube mesh (you can replace with actual cover meshes)
            UStaticMeshComponent* MeshComp = CoverActor->GetStaticMeshComponent();
            if (MeshComp)
            {
                // Use a basic cube mesh - you can replace this with actual cover assets
                MeshComp->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube")));
                MeshComp->SetWorldScale3D(FVector(2, 2, 3)); // Make it tall for cover
                UE_LOG(LogTemp, Log, TEXT("Created cover object at %s"), *Position.ToString());
            }
        }
    }
}

void ATGDemoManager::CreatePatrolWaypoints()
{
    // Create patrol waypoints for AI enemies
    TArray<FVector> WaypointPositions = {
        FVector(300, 300, 0),
        FVector(-300, 300, 0),
        FVector(-300, -300, 0),
        FVector(300, -300, 0),
        FVector(600, 0, 0),
        FVector(-600, 0, 0),
        FVector(0, 600, 0),
        FVector(0, -600, 0)
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
            WaypointActor->SetActorLabel(FString::Printf(TEXT("PatrolPoint_%d"), i));
            UStaticMeshComponent* MeshComp = WaypointActor->GetStaticMeshComponent();
            if (MeshComp)
            {
                // Use a small sphere for waypoints
                MeshComp->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere")));
                MeshComp->SetWorldScale3D(FVector(0.5, 0.5, 0.5));
                MeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                UE_LOG(LogTemp, Log, TEXT("Created patrol waypoint %d at %s"), i, *WaypointPositions[i].ToString());
            }
        }
    }
}
