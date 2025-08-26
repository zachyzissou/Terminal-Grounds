// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/Engine.h"
#include "TGTerritorial/Public/TerritorialTypes.h"
#include "TerritorialExtractionObjective.generated.h"

UENUM(BlueprintType)
enum class ETerritorialActionType : uint8
{
    None                UMETA(DisplayName = "None"),
    SabotageOperation   UMETA(DisplayName = "Sabotage Operation"),
    SupplyDelivery      UMETA(DisplayName = "Supply Delivery"),
    IntelGathering      UMETA(DisplayName = "Intelligence Gathering"),
    InfrastructureAssault UMETA(DisplayName = "Infrastructure Assault")
};

USTRUCT(BlueprintType)
struct TGCORE_API FTerritorialObjectiveReward
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 InfluenceValue = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 FactionReputation = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 ExtractionBonus = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    FString RewardDescription;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritorialObjectiveCompleted, int32, TerritoryID, ETerritorialActionType, ActionType, int32, InfluenceGained);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerritorialObjectiveStarted, int32, TerritoryID, ETerritorialActionType, ActionType);

/**
 * Territorial Extraction Objective
 * Links extraction missions to territorial warfare system
 * Players can complete these to affect territorial control
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API ATerritorialExtractionObjective : public AActor
{
    GENERATED_BODY()

public:
    ATerritorialExtractionObjective();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // Core objective configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    ETerritorialActionType ActionType = ETerritorialActionType::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 TargetTerritoryID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    ETerritoryType TerritoryType = ETerritoryType::Region;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 TargetFactionID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    int32 AllyFactionID = 0;

    // Objective rewards and requirements
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    FTerritorialObjectiveReward CompletionReward;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    float CompletionTime = 30.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    bool bRequiresSpecialEquipment = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Objective")
    FString ObjectiveDescription;

    // Visual and interaction
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UStaticMeshComponent* ObjectiveMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class USphereComponent* InteractionSphere;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visual")
    class UMaterialInterface* FactionMaterial;

    // Objective state
    UPROPERTY(BlueprintReadOnly, Category = "Objective State")
    bool bObjectiveActive = true;

    UPROPERTY(BlueprintReadOnly, Category = "Objective State")
    bool bObjectiveCompleted = false;

    UPROPERTY(BlueprintReadOnly, Category = "Objective State")
    float CompletionProgress = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Objective State")
    class APawn* InteractingPlayer = nullptr;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnTerritorialObjectiveCompleted OnTerritorialObjectiveCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnTerritorialObjectiveStarted OnTerritorialObjectiveStarted;

    // Core objective functions
    UFUNCTION(BlueprintCallable, Category = "Territorial Objective")
    bool CanPlayerStartObjective(APawn* Player);

    UFUNCTION(BlueprintCallable, Category = "Territorial Objective")
    void StartObjective(APawn* Player);

    UFUNCTION(BlueprintCallable, Category = "Territorial Objective")
    void CompleteObjective();

    UFUNCTION(BlueprintCallable, Category = "Territorial Objective")
    void CancelObjective();

    UFUNCTION(BlueprintPure, Category = "Territorial Objective")
    float GetCompletionPercentage() const;

    UFUNCTION(BlueprintPure, Category = "Territorial Objective")
    FString GetObjectiveStatusText() const;

    // Territorial system integration
    UFUNCTION(BlueprintCallable, Category = "Territorial Integration")
    void ApplyTerritorialInfluence();

    UFUNCTION(BlueprintCallable, Category = "Territorial Integration")
    void NotifyTerritorialSystem();

protected:
    // Internal objective processing
    UFUNCTION()
    void OnInteractionSphereBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

    UFUNCTION()
    void OnInteractionSphereEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

    // Objective progression
    void UpdateObjectiveProgress(float DeltaTime);
    void SetObjectiveMaterial();
    void UpdateVisualState();

    // Timer handles for objective processing
    UPROPERTY()
    FTimerHandle ObjectiveTimerHandle;

private:
    // Internal state tracking
    float ProgressTimer = 0.0f;
    bool bPlayerInRange = false;
    
    // Cached territorial manager reference
    UPROPERTY()
    class UTerritorialManager* TerritorialManager = nullptr;
};