#include "Trust/TGTrustSubsystem.h"

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
