#include "TGTerritorialProceduralSystem.h"
#include "TGCore.h"
#include "TGWorld/Public/TGTerritorialManager.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Engine/Engine.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"
#include "NavigationSystem.h"
#include "AI/NavigationSystemBase.h"

UTGTerritorialProceduralSystem::UTGTerritorialProceduralSystem()
{
    TerritorialManager = nullptr;
    ProceduralArena = nullptr;
    TerritorialWebSocket = nullptr;
}

void UTGTerritorialProceduralSystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    UE_LOG(LogTGCore, Log, TEXT("Initializing Territorial Procedural System"));
    
    // Get reference to Territorial Manager
    TerritorialManager = GetWorld()->GetSubsystem<UTGTerritorialManager>();
    if (!TerritorialManager)
    {
        UE_LOG(LogTGCore, Error, TEXT("Failed to get Territorial Manager subsystem"));
        return;
    }

    // Initialize the system
    if (!InitializeTerritorialProceduralSystem())
    {
        UE_LOG(LogTGCore, Error, TEXT("Failed to initialize Territorial Procedural System"));
        return;
    }

    // Register for territorial events
    RegisterTerritorialEvents();

    // Connect to WebSocket for real-time updates
    ConnectToTerritorialWebSocket();

    // Set up periodic update timers
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(TerritorialUpdateTimer,
            FTimerDelegate::CreateUObject(this, &UTGTerritorialProceduralSystem::ProcessPendingModifications),
            TerritorialUpdateInterval, true);
            
        World->GetTimerManager().SetTimer(AssetGenerationTimer,
            FTimerDelegate::CreateUObject(this, &UTGTerritorialProceduralSystem::ProcessSeasonalTerritorialEvolution),
            30.0f, true); // Check seasonal changes every 30 seconds
    }

    UE_LOG(LogTGCore, Log, TEXT("Territorial Procedural System initialized successfully"));
}

void UTGTerritorialProceduralSystem::Deinitialize()
{
    UE_LOG(LogTGCore, Log, TEXT("Deinitializing Territorial Procedural System"));

    // Clear timers
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(TerritorialUpdateTimer);
        World->GetTimerManager().ClearTimer(AssetGenerationTimer);
        World->GetTimerManager().ClearTimer(PerformanceOptimizationTimer);
    }

    // Clear all territorial modifications
    FScopeLock Lock(&TerritorialModificationMutex);
    for (auto& ModPair : TerritorialModifications)
    {
        ClearTerritorialAssets(ModPair.Key);
    }
    TerritorialModifications.Empty();

    // Clean up WebSocket
    if (TerritorialWebSocket)
    {
        TerritorialWebSocket = nullptr;
    }

    Super::Deinitialize();
}

bool UTGTerritorialProceduralSystem::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

bool UTGTerritorialProceduralSystem::InitializeTerritorialProceduralSystem()
{
    UE_LOG(LogTGCore, Log, TEXT("Initializing Territorial Procedural System components"));

    // Initialize faction asset libraries
    InitializeFactionAssetLibraries();

    // Find existing procedural arena in world
    if (UWorld* World = GetWorld())
    {
        for (TActorIterator<ATGProceduralArena> ActorIterator(World); ActorIterator; ++ActorIterator)
        {
            ProceduralArena = *ActorIterator;
            break;
        }
    }

    if (!ProceduralArena)
    {
        UE_LOG(LogTGCore, Warning, TEXT("No Procedural Arena found in world - territorial modifications will be limited"));
    }

    // Initialize protected gameplay areas from procedural arena data
    if (ProceduralArena)
    {
        ProtectedGameplayAreas.Empty();
        
        // Add capture node locations as protected areas
        for (ATGCaptureNode* CaptureNode : ProceduralArena->SpawnedCaptureNodes)
        {
            if (CaptureNode)
            {
                ProtectedGameplayAreas.Add(CaptureNode->GetActorLocation());
            }
        }

        // Add extraction pad location as protected area
        if (ProceduralArena->SpawnedExtractionPad)
        {
            ProtectedGameplayAreas.Add(ProceduralArena->SpawnedExtractionPad->GetActorLocation());
        }

        UE_LOG(LogTGCore, Log, TEXT("Protected %d gameplay areas from procedural modifications"), ProtectedGameplayAreas.Num());
    }

    return true;
}

