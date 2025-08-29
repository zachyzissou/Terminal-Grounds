// Copyright Terminal Grounds. All Rights Reserved.

#include "MetroJunctionConfig.h"

UMetroJunctionConfig::UMetroJunctionConfig()
{
    MapName = TEXT("Metro Junction");
    MapDescription = TEXT("Underground metro system with Directorate corporate control vs Free77 resistance");
    MapSize = FVector(80000.0f, 60000.0f, 1000.0f); // 800m x 600m x 10m
    MaxPlayers = 16;
    MinPlayers = 8;

    // Initialize faction arrays
    PrimaryFactions = {
        EFactionID::Directorate,
        EFactionID::Free77
    };
    
    SecondaryFactions = {
        EFactionID::CivicWardens
    };

    // Initialize extraction points
    ExtractionPoints = {
        FVector(-30000.0f, -5000.0f, -50000.0f),  // Platform Alpha (Directorate)
        FVector(30000.0f, -5000.0f, -50000.0f)    // Platform Beta (Free77)
    };

    // Balance configuration
    DirectorateInfluenceModifier = 1.1f;
    Free77InfluenceModifier = 1.0f;
    NeutralTerritoryBonus = 1.2f;

    // Lighting colors
    FactionLightingColors.Add(EFactionID::Directorate, FLinearColor(0.2f, 0.4f, 1.0f, 1.0f));
    FactionLightingColors.Add(EFactionID::Free77, FLinearColor(1.0f, 0.3f, 0.2f, 1.0f));
    FactionLightingColors.Add(EFactionID::CivicWardens, FLinearColor(0.7f, 0.7f, 0.7f, 1.0f));
}

void UMetroJunctionConfig::InitializeMetroJunctionConfig()
{
    SetupTerritorialZones();
    SetupFactionSpawns();
    ValidateMapBounds();
}

