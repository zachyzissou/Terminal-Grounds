#include "TGEconomicVictoryGameMode.h"
#include "TGEconomicVictorySubsystem.h"
#include "TGWorld/Public/Economy/TGConvoyEconomySubsystem.h"
#include "TGTerritorial/Public/TerritorialManager.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "GameFramework/GameStateBase.h"

ATGEconomicVictoryGameMode::ATGEconomicVictoryGameMode()
{
    // Default values
    bEnableEconomicVictory = true;
    SessionTimeLimit = 1800.0f; // 30 minutes
    MaxPlayersPerFaction = 8;
    bAllowMultipleVictoryTypes = true;
    VictoryAnnouncementDelay = 5.0f;

    // Initialize state
    bSessionActive = false;
    SessionStartTime = 0.0f;
    SessionWinner = -1;
    WinningVictoryType = EEconomicVictoryType::None;
}

void ATGEconomicVictoryGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);
    
    // Get subsystem references
    if (UWorld* World = GetWorld())
    {
        EconomicVictorySubsystem = World->GetSubsystem<UTGEconomicVictorySubsystem>();
        ConvoyEconomySubsystem = World->GetSubsystem<UTGConvoyEconomySubsystem>();
        
        // Territorial manager is accessed via subsystem
        if (UTerritorialSubsystem* TerritorialSubsystem = World->GetSubsystem<UTerritorialSubsystem>())
        {
            TerritorialManager = UTerritorialSubsystem::GetTerritorialManager(World);
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Game Mode initialized"));
}

void ATGEconomicVictoryGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    SetupSubsystemIntegration();
    
    if (bEnableEconomicVictory)
    {
        // Auto-start if enabled
        StartEconomicWarfareSession();
    }
}

void ATGEconomicVictoryGameMode::StartPlay()
{
    Super::StartPlay();
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Game Mode started play"));
}

void ATGEconomicVictoryGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    CleanupSubsystemIntegration();
    
    if (bSessionActive)
    {
        EndEconomicWarfareSession();
    }
    
    Super::EndPlay(EndPlayReason);
}

void ATGEconomicVictoryGameMode::StartEconomicWarfareSession()
{
    if (!ValidateSessionStart())
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot start economic warfare session - validation failed"));
        return;
    }
    
    // Initialize session state
    ResetSessionState();
    bSessionActive = true;
    SessionStartTime = GetWorld()->GetTimeSeconds();
    
    // Start economic victory subsystem session
    if (EconomicVictorySubsystem)
    {
        EconomicVictorySubsystem->StartEconomicVictorySession();
        InitializeEconomicVictoryConditions();
    }
    
    // Set up time warning timer
    if (SessionTimeLimit > 0.0f)
    {
        float WarningTime = SessionTimeLimit - 300.0f; // 5 minutes before end
        if (WarningTime > 0.0f)
        {
            GetWorld()->GetTimerManager().SetTimer(SessionTimeWarningTimer, 
                                                  this, 
                                                  &ATGEconomicVictoryGameMode::CheckSessionTimeWarnings, 
                                                  60.0f, // Check every minute
                                                  true,
                                                  WarningTime);
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("Economic Warfare Session Started"));
    OnEconomicVictorySessionStarted();
}

void ATGEconomicVictoryGameMode::EndEconomicWarfareSession()
{
    if (!bSessionActive)
    {
        return;
    }
    
    bSessionActive = false;
    
    // Clear timers
    GetWorld()->GetTimerManager().ClearTimer(SessionTimeWarningTimer);
    GetWorld()->GetTimerManager().ClearTimer(VictoryAnnouncementTimer);
    
    // End economic victory subsystem session
    if (EconomicVictorySubsystem)
    {
        EconomicVictorySubsystem->EndEconomicVictorySession();
    }
    
    UE_LOG(LogTemp, Log, TEXT("Economic Warfare Session Ended"));
    OnEconomicVictorySessionEnded(SessionWinner, WinningVictoryType);
}