void UTGTerritorialProceduralSystem::InitializeFactionAssetLibraries()
{
    // Initialize faction asset libraries with Terminal Grounds faction data
    FTGFactionAssetLibrary CorporateLibrary;
    CorporateLibrary.FactionPrimaryColor = FLinearColor(0.0f, 0.76f, 1.0f, 1.0f); // #00C2FF
    CorporateLibrary.FactionSecondaryColor = FLinearColor(0.05f, 0.06f, 0.07f, 1.0f); // #0C0F12
    FactionAssetLibraries.Add(1, CorporateLibrary); // Corporate Hegemony

    FTGFactionAssetLibrary Free77Library;
    Free77Library.FactionPrimaryColor = FLinearColor(0.74f, 0.76f, 0.78f, 1.0f); // #BDC3C7
    Free77Library.FactionSecondaryColor = FLinearColor(0.20f, 0.29f, 0.37f, 1.0f); // #34495E
    FactionAssetLibraries.Add(2, Free77Library); // The Seventy-Seven

    FTGFactionAssetLibrary IronScavengersLibrary;
    IronScavengersLibrary.FactionPrimaryColor = FLinearColor(0.83f, 0.33f, 0.0f, 1.0f); // #D35400
    IronScavengersLibrary.FactionSecondaryColor = FLinearColor(0.50f, 0.55f, 0.55f, 1.0f); // #7F8C8D
    FactionAssetLibraries.Add(3, IronScavengersLibrary); // Iron Scavengers

    FTGFactionAssetLibrary NomadLibrary;
    NomadLibrary.FactionPrimaryColor = FLinearColor(0.69f, 0.38f, 0.10f, 1.0f); // #AF601A
    NomadLibrary.FactionSecondaryColor = FLinearColor(0.43f, 0.17f, 0.0f, 1.0f); // #6E2C00
    FactionAssetLibraries.Add(4, NomadLibrary); // Nomad Clans

    FTGFactionAssetLibrary ArchiveLibrary;
    ArchiveLibrary.FactionPrimaryColor = FLinearColor(0.56f, 0.27f, 0.68f, 1.0f); // #8E44AD
    ArchiveLibrary.FactionSecondaryColor = FLinearColor(0.17f, 0.24f, 0.31f, 1.0f); // #2C3E50
    FactionAssetLibraries.Add(5, ArchiveLibrary); // Archive Keepers

    FTGFactionAssetLibrary CivicLibrary;
    CivicLibrary.FactionPrimaryColor = FLinearColor(0.15f, 0.68f, 0.38f, 1.0f); // #27AE60
    CivicLibrary.FactionSecondaryColor = FLinearColor(0.08f, 0.35f, 0.20f, 1.0f); // #145A32
    FactionAssetLibraries.Add(6, CivicLibrary); // Civic Wardens

    UE_LOG(LogTGCore, Log, TEXT("Initialized %d faction asset libraries"), FactionAssetLibraries.Num());
}

void UTGTerritorialProceduralSystem::RegisterTerritorialEvents()
{
    if (TerritorialManager)
    {
        // Bind to territorial control change events
        TerritorialManager->OnTerritoryControlChanged.AddDynamic(this, &UTGTerritorialProceduralSystem::ProcessTerritorialChange);

        UE_LOG(LogTGCore, Log, TEXT("Registered for territorial control change events"));
    }
}