void UMetroJunctionConfig::SetupTerritorialZones()
{
    TerritorialZones.Empty();

    // Metro Region (Root)
    FTerritorialInfo MetroRegion;
    MetroRegion.TerritoryID = 1001;
    MetroRegion.TerritoryType = ETerritoryType::Region;
    MetroRegion.Name = TEXT("Metro Junction Region");
    MetroRegion.Description = TEXT("Underground metro system with multiple transit lines and faction control points");
    MetroRegion.ResourceType = ETerritoryResourceType::Strategic;
    MetroRegion.StrategicValue = 85;
    MetroRegion.TacticalImportance = 75;
    MetroRegion.WorldPosition = FVector(0.0f, 0.0f, -50000.0f);
    MetroRegion.ControlRadius = 40000.0f; // 400m radius
    MetroRegion.ControlPointType = EControlPointType::CommandPost;
    TerritorialZones.Add(MetroRegion);

    // Directorate Corporate Zone
    FTerritorialInfo DirectorateDistrict;
    DirectorateDistrict.TerritoryID = 1002;
    DirectorateDistrict.TerritoryType = ETerritoryType::District;
    DirectorateDistrict.Name = TEXT("Directorate Corporate Zone");
    DirectorateDistrict.Description = TEXT("Corporate-controlled metro sector with security checkpoints and blue lighting");
    DirectorateDistrict.ResourceType = ETerritoryResourceType::Economic;
    DirectorateDistrict.StrategicValue = 70;
    DirectorateDistrict.TacticalImportance = 80;
    DirectorateDistrict.WorldPosition = FVector(-20000.0f, 0.0f, -50000.0f);
    DirectorateDistrict.ControlRadius = 20000.0f; // 200m radius
    DirectorateDistrict.ControlPointType = EControlPointType::Checkpoint;
    TerritorialZones.Add(DirectorateDistrict);

    // Free77 Resistance Zone
    FTerritorialInfo Free77District;
    Free77District.TerritoryID = 1003;
    Free77District.TerritoryType = ETerritoryType::District;
    Free77District.Name = TEXT("Free77 Resistance Zone");
    Free77District.Description = TEXT("Resistance-controlled metro sector with propaganda and improvised defenses");
    Free77District.ResourceType = ETerritoryResourceType::Military;
    Free77District.StrategicValue = 65;
    Free77District.TacticalImportance = 85;
    Free77District.WorldPosition = FVector(20000.0f, 0.0f, -50000.0f);
    Free77District.ControlRadius = 20000.0f; // 200m radius
    Free77District.ControlPointType = EControlPointType::CommandPost;
    TerritorialZones.Add(Free77District);

    // Central Junction Hub (Contested)
    FTerritorialInfo NeutralJunction;
    NeutralJunction.TerritoryID = 1004;
    NeutralJunction.TerritoryType = ETerritoryType::District;
    NeutralJunction.Name = TEXT("Central Junction Hub");
    NeutralJunction.Description = TEXT("Contested central platform where multiple lines converge");
    NeutralJunction.ResourceType = ETerritoryResourceType::Strategic;
    NeutralJunction.StrategicValue = 90;
    NeutralJunction.TacticalImportance = 90;
    NeutralJunction.WorldPosition = FVector(0.0f, 10000.0f, -50000.0f);
    NeutralJunction.ControlRadius = 15000.0f; // 150m radius
    NeutralJunction.ControlPointType = EControlPointType::CommArray;
    TerritorialZones.Add(NeutralJunction);

    // Control Points - Directorate
    FTerritorialInfo DirectoratePlatformA;
    DirectoratePlatformA.TerritoryID = 1005;
    DirectoratePlatformA.TerritoryType = ETerritoryType::ControlPoint;
    DirectoratePlatformA.Name = TEXT("Platform Alpha");
    DirectoratePlatformA.Description = TEXT("Main Directorate extraction platform with corporate security");
    DirectoratePlatformA.ResourceType = ETerritoryResourceType::Economic;
    DirectoratePlatformA.StrategicValue = 60;
    DirectoratePlatformA.TacticalImportance = 70;
    DirectoratePlatformA.WorldPosition = FVector(-30000.0f, -5000.0f, -50000.0f);
    DirectoratePlatformA.ControlRadius = 7500.0f; // 75m radius
    DirectoratePlatformA.ControlPointType = EControlPointType::ExtractionZone;
    TerritorialZones.Add(DirectoratePlatformA);

    FTerritorialInfo DirectorateCheckpoint;
    DirectorateCheckpoint.TerritoryID = 1006;
    DirectorateCheckpoint.TerritoryType = ETerritoryType::ControlPoint;
    DirectorateCheckpoint.Name = TEXT("Security Checkpoint");
    DirectorateCheckpoint.Description = TEXT("Directorate security control point with weapon scanners");
    DirectorateCheckpoint.ResourceType = ETerritoryResourceType::Military;
    DirectorateCheckpoint.StrategicValue = 50;
    DirectorateCheckpoint.TacticalImportance = 75;
    DirectorateCheckpoint.WorldPosition = FVector(-10000.0f, 5000.0f, -50000.0f);
    DirectorateCheckpoint.ControlRadius = 5000.0f; // 50m radius
    DirectorateCheckpoint.ControlPointType = EControlPointType::Checkpoint;
    TerritorialZones.Add(DirectorateCheckpoint);

    // Control Points - Free77
    FTerritorialInfo Free77PlatformB;
    Free77PlatformB.TerritoryID = 1007;
    Free77PlatformB.TerritoryType = ETerritoryType::ControlPoint;
    Free77PlatformB.Name = TEXT("Platform Beta");
    Free77PlatformB.Description = TEXT("Free77 resistance platform with improvised extraction setup");
    Free77PlatformB.ResourceType = ETerritoryResourceType::Military;
    Free77PlatformB.StrategicValue = 60;
    Free77PlatformB.TacticalImportance = 70;
    Free77PlatformB.WorldPosition = FVector(30000.0f, -5000.0f, -50000.0f);
    Free77PlatformB.ControlRadius = 7500.0f; // 75m radius
    Free77PlatformB.ControlPointType = EControlPointType::ExtractionZone;
    TerritorialZones.Add(Free77PlatformB);

    FTerritorialInfo Free77Outpost;
    Free77Outpost.TerritoryID = 1008;
    Free77Outpost.TerritoryType = ETerritoryType::ControlPoint;
    Free77Outpost.Name = TEXT("Resistance Outpost");
    Free77Outpost.Description = TEXT("Free77 forward operating base with ammunition depot");
    Free77Outpost.ResourceType = ETerritoryResourceType::Military;
    Free77Outpost.StrategicValue = 55;
    Free77Outpost.TacticalImportance = 80;
    Free77Outpost.WorldPosition = FVector(10000.0f, 5000.0f, -50000.0f);
    Free77Outpost.ControlRadius = 5000.0f; // 50m radius
    Free77Outpost.ControlPointType = EControlPointType::SupplyDepot;
    TerritorialZones.Add(Free77Outpost);
}