void ATGEconomicVictoryGameMode::HandleEconomicVictory(int32 WinningFactionID, EEconomicVictoryType VictoryType)
{
    if (SessionWinner != -1)
    {
        // Victory already achieved
        return;
    }
    
    SessionWinner = WinningFactionID;
    WinningVictoryType = VictoryType;
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Achieved: Faction %d won via %s"), 
           WinningFactionID, *UEnum::GetValueAsString(VictoryType));
    
    // Delayed victory announcement to allow for dramatic effect
    GetWorld()->GetTimerManager().SetTimer(VictoryAnnouncementTimer,
                                          [this, WinningFactionID, VictoryType]()
                                          {
                                              AnnounceVictory(WinningFactionID, VictoryType);
                                          },
                                          VictoryAnnouncementDelay,
                                          false);
}

void ATGEconomicVictoryGameMode::OnExtractionObjectiveCompleted(int32 TerritoryID, int32 FactionID, float EconomicImpact)
{
    if (!bSessionActive || !EconomicVictorySubsystem)
    {
        return;
    }
    
    // Update economic metrics for the faction
    EconomicVictorySubsystem->UpdateEconomicMetrics(FactionID);
    
    UE_LOG(LogTemp, Log, TEXT("Extraction objective completed - Territory: %d, Faction: %d, Economic Impact: %.2f"), 
           TerritoryID, FactionID, EconomicImpact);
}

void ATGEconomicVictoryGameMode::OnConvoyRouteControlChanged(FName RouteID, int32 OldControllerID, int32 NewControllerID)
{
    if (!bSessionActive)
    {
        return;
    }
    
    UpdateEconomicImpactFromConvoyChange(RouteID, OldControllerID, NewControllerID);
    
    UE_LOG(LogTemp, Log, TEXT("Convoy route control changed - Route: %s, Old: %d, New: %d"), 
           *RouteID.ToString(), OldControllerID, NewControllerID);
}

void ATGEconomicVictoryGameMode::OnTerritorialControlChanged(int32 TerritoryID, int32 OldFactionID, int32 NewFactionID)
{
    if (!bSessionActive)
    {
        return;
    }
    
    UpdateEconomicImpactFromTerritorialChange(TerritoryID, OldFactionID, NewFactionID);
    
    UE_LOG(LogTemp, Log, TEXT("Territorial control changed - Territory: %d, Old: %d, New: %d"), 
           TerritoryID, OldFactionID, NewFactionID);
}

bool ATGEconomicVictoryGameMode::IsEconomicVictoryActive() const
{
    return bSessionActive && bEnableEconomicVictory;
}

float ATGEconomicVictoryGameMode::GetSessionElapsedTime() const
{
    if (!bSessionActive)
    {
        return 0.0f;
    }
    
    return GetWorld()->GetTimeSeconds() - SessionStartTime;
}

FEconomicVictoryProgress ATGEconomicVictoryGameMode::GetSessionLeader() const
{
    if (!EconomicVictorySubsystem)
    {
        return FEconomicVictoryProgress();
    }
    
    return EconomicVictorySubsystem->GetClosestVictoryToCompletion();
}

void ATGEconomicVictoryGameMode::OnEconomicVictoryAchieved(int32 FactionID, EEconomicVictoryType VictoryType, float CompletionTime)
{
    HandleEconomicVictory(FactionID, VictoryType);
}

void ATGEconomicVictoryGameMode::OnEconomicVictoryThreatened(int32 ThreateningFactionID, EEconomicVictoryType VictoryType, float TimeToVictory)
{
    UE_LOG(LogTemp, Warning, TEXT("Economic Victory Threatened: Faction %d approaching %s victory in %.1f seconds"), 
           ThreateningFactionID, *UEnum::GetValueAsString(VictoryType), TimeToVictory);
    
    // This could trigger UI alerts, announcements, etc.
}

