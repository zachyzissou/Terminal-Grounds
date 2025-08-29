// Copyright Terminal Grounds. All Rights Reserved.

#include "TGProceduralTestActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"

ATGProceduralTestActor::ATGProceduralTestActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // Create root component
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

    // Create visualization mesh (sphere to show generation area)
    VisualizationMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisualizationMesh"));
    VisualizationMesh->SetupAttachment(RootComponent);
    VisualizationMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    VisualizationMesh->SetCastShadow(false);

    // Create info text
    InfoText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("InfoText"));
    InfoText->SetupAttachment(RootComponent);
    InfoText->SetRelativeLocation(FVector(0.0f, 0.0f, 500.0f));
    InfoText->SetTextRenderColor(FColor::White);
    InfoText->SetHorizontalAlignment(EHTA_Center);
    InfoText->SetVerticalAlignment(EVTA_TextTop);

    // Set default sphere mesh for visualization
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere"));
    if (SphereMesh.Succeeded())
    {
        VisualizationMesh->SetStaticMesh(SphereMesh.Object);
        VisualizationMesh->SetWorldScale3D(FVector(GenerationRadius / 5000.0f)); // Scale based on generation radius
        VisualizationMesh->SetMaterial(0, nullptr); // Use wireframe material in editor
    }

    ProceduralSubsystem = nullptr;
}

void ATGProceduralTestActor::BeginPlay()
{
    Super::BeginPlay();

    // Get procedural world subsystem
    ProceduralSubsystem = GetWorld()->GetSubsystem<UTGProceduralWorldSubsystem>();
    if (ProceduralSubsystem)
    {
        // Bind to events
        ProceduralSubsystem->OnTerrainGenerated.AddDynamic(this, &ATGProceduralTestActor::OnTerrainGenerated);
        ProceduralSubsystem->OnBuildingPlaced.AddDynamic(this, &ATGProceduralTestActor::OnBuildingPlaced);

        // Auto-generate if enabled
        if (bAutoGenerateOnBeginPlay)
        {
            TriggerGeneration();
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ATGProceduralTestActor: Could not find UTGProceduralWorldSubsystem"));
    }

    UpdateInfoDisplay();
}

void ATGProceduralTestActor::TriggerGeneration()
{
    if (!ProceduralSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("ProceduralSubsystem not available"));
        return;
    }

    GenerateAtCurrentLocation();
}

void ATGProceduralTestActor::ClearGeneration()
{
    if (!ProceduralSubsystem)
    {
        return;
    }

    ProceduralSubsystem->ClearTerritoryGeneration(TestTerritoryID, TestTerritoryType);
    GeneratedActors.Empty();
    
    if (bShowDebugInfo)
    {
        UE_LOG(LogTemp, Log, TEXT("Cleared generation for territory %d"), TestTerritoryID);
        GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Yellow, 
            FString::Printf(TEXT("Cleared territory %d"), TestTerritoryID));
    }

    UpdateInfoDisplay();
}

void ATGProceduralTestActor::ChangeToDirectorate()
{
    TestDominantFaction = ELocalFactionID::Directorate;
    TriggerGeneration();
}

void ATGProceduralTestActor::ChangeToFree77()
{
    TestDominantFaction = ELocalFactionID::Free77;
    TriggerGeneration();
}

void ATGProceduralTestActor::ChangeToCivicWardens()
{
    TestDominantFaction = ELocalFactionID::CivicWardens;
    TriggerGeneration();
}

void ATGProceduralTestActor::ShowGenerationArea()
{
    // Update visualization mesh scale to match generation radius
    if (VisualizationMesh)
    {
        float Scale = GenerationRadius / 5000.0f; // 5000 = default sphere radius
        VisualizationMesh->SetWorldScale3D(FVector(Scale));
    }

    if (bShowDebugInfo && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Cyan, 
            FString::Printf(TEXT("Generation Area: %.0fm radius"), GenerationRadius / 100.0f));
    }
}

