// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/SphereComponent.h"
#include "TerritorialTypes.h"
#include "FactionAreaComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnPlayerEnteredFactionArea, APawn*, Player, EFactionID, AreaFaction, int32, TerritoryID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnPlayerExitedFactionArea, APawn*, Player, EFactionID, AreaFaction, int32, TerritoryID);

/**
 * Faction Area Component - Defines territorial zones for factions in Metro Junction
 * Handles visual identity, spawn points, and territorial influence for faction areas
 */
UCLASS(ClassGroup=(TerritorialGrounds), meta=(BlueprintSpawnableComponent))
class TGTERRITORIAL_API UFactionAreaComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFactionAreaComponent();

protected:
    virtual void BeginPlay() override;

public:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // Faction configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction Area")
    EFactionID FactionID = EFactionID::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction Area")
    int32 TerritoryID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction Area")
    FString AreaName = TEXT("Unnamed Area");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction Area")
    FString AreaDescription = TEXT("Faction controlled territory");

    // Visual identity
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visual Identity")
    FLinearColor FactionColor = FLinearColor::White;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visual Identity")
    float LightingIntensity = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visual Identity")
    bool bEnableFactionLighting = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visual Identity")
    TArray<class UDecalComponent*> FactionDecals;

    // Spawn system
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Spawning")
    TArray<FVector> SpawnPoints;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Spawning")
    float SpawnPointRadius = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Spawning")
    int32 MaxPlayersInArea = 8;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Spawning")
    bool bAllowEnemySpawning = false;

    // Territorial influence
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    float InfluenceRadius = 1000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    float BaseInfluenceRate = 1.0f; // Influence per second for friendly players

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    float ContestInfluenceRate = 0.5f; // Reduced rate when contested

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    int32 MaxPlayersForInfluence = 4; // Diminishing returns after this

    // Area boundaries
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boundaries")
    FVector AreaCenter = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boundaries")
    float AreaRadius = 2000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boundaries")
    bool bUseComplexBoundary = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boundaries", meta = (EditCondition = "bUseComplexBoundary"))
    TArray<FVector> BoundaryPoints;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Faction Area Events")
    FOnPlayerEnteredFactionArea OnPlayerEnteredArea;

    UPROPERTY(BlueprintAssignable, Category = "Faction Area Events")
    FOnPlayerExitedFactionArea OnPlayerExitedArea;

    // Public interface
    UFUNCTION(BlueprintCallable, Category = "Faction Area")
    void InitializeFactionArea(EFactionID InFactionID, int32 InTerritoryID, const FVector& InAreaCenter, float InAreaRadius);

    UFUNCTION(BlueprintCallable, Category = "Faction Area")
    void SetFactionVisualIdentity(FLinearColor Color, float Intensity);

    UFUNCTION(BlueprintCallable, Category = "Faction Area")
    void AddSpawnPoint(const FVector& SpawnLocation);

    UFUNCTION(BlueprintCallable, Category = "Faction Area")
    void RemoveSpawnPoint(int32 SpawnIndex);

    UFUNCTION(BlueprintPure, Category = "Faction Area")
    TArray<FVector> GetAvailableSpawnPoints() const;

    UFUNCTION(BlueprintPure, Category = "Faction Area")
    FVector GetBestSpawnPoint(const TArray<APawn*>& ExistingPlayers) const;

    UFUNCTION(BlueprintPure, Category = "Faction Area")
    bool IsLocationInArea(const FVector& Location) const;

    UFUNCTION(BlueprintPure, Category = "Faction Area")
    TArray<APawn*> GetPlayersInArea() const;

    UFUNCTION(BlueprintPure, Category = "Faction Area")
    int32 GetFactionPlayerCount(EFactionID CheckFactionID) const;

    UFUNCTION(BlueprintPure, Category = "Faction Area")
    bool IsAreaContested() const;

    UFUNCTION(BlueprintCallable, Category = "Faction Area")
    void UpdateTerritorialInfluence(float DeltaTime);

    // Visual effects
    UFUNCTION(BlueprintCallable, Category = "Visual Effects")
    void ApplyFactionLighting();

    UFUNCTION(BlueprintCallable, Category = "Visual Effects")
    void SpawnFactionDecals();

    UFUNCTION(BlueprintCallable, Category = "Visual Effects")
    void UpdateAreaBoundaryEffects();

protected:
    // Internal state tracking
    UPROPERTY()
    TArray<TWeakObjectPtr<APawn>> PlayersInArea;

    UPROPERTY()
    class USphereComponent* AreaBoundary;

    UPROPERTY()
    TArray<class UPointLightComponent*> FactionLights;

    UPROPERTY()
    float LastInfluenceUpdate = 0.0f;

    // Internal functions
    void CheckPlayerProximity();
    void OnPlayerEntered(APawn* Player);
    void OnPlayerExited(APawn* Player);
    
    EFactionID GetPlayerFaction(APawn* Player) const;
    float CalculateInfluenceMultiplier() const;
    void NotifyTerritorialManager(int32 InfluenceChange, const FString& Cause);

    // Sphere component callbacks
    UFUNCTION()
    void OnAreaBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, 
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);
    
    UFUNCTION()
    void OnAreaEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, 
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};