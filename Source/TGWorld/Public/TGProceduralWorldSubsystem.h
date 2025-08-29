// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"
#include "TGProceduralWorldSubsystem.generated.h"

// Forward declarations
class UTerritorialManager;
struct FTerritorialInfo;

// Copy essential enums locally to avoid dependency
UENUM(BlueprintType)
enum class ELocalFactionID : uint8
{
    None            UMETA(DisplayName = "None"),
    Directorate     UMETA(DisplayName = "Directorate"),
    Free77          UMETA(DisplayName = "Free77"),
    CivicWardens    UMETA(DisplayName = "Civic Wardens"),
    NomadClans      UMETA(DisplayName = "Nomad Clans"),
    VulturesUnion   UMETA(DisplayName = "Vultures Union"),
    CorporateCombine UMETA(DisplayName = "Corporate Combine"),
    VaultedArchivists UMETA(DisplayName = "Vaulted Archivists")
};

UENUM(BlueprintType)
enum class ELocalTerritoryType : uint8
{
    Region          UMETA(DisplayName = "Region"),
    District        UMETA(DisplayName = "District"),
    ControlPoint    UMETA(DisplayName = "Control Point")
};

UENUM(BlueprintType)
enum class ELocalControlPointType : uint8
{
    CommandPost     UMETA(DisplayName = "Command Post"),
    Checkpoint      UMETA(DisplayName = "Checkpoint"),
    Watchtower      UMETA(DisplayName = "Watchtower"),
    SupplyDepot     UMETA(DisplayName = "Supply Depot")
};

UENUM(BlueprintType)
enum class ELocalTerritoryResourceType : uint8
{
    Strategic       UMETA(DisplayName = "Strategic"),
    Economic        UMETA(DisplayName = "Economic"), 
    Military        UMETA(DisplayName = "Military")
};

/**
 * Wrapper struct for generated actors array to work with TMap
 */
USTRUCT(BlueprintType)
struct TGWORLD_API FGeneratedActorArray
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<TWeakObjectPtr<AActor>> Actors;

    FGeneratedActorArray() {}
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerrainGenerated, int32, TerritoryID, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnBuildingPlaced, int32, TerritoryID, ELocalFactionID, ControllingFaction, FVector, Location);

UENUM(BlueprintType)
enum class EProceduralGenerationType : uint8
{
    Landscape       UMETA(DisplayName = "Landscape"),
    Buildings       UMETA(DisplayName = "Buildings"), 
    Details         UMETA(DisplayName = "Details"),
    Vegetation      UMETA(DisplayName = "Vegetation"),
    All             UMETA(DisplayName = "All")
};

USTRUCT(BlueprintType)
struct TGWORLD_API FProceduralGenerationRequest
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    int32 TerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    ELocalTerritoryType TerritoryType = ELocalTerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    ELocalFactionID DominantFaction = ELocalFactionID::None;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    EProceduralGenerationType GenerationType = EProceduralGenerationType::All;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    FVector CenterLocation = FVector::ZeroVector;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    float GenerationRadius = 10000.0f; // 100m default radius

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    int32 RandomSeed = 0;

    FProceduralGenerationRequest()
    {
        TerritoryID = 0;
        TerritoryType = ELocalTerritoryType::Region;
        DominantFaction = ELocalFactionID::None;
        GenerationType = EProceduralGenerationType::All;
        CenterLocation = FVector::ZeroVector;
        GenerationRadius = 10000.0f;
        RandomSeed = FMath::Rand();
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FFactionBuildingProfile
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    ELocalFactionID FactionID = ELocalFactionID::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Buildings")
    TArray<UStaticMesh*> CommandPostMeshes;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Buildings")
    TArray<UStaticMesh*> CheckpointMeshes;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Buildings")
    TArray<UStaticMesh*> WatchtowerMeshes;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Buildings")
    TArray<UStaticMesh*> SupplyDepotMeshes;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
    TArray<UMaterialInterface*> FactionMaterials;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Colors")
    FLinearColor PrimaryColor = FLinearColor::White;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Colors")
    FLinearColor AccentColor = FLinearColor::Gray;

    FFactionBuildingProfile()
    {
        FactionID = ELocalFactionID::None;
        PrimaryColor = FLinearColor::White;
        AccentColor = FLinearColor::Gray;
    }
};

/**
 * Procedural World Generation Subsystem
 * Integrates with TerritorialManager to generate faction-influenced environments
 * Supports landscape, building, and detail generation based on territorial control
 */
