#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/TimerHandle.h"
#include "TGExtractionPad.generated.h"

class ATGCaptureNode;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnExtractionCompleted, class ATGExtractionPad*, ExtractionPad);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnExtractionProgress, class ATGExtractionPad*, ExtractionPad, float, Progress);

UCLASS()
class TGCORE_API ATGExtractionPad : public AActor
{
	GENERATED_BODY()
	
public:	
	ATGExtractionPad();

protected:
	virtual void BeginPlay() override;

	// Components
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class UBoxComponent* ExtractionZone;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class UStaticMeshComponent* PadMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class USceneComponent* ProgressIndicator;

	// Extraction Properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
	float ExtractionTime = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
	int32 RequiredNodesOwned = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
	TArray<TObjectPtr<ATGCaptureNode>> CaptureNodesToCheck;

	UPROPERTY(BlueprintReadOnly, Category = "Extraction")
	bool bIsLocked = true;

	UPROPERTY(BlueprintReadOnly, Category = "Extraction")
	bool bIsExtracting = false;

	UPROPERTY(BlueprintReadOnly, Category = "Extraction")
	float ExtractionProgress = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Extraction")
	class ATGPlayPawn* ExtractingPlayer = nullptr;

	// Events
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnExtractionCompleted OnExtractionCompleted;

	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnExtractionProgress OnExtractionProgress;

	// Timer
	FTimerHandle ExtractionTimerHandle;

	// Functions
	UFUNCTION()
	void OnExtractionZoneBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnExtractionZoneEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

	UFUNCTION()
	void ProgressExtraction();

	void CheckCaptureNodeRequirements();

	void StartExtraction(class ATGPlayPawn* Player);

	void StopExtraction();

	void UpdateVisualState();

public:	
	virtual void Tick(float DeltaTime) override;

	// Public Interface
	UFUNCTION(BlueprintPure, Category = "Extraction")
	bool IsLocked() const { return bIsLocked; }

	UFUNCTION(BlueprintPure, Category = "Extraction")
	bool IsExtracting() const { return bIsExtracting; }

	UFUNCTION(BlueprintPure, Category = "Extraction")
	float GetExtractionProgress() const { return ExtractionProgress; }

	UFUNCTION(BlueprintPure, Category = "Extraction")
	int32 GetOwnedNodesCount() const;

	UFUNCTION(BlueprintCallable, Category = "Extraction")
	void ForceUnlock() { bIsLocked = false; UpdateVisualState(); }

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
	void OnExtractionStarted();

	UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
	void OnExtractionStopped();

	UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
	void OnPadUnlocked();

	UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
	void OnPadLocked();
};