#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TGDemoManager.generated.h"

class ATGEnemyGrunt;
class ATGWeapon;
class ATGPlayPawn;

UCLASS()
class TGCOMBAT_API ATGDemoManager : public AActor
{
    GENERATED_BODY()

public:
    ATGDemoManager();

protected:
    virtual void BeginPlay() override;

    // Demo Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    int32 NumberOfEnemies = 5;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    float EnemySpawnRadius = 2000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    TSubclassOf<ATGEnemyGrunt> EnemyClass;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    TSubclassOf<ATGWeapon> WeaponClass;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    TSubclassOf<ATGPlayPawn> PlayerClass;

    // Spawned Actors
    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    TArray<ATGEnemyGrunt*> SpawnedEnemies;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    ATGPlayPawn* PlayerPawn;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    ATGWeapon* PlayerWeapon;

public:
    // Demo Functions
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetupDemo();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SpawnEnemies();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SpawnPlayer();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SpawnWeapon();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void CreateCoverObjects();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void CreatePatrolPoints();

    // Utility Functions
    UFUNCTION(BlueprintCallable, Category = "Demo")
    FVector GetRandomSpawnLocation() const;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void ResetDemo();

private:
    void CreateBasicCover();
    void CreatePatrolWaypoints();
};
