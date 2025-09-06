#include "Trust/TGTrustSubsystem.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "World/TGTerritorialManager.h"
#include "Subsystems/SubsystemBlueprintLibrary.h"

FTGTrustRecord* UTGTrustSubsystem::FindRecordMutable(const FString& PlayerA, const FString& PlayerB)
{
    for (FTGTrustRecord& R : Records)
    {
        if ((R.PlayerA == PlayerA && R.PlayerB == PlayerB) || (R.PlayerA == PlayerB && R.PlayerB == PlayerA))
        {
            return &R;
        }
    }
    return nullptr;
}

const FTGTrustRecord* UTGTrustSubsystem::FindRecord(const FString& PlayerA, const FString& PlayerB) const
{
    for (const FTGTrustRecord& R : Records)
    {
        if ((R.PlayerA == PlayerA && R.PlayerB == PlayerB) || (R.PlayerA == PlayerB && R.PlayerB == PlayerA))
        {
            return &R;
        }
    }
    return nullptr;
}

void UTGTrustSubsystem::BroadcastTrust(const FString& PlayerA, const FString& PlayerB, float NewTrust)
{
    OnTrustChanged.Broadcast(PlayerA, PlayerB, NewTrust);
}

void UTGTrustSubsystem::RecordPledge(const FString& PlayerA, const FString& PlayerB)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = 0.1f;
        NewRec.bPledgeActive = true;
        Records.Add(MoveTemp(NewRec));
        BroadcastTrust(PlayerA, PlayerB, 0.1f);
        return;
    }
    Rec->bPledgeActive = true;
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex + 0.05f, -1.f, 1.f);
    BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
}

void UTGTrustSubsystem::RecordParley(const FString& PlayerA, const FString& PlayerB, float TrustDelta)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = FMath::Clamp(TrustDelta, -1.f, 1.f);
        NewRec.bPledgeActive = false;
        Records.Add(MoveTemp(NewRec));
        BroadcastTrust(PlayerA, PlayerB, TrustDelta);
        return;
    }
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex + TrustDelta, -1.f, 1.f);
    BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
}

void UTGTrustSubsystem::RecordBreach(const FString& PlayerA, const FString& PlayerB, float TrustPenalty)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = FMath::Clamp(-FMath::Abs(TrustPenalty), -1.f, 1.f);
        NewRec.bPledgeActive = false;
        Records.Add(MoveTemp(NewRec));
        BroadcastTrust(PlayerA, PlayerB, NewRec.TrustIndex);
        return;
    }
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex - FMath::Abs(TrustPenalty), -1.f, 1.f);
    Rec->bPledgeActive = false;
    BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
}

float UTGTrustSubsystem::GetTrustIndex(const FString& PlayerA, const FString& PlayerB) const
{
    const FTGTrustRecord* Rec = FindRecord(PlayerA, PlayerB);
    return Rec ? Rec->TrustIndex : 0.f;
}

void UTGTrustSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // Start siege trust decay timer (every 10 seconds)
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(SiegeTrustDecayTimer, 
            FTimerDelegate::CreateUObject(this, &UTGTrustSubsystem::ProcessSiegeTrustDecay, 10.0f), 
            10.0f, true);
    }
}

void UTGTrustSubsystem::ApplySiegeTrustBonus(const FString& PlayerA, const FString& PlayerB, float Bonus, float Duration)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = 0.0f;
        NewRec.SiegeTrustBonus = FMath::Clamp(Bonus, 0.0f, 0.5f);
        NewRec.LastSiegeInteraction = FDateTime::Now() + FTimespan::FromSeconds(Duration);
        Records.Add(MoveTemp(NewRec));
        return;
    }
    
    Rec->SiegeTrustBonus = FMath::Clamp(Bonus, 0.0f, 0.5f);
    Rec->LastSiegeInteraction = FDateTime::Now() + FTimespan::FromSeconds(Duration);
    BroadcastTrust(PlayerA, PlayerB, GetEffectiveTrustForSiege(PlayerA, PlayerB));
}

float UTGTrustSubsystem::GetEffectiveTrustForSiege(const FString& PlayerA, const FString& PlayerB) const
{
    const FTGTrustRecord* Rec = FindRecord(PlayerA, PlayerB);
    if (!Rec)
    {
        return 0.0f;
    }
    
    float EffectiveTrust = Rec->TrustIndex;
    
    // Apply siege bonus if still active
    if (FDateTime::Now() < Rec->LastSiegeInteraction)
    {
        EffectiveTrust += Rec->SiegeTrustBonus;
    }
    
    return FMath::Clamp(EffectiveTrust, -1.0f, 1.0f);
}