void UTGTerritorialProceduralSystem::ProcessTerritorialChange(int32 TerritoryId, int32 OldFactionId, int32 NewFactionId)
{
    UE_LOG(LogTGCore, Log, TEXT("Processing territorial change: Territory %d from Faction %d to Faction %d"), 
        TerritoryId, OldFactionId, NewFactionId);

    // Clear existing territorial assets
    ClearTerritorialAssets(TerritoryId);

    // Determine modification type based on faction change
    ETGTerritorialModificationType ModType = ETGTerritorialModificationType::Cosmetic;
    
    if (NewFactionId != 0) // Not neutral
    {
        FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(TerritoryId);
        
        if (TerritoryData.StrategicValue >= 7)
        {
            ModType = ETGTerritorialModificationType::StructuralChange;
        }
        else if (TerritoryData.StrategicValue >= 4)
        {
            ModType = ETGTerritorialModificationType::AssetPlacement;
        }
    }

    // Create territorial modification
    FTGTerritorialModification NewModification;
    NewModification.TerritoryId = TerritoryId;
    NewModification.ControllingFactionId = NewFactionId;
    NewModification.ModificationType = ModType;
    NewModification.ArchitecturalStyle = GetFactionArchitecturalStyle(NewFactionId);
    NewModification.LastModificationTime = FDateTime::Now();

    // Apply modification
    if (ApplyTerritorialModification(NewModification))
    {
        // Broadcast generation started event
        OnTerritorialProcGenerationStarted.Broadcast(TerritoryId, NewFactionId, ModType);

        // Request territorial assets if needed
        if (ModType != ETGTerritorialModificationType::None)
        {
            RequestTerritorialAssets(TerritoryId, NewFactionId, ModType);
        }
    }
}

bool UTGTerritorialProceduralSystem::ApplyTerritorialModification(const FTGTerritorialModification& Modification)
{
    // Validate modification first
    if (!ValidateTerritorialModification(Modification))
    {
        UE_LOG(LogTGCore, Warning, TEXT("Territorial modification validation failed for Territory %d"), 
            Modification.TerritoryId);
        return false;
    }

    // Apply modification based on type
    switch (Modification.ModificationType)
    {
        case ETGTerritorialModificationType::Cosmetic:
            return ApplyFactionCosmetics(Modification);
            
        case ETGTerritorialModificationType::AssetPlacement:
            return ApplyDynamicAssetPlacement(Modification);
            
        case ETGTerritorialModificationType::StructuralChange:
            return ApplyStructuralModifications(Modification);
            
        default:
            return true;
    }
}

bool UTGTerritorialProceduralSystem::ApplyFactionCosmetics(const FTGTerritorialModification& Modification)
{
    // Apply cosmetic faction elements: banners, signage, lighting
    FTGFactionAssetLibrary FactionLibrary = GetFactionAssetLibrary(Modification.ControllingFactionId);
    
    // Find valid placement locations for cosmetic elements
    TArray<FVector> PlacementLocations = GetValidPlacementLocations(Modification.TerritoryId, 
        ETGTerritorialModificationType::Cosmetic);

    int32 PlacedAssets = 0;
    const int32 MaxCosmeticAssets = 5;

    for (const FVector& Location : PlacementLocations)
    {
        if (PlacedAssets >= MaxCosmeticAssets) break;

        // Spawn faction banner
        if (FactionLibrary.BP_FactionBanner)
        {
            AActor* Banner = GetWorld()->SpawnActor<AActor>(FactionLibrary.BP_FactionBanner, Location, FRotator::ZeroRotator);
            if (Banner)
            {
                ApplyFactionStyling(Banner, Modification.ControllingFactionId);
                PlacedAssets++;
            }
        }
    }

    UE_LOG(LogTGCore, Log, TEXT("Applied cosmetic modifications: %d assets placed for Territory %d"), 
        PlacedAssets, Modification.TerritoryId);

    return PlacedAssets > 0;
}

