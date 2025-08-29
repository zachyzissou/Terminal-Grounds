// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TGProceduralWorldSubsystem.h"
#include "TGProceduralTestActor.generated.h"

/**
 * Test Actor for Procedural Generation System
 * Use this in the editor to test and preview procedural generation
 * Can be placed in levels to trigger generation at specific locations
 */
UCLASS(BlueprintType, Blueprintable)
class TGWORLD_API ATGProceduralTestActor : public AActor
{
    GENERATED_BODY()

public:
    ATGProceduralTestActor();

protected:
    virtual void BeginPlay() override;

public:
    // Test configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    int32 TestTerritoryID = 1001;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    ELocalTerritoryType TestTerritoryType = ELocalTerritoryType::District;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    ELocalFactionID TestDominantFaction = ELocalFactionID::Directorate;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    EProceduralGenerationType GenerationType = EProceduralGenerationType::All;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    float GenerationRadius = 15000.0f; // 150m radius

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    int32 RandomSeed = 12345;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    bool bAutoGenerateOnBeginPlay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test Generation")
    bool bShowDebugInfo = true;

    // Manual controls
    UFUNCTION(BlueprintCallable, Category = "Test Generation", meta = (CallInEditor = "true"))
    void TriggerGeneration();

    UFUNCTION(BlueprintCallable, Category = "Test Generation", meta = (CallInEditor = "true"))
    void ClearGeneration();

    UFUNCTION(BlueprintCallable, Category = "Test Generation", meta = (CallInEditor = "true"))
    void ChangeToDirectorate();

    UFUNCTION(BlueprintCallable, Category = "Test Generation", meta = (CallInEditor = "true"))
    void ChangeToFree77();

    UFUNCTION(BlueprintCallable, Category = "Test Generation", meta = (CallInEditor = "true"))
    void ChangeToCivicWardens();

    // Debug visualization
    UFUNCTION(BlueprintCallable, Category = "Debug")
    void ShowGenerationArea();

protected:
    // Visual components
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UStaticMeshComponent* VisualizationMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UTextRenderComponent* InfoText;

    // Event handlers
    UFUNCTION()
    void OnTerrainGenerated(int32 TerritoryID, bool bSuccess);

    UFUNCTION()
    void OnBuildingPlaced(int32 TerritoryID, ELocalFactionID ControllingFaction, FVector Location);

    void UpdateInfoDisplay();
    void GenerateAtCurrentLocation();

private:
    UPROPERTY()
    UTGProceduralWorldSubsystem* ProceduralSubsystem;

    TArray<AActor*> GeneratedActors;
};