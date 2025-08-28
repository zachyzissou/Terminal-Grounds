#include "Splice/TGSpliceEvent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameInstance.h"
#include "Codex/TGCodexSubsystem.h"
#include "Trust/TGTrustSubsystem.h"
#include "Economy/TGConvoyEconomySubsystem.h"

void UTGSpliceSubsystem::RegisterDeck(UTGSpliceEventDeck* Deck)
{
    if (Deck)
    {
        Decks.AddUnique(Deck);
    }
}

void UTGSpliceSubsystem::ClearDecks()
{
    Decks.Reset();
}

bool UTGSpliceSubsystem::IsCardEligible(const FTGSpliceEventCard& Card, const TMap<FName, FString>& Context) const
{
    // All constraints must match provided context (exact string compare)
    for (const auto& Kvp : Card.Constraints)
    {
        const FString* Found = Context.Find(Kvp.Key);
        if (!Found || *Found != Kvp.Value)
        {
            return false;
        }
    }
    return true;
}

const FTGSpliceOutcome* UTGSpliceSubsystem::ChooseOutcome(const FTGSpliceEventCard& Card) const
{
    if (Card.Outcomes.Num() == 0)
    {
        return nullptr;
    }
    // Simple uniform choice for now
    const int32 Index = FMath::RandRange(0, Card.Outcomes.Num() - 1);
    return &Card.Outcomes[Index];
}

bool UTGSpliceSubsystem::TriggerEligibleEvents(ETGSpliceTrigger Trigger, const TMap<FName, FString>& Context)
{
    bool bTriggeredAny = false;
    // Build weighted list of cards that contain this trigger and pass constraints
    TArray<const FTGSpliceEventCard*> Eligible;
    for (const TWeakObjectPtr<UTGSpliceEventDeck>& DeckPtr : Decks)
    {
        const UTGSpliceEventDeck* Deck = DeckPtr.Get();
        if (!Deck) continue;
        for (const FTGSpliceEventCard& Card : Deck->Cards)
        {
            if (!Card.Triggers.Contains(Trigger)) continue;
            if (!IsCardEligible(Card, Context)) continue;
            const int32 ClampedW = FMath::Max(1, Card.Weight);
            for (int32 i=0; i<ClampedW; ++i)
            {
                Eligible.Add(&Card);
            }
        }
    }

    if (Eligible.Num() == 0)
    {
        return false;
    }

    const int32 Pick = FMath::RandRange(0, Eligible.Num() - 1);
    const FTGSpliceEventCard* Card = Eligible[Pick];
    if (Card)
    {
        const FTGSpliceOutcome* Outcome = ChooseOutcome(*Card);
        if (Outcome)
        {
            // Apply side effects into other systems
            ApplyOutcome(*Outcome, Context);

            // Broadcast for UI/audio hooks
            OnSpliceEventTriggered.Broadcast(*Card, *Outcome);
            bTriggeredAny = true;
        }
    }
    return bTriggeredAny;
}

static UTGCodexSubsystem* TG_GetCodexSubsystem(const UObject* WorldContext)
{
    if (!WorldContext) return nullptr;
    if (const UWorld* World = WorldContext->GetWorld())
    {
        if (UGameInstance* GI = World->GetGameInstance())
        {
            return GI->GetSubsystem<UTGCodexSubsystem>();
        }
    }
    return nullptr;
}

static UTGTrustSubsystem* TG_GetTrustSubsystem(const UObject* WorldContext)
{
    if (!WorldContext) return nullptr;
    if (const UWorld* World = WorldContext->GetWorld())
    {
        if (UGameInstance* GI = World->GetGameInstance())
        {
            return GI->GetSubsystem<UTGTrustSubsystem>();
        }
    }
    return nullptr;
}

void UTGSpliceSubsystem::ApplyOutcome(const FTGSpliceOutcome& Outcome, const TMap<FName, FString>& Context)
{
    // Convoy economy shift
    if (Outcome.ConvoyIntegrityDelta != 0.f)
    {
        if (UWorld* World = GetWorld())
        {
            if (UTGConvoyEconomySubsystem* Convoy = World->GetSubsystem<UTGConvoyEconomySubsystem>())
            {
                const FName RouteId = Context.Contains("RouteId") ? FName(**Context.Find("RouteId")) : NAME_None;
                const FName JobType = Context.Contains("JobType") ? FName(**Context.Find("JobType")) : NAME_None;
                const bool bSuccess = Outcome.ConvoyIntegrityDelta >= 0.f;
                Convoy->ApplyConvoyOutcome(FMath::Abs(Outcome.ConvoyIntegrityDelta), RouteId, JobType, bSuccess);
            }
        }
    }

    // Trust adjustment (if context has player ids)
    if (Outcome.ReputationDelta != 0)
    {
        if (UTGTrustSubsystem* Trust = TG_GetTrustSubsystem(this))
        {
            const FString* A = Context.Find("PlayerA");
            const FString* B = Context.Find("PlayerB");
            if (A && B)
            {
                const float Delta = FMath::Clamp(Outcome.ReputationDelta / 100.f, -1.f, 1.f);
                if (Delta >= 0.f)
                {
                    Trust->RecordParley(*A, *B, Delta);
                }
                else
                {
                    Trust->RecordBreach(*A, *B, FMath::Abs(Delta));
                }
            }
        }
    }

    // Codex unlocks
    if (Outcome.UnlockCodexIds.Num() > 0)
    {
        if (UTGCodexSubsystem* Codex = TG_GetCodexSubsystem(this))
        {
            for (const FString& IdStr : Outcome.UnlockCodexIds)
            {
                FTGCodexEntry Entry;
                Entry.EntryId = FName(*IdStr);
                Entry.Title = FText::FromString(IdStr);
                Codex->UnlockCodex(Entry);
            }
        }
    }
}
