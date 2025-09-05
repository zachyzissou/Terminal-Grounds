#include "DominanceMeterComponent.h"
#include "Net/UnrealNetwork.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Engine/Engine.h"

UDominanceMeterComponent::UDominanceMeterComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    SetIsReplicatedByDefault(true);

    CurrentDominance = 0.5f;
    ClientDisplayDominance = 0.5f;
    DominanceDecayRate = 0.01f;
    bEnableDecay = true;
    InterpolationSpeed = 2.0f;
    ActiveModifier = 1.0f;
    ModifierEndTime = 0.0f;

    NotificationThresholds = {0.25f, 0.5f, 0.75f, 0.9f};
}

void UDominanceMeterComponent::BeginPlay()
{
    Super::BeginPlay();
    ClientDisplayDominance = CurrentDominance;
}

void UDominanceMeterComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (GetOwnerRole() == ROLE_Authority)
    {
        ProcessModifiers(DeltaTime);
        ProcessDecay(DeltaTime);
    }
    else
    {
        // Client-side interpolation for smooth visual updates
        InterpolateClientDisplay(DeltaTime);
    }
}

void UDominanceMeterComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(UDominanceMeterComponent, CurrentDominance);
    DOREPLIFETIME(UDominanceMeterComponent, ActiveModifier);
    DOREPLIFETIME(UDominanceMeterComponent, ModifierEndTime);
}

void UDominanceMeterComponent::AddDominanceDelta(float Delta)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    float ModifiedDelta = Delta * ActiveModifier;
    float OldDominance = CurrentDominance;
    
    CurrentDominance = FMath::Clamp(CurrentDominance + ModifiedDelta, 0.0f, 1.0f);

    if (FMath::Abs(CurrentDominance - OldDominance) > KINDA_SMALL_NUMBER)
    {
        CheckThresholds(OldDominance, CurrentDominance);
        OnDominanceChanged.Broadcast(OldDominance, CurrentDominance);

        if (IsDominanceComplete() && !FMath::IsNearlyEqual(OldDominance, 1.0f) && !FMath::IsNearlyEqual(OldDominance, 0.0f))
        {
            OnDominanceComplete.Broadcast();
        }
    }
}

void UDominanceMeterComponent::SetDominance(float NewDominance)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    float ClampedDominance = FMath::Clamp(NewDominance, 0.0f, 1.0f);
    
    if (!FMath::IsNearlyEqual(CurrentDominance, ClampedDominance))
    {
        float OldDominance = CurrentDominance;
        CurrentDominance = ClampedDominance;
        
        CheckThresholds(OldDominance, CurrentDominance);
        OnDominanceChanged.Broadcast(OldDominance, CurrentDominance);

        if (IsDominanceComplete() && !FMath::IsNearlyEqual(OldDominance, 1.0f) && !FMath::IsNearlyEqual(OldDominance, 0.0f))
        {
            OnDominanceComplete.Broadcast();
        }
    }
}

void UDominanceMeterComponent::ApplyDominanceModifier(float Multiplier, float Duration)
{
    if (GetOwnerRole() != ROLE_Authority)
    {
        return;
    }

    ActiveModifier = FMath::Max(0.1f, Multiplier); // Minimum 10% rate
    ModifierEndTime = GetWorld()->GetTimeSeconds() + Duration;

    UE_LOG(LogTemp, Log, TEXT("Dominance modifier applied: %f for %f seconds"), Multiplier, Duration);
}

void UDominanceMeterComponent::OnRep_Dominance(float OldDominance)
{
    CheckThresholds(OldDominance, CurrentDominance);
    OnDominanceChanged.Broadcast(OldDominance, CurrentDominance);

    if (IsDominanceComplete() && !FMath::IsNearlyEqual(OldDominance, 1.0f) && !FMath::IsNearlyEqual(OldDominance, 0.0f))
    {
        OnDominanceComplete.Broadcast();
    }
}

void UDominanceMeterComponent::ProcessDecay(float DeltaTime)
{
    if (!bEnableDecay || DominanceDecayRate <= 0.0f)
    {
        return;
    }

    // Decay towards neutral (0.5)
    float DecayAmount = DominanceDecayRate * DeltaTime;
    float OldDominance = CurrentDominance;
    
    if (CurrentDominance > 0.5f)
    {
        CurrentDominance = FMath::Max(0.5f, CurrentDominance - DecayAmount);
    }
    else if (CurrentDominance < 0.5f)
    {
        CurrentDominance = FMath::Min(0.5f, CurrentDominance + DecayAmount);
    }

    if (!FMath::IsNearlyEqual(CurrentDominance, OldDominance))
    {
        OnDominanceChanged.Broadcast(OldDominance, CurrentDominance);
    }
}

void UDominanceMeterComponent::ProcessModifiers(float DeltaTime)
{
    if (ModifierEndTime > 0.0f && GetWorld()->GetTimeSeconds() >= ModifierEndTime)
    {
        ActiveModifier = 1.0f;
        ModifierEndTime = 0.0f;
        UE_LOG(LogTemp, Log, TEXT("Dominance modifier expired"));
    }
}

void UDominanceMeterComponent::CheckThresholds(float OldValue, float NewValue)
{
    for (float Threshold : NotificationThresholds)
    {
        bool OldAbove = OldValue >= Threshold;
        bool NewAbove = NewValue >= Threshold;
        
        if (OldAbove != NewAbove && !TriggeredThresholds.Contains(Threshold))
        {
            OnDominanceThresholdReached.Broadcast(Threshold);
            TriggeredThresholds.Add(Threshold);
            
            // Reset threshold tracking if we cross back
            if (!NewAbove)
            {
                TriggeredThresholds.Remove(Threshold);
            }
        }
    }
}

void UDominanceMeterComponent::InterpolateClientDisplay(float DeltaTime)
{
    if (GetOwnerRole() == ROLE_Authority)
    {
        return;
    }

    float InterpSpeed = InterpolationSpeed * DeltaTime;
    ClientDisplayDominance = FMath::FInterpTo(ClientDisplayDominance, CurrentDominance, DeltaTime, InterpSpeed);
}