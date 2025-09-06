#include "TGExtractionPad.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "TGPlayPawn.h"
#include "TGCaptureNode.h"

ATGExtractionPad::ATGExtractionPad()
{
	PrimaryActorTick.bCanEverTick = true;

	// Create root component
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

	// Create extraction zone
	ExtractionZone = CreateDefaultSubobject<UBoxComponent>(TEXT("ExtractionZone"));
	ExtractionZone->SetupAttachment(RootComponent);
	ExtractionZone->SetBoxExtent(FVector(300.0f, 300.0f, 200.0f));
	ExtractionZone->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	ExtractionZone->SetCollisionResponseToAllChannels(ECR_Ignore);
	ExtractionZone->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

	// Create pad mesh
	PadMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PadMesh"));
	PadMesh->SetupAttachment(RootComponent);

	// Create progress indicator
	ProgressIndicator = CreateDefaultSubobject<USceneComponent>(TEXT("ProgressIndicator"));
	ProgressIndicator->SetupAttachment(PadMesh);

	// Initialize state
	bIsLocked = true;
	bIsExtracting = false;
	ExtractionProgress = 0.0f;
	ExtractingPlayer = nullptr;
}

void ATGExtractionPad::BeginPlay()
{
	Super::BeginPlay();

	// Bind overlap events
	ExtractionZone->OnComponentBeginOverlap.AddDynamic(this, &ATGExtractionPad::OnExtractionZoneBeginOverlap);
	ExtractionZone->OnComponentEndOverlap.AddDynamic(this, &ATGExtractionPad::OnExtractionZoneEndOverlap);

	// Check initial lock state
	CheckCaptureNodeRequirements();

	// Update initial visual state
	UpdateVisualState();
}

void ATGExtractionPad::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Continuously check capture node requirements
	CheckCaptureNodeRequirements();
}

void ATGExtractionPad::OnExtractionZoneBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
	{
		if (!bIsLocked && !bIsExtracting)
		{
			StartExtraction(Player);
		}
		else if (bIsLocked)
		{
			UE_LOG(LogTemp, Warning, TEXT("Extraction pad is locked. Capture %d nodes to unlock."), RequiredNodesOwned);
		}
	}
}

void ATGExtractionPad::OnExtractionZoneEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
	{
		if (ExtractingPlayer == Player)
		{
			StopExtraction();
		}
	}
}

void ATGExtractionPad::StartExtraction(ATGPlayPawn* Player)
{
	if (bIsLocked || bIsExtracting)
	{
		return;
	}

	bIsExtracting = true;
	ExtractingPlayer = Player;
	ExtractionProgress = 0.0f;

	// Start extraction timer
	GetWorld()->GetTimerManager().SetTimer(ExtractionTimerHandle, this, &ATGExtractionPad::ProgressExtraction, 0.1f, true);

	OnExtractionStarted();
	OnExtractionProgress.Broadcast(this, ExtractionProgress);

	UE_LOG(LogTemp, Log, TEXT("Extraction started by player %s"), Player ? *Player->GetName() : TEXT("Unknown"));
}

void ATGExtractionPad::StopExtraction()
{
	if (!bIsExtracting)
	{
		return;
	}

	bIsExtracting = false;
	ExtractingPlayer = nullptr;
	ExtractionProgress = 0.0f;

	// Clear extraction timer
	GetWorld()->GetTimerManager().ClearTimer(ExtractionTimerHandle);

	OnExtractionStopped();

	UE_LOG(LogTemp, Log, TEXT("Extraction stopped"));
}

void ATGExtractionPad::ProgressExtraction()
{
	if (!bIsExtracting || !ExtractingPlayer)
	{
		StopExtraction();
		return;
	}

	float ProgressIncrement = (1.0f / ExtractionTime) * 0.1f; // 0.1f is timer interval
	ExtractionProgress += ProgressIncrement;

	// Broadcast progress update
	OnExtractionProgress.Broadcast(this, ExtractionProgress);

	if (ExtractionProgress >= 1.0f)
	{
		// Extraction completed
		ExtractionProgress = 1.0f;
		bIsExtracting = false;
		GetWorld()->GetTimerManager().ClearTimer(ExtractionTimerHandle);

		OnExtractionCompleted.Broadcast(this);

		UE_LOG(LogTemp, Log, TEXT("Extraction completed by player %s!"), ExtractingPlayer ? *ExtractingPlayer->GetName() : TEXT("Unknown"));
		
		ExtractingPlayer = nullptr;
	}
}

void ATGExtractionPad::CheckCaptureNodeRequirements()
{
	int32 OwnedNodes = GetOwnedNodesCount();
	bool bShouldBeUnlocked = (OwnedNodes >= RequiredNodesOwned);

	if (bIsLocked && bShouldBeUnlocked)
	{
		bIsLocked = false;
		OnPadUnlocked();
		UpdateVisualState();
		UE_LOG(LogTemp, Log, TEXT("Extraction pad unlocked! Owned nodes: %d/%d"), OwnedNodes, RequiredNodesOwned);
	}
	else if (!bIsLocked && !bShouldBeUnlocked)
	{
		bIsLocked = true;
		if (bIsExtracting)
		{
			StopExtraction();
		}
		OnPadLocked();
		UpdateVisualState();
		UE_LOG(LogTemp, Log, TEXT("Extraction pad locked! Owned nodes: %d/%d"), OwnedNodes, RequiredNodesOwned);
	}
}

int32 ATGExtractionPad::GetOwnedNodesCount() const
{
	int32 OwnedCount = 0;
	
	for (ATGCaptureNode* Node : CaptureNodesToCheck)
	{
		if (IsValid(Node) && Node->IsOwned())
		{
			OwnedCount++;
		}
	}
	
	return OwnedCount;
}

void ATGExtractionPad::UpdateVisualState()
{
	// This will be implemented in Blueprint to change materials/effects
	UE_LOG(LogTemp, Log, TEXT("Updating extraction pad visual state - Locked: %s, Extracting: %s"), 
		bIsLocked ? TEXT("Yes") : TEXT("No"),
		bIsExtracting ? TEXT("Yes") : TEXT("No"));
}