bool UTGTerritorialProceduralSystem::ApplyDynamicAssetPlacement(const FTGTerritorialModification& Modification)
{
    // Apply dynamic asset placement: barriers, supply caches, communication relays
    FTGFactionAssetLibrary FactionLibrary = GetFactionAssetLibrary(Modification.ControllingFactionId);
    
    TArray<FVector> PlacementLocations = GetValidPlacementLocations(Modification.TerritoryId,
        ETGTerritorialModificationType::AssetPlacement);

    int32 PlacedAssets = 0;
    const int32 MaxDynamicAssets = 8;

    for (const FVector& Location : PlacementLocations)
    {
        if (PlacedAssets >= MaxDynamicAssets) break;

        // Determine asset type based on strategic positioning
        TSubclassOf<AActor> AssetClass = nullptr;
        
        if (PlacedAssets % 3 == 0 && FactionLibrary.BP_DefensiveBarrier)
        {
            AssetClass = FactionLibrary.BP_DefensiveBarrier;
        }
        else if (PlacedAssets % 3 == 1 && FactionLibrary.BP_SupplyCache)
        {
            AssetClass = FactionLibrary.BP_SupplyCache;
        }
        else if (PlacedAssets % 3 == 2 && FactionLibrary.BP_CommunicationRelay)
        {
            AssetClass = FactionLibrary.BP_CommunicationRelay;
        }

        if (AssetClass)
        {
            AActor* Asset = GetWorld()->SpawnActor<AActor>(AssetClass, Location, FRotator::ZeroRotator);
            if (Asset)
            {
                ApplyFactionStyling(Asset, Modification.ControllingFactionId);
                PlacedAssets++;
            }
        }
    }

    UE_LOG(LogTGCore, Log, TEXT("Applied dynamic asset placement: %d assets placed for Territory %d"), 
        PlacedAssets, Modification.TerritoryId);

    return PlacedAssets > 0;
}

bool UTGTerritorialProceduralSystem::ApplyStructuralModifications(const FTGTerritorialModification& Modification)
{
    // Apply structural modifications: doors, checkpoints, fortifications
    if (!ProceduralArena)
    {
        UE_LOG(LogTGCore, Warning, TEXT("Cannot apply structural modifications without Procedural Arena reference"));
        return false;
    }

    FTGFactionAssetLibrary FactionLibrary = GetFactionAssetLibrary(Modification.ControllingFactionId);
    
    // Find connection points in the procedural arena for structural modifications
    TArray<FVector> StructuralLocations;
    
    // Get existing lego snap points from procedural arena
    for (AActor* Piece : ProceduralArena->SpawnedPieces)
    {
        if (Piece)
        {
            // Add strategic connection points (simplified for this implementation)
            FVector PieceLocation = Piece->GetActorLocation();
            StructuralLocations.Add(PieceLocation + FVector(200, 0, 0)); // East connection
            StructuralLocations.Add(PieceLocation + FVector(-200, 0, 0)); // West connection
        }
    }

    // Filter to valid structural locations
    TArray<FVector> ValidLocations = FilterValidLocations(StructuralLocations, ETGTerritorialModificationType::StructuralChange);

    int32 PlacedStructures = 0;
    const int32 MaxStructuralAssets = 3; // Limited to maintain balance

    for (const FVector& Location : ValidLocations)
    {
        if (PlacedStructures >= MaxStructuralAssets) break;

        // Alternate between different structural elements
        TSubclassOf<AActor> StructureClass = nullptr;
        
        if (PlacedStructures % 3 == 0 && FactionLibrary.BP_SecurityCheckpoint)
        {
            StructureClass = FactionLibrary.BP_SecurityCheckpoint;
        }
        else if (PlacedStructures % 3 == 1 && FactionLibrary.BP_FactionDoor)
        {
            StructureClass = FactionLibrary.BP_FactionDoor;
        }
        else if (PlacedStructures % 3 == 2 && FactionLibrary.BP_FortificationWall)
        {
            StructureClass = FactionLibrary.BP_FortificationWall;
        }

        if (StructureClass)
        {
            AActor* Structure = GetWorld()->SpawnActor<AActor>(StructureClass, Location, FRotator::ZeroRotator);
            if (Structure)
            {
                ApplyFactionStyling(Structure, Modification.ControllingFactionId);
                PlacedStructures++;

                // Rebuild nav mesh to account for structural changes
                if (UNavigationSystemV1* NavSys = UNavigationSystemV1::GetCurrent(GetWorld()))
                {
                    NavSys->Build();
                }
            }
        }
    }

    UE_LOG(LogTGCore, Log, TEXT("Applied structural modifications: %d structures placed for Territory %d"), 
        PlacedStructures, Modification.TerritoryId);

    return PlacedStructures > 0;
}

