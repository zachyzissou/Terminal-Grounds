#include "TGCaptureNode.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "TGPlayPawn.h"

ATGCaptureNode::ATGCaptureNode()
{
	PrimaryActorTick.bCanEverTick = true;

	// Create root component
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

	// Create capture radius sphere
	CaptureRadius = CreateDefaultSubobject<USphereComponent>(TEXT("CaptureRadius"));
	CaptureRadius->SetupAttachment(RootComponent);
	CaptureRadius->SetSphereRadius(CaptureRadius_Value);
	CaptureRadius->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	CaptureRadius->SetCollisionResponseToAllChannels(ECR_Ignore);
	CaptureRadius->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

	// Create node mesh
	NodeMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NodeMesh"));
	NodeMesh->SetupAttachment(RootComponent);

	// Create progress indicator
	ProgressIndicator = CreateDefaultSubobject<USceneComponent>(TEXT("ProgressIndicator"));
	ProgressIndicator->SetupAttachment(NodeMesh);

	// Initialize state
	CurrentState = ECaptureNodeState::Neutral;
	CaptureProgress = 0.0f;
	FriendlyPlayersInRange = 0;
	HostilePlayersInRange = 0;
}

void ATGCaptureNode::BeginPlay()
{
	Super::BeginPlay();

	// Bind overlap events
	CaptureRadius->OnComponentBeginOverlap.AddDynamic(this, &ATGCaptureNode::OnCaptureRadiusBeginOverlap);
	CaptureRadius->OnComponentEndOverlap.AddDynamic(this, &ATGCaptureNode::OnCaptureRadiusEndOverlap);

	// Set initial radius
	CaptureRadius->SetSphereRadius(CaptureRadius_Value);

	// Update initial visual state
	UpdateVisualState();
}

void ATGCaptureNode::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Update capture logic continuously
	UpdateCaptureLogic();
}

void ATGCaptureNode::OnCaptureRadiusBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
	{
		// For now, assume all players are friendly (can be expanded for team-based gameplay)
		FriendlyPlayersInRange++;
		
		UE_LOG(LogTemp, Log, TEXT("Player entered capture node %s. Friendly players: %d"), *GetName(), FriendlyPlayersInRange);
	}
}

void ATGCaptureNode::OnCaptureRadiusEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
	{
		FriendlyPlayersInRange = FMath::Max(0, FriendlyPlayersInRange - 1);
		
		UE_LOG(LogTemp, Log, TEXT("Player left capture node %s. Friendly players: %d"), *GetName(), FriendlyPlayersInRange);
	}
}

void ATGCaptureNode::UpdateCaptureLogic()
{
	bool bShouldCapture = false;
	ECaptureNodeState NewState = CurrentState;

	// Determine if we should start, continue, or stop capturing
	if (FriendlyPlayersInRange > 0 && HostilePlayersInRange == 0)
	{
		// Only friendly players present
		if (CurrentState == ECaptureNodeState::Neutral || CurrentState == ECaptureNodeState::Hostile)
		{
			NewState = ECaptureNodeState::Capturing;
			bShouldCapture = true;
		}
		else if (CurrentState == ECaptureNodeState::Capturing)
		{
			bShouldCapture = true;
		}
	}
	else if (FriendlyPlayersInRange == 0 && HostilePlayersInRange > 0)
	{
		// Only hostile players present - they could recapture
		if (CurrentState == ECaptureNodeState::Owned)
		{
			NewState = ECaptureNodeState::Hostile;
		}
	}
	else if (FriendlyPlayersInRange == 0 && HostilePlayersInRange == 0)
	{
		// No players present - maintain current state
		bShouldCapture = false;
	}
	else
	{
		// Contested - pause capture progress
		bShouldCapture = false;
	}

	// Update state if changed
	if (NewState != CurrentState)
	{
		SetCaptureState(NewState);
	}

	// Manage capture timer
	if (bShouldCapture)
	{
		if (!GetWorld()->GetTimerManager().IsTimerActive(CaptureTimerHandle))
		{
			GetWorld()->GetTimerManager().SetTimer(CaptureTimerHandle, this, &ATGCaptureNode::ProgressCapture, 0.1f, true);
		}
	}
	else
	{
		if (GetWorld()->GetTimerManager().IsTimerActive(CaptureTimerHandle))
		{
			GetWorld()->GetTimerManager().ClearTimer(CaptureTimerHandle);
		}
	}
}

void ATGCaptureNode::ProgressCapture()
{
	if (CurrentState != ECaptureNodeState::Capturing)
	{
		return;
	}

	float ProgressIncrement = (1.0f / CaptureTime) * 0.1f; // 0.1f is timer interval
	CaptureProgress += ProgressIncrement;

	// Broadcast progress update
	OnProgressUpdated(CaptureProgress);

	if (CaptureProgress >= 1.0f)
	{
		// Capture completed
		CaptureProgress = 1.0f;
		SetCaptureState(ECaptureNodeState::Owned);
		GetWorld()->GetTimerManager().ClearTimer(CaptureTimerHandle);
		
		OnCaptureCompleted();
		
		UE_LOG(LogTemp, Log, TEXT("Capture node %s has been captured!"), *GetName());
	}
}

void ATGCaptureNode::SetCaptureState(ECaptureNodeState NewState)
{
	if (CurrentState != NewState)
	{
		ECaptureNodeState PreviousState = CurrentState;
		CurrentState = NewState;

		// Reset progress for certain state transitions
		if (NewState == ECaptureNodeState::Neutral || NewState == ECaptureNodeState::Hostile)
		{
			CaptureProgress = 0.0f;
		}
		else if (NewState == ECaptureNodeState::Capturing && PreviousState != ECaptureNodeState::Capturing)
		{
			OnCaptureStarted();
		}

		// Update visuals
		UpdateVisualState();

		// Broadcast state change
		OnCaptureStateChanged.Broadcast(this, CurrentState);
		
		UE_LOG(LogTemp, Log, TEXT("Capture node %s state changed to %s"), *GetName(), 
			*UEnum::GetValueAsString(CurrentState));
	}
}

void ATGCaptureNode::UpdateVisualState()
{
	// This will be implemented in Blueprint to change materials/colors
	// For now, just log the state change
	UE_LOG(LogTemp, Log, TEXT("Updating visual state for node %s: %s"), *GetName(), 
		*UEnum::GetValueAsString(CurrentState));
}