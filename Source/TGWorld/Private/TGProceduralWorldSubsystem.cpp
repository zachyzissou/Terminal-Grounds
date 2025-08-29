// Copyright Terminal Grounds. All Rights Reserved.

#include "TGProceduralWorldSubsystem.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/KismetMathLibrary.h"

// Include territorial types in implementation only to avoid circular dependency
#include "TerritorialTypes.h"
#include "TGTerritorialManager.h"

void UTGProceduralWorldSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // Initialize default faction profiles
    InitializeDefaultFactionProfiles();

    // Get reference to territorial manager
    TerritorialManager = GetWorld()->GetSubsystem<UTGTerritorialManager>();
    if (TerritorialManager)
    {
        // TODO: Bind to territorial change events when they're implemented
        UE_LOG(LogTemp, Log, TEXT("UTGProceduralWorldSubsystem initialized and connected to TerritorialManager"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("UTGProceduralWorldSubsystem: Could not find TGTerritorialManager"));
    }
}

void UTGProceduralWorldSubsystem::Deinitialize()
{
    // Clear all generated content
    for (auto& TerritoryPair : GeneratedActorsByTerritory)
    {
        for (TWeakObjectPtr<AActor> ActorPtr : TerritoryPair.Value.Actors)
        {
            if (ActorPtr.IsValid())
            {
                ActorPtr->Destroy();
            }
        }
    }
    GeneratedActorsByTerritory.Empty();

    Super::Deinitialize();
}

void UTGProceduralWorldSubsystem::InitializeDefaultFactionProfiles()
{
    // Directorate Profile - Clean, corporate aesthetic
    FFactionBuildingProfile DirectorateProfile;
    DirectorateProfile.FactionID = ELocalFactionID::Directorate;
    DirectorateProfile.PrimaryColor = FLinearColor(0.2f, 0.4f, 1.0f, 1.0f); // Corporate blue
    DirectorateProfile.AccentColor = FLinearColor(0.8f, 0.8f, 0.9f, 1.0f);  // Clean white/gray
    FactionProfiles.Add(ELocalFactionID::Directorate, DirectorateProfile);

    // Free77 Profile - Gritty, improvised aesthetic  
    FFactionBuildingProfile Free77Profile;
    Free77Profile.FactionID = ELocalFactionID::Free77;
    Free77Profile.PrimaryColor = FLinearColor(1.0f, 0.3f, 0.2f, 1.0f); // Resistance red
    Free77Profile.AccentColor = FLinearColor(0.4f, 0.3f, 0.2f, 1.0f);  // Rust brown
    FactionProfiles.Add(ELocalFactionID::Free77, Free77Profile);

    // CivicWardens Profile - Neutral, maintenance aesthetic
    FFactionBuildingProfile CivicProfile;
    CivicProfile.FactionID = ELocalFactionID::CivicWardens;
    CivicProfile.PrimaryColor = FLinearColor(0.7f, 0.7f, 0.7f, 1.0f); // Neutral gray
    CivicProfile.AccentColor = FLinearColor(0.9f, 0.8f, 0.2f, 1.0f);  // Warning yellow
    FactionProfiles.Add(ELocalFactionID::CivicWardens, CivicProfile);

    UE_LOG(LogTemp, Log, TEXT("Initialized default faction building profiles"));
}

bool UTGProceduralWorldSubsystem::GenerateTerritory(const FProceduralGenerationRequest& Request)
{
    if (Request.TerritoryID <= 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("GenerateTerritory: Invalid TerritoryID %d"), Request.TerritoryID);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Generating territory %d of type %d at location %s"), 
           Request.TerritoryID, (int32)Request.TerritoryType, *Request.CenterLocation.ToString());

    // Clear existing generation for this territory
    ClearTerritoryGeneration(Request.TerritoryID, Request.TerritoryType);

    bool bSuccess = true;

    // Generate based on requested type
    switch (Request.GenerationType)
    {
        case EProceduralGenerationType::Landscape:
            GenerateLandscapeInternal(Request);
            break;
            
        case EProceduralGenerationType::Buildings:
            GenerateBuildingsInternal(Request);
            break;
            
        case EProceduralGenerationType::Details:
            GenerateDetailsInternal(Request);
            break;
            
        case EProceduralGenerationType::Vegetation:
            GenerateVegetationInternal(Request);
            break;
            
        case EProceduralGenerationType::All:
            GenerateLandscapeInternal(Request);
            GenerateBuildingsInternal(Request);
            GenerateDetailsInternal(Request);
            GenerateVegetationInternal(Request);
            break;
    }

    // Broadcast completion
    OnTerrainGenerated.Broadcast(Request.TerritoryID, bSuccess);

    return bSuccess;
}