bool UTGTerritorialProceduralSystem::ValidateTerritorialModification(const FTGTerritorialModification& Modification)
{
    // Check if territory exists
    FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(Modification.TerritoryId);
    if (TerritoryData.TerritoryId == 0)
    {
        UE_LOG(LogTGCore, Warning, TEXT("Territory %d not found"), Modification.TerritoryId);
        return false;
    }

    // Check modification cooldown
    FDateTime CurrentTime = FDateTime::Now();
    if (LastAssetGenerationTime.Contains(Modification.TerritoryId))
    {
        FTimespan TimeSinceLastModification = CurrentTime - LastAssetGenerationTime[Modification.TerritoryId];
        if (TimeSinceLastModification.GetTotalSeconds() < AssetGenerationCooldown)
        {
            UE_LOG(LogTGCore, Log, TEXT("Territorial modification for Territory %d is on cooldown"), Modification.TerritoryId);
            return false;
        }
    }

    // Check concurrent modification limit
    if (TerritorialModifications.Num() >= MaxConcurrentModifications)
    {
        UE_LOG(LogTGCore, Warning, TEXT("Maximum concurrent modifications reached (%d)"), MaxConcurrentModifications);
        return false;
    }

    return true;
}

TArray<FVector> UTGTerritorialProceduralSystem::GetValidPlacementLocations(int32 TerritoryId, ETGTerritorialModificationType ModType)
{
    TArray<FVector> ValidLocations;

    if (!ProceduralArena)
    {
        return ValidLocations;
    }

    // Generate candidate locations based on procedural arena layout
    TArray<FVector> CandidateLocations;

    // Add locations around spawned pieces
    for (AActor* Piece : ProceduralArena->SpawnedPieces)
    {
        if (Piece)
        {
            FVector BaseLocation = Piece->GetActorLocation();
            
            // Add surrounding locations at different distances based on modification type
            float PlacementRadius = (ModType == ETGTerritorialModificationType::Cosmetic) ? 300.0f : 500.0f;
            
            for (int32 i = 0; i < 8; i++)
            {
                float Angle = i * 45.0f * PI / 180.0f;
                FVector Offset = FVector(FMath::Cos(Angle), FMath::Sin(Angle), 0) * PlacementRadius;
                CandidateLocations.Add(BaseLocation + Offset);
            }
        }
    }

    // Filter candidates based on modification type constraints
    ValidLocations = FilterValidLocations(CandidateLocations, ModType);

    UE_LOG(LogTGCore, Log, TEXT("Generated %d valid placement locations for Territory %d"), 
        ValidLocations.Num(), TerritoryId);

    return ValidLocations;
}

TArray<FVector> UTGTerritorialProceduralSystem::FilterValidLocations(const TArray<FVector>& Candidates, ETGTerritorialModificationType ModType)
{
    TArray<FVector> ValidLocations;

    for (const FVector& Candidate : Candidates)
    {
        if (CanPlaceAssetAtLocation(Candidate, ModType))
        {
            ValidLocations.Add(Candidate);
        }
    }

    return ValidLocations;
}

bool UTGTerritorialProceduralSystem::CanPlaceAssetAtLocation(const FVector& Location, ETGTerritorialModificationType ModType)
{
    // Check distance from protected gameplay areas
    for (const FVector& ProtectedArea : ProtectedGameplayAreas)
    {
        float Distance = FVector::Dist(Location, ProtectedArea);
        
        if (Distance < MinDistanceFromCaptureNodes)
        {
            return false;
        }
    }

    // Check if location is in protected area
    if (IsLocationInProtectedArea(Location))
    {
        return false;
    }

    // Additional checks based on modification type
    if (ModType == ETGTerritorialModificationType::StructuralChange)
    {
        // Ensure structural modifications don't block critical paths
        if (CalculateSightlineImpact(Location, FVector(200, 200, 200)) > MaxSightlineBlockagePercentage)
        {
            return false;
        }
    }

    return true;
}