void ATGEconomicVictoryGameMode::OnConvoyOutcome(FName RouteId, EJobType JobType, bool bSuccess)
{
    if (!bSessionActive || !EconomicVictorySubsystem)
    {
        return;
    }
    
    // Get the faction that controlled this route
    if (ConvoyEconomySubsystem)
    {
        FConvoyRoute Route = ConvoyEconomySubsystem->GetRoute(RouteId);
        if (Route.FactionControllerID > 0)
        {
            // Update metrics for the controlling faction
            EconomicVictorySubsystem->UpdateEconomicMetrics(Route.FactionControllerID);
        }
    }
}

void ATGEconomicVictoryGameMode::OnTerritorialControlChangedDelegate(int32 TerritoryID, ETerritoryType TerritoryType, int32 OldFaction, int32 NewFaction)
{
    OnTerritorialControlChanged(TerritoryID, OldFaction, NewFaction);
}

void ATGEconomicVictoryGameMode::SetupSubsystemIntegration()
{
    // Bind to economic victory events
    if (EconomicVictorySubsystem)
    {
        EconomicVictorySubsystem->OnEconomicVictoryAchieved.AddDynamic(this, &ATGEconomicVictoryGameMode::OnEconomicVictoryAchieved);
        EconomicVictorySubsystem->OnEconomicVictoryThreatened.AddDynamic(this, &ATGEconomicVictoryGameMode::OnEconomicVictoryThreatened);
    }
    
    // Bind to convoy economy events
    if (ConvoyEconomySubsystem)
    {
        ConvoyEconomySubsystem->OnConvoyOutcome.AddDynamic(this, &ATGEconomicVictoryGameMode::OnConvoyOutcome);
    }
    
    // Bind to territorial events
    if (TerritorialManager)
    {
        TerritorialManager->OnTerritorialControlChanged.AddDynamic(this, &ATGEconomicVictoryGameMode::OnTerritorialControlChangedDelegate);
    }
}

void ATGEconomicVictoryGameMode::CleanupSubsystemIntegration()
{
    // Unbind from economic victory events
    if (EconomicVictorySubsystem)
    {
        EconomicVictorySubsystem->OnEconomicVictoryAchieved.RemoveDynamic(this, &ATGEconomicVictoryGameMode::OnEconomicVictoryAchieved);
        EconomicVictorySubsystem->OnEconomicVictoryThreatened.RemoveDynamic(this, &ATGEconomicVictoryGameMode::OnEconomicVictoryThreatened);
    }
    
    // Unbind from convoy economy events
    if (ConvoyEconomySubsystem)
    {
        ConvoyEconomySubsystem->OnConvoyOutcome.RemoveDynamic(this, &ATGEconomicVictoryGameMode::OnConvoyOutcome);
    }
    
    // Unbind from territorial events
    if (TerritorialManager)
    {
        TerritorialManager->OnTerritorialControlChanged.RemoveDynamic(this, &ATGEconomicVictoryGameMode::OnTerritorialControlChangedDelegate);
    }
}

void ATGEconomicVictoryGameMode::UpdateEconomicImpactFromTerritorialChange(int32 TerritoryID, int32 OldFactionID, int32 NewFactionID)
{
    if (!EconomicVictorySubsystem)
    {
        return;
    }
    
    // Update metrics for both old and new controlling factions
    if (OldFactionID >= 0)
    {
        EconomicVictorySubsystem->UpdateEconomicMetrics(OldFactionID);
    }
    
    if (NewFactionID >= 0)
    {
        EconomicVictorySubsystem->UpdateEconomicMetrics(NewFactionID);
    }
    
    // Territorial changes can affect convoy route values
    // This would need integration with the territorial system to determine
    // which convoy routes are affected by this territorial change
}

void ATGEconomicVictoryGameMode::UpdateEconomicImpactFromConvoyChange(FName RouteID, int32 OldControllerID, int32 NewControllerID)
{
    if (!EconomicVictorySubsystem)
    {
        return;
    }
    
    // Update metrics for both old and new controlling factions
    if (OldControllerID >= 0)
    {
        EconomicVictorySubsystem->UpdateEconomicMetrics(OldControllerID);
    }
    
    if (NewControllerID >= 0)
    {
        EconomicVictorySubsystem->UpdateEconomicMetrics(NewControllerID);
    }
}