UCLASS(BlueprintType)
class TGWORLD_API UTGProceduralWorldSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    // Subsystem lifecycle
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Main generation interface
    UFUNCTION(BlueprintCallable, Category = "Procedural Generation")
    bool GenerateTerritory(const FProceduralGenerationRequest& Request);

    UFUNCTION(BlueprintCallable, Category = "Procedural Generation")
    void RegenerateTerritory(int32 TerritoryID, ELocalTerritoryType TerritoryType, ELocalFactionID NewDominantFaction);

    UFUNCTION(BlueprintCallable, Category = "Procedural Generation")
    void ClearTerritoryGeneration(int32 TerritoryID, ELocalTerritoryType TerritoryType);

    // Landscape generation
    UFUNCTION(BlueprintCallable, Category = "Landscape")
    bool GenerateLandscapeForTerritory(const FTerritorialInfo& TerritoryInfo, const FVector& Location, float Radius);

    // Building placement
    UFUNCTION(BlueprintCallable, Category = "Buildings")
    TArray<AActor*> PlaceFactionBuildings(const FTerritorialInfo& TerritoryInfo, 
                                        const FVector& CenterLocation, 
                                        float Radius,
                                        int32 BuildingCount = 5);

    UFUNCTION(BlueprintCallable, Category = "Buildings")
    AActor* PlaceSingleBuilding(const FVector& Location, 
                              ELocalFactionID ControllingFaction, 
                              ELocalControlPointType BuildingType);

    // Faction configuration
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetFactionBuildingProfile(ELocalFactionID FactionID, const FFactionBuildingProfile& Profile);

    UFUNCTION(BlueprintPure, Category = "Configuration")
    FFactionBuildingProfile GetFactionBuildingProfile(ELocalFactionID FactionID) const;

    // Query functions
    UFUNCTION(BlueprintPure, Category = "Generation")
    bool IsTerritorGenerated(int32 TerritoryID, ELocalTerritoryType TerritoryType) const;

    UFUNCTION(BlueprintPure, Category = "Generation")
    TArray<AActor*> GetGeneratedActorsInTerritory(int32 TerritoryID, ELocalTerritoryType TerritoryType) const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnTerrainGenerated OnTerrainGenerated;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnBuildingPlaced OnBuildingPlaced;

protected:
    // Initialization
    void InitializeDefaultFactionProfiles();

    // Internal generation systems
    void GenerateLandscapeInternal(const FProceduralGenerationRequest& Request);
    void GenerateBuildingsInternal(const FProceduralGenerationRequest& Request);
    void GenerateDetailsInternal(const FProceduralGenerationRequest& Request);
    void GenerateVegetationInternal(const FProceduralGenerationRequest& Request);

    // Faction-specific generation
    UStaticMesh* SelectFactionMesh(ELocalFactionID FactionID, ELocalControlPointType BuildingType) const;
    UMaterialInterface* SelectFactionMaterial(ELocalFactionID FactionID) const;
    FVector CalculateBuildingPlacement(const FVector& CenterLocation, float Radius, int32 BuildingIndex, int32 TotalBuildings) const;

    // Landscape utilities
    void ApplyFactionLandscapeModifications(const FVector& Location, float Radius, ELocalFactionID FactionID);
    void CreateFactionLighting(const FVector& Location, ELocalFactionID FactionID);

    // Territory tracking
    void RegisterGeneratedActor(int32 TerritoryID, ELocalTerritoryType TerritoryType, AActor* Actor);
    void UnregisterTerritoryActors(int32 TerritoryID, ELocalTerritoryType TerritoryType);

private:
    // Configuration
    UPROPERTY()
    TMap<ELocalFactionID, FFactionBuildingProfile> FactionProfiles;

    // Tracking generated content
    UPROPERTY()
    TMap<FString, FGeneratedActorArray> GeneratedActorsByTerritory;

    // Generation settings
    UPROPERTY()
    bool bAutoGenerateOnTerritorialChange = true;

    UPROPERTY()
    float DefaultGenerationRadius = 20000.0f; // 200m default

    UPROPERTY()
    int32 DefaultBuildingsPerTerritory = 8;

    // Integration with territorial system
    UPROPERTY()
    class UTerritorialManager* TerritorialManager;

    // Utility functions
    FString GetTerritoryKey(int32 TerritoryID, ELocalTerritoryType TerritoryType) const;
    FRandomStream GetTerritoryRandomStream(int32 TerritoryID, int32 Seed = 0) const;

    // Territorial change handlers
    UFUNCTION()
    void OnTerritorialInfluenceChanged(int32 TerritoryID, ELocalTerritoryType TerritoryType, int32 NewDominantFaction);
};