void UMetroJunctionConfig::SetupFactionSpawns()
{
    FactionSpawnPoints.Empty();

    // Directorate spawn points (Corporate zone)
    TArray<FVector> DirectorateSpawns = {
        FVector(-25000.0f, -10000.0f, -50000.0f),
        FVector(-30000.0f, 0.0f, -50000.0f),
        FVector(-20000.0f, -5000.0f, -50000.0f),
        FVector(-35000.0f, -15000.0f, -50000.0f)
    };
    FFactionSpawnPoints DirectorateSpawnWrapper;
    DirectorateSpawnWrapper.SpawnLocations = DirectorateSpawns;
    FactionSpawnPoints.Add(EFactionID::Directorate, DirectorateSpawnWrapper);

    // Free77 spawn points (Resistance zone)
    TArray<FVector> Free77Spawns = {
        FVector(25000.0f, -10000.0f, -50000.0f),
        FVector(30000.0f, 0.0f, -50000.0f),
        FVector(20000.0f, -5000.0f, -50000.0f),
        FVector(35000.0f, -15000.0f, -50000.0f)
    };
    FFactionSpawnPoints Free77SpawnWrapper;
    Free77SpawnWrapper.SpawnLocations = Free77Spawns;
    FactionSpawnPoints.Add(EFactionID::Free77, Free77SpawnWrapper);

    // Neutral/CivicWardens spawns (Central area)
    TArray<FVector> NeutralSpawns = {
        FVector(-5000.0f, 15000.0f, -50000.0f),
        FVector(5000.0f, 15000.0f, -50000.0f),
        FVector(0.0f, 20000.0f, -50000.0f)
    };
    FFactionSpawnPoints NeutralSpawnWrapper;
    NeutralSpawnWrapper.SpawnLocations = NeutralSpawns;
    FactionSpawnPoints.Add(EFactionID::CivicWardens, NeutralSpawnWrapper);
}

void UMetroJunctionConfig::ValidateMapBounds()
{
    // Ensure all territorial zones are within map bounds
    for (const FTerritorialInfo& Zone : TerritorialZones)
    {
        const FVector& Pos = Zone.WorldPosition;
        
        // Check X bounds (-400m to +400m)
        if (Pos.X < -40000.0f || Pos.X > 40000.0f)
        {
            UE_LOG(LogTemp, Warning, TEXT("MetroJunctionConfig: Territory %s X position out of bounds: %f"), 
                *Zone.Name, Pos.X);
        }
        
        // Check Y bounds (-300m to +300m)
        if (Pos.Y < -30000.0f || Pos.Y > 30000.0f)
        {
            UE_LOG(LogTemp, Warning, TEXT("MetroJunctionConfig: Territory %s Y position out of bounds: %f"), 
                *Zone.Name, Pos.Y);
        }
    }
}

