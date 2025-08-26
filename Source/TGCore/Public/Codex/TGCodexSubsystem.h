#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TGCodexSubsystem.generated.h"

UENUM(BlueprintType)
enum class ETGCodexCategory : uint8
{
    People,
    Places,
    Tech,
    Doctrine,
    Incidents
};

USTRUCT(BlueprintType)
struct FTGCodexEntry
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FName EntryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    ETGCodexCategory Category = ETGCodexCategory::People;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FText Title;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FText Body;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FTGOnCodexUnlocked, const FTGCodexEntry&, Entry);

/** Lightweight codex unlock and query subsystem. */
UCLASS(BlueprintType)
class TGCORE_API UTGCodexSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Codex")
    bool UnlockCodex(const FTGCodexEntry& Entry);

    UFUNCTION(BlueprintCallable, Category = "Codex")
    bool IsUnlocked(FName EntryId) const;

    UFUNCTION(BlueprintCallable, Category = "Codex")
    void GetUnlockedByCategory(ETGCodexCategory Category, TArray<FTGCodexEntry>& OutEntries) const;

    UPROPERTY(BlueprintAssignable, Category = "Codex")
    FTGOnCodexUnlocked OnCodexUnlocked;

private:
    UPROPERTY()
    TMap<FName, FTGCodexEntry> Unlocked;

public:
    UFUNCTION(BlueprintCallable, Category = "Codex")
    void GetAllUnlockedIds(TArray<FName>& OutIds) const { Unlocked.GetKeys(OutIds); }
};
