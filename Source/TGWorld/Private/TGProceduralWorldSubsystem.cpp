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

// Utility functions to convert between local and canonical types
EFactionID ConvertToCanonicalFaction(ELocalFactionID LocalFaction)
{
    switch (LocalFaction)
    {
        case ELocalFactionID::None: return EFactionID::None;
        case ELocalFactionID::Directorate: return EFactionID::Directorate;
        case ELocalFactionID::Free77: return EFactionID::Free77;
        case ELocalFactionID::CivicWardens: return EFactionID::CivicWardens;
        case ELocalFactionID::NomadClans: return EFactionID::NomadClans;
        case ELocalFactionID::VulturesUnion: return EFactionID::VulturesUnion;
        case ELocalFactionID::CorporateCombine: return EFactionID::CorporateCombine;
        case ELocalFactionID::VaultedArchivists: return EFactionID::VaultedArchivists;
        default: return EFactionID::None;
    }
}

EControlPointType ConvertToCanonicalControlPoint(ELocalControlPointType LocalType)
{
    switch (LocalType)
    {
        case ELocalControlPointType::CommandPost: return EControlPointType::CommandPost;
        case ELocalControlPointType::Checkpoint: return EControlPointType::Checkpoint;
        case ELocalControlPointType::Watchtower: return EControlPointType::CommArray; // Map Watchtower to CommArray
        case ELocalControlPointType::SupplyDepot: return EControlPointType::SupplyDepot;
        default: return EControlPointType::Checkpoint;
    }
}

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
    // Generate detail objects like crates, barrels, and props
    FRandomStream RandomStream = GetTerritoryRandomStream(Request.TerritoryID);
    
    // Spawn random detail objects around the territory center
    int32 NumDetails = RandomStream.RandRange(10, 20);
    
    for (int32 i = 0; i < NumDetails; i++)
    {
        // Random position within generation radius
        FVector RandomOffset = FVector(
            RandomStream.FRandRange(-Request.GenerationRadius * 0.8f, Request.GenerationRadius * 0.8f),
            RandomStream.FRandRange(-Request.GenerationRadius * 0.8f, Request.GenerationRadius * 0.8f),
            0.0f
        );
        
        FVector SpawnLocation = Request.CenterLocation + RandomOffset;
        
        // Line trace to ground
        FHitResult HitResult;
        FVector TraceStart = SpawnLocation + FVector(0, 0, 1000.0f);
        FVector TraceEnd = SpawnLocation - FVector(0, 0, 1000.0f);
        
        if (GetWorld()->LineTraceSingleByChannel(HitResult, TraceStart, TraceEnd, ECC_WorldStatic))
        {
            SpawnLocation = HitResult.Location;
        }
        
        // Select appropriate detail mesh (using engine primitives for now)
        UStaticMesh* DetailMesh = nullptr;
        
        // Try to load basic shapes for details
        int32 MeshType = RandomStream.RandRange(0, 2);
        switch (MeshType)
        {
            case 0:
                DetailMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
                break;
            case 1:
                DetailMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
                break;
            case 2:
                DetailMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
                break;
        }
        
        if (DetailMesh)
        {
            // Spawn static mesh actor
            AStaticMeshActor* DetailActor = GetWorld()->SpawnActor<AStaticMeshActor>(
                AStaticMeshActor::StaticClass(),
                SpawnLocation,
                FRotator(0, RandomStream.FRandRange(0.0f, 360.0f), 0)
            );
            
            if (DetailActor && DetailActor->GetStaticMeshComponent())
            {
                DetailActor->GetStaticMeshComponent()->SetStaticMesh(DetailMesh);
                
                // Apply faction coloring if available
                if (UMaterialInterface* FactionMaterial = SelectFactionMaterial(Request.DominantFaction))
                {
                    DetailActor->GetStaticMeshComponent()->SetMaterial(0, FactionMaterial);
                }
                
                // Scale detail objects
                float Scale = RandomStream.FRandRange(0.5f, 2.0f);
                DetailActor->SetActorScale3D(FVector(Scale));
                
                // Register for cleanup
                RegisterGeneratedActor(Request.TerritoryID, Request.TerritoryType, DetailActor);
            }
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("Generated %d detail objects for territory %d"), NumDetails, Request.TerritoryID);
}

