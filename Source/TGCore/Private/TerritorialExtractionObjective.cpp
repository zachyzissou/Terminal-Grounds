// Copyright Terminal Grounds. All Rights Reserved.

#include "TerritorialExtractionObjective.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "Engine/Engine.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "TimerManager.h"
#include "TGTerritorial/Public/TerritorialManager.h"

ATerritorialExtractionObjective::ATerritorialExtractionObjective()
{
    PrimaryActorTick.bCanEverTick = true;

    // Create objective mesh component
    ObjectiveMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ObjectiveMesh"));
    RootComponent = ObjectiveMesh;
    ObjectiveMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ObjectiveMesh->SetCollisionResponseToAllChannels(ECR_Ignore);

    // Create interaction sphere
    InteractionSphere = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionSphere"));
    InteractionSphere->SetupAttachment(RootComponent);
    InteractionSphere->SetSphereRadius(300.0f);
    InteractionSphere->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionSphere->SetCollisionObjectType(ECC_WorldDynamic);
    InteractionSphere->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionSphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

    // Set default values
    ObjectiveDescription = TEXT("Complete territorial objective");
    CompletionTime = 30.0f;
    CompletionReward.InfluenceValue = 25;
    CompletionReward.FactionReputation = 100;
    CompletionReward.ExtractionBonus = 500;
    CompletionReward.RewardDescription = TEXT("Territorial influence gained");
}

void ATerritorialExtractionObjective::BeginPlay()
{
    Super::BeginPlay();

    // Bind interaction sphere overlap events
    InteractionSphere->OnComponentBeginOverlap.AddDynamic(this, &ATerritorialExtractionObjective::OnInteractionSphereBeginOverlap);
    InteractionSphere->OnComponentEndOverlap.AddDynamic(this, &ATerritorialExtractionObjective::OnInteractionSphereEndOverlap);

    // Set initial visual state
    SetObjectiveMaterial();
    UpdateVisualState();

    // Get reference to territorial manager
    if (UWorld* World = GetWorld())
    {
        if (UTerritorialSubsystem* TerritorialSubsystem = World->GetSubsystem<UTerritorialSubsystem>())
        {
            TerritorialManager = TerritorialSubsystem->GetTerritorialManager(this);
        }
    }

    UE_LOG(LogTemp, Log, TEXT("TerritorialExtractionObjective initialized: %s (Territory %d, Action %d)"), 
        *GetName(), TargetTerritoryID, (int32)ActionType);
}

void ATerritorialExtractionObjective::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bObjectiveActive && InteractingPlayer && !bObjectiveCompleted)
    {
        UpdateObjectiveProgress(DeltaTime);
        UpdateVisualState();
    }
}

bool ATerritorialExtractionObjective::CanPlayerStartObjective(APawn* Player)
{
    if (!Player || !bObjectiveActive || bObjectiveCompleted)
    {
        return false;
    }

    if (InteractingPlayer && InteractingPlayer != Player)
    {
        return false; // Another player is already interacting
    }

    // Additional requirements can be checked here
    if (bRequiresSpecialEquipment)
    {
        // TODO: Check for special equipment in player inventory
        // For now, assume player has required equipment
    }

    return true;
}

void ATerritorialExtractionObjective::StartObjective(APawn* Player)
{
    if (!CanPlayerStartObjective(Player))
    {
        return;
    }

    InteractingPlayer = Player;
    CompletionProgress = 0.0f;
    ProgressTimer = 0.0f;

    // Fire start event
    OnTerritorialObjectiveStarted.Broadcast(TargetTerritoryID, ActionType);

    UE_LOG(LogTemp, Log, TEXT("Territorial objective started by player: %s"), *Player->GetName());

    // Start progress timer
    GetWorld()->GetTimerManager().SetTimer(ObjectiveTimerHandle, 
        [this]() { UpdateObjectiveProgress(0.1f); }, 0.1f, true);
}

void ATerritorialExtractionObjective::CompleteObjective()
{
    if (bObjectiveCompleted)
    {
        return;
    }

    bObjectiveCompleted = true;
    CompletionProgress = 1.0f;

    // Clear timer
    GetWorld()->GetTimerManager().ClearTimer(ObjectiveTimerHandle);

    // Apply territorial influence
    ApplyTerritorialInfluence();

    // Notify territorial system
    NotifyTerritorialSystem();

    // Fire completion event
    OnTerritorialObjectiveCompleted.Broadcast(TargetTerritoryID, ActionType, CompletionReward.InfluenceValue);

    // Give rewards to player
    if (InteractingPlayer)
    {
        // TODO: Apply faction reputation and extraction bonus to player
        UE_LOG(LogTemp, Log, TEXT("Player %s completed territorial objective: +%d influence, +%d reputation"), 
            *InteractingPlayer->GetName(), CompletionReward.InfluenceValue, CompletionReward.FactionReputation);
    }

    // Update visual state
    UpdateVisualState();

    UE_LOG(LogTemp, Log, TEXT("Territorial objective completed: %s"), *GetName());
}

void ATerritorialExtractionObjective::CancelObjective()
{
    if (!InteractingPlayer)
    {
        return;
    }

    InteractingPlayer = nullptr;
    CompletionProgress = 0.0f;
    ProgressTimer = 0.0f;

    // Clear timer
    GetWorld()->GetTimerManager().ClearTimer(ObjectiveTimerHandle);

    // Update visual state
    UpdateVisualState();

    UE_LOG(LogTemp, Log, TEXT("Territorial objective cancelled"));
}

