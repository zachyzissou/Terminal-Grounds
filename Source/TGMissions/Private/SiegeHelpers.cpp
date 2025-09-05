#include "SiegeHelpers.h"
#include "TGMissionDirector2.h"
#include "../TGTerritorial/Public/DominanceMeterComponent.h"
#include "../TGTerritorial/Public/TicketPoolComponent.h"
#include "Engine/World.h"

USiegeHelperComponent::USiegeHelperComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    SetIsReplicatedByDefault(false); // This is a helper component, state is managed elsewhere

    bSiegeActive = false;
    CurrentPhase = ESiegePhase::Probe;
    CompletedStagesInCurrentPhase = 0;
    
    BoundPhaseGate = nullptr;
    BoundDominanceMeter = nullptr;
    BoundTicketPool = nullptr;
    BoundMissionDirector = nullptr;
}

void USiegeHelperComponent::BeginPlay()
{
    Super::BeginPlay();
}

void USiegeHelperComponent::StartSiege(const FSiegePlan& Plan)
{
    CurrentSiegePlan = Plan;
    CurrentPhase = ESiegePhase::Probe;
    CompletedStagesInCurrentPhase = 0;
    bSiegeActive = true;

    // Initialize phase gate if bound
    if (BoundPhaseGate)
    {
        BoundPhaseGate->SetPhase(ESiegePhase::Probe);
    }

    // Set up mission stages for the Probe phase
    SetupMissionStagesForPhase(ESiegePhase::Probe);

    UE_LOG(LogTemp, Log, TEXT("Siege started with %d Probe stages, %d Interdict stages, %d Dominate stages"),
        Plan.ProbeStages.Num(), Plan.InterdictStages.Num(), Plan.DominateStages.Num());
}

void USiegeHelperComponent::EndSiege(bool bVictory)
{
    bSiegeActive = false;
    CompletedStagesInCurrentPhase = 0;

    if (BoundMissionDirector)
    {
        if (bVictory)
        {
            BoundMissionDirector->CompleteMission();
        }
        else
        {
            BoundMissionDirector->FailMission();
        }
    }

    OnSiegeCompleted.Broadcast();
    UE_LOG(LogTemp, Log, TEXT("Siege ended with %s"), bVictory ? TEXT("Victory") : TEXT("Defeat"));
}

void USiegeHelperComponent::ProcessSiegeStageCompletion(EMissionStage CompletedStage)
{
    if (!bSiegeActive)
    {
        return;
    }

    CompletedStagesInCurrentPhase++;

    // Apply dominance reward for completing a stage
    if (BoundDominanceMeter)
    {
        ApplyDominanceReward(CurrentSiegePlan.DominanceRewardPerStage);
    }

    // Check if we should advance to the next phase
    CheckPhaseAdvancementConditions();

    UE_LOG(LogTemp, Log, TEXT("Siege stage completed: %s (%d stages completed in current phase)"), 
        *UEnum::GetValueAsString(CompletedStage), CompletedStagesInCurrentPhase);
}

void USiegeHelperComponent::ApplySiegeDynamicEventOutcome(const FSiegeDynamicEventOutcome& Outcome)
{
    // Apply dominance changes
    if (BoundDominanceMeter && FMath::Abs(Outcome.DominanceDelta) > KINDA_SMALL_NUMBER)
    {
        BoundDominanceMeter->AddDominanceDelta(Outcome.DominanceDelta);
    }

    // Apply ticket changes
    if (BoundTicketPool)
    {
        if (Outcome.AttackerTicketDelta != 0)
        {
            if (Outcome.AttackerTicketDelta > 0)
            {
                BoundTicketPool->RefillAttackerTickets(Outcome.AttackerTicketDelta);
            }
            else
            {
                BoundTicketPool->ConsumeAttackerTickets(FMath::Abs(Outcome.AttackerTicketDelta));
            }
        }

        if (Outcome.DefenderTicketDelta != 0)
        {
            if (Outcome.DefenderTicketDelta > 0)
            {
                BoundTicketPool->RefillDefenderTickets(Outcome.DefenderTicketDelta);
            }
            else
            {
                BoundTicketPool->ConsumeDefenderTickets(FMath::Abs(Outcome.DefenderTicketDelta));
            }
        }
    }

    // Force phase change if requested
    if (Outcome.bShouldAdvancePhase)
    {
        if (BoundPhaseGate)
        {
            BoundPhaseGate->AdvancePhase();
        }
    }

    OnSiegeEventOutcome.Broadcast(Outcome);
}