void UTGProceduralWorldSubsystem::GenerateVegetationInternal(const FProceduralGenerationRequest& Request)
{
    // Generate vegetation based on territory resource type
    FRandomStream RandomStream = GetTerritoryRandomStream(Request.TerritoryID);
    
    // Different vegetation density based on faction and resource type
    int32 VegetationCount = 0;
    
    // Economic territories get more vegetation (civilian areas)
    // Military territories get less (more industrial)
    // Strategic territories get minimal (high security areas)
    switch (Request.DominantFaction)
    {
        case ELocalFactionID::CivicWardens:
            VegetationCount = RandomStream.RandRange(15, 25); // More maintained vegetation
            break;
        case ELocalFactionID::NomadClans:
            VegetationCount = RandomStream.RandRange(20, 30); // Natural growth
            break;
        case ELocalFactionID::Directorate:
            VegetationCount = RandomStream.RandRange(5, 10);  // Minimal, controlled
            break;
        case ELocalFactionID::Free77:
            VegetationCount = RandomStream.RandRange(8, 15);  // Some overgrowth
            break;
        case ELocalFactionID::VulturesUnion:
            VegetationCount = RandomStream.RandRange(12, 18); // Scavenged areas
            break;
        default:
            VegetationCount = RandomStream.RandRange(10, 15); // Default amount
            break;
    }
    
    for (int32 i = 0; i < VegetationCount; i++)
    {
        // Random position within generation radius
        FVector RandomOffset = FVector(
            RandomStream.FRandRange(-Request.GenerationRadius * 0.9f, Request.GenerationRadius * 0.9f),
            RandomStream.FRandRange(-Request.GenerationRadius * 0.9f, Request.GenerationRadius * 0.9f),
            0.0f
        );
        
        FVector SpawnLocation = Request.CenterLocation + RandomOffset;
        
        // Line trace to ground
        FHitResult HitResult;
        FVector TraceStart = SpawnLocation + FVector(0, 0, 1000.0f);
        FVector TraceEnd = SpawnLocation - FVector(0, 0, 1000.0f);
        
        if (GetWorld()->LineTraceSingleByChannel(HitResult, TraceStart, TraceEnd, ECC_WorldStatic))
        {
            SpawnLocation = HitResult.Location;
        }
        
        // Use engine foliage meshes as placeholders
        UStaticMesh* VegetationMesh = nullptr;
        
        // Try different vegetation types
        TArray<FString> VegetationPaths = {
            TEXT("/Game/StarterContent/Props/SM_Bush.SM_Bush"),
            TEXT("/Engine/BasicShapes/Cylinder.Cylinder") // Fallback
        };
        
        for (const FString& Path : VegetationPaths)
        {
            VegetationMesh = LoadObject<UStaticMesh>(nullptr, *Path);
            if (VegetationMesh)
            {
                break;
            }
        }
        
        if (VegetationMesh)
        {
            // Spawn vegetation
            AStaticMeshActor* VegetationActor = GetWorld()->SpawnActor<AStaticMeshActor>(
                AStaticMeshActor::StaticClass(),
                SpawnLocation,
                FRotator(0, RandomStream.FRandRange(0.0f, 360.0f), 0)
            );
            
            if (VegetationActor && VegetationActor->GetStaticMeshComponent())
            {
                VegetationActor->GetStaticMeshComponent()->SetStaticMesh(VegetationMesh);
                
                // Vary vegetation scale
                float Scale = RandomStream.FRandRange(0.8f, 1.5f);
                VegetationActor->SetActorScale3D(FVector(Scale));
                
                // Register for cleanup
                RegisterGeneratedActor(Request.TerritoryID, Request.TerritoryType, VegetationActor);
            }
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("Generated %d vegetation objects for territory %d"), VegetationCount, Request.TerritoryID);
}

UStaticMesh* UTGProceduralWorldSubsystem::SelectFactionMesh(ELocalFactionID FactionID, ELocalControlPointType BuildingType) const
{
    // Convert to canonical types
    EFactionID CanonicalFaction = ConvertToCanonicalFaction(FactionID);
    EControlPointType CanonicalBuildingType = ConvertToCanonicalControlPoint(BuildingType);
    
    // Load appropriate meshes based on faction and building type
    UStaticMesh* SelectedMesh = nullptr;
    
    // Try to load from available asset libraries
    TArray<FString> MeshPaths;
    
    switch (BuildingType)
    {
        case ELocalControlPointType::CommandPost:
            // Use larger structures for command posts
            MeshPaths = {
                TEXT("/Game/Construction_VOL1/Meshes/SM_Construction_MainStructure"),
                TEXT("/Game/Construction_VOL2/Meshes/SM_Construction_HQ"),
                TEXT("/Game/kb3d_missiontominerva/Meshes/KB3D_MTM_BldgLgCommsArray_A_Building_01a"),
                TEXT("/Engine/BasicShapes/Cube.Cube") // Fallback
            };
            break;
            
        case ELocalControlPointType::Checkpoint:
            // Use smaller guard structures
            MeshPaths = {
                TEXT("/Game/Construction_VOL1/Meshes/SM_Construction_Checkpoint"),
                TEXT("/Game/Construction_VOL2/Meshes/SM_Construction_GuardPost"), 
                TEXT("/Game/ProceduralBuildingGenerator/Meshes/PBG_Structure_Small"),
                TEXT("/Engine/BasicShapes/Cylinder.Cylinder") // Fallback
            };
            break;
            
        case ELocalControlPointType::Watchtower:
            // Use tall observation structures
            MeshPaths = {
                TEXT("/Game/Construction_VOL1/Meshes/SM_Construction_Tower"),
                TEXT("/Game/kb3d_missiontominerva/Meshes/KB3D_MTM_BldgLgCommsArray_A_BaseStructure01"),
                TEXT("/Game/ProceduralBuildingGenerator/Meshes/PBG_Structure_Tall"),
                TEXT("/Engine/BasicShapes/Cylinder.Cylinder") // Fallback
            };
            break;
            
        case ELocalControlPointType::SupplyDepot:
            // Use warehouse/storage structures
            MeshPaths = {
                TEXT("/Game/Construction_VOL2/Meshes/SM_Construction_Warehouse"),
                TEXT("/Game/kb3d_missiontominerva/Meshes/KB3D_MTM_BldgLgCommunityCenter_A_Building_01a"),
                TEXT("/Game/ProceduralBuildingGenerator/Meshes/PBG_Structure_Wide"),
                TEXT("/Engine/BasicShapes/Cube.Cube") // Fallback
            };
            break;
            
        default:
            // Default to basic structure
            MeshPaths = {
                TEXT("/Engine/BasicShapes/Cube.Cube")
            };
            break;
    }
    
    // Try to load first available mesh
    for (const FString& MeshPath : MeshPaths)
    {
        SelectedMesh = LoadObject<UStaticMesh>(nullptr, *MeshPath);
        if (SelectedMesh)
        {
            UE_LOG(LogTemp, Log, TEXT("Selected mesh %s for faction %d building type %d"), 
                   *MeshPath, (int32)FactionID, (int32)BuildingType);
            break;
        }
    }
    
    return SelectedMesh;
}

UMaterialInterface* UTGProceduralWorldSubsystem::SelectFactionMaterial(ELocalFactionID FactionID) const
{
    // Convert to canonical type
    EFactionID CanonicalFaction = ConvertToCanonicalFaction(FactionID);
    
    // Load faction-specific materials based on available assets
    UMaterialInterface* FactionMaterial = nullptr;
    
    // Try to load faction materials from the Terminal Grounds assets
    FString MaterialPath;
    
    switch (FactionID)
    {
        case ELocalFactionID::Directorate:
            // Corporate blue materials
            MaterialPath = TEXT("/Game/TG/Materials/Human/M_TG_Human_Master");
            break;
            
        case ELocalFactionID::Free77:
            // Resistance red materials  
            MaterialPath = TEXT("/Game/TG/Materials/Human/M_TG_Human_Master");
            break;
            
        case ELocalFactionID::CivicWardens:
            // Neutral maintenance materials
            MaterialPath = TEXT("/Game/TG/Materials/Human/M_TG_Human_Master");
            break;
            
        case ELocalFactionID::NomadClans:
            // Improvised materials
            MaterialPath = TEXT("/Game/TG/Materials/Hybrid/M_TG_Hybrid_Master");
            break;
            
        case ELocalFactionID::VulturesUnion:
            // Scavenged materials
            MaterialPath = TEXT("/Game/TG/Materials/Alien/M_TG_Alien_Master");
            break;
            
        case ELocalFactionID::CorporateCombine:
            // High-tech corporate materials
            MaterialPath = TEXT("/Game/TG/Materials/Human/M_TG_Human_Master");
            break;
            
        case ELocalFactionID::VaultedArchivists:
            // Archival/preservation materials
            MaterialPath = TEXT("/Game/TG/Materials/Hybrid/M_TG_Hybrid_Master");
            break;
            
        default:
            // Default material
            MaterialPath = TEXT("/Game/TG/Materials/Human/M_TG_Human_Master");
            break;
    }
    
    // Try to load the faction material
    FactionMaterial = LoadObject<UMaterialInterface>(nullptr, *MaterialPath);
    
    if (FactionMaterial)
    {
        UE_LOG(LogTemp, Log, TEXT("Selected faction material %s for faction %d"), 
               *MaterialPath, (int32)FactionID);
    }
    else
    {
        // Try fallback materials
        TArray<FString> FallbackPaths = {
            TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"),
            TEXT("/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial")
        };
        
        for (const FString& FallbackPath : FallbackPaths)
        {
            FactionMaterial = LoadObject<UMaterialInterface>(nullptr, *FallbackPath);
            if (FactionMaterial)
            {
                UE_LOG(LogTemp, Warning, TEXT("Using fallback material %s for faction %d"), 
                       *FallbackPath, (int32)FactionID);
                break;
            }
        }
    }
    
    return FactionMaterial;
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

bool UTGProceduralWorldSubsystem::IsTerritorGenerated(int32 TerritoryID, ELocalTerritoryType TerritoryType) const
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