bool UTGTerritorialProceduralSystem::IsLocationInProtectedArea(const FVector& Location)
{
    for (const FVector& ProtectedArea : ProtectedGameplayAreas)
    {
        if (FVector::Dist(Location, ProtectedArea) < MinDistanceFromCaptureNodes)
        {
            return true;
        }
    }
    return false;
}

float UTGTerritorialProceduralSystem::CalculateSightlineImpact(const FVector& Location, const FVector& AssetBounds)
{
    // Simplified sightline impact calculation
    // In production, this would use more sophisticated ray tracing
    
    float ImpactPercentage = 0.0f;
    
    // Check sightlines between capture nodes
    for (int32 i = 0; i < ProtectedGameplayAreas.Num() - 1; i++)
    {
        for (int32 j = i + 1; j < ProtectedGameplayAreas.Num(); j++)
        {
            FVector StartPoint = ProtectedGameplayAreas[i];
            FVector EndPoint = ProtectedGameplayAreas[j];
            
            // Check if asset would intersect this sightline
            FVector ClosestPoint = FMath::ClosestPointOnSegment(Location, StartPoint, EndPoint);
            float DistanceToSightline = FVector::Dist(Location, ClosestPoint);
            
            if (DistanceToSightline < AssetBounds.Size())
            {
                ImpactPercentage += 5.0f; // Each blocked sightline adds 5%
            }
        }
    }
    
    return FMath::Clamp(ImpactPercentage, 0.0f, 100.0f);
}

void UTGTerritorialProceduralSystem::ApplyFactionStyling(AActor* Asset, int32 FactionId)
{
    if (!Asset)
    {
        return;
    }

    FTGFactionAssetLibrary FactionLibrary = GetFactionAssetLibrary(FactionId);
    
    // Apply faction colors to all mesh components
    TArray<UStaticMeshComponent*> MeshComponents;
    Asset->GetComponents<UStaticMeshComponent>(MeshComponents);
    
    for (UStaticMeshComponent* MeshComp : MeshComponents)
    {
        if (MeshComp)
        {
            // Create dynamic material instance to apply faction colors
            if (UMaterialInterface* OriginalMaterial = MeshComp->GetMaterial(0))
            {
                UMaterialInstanceDynamic* DynamicMaterial = MeshComp->CreateDynamicMaterialInstance(0, OriginalMaterial);
                if (DynamicMaterial)
                {
                    DynamicMaterial->SetVectorParameterValue(TEXT("PrimaryColor"), FactionLibrary.FactionPrimaryColor);
                    DynamicMaterial->SetVectorParameterValue(TEXT("SecondaryColor"), FactionLibrary.FactionSecondaryColor);
                }
            }
        }
    }
}

void UTGTerritorialProceduralSystem::ClearTerritorialAssets(int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialModificationMutex);
    
    if (TerritorialModifications.Contains(TerritoryId))
    {
        FTGTerritorialModification& Modification = TerritorialModifications[TerritoryId];
        
        // Destroy all placed assets
        for (AActor* Asset : Modification.PlacedAssets)
        {
            if (IsValid(Asset))
            {
                Asset->Destroy();
            }
        }
        
        Modification.PlacedAssets.Empty();
        TerritorialModifications.Remove(TerritoryId);
        
        UE_LOG(LogTGCore, Log, TEXT("Cleared territorial assets for Territory %d"), TerritoryId);
    }
}

FTGFactionAssetLibrary UTGTerritorialProceduralSystem::GetFactionAssetLibrary(int32 FactionId)
{
    if (FactionAssetLibraries.Contains(FactionId))
    {
        return FactionAssetLibraries[FactionId];
    }
    
    // Return default neutral library
    FTGFactionAssetLibrary DefaultLibrary;
    return DefaultLibrary;
}

