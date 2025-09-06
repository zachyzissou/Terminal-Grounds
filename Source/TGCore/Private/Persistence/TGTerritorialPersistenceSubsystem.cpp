#include "Persistence/TGTerritorialPersistenceSubsystem.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"
#include "Trust/TGTrustSubsystem.h"

void UTGTerritorialPersistenceSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    bInitialized = false;
    CurrentSaveGame = nullptr;
    
    // Load existing data
    LoadAllTerritoryStates();
    
    // Initialize auto-save if enabled
    if (bAutoSaveEnabled)
    {
        InitializeAutoSave();
    }
    
    bInitialized = true;
}

void UTGTerritorialPersistenceSubsystem::Deinitialize()
{
    // Save all data before shutdown
    if (bInitialized)
    {
        SaveAllTerritoryStates();
    }
    
    // Clear auto-save timer
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(AutoSaveTimer);
    }
    
    Super::Deinitialize();
}

void UTGTerritorialPersistenceSubsystem::SaveTerritoryState(const FString& TerritoryID, const FTGTerritoryState& State)
{
    FScopeLock Lock(&DataLock);
    
    CachedTerritoryStates.Add(TerritoryID, State);
    
    // Immediate sync to save game
    SyncToSaveGame();
    
    OnSiegeDataPersisted.Broadcast(TerritoryID);
}

bool UTGTerritorialPersistenceSubsystem::LoadTerritoryState(const FString& TerritoryID, FTGTerritoryState& OutState)
{
    FScopeLock Lock(&DataLock);
    
    const FTGTerritoryState* State = FindTerritoryState(TerritoryID);
    if (State)
    {
        OutState = *State;
        OnTerritoryStateLoaded.Broadcast(TerritoryID, *State);
        return true;
    }
    
    return false;
}

void UTGTerritorialPersistenceSubsystem::UpdateTerritoryPhase(const FString& TerritoryID, ESiegePhase NewPhase, float Progress)
{
    FScopeLock Lock(&DataLock);
    
    FTGTerritoryState* State = FindTerritoryStateMutable(TerritoryID);
    if (State)
    {
        State->CurrentPhase = NewPhase;
        State->PhaseProgress = Progress;
        State->LastSiegeTime = FDateTime::Now();
    }
    else
    {
        // Create new territory state
        FTGTerritoryState NewState;
        NewState.TerritoryID = TerritoryID;
        NewState.CurrentPhase = NewPhase;
        NewState.PhaseProgress = Progress;
        CachedTerritoryStates.Add(TerritoryID, NewState);
    }
}

void UTGTerritorialPersistenceSubsystem::UpdateTerritoryDominance(const FString& TerritoryID, float DominanceValue)
{
    FScopeLock Lock(&DataLock);
    
    FTGTerritoryState* State = FindTerritoryStateMutable(TerritoryID);
    if (State)
    {
        State->DominanceValue = FMath::Clamp(DominanceValue, 0.0f, 1.0f);
        State->LastSiegeTime = FDateTime::Now();
    }
}

void UTGTerritorialPersistenceSubsystem::UpdateTerritoryTickets(const FString& TerritoryID, int32 AttackerTickets, int32 DefenderTickets)
{
    FScopeLock Lock(&DataLock);
    
    FTGTerritoryState* State = FindTerritoryStateMutable(TerritoryID);
    if (State)
    {
        State->AttackerTickets = FMath::Max(0, AttackerTickets);
        State->DefenderTickets = FMath::Max(0, DefenderTickets);
        State->LastSiegeTime = FDateTime::Now();
    }
}

void UTGTerritorialPersistenceSubsystem::StartSiegePersistence(const FString& TerritoryID, const TArray<FString>& ParticipatingFactions)
{
    FScopeLock Lock(&DataLock);
    
    FTGTerritoryState* State = FindTerritoryStateMutable(TerritoryID);
    if (State)
    {
        State->bSiegeActive = true;
        State->ParticipatingFactions = ParticipatingFactions;
        State->LastSiegeTime = FDateTime::Now();
    }
    else
    {
        FTGTerritoryState NewState;
        NewState.TerritoryID = TerritoryID;
        NewState.bSiegeActive = true;
        NewState.ParticipatingFactions = ParticipatingFactions;
        CachedTerritoryStates.Add(TerritoryID, NewState);
    }
}

void UTGTerritorialPersistenceSubsystem::EndSiegePersistence(const FString& TerritoryID, bool bVictory, const FString& WinningFaction)
{
    FScopeLock Lock(&DataLock);
    
    FTGTerritoryState* State = FindTerritoryStateMutable(TerritoryID);
    if (State)
    {
        State->bSiegeActive = false;
        if (bVictory)
        {
            State->ControllingFaction = WinningFaction;
        }
        State->LastSiegeTime = FDateTime::Now();
        
        // Reset for next siege
        State->CurrentPhase = ESiegePhase::Probe;
        State->PhaseProgress = 0.0f;
        State->DominanceValue = 0.5f;
        State->AttackerTickets = 100;
        State->DefenderTickets = 100;
    }
}

