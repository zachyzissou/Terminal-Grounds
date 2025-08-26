#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGCodexPanelWidget.generated.h"

class UTGCodexSubsystem;
enum class ETGCodexCategory : uint8;
struct FTGCodexEntry;

UCLASS(BlueprintType)
class TGUI_API UTGCodexPanelWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Codex")
    ETGCodexCategory CategoryFilter;

    UFUNCTION(BlueprintCallable, Category="Codex")
    void Refresh();

    UFUNCTION(BlueprintImplementableEvent, Category="Codex")
    void OnCodexListUpdated(const TArray<FTGCodexEntry>& Entries);

protected:
    virtual void NativeConstruct() override;

private:
    UFUNCTION()
    void HandleCodexUnlocked(const FTGCodexEntry& Entry);

    TWeakObjectPtr<UTGCodexSubsystem> CodexSubsystem;
};
