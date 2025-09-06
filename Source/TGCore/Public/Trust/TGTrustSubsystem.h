#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "TGTrustSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FTGTrustRecord
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString PlayerA;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString PlayerB;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float TrustIndex = 0.f; // -1..+1 band

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bPledgeActive = false;
    
    // Siege-specific trust data
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float SiegeTrustBonus = 0.f;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FDateTime LastSiegeInteraction;
};

// Faction relationship structure
USTRUCT(BlueprintType)
struct FTGFactionRelation
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString FactionA;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString FactionB;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float RelationIndex = 0.f; // -1 (hostile) to +1 (allied)
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bSiegeAlliance = false;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float AllianeDuration = 0.f; // Seconds remaining
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 SharedSiegeVictories = 0;
    
    // Territorial trust data
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float TerritorialCooperationScore = 0.f; // Tracks territorial cooperation history
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 TerritorialBetrayalCount = 0; // Number of territorial betrayals
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float LastTerritorialAction = 0.f; // Hours since last territorial interaction
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 SharedExtractionAssists = 0; // Successful extraction assistance count
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float TerritorialTrustDecayRate = 1.0f; // Custom decay rate based on territorial activity
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FTGOnTrustChanged, const FString&, PlayerA, const FString&, PlayerB, float, NewTrust);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FTGOnFactionRelationChanged, const FString&, FactionA, const FString&, FactionB, float, NewRelation);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FTGOnSiegeAllianceFormed, const FString&, FactionA, const FString&, FactionB);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FTGOnSiegeAllianceBroken, const FString&, FactionA, const FString&, FactionB);

// Territorial trust event delegates
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FTGOnTerritorialCooperation, const FString&, PlayerA, const FString&, PlayerB, int32, TerritoryID, float, TrustGain);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FTGOnTerritorialBetrayal, const FString&, PlayerA, const FString&, PlayerB, int32, TerritoryID, float, TrustLoss);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FTGOnExtractionAssistance, const FString&, Helper, const FString&, Assisted, float, TrustBonus);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FTGOnBoundaryRespect, const FString&, PlayerA, const FString&, PlayerB, int32, NeutralZoneID, float, TrustGain);