TArray<FTerritorialConfigRow> UMetroJunctionConfig::GetTerritorialConfiguration() const
{
    TArray<FTerritorialConfigRow> ConfigRows;

    for (const FTerritorialInfo& Zone : TerritorialZones)
    {
        FTerritorialConfigRow Row;
        Row.TerritoryInfo = Zone;
        
        // Set up connections based on territory hierarchy
        switch (Zone.TerritoryID)
        {
        case 1001: // Metro Region
            Row.ConnectedTerritories = {1002, 1003, 1004};
            Row.ParentTerritoryID = 0;
            Row.ChildTerritoryIDs = {1002, 1003, 1004};
            break;
        case 1002: // Directorate District
            Row.ConnectedTerritories = {1001, 1005, 1006};
            Row.ParentTerritoryID = 1001;
            Row.ChildTerritoryIDs = {1005, 1006};
            break;
        case 1003: // Free77 District
            Row.ConnectedTerritories = {1001, 1007, 1008};
            Row.ParentTerritoryID = 1001;
            Row.ChildTerritoryIDs = {1007, 1008};
            break;
        case 1004: // Neutral Junction
            Row.ConnectedTerritories = {1001, 1002, 1003};
            Row.ParentTerritoryID = 1001;
            break;
        case 1005: // Platform Alpha
            Row.ConnectedTerritories = {1002, 1006};
            Row.ParentTerritoryID = 1002;
            break;
        case 1006: // Security Checkpoint
            Row.ConnectedTerritories = {1002, 1005};
            Row.ParentTerritoryID = 1002;
            break;
        case 1007: // Platform Beta
            Row.ConnectedTerritories = {1003, 1008};
            Row.ParentTerritoryID = 1003;
            break;
        case 1008: // Resistance Outpost
            Row.ConnectedTerritories = {1003, 1007};
            Row.ParentTerritoryID = 1003;
            break;
        }
        
        ConfigRows.Add(Row);
    }

    return ConfigRows;
}

FFactionConfig UMetroJunctionConfig::GetFactionConfig(EFactionID FactionID) const
{
    FFactionConfig Config;
    Config.FactionID = static_cast<int32>(FactionID);

    switch (FactionID)
    {
    case EFactionID::Directorate:
        Config.FactionName = TEXT("Directorate");
        Config.Description = TEXT("Corporate authority with advanced security systems");
        Config.FactionColor = FLinearColor(0.2f, 0.4f, 1.0f, 1.0f);
        Config.InfluenceModifier = DirectorateInfluenceModifier;
        Config.AggressionLevel = 0.6f;
        Config.DefensiveBonus = 1.2f;
        Config.PreferredResources = {ETerritoryResourceType::Economic, ETerritoryResourceType::Strategic};
        break;
    case EFactionID::Free77:
        Config.FactionName = TEXT("Free77");
        Config.Description = TEXT("Resistance movement with guerrilla tactics");
        Config.FactionColor = FLinearColor(1.0f, 0.3f, 0.2f, 1.0f);
        Config.InfluenceModifier = Free77InfluenceModifier;
        Config.AggressionLevel = 0.8f;
        Config.DefensiveBonus = 0.9f;
        Config.PreferredResources = {ETerritoryResourceType::Military, ETerritoryResourceType::Strategic};
        break;
    case EFactionID::CivicWardens:
        Config.FactionName = TEXT("Civic Wardens");
        Config.Description = TEXT("Neutral civilian protection force");
        Config.FactionColor = FLinearColor(0.7f, 0.7f, 0.7f, 1.0f);
        Config.InfluenceModifier = 0.8f;
        Config.AggressionLevel = 0.3f;
        Config.DefensiveBonus = 1.1f;
        Config.PreferredResources = {ETerritoryResourceType::Cultural};
        break;
    default:
        Config.FactionName = TEXT("Unknown");
        break;
    }

    return Config;
}

bool UMetroJunctionConfig::ValidateConfiguration() const
{
    // Basic validation checks
    if (TerritorialZones.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("MetroJunctionConfig: No territorial zones configured"));
        return false;
    }

    if (ExtractionPoints.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("MetroJunctionConfig: No extraction points configured"));
        return false;
    }

    if (FactionSpawnPoints.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("MetroJunctionConfig: No faction spawn points configured"));
        return false;
    }

    // Ensure primary factions have spawn points
    for (EFactionID Faction : PrimaryFactions)
    {
        if (!FactionSpawnPoints.Contains(Faction))
        {
            UE_LOG(LogTemp, Error, TEXT("MetroJunctionConfig: Primary faction %d missing spawn points"), 
                static_cast<int32>(Faction));
            return false;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("MetroJunctionConfig: Configuration validation passed"));
    return true;
}