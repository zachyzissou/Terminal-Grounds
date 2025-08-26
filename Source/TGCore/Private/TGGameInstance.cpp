#include "TGGameInstance.h"
#include "Kismet/GameplayStatics.h"
#include "TGProfileSave.h"
#include "Trust/TGTrustSubsystem.h"
#include "Codex/TGCodexSubsystem.h"
#include "Engine/World.h"

static const FString SLOT_NAME = TEXT("TGProfile");
static const int32 SLOT_INDEX = 0;

void UTGGameInstance::Init()
{
    Super::Init();
    LoadProfile();
    SyncFromProfile();
}

void UTGGameInstance::Shutdown()
{
    SyncToProfile();
    SaveProfile();
    Super::Shutdown();
}

void UTGGameInstance::LoadProfile()
{
    if (USaveGame* Loaded = UGameplayStatics::LoadGameFromSlot(SLOT_NAME, SLOT_INDEX))
    {
        Profile = Cast<UTGProfileSave>(Loaded);
    }
    if (!Profile)
    {
        Profile = Cast<UTGProfileSave>(UGameplayStatics::CreateSaveGameObject(UTGProfileSave::StaticClass()));
    }
}

void UTGGameInstance::SaveProfile()
{
    if (Profile)
    {
        UGameplayStatics::SaveGameToSlot(Profile, SLOT_NAME, SLOT_INDEX);
    }
}

void UTGGameInstance::SyncFromProfile()
{
    if (!Profile) return;
    // Trust
    if (UTGTrustSubsystem* Trust = GetSubsystem<UTGTrustSubsystem>())
    {
        for (const FTGTrustRecord& Rec : Profile->TrustRecords)
        {
            // Rebuild records by applying neutral parlays; direct injection would require API exposure
            if (!Rec.PlayerA.IsEmpty() && !Rec.PlayerB.IsEmpty())
            {
                if (Rec.bPledgeActive)
                {
                    Trust->RecordPledge(Rec.PlayerA, Rec.PlayerB);
                }
                // Set baseline
                const float current = Trust->GetTrustIndex(Rec.PlayerA, Rec.PlayerB);
                const float delta = Rec.TrustIndex - current;
                if (!FMath::IsNearlyZero(delta))
                {
                    if (delta >= 0)
                        Trust->RecordParley(Rec.PlayerA, Rec.PlayerB, delta);
                    else
                        Trust->RecordBreach(Rec.PlayerA, Rec.PlayerB, -delta);
                }
            }
        }
    }

    // Codex
    if (UTGCodexSubsystem* Codex = GetSubsystem<UTGCodexSubsystem>())
    {
        for (const FName& Id : Profile->UnlockedCodexIds)
        {
            FTGCodexEntry Entry; Entry.EntryId = Id; Entry.Title = FText::FromName(Id);
            Codex->UnlockCodex(Entry);
        }
    }

    // Convoy index is world-scoped; set during first map load by a level blueprint or world subsystem bootstrap if desired.
}

void UTGGameInstance::SyncToProfile()
{
    if (!Profile) return;
    Profile->TrustRecords.Reset();

    if (UTGTrustSubsystem* Trust = GetSubsystem<UTGTrustSubsystem>())
    {
    TArray<FTGTrustRecord> All;
    Trust->GetAllRecords(All);
    Profile->TrustRecords = All;
    }

    if (UTGCodexSubsystem* Codex = GetSubsystem<UTGCodexSubsystem>())
    {
    Profile->UnlockedCodexIds.Reset();
    Codex->GetAllUnlockedIds(Profile->UnlockedCodexIds);
    }
}