UCLASS()
class TGCORE_API UTGTrustSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Trust")
    void RecordPledge(const FString& PlayerA, const FString& PlayerB);

    UFUNCTION(BlueprintCallable, Category="Trust")
    void RecordParley(const FString& PlayerA, const FString& PlayerB, float TrustDelta = 0.05f);

    UFUNCTION(BlueprintCallable, Category="Trust")
    void RecordBreach(const FString& PlayerA, const FString& PlayerB, float TrustPenalty = 0.4f);

    UFUNCTION(BlueprintCallable, Category="Trust")
    float GetTrustIndex(const FString& PlayerA, const FString& PlayerB) const;
    
    // Siege-specific trust functions
    UFUNCTION(BlueprintCallable, Category="Trust|Siege")
    void ApplySiegeTrustBonus(const FString& PlayerA, const FString& PlayerB, float Bonus, float Duration);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Siege")
    float GetEffectiveTrustForSiege(const FString& PlayerA, const FString& PlayerB) const;
    
    // Faction relationship functions
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    void SetFactionRelation(const FString& FactionA, const FString& FactionB, float RelationValue);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    float GetFactionRelation(const FString& FactionA, const FString& FactionB) const;
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    void FormSiegeAlliance(const FString& FactionA, const FString& FactionB, float Duration);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    void BreakSiegeAlliance(const FString& FactionA, const FString& FactionB);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    bool ArFactionsAllied(const FString& FactionA, const FString& FactionB) const;
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    TArray<FString> GetAlliedFactions(const FString& Faction) const;
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    void RecordSiegeVictory(const FString& FactionA, const FString& FactionB);
    
    // Territorial trust functions
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    void RecordTerritorialCooperation(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustBonus = 0.08f);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    void RecordTerritorialBetrayal(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustPenalty = 0.6f);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    void RecordBoundaryRespect(const FString& PlayerA, const FString& PlayerB, int32 NeutralZoneID, float TrustGain = 0.04f);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    void RecordSupplyRouteProtection(const FString& ProtectorPlayer, const FString& ConvoyPlayer, float TrustBonus = 0.06f);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    void RecordExtractionAssistance(const FString& HelperPlayer, const FString& AssistedPlayer, int32 ExtractionPointID, float TrustBonus = 0.10f);
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    float GetTerritorialTrustModifier(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID) const;
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    bool ShouldApplyTerritorialDecay(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID) const;
    
    UFUNCTION(BlueprintCallable, Category="Trust|Territorial")
    void ApplyTerritorialContext(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, int32 FactionControllingTerritory);
    
    UFUNCTION(BlueprintPure, Category="Trust|Territorial")
    int32 GetTerritorialCooperationScore(const FString& PlayerA, const FString& PlayerB) const;
    
    UFUNCTION(BlueprintPure, Category="Trust|Territorial")
    int32 GetTerritorialBetrayalCount(const FString& PlayerA, const FString& PlayerB) const;

    UPROPERTY(BlueprintAssignable, Category="Trust")
    FTGOnTrustChanged OnTrustChanged;
    
    UPROPERTY(BlueprintAssignable, Category="Trust|Faction")
    FTGOnFactionRelationChanged OnFactionRelationChanged;
    
    UPROPERTY(BlueprintAssignable, Category="Trust|Faction")
    FTGOnSiegeAllianceFormed OnSiegeAllianceFormed;
    
    UPROPERTY(BlueprintAssignable, Category="Trust|Faction")
    FTGOnSiegeAllianceBroken OnSiegeAllianceBroken;
    
    // Territorial trust events
    UPROPERTY(BlueprintAssignable, Category="Trust|Territorial")
    FTGOnTerritorialCooperation OnTerritorialCooperation;
    
    UPROPERTY(BlueprintAssignable, Category="Trust|Territorial")
    FTGOnTerritorialBetrayal OnTerritorialBetrayal;
    
    UPROPERTY(BlueprintAssignable, Category="Trust|Territorial")
    FTGOnExtractionAssistance OnExtractionAssistance;
    
    UPROPERTY(BlueprintAssignable, Category="Trust|Territorial")
    FTGOnBoundaryRespect OnBoundaryRespect;

protected:
    UPROPERTY()
    TArray<FTGTrustRecord> Records;
    
    UPROPERTY()
    TArray<FTGFactionRelation> FactionRelations;

    FTGTrustRecord* FindRecordMutable(const FString& PlayerA, const FString& PlayerB);
    const FTGTrustRecord* FindRecord(const FString& PlayerA, const FString& PlayerB) const;
    void BroadcastTrust(const FString& PlayerA, const FString& PlayerB, float NewTrust);
    
    FTGFactionRelation* FindFactionRelationMutable(const FString& FactionA, const FString& FactionB);
    const FTGFactionRelation* FindFactionRelation(const FString& FactionA, const FString& FactionB) const;
    void BroadcastFactionRelation(const FString& FactionA, const FString& FactionB, float NewRelation);
    
    // Siege trust decay system
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    void ProcessSiegeTrustDecay(float DeltaTime);
    void ProcessAllianceDuration(float DeltaTime);
    
    // Territorial trust decay system
    void ProcessTerritorialTrustDecay(float DeltaTime);
    void UpdateTerritorialContextModifiers();
    
    // Territorial trust calculation helpers
    float CalculateTerritorialTrustDecayRate(const FTGTrustRecord& Record, int32 TerritoryID) const;
    float GetFactionTerritorialBonus(const FString& PlayerFaction, int32 TerritoryControllingFaction) const;
    bool IsTerritoryContested(int32 TerritoryID) const;
    
    // Integration with territorial manager
    class UTGTerritorialManager* GetTerritorialManager() const;
    
    FTimerHandle SiegeTrustDecayTimer;

public:
    UFUNCTION(BlueprintCallable, Category="Trust")
    void GetAllRecords(TArray<FTGTrustRecord>& OutRecords) const { OutRecords = Records; }
    
    UFUNCTION(BlueprintCallable, Category="Trust|Faction")
    void GetAllFactionRelations(TArray<FTGFactionRelation>& OutRelations) const { OutRelations = FactionRelations; }
};
