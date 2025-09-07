#pragma once

#include "CoreMinimal.h"
#include "TGGameMode.h"
#include "Engine/TimerHandle.h"
#include "TGPlaytestGameMode.generated.h"

class ATGDemoSetup;
class ATGEnemyGrunt;
class ATGPlayPawn;

UENUM(BlueprintType)
enum class EPlaytestMissionState : uint8
{
    Setup       UMETA(DisplayName = "Setup"),
    InProgress  UMETA(DisplayName = "In Progress"),
    WaitingForExtraction UMETA(DisplayName = "Waiting For Extraction"),
    Success     UMETA(DisplayName = "Success"),
    Failed      UMETA(DisplayName = "Failed")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMissionStateChanged, EPlaytestMissionState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnEnemyCountChanged, int32, RemainingEnemies, int32, TotalEnemies);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMissionComplete);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMissionFailed);

UCLASS(BlueprintType)
class TGCORE_API ATGPlaytestGameMode : public ATGGameMode
{
    GENERATED_BODY()

public:
    ATGPlaytestGameMode();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // Mission Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mission")
    bool bAutoSetupOnBeginPlay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mission")
    float MissionSetupDelay = 2.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mission")
    bool bShowMissionUpdates = true;

    // Mission State
    UPROPERTY(BlueprintReadOnly, Category = "Mission")
    EPlaytestMissionState CurrentMissionState = EPlaytestMissionState::Setup;

    UPROPERTY(BlueprintReadOnly, Category = "Mission")
    int32 RemainingEnemies = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Mission")
    int32 TotalEnemies = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Mission")
    bool bAllEnemiesCleared = false;

    UPROPERTY(BlueprintReadOnly, Category = "Mission")
    bool bPlayerInExtractionZone = false;

    // References
    UPROPERTY(BlueprintReadOnly, Category = "Mission")
    TObjectPtr<ATGDemoSetup> DemoSetup;

    UPROPERTY()
    TArray<TWeakObjectPtr<ATGEnemyGrunt>> TrackedEnemies;

    // Timers
    FTimerHandle MissionSetupTimerHandle;
    FTimerHandle MissionCheckTimerHandle;

public:
    // Mission Control Interface
    UFUNCTION(BlueprintCallable, Category = "Mission")
    void StartMission();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void CompleteMission();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void FailMission();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void RestartMission();

    // Enemy Tracking
    UFUNCTION(BlueprintCallable, Category = "Mission")
    void RegisterEnemy(ATGEnemyGrunt* Enemy);

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void UnregisterEnemy(ATGEnemyGrunt* Enemy);

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void OnEnemyDied(ATGEnemyGrunt* Enemy);

    // Extraction Zone
    UFUNCTION(BlueprintCallable, Category = "Mission")
    void PlayerEnteredExtractionZone();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void PlayerExitedExtractionZone();

    // Player Events
    UFUNCTION(BlueprintCallable, Category = "Mission")
    void OnPlayerDied();

    // State Queries
    UFUNCTION(BlueprintPure, Category = "Mission")
    EPlaytestMissionState GetMissionState() const { return CurrentMissionState; }

    UFUNCTION(BlueprintPure, Category = "Mission")
    int32 GetRemainingEnemies() const { return RemainingEnemies; }

    UFUNCTION(BlueprintPure, Category = "Mission")
    int32 GetTotalEnemies() const { return TotalEnemies; }

    UFUNCTION(BlueprintPure, Category = "Mission")
    bool CanExtract() const { return bAllEnemiesCleared; }

    // Mission Setup
    UFUNCTION(BlueprintCallable, Category = "Mission")
    void InitializeMission();

    UFUNCTION(BlueprintImplementableEvent, Category = "Mission")
    void OnMissionInitialized();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Mission Events")
    FOnMissionStateChanged OnMissionStateChanged;

    UPROPERTY(BlueprintAssignable, Category = "Mission Events")
    FOnEnemyCountChanged OnEnemyCountChanged;

    UPROPERTY(BlueprintAssignable, Category = "Mission Events")
    FOnMissionComplete OnMissionComplete;

    UPROPERTY(BlueprintAssignable, Category = "Mission Events")
    FOnMissionFailed OnMissionFailed;

protected:
    // Internal Functions
    void SetMissionState(EPlaytestMissionState NewState);
    void UpdateEnemyCount();
    void CheckMissionStatus();
    void FindDemoSetup();
    void SetupEnemyTracking();

    UFUNCTION()
    void MissionSetupTimer();

    UFUNCTION()
    void MissionStatusCheck();
};