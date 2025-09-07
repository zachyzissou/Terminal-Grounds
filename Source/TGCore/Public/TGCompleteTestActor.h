#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TGCompleteTestActor.generated.h"

class ATGPlaytestGameMode;
class UTGProceduralWorldSubsystem;
class ATGDemoSetup;
class ATGPlaytestExtractionZone;

UENUM(BlueprintType)
enum class ETestScenarioType : uint8
{
    DirectorateOutpost      UMETA(DisplayName = "Directorate Outpost"),
    Free77Stronghold        UMETA(DisplayName = "Free77 Stronghold"),
    ContestedTerritory      UMETA(DisplayName = "Contested Territory"),
    MultiFactionalBattle    UMETA(DisplayName = "Multi-Factional Battle"),
    RandomizedEnvironment   UMETA(DisplayName = "Randomized Environment")
};

/**
 * Complete test actor that demonstrates Phase 1 combat with procedural generation
 * Place this in any level to create a fully playable Terminal Grounds experience
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API ATGCompleteTestActor : public AActor
{
    GENERATED_BODY()
    
public:    
    ATGCompleteTestActor();

protected:
    virtual void BeginPlay() override;

    // Test Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Configuration")
    ETestScenarioType ScenarioType = ETestScenarioType::DirectorateOutpost;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Configuration")
    bool bAutoSetupOnBeginPlay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Configuration")
    float SetupDelay = 2.0f;

    // Combat Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat Setup")
    int32 NumberOfEnemies = 8;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat Setup")
    float CombatAreaRadius = 5000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat Setup")
    TSubclassOf<class ATGEnemyGrunt> EnemyClass;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat Setup")
    TSubclassOf<class ATGWeapon> WeaponClass;

    // Procedural Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Procedural Generation")
    bool bGenerateProceduralEnvironment = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Procedural Generation")
    float ProceduralGenerationRadius = 10000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Procedural Generation")
    int32 NumberOfTerritories = 3;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Procedural Generation")
    bool bGenerateBuildings = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Procedural Generation")
    bool bGenerateDetails = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Procedural Generation")
    bool bGenerateVegetation = true;

    // Extraction Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction Setup")
    bool bCreateExtractionZone = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction Setup")
    FVector ExtractionZoneOffset = FVector(0, 0, 0);

    // Spawned Components
    UPROPERTY(BlueprintReadOnly, Category = "Runtime")
    TObjectPtr<ATGDemoSetup> SpawnedDemoSetup;

    UPROPERTY(BlueprintReadOnly, Category = "Runtime")
    TObjectPtr<ATGPlaytestExtractionZone> SpawnedExtractionZone;

    UPROPERTY(BlueprintReadOnly, Category = "Runtime")
    TArray<int32> GeneratedTerritoryIDs;

public:
    // Setup Functions
    UFUNCTION(BlueprintCallable, Category = "Test Setup")
    void SetupCompleteTest();

    UFUNCTION(BlueprintCallable, Category = "Test Setup")
    void SetupCombatScenario();

    UFUNCTION(BlueprintCallable, Category = "Test Setup")
    void SetupProceduralEnvironment();

    UFUNCTION(BlueprintCallable, Category = "Test Setup")
    void SetupExtractionZone();

    UFUNCTION(BlueprintCallable, Category = "Test Setup")
    void CleanupTest();

    // Procedural Generation
    UFUNCTION(BlueprintCallable, Category = "Procedural")
    void GenerateTerritory(int32 TerritoryID, uint8 FactionID, FVector CenterLocation, float Radius);

    UFUNCTION(BlueprintCallable, Category = "Procedural")
    void GenerateScenarioEnvironment();

    UFUNCTION(BlueprintCallable, Category = "Procedural")
    void ClearAllGeneratedTerritories();

    // Utility
    UFUNCTION(BlueprintPure, Category = "Test")
    FVector GetRandomLocationInRadius(float Radius) const;

    UFUNCTION(BlueprintPure, Category = "Test")
    uint8 GetFactionForScenario() const;

    // Blueprint Events
    UFUNCTION(BlueprintImplementableEvent, Category = "Test Events")
    void OnTestSetupComplete();

    UFUNCTION(BlueprintImplementableEvent, Category = "Test Events")
    void OnCombatSetupComplete(int32 EnemyCount);

    UFUNCTION(BlueprintImplementableEvent, Category = "Test Events")
    void OnProceduralGenerationComplete(int32 TerritoryCount);

    UFUNCTION(BlueprintImplementableEvent, Category = "Test Events")
    void OnExtractionZoneCreated();

private:
    FTimerHandle SetupTimerHandle;

    void DelayedSetup();
    void ValidateGameMode();
    void LogTestConfiguration();
};