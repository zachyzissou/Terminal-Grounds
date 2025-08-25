// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "TerritorialTypes.generated.h"

/**
 * Territory hierarchy types
 */
UENUM(BlueprintType)
enum class ETerritoryType : uint8
{
    Region      UMETA(DisplayName = "Region"),
    District    UMETA(DisplayName = "District"),
    ControlPoint UMETA(DisplayName = "Control Point")
};

/**
 * Faction identifiers
 */
UENUM(BlueprintType)
enum class EFactionID : uint8
{
    None = 0            UMETA(DisplayName = "None"),
    Directorate = 1     UMETA(DisplayName = "Directorate"),
    Free77 = 2          UMETA(DisplayName = "Free77"),
    NomadClans = 3      UMETA(DisplayName = "Nomad Clans"),
    CivicWardens = 4    UMETA(DisplayName = "Civic Wardens"),
    VulturesUnion = 5   UMETA(DisplayName = "Vultures Union"),
    VaultedArchivists = 6 UMETA(DisplayName = "Vaulted Archivists"),
    CorporateCombine = 7 UMETA(DisplayName = "Corporate Combine")
};

/**
 * Territory resource types
 */
UENUM(BlueprintType)
enum class ETerritoryResourceType : uint8
{
    Salvage         UMETA(DisplayName = "Salvage"),
    Intelligence    UMETA(DisplayName = "Intelligence"),
    Strategic       UMETA(DisplayName = "Strategic"),
    Technology      UMETA(DisplayName = "Technology"),
    Economic        UMETA(DisplayName = "Economic"),
    Cultural        UMETA(DisplayName = "Cultural"),
    Military        UMETA(DisplayName = "Military")
};

/**
 * Control point types
 */
UENUM(BlueprintType)
enum class EControlPointType : uint8
{
    CommandPost     UMETA(DisplayName = "Command Post"),
    SupplyDepot     UMETA(DisplayName = "Supply Depot"),
    Checkpoint      UMETA(DisplayName = "Checkpoint"),
    CommArray       UMETA(DisplayName = "Communication Array"),
    ExtractionZone  UMETA(DisplayName = "Extraction Zone"),
    CivilianShelter UMETA(DisplayName = "Civilian Shelter")
};

/**
 * Territorial state structure
 */
USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 TerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    ETerritoryType TerritoryType = ETerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    TMap<int32, int32> FactionInfluences; // FactionID -> Influence%

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 DominantFaction = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    bool bIsContested = false;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FDateTime LastUpdated;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    float InfluenceDecayRate = 1.0f;

    FTerritorialState()
    {
        TerritoryID = 0;
        TerritoryType = ETerritoryType::Region;
        DominantFaction = 0;
        bIsContested = false;
        LastUpdated = FDateTime::Now();
        InfluenceDecayRate = 1.0f;
    }
};

/**
 * Territorial update message
 */
USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialUpdate
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 TerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    ETerritoryType TerritoryType = ETerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 FactionID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 InfluenceChange = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FString ChangeCause;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 NewInfluenceValue = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    bool bControlChanged = false;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FDateTime Timestamp;

    FTerritorialUpdate()
    {
        TerritoryID = 0;
        TerritoryType = ETerritoryType::Region;
        FactionID = 0;
        InfluenceChange = 0;
        ChangeCause = TEXT("");
        NewInfluenceValue = 0;
        bControlChanged = false;
        Timestamp = FDateTime::Now();
    }
};

/**
 * Territory information structure
 */
USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialInfo
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 TerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    ETerritoryType TerritoryType = ETerritoryType::Region;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FString Name;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FString Description;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    ETerritoryResourceType ResourceType = ETerritoryResourceType::Salvage;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 StrategicValue = 50; // 1-100

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 TacticalImportance = 30; // 1-100

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FVector WorldPosition;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    float ControlRadius = 100.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    EControlPointType ControlPointType = EControlPointType::CommandPost;

    FTerritorialInfo()
    {
        TerritoryID = 0;
        TerritoryType = ETerritoryType::Region;
        Name = TEXT("");
        Description = TEXT("");
        ResourceType = ETerritoryResourceType::Salvage;
        StrategicValue = 50;
        TacticalImportance = 30;
        WorldPosition = FVector::ZeroVector;
        ControlRadius = 100.0f;
        ControlPointType = EControlPointType::CommandPost;
    }
};

/**
 * Faction configuration
 */
USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FFactionConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    int32 FactionID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    FString FactionName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    FString Description;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    FLinearColor FactionColor = FLinearColor::White;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    float InfluenceModifier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    float AggressionLevel = 0.5f; // 0.0-1.0

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    float DefensiveBonus = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    TArray<ETerritoryResourceType> PreferredResources;

    FFactionConfig()
    {
        FactionID = 0;
        FactionName = TEXT("");
        Description = TEXT("");
        FactionColor = FLinearColor::White;
        InfluenceModifier = 1.0f;
        AggressionLevel = 0.5f;
        DefensiveBonus = 1.0f;
    }
};

/**
 * Data table row for territorial configuration
 */
USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FTerritorialConfigRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FTerritorialInfo TerritoryInfo;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    TArray<int32> ConnectedTerritories;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 ParentTerritoryID = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    TArray<int32> ChildTerritoryIDs;
};

/**
 * Data table row for faction configuration
 */
USTRUCT(BlueprintType)
struct TGTERRITORIAL_API FFactionConfigRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    FFactionConfig FactionConfig;
};