void UTGTerritorialPersistenceSubsystem::RecordSiegePerformance(const FString& SiegeID, const FTGSiegePerformanceRecord& PerformanceData)
{
    FScopeLock Lock(&DataLock);
    
    CachedSiegeHistory.Add(PerformanceData);
    
    // Maintain max history size
    if (CachedSiegeHistory.Num() > MaxSiegeHistoryRecords)
    {
        CompressSiegeHistory();
    }
    
    SyncToSaveGame();
}

TArray<FString> UTGTerritorialPersistenceSubsystem::GetAllTerritoryIDs()
{
    FScopeLock Lock(&DataLock);
    
    TArray<FString> TerritoryIDs;
    CachedTerritoryStates.GetKeys(TerritoryIDs);
    return TerritoryIDs;
}

TArray<FTGTerritoryState> UTGTerritorialPersistenceSubsystem::GetTerritoriesControlledBy(const FString& Faction)
{
    FScopeLock Lock(&DataLock);
    
    TArray<FTGTerritoryState> ControlledTerritories;
    
    for (const auto& Pair : CachedTerritoryStates)
    {
        if (Pair.Value.ControllingFaction == Faction)
        {
            ControlledTerritories.Add(Pair.Value);
        }
    }
    
    return ControlledTerritories;
}

bool UTGTerritorialPersistenceSubsystem::IsTerritoryUnderSiege(const FString& TerritoryID)
{
    FScopeLock Lock(&DataLock);
    
    const FTGTerritoryState* State = FindTerritoryState(TerritoryID);
    return State && State->bSiegeActive;
}

float UTGTerritorialPersistenceSubsystem::GetTerritoryControlPercentage(const FString& Faction)
{
    FScopeLock Lock(&DataLock);
    
    int32 TotalTerritories = CachedTerritoryStates.Num();
    if (TotalTerritories == 0)
    {
        return 0.0f;
    }
    
    int32 ControlledTerritories = 0;
    for (const auto& Pair : CachedTerritoryStates)
    {
        if (Pair.Value.ControllingFaction == Faction)
        {
            ControlledTerritories++;
        }
    }
    
    return (float)ControlledTerritories / (float)TotalTerritories * 100.0f;
}

void UTGTerritorialPersistenceSubsystem::UpdatePlayerSiegeStats(bool bVictory, float PerformanceRating)
{
    UTGProfileSave* SaveGame = GetOrCreateSaveGame();
    if (SaveGame)
    {
        SaveGame->SiegeParticipations++;
        if (bVictory)
        {
            SaveGame->SiegeVictories++;
        }
        
        // Update rating using ELO-like system
        float K = 32.0f; // K-factor
        float Expected = 0.5f; // Expected result (0.5 for balanced)
        float Actual = bVictory ? 1.0f : 0.0f;
        SaveGame->PlayerSiegeRating = SaveGame->PlayerSiegeRating + K * (Actual - Expected);
        SaveGame->PlayerSiegeRating = FMath::Clamp(SaveGame->PlayerSiegeRating, 100.0f, 3000.0f);
        
        SaveGame->LastSiegeTime = FDateTime::Now();
        
        UGameplayStatics::SaveGameToSlot(SaveGame, SaveSlotName, 0);
    }
}

float UTGTerritorialPersistenceSubsystem::GetPlayerSiegeRating()
{
    const UTGProfileSave* SaveGame = GetOrCreateSaveGame();
    return SaveGame ? SaveGame->PlayerSiegeRating : 1000.0f;
}

int32 UTGTerritorialPersistenceSubsystem::GetPlayerSiegeVictories()
{
    const UTGProfileSave* SaveGame = GetOrCreateSaveGame();
    return SaveGame ? SaveGame->SiegeVictories : 0;
}

TArray<FTGSiegePerformanceRecord> UTGTerritorialPersistenceSubsystem::GetRecentSiegeHistory(int32 Count)
{
    FScopeLock Lock(&DataLock);
    
    TArray<FTGSiegePerformanceRecord> RecentHistory = CachedSiegeHistory;
    
    // Sort by end time (most recent first)
    RecentHistory.Sort([](const FTGSiegePerformanceRecord& A, const FTGSiegePerformanceRecord& B) {
        return A.EndTime > B.EndTime;
    });
    
    if (Count > 0 && RecentHistory.Num() > Count)
    {
        RecentHistory.SetNum(Count);
    }
    
    return RecentHistory;
}

float UTGTerritorialPersistenceSubsystem::GetAverageSiegeFPS()
{
    FScopeLock Lock(&DataLock);
    
    if (CachedSiegeHistory.Num() == 0)
    {
        return 60.0f; // Default target
    }
    
    float TotalFPS = 0.0f;
    for (const FTGSiegePerformanceRecord& Record : CachedSiegeHistory)
    {
        TotalFPS += Record.AverageFPS;
    }
    
    return TotalFPS / (float)CachedSiegeHistory.Num();
}

