#pragma once

#include "CoreMinimal.h"
#include "TGGameMode.h"
#include "TGEconomicVictorySubsystem.h"
#include "TGWorld/Public/Economy/TGConvoyEconomySubsystem.h"
#include "TGTerritorial/Public/TerritorialManager.h"
#include "TGEconomicVictoryGameMode.generated.h"

UCLASS(BlueprintType, Blueprintable)
class TGCORE_API ATGEconomicVictoryGameMode : public ATGGameMode
{
    GENERATED_BODY()

public:
    ATGEconomicVictoryGameMode();

    // Game Mode overrides
    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
    virtual void StartPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // Economic Victory Game Mode specific functions
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void StartEconomicWarfareSession();

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void EndEconomicWarfareSession();

    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void HandleEconomicVictory(int32 WinningFactionID, EEconomicVictoryType VictoryType);

    // Integration with extraction objectives
    UFUNCTION(BlueprintCallable, Category = "Economic Victory Integration")
    void OnExtractionObjectiveCompleted(int32 TerritoryID, int32 FactionID, float EconomicImpact);

    // Integration with convoy system
    UFUNCTION(BlueprintCallable, Category = "Economic Victory Integration")
    void OnConvoyRouteControlChanged(FName RouteID, int32 OldControllerID, int32 NewControllerID);

    // Integration with territorial system
    UFUNCTION(BlueprintCallable, Category = "Economic Victory Integration")
    void OnTerritorialControlChanged(int32 TerritoryID, int32 OldFactionID, int32 NewFactionID);

    // Game session management
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    bool IsEconomicVictoryActive() const;

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    float GetSessionElapsedTime() const;

    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FEconomicVictoryProgress GetSessionLeader() const;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Victory Config")
    bool bEnableEconomicVictory = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Victory Config")
    float SessionTimeLimit = 1800.0f; // 30 minutes default

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Victory Config")
    int32 MaxPlayersPerFaction = 8;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Victory Config")
    bool bAllowMultipleVictoryTypes = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Victory Config")
    float VictoryAnnouncementDelay = 5.0f;

    // Events for Blueprint integration
    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnEconomicVictorySessionStarted();

    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnEconomicVictorySessionEnded(int32 WinningFactionID, EEconomicVictoryType VictoryType);

    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnSessionTimeWarning(float TimeRemaining);

    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnVictoryProgressMilestone(int32 FactionID, EEconomicVictoryType VictoryType, float Progress);

protected:
    virtual void BeginPlay() override;

    // Bind to subsystem events
    UFUNCTION()
    void OnEconomicVictoryAchieved(int32 FactionID, EEconomicVictoryType VictoryType, float CompletionTime);

    UFUNCTION()
    void OnEconomicVictoryThreatened(int32 ThreateningFactionID, EEconomicVictoryType VictoryType, float TimeToVictory);

    UFUNCTION()
    void OnConvoyOutcome(FName RouteId, EJobType JobType, bool bSuccess);

    UFUNCTION()
    void OnTerritorialControlChangedDelegate(int32 TerritoryID, ETerritoryType TerritoryType, int32 OldFaction, int32 NewFaction);

private:
    // Subsystem references
    UPROPERTY()
    UTGEconomicVictorySubsystem* EconomicVictorySubsystem;

    UPROPERTY()
    UTGConvoyEconomySubsystem* ConvoyEconomySubsystem;

    UPROPERTY()
    UTerritorialManager* TerritorialManager;

    // Session state
    UPROPERTY()
    bool bSessionActive = false;

    UPROPERTY()
    float SessionStartTime = 0.0f;

    UPROPERTY()
    int32 SessionWinner = -1;

    UPROPERTY()
    EEconomicVictoryType WinningVictoryType = EEconomicVictoryType::None;

    // Timer handles
    FTimerHandle SessionTimeWarningTimer;
    FTimerHandle VictoryAnnouncementTimer;

    // Integration helpers
    void SetupSubsystemIntegration();
    void CleanupSubsystemIntegration();
    void UpdateEconomicImpactFromTerritorialChange(int32 TerritoryID, int32 OldFactionID, int32 NewFactionID);
    void UpdateEconomicImpactFromConvoyChange(FName RouteID, int32 OldControllerID, int32 NewControllerID);
    void CheckSessionTimeWarnings();
    void BroadcastVictoryProgressMilestones();

    // Victory handling
    void ProcessVictoryCondition(int32 FactionID, EEconomicVictoryType VictoryType);
    void AnnounceVictory(int32 WinningFactionID, EEconomicVictoryType VictoryType);

    // Session management helpers
    void InitializeEconomicVictoryConditions();
    void ResetSessionState();
    bool ValidateSessionStart() const;
};