void UTGTrustSubsystem::SetFactionRelation(const FString& FactionA, const FString& FactionB, float RelationValue)
{
    if (FactionA == FactionB) return;
    
    FTGFactionRelation* Rel = FindFactionRelationMutable(FactionA, FactionB);
    if (!Rel)
    {
        FTGFactionRelation NewRel;
        NewRel.FactionA = FactionA;
        NewRel.FactionB = FactionB;
        NewRel.RelationIndex = FMath::Clamp(RelationValue, -1.0f, 1.0f);
        FactionRelations.Add(MoveTemp(NewRel));
        BroadcastFactionRelation(FactionA, FactionB, RelationValue);
        return;
    }
    
    float OldRelation = Rel->RelationIndex;
    Rel->RelationIndex = FMath::Clamp(RelationValue, -1.0f, 1.0f);
    
    if (OldRelation != Rel->RelationIndex)
    {
        BroadcastFactionRelation(FactionA, FactionB, Rel->RelationIndex);
    }
}

float UTGTrustSubsystem::GetFactionRelation(const FString& FactionA, const FString& FactionB) const
{
    if (FactionA == FactionB) return 1.0f;
    
    const FTGFactionRelation* Rel = FindFactionRelation(FactionA, FactionB);
    return Rel ? Rel->RelationIndex : 0.0f;
}

void UTGTrustSubsystem::FormSiegeAlliance(const FString& FactionA, const FString& FactionB, float Duration)
{
    if (FactionA == FactionB) return;
    
    FTGFactionRelation* Rel = FindFactionRelationMutable(FactionA, FactionB);
    if (!Rel)
    {
        FTGFactionRelation NewRel;
        NewRel.FactionA = FactionA;
        NewRel.FactionB = FactionB;
        NewRel.RelationIndex = FMath::Max(0.3f, NewRel.RelationIndex); // Minimum positive relation for alliance
        NewRel.bSiegeAlliance = true;
        NewRel.AllianeDuration = Duration;
        FactionRelations.Add(MoveTemp(NewRel));
        OnSiegeAllianceFormed.Broadcast(FactionA, FactionB);
        return;
    }
    
    if (!Rel->bSiegeAlliance)
    {
        Rel->bSiegeAlliance = true;
        Rel->AllianeDuration = Duration;
        Rel->RelationIndex = FMath::Max(0.3f, Rel->RelationIndex);
        OnSiegeAllianceFormed.Broadcast(FactionA, FactionB);
    }
    else
    {
        // Extend existing alliance
        Rel->AllianeDuration = FMath::Max(Rel->AllianeDuration, Duration);
    }
}

void UTGTrustSubsystem::BreakSiegeAlliance(const FString& FactionA, const FString& FactionB)
{
    FTGFactionRelation* Rel = FindFactionRelationMutable(FactionA, FactionB);
    if (Rel && Rel->bSiegeAlliance)
    {
        Rel->bSiegeAlliance = false;
        Rel->AllianeDuration = 0.0f;
        Rel->RelationIndex = FMath::Max(-0.2f, Rel->RelationIndex - 0.3f); // Penalty for breaking alliance
        OnSiegeAllianceBroken.Broadcast(FactionA, FactionB);
    }
}

bool UTGTrustSubsystem::ArFactionsAllied(const FString& FactionA, const FString& FactionB) const
{
    if (FactionA == FactionB) return true;
    
    const FTGFactionRelation* Rel = FindFactionRelation(FactionA, FactionB);
    return Rel && Rel->bSiegeAlliance && Rel->AllianeDuration > 0.0f;
}

TArray<FString> UTGTrustSubsystem::GetAlliedFactions(const FString& Faction) const
{
    TArray<FString> Allies;
    
    for (const FTGFactionRelation& Rel : FactionRelations)
    {
        if (Rel.bSiegeAlliance && Rel.AllianeDuration > 0.0f)
        {
            if (Rel.FactionA == Faction)
            {
                Allies.Add(Rel.FactionB);
            }
            else if (Rel.FactionB == Faction)
            {
                Allies.Add(Rel.FactionA);
            }
        }
    }
    
    return Allies;
}

