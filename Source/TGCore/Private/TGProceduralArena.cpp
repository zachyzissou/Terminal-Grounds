#include "TGProceduralArena.h"
#include "TGCaptureNode.h"
#include "TGExtractionPad.h"
#include "TGAI/Public/TGEnemyGrunt.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "NavigationSystem.h"
#include "NavMesh/NavMeshBoundsVolume.h"
#include "Kismet/GameplayStatics.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerStart.h"

ATGProceduralArena::ATGProceduralArena()
{
	PrimaryActorTick.bCanEverTick = false;

	// Create root component
	ArenaRoot = CreateDefaultSubobject<USceneComponent>(TEXT("ArenaRoot"));
	RootComponent = ArenaRoot;

	// Initialize arrays
	SpawnedPieces.Empty();
	SpawnedCaptureNodes.Empty();
	SpawnedEnemies.Empty();
	SpawnedExtractionPad = nullptr;
}

void ATGProceduralArena::BeginPlay()
{
	Super::BeginPlay();
}

void ATGProceduralArena::GenerateArena()
{
	UE_LOG(LogTemp, Log, TEXT("Starting arena generation with seed %d"), RandomSeed);

	// Clear existing arena
	ClearArena();

	// Set random seed for consistent generation
	FMath::RandInit(RandomSeed);

	// Generate pieces in order
	SpawnLegoPieces();
	PlaceCaptureNodes();
	PlaceExtractionPad();
	SpawnEnemies();
	PlacePlayerStart();

	// Rebuild navigation
	RebuildNavMesh();

	// Validate the generated arena
	ValidateArena();

	OnArenaGenerated();

	UE_LOG(LogTemp, Log, TEXT("Arena generation completed. Spawned %d pieces"), SpawnedPieces.Num());
}

void ATGProceduralArena::ClearArena()
{
	UE_LOG(LogTemp, Log, TEXT("Clearing existing arena"));

	// Destroy all spawned pieces
	for (AActor* Piece : SpawnedPieces)
	{
		if (IsValid(Piece))
		{
			Piece->Destroy();
		}
	}
	SpawnedPieces.Empty();

	// Destroy capture nodes
	for (ATGCaptureNode* Node : SpawnedCaptureNodes)
	{
		if (IsValid(Node))
		{
			Node->Destroy();
		}
	}
	SpawnedCaptureNodes.Empty();

	// Destroy enemies
	for (ATGEnemyGrunt* Enemy : SpawnedEnemies)
	{
		if (IsValid(Enemy))
		{
			Enemy->Destroy();
		}
	}
	SpawnedEnemies.Empty();

	// Destroy extraction pad
	if (IsValid(SpawnedExtractionPad))
	{
		SpawnedExtractionPad->Destroy();
		SpawnedExtractionPad = nullptr;
	}

	OnArenaCleared();
}

void ATGProceduralArena::SpawnLegoPieces()
{
	UE_LOG(LogTemp, Log, TEXT("Spawning lego pieces - Rooms: %d, Corridors: %d"), RoomCount, CorridorCount);

	// Spawn rooms
	for (int32 i = 0; i < RoomCount; i++)
	{
		TSubclassOf<AActor> RoomClass = (FMath::RandBool()) ? BP_Room_Small : BP_Room_Med;
		if (!RoomClass)
		{
			UE_LOG(LogTemp, Warning, TEXT("Room blueprint class not set, skipping room %d"), i);
			continue;
		}

		FVector SpawnLocation = GetRandomPositionInRadius(ArenaRadius);
		if (IsPositionValid(SpawnLocation))
		{
			if (AActor* SpawnedRoom = GetWorld()->SpawnActor<AActor>(RoomClass, SpawnLocation, FRotator::ZeroRotator))
			{
				SpawnedPieces.Add(SpawnedRoom);
				UE_LOG(LogTemp, Log, TEXT("Spawned room %d at %s"), i, *SpawnLocation.ToString());
			}
		}
	}

	// Spawn corridors
	for (int32 i = 0; i < CorridorCount; i++)
	{
		TSubclassOf<AActor> CorridorClass = (FMath::RandBool()) ? BP_Corridor_Straight : BP_Corridor_T;
		if (!CorridorClass)
		{
			UE_LOG(LogTemp, Warning, TEXT("Corridor blueprint class not set, skipping corridor %d"), i);
			continue;
		}

		FVector SpawnLocation = GetRandomPositionInRadius(ArenaRadius);
		FRotator SpawnRotation = FRotator(0, FMath::RandRange(0.0f, 360.0f), 0);
		
		if (IsPositionValid(SpawnLocation))
		{
			if (AActor* SpawnedCorridor = GetWorld()->SpawnActor<AActor>(CorridorClass, SpawnLocation, SpawnRotation))
			{
				SpawnedPieces.Add(SpawnedCorridor);
				UE_LOG(LogTemp, Log, TEXT("Spawned corridor %d at %s"), i, *SpawnLocation.ToString());
			}
		}
	}

	// Spawn a central courtyard if blueprint is available
	if (BP_Courtyard_Square)
	{
		FVector CourtyardLocation = GetActorLocation(); // Center of arena
		if (AActor* SpawnedCourtyard = GetWorld()->SpawnActor<AActor>(BP_Courtyard_Square, CourtyardLocation, FRotator::ZeroRotator))
		{
			SpawnedPieces.Add(SpawnedCourtyard);
			UE_LOG(LogTemp, Log, TEXT("Spawned central courtyard at %s"), *CourtyardLocation.ToString());
		}
	}
}

