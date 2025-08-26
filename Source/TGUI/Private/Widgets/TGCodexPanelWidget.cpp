#include "Widgets/TGCodexPanelWidget.h"
#include "Codex/TGCodexSubsystem.h"
#include "Engine/World.h"

void UTGCodexPanelWidget::NativeConstruct()
{
    Super::NativeConstruct();
    if (UWorld* World = GetWorld())
    {
        if (UTGCodexSubsystem* Codex = World->GetGameInstance() ? World->GetGameInstance()->GetSubsystem<UTGCodexSubsystem>() : nullptr)
        {
            CodexSubsystem = Codex;
            Codex->OnCodexUnlocked.AddDynamic(this, &UTGCodexPanelWidget::HandleCodexUnlocked);
        }
    }
    Refresh();
}

void UTGCodexPanelWidget::Refresh()
{
    if (!CodexSubsystem.IsValid()) return;
    TArray<FTGCodexEntry> Entries;
    CodexSubsystem->GetUnlockedByCategory(CategoryFilter, Entries);
    OnCodexListUpdated(Entries);
}

void UTGCodexPanelWidget::HandleCodexUnlocked(const FTGCodexEntry& Entry)
{
    if (!CodexSubsystem.IsValid()) return;
    Refresh();
}