void UTGTrustSubsystem::RecordSiegeVictory(const FString& FactionA, const FString& FactionB)
{
    FTGFactionRelation* Rel = FindFactionRelationMutable(FactionA, FactionB);
    if (!Rel)
    {
        FTGFactionRelation NewRel;
        NewRel.FactionA = FactionA;
        NewRel.FactionB = FactionB;
        NewRel.SharedSiegeVictories = 1;
        NewRel.RelationIndex = 0.1f; // Small positive boost
        FactionRelations.Add(MoveTemp(NewRel));
        return;
    }
    
    Rel->SharedSiegeVictories++;
    if (Rel->bSiegeAlliance)
    {
        Rel->RelationIndex = FMath::Min(1.0f, Rel->RelationIndex + 0.05f); // Reward for shared victories
    }
}

FTGFactionRelation* UTGTrustSubsystem::FindFactionRelationMutable(const FString& FactionA, const FString& FactionB)
{
    for (FTGFactionRelation& R : FactionRelations)
    {
        if ((R.FactionA == FactionA && R.FactionB == FactionB) || (R.FactionA == FactionB && R.FactionB == FactionA))
        {
            return &R;
        }
    }
    return nullptr;
}

const FTGFactionRelation* UTGTrustSubsystem::FindFactionRelation(const FString& FactionA, const FString& FactionB) const
{
    for (const FTGFactionRelation& R : FactionRelations)
    {
        if ((R.FactionA == FactionA && R.FactionB == FactionB) || (R.FactionA == FactionB && R.FactionB == FactionA))
        {
            return &R;
        }
    }
    return nullptr;
}

void UTGTrustSubsystem::BroadcastFactionRelation(const FString& FactionA, const FString& FactionB, float NewRelation)
{
    OnFactionRelationChanged.Broadcast(FactionA, FactionB, NewRelation);
}

void UTGTrustSubsystem::ProcessSiegeTrustDecay(float DeltaTime)
{
    FDateTime Now = FDateTime::Now();
    
    // Decay siege trust bonuses
    for (FTGTrustRecord& Rec : Records)
    {
        if (Rec.SiegeTrustBonus > 0.0f && Now > Rec.LastSiegeInteraction)
        {
            Rec.SiegeTrustBonus = 0.0f;
        }
    }
    
    ProcessAllianceDuration(DeltaTime);
    ProcessTerritorialTrustDecay(DeltaTime);
}

void UTGTrustSubsystem::ProcessAllianceDuration(float DeltaTime)
{
    TArray<FTGFactionRelation> ExpiredAlliances;
    
    for (FTGFactionRelation& Rel : FactionRelations)
    {
        if (Rel.bSiegeAlliance && Rel.AllianeDuration > 0.0f)
        {
            Rel.AllianeDuration -= DeltaTime;
            
            if (Rel.AllianeDuration <= 0.0f)
            {
                Rel.bSiegeAlliance = false;
                ExpiredAlliances.Add(Rel);
            }
        }
    }
    
    // Broadcast expired alliances
    for (const FTGFactionRelation& ExpiredRel : ExpiredAlliances)
    {
        OnSiegeAllianceBroken.Broadcast(ExpiredRel.FactionA, ExpiredRel.FactionB);
    }
}

// Territorial Trust System Implementation

void UTGTrustSubsystem::RecordTerritorialCooperation(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustBonus)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = FMath::Clamp(TrustBonus, 0.0f, 1.0f);
        NewRec.TerritorialCooperationScore = 1.0f;
        NewRec.LastTerritorialAction = 0.0f;
        Records.Add(MoveTemp(NewRec));
        OnTerritorialCooperation.Broadcast(PlayerA, PlayerB, TerritoryID, TrustBonus);
        BroadcastTrust(PlayerA, PlayerB, TrustBonus);
        return;
    }
    
    // Apply territorial context modifier
    float ContextualBonus = TrustBonus;
    if (UTGTerritorialManager* TerritorialManager = GetTerritorialManager())
    {
        // Bonus cooperation in contested territories
        if (TerritorialManager->IsTerritoryContested(TerritoryID))
        {
            ContextualBonus *= 1.5f; // 50% bonus in contested zones
        }
        
        // Reduced bonus in enemy territory (higher risk)
        int32 ControllingFaction = TerritorialManager->GetControllingFaction(TerritoryID);
        if (ControllingFaction > 0) // Enemy controlled
        {
            ContextualBonus *= 1.25f; // 25% bonus for cooperation in enemy territory
        }
    }
    
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex + ContextualBonus, -1.0f, 1.0f);
    Rec->TerritorialCooperationScore += 1.0f;
    Rec->LastTerritorialAction = 0.0f; // Reset decay timer
    
    OnTerritorialCooperation.Broadcast(PlayerA, PlayerB, TerritoryID, ContextualBonus);
    BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
}

