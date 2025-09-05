#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/DataTable.h"
#include "GameplayTagContainer.h"
#include "TGMissionDirector2.generated.h"

UENUM(BlueprintType)
enum class EMissionStage : uint8
{
    Briefing        UMETA(DisplayName = "Briefing"),
    Deployment      UMETA(DisplayName = "Deployment"),
    Primary         UMETA(DisplayName = "Primary Objective"),
    Secondary       UMETA(DisplayName = "Secondary Objective"),
    Dynamic         UMETA(DisplayName = "Dynamic Event"),
    Extraction      UMETA(DisplayName = "Extraction"),
    Completed       UMETA(DisplayName = "Completed"),
    Failed          UMETA(DisplayName = "Failed")
};

UENUM(BlueprintType)
enum class EThreatLevel : uint8
{
    Low         UMETA(DisplayName = "Low Threat"),
    Moderate    UMETA(DisplayName = "Moderate Threat"),
    High        UMETA(DisplayName = "High Threat"),
    Extreme     UMETA(DisplayName = "Extreme Threat"),
    Critical    UMETA(DisplayName = "Critical Threat")
};

USTRUCT(BlueprintType)
struct FMissionStageData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    EMissionStage StageType;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    FText StageName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    FText StageDescription;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    TArray<FText> Objectives;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    float TimeLimit = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    FGameplayTagContainer RequiredConditions;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stage")
    FGameplayTagContainer CompletionTags;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
    int32 BaseReward = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
    float RewardMultiplier = 1.0f;
};

USTRUCT(BlueprintType)
struct FDynamicEvent
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FString EventName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FText EventDescription;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    float TriggerProbability = 0.3f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    FGameplayTagContainer TriggerConditions;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    EThreatLevel ThreatIncrease = EThreatLevel::Low;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Event")
    TArray<FMissionStageData> AdditionalStages;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMissionStageChanged, EMissionStage, NewStage);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnDynamicEventTriggered, const FDynamicEvent&, Event, float, IntensityModifier);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnThreatLevelChanged, EThreatLevel, OldLevel, EThreatLevel, NewLevel);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMissionCompleted);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMissionFailed);

/**
 * Advanced mission director managing multi-stage missions with dynamic events
 */
UCLASS()
class TGMISSIONS_API ATGMissionDirector2 : public AActor
{
    GENERATED_BODY()

public:
    ATGMissionDirector2();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

public:
    // Mission Management
    UFUNCTION(BlueprintCallable, Category = "Mission")
    void StartMission(const TArray<FMissionStageData>& MissionStages);

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void AdvanceToNextStage();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void CompleteMission();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void FailMission();

    UFUNCTION(BlueprintCallable, Category = "Mission")
    void AbortMission();

    // Stage Management
    UFUNCTION(BlueprintPure, Category = "Mission")
    EMissionStage GetCurrentStage() const { return CurrentStage; }

    UFUNCTION(BlueprintPure, Category = "Mission")
    FMissionStageData GetCurrentStageData() const;

    UFUNCTION(BlueprintPure, Category = "Mission")
    float GetStageProgress() const;

    UFUNCTION(BlueprintPure, Category = "Mission")
    float GetStageTimeRemaining() const;

    // Dynamic Events
    UFUNCTION(BlueprintCallable, Category = "Events")
    void RegisterDynamicEvent(const FDynamicEvent& Event);

    UFUNCTION(BlueprintCallable, Category = "Events")
    void TriggerDynamicEvent(const FString& EventName, float IntensityModifier = 1.0f);

    UFUNCTION(BlueprintCallable, Category = "Events")
    void CheckEventTriggers();

    // Threat Scaling
    UFUNCTION(BlueprintCallable, Category = "Threat")
    void SetThreatLevel(EThreatLevel NewThreatLevel);

    UFUNCTION(BlueprintPure, Category = "Threat")
    EThreatLevel GetCurrentThreatLevel() const { return CurrentThreatLevel; }

    UFUNCTION(BlueprintCallable, Category = "Threat")
    void IncreaseThreatLevel(int32 LevelsToIncrease = 1);

    UFUNCTION(BlueprintPure, Category = "Threat")
    float GetThreatScaling() const;

    // Objectives
    UFUNCTION(BlueprintCallable, Category = "Objectives")
    void CompleteObjective(const FString& ObjectiveId);

    UFUNCTION(BlueprintCallable, Category = "Objectives")
    void AddObjective(const FText& ObjectiveText, const FString& ObjectiveId);

    UFUNCTION(BlueprintPure, Category = "Objectives")
    TArray<FText> GetActiveObjectives() const;

    // Conditions
    UFUNCTION(BlueprintCallable, Category = "Conditions")
    void AddConditionTag(const FGameplayTag& Tag);

    UFUNCTION(BlueprintCallable, Category = "Conditions")
    void RemoveConditionTag(const FGameplayTag& Tag);

    UFUNCTION(BlueprintPure, Category = "Conditions")
    bool CheckConditions(const FGameplayTagContainer& RequiredTags) const;

    // Siege Integration
    UFUNCTION(BlueprintCallable, Category = "Siege")
    void StartSiege(const struct FSiegePlan& Plan);

    UFUNCTION(BlueprintCallable, Category = "Siege")
    EMissionStage MapExtractionToSiege(EMissionStage OriginalStage) const;

    UFUNCTION(BlueprintCallable, Category = "Siege")
    void ProcessSiegeStageCompletion(EMissionStage CompletedStage);

    UFUNCTION(BlueprintPure, Category = "Siege")
    bool IsSiegeMode() const { return bSiegeMode; }

    UFUNCTION(BlueprintCallable, Category = "Siege")
    void SetSiegeMode(bool bEnabled) { bSiegeMode = bEnabled; }

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnMissionStageChanged OnMissionStageChanged;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnDynamicEventTriggered OnDynamicEventTriggered;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnThreatLevelChanged OnThreatLevelChanged;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnMissionCompleted OnMissionCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnMissionFailed OnMissionFailed;

protected:
    // Mission State
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    TArray<FMissionStageData> MissionStages;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    int32 CurrentStageIndex;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    EMissionStage CurrentStage;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    EThreatLevel CurrentThreatLevel;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    float StageStartTime;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    bool bMissionActive;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    bool bSiegeMode;

    // Dynamic Events
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Events")
    TArray<FDynamicEvent> RegisteredEvents;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Events")
    TArray<FString> TriggeredEventNames;

    // Conditions and Objectives
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Progress")
    FGameplayTagContainer ActiveConditions;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Progress")
    TMap<FString, FText> ActiveObjectives;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Progress")
    TArray<FString> CompletedObjectives;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float EventCheckInterval = 30.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float BaseThreatScaling = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Configuration")
    float ThreatScalingIncrement = 0.25f;

private:
    void UpdateStageProgress();
    void ProcessStageTimeLimit(float DeltaTime);
    bool EvaluateEventTrigger(const FDynamicEvent& Event) const;
    void ApplyThreatScaling();

    FTimerHandle EventCheckTimer;
};