void UTGProceduralWorldSubsystem::RegenerateTerritory(int32 TerritoryID, ELocalTerritoryType TerritoryType, ELocalFactionID NewDominantFaction)
{
    // Get territorial info if available
    FProceduralGenerationRequest Request;
    Request.TerritoryID = TerritoryID;
    Request.TerritoryType = TerritoryType;
    Request.DominantFaction = NewDominantFaction;
    Request.GenerationType = EProceduralGenerationType::All;

    // TODO: Get actual center location from TerritorialManager
    Request.CenterLocation = FVector::ZeroVector;
    Request.GenerationRadius = DefaultGenerationRadius;

    GenerateTerritory(Request);
}

void UTGProceduralWorldSubsystem::ClearTerritoryGeneration(int32 TerritoryID, ELocalTerritoryType TerritoryType)
{
    FString TerritoryKey = GetTerritoryKey(TerritoryID, TerritoryType);
    
    if (FGeneratedActorArray* ActorArray = GeneratedActorsByTerritory.Find(TerritoryKey))
    {
        for (TWeakObjectPtr<AActor> ActorPtr : ActorArray->Actors)
        {
            if (ActorPtr.IsValid())
            {
                ActorPtr->Destroy();
            }
        }
        GeneratedActorsByTerritory.Remove(TerritoryKey);
    }
}

bool UTGProceduralWorldSubsystem::GenerateLandscapeForTerritory(const FTerritorialInfo& TerritoryInfo, const FVector& Location, float Radius)
{
    // This would integrate with UE5's landscape system
    // For now, create basic terrain modifications
    ApplyFactionLandscapeModifications(Location, Radius, TerritoryInfo.DominantFaction);
    CreateFactionLighting(Location, TerritoryInfo.DominantFaction);
    
    UE_LOG(LogTemp, Log, TEXT("Generated landscape for territory %d at %s"), TerritoryInfo.TerritoryID, *Location.ToString());
    return true;
}

TArray<AActor*> UTGProceduralWorldSubsystem::PlaceFactionBuildings(const FTerritorialInfo& TerritoryInfo, 
                                                                 const FVector& CenterLocation, 
                                                                 float Radius,
                                                                 int32 BuildingCount)
{
    TArray<AActor*> PlacedBuildings;
    FRandomStream RandomStream = GetTerritoryRandomStream(TerritoryInfo.TerritoryID);

    for (int32 i = 0; i < BuildingCount; i++)
    {
        // Calculate building placement using circular distribution
        FVector BuildingLocation = CalculateBuildingPlacement(CenterLocation, Radius, i, BuildingCount);
        
        // Vary building types based on territory type
        EControlPointType BuildingType = EControlPointType::Checkpoint;
        switch (TerritoryInfo.ResourceType)
        {
            case ETerritoryResourceType::Military:
                BuildingType = (i % 3 == 0) ? EControlPointType::CommandPost : EControlPointType::Watchtower;
                break;
            case ETerritoryResourceType::Economic:
                BuildingType = (i % 3 == 0) ? EControlPointType::SupplyDepot : EControlPointType::Checkpoint;
                break;
            case ETerritoryResourceType::Strategic:
                BuildingType = EControlPointType::CommandPost;
                break;
        }

        // Place the building
        AActor* PlacedBuilding = PlaceSingleBuilding(BuildingLocation, TerritoryInfo.DominantFaction, BuildingType);
        if (PlacedBuilding)
        {
            PlacedBuildings.Add(PlacedBuilding);
            RegisterGeneratedActor(TerritoryInfo.TerritoryID, TerritoryInfo.TerritoryType, PlacedBuilding);
            
            // Broadcast building placement
            OnBuildingPlaced.Broadcast(TerritoryInfo.TerritoryID, TerritoryInfo.DominantFaction, BuildingLocation);
        }
    }

    return PlacedBuildings;
}