void UTGTrustSubsystem::RecordTerritorialBetrayal(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustPenalty)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = -FMath::Abs(TrustPenalty);
        NewRec.TerritorialBetrayalCount = 1;
        NewRec.LastTerritorialAction = 0.0f;
        NewRec.TerritorialTrustDecayRate = 2.0f; // Faster decay after betrayal
        Records.Add(MoveTemp(NewRec));
        OnTerritorialBetrayal.Broadcast(PlayerA, PlayerB, TerritoryID, TrustPenalty);
        BroadcastTrust(PlayerA, PlayerB, NewRec.TrustIndex);
        return;
    }
    
    // Territorial betrayals have severe consequences
    float ContextualPenalty = TrustPenalty;
    if (UTGTerritorialManager* TerritorialManager = GetTerritorialManager())
    {
        // Severe penalty for betrayal in allied territory
        int32 ControllingFaction = TerritorialManager->GetControllingFaction(TerritoryID);
        if (ControllingFaction > 0) // In controlled territory
        {
            ContextualPenalty *= 1.8f; // 80% more severe in controlled territory
        }
    }
    
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex - ContextualPenalty, -1.0f, 1.0f);
    Rec->TerritorialBetrayalCount++;
    Rec->bPledgeActive = false; // Betrayal breaks any active pledges
    Rec->LastTerritorialAction = 0.0f;
    Rec->TerritorialTrustDecayRate = FMath::Min(5.0f, 1.0f + (Rec->TerritorialBetrayalCount * 0.5f)); // Escalating decay
    
    OnTerritorialBetrayal.Broadcast(PlayerA, PlayerB, TerritoryID, ContextualPenalty);
    BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
}

void UTGTrustSubsystem::RecordBoundaryRespect(const FString& PlayerA, const FString& PlayerB, int32 NeutralZoneID, float TrustGain)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = PlayerA;
        NewRec.PlayerB = PlayerB;
        NewRec.TrustIndex = FMath::Clamp(TrustGain, 0.0f, 1.0f);
        NewRec.TerritorialCooperationScore = 0.5f; // Neutral respect
        Records.Add(MoveTemp(NewRec));
        OnBoundaryRespect.Broadcast(PlayerA, PlayerB, NeutralZoneID, TrustGain);
        BroadcastTrust(PlayerA, PlayerB, TrustGain);
        return;
    }
    
    // Small but consistent trust gain for respecting boundaries
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex + TrustGain, -1.0f, 1.0f);
    Rec->TerritorialCooperationScore += 0.25f; // Small cooperation score increase
    Rec->LastTerritorialAction = 0.0f;
    
    OnBoundaryRespect.Broadcast(PlayerA, PlayerB, NeutralZoneID, TrustGain);
    BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
}

void UTGTrustSubsystem::RecordSupplyRouteProtection(const FString& ProtectorPlayer, const FString& ConvoyPlayer, float TrustBonus)
{
    FTGTrustRecord* Rec = FindRecordMutable(ProtectorPlayer, ConvoyPlayer);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = ProtectorPlayer;
        NewRec.PlayerB = ConvoyPlayer;
        NewRec.TrustIndex = FMath::Clamp(TrustBonus, 0.0f, 1.0f);
        NewRec.TerritorialCooperationScore = 1.5f; // High cooperation for escort
        Records.Add(MoveTemp(NewRec));
        BroadcastTrust(ProtectorPlayer, ConvoyPlayer, TrustBonus);
        return;
    }
    
    // Supply protection is highly valued
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex + TrustBonus, -1.0f, 1.0f);
    Rec->TerritorialCooperationScore += 1.5f;
    Rec->LastTerritorialAction = 0.0f;
    
    BroadcastTrust(ProtectorPlayer, ConvoyPlayer, Rec->TrustIndex);
}