ETGFactionArchitecturalStyle UTGTerritorialProceduralSystem::GetFactionArchitecturalStyle(int32 FactionId)
{
    switch (FactionId)
    {
        case 1: return ETGFactionArchitecturalStyle::CorporateHegemony;
        case 2: return ETGFactionArchitecturalStyle::Free77;
        case 3: return ETGFactionArchitecturalStyle::IronScavengers;
        case 4: return ETGFactionArchitecturalStyle::NomadClans;
        case 5: return ETGFactionArchitecturalStyle::ArchiveKeepers;
        case 6: return ETGFactionArchitecturalStyle::CivicWardens;
        default: return ETGFactionArchitecturalStyle::Neutral;
    }
}

void UTGTerritorialProceduralSystem::RequestTerritorialAssets(int32 TerritoryId, int32 FactionId, ETGTerritorialModificationType ModType)
{
    // Add to pending asset generation queue
    if (!PendingAssetGeneration.Contains(TerritoryId))
    {
        PendingAssetGeneration.Add(TerritoryId);
        
        // Record last generation time
        LastAssetGenerationTime.Add(TerritoryId, FDateTime::Now());
        
        // Broadcast asset request event
        OnTerritorialAssetsRequested.Broadcast(TerritoryId, FactionId);
        
        // Trigger asset generation pipeline (integration with existing production pipeline)
        FString AssetType;
        switch (ModType)
        {
            case ETGTerritorialModificationType::Cosmetic:
                AssetType = TEXT("territorial_cosmetic");
                break;
            case ETGTerritorialModificationType::AssetPlacement:
                AssetType = TEXT("territorial_dynamic");
                break;
            case ETGTerritorialModificationType::StructuralChange:
                AssetType = TEXT("territorial_structural");
                break;
            default:
                AssetType = TEXT("territorial_general");
                break;
        }
        
        TriggerAssetGeneration(TerritoryId, FactionId, AssetType);
    }
}

void UTGTerritorialProceduralSystem::TriggerAssetGeneration(int32 TerritoryId, int32 FactionId, const FString& AssetType)
{
    // Integration point with production_territorial_pipeline.py
    // This would call the Python asset generation system
    
    UE_LOG(LogTGCore, Log, TEXT("Triggering asset generation for Territory %d, Faction %d, Type %s"), 
        TerritoryId, FactionId, *AssetType);
    
    // In a full implementation, this would:
    // 1. Call Python script via subprocess
    // 2. Pass territorial and faction data
    // 3. Monitor generation progress
    // 4. Handle completion via OnAssetGenerationComplete callback
}

void UTGTerritorialProceduralSystem::OnAssetGenerationComplete(int32 TerritoryId, int32 FactionId, const TArray<FString>& GeneratedAssetPaths)
{
    UE_LOG(LogTGCore, Log, TEXT("Asset generation complete for Territory %d: %d assets generated"), 
        TerritoryId, GeneratedAssetPaths.Num());
    
    // Remove from pending queue
    PendingAssetGeneration.Remove(TerritoryId);
    
    // Load and apply generated assets
    if (LoadGeneratedAssets(GeneratedAssetPaths, TerritoryId))
    {
        OnTerritorialProcGenerationComplete.Broadcast(TerritoryId, FactionId, true);
    }
    else
    {
        OnTerritorialProcGenerationComplete.Broadcast(TerritoryId, FactionId, false);
    }
}

bool UTGTerritorialProceduralSystem::LoadGeneratedAssets(const TArray<FString>& AssetPaths, int32 TerritoryId)
{
    // Load generated assets from file paths and apply to territory
    // This would involve UE5 asset loading and placement
    
    UE_LOG(LogTGCore, Log, TEXT("Loading %d generated assets for Territory %d"), AssetPaths.Num(), TerritoryId);
    
    // In a full implementation, this would:
    // 1. Load static meshes from generated asset paths
    // 2. Apply faction-specific materials
    // 3. Place assets at validated locations
    // 4. Update territorial modification data
    
    return true;
}