AActor* UTGProceduralWorldSubsystem::PlaceSingleBuilding(const FVector& Location, EFactionID ControllingFaction, EControlPointType BuildingType)
{
    // Get faction building profile
    FFactionBuildingProfile* Profile = FactionProfiles.Find(ControllingFaction);
    if (!Profile)
    {
        UE_LOG(LogTemp, Warning, TEXT("No building profile found for faction %d"), (int32)ControllingFaction);
        return nullptr;
    }

    // Select appropriate mesh for building type
    UStaticMesh* SelectedMesh = SelectFactionMesh(ControllingFaction, BuildingType);
    if (!SelectedMesh)
    {
        UE_LOG(LogTemp, Warning, TEXT("No mesh available for faction %d building type %d"), (int32)ControllingFaction, (int32)BuildingType);
        return nullptr;
    }

    // Create building actor
    AStaticMeshActor* BuildingActor = GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Location, FRotator::ZeroRotator);
    if (BuildingActor)
    {
        // Set mesh
        BuildingActor->GetStaticMeshComponent()->SetStaticMesh(SelectedMesh);
        
        // Apply faction material if available
        UMaterialInterface* FactionMaterial = SelectFactionMaterial(ControllingFaction);
        if (FactionMaterial)
        {
            BuildingActor->GetStaticMeshComponent()->SetMaterial(0, FactionMaterial);
        }

        // Set building name for identification
        FString BuildingName = FString::Printf(TEXT("Procedural_%s_%s_%d"), 
                                             *UEnum::GetValueAsString(ControllingFaction),
                                             *UEnum::GetValueAsString(BuildingType),
                                             FMath::Rand());
        BuildingActor->SetActorLabel(BuildingName);

        UE_LOG(LogTemp, Log, TEXT("Placed %s building at %s"), *BuildingName, *Location.ToString());
    }

    return BuildingActor;
}

void UTGProceduralWorldSubsystem::GenerateLandscapeInternal(const FProceduralGenerationRequest& Request)
{
    // Placeholder for landscape generation
    // This would interface with UE5's landscape system or procedural mesh generation
    UE_LOG(LogTemp, Log, TEXT("Generated landscape for territory %d"), Request.TerritoryID);
}

void UTGProceduralWorldSubsystem::GenerateBuildingsInternal(const FProceduralGenerationRequest& Request)
{
    // Get territorial info for building placement
    FTerritorialInfo TerritoryInfo;
    TerritoryInfo.TerritoryID = Request.TerritoryID;
    TerritoryInfo.TerritoryType = Request.TerritoryType;
    TerritoryInfo.DominantFaction = Request.DominantFaction;
    TerritoryInfo.ResourceType = ETerritoryResourceType::Strategic; // Default

    // Place buildings
    PlaceFactionBuildings(TerritoryInfo, Request.CenterLocation, Request.GenerationRadius, DefaultBuildingsPerTerritory);
}

void UTGProceduralWorldSubsystem::GenerateDetailsInternal(const FProceduralGenerationRequest& Request)
{
    // Placeholder for detail generation (props, decals, etc.)
    UE_LOG(LogTemp, Log, TEXT("Generated details for territory %d"), Request.TerritoryID);
}

void UTGProceduralWorldSubsystem::GenerateVegetationInternal(const FProceduralGenerationRequest& Request)
{
    // Placeholder for vegetation/foliage generation
    UE_LOG(LogTemp, Log, TEXT("Generated vegetation for territory %d"), Request.TerritoryID);
}

UStaticMesh* UTGProceduralWorldSubsystem::SelectFactionMesh(EFactionID FactionID, EControlPointType BuildingType) const
{
    // This would select from actual mesh libraries
    // For now, return nullptr to indicate placeholder
    return nullptr;
}

UMaterialInterface* UTGProceduralWorldSubsystem::SelectFactionMaterial(EFactionID FactionID) const
{
    // This would select from faction material libraries
    // For now, return nullptr to use default materials
    return nullptr;
}

