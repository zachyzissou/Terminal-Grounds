#include "TicketPoolComponent.h"
#include "Net/UnrealNetwork.h"
#include "Engine/World.h"
#include "Engine/Engine.h"

UTicketPoolComponent::UTicketPoolComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    SetIsReplicatedByDefault(true);

    InitialAttackerTickets = 100;
    InitialDefenderTickets = 100;
    bAllowNegativeTickets = false;
    TicketsPerRespawn = 1;
    TicketsPerObjectiveLoss = 5;
    AttackerConsumptionRate = 1.0f;
    DefenderConsumptionRate = 1.0f;
}

void UTicketPoolComponent::BeginPlay()
{
    Super::BeginPlay();

    if (GetOwnerRole() == ROLE_Authority)
    {
        Tickets.AttackerTickets = InitialAttackerTickets;
        Tickets.DefenderTickets = InitialDefenderTickets;
        PreviousTickets = Tickets;
    }
}

void UTicketPoolComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(UTicketPoolComponent, Tickets);
    DOREPLIFETIME(UTicketPoolComponent, AttackerConsumptionRate);
    DOREPLIFETIME(UTicketPoolComponent, DefenderConsumptionRate);
}

void UTicketPoolComponent::ConsumeAttackerTickets(int32 Amount)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    int32 ScaledAmount = FMath::RoundToInt(Amount * AttackerConsumptionRate);
    ConsumeTicketsInternal(true, ScaledAmount);
}

void UTicketPoolComponent::ConsumeDefenderTickets(int32 Amount)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    int32 ScaledAmount = FMath::RoundToInt(Amount * DefenderConsumptionRate);
    ConsumeTicketsInternal(false, ScaledAmount);
}

void UTicketPoolComponent::RefillAttackerTickets(int32 Amount)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    RefillTicketsInternal(true, Amount);
}

void UTicketPoolComponent::RefillDefenderTickets(int32 Amount)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    RefillTicketsInternal(false, Amount);
}

void UTicketPoolComponent::ResetTickets()
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    int32 OldAttackerTickets = Tickets.AttackerTickets;
    int32 OldDefenderTickets = Tickets.DefenderTickets;

    Tickets.AttackerTickets = InitialAttackerTickets;
    Tickets.DefenderTickets = InitialDefenderTickets;

    if (OldAttackerTickets != Tickets.AttackerTickets)
    {
        OnTicketsRefilled.Broadcast(true, Tickets.AttackerTickets);
    }

    if (OldDefenderTickets != Tickets.DefenderTickets)
    {
        OnTicketsRefilled.Broadcast(false, Tickets.DefenderTickets);
    }

    PreviousTickets = Tickets;

    UE_LOG(LogTemp, Log, TEXT("Tickets reset - Attackers: %d, Defenders: %d"), 
        Tickets.AttackerTickets, Tickets.DefenderTickets);
}

float UTicketPoolComponent::GetAttackerTicketPercentage() const
{
    if (InitialAttackerTickets <= 0)
    {
        return 0.0f;
    }

    return FMath::Clamp(static_cast<float>(Tickets.AttackerTickets) / static_cast<float>(InitialAttackerTickets), 0.0f, 1.0f);
}

float UTicketPoolComponent::GetDefenderTicketPercentage() const
{
    if (InitialDefenderTickets <= 0)
    {
        return 0.0f;
    }

    return FMath::Clamp(static_cast<float>(Tickets.DefenderTickets) / static_cast<float>(InitialDefenderTickets), 0.0f, 1.0f);
}

void UTicketPoolComponent::SetTicketConsumptionRate(float AttackerRate, float DefenderRate)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    AttackerConsumptionRate = FMath::Max(0.1f, AttackerRate);
    DefenderConsumptionRate = FMath::Max(0.1f, DefenderRate);

    UE_LOG(LogTemp, Log, TEXT("Ticket consumption rates updated - Attacker: %f, Defender: %f"), 
        AttackerConsumptionRate, DefenderConsumptionRate);
}

void UTicketPoolComponent::GetTicketConsumptionRates(float& OutAttackerRate, float& OutDefenderRate) const
{
    OutAttackerRate = AttackerConsumptionRate;
    OutDefenderRate = DefenderConsumptionRate;
}

