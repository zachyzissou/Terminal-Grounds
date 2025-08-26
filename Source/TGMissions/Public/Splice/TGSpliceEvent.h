#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Subsystems/WorldSubsystem.h"
#include "TGSpliceEvent.generated.h"

UENUM(BlueprintType)
enum class ETGSpliceTrigger : uint8
{
    OnMissionStart    UMETA(DisplayName="Mission Start"),
    OnObjectiveStart  UMETA(DisplayName="Objective Start"),
    OnObjectiveComplete UMETA(DisplayName="Objective Complete"),
    OnTimerThreshold  UMETA(DisplayName="Timer Threshold"),
    OnExtractionWindow UMETA(DisplayName="Extraction Window")
};

USTRUCT(BlueprintType)
struct FTGSpliceOutcome
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    FString OutcomeId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    int32 ReputationDelta = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    float ConvoyIntegrityDelta = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    TArray<FString> UnlockCodexIds;
};

USTRUCT(BlueprintType)
struct FTGSpliceEventCard
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    FString Id;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    FText DisplayName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    FText Description;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    TArray<ETGSpliceTrigger> Triggers;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    int32 Weight = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    TMap<FName, FString> Constraints; // e.g. RegionId, FactionId, Weather

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Splice")
    TArray<FTGSpliceOutcome> Outcomes;
};

UCLASS(BlueprintType)
class TGMISSIONS_API UTGSpliceEventDeck : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Splice")
    TArray<FTGSpliceEventCard> Cards;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FTGOnSpliceEventTriggered, const FTGSpliceEventCard&, Card, const FTGSpliceOutcome&, Outcome);

UCLASS()
class TGMISSIONS_API UTGSpliceSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Splice")
    void RegisterDeck(UTGSpliceEventDeck* Deck);

    UFUNCTION(BlueprintCallable, Category="Splice")
    void ClearDecks();

    UFUNCTION(BlueprintCallable, Category="Splice")
    bool TriggerEligibleEvents(ETGSpliceTrigger Trigger, const TMap<FName, FString>& Context);

    UPROPERTY(BlueprintAssignable, Category="Splice")
    FTGOnSpliceEventTriggered OnSpliceEventTriggered;

protected:
    TArray<TWeakObjectPtr<UTGSpliceEventDeck>> Decks;

    bool IsCardEligible(const FTGSpliceEventCard& Card, const TMap<FName, FString>& Context) const;
    const FTGSpliceOutcome* ChooseOutcome(const FTGSpliceEventCard& Card) const;

    /** Apply card outcome side effects into other systems (convoy economy, trust, codex). */
    void ApplyOutcome(const FTGSpliceOutcome& Outcome, const TMap<FName, FString>& Context);
};
