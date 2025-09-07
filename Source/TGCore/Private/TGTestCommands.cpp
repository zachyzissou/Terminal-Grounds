#include "TGTestCommands.h"
#include "TGCompleteTestActor.h"
#include "TGPlaytestGameMode.h"
#include "TGWorld/Public/TGProceduralWorldSubsystem.h"
#include "TGCombat/Public/TGDemoSetup.h"
#include "TGAI/Public/TGEnemyGrunt.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"

UTGTestCommands::UTGTestCommands()
{
}

UWorld* UTGTestCommands::GetWorldFromContext(const UObject* WorldContext)
{
    if (!WorldContext)
    {
        return nullptr;
    }
    
    // Try to get world from various context types
    if (const UWorld* World = WorldContext->GetWorld())
    {
        return const_cast<UWorld*>(World);
    }
    
    return nullptr;
}

void UTGTestCommands::TG_SpawnCompleteTest(const UObject* WorldContext)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        UE_LOG(LogTemp, Error, TEXT("TG_SpawnCompleteTest: Invalid world context"));
        return;
    }
    
    // Get player location for spawn
    FVector SpawnLocation = FVector::ZeroVector;
    if (APlayerController* PC = World->GetFirstPlayerController())
    {
        if (APawn* PlayerPawn = PC->GetPawn())
        {
            SpawnLocation = PlayerPawn->GetActorLocation();
        }
    }
    
    // Spawn the complete test actor
    FActorSpawnParameters SpawnParams;
    SpawnParams.Name = TEXT("TG_CompleteTestActor");
    
    ATGCompleteTestActor* TestActor = World->SpawnActor<ATGCompleteTestActor>(
        ATGCompleteTestActor::StaticClass(),
        SpawnLocation,
        FRotator::ZeroRotator,
        SpawnParams
    );
    
    if (TestActor)
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Green, 
                TEXT("Terminal Grounds Complete Test spawned! Combat and procedural generation will begin in 2 seconds..."));
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_SpawnCompleteTest: Successfully spawned complete test actor at %s"), 
               *SpawnLocation.ToString());
    }
    else
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, 
                TEXT("Failed to spawn Terminal Grounds test actor!"));
        }
        UE_LOG(LogTemp, Error, TEXT("TG_SpawnCompleteTest: Failed to spawn test actor"));
    }
}

void UTGTestCommands::TG_GenerateTerritory(const UObject* WorldContext, int32 TerritoryID, int32 FactionID)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    UTGProceduralWorldSubsystem* ProceduralSystem = World->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (!ProceduralSystem)
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, 
                TEXT("Procedural World Subsystem not found!"));
        }
        return;
    }
    
    // Get player location as center
    FVector CenterLocation = FVector::ZeroVector;
    if (APlayerController* PC = World->GetFirstPlayerController())
    {
        if (APawn* PlayerPawn = PC->GetPawn())
        {
            CenterLocation = PlayerPawn->GetActorLocation();
        }
    }
    
    FProceduralGenerationRequest Request;
    Request.TerritoryID = TerritoryID;
    Request.TerritoryType = ELocalTerritoryType::District;
    Request.DominantFaction = (ELocalFactionID)FMath::Clamp(FactionID, 0, 7);
    Request.CenterLocation = CenterLocation;
    Request.GenerationRadius = 5000.0f;
    Request.GenerationType = EProceduralGenerationType::All;
    
    bool bSuccess = ProceduralSystem->GenerateTerritory(Request);
    
    if (bSuccess)
    {
        FString FactionName = UEnum::GetValueAsString((ELocalFactionID)FactionID);
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Green, 
                FString::Printf(TEXT("Generated %s territory (ID: %d)"), *FactionName, TerritoryID));
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_GenerateTerritory: Generated territory %d for faction %s"), 
               TerritoryID, *FactionName);
    }
    else
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, 
                TEXT("Failed to generate territory!"));
        }
    }
}

void UTGTestCommands::TG_ClearTerritory(const UObject* WorldContext, int32 TerritoryID)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    UTGProceduralWorldSubsystem* ProceduralSystem = World->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (!ProceduralSystem)
    {
        return;
    }
    
    ProceduralSystem->ClearTerritoryGeneration(TerritoryID, ELocalTerritoryType::District);
    
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Yellow, 
            FString::Printf(TEXT("Cleared territory %d"), TerritoryID));
    }
    UE_LOG(LogTemp, Warning, TEXT("TG_ClearTerritory: Cleared territory %d"), TerritoryID);
}

void UTGTestCommands::TG_SpawnEnemies(const UObject* WorldContext, int32 Count)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    // Find or create demo setup
    ATGDemoSetup* DemoSetup = nullptr;
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(World, ATGDemoSetup::StaticClass(), FoundActors);
    
    if (FoundActors.Num() > 0)
    {
        DemoSetup = Cast<ATGDemoSetup>(FoundActors[0]);
    }
    else
    {
        // Create new demo setup
        FVector SpawnLocation = FVector::ZeroVector;
        if (APlayerController* PC = World->GetFirstPlayerController())
        {
            if (APawn* PlayerPawn = PC->GetPawn())
            {
                SpawnLocation = PlayerPawn->GetActorLocation();
            }
        }
        
        DemoSetup = World->SpawnActor<ATGDemoSetup>(
            ATGDemoSetup::StaticClass(),
            SpawnLocation,
            FRotator::ZeroRotator
        );
    }
    
    if (DemoSetup)
    {
        DemoSetup->NumberOfEnemies = Count;
        DemoSetup->SpawnEnemies();
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Green, 
                FString::Printf(TEXT("Spawned %d enemies"), Count));
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_SpawnEnemies: Spawned %d enemies"), Count);
    }
}