float UTGTerritorialPersistenceSubsystem::GetAverageSiegeLatency()
{
    FScopeLock Lock(&DataLock);
    
    if (CachedSiegeHistory.Num() == 0)
    {
        return 0.0f;
    }
    
    float TotalLatency = 0.0f;
    for (const FTGSiegePerformanceRecord& Record : CachedSiegeHistory)
    {
        TotalLatency += Record.PeakLatency;
    }
    
    return TotalLatency / (float)CachedSiegeHistory.Num();
}

void UTGTerritorialPersistenceSubsystem::SaveAllTerritoryStates()
{
    FScopeLock Lock(&DataLock);
    
    UTGProfileSave* SaveGame = GetOrCreateSaveGame();
    if (SaveGame)
    {
        SyncToSaveGame();
        UGameplayStatics::SaveGameToSlot(SaveGame, SaveSlotName, 0);
    }
}

void UTGTerritorialPersistenceSubsystem::LoadAllTerritoryStates()
{
    CurrentSaveGame = Cast<UTGProfileSave>(UGameplayStatics::LoadGameFromSlot(SaveSlotName, 0));
    if (!CurrentSaveGame)
    {
        CurrentSaveGame = Cast<UTGProfileSave>(UGameplayStatics::CreateSaveGameObject(UTGProfileSave::StaticClass()));
    }
    
    if (CurrentSaveGame)
    {
        SyncWithSaveGame();
    }
}

void UTGTerritorialPersistenceSubsystem::CleanupOldSiegeData(int32 DaysToKeep)
{
    FScopeLock Lock(&DataLock);
    
    FDateTime CutoffTime = FDateTime::Now() - FTimespan::FromDays(DaysToKeep);
    
    CachedSiegeHistory.RemoveAll([CutoffTime](const FTGSiegePerformanceRecord& Record) {
        return Record.EndTime < CutoffTime;
    });
    
    SyncToSaveGame();
}

// Protected methods

void UTGTerritorialPersistenceSubsystem::InitializeAutoSave()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(AutoSaveTimer, 
            FTimerDelegate::CreateUObject(this, &UTGTerritorialPersistenceSubsystem::PerformAutoSave),
            AutoSaveInterval, true);
    }
}

void UTGTerritorialPersistenceSubsystem::PerformAutoSave()
{
    SaveAllTerritoryStates();
}

UTGProfileSave* UTGTerritorialPersistenceSubsystem::GetOrCreateSaveGame()
{
    if (!CurrentSaveGame)
    {
        LoadAllTerritoryStates();
    }
    return CurrentSaveGame;
}

void UTGTerritorialPersistenceSubsystem::SyncWithSaveGame()
{
    if (!CurrentSaveGame)
    {
        return;
    }
    
    FScopeLock Lock(&DataLock);
    
    // Load territory states
    CachedTerritoryStates.Empty();
    for (const FTGTerritoryState& State : CurrentSaveGame->TerritoryStates)
    {
        CachedTerritoryStates.Add(State.TerritoryID, State);
    }
    
    // Load siege history
    CachedSiegeHistory = CurrentSaveGame->SiegeHistory;
}

void UTGTerritorialPersistenceSubsystem::SyncToSaveGame()
{
    if (!CurrentSaveGame)
    {
        return;
    }
    
    // Save territory states
    CurrentSaveGame->TerritoryStates.Empty();
    for (const auto& Pair : CachedTerritoryStates)
    {
        CurrentSaveGame->TerritoryStates.Add(Pair.Value);
    }
    
    // Save siege history
    CurrentSaveGame->SiegeHistory = CachedSiegeHistory;
}

FTGTerritoryState* UTGTerritorialPersistenceSubsystem::FindTerritoryStateMutable(const FString& TerritoryID)
{
    return CachedTerritoryStates.Find(TerritoryID);
}

const FTGTerritoryState* UTGTerritorialPersistenceSubsystem::FindTerritoryState(const FString& TerritoryID) const
{
    return CachedTerritoryStates.Find(TerritoryID);
}

void UTGTerritorialPersistenceSubsystem::OptimizeCacheSize()
{
    FScopeLock Lock(&DataLock);
    
    // Remove territories that haven't been accessed in 30 days
    FDateTime CutoffTime = FDateTime::Now() - FTimespan::FromDays(30);
    
    TArray<FString> ToRemove;
    for (const auto& Pair : CachedTerritoryStates)
    {
        if (Pair.Value.LastSiegeTime < CutoffTime && !Pair.Value.bSiegeActive)
        {
            ToRemove.Add(Pair.Key);
        }
    }
    
    for (const FString& TerritoryID : ToRemove)
    {
        CachedTerritoryStates.Remove(TerritoryID);
    }
}

void UTGTerritorialPersistenceSubsystem::CompressSiegeHistory()
{
    // Keep only the most recent records
    int32 TargetSize = MaxSiegeHistoryRecords * 0.8f; // Keep 80% after compression
    
    if (CachedSiegeHistory.Num() > TargetSize)
    {
        // Sort by end time (most recent first)
        CachedSiegeHistory.Sort([](const FTGSiegePerformanceRecord& A, const FTGSiegePerformanceRecord& B) {
            return A.EndTime > B.EndTime;
        });
        
        CachedSiegeHistory.SetNum(TargetSize);
    }
}