FVector UTGProceduralWorldSubsystem::CalculateBuildingPlacement(const FVector& CenterLocation, float Radius, int32 BuildingIndex, int32 TotalBuildings) const
{
    // Distribute buildings in a circle around the center
    float AngleStep = 360.0f / FMath::Max(1, TotalBuildings);
    float CurrentAngle = AngleStep * BuildingIndex;
    
    // Add some randomization
    float RandomRadius = Radius * FMath::RandRange(0.3f, 0.9f);
    float RandomAngle = CurrentAngle + FMath::RandRange(-15.0f, 15.0f);
    
    FVector Offset = FVector(
        RandomRadius * FMath::Cos(FMath::DegreesToRadians(RandomAngle)),
        RandomRadius * FMath::Sin(FMath::DegreesToRadians(RandomAngle)),
        0.0f
    );
    
    return CenterLocation + Offset;
}

void UTGProceduralWorldSubsystem::ApplyFactionLandscapeModifications(const FVector& Location, float Radius, EFactionID FactionID)
{
    // Placeholder for landscape modifications
    // This would modify heightmaps, apply materials, etc. based on faction
}

void UTGProceduralWorldSubsystem::CreateFactionLighting(const FVector& Location, EFactionID FactionID)
{
    // Placeholder for faction-specific lighting
    // Would place lights with faction colors
}

void UTGProceduralWorldSubsystem::RegisterGeneratedActor(int32 TerritoryID, ELocalTerritoryType TerritoryType, AActor* Actor)
{
    if (!Actor) return;

    FString TerritoryKey = GetTerritoryKey(TerritoryID, TerritoryType);
    GeneratedActorsByTerritory.FindOrAdd(TerritoryKey).Actors.Add(Actor);
}

void UTGProceduralWorldSubsystem::UnregisterTerritoryActors(int32 TerritoryID, ELocalTerritoryType TerritoryType)
{
    FString TerritoryKey = GetTerritoryKey(TerritoryID, TerritoryType);
    GeneratedActorsByTerritory.Remove(TerritoryKey);
}

FString UTGProceduralWorldSubsystem::GetTerritoryKey(int32 TerritoryID, ELocalTerritoryType TerritoryType) const
{
    return FString::Printf(TEXT("%d_%d"), TerritoryID, (int32)TerritoryType);
}

FRandomStream UTGProceduralWorldSubsystem::GetTerritoryRandomStream(int32 TerritoryID, int32 Seed) const
{
    int32 CombinedSeed = TerritoryID * 1000 + Seed;
    return FRandomStream(CombinedSeed);
}

void UTGProceduralWorldSubsystem::SetFactionBuildingProfile(EFactionID FactionID, const FFactionBuildingProfile& Profile)
{
    FactionProfiles.Add(FactionID, Profile);
}

FFactionBuildingProfile UTGProceduralWorldSubsystem::GetFactionBuildingProfile(EFactionID FactionID) const
{
    if (const FFactionBuildingProfile* Profile = FactionProfiles.Find(FactionID))
    {
        return *Profile;
    }
    return FFactionBuildingProfile(); // Return default profile
}

bool UTGProceduralWorldSubsystem::IsTerritorGenerated(int32 TerritoryID, ETerritoryType TerritoryType) const
{
    FString TerritoryKey = GetTerritoryKey(TerritoryID, TerritoryType);
    return GeneratedActorsByTerritory.Contains(TerritoryKey);
}

TArray<AActor*> UTGProceduralWorldSubsystem::GetGeneratedActorsInTerritory(int32 TerritoryID, ELocalTerritoryType TerritoryType) const
{
    TArray<AActor*> ValidActors;
    FString TerritoryKey = GetTerritoryKey(TerritoryID, TerritoryType);
    
    if (const FGeneratedActorArray* ActorArray = GeneratedActorsByTerritory.Find(TerritoryKey))
    {
        for (const TWeakObjectPtr<AActor>& ActorPtr : ActorArray->Actors)
        {
            if (ActorPtr.IsValid())
            {
                ValidActors.Add(ActorPtr.Get());
            }
        }
    }
    
    return ValidActors;
}

void UTGProceduralWorldSubsystem::OnTerritorialInfluenceChanged(int32 TerritoryID, ELocalTerritoryType TerritoryType, int32 NewDominantFaction)
{
    if (bAutoGenerateOnTerritorialChange)
    {
        RegenerateTerritory(TerritoryID, TerritoryType, (ELocalFactionID)NewDominantFaction);
    }
}