#include "Splice/TGSpliceEvent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameInstance.h"
#include "Codex/TGCodexSubsystem.h"
#include "Trust/TGTrustSubsystem.h"
#include "Economy/TGConvoyEconomySubsystem.h"
#include "TGTerritorialManager.h"

void UTGSpliceSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    TerritorialManager = nullptr;
    
    UE_LOG(LogTemp, Log, TEXT("UTGSpliceSubsystem: Initialized"));
    
    // Initialize territorial integration (will be called automatically when TGTerritorialManager is ready)
    InitializeTerritorialIntegration();
}

void UTGSpliceSubsystem::Deinitialize()
{
    // Unbind from territorial events
    if (TerritorialManager)
    {
        TerritorialManager->OnTerritoryControlChanged.RemoveAll(this);
        TerritorialManager->OnTerritoryContested.RemoveAll(this);
        TerritorialManager->OnInfluenceChanged.RemoveAll(this);
        TerritorialManager = nullptr;
    }
    
    UE_LOG(LogTemp, Log, TEXT("UTGSpliceSubsystem: Deinitialized"));
    
    Super::Deinitialize();
}

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

// Territorial Event Context Implementation
TMap<FName, FString> FTGTerritorialEventContext::ToContextMap() const
{
    TMap<FName, FString> ContextMap;
    
    ContextMap.Add("TerritoryId", FString::FromInt(TerritoryId));
    ContextMap.Add("TerritoryName", TerritoryName);
    ContextMap.Add("TerritoryType", TerritoryType);
    ContextMap.Add("PreviousControllerFactionId", FString::FromInt(PreviousControllerFactionId));
    ContextMap.Add("PreviousControllerFactionName", PreviousControllerFactionName);
    ContextMap.Add("NewControllerFactionId", FString::FromInt(NewControllerFactionId));
    ContextMap.Add("NewControllerFactionName", NewControllerFactionName);
    ContextMap.Add("StrategicValue", FString::FromInt(StrategicValue));
    ContextMap.Add("ResourceMultiplier", FString::SanitizeFloat(ResourceMultiplier));
    ContextMap.Add("WasContested", bWasContested ? TEXT("true") : TEXT("false"));
    ContextMap.Add("IsContested", bIsContested ? TEXT("true") : TEXT("false"));
    
    // Add connected territory information
    FString ConnectedIdsList;
    for (int32 i = 0; i < ConnectedTerritoryIds.Num(); ++i)
    {
        ConnectedIdsList += FString::FromInt(ConnectedTerritoryIds[i]);
        if (i < ConnectedTerritoryIds.Num() - 1)
        {
            ConnectedIdsList += TEXT(",");
        }
    }
    ContextMap.Add("ConnectedTerritoryIds", ConnectedIdsList);
    
    FString ConnectedNamesList;
    for (int32 i = 0; i < ConnectedTerritoryNames.Num(); ++i)
    {
        ConnectedNamesList += ConnectedTerritoryNames[i];
        if (i < ConnectedTerritoryNames.Num() - 1)
        {
            ConnectedNamesList += TEXT(",");
        }
    }
    ContextMap.Add("ConnectedTerritoryNames", ConnectedNamesList);
    
    return ContextMap;
}

// Territorial Integration Methods
void UTGSpliceSubsystem::InitializeTerritorialIntegration()
{
    if (UWorld* World = GetWorld())
    {
        TerritorialManager = World->GetSubsystem<UTGTerritorialManager>();
        if (TerritorialManager)
        {
            // Bind to territorial events
            TerritorialManager->OnTerritoryControlChanged.AddUObject(this, &UTGSpliceSubsystem::OnTerritorialControlChanged);
            TerritorialManager->OnTerritoryContested.AddUObject(this, &UTGSpliceSubsystem::OnTerritorialContested);
            TerritorialManager->OnInfluenceChanged.AddUObject(this, &UTGSpliceSubsystem::OnTerritorialInfluenceChanged);
            
            UE_LOG(LogTemp, Log, TEXT("UTGSpliceSubsystem: Territorial integration initialized"));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("UTGSpliceSubsystem: Failed to find UTGTerritorialManager"));
        }
    }
}

bool UTGSpliceSubsystem::TriggerTerritorialEvents(ETGSpliceTrigger Trigger, const FTGTerritorialEventContext& TerritorialContext)
{
    // Convert territorial context to standard context map
    TMap<FName, FString> Context = TerritorialContext.ToContextMap();
    
    // Use existing trigger system with enhanced context
    return TriggerEligibleEvents(Trigger, Context);
}

