#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/StaticMesh.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "TGProceduralArena.generated.h"

class ATGCaptureNode;
class ATGExtractionPad;
class ATGEnemyGrunt;

USTRUCT(BlueprintType)
struct FLegoSnapPoint
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Snap")
	FVector LocalPosition = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Snap")
	FRotator LocalRotation = FRotator::ZeroRotator;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Snap")
	FString SnapID = TEXT("Default");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Snap")
	bool bIsOccupied = false;

	FLegoSnapPoint()
	{
		LocalPosition = FVector::ZeroVector;
		LocalRotation = FRotator::ZeroRotator;
		SnapID = TEXT("Default");
		bIsOccupied = false;
	}
};

USTRUCT(BlueprintType)
struct FArenaValidationReport
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	bool bIsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	int32 NavMeshTileCount = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	int32 UnreachableSpawnPoints = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	int32 CaptureNodeCount = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	float AveragePathLength = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	float ConnectivityPercentage = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	TArray<FString> ValidationErrors;

	FArenaValidationReport()
	{
		bIsValid = false;
		NavMeshTileCount = 0;
		UnreachableSpawnPoints = 0;
		CaptureNodeCount = 0;
		AveragePathLength = 0.0f;
		ConnectivityPercentage = 0.0f;
		ValidationErrors.Empty();
	}
};

UCLASS()
class TGCORE_API ATGProceduralArena : public AActor
{
	GENERATED_BODY()
	
public:	
	ATGProceduralArena();

protected:
	virtual void BeginPlay() override;

	// Root component
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class USceneComponent* ArenaRoot;

	// Generation Parameters
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
	int32 RandomSeed = 12345;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
	int32 RoomCount = 5;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
	int32 CorridorCount = 8;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
	float ArenaRadius = 3000.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generation")
	int32 EnemyCount = 10;

	// Lego Kit Blueprints
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lego Kit")
	TSubclassOf<AActor> BP_Room_Small;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lego Kit")
	TSubclassOf<AActor> BP_Room_Med;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lego Kit")
	TSubclassOf<AActor> BP_Corridor_Straight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lego Kit")
	TSubclassOf<AActor> BP_Corridor_T;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lego Kit")
	TSubclassOf<AActor> BP_Courtyard_Square;

	// Spawned Objects
	UPROPERTY(BlueprintReadOnly, Category = "Generation")
	TArray<AActor*> SpawnedPieces;

	UPROPERTY(BlueprintReadOnly, Category = "Generation")
	TArray<ATGCaptureNode*> SpawnedCaptureNodes;

	UPROPERTY(BlueprintReadOnly, Category = "Generation")
	TArray<ATGEnemyGrunt*> SpawnedEnemies;

	UPROPERTY(BlueprintReadOnly, Category = "Generation")
	ATGExtractionPad* SpawnedExtractionPad;

	// Validation
	UPROPERTY(BlueprintReadOnly, Category = "Validation")
	FArenaValidationReport LastValidationReport;

public:
	// Generation Functions
	UFUNCTION(BlueprintCallable, Category = "Generation", CallInEditor)
	void GenerateArena();

	UFUNCTION(BlueprintCallable, Category = "Generation", CallInEditor)
	void ClearArena();

	UFUNCTION(BlueprintCallable, Category = "Generation", CallInEditor)
	void ValidateArena();

	UFUNCTION(BlueprintCallable, Category = "Generation")
	void RebuildNavMesh();

	// Blueprint Generation Interface
	UFUNCTION(BlueprintCallable, Category = "Generation")
	bool BuildArenaFromSeed(int32 Seed, int32 Rooms, int32 Corridors, float Radius);

	// Getters
	UFUNCTION(BlueprintPure, Category = "Validation")
	FArenaValidationReport GetValidationReport() const { return LastValidationReport; }

	UFUNCTION(BlueprintPure, Category = "Generation")
	int32 GetSpawnedPieceCount() const { return SpawnedPieces.Num(); }

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "Generation")
	void OnArenaGenerated();

	UFUNCTION(BlueprintImplementableEvent, Category = "Generation")
	void OnArenaCleared();

	UFUNCTION(BlueprintImplementableEvent, Category = "Validation")
	void OnArenaValidated(const FArenaValidationReport& Report);

private:
	void SpawnLegoPieces();
	void PlaceCaptureNodes();
	void PlaceExtractionPad();
	void SpawnEnemies();
	void PlacePlayerStart();
	
	FVector GetRandomPositionInRadius(float Radius) const;
	bool IsPositionValid(const FVector& Position, float MinDistance = 1000.0f) const;
	void ConnectPieces();
	
	// Validation helpers
	void ValidateNavMesh();
	void ValidateConnectivity();
	void ValidateSpawnPoints();
};