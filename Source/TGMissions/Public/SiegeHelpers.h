#pragma once

#include "CoreMinimal.h"
#include "TGMissionDirector2.h"
#include "../TGTerritorial/Public/PhaseGateComponent.h"
#include "SiegeHelpers.generated.h"

USTRUCT(BlueprintType)
struct FSiegePlan
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege Plan")
    TArray<FMissionStageData> ProbeStages;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege Plan")
    TArray<FMissionStageData> InterdictStages;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege Plan")
    TArray<FMissionStageData> DominateStages;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege Plan")
    float DominanceRewardPerStage = 0.1f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege Plan")
    int32 TicketCostPerFailure = 5;

    FSiegePlan()
    {
        DominanceRewardPerStage = 0.1f;
        TicketCostPerFailure = 5;
    }
};

USTRUCT(BlueprintType)
struct FSiegeDynamicEventOutcome
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Outcome")
    float DominanceDelta = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Outcome")
    int32 AttackerTicketDelta = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Outcome")
    int32 DefenderTicketDelta = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Outcome")
    bool bShouldAdvancePhase = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Outcome")
    ESiegePhase ForcePhase = ESiegePhase::Probe;

    FSiegeDynamicEventOutcome()
    {
        DominanceDelta = 0.0f;
        AttackerTicketDelta = 0;
        DefenderTicketDelta = 0;
        bShouldAdvancePhase = false;
        ForcePhase = ESiegePhase::Probe;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnSiegePhaseAdvanced, ESiegePhase, OldPhase, ESiegePhase, NewPhase);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSiegeEventOutcome, const FSiegeDynamicEventOutcome&, Outcome);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnSiegeCompleted);

/**
 * Siege Helper Component
 * Extends MissionDirector2 with siege-specific functionality
 * Handles phase transitions, dominance effects, and siege victory conditions
 */
UCLASS(BlueprintType, Blueprintable, meta=(BlueprintSpawnableComponent))
class TGMISSIONS_API USiegeHelperComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    USiegeHelperComponent();

    // Siege Events
    UPROPERTY(BlueprintAssignable, Category = "Siege Events")
    FOnSiegePhaseAdvanced OnSiegePhaseAdvanced;

    UPROPERTY(BlueprintAssignable, Category = "Siege Events")
    FOnSiegeEventOutcome OnSiegeEventOutcome;

    UPROPERTY(BlueprintAssignable, Category = "Siege Events")
    FOnSiegeCompleted OnSiegeCompleted;

    // Siege Management
    UFUNCTION(BlueprintCallable, Category = "Siege")
    void StartSiege(const FSiegePlan& Plan);

    UFUNCTION(BlueprintCallable, Category = "Siege")
    void EndSiege(bool bVictory);

    UFUNCTION(BlueprintCallable, Category = "Siege")
    void ProcessSiegeStageCompletion(EMissionStage CompletedStage);

    UFUNCTION(BlueprintCallable, Category = "Siege")
    void ApplySiegeDynamicEventOutcome(const FSiegeDynamicEventOutcome& Outcome);

    // Phase Integration
    UFUNCTION(BlueprintCallable, Category = "Siege|Phase")
    void BindToPhaseGate(UPhaseGateComponent* PhaseGate);

    UFUNCTION(BlueprintCallable, Category = "Siege|Phase")
    void AdvanceToNextSiegePhase();

    UFUNCTION(BlueprintPure, Category = "Siege|Phase")
    ESiegePhase GetCurrentSiegePhase() const;

    // Dominance Integration
    UFUNCTION(BlueprintCallable, Category = "Siege|Dominance")
    void BindToDominanceMeter(class UDominanceMeterComponent* DominanceMeter);

    UFUNCTION(BlueprintCallable, Category = "Siege|Dominance")
    void ApplyDominanceReward(float Amount);

    // Ticket Integration
    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets")
    void BindToTicketPool(class UTicketPoolComponent* TicketPool);

    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets")
    void ApplyTicketPenalty(bool bIsAttacker, int32 Amount);

    // Mission Director Integration
    UFUNCTION(BlueprintCallable, Category = "Siege|Mission")
    void BindToMissionDirector(ATGMissionDirector2* MissionDirector);

    // Siege State Queries
    UFUNCTION(BlueprintPure, Category = "Siege|State")
    bool IsSiegeActive() const { return bSiegeActive; }

    UFUNCTION(BlueprintPure, Category = "Siege|State")
    FSiegePlan GetCurrentSiegePlan() const { return CurrentSiegePlan; }

    UFUNCTION(BlueprintPure, Category = "Siege|State")
    TArray<FMissionStageData> GetCurrentPhaseStages() const;

protected:
    virtual void BeginPlay() override;

    // Siege State
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    bool bSiegeActive;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    FSiegePlan CurrentSiegePlan;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    ESiegePhase CurrentPhase;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Siege State")
    int32 CompletedStagesInCurrentPhase;

    // Component References
    UPROPERTY()
    UPhaseGateComponent* BoundPhaseGate;

    UPROPERTY()
    class UDominanceMeterComponent* BoundDominanceMeter;

    UPROPERTY()
    class UTicketPoolComponent* BoundTicketPool;

    UPROPERTY()
    ATGMissionDirector2* BoundMissionDirector;

private:
    void OnPhaseChanged(ESiegePhase OldPhase, ESiegePhase NewPhase);
    void OnMissionStageChanged(EMissionStage NewStage);
    void SetupMissionStagesForPhase(ESiegePhase Phase);
    TArray<FMissionStageData> GetStagesForPhase(ESiegePhase Phase) const;
    void CheckPhaseAdvancementConditions();
};