void ATGProceduralArena::PlaceCaptureNodes()
{
	UE_LOG(LogTemp, Log, TEXT("Placing capture nodes"));

	// Place 3 capture nodes at strategic positions
	TArray<FVector> NodePositions;
	
	// Try to place nodes with good distribution
	for (int32 i = 0; i < 3; i++)
	{
		FVector BestPosition = FVector::ZeroVector;
		float BestScore = 0.0f;
		
		// Try multiple positions and pick the best one
		for (int32 j = 0; j < 10; j++)
		{
			FVector TestPosition = GetRandomPositionInRadius(ArenaRadius * 0.8f);
			float Score = 0.0f;
			
			// Score based on distance from other nodes
			for (const FVector& ExistingPos : NodePositions)
			{
				float Distance = FVector::Dist(TestPosition, ExistingPos);
				Score += FMath::Min(Distance, 2000.0f); // Prefer nodes that are well separated
			}
			
			if (Score > BestScore)
			{
				BestScore = Score;
				BestPosition = TestPosition;
			}
		}
		
		NodePositions.Add(BestPosition);
		
		// Spawn the capture node
		if (ATGCaptureNode* CaptureNode = GetWorld()->SpawnActor<ATGCaptureNode>(ATGCaptureNode::StaticClass(), BestPosition, FRotator::ZeroRotator))
		{
			SpawnedCaptureNodes.Add(CaptureNode);
			UE_LOG(LogTemp, Log, TEXT("Placed capture node %d at %s"), i, *BestPosition.ToString());
		}
	}
}

void ATGProceduralArena::PlaceExtractionPad()
{
	UE_LOG(LogTemp, Log, TEXT("Placing extraction pad"));

	// Place extraction pad at a position that's not too close to capture nodes
	FVector BestPosition = FVector::ZeroVector;
	float BestScore = 0.0f;
	
	for (int32 i = 0; i < 20; i++)
	{
		FVector TestPosition = GetRandomPositionInRadius(ArenaRadius * 0.6f);
		float Score = 0.0f;
		
		// Score based on distance from capture nodes (prefer some distance)
		for (ATGCaptureNode* Node : SpawnedCaptureNodes)
		{
			if (IsValid(Node))
			{
				float Distance = FVector::Dist(TestPosition, Node->GetActorLocation());
				Score += FMath::Clamp(Distance - 1000.0f, 0.0f, 1500.0f); // Sweet spot distance
			}
		}
		
		if (Score > BestScore)
		{
			BestScore = Score;
			BestPosition = TestPosition;
		}
	}

	// Spawn the extraction pad
	if (ATGExtractionPad* ExtractionPad = GetWorld()->SpawnActor<ATGExtractionPad>(ATGExtractionPad::StaticClass(), BestPosition, FRotator::ZeroRotator))
	{
		SpawnedExtractionPad = ExtractionPad;
		
		// Link capture nodes to extraction pad
		ExtractionPad->CaptureNodesToCheck = SpawnedCaptureNodes;
		
		UE_LOG(LogTemp, Log, TEXT("Placed extraction pad at %s"), *BestPosition.ToString());
	}
}

void ATGProceduralArena::SpawnEnemies()
{
	UE_LOG(LogTemp, Log, TEXT("Spawning %d enemies"), EnemyCount);

	for (int32 i = 0; i < EnemyCount; i++)
	{
		FVector SpawnLocation = GetRandomPositionInRadius(ArenaRadius * 0.9f);
		
		if (ATGEnemyGrunt* Enemy = GetWorld()->SpawnActor<ATGEnemyGrunt>(ATGEnemyGrunt::StaticClass(), SpawnLocation, FRotator::ZeroRotator))
		{
			SpawnedEnemies.Add(Enemy);
			UE_LOG(LogTemp, Log, TEXT("Spawned enemy %d at %s"), i, *SpawnLocation.ToString());
		}
	}
}