void UTicketPoolComponent::OnRep_Tickets()
{
    // Check for changes and broadcast events
    if (PreviousTickets.AttackerTickets != Tickets.AttackerTickets)
    {
        int32 Consumed = PreviousTickets.AttackerTickets - Tickets.AttackerTickets;
        if (Consumed > 0)
        {
            OnTicketsConsumed.Broadcast(true, Consumed, Tickets.AttackerTickets);
        }
        else if (Consumed < 0)
        {
            OnTicketsRefilled.Broadcast(true, Tickets.AttackerTickets);
        }

        CheckExhaustion(true, PreviousTickets.AttackerTickets, Tickets.AttackerTickets);
    }

    if (PreviousTickets.DefenderTickets != Tickets.DefenderTickets)
    {
        int32 Consumed = PreviousTickets.DefenderTickets - Tickets.DefenderTickets;
        if (Consumed > 0)
        {
            OnTicketsConsumed.Broadcast(false, Consumed, Tickets.DefenderTickets);
        }
        else if (Consumed < 0)
        {
            OnTicketsRefilled.Broadcast(false, Tickets.DefenderTickets);
        }

        CheckExhaustion(false, PreviousTickets.DefenderTickets, Tickets.DefenderTickets);
    }

    PreviousTickets = Tickets;
}

void UTicketPoolComponent::ConsumeTicketsInternal(bool bIsAttacker, int32 Amount)
{
    if (Amount <= 0)
    {
        return;
    }

    int32 OldValue;
    int32* TargetTickets;

    if (bIsAttacker)
    {
        OldValue = Tickets.AttackerTickets;
        TargetTickets = &Tickets.AttackerTickets;
    }
    else
    {
        OldValue = Tickets.DefenderTickets;
        TargetTickets = &Tickets.DefenderTickets;
    }

    if (bAllowNegativeTickets)
    {
        *TargetTickets -= Amount;
    }
    else
    {
        *TargetTickets = FMath::Max(0, *TargetTickets - Amount);
    }

    int32 ActualConsumed = OldValue - *TargetTickets;
    
    if (ActualConsumed > 0)
    {
        OnTicketsConsumed.Broadcast(bIsAttacker, ActualConsumed, *TargetTickets);
        CheckExhaustion(bIsAttacker, OldValue, *TargetTickets);

        UE_LOG(LogTemp, Log, TEXT("%s tickets consumed: %d (remaining: %d)"), 
            bIsAttacker ? TEXT("Attacker") : TEXT("Defender"), 
            ActualConsumed, 
            *TargetTickets);
    }
}

void UTicketPoolComponent::RefillTicketsInternal(bool bIsAttacker, int32 Amount)
{
    if (Amount <= 0)
    {
        return;
    }

    int32* TargetTickets;
    int32 MaxTickets;

    if (bIsAttacker)
    {
        TargetTickets = &Tickets.AttackerTickets;
        MaxTickets = InitialAttackerTickets;
    }
    else
    {
        TargetTickets = &Tickets.DefenderTickets;
        MaxTickets = InitialDefenderTickets;
    }

    int32 OldValue = *TargetTickets;
    *TargetTickets = FMath::Min(MaxTickets, *TargetTickets + Amount);

    if (*TargetTickets > OldValue)
    {
        OnTicketsRefilled.Broadcast(bIsAttacker, *TargetTickets);

        UE_LOG(LogTemp, Log, TEXT("%s tickets refilled: %d -> %d"), 
            bIsAttacker ? TEXT("Attacker") : TEXT("Defender"), 
            OldValue, 
            *TargetTickets);
    }
}

void UTicketPoolComponent::CheckExhaustion(bool bIsAttacker, int32 OldValue, int32 NewValue)
{
    bool WasExhausted = OldValue <= 0;
    bool IsExhausted = NewValue <= 0;

    if (!WasExhausted && IsExhausted)
    {
        OnTicketsExhausted.Broadcast(bIsAttacker);
        
        UE_LOG(LogTemp, Warning, TEXT("%s tickets exhausted!"), 
            bIsAttacker ? TEXT("Attacker") : TEXT("Defender"));
    }
}