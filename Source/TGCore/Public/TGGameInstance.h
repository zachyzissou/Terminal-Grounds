#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "TGGameInstance.generated.h"

class UTGProfileSave;
class UTGTrustSubsystem;
class UTGCodexSubsystem;

UCLASS()
class TGCORE_API UTGGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    UPROPERTY()
    UTGProfileSave* Profile = nullptr;

    void LoadProfile();
    void SaveProfile();
    void SyncFromProfile();
    void SyncToProfile();
};