void USiegeHelperComponent::BindToPhaseGate(UPhaseGateComponent* PhaseGate)
{
    if (PhaseGate)
    {
        BoundPhaseGate = PhaseGate;
        CurrentPhase = PhaseGate->GetPhase();
        
        // Bind to phase change events
        PhaseGate->OnPhaseChanged.AddDynamic(this, &USiegeHelperComponent::OnPhaseChanged);
    }
}

void USiegeHelperComponent::AdvanceToNextSiegePhase()
{
    if (BoundPhaseGate)
    {
        BoundPhaseGate->AdvancePhase();
    }
}

ESiegePhase USiegeHelperComponent::GetCurrentSiegePhase() const
{
    if (BoundPhaseGate)
    {
        return BoundPhaseGate->GetPhase();
    }
    return CurrentPhase;
}

void USiegeHelperComponent::BindToDominanceMeter(UDominanceMeterComponent* DominanceMeter)
{
    if (DominanceMeter)
    {
        BoundDominanceMeter = DominanceMeter;
    }
}

void USiegeHelperComponent::ApplyDominanceReward(float Amount)
{
    if (BoundDominanceMeter)
    {
        BoundDominanceMeter->AddDominanceDelta(Amount);
    }
}

void USiegeHelperComponent::BindToTicketPool(UTicketPoolComponent* TicketPool)
{
    if (TicketPool)
    {
        BoundTicketPool = TicketPool;
    }
}

void USiegeHelperComponent::ApplyTicketPenalty(bool bIsAttacker, int32 Amount)
{
    if (BoundTicketPool)
    {
        if (bIsAttacker)
        {
            BoundTicketPool->ConsumeAttackerTickets(Amount);
        }
        else
        {
            BoundTicketPool->ConsumeDefenderTickets(Amount);
        }
    }
}

void USiegeHelperComponent::BindToMissionDirector(ATGMissionDirector2* MissionDirector)
{
    if (MissionDirector)
    {
        BoundMissionDirector = MissionDirector;
        
        // Bind to stage change events
        MissionDirector->OnMissionStageChanged.AddDynamic(this, &USiegeHelperComponent::OnMissionStageChanged);
    }
}

TArray<FMissionStageData> USiegeHelperComponent::GetCurrentPhaseStages() const
{
    return GetStagesForPhase(GetCurrentSiegePhase());
}

void USiegeHelperComponent::OnPhaseChanged(ESiegePhase OldPhase, ESiegePhase NewPhase)
{
    CurrentPhase = NewPhase;
    CompletedStagesInCurrentPhase = 0;

    // Set up mission stages for the new phase
    SetupMissionStagesForPhase(NewPhase);

    OnSiegePhaseAdvanced.Broadcast(OldPhase, NewPhase);

    UE_LOG(LogTemp, Log, TEXT("Siege phase advanced from %s to %s"), 
        *UEnum::GetValueAsString(OldPhase), 
        *UEnum::GetValueAsString(NewPhase));
}

void USiegeHelperComponent::OnMissionStageChanged(EMissionStage NewStage)
{
    // Process stage completion for siege
    if (NewStage == EMissionStage::Completed)
    {
        ProcessSiegeStageCompletion(NewStage);
    }
    else if (NewStage == EMissionStage::Failed)
    {
        // Apply ticket penalty for failed stages
        ApplyTicketPenalty(true, CurrentSiegePlan.TicketCostPerFailure);
    }
}

void USiegeHelperComponent::SetupMissionStagesForPhase(ESiegePhase Phase)
{
    if (!BoundMissionDirector)
    {
        return;
    }

    TArray<FMissionStageData> PhaseStages = GetStagesForPhase(Phase);
    if (PhaseStages.Num() > 0)
    {
        BoundMissionDirector->StartMission(PhaseStages);
    }
}

TArray<FMissionStageData> USiegeHelperComponent::GetStagesForPhase(ESiegePhase Phase) const
{
    switch (Phase)
    {
        case ESiegePhase::Probe:
            return CurrentSiegePlan.ProbeStages;
        case ESiegePhase::Interdict:
            return CurrentSiegePlan.InterdictStages;
        case ESiegePhase::Dominate:
            return CurrentSiegePlan.DominateStages;
        case ESiegePhase::Locked:
            return TArray<FMissionStageData>(); // No stages during lock
        default:
            return TArray<FMissionStageData>();
    }
}

void USiegeHelperComponent::CheckPhaseAdvancementConditions()
{
    if (!BoundPhaseGate)
    {
        return;
    }

    TArray<FMissionStageData> CurrentPhaseStages = GetStagesForPhase(CurrentPhase);
    
    // Check if we've completed all stages for the current phase
    if (CompletedStagesInCurrentPhase >= CurrentPhaseStages.Num() && CurrentPhaseStages.Num() > 0)
    {
        // All stages completed, advance phase
        BoundPhaseGate->AdvancePhase();
    }
}