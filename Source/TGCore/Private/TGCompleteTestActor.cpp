#include "TGCompleteTestActor.h"
#include "TGPlaytestGameMode.h"
#include "TGWorld/Public/TGProceduralWorldSubsystem.h"
#include "TGCombat/Public/TGDemoSetup.h"
#include "TGPlaytestExtractionZone.h"
#include "TGAI/Public/TGEnemyGrunt.h"
#include "TGCombat/Public/TGWeapon.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"
#include "NavigationSystem.h"
#include "Components/BoxComponent.h"
#include "TimerManager.h"

ATGCompleteTestActor::ATGCompleteTestActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // Create root component
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

    // Default configuration
    ScenarioType = ETestScenarioType::DirectorateOutpost;
    bAutoSetupOnBeginPlay = true;
    SetupDelay = 2.0f;
    
    // Combat defaults
    NumberOfEnemies = 8;
    CombatAreaRadius = 5000.0f;
    
    // Procedural defaults
    bGenerateProceduralEnvironment = true;
    ProceduralGenerationRadius = 10000.0f;
    NumberOfTerritories = 3;
    bGenerateBuildings = true;
    bGenerateDetails = true;
    bGenerateVegetation = true;
    
    // Extraction defaults
    bCreateExtractionZone = true;
    ExtractionZoneOffset = FVector(0, 5000.0f, 0); // 50m north of center
}

void ATGCompleteTestActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (bAutoSetupOnBeginPlay)
    {
        // Delay setup to allow level systems to initialize
        GetWorld()->GetTimerManager().SetTimer(SetupTimerHandle, this, &ATGCompleteTestActor::DelayedSetup, SetupDelay, false);
        
        UE_LOG(LogTemp, Warning, TEXT("ATGCompleteTestActor: Starting complete Terminal Grounds test in %.1f seconds..."), SetupDelay);
    }
}

void ATGCompleteTestActor::DelayedSetup()
{
    SetupCompleteTest();
}

void ATGCompleteTestActor::SetupCompleteTest()
{
    UE_LOG(LogTemp, Warning, TEXT("========================================"));
    UE_LOG(LogTemp, Warning, TEXT("TERMINAL GROUNDS COMPLETE TEST STARTING"));
    UE_LOG(LogTemp, Warning, TEXT("========================================"));
    
    LogTestConfiguration();
    ValidateGameMode();
    
    // Setup in order: Environment -> Combat -> Extraction
    if (bGenerateProceduralEnvironment)
    {
        SetupProceduralEnvironment();
    }
    
    SetupCombatScenario();
    
    if (bCreateExtractionZone)
    {
        SetupExtractionZone();
    }
    
    OnTestSetupComplete();
    
    UE_LOG(LogTemp, Warning, TEXT("========================================"));
    UE_LOG(LogTemp, Warning, TEXT("TERMINAL GROUNDS TEST SETUP COMPLETE"));
    UE_LOG(LogTemp, Warning, TEXT("Mission: Eliminate all enemies and reach extraction"));
    UE_LOG(LogTemp, Warning, TEXT("========================================"));
}