float ATerritorialExtractionObjective::GetCompletionPercentage() const
{
    return CompletionProgress;
}

FString ATerritorialExtractionObjective::GetObjectiveStatusText() const
{
    if (bObjectiveCompleted)
    {
        return TEXT("COMPLETED");
    }
    else if (InteractingPlayer)
    {
        return FString::Printf(TEXT("IN PROGRESS - %d%%"), (int32)(CompletionProgress * 100));
    }
    else if (bObjectiveActive)
    {
        return TEXT("AVAILABLE");
    }
    else
    {
        return TEXT("INACTIVE");
    }
}

void ATerritorialExtractionObjective::ApplyTerritorialInfluence()
{
    if (!TerritorialManager)
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot apply territorial influence - TerritorialManager not found"));
        return;
    }

    // Determine influence application based on action type
    int32 InfluenceChange = 0;
    int32 TargetFaction = 0;
    FString Cause;

    switch (ActionType)
    {
    case ETerritorialActionType::SabotageOperation:
        InfluenceChange = -CompletionReward.InfluenceValue; // Negative for target faction
        TargetFaction = TargetFactionID;
        Cause = TEXT("Player sabotage operation");
        break;

    case ETerritorialActionType::SupplyDelivery:
        InfluenceChange = CompletionReward.InfluenceValue; // Positive for ally faction
        TargetFaction = AllyFactionID;
        Cause = TEXT("Player supply delivery");
        break;

    case ETerritorialActionType::IntelGathering:
        // Intel gathering provides faction reputation but minimal territorial influence
        InfluenceChange = CompletionReward.InfluenceValue / 2;
        TargetFaction = AllyFactionID;
        Cause = TEXT("Player intelligence gathering");
        break;

    case ETerritorialActionType::InfrastructureAssault:
        // Infrastructure assault has major territorial impact
        InfluenceChange = -CompletionReward.InfluenceValue * 2; // Double negative impact
        TargetFaction = TargetFactionID;
        Cause = TEXT("Player infrastructure assault");
        break;

    default:
        UE_LOG(LogTemp, Warning, TEXT("Unknown territorial action type: %d"), (int32)ActionType);
        return;
    }

    // Apply the influence change
    bool bSuccess = TerritorialManager->UpdateTerritorialInfluence(
        TargetTerritoryID, 
        TerritoryType, 
        TargetFaction, 
        InfluenceChange, 
        Cause
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Applied territorial influence: Territory %d, Faction %d, Change %d"), 
            TargetTerritoryID, TargetFaction, InfluenceChange);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to apply territorial influence"));
    }
}

void ATerritorialExtractionObjective::NotifyTerritorialSystem()
{
    // Additional notifications to territorial system can be implemented here
    // For example, notifying faction AIs about player actions
    
    UE_LOG(LogTemp, Log, TEXT("Territorial system notified of objective completion"));
}

void ATerritorialExtractionObjective::OnInteractionSphereBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
    if (APawn* Player = Cast<APawn>(OtherActor))
    {
        if (Player->IsPlayerControlled() && CanPlayerStartObjective(Player))
        {
            bPlayerInRange = true;
            
            // Auto-start objective if no other player is interacting
            if (!InteractingPlayer)
            {
                StartObjective(Player);
            }
        }
    }
}

void ATerritorialExtractionObjective::OnInteractionSphereEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
    if (APawn* Player = Cast<APawn>(OtherActor))
    {
        if (Player == InteractingPlayer)
        {
            bPlayerInRange = false;
            
            // Cancel objective if player leaves area
            CancelObjective();
        }
    }
}

void ATerritorialExtractionObjective::UpdateObjectiveProgress(float DeltaTime)
{
    if (!InteractingPlayer || bObjectiveCompleted)
    {
        return;
    }

    ProgressTimer += DeltaTime;
    CompletionProgress = FMath::Clamp(ProgressTimer / CompletionTime, 0.0f, 1.0f);

    // Complete objective when progress reaches 100%
    if (CompletionProgress >= 1.0f)
    {
        CompleteObjective();
    }
}

void ATerritorialExtractionObjective::SetObjectiveMaterial()
{
    if (!ObjectiveMesh || !FactionMaterial)
    {
        return;
    }

    // Set material based on faction
    ObjectiveMesh->SetMaterial(0, FactionMaterial);
}

void ATerritorialExtractionObjective::UpdateVisualState()
{
    if (!ObjectiveMesh)
    {
        return;
    }

    // Update visual state based on objective status
    if (bObjectiveCompleted)
    {
        // Objective completed - reduce visibility or change material
        ObjectiveMesh->SetScalarParameterValueOnMaterials(TEXT("Opacity"), 0.5f);
    }
    else if (InteractingPlayer)
    {
        // Objective in progress - pulsing or glowing effect
        float PulseValue = 0.5f + 0.5f * FMath::Sin(GetWorld()->GetTimeSeconds() * 5.0f);
        ObjectiveMesh->SetScalarParameterValueOnMaterials(TEXT("Intensity"), PulseValue);
    }
    else if (bObjectiveActive)
    {
        // Objective available - normal visibility
        ObjectiveMesh->SetScalarParameterValueOnMaterials(TEXT("Opacity"), 1.0f);
        ObjectiveMesh->SetScalarParameterValueOnMaterials(TEXT("Intensity"), 1.0f);
    }
}