void ATGProceduralTestActor::OnTerrainGenerated(int32 TerritoryID, bool bSuccess)
{
    if (TerritoryID != TestTerritoryID)
    {
        return; // Not our territory
    }

    if (bShowDebugInfo)
    {
        FString StatusText = bSuccess ? TEXT("SUCCESS") : TEXT("FAILED");
        FColor StatusColor = bSuccess ? FColor::Green : FColor::Red;
        
        UE_LOG(LogTemp, Log, TEXT("Terrain generation %s for territory %d"), *StatusText, TerritoryID);
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 3.0f, StatusColor, 
                FString::Printf(TEXT("Generation %s for territory %d"), *StatusText, TerritoryID));
        }
    }

    // Update our actor list
    if (ProceduralSubsystem)
    {
        GeneratedActors = ProceduralSubsystem->GetGeneratedActorsInTerritory(TestTerritoryID, TestTerritoryType);
    }

    UpdateInfoDisplay();
}

void ATGProceduralTestActor::OnBuildingPlaced(int32 TerritoryID, ELocalFactionID ControllingFaction, FVector Location)
{
    if (TerritoryID != TestTerritoryID)
    {
        return; // Not our territory
    }

    if (bShowDebugInfo)
    {
        UE_LOG(LogTemp, Log, TEXT("Building placed for faction %d at %s"), (int32)ControllingFaction, *Location.ToString());
    }
}

void ATGProceduralTestActor::UpdateInfoDisplay()
{
    if (!InfoText)
    {
        return;
    }

    FString FactionName = UEnum::GetValueAsString(TestDominantFaction);
    FactionName = FactionName.Replace(TEXT("EFactionID::"), TEXT(""));

    FString InfoString = FString::Printf(TEXT("Procedural Test\nTerritory: %d\nFaction: %s\nRadius: %.0fm\nObjects: %d"),
        TestTerritoryID, 
        *FactionName,
        GenerationRadius / 100.0f,
        GeneratedActors.Num());

    InfoText->SetText(FText::FromString(InfoString));

    // Color text based on faction
    FColor TextColor = FColor::White;
    switch (TestDominantFaction)
    {
        case ELocalFactionID::Directorate:
            TextColor = FColor(51, 102, 255); // Blue
            break;
        case ELocalFactionID::Free77:
            TextColor = FColor(255, 76, 51); // Red
            break;
        case ELocalFactionID::CivicWardens:
            TextColor = FColor(179, 179, 179); // Gray
            break;
    }
    InfoText->SetTextRenderColor(TextColor);
}

void ATGProceduralTestActor::GenerateAtCurrentLocation()
{
    if (!ProceduralSubsystem)
    {
        return;
    }

    // Create generation request
    FProceduralGenerationRequest Request;
    Request.TerritoryID = TestTerritoryID;
    Request.TerritoryType = TestTerritoryType;
    Request.DominantFaction = TestDominantFaction;
    Request.GenerationType = GenerationType;
    Request.CenterLocation = GetActorLocation();
    Request.GenerationRadius = GenerationRadius;
    Request.RandomSeed = RandomSeed;

    // Trigger generation
    bool bStarted = ProceduralSubsystem->GenerateTerritory(Request);

    if (bShowDebugInfo)
    {
        FString StatusText = bStarted ? TEXT("STARTED") : TEXT("FAILED TO START");
        FColor StatusColor = bStarted ? FColor::Blue : FColor::Red;
        
        UE_LOG(LogTemp, Log, TEXT("Generation %s for territory %d at %s"), 
               *StatusText, TestTerritoryID, *GetActorLocation().ToString());
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 3.0f, StatusColor, 
                FString::Printf(TEXT("Generation %s"), *StatusText));
        }
    }

    UpdateInfoDisplay();
    ShowGenerationArea();
}