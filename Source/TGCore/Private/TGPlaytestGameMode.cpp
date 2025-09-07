#include "TGPlaytestGameMode.h"
#include "TGPlayPawn.h"
#include "TGCombat/Public/TGDemoSetup.h"
#include "TGAI/Public/TGEnemyGrunt.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Engine.h"

ATGPlaytestGameMode::ATGPlaytestGameMode()
{
    DefaultPawnClass = ATGPlayPawn::StaticClass();
    
    // Initialize mission settings
    bAutoSetupOnBeginPlay = true;
    MissionSetupDelay = 2.0f;
    bShowMissionUpdates = true;
    
    // Initialize state
    CurrentMissionState = EPlaytestMissionState::Setup;
    RemainingEnemies = 0;
    TotalEnemies = 0;
    bAllEnemiesCleared = false;
    bPlayerInExtractionZone = false;
}

void ATGPlaytestGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    if (bAutoSetupOnBeginPlay)
    {
        // Delay setup to allow level to fully load
        GetWorldTimerManager().SetTimer(MissionSetupTimerHandle, 
                                       this, 
                                       &ATGPlaytestGameMode::MissionSetupTimer, 
                                       MissionSetupDelay, 
                                       false);
    }
}

void ATGPlaytestGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // Clear all timers
    GetWorldTimerManager().ClearTimer(MissionSetupTimerHandle);
    GetWorldTimerManager().ClearTimer(MissionCheckTimerHandle);
    
    Super::EndPlay(EndPlayReason);
}

void ATGPlaytestGameMode::MissionSetupTimer()
{
    InitializeMission();
}

void ATGPlaytestGameMode::InitializeMission()
{
    UE_LOG(LogTemp, Warning, TEXT("ATGPlaytestGameMode: Initializing Mission"));
    
    // Find the demo setup actor
    FindDemoSetup();
    
    if (DemoSetup)
    {
        // Set up demo if not already done
        DemoSetup->SetupCompleteDemo();
        
        // Set up enemy tracking
        SetupEnemyTracking();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ATGPlaytestGameMode: Could not find ATGDemoSetup actor"));
    }
    
    // Initialize mission state
    SetMissionState(EPlaytestMissionState::InProgress);
    
    // Start periodic mission status checking
    GetWorldTimerManager().SetTimer(MissionCheckTimerHandle,
                                   this,
                                   &ATGPlaytestGameMode::MissionStatusCheck,
                                   1.0f,
                                   true);
    
    // Notify Blueprint
    OnMissionInitialized();
    
    if (bShowMissionUpdates && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Yellow, 
                                       TEXT("Mission Objective: Eliminate all enemies, then reach extraction"));
    }
}

void ATGPlaytestGameMode::FindDemoSetup()
{
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), ATGDemoSetup::StaticClass(), FoundActors);
    
    if (FoundActors.Num() > 0)
    {
        DemoSetup = Cast<ATGDemoSetup>(FoundActors[0]);
        UE_LOG(LogTemp, Warning, TEXT("ATGPlaytestGameMode: Found ATGDemoSetup actor"));
    }
}

void ATGPlaytestGameMode::SetupEnemyTracking()
{
    if (!DemoSetup)
        return;
        
    TrackedEnemies.Empty();
    
    // Get all spawned enemies from demo setup
    const TArray<ATGEnemyGrunt*>& SpawnedEnemies = DemoSetup->SpawnedEnemies;
    
    for (ATGEnemyGrunt* Enemy : SpawnedEnemies)
    {
        if (Enemy && IsValid(Enemy))
        {
            RegisterEnemy(Enemy);
        }
    }
    
    UpdateEnemyCount();
    
    UE_LOG(LogTemp, Warning, TEXT("ATGPlaytestGameMode: Tracking %d enemies"), TrackedEnemies.Num());
}

void ATGPlaytestGameMode::StartMission()
{
    if (CurrentMissionState == EPlaytestMissionState::Setup)
    {
        InitializeMission();
    }
}

void ATGPlaytestGameMode::SetMissionState(EPlaytestMissionState NewState)
{
    if (CurrentMissionState != NewState)
    {
        CurrentMissionState = NewState;
        OnMissionStateChanged.Broadcast(CurrentMissionState);
        
        // Log state changes
        FString StateString;
        switch (NewState)
        {
            case EPlaytestMissionState::Setup:
                StateString = TEXT("Setup");
                break;
            case EPlaytestMissionState::InProgress:
                StateString = TEXT("In Progress");
                break;
            case EPlaytestMissionState::WaitingForExtraction:
                StateString = TEXT("Waiting For Extraction");
                break;
            case EPlaytestMissionState::Success:
                StateString = TEXT("Success");
                break;
            case EPlaytestMissionState::Failed:
                StateString = TEXT("Failed");
                break;
        }
        
        UE_LOG(LogTemp, Warning, TEXT("ATGPlaytestGameMode: Mission State -> %s"), *StateString);
    }
}

