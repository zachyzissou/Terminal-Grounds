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
    OnExtractionWindow UMETA(DisplayName="Extraction Window"),
    // Territorial warfare triggers
    OnTerritorialControlChange UMETA(DisplayName="Territorial Control Change"),
    OnTerritorialContested UMETA(DisplayName="Territory Contested"),
    OnFactionDominance UMETA(DisplayName="Faction Dominance"),
    OnTerritorialLoss UMETA(DisplayName="Territorial Loss")
};

USTRUCT(BlueprintType)
struct FTGTerritorialEventContext
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    int32 TerritoryId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    FString TerritoryName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    FString TerritoryType;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    int32 PreviousControllerFactionId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    FString PreviousControllerFactionName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    int32 NewControllerFactionId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    FString NewControllerFactionName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    int32 StrategicValue = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    float ResourceMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    bool bWasContested = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    bool bIsContested = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    TArray<int32> ConnectedTerritoryIds;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Territorial")
    TArray<FString> ConnectedTerritoryNames;

    // Helper method to convert to context map for existing splice system
    TMap<FName, FString> ToContextMap() const;
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
    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    UFUNCTION(BlueprintCallable, Category="Splice")
    void RegisterDeck(UTGSpliceEventDeck* Deck);

    UFUNCTION(BlueprintCallable, Category="Splice")
    void ClearDecks();

    UFUNCTION(BlueprintCallable, Category="Splice")
    bool TriggerEligibleEvents(ETGSpliceTrigger Trigger, const TMap<FName, FString>& Context);

    /** Trigger territorial events with rich territorial context */
    UFUNCTION(BlueprintCallable, Category="Splice")
    bool TriggerTerritorialEvents(ETGSpliceTrigger Trigger, const FTGTerritorialEventContext& TerritorialContext);

    /** Initialize territorial system integration */
    UFUNCTION(BlueprintCallable, Category="Splice")
    void InitializeTerritorialIntegration();

    UPROPERTY(BlueprintAssignable, Category="Splice")
    FTGOnSpliceEventTriggered OnSpliceEventTriggered;

protected:
    TArray<TWeakObjectPtr<UTGSpliceEventDeck>> Decks;

    bool IsCardEligible(const FTGSpliceEventCard& Card, const TMap<FName, FString>& Context) const;
    const FTGSpliceOutcome* ChooseOutcome(const FTGSpliceEventCard& Card) const;

    /** Apply card outcome side effects into other systems (convoy economy, trust, codex). */
    void ApplyOutcome(const FTGSpliceOutcome& Outcome, const TMap<FName, FString>& Context);

private:
    // Territorial integration
    UPROPERTY()
    class UTGTerritorialManager* TerritorialManager;

    // Event handler delegates
    void OnTerritorialControlChanged(int32 TerritoryId, int32 OldControllerFactionId, int32 NewControllerFactionId);
    void OnTerritorialContested(int32 TerritoryId, bool bContested);
    void OnTerritorialInfluenceChanged(int32 TerritoryId, int32 FactionId, int32 NewInfluenceLevel);

    // Helper methods
    FTGTerritorialEventContext BuildTerritorialContext(int32 TerritoryId, int32 OldFactionId, int32 NewFactionId);
    TArray<int32> GetConnectedTerritories(int32 TerritoryId);
    bool CheckFactionDominance(int32 FactionId, const TArray<int32>& TerritoryIds);
};