void UTGTrustSubsystem::RecordExtractionAssistance(const FString& HelperPlayer, const FString& AssistedPlayer, int32 ExtractionPointID, float TrustBonus)
{
    FTGTrustRecord* Rec = FindRecordMutable(HelperPlayer, AssistedPlayer);
    if (!Rec)
    {
        FTGTrustRecord NewRec;
        NewRec.PlayerA = HelperPlayer;
        NewRec.PlayerB = AssistedPlayer;
        NewRec.TrustIndex = FMath::Clamp(TrustBonus, 0.0f, 1.0f);
        NewRec.SharedExtractionAssists = 1;
        NewRec.TerritorialCooperationScore = 2.0f; // Very high cooperation for extraction help
        Records.Add(MoveTemp(NewRec));
        OnExtractionAssistance.Broadcast(HelperPlayer, AssistedPlayer, TrustBonus);
        BroadcastTrust(HelperPlayer, AssistedPlayer, TrustBonus);
        return;
    }
    
    // Extraction assistance is the highest form of territorial cooperation
    float ContextualBonus = TrustBonus;
    if (UTGTerritorialManager* TerritorialManager = GetTerritorialManager())
    {
        // Huge bonus for helping in contested extraction zones
        if (TerritorialManager->IsTerritoryContested(ExtractionPointID))
        {
            ContextualBonus *= 2.0f; // Double bonus in contested extraction zones
        }
    }
    
    Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex + ContextualBonus, -1.0f, 1.0f);
    Rec->SharedExtractionAssists++;
    Rec->TerritorialCooperationScore += 2.0f;
    Rec->LastTerritorialAction = 0.0f;
    
    // Extraction assistance can restore pledges if trust is high enough
    if (Rec->TrustIndex > 0.5f && Rec->SharedExtractionAssists >= 3)
    {
        Rec->bPledgeActive = true;
    }
    
    OnExtractionAssistance.Broadcast(HelperPlayer, AssistedPlayer, ContextualBonus);
    BroadcastTrust(HelperPlayer, AssistedPlayer, Rec->TrustIndex);
}

float UTGTrustSubsystem::GetTerritorialTrustModifier(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID) const
{
    const FTGTrustRecord* Rec = FindRecord(PlayerA, PlayerB);
    if (!Rec)
    {
        return 1.0f; // No modifier if no relationship exists
    }
    
    float BaseModifier = 1.0f + (Rec->TerritorialCooperationScore * 0.1f); // 10% per cooperation point
    
    // Penalty for betrayals
    if (Rec->TerritorialBetrayalCount > 0)
    {
        BaseModifier *= FMath::Max(0.3f, 1.0f - (Rec->TerritorialBetrayalCount * 0.15f)); // 15% penalty per betrayal
    }
    
    // Bonus for extraction assists
    if (Rec->SharedExtractionAssists > 0)
    {
        BaseModifier *= (1.0f + (Rec->SharedExtractionAssists * 0.05f)); // 5% bonus per assist
    }
    
    return FMath::Clamp(BaseModifier, 0.2f, 3.0f); // Clamp between 20% and 300%
}

bool UTGTrustSubsystem::ShouldApplyTerritorialDecay(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID) const
{
    const FTGTrustRecord* Rec = FindRecord(PlayerA, PlayerB);
    if (!Rec)
    {
        return false;
    }
    
    // No decay if recent territorial activity
    if (Rec->LastTerritorialAction < 24.0f) // Less than 24 hours
    {
        return false;
    }
    
    // Always apply decay if there have been betrayals
    if (Rec->TerritorialBetrayalCount > 0)
    {
        return true;
    }
    
    // Apply decay in contested territories
    if (UTGTerritorialManager* TerritorialManager = GetTerritorialManager())
    {
        return TerritorialManager->IsTerritoryContested(TerritoryID);
    }
    
    return false;
}

void UTGTrustSubsystem::ApplyTerritorialContext(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, int32 FactionControllingTerritory)
{
    FTGTrustRecord* Rec = FindRecordMutable(PlayerA, PlayerB);
    if (!Rec)
    {
        return;
    }
    
    // Apply faction-specific territorial bonuses
    float FactionBonus = GetFactionTerritorialBonus(PlayerA, FactionControllingTerritory);
    if (FactionBonus != 1.0f)
    {
        Rec->TrustIndex = FMath::Clamp(Rec->TrustIndex * FactionBonus, -1.0f, 1.0f);
        BroadcastTrust(PlayerA, PlayerB, Rec->TrustIndex);
    }
}