void UTGTestCommands::TG_RestartMission(const UObject* WorldContext)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    if (ATGPlaytestGameMode* GameMode = Cast<ATGPlaytestGameMode>(World->GetAuthGameMode()))
    {
        GameMode->RestartMission();
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Yellow, 
                TEXT("Mission restarting..."));
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_RestartMission: Mission restart initiated"));
    }
    else
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, 
                TEXT("ATGPlaytestGameMode not active! Set it in World Settings"));
        }
    }
}

void UTGTestCommands::TG_ShowStatus(const UObject* WorldContext)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    if (ATGPlaytestGameMode* GameMode = Cast<ATGPlaytestGameMode>(World->GetAuthGameMode()))
    {
        FString StatusMessage = FString::Printf(
            TEXT("Mission Status:\n  State: %s\n  Enemies: %d/%d\n  Can Extract: %s"),
            *UEnum::GetValueAsString(GameMode->GetMissionState()),
            GameMode->GetRemainingEnemies(),
            GameMode->GetTotalEnemies(),
            GameMode->CanExtract() ? TEXT("Yes") : TEXT("No")
        );
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Cyan, StatusMessage);
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_ShowStatus:\n%s"), *StatusMessage);
    }
}

void UTGTestCommands::TG_TestDirectorateVsFree77(const UObject* WorldContext)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    // Spawn complete test actor with contested territory
    FVector SpawnLocation = FVector::ZeroVector;
    if (APlayerController* PC = World->GetFirstPlayerController())
    {
        if (APawn* PlayerPawn = PC->GetPawn())
        {
            SpawnLocation = PlayerPawn->GetActorLocation();
        }
    }
    
    ATGCompleteTestActor* TestActor = World->SpawnActor<ATGCompleteTestActor>(
        ATGCompleteTestActor::StaticClass(),
        SpawnLocation,
        FRotator::ZeroRotator
    );
    
    if (TestActor)
    {
        TestActor->ScenarioType = ETestScenarioType::ContestedTerritory;
        TestActor->NumberOfEnemies = 10;
        TestActor->NumberOfTerritories = 2;
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Cyan, 
                TEXT("Directorate vs Free77 battle scenario spawned!"));
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_TestDirectorateVsFree77: Contested territory scenario created"));
    }
}

void UTGTestCommands::TG_TestMultiFaction(const UObject* WorldContext)
{
    UWorld* World = GetWorldFromContext(WorldContext);
    if (!World)
    {
        return;
    }
    
    // Spawn complete test actor with multi-faction battle
    FVector SpawnLocation = FVector::ZeroVector;
    if (APlayerController* PC = World->GetFirstPlayerController())
    {
        if (APawn* PlayerPawn = PC->GetPawn())
        {
            SpawnLocation = PlayerPawn->GetActorLocation();
        }
    }
    
    ATGCompleteTestActor* TestActor = World->SpawnActor<ATGCompleteTestActor>(
        ATGCompleteTestActor::StaticClass(),
        SpawnLocation,
        FRotator::ZeroRotator
    );
    
    if (TestActor)
    {
        TestActor->ScenarioType = ETestScenarioType::MultiFactionalBattle;
        TestActor->NumberOfEnemies = 15;
        TestActor->NumberOfTerritories = 5;
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Cyan, 
                TEXT("Multi-faction battle scenario spawned! 5 factions competing!"));
        }
        UE_LOG(LogTemp, Warning, TEXT("TG_TestMultiFaction: Multi-faction battle scenario created"));
    }
}

void UTGTestCommands::TG_Help(const UObject* WorldContext)
{
    FString HelpText = TEXT("Terminal Grounds Console Commands:\n\n");
    HelpText += TEXT("TG_SpawnCompleteTest - Spawn full test with enemies and procedural generation\n");
    HelpText += TEXT("TG_GenerateTerritory [ID] [FactionID] - Generate faction territory at player location\n");
    HelpText += TEXT("TG_ClearTerritory [ID] - Clear specific territory\n");
    HelpText += TEXT("TG_SpawnEnemies [Count] - Spawn enemies at player location\n");
    HelpText += TEXT("TG_RestartMission - Restart current mission\n");
    HelpText += TEXT("TG_ShowStatus - Show mission status\n");
    HelpText += TEXT("TG_TestDirectorateVsFree77 - Spawn Directorate vs Free77 scenario\n");
    HelpText += TEXT("TG_TestMultiFaction - Spawn 5-faction battle scenario\n");
    HelpText += TEXT("\nFaction IDs: 1=Directorate, 2=Free77, 3=NomadClans, 4=CivicWardens,\n");
    HelpText += TEXT("             5=VulturesUnion, 6=VaultedArchivists, 7=CorporateCombine");
    
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 20.0f, FColor::White, HelpText);
    }
    UE_LOG(LogTemp, Warning, TEXT("%s"), *HelpText);
}