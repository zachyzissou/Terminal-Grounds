#include "PhaseGateComponent.h"
#include "Net/UnrealNetwork.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Engine/Engine.h"

UPhaseGateComponent::UPhaseGateComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    SetIsReplicatedByDefault(true);

    CurrentPhase = ESiegePhase::Probe;
    PhaseProgress = 0.0f;
    PhaseProgressThreshold = 1.0f;
    bAutoAdvancePhase = true;
    LockDurationSeconds = 300.0f;
}

void UPhaseGateComponent::BeginPlay()
{
    Super::BeginPlay();

    if (GetOwnerRole() == ROLE_Authority)
    {
        PhaseStartTime = FDateTime::Now();
    }
}

void UPhaseGateComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(UPhaseGateComponent, CurrentPhase);
    DOREPLIFETIME(UPhaseGateComponent, PhaseProgress);
    DOREPLIFETIME(UPhaseGateComponent, PhaseStartTime);
    DOREPLIFETIME(UPhaseGateComponent, LockEndTime);
}

bool UPhaseGateComponent::CanAdvancePhase() const
{
    if (CurrentPhase == ESiegePhase::Locked)
    {
        return false;
    }

    if (CurrentPhase == ESiegePhase::Dominate)
    {
        return true; // Can advance to Locked
    }

    return PhaseProgress >= PhaseProgressThreshold;
}

void UPhaseGateComponent::AdvancePhase()
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    if (!CanAdvancePhase())
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot advance phase - conditions not met"));
        return;
    }

    ESiegePhase OldPhase = CurrentPhase;
    
    switch (CurrentPhase)
    {
        case ESiegePhase::Probe:
            CurrentPhase = ESiegePhase::Interdict;
            break;
        case ESiegePhase::Interdict:
            CurrentPhase = ESiegePhase::Dominate;
            break;
        case ESiegePhase::Dominate:
            CurrentPhase = ESiegePhase::Locked;
            LockEndTime = FDateTime::Now() + FTimespan::FromSeconds(LockDurationSeconds);
            break;
        case ESiegePhase::Locked:
            // Cannot advance from Locked
            return;
    }

    PhaseProgress = 0.0f;
    PhaseStartTime = FDateTime::Now();
    
    BroadcastPhaseChange(OldPhase, CurrentPhase);
}

void UPhaseGateComponent::SetPhase(ESiegePhase NewPhase)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    if (CurrentPhase == NewPhase)
    {
        return;
    }

    ESiegePhase OldPhase = CurrentPhase;
    CurrentPhase = NewPhase;
    PhaseProgress = 0.0f;
    PhaseStartTime = FDateTime::Now();

    if (NewPhase == ESiegePhase::Locked)
    {
        LockEndTime = FDateTime::Now() + FTimespan::FromSeconds(LockDurationSeconds);
    }

    BroadcastPhaseChange(OldPhase, NewPhase);
}

FString UPhaseGateComponent::GetPhaseName() const
{
    switch (CurrentPhase)
    {
        case ESiegePhase::Probe:
            return TEXT("Probe");
        case ESiegePhase::Interdict:
            return TEXT("Interdict");
        case ESiegePhase::Dominate:
            return TEXT("Dominate");
        case ESiegePhase::Locked:
            return TEXT("Locked");
        default:
            return TEXT("Unknown");
    }
}

void UPhaseGateComponent::UpdatePhaseProgress(float Delta)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    if (CurrentPhase == ESiegePhase::Locked)
    {
        return;
    }

    float OldProgress = PhaseProgress;
    PhaseProgress = FMath::Clamp(PhaseProgress + Delta, 0.0f, PhaseProgressThreshold);

    if (bAutoAdvancePhase && PhaseProgress >= PhaseProgressThreshold && OldProgress < PhaseProgressThreshold)
    {
        AdvancePhase();
    }
}

void UPhaseGateComponent::OnRep_Phase(ESiegePhase OldPhase)
{
    BroadcastPhaseChange(OldPhase, CurrentPhase);
}

void UPhaseGateComponent::OnRep_Progress()
{
    // Clients can react to progress changes if needed
}

void UPhaseGateComponent::BroadcastPhaseChange(ESiegePhase OldPhase, ESiegePhase NewPhase)
{
    OnPhaseChanged.Broadcast(OldPhase, NewPhase);

    UE_LOG(LogTemp, Log, TEXT("Phase changed from %s to %s"), 
        *GetPhaseName(), 
        *StaticEnum<ESiegePhase>()->GetNameStringByValue((int64)NewPhase));
}

bool UPhaseGateComponent::IsLocked() const
{
    if (CurrentPhase != ESiegePhase::Locked)
    {
        return false;
    }

    return FDateTime::Now() < LockEndTime;
}