int32 UTGTrustSubsystem::GetTerritorialCooperationScore(const FString& PlayerA, const FString& PlayerB) const
{
    const FTGTrustRecord* Rec = FindRecord(PlayerA, PlayerB);
    return Rec ? FMath::RoundToInt(Rec->TerritorialCooperationScore) : 0;
}

int32 UTGTrustSubsystem::GetTerritorialBetrayalCount(const FString& PlayerA, const FString& PlayerB) const
{
    const FTGTrustRecord* Rec = FindRecord(PlayerA, PlayerB);
    return Rec ? Rec->TerritorialBetrayalCount : 0;
}

void UTGTrustSubsystem::ProcessTerritorialTrustDecay(float DeltaTime)
{
    FDateTime Now = FDateTime::Now();
    
    for (FTGTrustRecord& Rec : Records)
    {
        // Update time since last territorial action
        Rec.LastTerritorialAction += (DeltaTime / 3600.0f); // Convert to hours
        
        // Apply territorial trust decay if conditions are met
        if (Rec.LastTerritorialAction > 48.0f) // After 48 hours of inactivity
        {
            float DecayAmount = (DeltaTime / 3600.0f) * 0.001f * Rec.TerritorialTrustDecayRate; // Base 0.1% per hour
            
            if (Rec.TrustIndex > 0.0f)
            {
                Rec.TrustIndex = FMath::Max(0.0f, Rec.TrustIndex - DecayAmount);
            }
            else if (Rec.TrustIndex < 0.0f)
            {
                // Negative trust decays towards zero more slowly
                Rec.TrustIndex = FMath::Min(0.0f, Rec.TrustIndex + (DecayAmount * 0.5f));
            }
        }
        
        // Slowly reduce cooperation scores over time
        if (Rec.LastTerritorialAction > 72.0f) // After 72 hours
        {
            Rec.TerritorialCooperationScore = FMath::Max(0.0f, Rec.TerritorialCooperationScore - (DeltaTime * 0.01f));
        }
    }
}

void UTGTrustSubsystem::UpdateTerritorialContextModifiers()
{
    // Update territorial context for all trust relationships
    // Called periodically to adjust trust based on changing territorial control
    
    UTGTerritorialManager* TerritorialManager = GetTerritorialManager();
    if (!TerritorialManager)
    {
        return;
    }
    
    // This would typically be called when territorial control changes
    // Implementation depends on integration with TerritorialManager events
}

float UTGTrustSubsystem::CalculateTerritorialTrustDecayRate(const FTGTrustRecord& Record, int32 TerritoryID) const
{
    float BaseDecayRate = Record.TerritorialTrustDecayRate;
    
    // Faster decay in contested territories
    if (IsTerritoryContested(TerritoryID))
    {
        BaseDecayRate *= 1.5f;
    }
    
    // Slower decay for players with high cooperation scores
    if (Record.TerritorialCooperationScore > 5.0f)
    {
        BaseDecayRate *= 0.7f;
    }
    
    return BaseDecayRate;
}

float UTGTrustSubsystem::GetFactionTerritorialBonus(const FString& PlayerFaction, int32 TerritoryControllingFaction) const
{
    // Faction-specific territorial trust bonuses
    // These could be configured per faction based on lore and gameplay balance
    
    if (PlayerFaction.IsEmpty() || TerritoryControllingFaction <= 0)
    {
        return 1.0f;
    }
    
    // Example faction bonuses (these would be data-driven in a real implementation)
    // Directorate: Bonus in corporate territories
    // Free77: Bonus in contested zones
    // NomadClans: Bonus in wasteland territories
    // etc.
    
    return 1.0f; // Default no bonus
}

bool UTGTrustSubsystem::IsTerritoryContested(int32 TerritoryID) const
{
    UTGTerritorialManager* TerritorialManager = GetTerritorialManager();
    return TerritorialManager ? TerritorialManager->IsTerritoryContested(TerritoryID) : false;
}

UTGTerritorialManager* UTGTrustSubsystem::GetTerritorialManager() const
{
    if (UWorld* World = GetWorld())
    {
        return World->GetSubsystem<UTGTerritorialManager>();
    }
    return nullptr;
}
