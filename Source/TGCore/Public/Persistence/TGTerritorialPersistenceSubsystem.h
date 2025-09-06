#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/Engine.h"
#include "TGProfileSave.h"
#include "../TGTerritorial/Public/PhaseGateComponent.h"
#include "TGTerritorialPersistenceSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerritoryStateLoaded, const FString&, TerritoryID, const FTGTerritoryState&, State);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSiegeDataPersisted, const FString&, TerritoryID);

/**
 * Territorial Persistence Subsystem
 * Handles saving and loading of territory states, siege progress, and performance metrics
 * Integrates with the Profile Save system for comprehensive data persistence
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGTerritorialPersistenceSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Territory state management
    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void SaveTerritoryState(const FString& TerritoryID, const FTGTerritoryState& State);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    bool LoadTerritoryState(const FString& TerritoryID, FTGTerritoryState& OutState);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void UpdateTerritoryPhase(const FString& TerritoryID, ESiegePhase NewPhase, float Progress);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void UpdateTerritoryDominance(const FString& TerritoryID, float DominanceValue);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void UpdateTerritoryTickets(const FString& TerritoryID, int32 AttackerTickets, int32 DefenderTickets);

    // Siege management
    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void StartSiegePersistence(const FString& TerritoryID, const TArray<FString>& ParticipatingFactions);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void EndSiegePersistence(const FString& TerritoryID, bool bVictory, const FString& WinningFaction);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void RecordSiegePerformance(const FString& SiegeID, const FTGSiegePerformanceRecord& PerformanceData);

    // Territory queries
    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    TArray<FString> GetAllTerritoryIDs();

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    TArray<FTGTerritoryState> GetTerritoriesControlledBy(const FString& Faction);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    bool IsTerritoryUnderSiege(const FString& TerritoryID);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    float GetTerritoryControlPercentage(const FString& Faction);

    // Player siege statistics
    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void UpdatePlayerSiegeStats(bool bVictory, float PerformanceRating);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    float GetPlayerSiegeRating();

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    int32 GetPlayerSiegeVictories();

    // Performance analytics
    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    TArray<FTGSiegePerformanceRecord> GetRecentSiegeHistory(int32 Count = 10);

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    float GetAverageSiegeFPS();

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    float GetAverageSiegeLatency();

    // Batch operations for performance
    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void SaveAllTerritoryStates();

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void LoadAllTerritoryStates();

    UFUNCTION(BlueprintCallable, Category = "Territorial Persistence")
    void CleanupOldSiegeData(int32 DaysToKeep = 30);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnTerritoryStateLoaded OnTerritoryStateLoaded;

    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnSiegeDataPersisted OnSiegeDataPersisted;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Persistence Config")
    bool bAutoSaveEnabled = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Persistence Config")
    float AutoSaveInterval = 300.0f; // 5 minutes

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Persistence Config")
    int32 MaxSiegeHistoryRecords = 1000;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Persistence Config")
    FString SaveSlotName = TEXT("TerritorialData");

protected:
    // Internal state
    UPROPERTY()
    TMap<FString, FTGTerritoryState> CachedTerritoryStates;

    UPROPERTY()
    TArray<FTGSiegePerformanceRecord> CachedSiegeHistory;

    // Save game integration
    UPROPERTY()
    UTGProfileSave* CurrentSaveGame;

    // Auto-save system
    FTimerHandle AutoSaveTimer;
    
    // Internal methods
    void InitializeAutoSave();
    void PerformAutoSave();
    UTGProfileSave* GetOrCreateSaveGame();
    void SyncWithSaveGame();
    void SyncToSaveGame();
    
    // Territory state helpers
    FTGTerritoryState* FindTerritoryStateMutable(const FString& TerritoryID);
    const FTGTerritoryState* FindTerritoryState(const FString& TerritoryID) const;
    
    // Performance optimization
    void OptimizeCacheSize();
    void CompressSiegeHistory();

private:
    bool bInitialized;
    mutable FCriticalSection DataLock; // Thread safety for concurrent access
};