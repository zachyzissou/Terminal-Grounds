#pragma once

#include "CoreMinimal.h"
#include "TGCore/Public/TGCharacter.h"
#include "AIController.h"
#include "Components/SphereComponent.h"
#include "Engine/TimerHandle.h"
#include "TGEnemyGrunt.generated.h"

UENUM(BlueprintType)
enum class EEnemyState : uint8
{
	Patrolling	UMETA(DisplayName = "Patrolling"),
	Chasing		UMETA(DisplayName = "Chasing"),
	Attacking	UMETA(DisplayName = "Attacking"),
	Dead		UMETA(DisplayName = "Dead")
};

UCLASS()
class TGAI_API ATGEnemyGrunt : public ATGCharacter
{
	GENERATED_BODY()

public:
	ATGEnemyGrunt();

protected:
	virtual void BeginPlay() override;

	// Components
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI")
	class USphereComponent* DetectionRadius;

	// AI Properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float DetectionRange = 1500.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float AttackRange = 800.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float PatrolRadius = 1000.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float MovementSpeed = 300.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	TArray<AActor*> PatrolPoints;

	// Combat Properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float Health = 75.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float MaxHealth = 75.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float Damage = 25.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float FireRate = 2.0f; // Shots per second

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float AttackCooldown = 0.5f;

	// State
	UPROPERTY(BlueprintReadOnly, Category = "AI")
	EEnemyState CurrentState = EEnemyState::Patrolling;

	UPROPERTY(BlueprintReadOnly, Category = "AI")
	AActor* CurrentTarget = nullptr;

	UPROPERTY(BlueprintReadOnly, Category = "AI")
	int32 CurrentPatrolIndex = 0;

	UPROPERTY(BlueprintReadOnly, Category = "AI")
	FVector StartLocation;

	// Timers
	FTimerHandle AttackTimerHandle;
	FTimerHandle PatrolTimerHandle;

	// Functions
	UFUNCTION()
	void OnDetectionRadiusBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnDetectionRadiusEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

	UFUNCTION()
	void UpdateAILogic();

	UFUNCTION()
	void AttackTarget();

	void SetEnemyState(EEnemyState NewState);

	void StartPatrol();

	void StartChase();

	void StartAttack();

	void MoveTo(FVector Destination);

	bool CanSeeTarget(AActor* Target) const;

	bool IsTargetInRange(AActor* Target, float Range) const;

public:
	virtual void Tick(float DeltaTime) override;

	// Public Interface
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void TakeDamage(float DamageAmount);

	UFUNCTION(BlueprintPure, Category = "AI")
	EEnemyState GetCurrentState() const { return CurrentState; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	float GetHealth() const { return Health; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsDead() const { return CurrentState == EEnemyState::Dead || Health <= 0.0f; }

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "AI")
	void OnStateChanged(EEnemyState NewState);

	UFUNCTION(BlueprintImplementableEvent, Category = "Combat")
	void OnHealthChanged(float NewHealth, float MaxHealthValue);

	UFUNCTION(BlueprintImplementableEvent, Category = "Combat")
	void OnDeath();

	UFUNCTION(BlueprintImplementableEvent, Category = "Combat")
	void OnAttack();
};