void UTGSpliceSubsystem::OnTerritorialControlChanged(int32 TerritoryId, int32 OldControllerFactionId, int32 NewControllerFactionId)
{
    // Build territorial context
    FTGTerritorialEventContext TerritorialContext = BuildTerritorialContext(TerritoryId, OldControllerFactionId, NewControllerFactionId);
    
    // Trigger territorial control change events
    TriggerTerritorialEvents(ETGSpliceTrigger::OnTerritorialControlChange, TerritorialContext);
    
    // Check for faction dominance (if new controller controls multiple strategic territories)
    TArray<int32> ConnectedTerritories = GetConnectedTerritories(TerritoryId);
    if (CheckFactionDominance(NewControllerFactionId, ConnectedTerritories))
    {
        TriggerTerritorialEvents(ETGSpliceTrigger::OnFactionDominance, TerritorialContext);
    }
    
    // Check for territorial loss (if old controller lost strategic territory)
    if (OldControllerFactionId != 0 && TerritorialContext.StrategicValue >= 5)
    {
        TriggerTerritorialEvents(ETGSpliceTrigger::OnTerritorialLoss, TerritorialContext);
    }
}

void UTGSpliceSubsystem::OnTerritorialContested(int32 TerritoryId, bool bContested)
{
    // Build territorial context for contested status change
    FTGTerritorialEventContext TerritorialContext = BuildTerritorialContext(TerritoryId, 0, 0);
    TerritorialContext.bIsContested = bContested;
    TerritorialContext.bWasContested = !bContested;
    
    // Trigger contested events
    TriggerTerritorialEvents(ETGSpliceTrigger::OnTerritorialContested, TerritorialContext);
}

void UTGSpliceSubsystem::OnTerritorialInfluenceChanged(int32 TerritoryId, int32 FactionId, int32 NewInfluenceLevel)
{
    // For now, we don't directly trigger events on influence changes
    // but this could be extended for more granular narrative events
    UE_LOG(LogTemp, VeryVerbose, TEXT("Territorial influence changed: Territory %d, Faction %d, Influence %d"), 
           TerritoryId, FactionId, NewInfluenceLevel);
}

FTGTerritorialEventContext UTGSpliceSubsystem::BuildTerritorialContext(int32 TerritoryId, int32 OldFactionId, int32 NewFactionId)
{
    FTGTerritorialEventContext Context;
    Context.TerritoryId = TerritoryId;
    Context.PreviousControllerFactionId = OldFactionId;
    Context.NewControllerFactionId = NewFactionId;
    
    if (TerritorialManager)
    {
        FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(TerritoryId);
        Context.TerritoryName = TerritoryData.TerritoryName;
        Context.TerritoryType = TerritoryData.TerritoryType;
        Context.StrategicValue = TerritoryData.StrategicValue;
        Context.ResourceMultiplier = TerritoryData.ResourceMultiplier;
        Context.bIsContested = TerritorialManager->IsTerritoryContested(TerritoryId);
        
        // Get connected territories for context
        Context.ConnectedTerritoryIds = GetConnectedTerritories(TerritoryId);
        
        // Fill in connected territory names
        for (int32 ConnectedId : Context.ConnectedTerritoryIds)
        {
            FTGTerritoryData ConnectedData = TerritorialManager->GetTerritoryData(ConnectedId);
            Context.ConnectedTerritoryNames.Add(ConnectedData.TerritoryName);
        }
    }
    
    return Context;
}

TArray<int32> UTGSpliceSubsystem::GetConnectedTerritories(int32 TerritoryId)
{
    TArray<int32> ConnectedTerritories;
    
    if (TerritorialManager)
    {
        // Get territory data to find parent/child relationships
        FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(TerritoryId);
        
        // Get all territories and find connections based on spatial proximity or hierarchy
        TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();
        
        for (const FTGTerritoryData& Territory : AllTerritories)
        {
            if (Territory.TerritoryId == TerritoryId) continue;
            
            // Consider territories connected if they share a parent or are spatially close
            if (Territory.ParentTerritoryId == TerritoryData.ParentTerritoryId ||
                Territory.TerritoryId == TerritoryData.ParentTerritoryId ||
                Territory.ParentTerritoryId == TerritoryId)
            {
                ConnectedTerritories.Add(Territory.TerritoryId);
            }
        }
    }
    
    return ConnectedTerritories;
}

bool UTGSpliceSubsystem::CheckFactionDominance(int32 FactionId, const TArray<int32>& TerritoryIds)
{
    if (!TerritorialManager || TerritoryIds.Num() == 0) return false;
    
    int32 ControlledCount = 0;
    int32 HighValueCount = 0;
    
    for (int32 TerritoryId : TerritoryIds)
    {
        int32 ControllingFaction = TerritorialManager->GetControllingFaction(TerritoryId);
        if (ControllingFaction == FactionId)
        {
            ControlledCount++;
            
            FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(TerritoryId);
            if (TerritoryData.StrategicValue >= 7)
            {
                HighValueCount++;
            }
        }
    }
    
    // Consider dominance if faction controls >50% of connected territories OR 2+ high-value territories
    return (ControlledCount > TerritoryIds.Num() / 2) || (HighValueCount >= 2);
}