void ATGCompleteTestActor::SetupCombatScenario()
{
    UE_LOG(LogTemp, Warning, TEXT("Setting up combat scenario with %d enemies..."), NumberOfEnemies);
    
    // Spawn the demo setup actor
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    
    SpawnedDemoSetup = GetWorld()->SpawnActor<ATGDemoSetup>(
        ATGDemoSetup::StaticClass(),
        GetActorLocation(),
        FRotator::ZeroRotator,
        SpawnParams
    );
    
    if (SpawnedDemoSetup)
    {
        // Configure demo setup
        SpawnedDemoSetup->NumberOfEnemies = NumberOfEnemies;
        SpawnedDemoSetup->EnemySpawnRadius = CombatAreaRadius;
        SpawnedDemoSetup->bAutoSetupOnBeginPlay = false; // We'll trigger manually
        
        // Set enemy and weapon classes if specified
        if (EnemyClass)
        {
            SpawnedDemoSetup->EnemyClass = EnemyClass;
        }
        if (WeaponClass)
        {
            SpawnedDemoSetup->WeaponClass = WeaponClass;
        }
        
        // Create cover objects based on scenario
        SpawnedDemoSetup->bCreateCoverObjects = true;
        SpawnedDemoSetup->bCreatePatrolPoints = true;
        
        // Setup the demo
        SpawnedDemoSetup->SetupCompleteDemo();
        
        UE_LOG(LogTemp, Warning, TEXT("Combat scenario setup complete: %d enemies spawned"), SpawnedDemoSetup->SpawnedEnemies.Num());
        OnCombatSetupComplete(SpawnedDemoSetup->SpawnedEnemies.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to spawn ATGDemoSetup!"));
    }
}

void ATGCompleteTestActor::SetupProceduralEnvironment()
{
    UE_LOG(LogTemp, Warning, TEXT("Generating procedural environment for scenario: %s"), 
           *UEnum::GetValueAsString(ScenarioType));
    
    UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (!ProceduralSystem)
    {
        UE_LOG(LogTemp, Error, TEXT("UTGProceduralWorldSubsystem not found!"));
        return;
    }
    
    GenerateScenarioEnvironment();
}

void ATGCompleteTestActor::GenerateScenarioEnvironment()
{
    UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (!ProceduralSystem)
    {
        return;
    }
    
    GeneratedTerritoryIDs.Empty();
    
    switch (ScenarioType)
    {
        case ETestScenarioType::DirectorateOutpost:
        {
            // Single Directorate territory
            GenerateTerritory(1001, (uint8)ELocalFactionID::Directorate, GetActorLocation(), ProceduralGenerationRadius);
            break;
        }
        
        case ETestScenarioType::Free77Stronghold:
        {
            // Single Free77 territory with heavy fortification
            GenerateTerritory(2001, (uint8)ELocalFactionID::Free77, GetActorLocation(), ProceduralGenerationRadius);
            break;
        }
        
        case ETestScenarioType::ContestedTerritory:
        {
            // Two opposing faction territories
            FVector DirectoratePos = GetActorLocation() + FVector(-ProceduralGenerationRadius * 0.6f, 0, 0);
            FVector Free77Pos = GetActorLocation() + FVector(ProceduralGenerationRadius * 0.6f, 0, 0);
            
            GenerateTerritory(3001, (uint8)ELocalFactionID::Directorate, DirectoratePos, ProceduralGenerationRadius * 0.5f);
            GenerateTerritory(3002, (uint8)ELocalFactionID::Free77, Free77Pos, ProceduralGenerationRadius * 0.5f);
            break;
        }
        
        case ETestScenarioType::MultiFactionalBattle:
        {
            // Multiple faction territories in a circle
            float AngleStep = 360.0f / NumberOfTerritories;
            TArray<uint8> Factions = {
                (uint8)ELocalFactionID::Directorate,
                (uint8)ELocalFactionID::Free77,
                (uint8)ELocalFactionID::CivicWardens,
                (uint8)ELocalFactionID::NomadClans,
                (uint8)ELocalFactionID::VulturesUnion
            };
            
            for (int32 i = 0; i < NumberOfTerritories; i++)
            {
                float Angle = FMath::DegreesToRadians(AngleStep * i);
                FVector TerritoryPos = GetActorLocation() + FVector(
                    FMath::Cos(Angle) * ProceduralGenerationRadius * 0.7f,
                    FMath::Sin(Angle) * ProceduralGenerationRadius * 0.7f,
                    0
                );
                
                uint8 FactionID = Factions[i % Factions.Num()];
                GenerateTerritory(4001 + i, FactionID, TerritoryPos, ProceduralGenerationRadius * 0.4f);
            }
            break;
        }
        
        case ETestScenarioType::RandomizedEnvironment:
        {
            // Random faction territories
            FRandomStream RandomStream(FMath::Rand());
            
            for (int32 i = 0; i < NumberOfTerritories; i++)
            {
                FVector RandomPos = GetActorLocation() + FVector(
                    RandomStream.FRandRange(-ProceduralGenerationRadius, ProceduralGenerationRadius),
                    RandomStream.FRandRange(-ProceduralGenerationRadius, ProceduralGenerationRadius),
                    0
                );
                
                uint8 RandomFaction = RandomStream.RandRange(1, 7); // Random faction
                GenerateTerritory(5001 + i, RandomFaction, RandomPos, ProceduralGenerationRadius * 0.3f);
            }
            break;
        }
    }
    
    OnProceduralGenerationComplete(GeneratedTerritoryIDs.Num());
}

void ATGCompleteTestActor::GenerateTerritory(int32 TerritoryID, uint8 FactionID, FVector CenterLocation, float Radius)
{
    UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (!ProceduralSystem)
    {
        return;
    }
    
    FProceduralGenerationRequest Request;
    Request.TerritoryID = TerritoryID;
    Request.TerritoryType = ELocalTerritoryType::District;
    Request.DominantFaction = (ELocalFactionID)FactionID;
    Request.CenterLocation = CenterLocation;
    Request.GenerationRadius = Radius;
    
    // Set generation type based on configuration
    if (bGenerateBuildings && bGenerateDetails && bGenerateVegetation)
    {
        Request.GenerationType = EProceduralGenerationType::All;
    }
    else if (bGenerateBuildings)
    {
        Request.GenerationType = EProceduralGenerationType::Buildings;
    }
    else if (bGenerateDetails)
    {
        Request.GenerationType = EProceduralGenerationType::Details;
    }
    else if (bGenerateVegetation)
    {
        Request.GenerationType = EProceduralGenerationType::Vegetation;
    }
    
    bool bSuccess = ProceduralSystem->GenerateTerritory(Request);
    
    if (bSuccess)
    {
        GeneratedTerritoryIDs.Add(TerritoryID);
        
        FString FactionName = UEnum::GetValueAsString((ELocalFactionID)FactionID);
        UE_LOG(LogTemp, Warning, TEXT("Generated %s territory (ID: %d) at %s with radius %.0f"), 
               *FactionName, TerritoryID, *CenterLocation.ToString(), Radius);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to generate territory %d"), TerritoryID);
    }
}

void ATGCompleteTestActor::SetupExtractionZone()
{
    UE_LOG(LogTemp, Warning, TEXT("Creating extraction zone..."));
    
    FVector ExtractionLocation = GetActorLocation() + ExtractionZoneOffset;
    
    // Line trace to ground
    FHitResult HitResult;
    FVector TraceStart = ExtractionLocation + FVector(0, 0, 1000);
    FVector TraceEnd = ExtractionLocation - FVector(0, 0, 1000);
    
    if (GetWorld()->LineTraceSingleByChannel(HitResult, TraceStart, TraceEnd, ECC_WorldStatic))
    {
        ExtractionLocation = HitResult.Location;
    }
    
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    
    SpawnedExtractionZone = GetWorld()->SpawnActor<ATGPlaytestExtractionZone>(
        ATGPlaytestExtractionZone::StaticClass(),
        ExtractionLocation,
        FRotator::ZeroRotator,
        SpawnParams
    );
    
    if (SpawnedExtractionZone)
    {
        SpawnedExtractionZone->bRequiresAllEnemiesDead = true;
        SpawnedExtractionZone->bShowDebugMessages = true;
        
        UE_LOG(LogTemp, Warning, TEXT("Extraction zone created at %s"), *ExtractionLocation.ToString());
        OnExtractionZoneCreated();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to spawn extraction zone!"));
    }
}

void ATGCompleteTestActor::CleanupTest()
{
    UE_LOG(LogTemp, Warning, TEXT("Cleaning up test environment..."));
    
    // Clear generated territories
    ClearAllGeneratedTerritories();
    
    // Destroy spawned actors
    if (SpawnedDemoSetup)
    {
        SpawnedDemoSetup->ResetDemo();
        SpawnedDemoSetup->Destroy();
        SpawnedDemoSetup = nullptr;
    }
    
    if (SpawnedExtractionZone)
    {
        SpawnedExtractionZone->Destroy();
        SpawnedExtractionZone = nullptr;
    }
    
    UE_LOG(LogTemp, Warning, TEXT("Test cleanup complete"));
}

void ATGCompleteTestActor::ClearAllGeneratedTerritories()
{
    UTGProceduralWorldSubsystem* ProceduralSystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (!ProceduralSystem)
    {
        return;
    }
    
    for (int32 TerritoryID : GeneratedTerritoryIDs)
    {
        ProceduralSystem->ClearTerritoryGeneration(TerritoryID, ELocalTerritoryType::District);
    }
    
    GeneratedTerritoryIDs.Empty();
}

FVector ATGCompleteTestActor::GetRandomLocationInRadius(float Radius) const
{
    float RandomAngle = FMath::FRandRange(0.0f, 360.0f);
    float RandomDistance = FMath::FRandRange(0.0f, Radius);
    
    float X = FMath::Cos(FMath::DegreesToRadians(RandomAngle)) * RandomDistance;
    float Y = FMath::Sin(FMath::DegreesToRadians(RandomAngle)) * RandomDistance;
    
    return GetActorLocation() + FVector(X, Y, 0);
}

uint8 ATGCompleteTestActor::GetFactionForScenario() const
{
    switch (ScenarioType)
    {
        case ETestScenarioType::DirectorateOutpost:
            return (uint8)ELocalFactionID::Directorate;
        case ETestScenarioType::Free77Stronghold:
            return (uint8)ELocalFactionID::Free77;
        default:
            return (uint8)ELocalFactionID::None;
    }
}

void ATGCompleteTestActor::ValidateGameMode()
{
    AGameModeBase* CurrentGameMode = GetWorld()->GetAuthGameMode();
    if (!CurrentGameMode->IsA<ATGPlaytestGameMode>())
    {
        UE_LOG(LogTemp, Warning, TEXT("WARNING: Current game mode is not ATGPlaytestGameMode!"));
        UE_LOG(LogTemp, Warning, TEXT("Some features may not work correctly. Please set World Settings -> Game Mode to ATGPlaytestGameMode"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Game mode validated: ATGPlaytestGameMode active"));
    }
}

void ATGCompleteTestActor::LogTestConfiguration()
{
    UE_LOG(LogTemp, Warning, TEXT("Test Configuration:"));
    UE_LOG(LogTemp, Warning, TEXT("  Scenario: %s"), *UEnum::GetValueAsString(ScenarioType));
    UE_LOG(LogTemp, Warning, TEXT("  Enemies: %d"), NumberOfEnemies);
    UE_LOG(LogTemp, Warning, TEXT("  Combat Radius: %.0fm"), CombatAreaRadius / 100.0f);
    UE_LOG(LogTemp, Warning, TEXT("  Procedural Generation: %s"), bGenerateProceduralEnvironment ? TEXT("Enabled") : TEXT("Disabled"));
    
    if (bGenerateProceduralEnvironment)
    {
        UE_LOG(LogTemp, Warning, TEXT("  Territories: %d"), NumberOfTerritories);
        UE_LOG(LogTemp, Warning, TEXT("  Generation Radius: %.0fm"), ProceduralGenerationRadius / 100.0f);
        UE_LOG(LogTemp, Warning, TEXT("  Buildings: %s"), bGenerateBuildings ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Warning, TEXT("  Details: %s"), bGenerateDetails ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Warning, TEXT("  Vegetation: %s"), bGenerateVegetation ? TEXT("Yes") : TEXT("No"));
    }
    
    UE_LOG(LogTemp, Warning, TEXT("  Extraction Zone: %s"), bCreateExtractionZone ? TEXT("Enabled") : TEXT("Disabled"));
}