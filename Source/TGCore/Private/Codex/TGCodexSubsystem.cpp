#include "Codex/TGCodexSubsystem.h"

bool UTGCodexSubsystem::UnlockCodex(const FTGCodexEntry& Entry)
{
    if (Entry.EntryId.IsNone())
    {
        return false;
    }
    if (Unlocked.Contains(Entry.EntryId))
    {
        return false;
    }
    Unlocked.Add(Entry.EntryId, Entry);
    OnCodexUnlocked.Broadcast(Entry);
    return true;
}

bool UTGCodexSubsystem::IsUnlocked(FName EntryId) const
{
    return Unlocked.Contains(EntryId);
}

void UTGCodexSubsystem::GetUnlockedByCategory(ETGCodexCategory Category, TArray<FTGCodexEntry>& OutEntries) const
{
    for (const auto& KVP : Unlocked)
    {
        if (KVP.Value.Category == Category)
        {
            OutEntries.Add(KVP.Value);
        }
    }
}