void ATGPlaytestGameMode::RegisterEnemy(ATGEnemyGrunt* Enemy)
{
    if (Enemy && IsValid(Enemy))
    {
        TrackedEnemies.AddUnique(Enemy);
        UpdateEnemyCount();
    }
}

void ATGPlaytestGameMode::UnregisterEnemy(ATGEnemyGrunt* Enemy)
{
    if (Enemy)
    {
        TrackedEnemies.Remove(Enemy);
        UpdateEnemyCount();
    }
}

void ATGPlaytestGameMode::OnEnemyDied(ATGEnemyGrunt* Enemy)
{
    if (Enemy)
    {
        UnregisterEnemy(Enemy);
        
        if (bShowMissionUpdates && GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Green, 
                                           FString::Printf(TEXT("Enemy Eliminated! %d Remaining"), RemainingEnemies));
        }
        
        // Check if all enemies are dead
        if (RemainingEnemies <= 0)
        {
            bAllEnemiesCleared = true;
            SetMissionState(EPlaytestMissionState::WaitingForExtraction);
            
            if (bShowMissionUpdates && GEngine)
            {
                GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Yellow, 
                                               TEXT("All enemies eliminated! Head to extraction zone!"));
            }
        }
    }
}

void ATGPlaytestGameMode::UpdateEnemyCount()
{
    // Clean up invalid references
    TrackedEnemies.RemoveAll([](const TWeakObjectPtr<ATGEnemyGrunt>& Enemy) {
        return !Enemy.IsValid() || Enemy->IsDead();
    });
    
    RemainingEnemies = TrackedEnemies.Num();
    
    // Set total on first count
    if (TotalEnemies == 0)
    {
        TotalEnemies = RemainingEnemies;
    }
    
    OnEnemyCountChanged.Broadcast(RemainingEnemies, TotalEnemies);
}

void ATGPlaytestGameMode::PlayerEnteredExtractionZone()
{
    bPlayerInExtractionZone = true;
    CheckMissionStatus();
    
    if (bShowMissionUpdates && GEngine)
    {
        if (bAllEnemiesCleared)
        {
            GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Green, 
                                           TEXT("Mission Complete! Well done!"));
        }
        else
        {
            GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Red, 
                                           FString::Printf(TEXT("Eliminate remaining enemies first! %d left"), RemainingEnemies));
        }
    }
}

void ATGPlaytestGameMode::PlayerExitedExtractionZone()
{
    bPlayerInExtractionZone = false;
}

void ATGPlaytestGameMode::OnPlayerDied()
{
    SetMissionState(EPlaytestMissionState::Failed);
    FailMission();
}

void ATGPlaytestGameMode::CheckMissionStatus()
{
    if (CurrentMissionState == EPlaytestMissionState::InProgress || 
        CurrentMissionState == EPlaytestMissionState::WaitingForExtraction)
    {
        // Check for mission success
        if (bAllEnemiesCleared && bPlayerInExtractionZone)
        {
            CompleteMission();
        }
    }
}

void ATGPlaytestGameMode::CompleteMission()
{
    SetMissionState(EPlaytestMissionState::Success);
    OnMissionComplete.Broadcast();
    
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Green, 
                                       TEXT("MISSION SUCCESS! Press R to restart"));
    }
    
    // Stop mission checking
    GetWorldTimerManager().ClearTimer(MissionCheckTimerHandle);
}

void ATGPlaytestGameMode::FailMission()
{
    SetMissionState(EPlaytestMissionState::Failed);
    OnMissionFailed.Broadcast();
    
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Red, 
                                       TEXT("MISSION FAILED! Press R to restart"));
    }
    
    // Stop mission checking  
    GetWorldTimerManager().ClearTimer(MissionCheckTimerHandle);
}

void ATGPlaytestGameMode::RestartMission()
{
    // Clear current state
    TrackedEnemies.Empty();
    RemainingEnemies = 0;
    TotalEnemies = 0;
    bAllEnemiesCleared = false;
    bPlayerInExtractionZone = false;
    
    // Reset demo setup
    if (DemoSetup)
    {
        DemoSetup->ResetDemo();
    }
    
    // Restart mission after brief delay
    GetWorldTimerManager().SetTimer(MissionSetupTimerHandle, 
                                   this, 
                                   &ATGPlaytestGameMode::MissionSetupTimer, 
                                   1.0f, 
                                   false);
    
    SetMissionState(EPlaytestMissionState::Setup);
}

void ATGPlaytestGameMode::MissionStatusCheck()
{
    UpdateEnemyCount();
    CheckMissionStatus();
}