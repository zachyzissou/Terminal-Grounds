// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TerritorialTypes.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "TerritorialExtractionPoint.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnExtractionStarted, APawn*, Player, EFactionID, PlayerFaction, int32, TerritorialInfluenceGain, float, ExtractionTime);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnExtractionCompleted, APawn*, Player, EFactionID, PlayerFaction, int32, TerritorialInfluenceGain);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnExtractionCanceled, APawn*, Player, EFactionID, PlayerFaction, FString, CancellationReason);

UENUM(BlueprintType)
enum class EExtractionState : uint8
{
    Available       UMETA(DisplayName = "Available"),
    InProgress      UMETA(DisplayName = "In Progress"),
    Contested       UMETA(DisplayName = "Contested"),
    Unavailable     UMETA(DisplayName = "Unavailable"),
    Compromised     UMETA(DisplayName = "Compromised")
};

/**
 * Territorial Extraction Point - Metro Junction specific extraction mechanics
 * Combines extraction shooter gameplay with territorial influence system
 * Based on Map Designer specifications for metro platform extractions
 */
UCLASS(BlueprintType, Blueprintable)
class TGTERRITORIAL_API ATerritorialExtractionPoint : public AActor
{
    GENERATED_BODY()

public:
    ATerritorialExtractionPoint();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // Core components
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UStaticMeshComponent* ExtractionPlatform;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USphereComponent* ExtractionTrigger;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USphereComponent* ContestationZone;

    // Extraction configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    int32 TerritoryID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    EFactionID OwningFaction = EFactionID::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    FString ExtractionPointName = TEXT("Extraction Point");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    float BaseExtractionTime = 30.0f; // 30 seconds base extraction

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    float FactionBonusTime = 5.0f; // 5 second bonus for owning faction

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    float ContestedPenaltyTime = 10.0f; // 10 second penalty when contested

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    int32 BaseTerritorialInfluence = 25; // Influence gained for successful extraction

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    int32 ControlleredTerritoryBonus = 15; // Extra influence if faction controls territory

    // Risk/Reward mechanics
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Risk Reward")
    float ExtractionSuccessRate = 0.85f; // 85% base success rate

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Risk Reward")
    float ContestedSuccessRatePenalty = 0.20f; // -20% when contested

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Risk Reward")
    float FactionControlledBonus = 0.10f; // +10% when faction controls territory

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Risk Reward")
    int32 MaxSimultaneousExtractions = 2; // Maximum concurrent extractions

    // Visual and audio feedback
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Feedback")
    TMap<EFactionID, FLinearColor> FactionColors;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Feedback")
    bool bShowExtractionProgress = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Feedback")
    bool bShowTerritorialInfluence = true;

    // Current state
    UPROPERTY(BlueprintReadOnly, Category = "State")
    EExtractionState CurrentState = EExtractionState::Available;

    UPROPERTY(BlueprintReadOnly, Category = "State")
    TArray<APawn*> PlayersInExtractionZone;

    UPROPERTY(BlueprintReadOnly, Category = "State")
    TArray<APawn*> PlayersInContestationZone;

    UPROPERTY(BlueprintReadOnly, Category = "State")
    APawn* CurrentExtractingPlayer = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "State")
    float ExtractionProgress = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "State")
    float CurrentExtractionTime = 0.0f;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Extraction Events")
    FOnExtractionStarted OnExtractionStarted;

    UPROPERTY(BlueprintAssignable, Category = "Extraction Events")
    FOnExtractionCompleted OnExtractionCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Extraction Events")
    FOnExtractionCanceled OnExtractionCanceled;

    // Public interface
    UFUNCTION(BlueprintCallable, Category = "Extraction")
    bool StartExtraction(APawn* Player);

    UFUNCTION(BlueprintCallable, Category = "Extraction")
    void CancelExtraction(const FString& Reason);

    UFUNCTION(BlueprintCallable, Category = "Extraction")
    void CompleteExtraction();

    UFUNCTION(BlueprintPure, Category = "Extraction")
    bool CanPlayerExtract(APawn* Player) const;

    UFUNCTION(BlueprintPure, Category = "Extraction")
    float CalculateExtractionTime(APawn* Player) const;

    UFUNCTION(BlueprintPure, Category = "Extraction")
    float CalculateSuccessRate(APawn* Player) const;

    UFUNCTION(BlueprintPure, Category = "Extraction")
    int32 CalculateTerritorialInfluence(APawn* Player) const;

    UFUNCTION(BlueprintPure, Category = "Extraction")
    bool IsExtractionContested() const;

    UFUNCTION(BlueprintPure, Category = "Extraction")
    EFactionID GetTerritoryControllingFaction() const;

    // Visual updates
    UFUNCTION(BlueprintCallable, Category = "Visuals")
    void UpdateExtractionVisuals();

    UFUNCTION(BlueprintCallable, Category = "Visuals")
    void SetFactionControlVisuals(EFactionID ControllingFaction);

protected:
    // Internal state management
    void UpdateExtractionState();
    void UpdateExtractionProgress(float DeltaTime);
    void CheckContestationStatus();

    // Player management
    EFactionID GetPlayerFaction(APawn* Player) const;
    bool IsPlayerInExtractionZone(APawn* Player) const;
    bool IsPlayerInContestationZone(APawn* Player) const;

    // Territorial integration
    void NotifyTerritorialInfluenceGain(APawn* Player, int32 InfluenceAmount);
    void UpdateTerritorialDisplay();

    // Overlap handlers
    UFUNCTION()
    void OnExtractionTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

    UFUNCTION()
    void OnExtractionTriggerEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

    UFUNCTION()
    void OnContestationZoneBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

    UFUNCTION()
    void OnContestationZoneEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

private:
    // Internal timers and state
    float ExtractionTimer = 0.0f;
    float LastStateUpdate = 0.0f;
    
    // Performance optimization
    float LastTerritorialCheck = 0.0f;
    static constexpr float TERRITORIAL_CHECK_INTERVAL = 2.0f; // Check territorial control every 2 seconds
};