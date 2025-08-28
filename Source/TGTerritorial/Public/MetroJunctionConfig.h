// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "TerritorialTypes.h"
#include "MetroJunctionConfig.generated.h"

/**
 * Metro Junction Map Territorial Configuration
 * Defines the territorial zones, control points, and faction dynamics for Metro Junction
 * Based on Map Designer specifications: 800m x 600m with Directorate vs Free77 conflict
 */
UCLASS(BlueprintType, Blueprintable, Category = "Terminal Grounds|Maps")
class TGTERRITORIAL_API UMetroJunctionConfig : public UObject
{
    GENERATED_BODY()

public:
    UMetroJunctionConfig();

    // Metro Junction territorial layout
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Metro Junction")
    FString MapName = TEXT("Metro Junction");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Metro Junction")
    FString MapDescription = TEXT("Underground metro system with Directorate corporate control vs Free77 resistance");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Metro Junction")
    FVector MapSize = FVector(80000.0f, 60000.0f, 1000.0f); // 800m x 600m x 10m

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Metro Junction")
    int32 MaxPlayers = 16;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Metro Junction")
    int32 MinPlayers = 8;

    // Primary factions for this map
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factions")
    TArray<EFactionID> PrimaryFactions = {
        EFactionID::Directorate,
        EFactionID::Free77
    };

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factions")
    TArray<EFactionID> SecondaryFactions = {
        EFactionID::CivicWardens  // Neutral civilian presence
    };

    // Territorial zones configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territories")
    TArray<FTerritorialInfo> TerritorialZones;

    // Extraction points
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    TArray<FVector> ExtractionPoints = {
        FVector(-30000.0f, -5000.0f, -50000.0f),  // Platform Alpha (Directorate)
        FVector(30000.0f, -5000.0f, -50000.0f)    // Platform Beta (Free77)
    };

    // Spawn points for factions
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Spawns")
    TMap<EFactionID, TArray<FVector>> FactionSpawnPoints;

    // Game balance configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    float DirectorateInfluenceModifier = 1.1f; // Slightly higher corporate efficiency

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    float Free77InfluenceModifier = 1.0f; // Baseline resistance effectiveness

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    float NeutralTerritoryBonus = 1.2f; // Central junction provides strategic advantage

    // Environmental storytelling elements
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment")
    TMap<EFactionID, FLinearColor> FactionLightingColors = {
        {EFactionID::Directorate, FLinearColor(0.2f, 0.4f, 1.0f, 1.0f)},  // Corporate blue
        {EFactionID::Free77, FLinearColor(1.0f, 0.3f, 0.2f, 1.0f)}        // Resistance red
    };

    // Initialize default configuration
    UFUNCTION(BlueprintCallable, Category = "Metro Junction")
    void InitializeMetroJunctionConfig();

    // Get territorial configuration for UE5 territorial system
    UFUNCTION(BlueprintPure, Category = "Metro Junction")
    TArray<FTerritorialConfigRow> GetTerritorialConfiguration() const;

    // Faction configuration
    UFUNCTION(BlueprintPure, Category = "Metro Junction")
    FFactionConfig GetFactionConfig(EFactionID FactionID) const;

    // Validation
    UFUNCTION(BlueprintCallable, Category = "Metro Junction")
    bool ValidateConfiguration() const;

protected:
    void SetupTerritorialZones();
    void SetupFactionSpawns();
    void ValidateMapBounds();
};