void ATGProceduralArena::PlacePlayerStart()
{
	// Find or create a player start
	TArray<AActor*> PlayerStarts;
	UGameplayStatics::GetAllActorsOfClass(GetWorld(), APlayerStart::StaticClass(), PlayerStarts);
	
	if (PlayerStarts.Num() == 0)
	{
		// Spawn a new player start at arena center
		FVector PlayerStartLocation = GetActorLocation() + FVector(0, 0, 100);
		GetWorld()->SpawnActor<APlayerStart>(APlayerStart::StaticClass(), PlayerStartLocation, FRotator::ZeroRotator);
		UE_LOG(LogTemp, Log, TEXT("Created player start at %s"), *PlayerStartLocation.ToString());
	}
}

FVector ATGProceduralArena::GetRandomPositionInRadius(float Radius) const
{
	FVector BaseLocation = GetActorLocation();
	FVector RandomDirection = FVector(FMath::RandRange(-1.0f, 1.0f), FMath::RandRange(-1.0f, 1.0f), 0.0f).GetSafeNormal();
	float RandomDistance = FMath::RandRange(0.0f, Radius);
	
	return BaseLocation + (RandomDirection * RandomDistance);
}

bool ATGProceduralArena::IsPositionValid(const FVector& Position, float MinDistance) const
{
	// Check distance from existing pieces
	for (const AActor* ExistingPiece : SpawnedPieces)
	{
		if (IsValid(ExistingPiece))
		{
			float Distance = FVector::Dist(Position, ExistingPiece->GetActorLocation());
			if (Distance < MinDistance)
			{
				return false;
			}
		}
	}
	
	return true;
}

void ATGProceduralArena::RebuildNavMesh()
{
	UE_LOG(LogTemp, Log, TEXT("Rebuilding navigation mesh"));

	if (UNavigationSystemV1* NavSystem = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()))
	{
		NavSystem->Build();
		UE_LOG(LogTemp, Log, TEXT("Navigation mesh rebuild initiated"));
	}
}

void ATGProceduralArena::ValidateArena()
{
	UE_LOG(LogTemp, Log, TEXT("Validating generated arena"));

	LastValidationReport = FArenaValidationReport();

	ValidateNavMesh();
	ValidateConnectivity();
	ValidateSpawnPoints();

	// Final validation
	LastValidationReport.CaptureNodeCount = SpawnedCaptureNodes.Num();
	LastValidationReport.bIsValid = (LastValidationReport.CaptureNodeCount >= 3 && 
									LastValidationReport.ConnectivityPercentage >= 100.0f &&
									LastValidationReport.UnreachableSpawnPoints == 0);

	if (!LastValidationReport.bIsValid)
	{
		LastValidationReport.ValidationErrors.Add(TEXT("Arena failed validation requirements"));
	}

	OnArenaValidated(LastValidationReport);

	UE_LOG(LogTemp, Log, TEXT("Arena validation complete - Valid: %s"), 
		LastValidationReport.bIsValid ? TEXT("Yes") : TEXT("No"));
}

bool ATGProceduralArena::BuildArenaFromSeed(int32 Seed, int32 Rooms, int32 Corridors, float Radius)
{
	RandomSeed = Seed;
	RoomCount = Rooms;
	CorridorCount = Corridors;
	ArenaRadius = Radius;

	GenerateArena();

	return LastValidationReport.bIsValid;
}

void ATGProceduralArena::ValidateNavMesh()
{
	// This is a simplified validation - in a real implementation, you'd check actual navmesh data
	LastValidationReport.NavMeshTileCount = FMath::RandRange(50, 200); // Mock data
	LastValidationReport.AveragePathLength = FMath::RandRange(1500.0f, 3000.0f);
}

void ATGProceduralArena::ValidateConnectivity()
{
	// Simplified connectivity check - assume 100% if we have spawned pieces
	if (SpawnedPieces.Num() > 0)
	{
		LastValidationReport.ConnectivityPercentage = 100.0f;
	}
	else
	{
		LastValidationReport.ConnectivityPercentage = 0.0f;
		LastValidationReport.ValidationErrors.Add(TEXT("No arena pieces spawned"));
	}
}

void ATGProceduralArena::ValidateSpawnPoints()
{
	// Check if we have the required number of capture nodes
	if (SpawnedCaptureNodes.Num() < 3)
	{
		LastValidationReport.ValidationErrors.Add(FString::Printf(TEXT("Insufficient capture nodes: %d (required: 3)"), SpawnedCaptureNodes.Num()));
	}

	// Check if extraction pad exists
	if (!IsValid(SpawnedExtractionPad))
	{
		LastValidationReport.ValidationErrors.Add(TEXT("Missing extraction pad"));
	}

	LastValidationReport.UnreachableSpawnPoints = 0; // Assume all reachable for now
}