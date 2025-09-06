#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/TimerHandle.h"
#include "TGCaptureNode.generated.h"

UENUM(BlueprintType)
enum class ECaptureNodeState : uint8
{
	Neutral		UMETA(DisplayName = "Neutral"),
	Capturing	UMETA(DisplayName = "Capturing"),
	Hostile		UMETA(DisplayName = "Hostile"),
	Owned		UMETA(DisplayName = "Owned")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCaptureStateChanged, class ATGCaptureNode*, CaptureNode, ECaptureNodeState, NewState);

UCLASS()
class TGCORE_API ATGCaptureNode : public AActor
{
	GENERATED_BODY()
	
public:	
	ATGCaptureNode();

protected:
	virtual void BeginPlay() override;

	// Components
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class USphereComponent* CaptureRadius;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class UStaticMeshComponent* NodeMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class USceneComponent* ProgressIndicator;

	// Capture Properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Capture")
	float CaptureTime = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Capture")
	float CaptureRadius_Value = 800.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Capture")
	ECaptureNodeState CurrentState = ECaptureNodeState::Neutral;

	UPROPERTY(BlueprintReadOnly, Category = "Capture")
	float CaptureProgress = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Capture")
	int32 FriendlyPlayersInRange = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Capture")
	int32 HostilePlayersInRange = 0;

	// Events
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnCaptureStateChanged OnCaptureStateChanged;

	// Timer
	FTimerHandle CaptureTimerHandle;

	// Functions
	UFUNCTION()
	void OnCaptureRadiusBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnCaptureRadiusEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

	UFUNCTION()
	void UpdateCaptureLogic();

	UFUNCTION()
	void ProgressCapture();

	void SetCaptureState(ECaptureNodeState NewState);

	void UpdateVisualState();

public:	
	virtual void Tick(float DeltaTime) override;

	// Public Interface
	UFUNCTION(BlueprintPure, Category = "Capture")
	ECaptureNodeState GetCaptureState() const { return CurrentState; }

	UFUNCTION(BlueprintPure, Category = "Capture")
	float GetCaptureProgress() const { return CaptureProgress; }

	UFUNCTION(BlueprintPure, Category = "Capture")
	bool IsOwned() const { return CurrentState == ECaptureNodeState::Owned; }

	UFUNCTION(BlueprintPure, Category = "Capture")
	bool IsContested() const { return FriendlyPlayersInRange > 0 && HostilePlayersInRange > 0; }

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "Capture")
	void OnCaptureStarted();

	UFUNCTION(BlueprintImplementableEvent, Category = "Capture")
	void OnCaptureCompleted();

	UFUNCTION(BlueprintImplementableEvent, Category = "Capture")
	void OnCaptureLost();

	UFUNCTION(BlueprintImplementableEvent, Category = "Capture")
	void OnProgressUpdated(float Progress);
};