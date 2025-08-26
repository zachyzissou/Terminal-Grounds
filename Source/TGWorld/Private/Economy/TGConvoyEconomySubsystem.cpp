#include "Economy/TGConvoyEconomySubsystem.h"

UTGConvoyEconomySubsystem::UTGConvoyEconomySubsystem()
    : IntegrityIndex(0.5f)
{
}

void UTGConvoyEconomySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UTGConvoyEconomySubsystem::Deinitialize()
{
    Super::Deinitialize();
}

void UTGConvoyEconomySubsystem::ApplyConvoyOutcome(float Delta, FName RouteId, FName JobType, bool bSuccess)
{
    const float SignedDelta = bSuccess ? FMath::Abs(Delta) : -FMath::Abs(Delta);
    const float Old = IntegrityIndex;
    IntegrityIndex = FMath::Clamp(IntegrityIndex + SignedDelta, 0.f, 1.f);
    if (!RouteId.IsNone())
    {
        ActiveRoutes.Add(RouteId);
    }
    BroadcastChange(Old, IntegrityIndex);
}

void UTGConvoyEconomySubsystem::SetIntegrityIndex(float NewValue)
{
    const float Old = IntegrityIndex;
    IntegrityIndex = FMath::Clamp(NewValue, 0.f, 1.f);
    BroadcastChange(Old, IntegrityIndex);
}

void UTGConvoyEconomySubsystem::AdvanceDecay(float DeltaSeconds)
{
    if (DecayHalfLifeSeconds <= 0.f)
    {
        return;
    }
    const float Lambda = FMath::Loge(2.0f) / DecayHalfLifeSeconds;
    const float Old = IntegrityIndex;
    IntegrityIndex = Equilibrium + (IntegrityIndex - Equilibrium) * FMath::Exp(-Lambda * DeltaSeconds);
    if (!FMath::IsNearlyEqual(Old, IntegrityIndex))
    {
        BroadcastChange(Old, IntegrityIndex);
    }
}

void UTGConvoyEconomySubsystem::BroadcastChange(float OldIndex, float NewIndex)
{
    const float Delta = NewIndex - OldIndex;
    OnIntegrityIndexChanged.Broadcast(NewIndex, Delta);
}
