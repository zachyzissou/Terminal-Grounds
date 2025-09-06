#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TGDemoSetup.generated.h"

class ATGEnemyGrunt;
class ATGWeapon;
class ATGPlayPawn;

UCLASS(BlueprintType, Blueprintable)
class TGCOMBAT_API ATGDemoSetup : public AActor
{
    GENERATED_BODY()

public:
    ATGDemoSetup();

protected:
    virtual void BeginPlay() override;

    // Demo Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo Setup")
    bool bAutoSetupOnBeginPlay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo Setup")
    int32 NumberOfEnemies = 8;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo Setup")
    float EnemySpawnRadius = 2500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo Setup")
    TSubclassOf<ATGEnemyGrunt> EnemyClass;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo Setup")
    TSubclassOf<ATGWeapon> WeaponClass;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo Setup")
    TSubclassOf<ATGPlayPawn> PlayerClass;

    // Environment Setup
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment")
    bool bCreateCoverObjects = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment")
    bool bCreatePatrolPoints = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment")
    bool bSetupLighting = true;

    // Spawned Actors
    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    TArray<ATGEnemyGrunt*> SpawnedEnemies;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    ATGPlayPawn* PlayerPawn;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    ATGWeapon* PlayerWeapon;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    TArray<AActor*> CoverObjects;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    TArray<AActor*> PatrolPoints;

public:
    // Demo Functions
    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void SetupCompleteDemo();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void SpawnEnemies();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void SpawnPlayer();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void SpawnWeapon();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void CreateCoverObjects();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void CreatePatrolPoints();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void SetupLighting();

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void ResetDemo();

    // Utility Functions
    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    FVector GetRandomSpawnLocation() const;

    UFUNCTION(BlueprintCallable, Category = "Demo Setup")
    void LogDemoStatus() const;

private:
    void CreateBasicCover();
    void CreatePatrolWaypoints();
    void SetupAtmosphericLighting();
};