void ATGEconomicVictoryGameMode::CheckSessionTimeWarnings()
{
    if (!bSessionActive)
    {
        return;
    }
    
    float ElapsedTime = GetSessionElapsedTime();
    float TimeRemaining = SessionTimeLimit - ElapsedTime;
    
    // Send warnings at specific intervals
    if (TimeRemaining <= 300.0f && TimeRemaining > 240.0f) // 5 minutes
    {
        OnSessionTimeWarning(TimeRemaining);
    }
    else if (TimeRemaining <= 60.0f && TimeRemaining > 30.0f) // 1 minute
    {
        OnSessionTimeWarning(TimeRemaining);
    }
    else if (TimeRemaining <= 10.0f && TimeRemaining > 0.0f) // 10 seconds
    {
        OnSessionTimeWarning(TimeRemaining);
    }
    else if (TimeRemaining <= 0.0f)
    {
        // Time limit reached - end session
        EndEconomicWarfareSession();
    }
}

void ATGEconomicVictoryGameMode::BroadcastVictoryProgressMilestones()
{
    if (!EconomicVictorySubsystem)
    {
        return;
    }
    
    TArray<FEconomicVictoryProgress> AllProgress = EconomicVictorySubsystem->GetAllVictoryProgress();
    
    for (const FEconomicVictoryProgress& Progress : AllProgress)
    {
        // Check for milestone percentages
        if (Progress.Progress >= 0.25f && Progress.Progress < 0.5f)
        {
            OnVictoryProgressMilestone(Progress.FactionID, Progress.VictoryType, Progress.Progress);
        }
        else if (Progress.Progress >= 0.5f && Progress.Progress < 0.75f)
        {
            OnVictoryProgressMilestone(Progress.FactionID, Progress.VictoryType, Progress.Progress);
        }
        else if (Progress.Progress >= 0.75f && Progress.Progress < 0.9f)
        {
            OnVictoryProgressMilestone(Progress.FactionID, Progress.VictoryType, Progress.Progress);
        }
    }
}

void ATGEconomicVictoryGameMode::ProcessVictoryCondition(int32 FactionID, EEconomicVictoryType VictoryType)
{
    if (!bAllowMultipleVictoryTypes && SessionWinner != -1)
    {
        // Only one victory type allowed and someone already won
        return;
    }
    
    HandleEconomicVictory(FactionID, VictoryType);
}

void ATGEconomicVictoryGameMode::AnnounceVictory(int32 WinningFactionID, EEconomicVictoryType VictoryType)
{
    UE_LOG(LogTemp, Log, TEXT("VICTORY ANNOUNCED: Faction %d achieved %s victory!"), 
           WinningFactionID, *UEnum::GetValueAsString(VictoryType));
    
    // End the session
    EndEconomicWarfareSession();
}

void ATGEconomicVictoryGameMode::InitializeEconomicVictoryConditions()
{
    if (!EconomicVictorySubsystem)
    {
        return;
    }
    
    // The subsystem already initializes default conditions
    // This method can be used to customize conditions based on game mode settings
    
    UE_LOG(LogTemp, Log, TEXT("Economic victory conditions initialized"));
}

void ATGEconomicVictoryGameMode::ResetSessionState()
{
    SessionWinner = -1;
    WinningVictoryType = EEconomicVictoryType::None;
    SessionStartTime = 0.0f;
}

bool ATGEconomicVictoryGameMode::ValidateSessionStart() const
{
    // Check that required subsystems are available
    if (!EconomicVictorySubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Economic Victory Subsystem not available"));
        return false;
    }
    
    if (!ConvoyEconomySubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Convoy Economy Subsystem not available"));
        return false;
    }
    
    // Additional validation can be added here
    return true;
}