// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Engine/Engine.h"
#include "TerritorialTypes.h"
#include "TerritorialManager.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnTerritorialControlChanged, int32, TerritoryID, ETerritoryType, TerritoryType, int32, OldFaction, int32, NewFaction);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritoryContested, int32, TerritoryID, ETerritoryType, TerritoryType, const TArray<int32>&, ContestingFactions);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FiveParams(FOnPlayerTerritorialAction, int32, PlayerID, int32, FactionID, const FString&, ActionType, int32, InfluenceGained, int32, TerritoryID);

/**
 * Core territorial management system for Terminal Grounds
 * Handles faction influence, territorial control, and real-time synchronization
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API UTerritorialManager : public UObject
{
    GENERATED_BODY()

public:
    UTerritorialManager();

    // Core territorial operations
    UFUNCTION(BlueprintCallable, Category = "Territorial")
    bool UpdateTerritorialInfluence(int32 TerritoryID, ETerritoryType TerritoryType, int32 FactionID, int32 InfluenceChange, const FString& Cause);

    UFUNCTION(BlueprintCallable, Category = "Territorial")
    FTerritorialState GetTerritorialState(int32 TerritoryID, ETerritoryType TerritoryType);

    UFUNCTION(BlueprintCallable, Category = "Territorial")
    TArray<FTerritorialUpdate> GetRecentTerritorialUpdates();

    // Faction influence queries
    UFUNCTION(BlueprintPure, Category = "Territorial")
    int32 GetFactionInfluence(int32 TerritoryID, ETerritoryType TerritoryType, int32 FactionID);

    UFUNCTION(BlueprintPure, Category = "Territorial")
    int32 GetDominantFaction(int32 TerritoryID, ETerritoryType TerritoryType);

    UFUNCTION(BlueprintPure, Category = "Territorial")
    bool IsTerritoryContested(int32 TerritoryID, ETerritoryType TerritoryType);

    // Territorial hierarchy queries
    UFUNCTION(BlueprintPure, Category = "Territorial")
    TArray<int32> GetDistrictsInRegion(int32 RegionID);

    UFUNCTION(BlueprintPure, Category = "Territorial")
    TArray<int32> GetControlPointsInDistrict(int32 DistrictID);

    UFUNCTION(BlueprintPure, Category = "Territorial")
    FTerritorialInfo GetTerritoryInfo(int32 TerritoryID, ETerritoryType TerritoryType);

    // System control
    UFUNCTION(BlueprintCallable, Category = "Territorial")
    void InitializeTerritorialSystem();

    UFUNCTION(BlueprintCallable, Category = "Territorial")
    void ShutdownTerritorialSystem();

    UFUNCTION(BlueprintCallable, Category = "Territorial")
    bool IsSystemOnline();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnTerritorialControlChanged OnTerritorialControlChanged;

    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnTerritoryContested OnTerritoryContested;

    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnPlayerTerritorialAction OnPlayerTerritorialAction;

protected:
    // WebSocket connection for real-time updates (forward declared)
    // UPROPERTY()
    // class UWebSocketComponent* WebSocketConnection;

    // Cached territorial state for performance
    UPROPERTY()
    TMap<FString, FTerritorialState> CachedTerritorialStates;

    // Database connection (will be implemented via plugin)
    // UPROPERTY()
    // class UTerritorialDatabase* DatabaseConnection;

    // System state
    UPROPERTY()
    bool bSystemInitialized;

    UPROPERTY()
    bool bWebSocketConnected;

private:
    // Internal update processing
    void ProcessTerritorialUpdate(const FString& UpdateMessage);
    void ProcessAIDecision(const FString& DecisionMessage);
    void UpdateCachedState(const FTerritorialState& NewState);

    // WebSocket event handlers
    UFUNCTION()
    void OnWebSocketConnected();

    UFUNCTION()
    void OnWebSocketDisconnected();

    UFUNCTION()
    void OnWebSocketMessage(const FString& Message);

    // Database operations
    bool SaveTerritorialState(const FTerritorialState& State);
    bool LoadTerritorialState(int32 TerritoryID, ETerritoryType TerritoryType, FTerritorialState& OutState);
    bool RecordInfluenceChange(int32 TerritoryID, ETerritoryType TerritoryType, int32 FactionID, int32 Change, const FString& Cause);

    // Influence calculation helpers
    int32 CalculateNewInfluence(int32 CurrentInfluence, int32 Change, float FactionModifier);
    bool DetermineIfContested(const TMap<int32, int32>& FactionInfluences);
    int32 FindDominantFaction(const TMap<int32, int32>& FactionInfluences);

    // Performance optimization
    FDateTime LastCacheUpdate;
    static constexpr float CACHE_UPDATE_INTERVAL = 1.0f; // 1 second cache interval
};

/**
 * Singleton access to territorial manager
 */
UCLASS(BlueprintType)
class TGTERRITORIAL_API UTerritorialSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintPure, Category = "Territorial")
    static UTerritorialManager* GetTerritorialManager(const UObject* WorldContext);

protected:
    UPROPERTY()
    UTerritorialManager* TerritorialManager;
};