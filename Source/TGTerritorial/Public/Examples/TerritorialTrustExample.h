// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Trust/TGTrustSubsystem.h"
#include "TerritorialTypes.h"
#include "TerritorialTrustExample.generated.h"

/**
 * Example actor demonstrating territorial trust system integration
 * Shows how to properly record territorial trust actions and handle events
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API ATerritorialTrustExample : public AActor
{
    GENERATED_BODY()

public:
    ATerritorialTrustExample();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // Example functions showing trust system integration
    UFUNCTION(BlueprintCallable, Category = "Trust Examples")
    void ExampleRecordCooperation(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID);

    UFUNCTION(BlueprintCallable, Category = "Trust Examples")
    void ExampleRecordBetrayal(const FString& Betrayer, const FString& Victim, int32 TerritoryID);

    UFUNCTION(BlueprintCallable, Category = "Trust Examples")
    void ExampleRecordExtractionAssist(const FString& Helper, const FString& Assisted, int32 ExtractionPointID);

    UFUNCTION(BlueprintCallable, Category = "Trust Examples")
    void ExampleCheckTrustModifier(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID);

    // Event handlers showing how to respond to trust events
    UFUNCTION()
    void OnTerritorialCooperationReceived(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustGain);

    UFUNCTION()
    void OnTerritorialBetrayalReceived(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustLoss);

    UFUNCTION()
    void OnExtractionAssistanceReceived(const FString& Helper, const FString& Assisted, float TrustBonus);

protected:
    UPROPERTY()
    UTGTrustSubsystem* TrustSystem;

    // Example configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Example Config")
    bool bEnableLogging = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Example Config")
    bool bAutoBindEvents = true;

    // Helper functions
    void BindTrustEvents();
    void LogTrustAction(const FString& Action, const FString& PlayerA, const FString& PlayerB, float Value);
};