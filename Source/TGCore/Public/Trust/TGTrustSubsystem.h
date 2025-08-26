#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
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
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FTGOnTrustChanged, const FString&, PlayerA, const FString&, PlayerB, float, NewTrust);

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

    UPROPERTY(BlueprintAssignable, Category="Trust")
    FTGOnTrustChanged OnTrustChanged;

protected:
    UPROPERTY()
    TArray<FTGTrustRecord> Records;

    FTGTrustRecord* FindRecordMutable(const FString& PlayerA, const FString& PlayerB);
    const FTGTrustRecord* FindRecord(const FString& PlayerA, const FString& PlayerB) const;
    void BroadcastTrust(const FString& PlayerA, const FString& PlayerB, float NewTrust);

public:
    UFUNCTION(BlueprintCallable, Category="Trust")
    void GetAllRecords(TArray<FTGTrustRecord>& OutRecords) const { OutRecords = Records; }
};