void UTGTerritorialProceduralSystem::ConnectToTerritorialWebSocket()
{
    UE_LOG(LogTGCore, Log, TEXT("Connecting to Territorial WebSocket Server (port 8765)"));
    
    // In a full implementation, this would establish WebSocket connection
    // to the existing territorial_websocket_server.py for real-time updates
}

void UTGTerritorialProceduralSystem::OnTerritorialWebSocketMessage(const FString& Message)
{
    // Parse WebSocket message and trigger appropriate territorial updates
    UE_LOG(LogTGCore, Log, TEXT("Received territorial WebSocket message: %s"), *Message);
}

void UTGTerritorialProceduralSystem::ProcessPendingModifications()
{
    // Process any pending territorial modifications
    FScopeLock Lock(&TerritorialModificationMutex);
    
    // This method runs on timer to handle queued modifications
    if (PendingAssetGeneration.Num() > 0)
    {
        UE_LOG(LogTGCore, VeryVerbose, TEXT("Processing %d pending territorial modifications"), 
            PendingAssetGeneration.Num());
    }
}

void UTGTerritorialProceduralSystem::ProcessSeasonalTerritorialEvolution()
{
    // Handle seasonal changes to territorial control and procedural generation
    // This integrates with Season 1 Arc convoy routes and Black Vault POIs
    
    UE_LOG(LogTGCore, VeryVerbose, TEXT("Processing seasonal territorial evolution"));
}

void UTGTerritorialProceduralSystem::UpdateTerritorialInfluence(int32 TerritoryId, int32 FactionId, float InfluenceLevel)
{
    // Update territorial influence and trigger procedural changes if needed
    if (TerritorialManager)
    {
        int32 NewInfluence = FMath::RoundToInt(InfluenceLevel * 100.0f);
        TerritorialManager->UpdateFactionInfluence(TerritoryId, FactionId, NewInfluence);
    }
}

bool UTGTerritorialProceduralSystem::CheckCompetitiveBalance(const TArray<FVector>& ProposedLocations)
{
    // Validate that proposed asset locations maintain competitive balance
    for (const FVector& Location : ProposedLocations)
    {
        if (CalculateSightlineImpact(Location, FVector(200, 200, 200)) > MaxSightlineBlockagePercentage)
        {
            return false;
        }
    }
    return true;
}

void UTGTerritorialProceduralSystem::UpdateTerritorialLOD(const FVector& ViewerLocation, float MaxDistance)
{
    // Optimize territorial assets based on viewer distance
    FScopeLock Lock(&TerritorialModificationMutex);
    
    for (auto& ModPair : TerritorialModifications)
    {
        for (AActor* Asset : ModPair.Value.PlacedAssets)
        {
            if (IsValid(Asset))
            {
                float Distance = FVector::Dist(ViewerLocation, Asset->GetActorLocation());
                bool bShouldBeVisible = Distance <= MaxDistance;
                
                Asset->SetActorHiddenInGame(!bShouldBeVisible);
            }
        }
    }
}

void UTGTerritorialProceduralSystem::OptimizeTerritorialAssets(int32 MaxVisibleAssets)
{
    // Limit number of visible territorial assets for performance
    int32 VisibleCount = 0;
    
    FScopeLock Lock(&TerritorialModificationMutex);
    
    for (auto& ModPair : TerritorialModifications)
    {
        for (AActor* Asset : ModPair.Value.PlacedAssets)
        {
            if (IsValid(Asset) && VisibleCount < MaxVisibleAssets)
            {
                Asset->SetActorHiddenInGame(false);
                VisibleCount++;
            }
            else if (IsValid(Asset))
            {
                Asset->SetActorHiddenInGame(true);
            }
        }
    }
}

void UTGTerritorialProceduralSystem::ApplyConvoyRouteModifications(int32 TerritoryId)
{
    // Apply convoy route modifications for Season 1 Arc integration
    UE_LOG(LogTGCore, Log, TEXT("Applying convoy route modifications for Territory %d"), TerritoryId);
    
    // This would integrate with the convoy economy system to modify routes
    // based on territorial control changes
}