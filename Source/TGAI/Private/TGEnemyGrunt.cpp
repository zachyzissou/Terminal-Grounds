#include "TGEnemyGrunt.h"
#include "Components/SphereComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AIController.h"
#include "NavigationSystem.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "TGCore/Public/TGPlayPawn.h"
#include "TGCore/Public/TGPlaytestGameMode.h"
#include "Components/CapsuleComponent.h"
#include "Kismet/GameplayStatics.h"

ATGEnemyGrunt::ATGEnemyGrunt()
{
	PrimaryActorTick.bCanEverTick = true;

	// Set up AI controller
	AIControllerClass = AAIController::StaticClass();

	// Configure character movement
	GetCharacterMovement()->MaxWalkSpeed = MovementSpeed;
	GetCharacterMovement()->bOrientRotationToMovement = true;

	// Create detection radius
	DetectionRadius = CreateDefaultSubobject<USphereComponent>(TEXT("DetectionRadius"));
	DetectionRadius->SetupAttachment(GetCapsuleComponent());
	DetectionRadius->SetSphereRadius(DetectionRange);
	DetectionRadius->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	DetectionRadius->SetCollisionResponseToAllChannels(ECR_Ignore);
	DetectionRadius->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

	// Initialize state
	CurrentState = EEnemyState::Patrolling;
	CurrentTarget = nullptr;
	Health = MaxHealth;
}

void ATGEnemyGrunt::BeginPlay()
{
	Super::BeginPlay();

	// Store starting location
	StartLocation = GetActorLocation();

	// Bind detection events
	DetectionRadius->OnComponentBeginOverlap.AddDynamic(this, &ATGEnemyGrunt::OnDetectionRadiusBeginOverlap);
	DetectionRadius->OnComponentEndOverlap.AddDynamic(this, &ATGEnemyGrunt::OnDetectionRadiusEndOverlap);

	// Set detection radius
	DetectionRadius->SetSphereRadius(DetectionRange);

	// Start AI logic timer
	GetWorld()->GetTimerManager().SetTimer(PatrolTimerHandle, this, &ATGEnemyGrunt::UpdateAILogic, 0.5f, true);

	// Start patrolling
	StartPatrol();
}

void ATGEnemyGrunt::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Update AI logic continuously for responsiveness
	UpdateAILogic();
}

void ATGEnemyGrunt::OnDetectionRadiusBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (IsDead())
	{
		return;
	}

	if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
	{
		if (CanSeeTarget(Player))
		{
			CurrentTarget = Player;
			StartChase();
			UE_LOG(LogTemp, Log, TEXT("Enemy %s detected player %s"), *GetName(), *Player->GetName());
		}
	}
}

void ATGEnemyGrunt::OnDetectionRadiusEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (IsDead())
	{
		return;
	}

	if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
	{
		if (CurrentTarget == Player)
		{
			CurrentTarget = nullptr;
			StartPatrol();
			UE_LOG(LogTemp, Log, TEXT("Enemy %s lost sight of player %s"), *GetName(), *Player->GetName());
		}
	}
}

void ATGEnemyGrunt::UpdateAILogic()
{
	if (IsDead())
	{
		return;
	}

	switch (CurrentState)
	{
		case EEnemyState::Patrolling:
		{
			// Look for nearby targets
			if (CurrentTarget && IsValid(CurrentTarget) && CanSeeTarget(CurrentTarget))
			{
				StartChase();
			}
			break;
		}
		case EEnemyState::Chasing:
		{
			if (!CurrentTarget || !IsValid(CurrentTarget))
			{
				StartPatrol();
				break;
			}

			if (IsTargetInRange(CurrentTarget, AttackRange))
			{
				StartAttack();
			}
			else if (IsTargetInRange(CurrentTarget, DetectionRange) && CanSeeTarget(CurrentTarget))
			{
				// Continue chasing
				MoveTo(CurrentTarget->GetActorLocation());
			}
			else
			{
				// Lost target
				CurrentTarget = nullptr;
				StartPatrol();
			}
			break;
		}
		case EEnemyState::Attacking:
		{
			if (!CurrentTarget || !IsValid(CurrentTarget))
			{
				StartPatrol();
				break;
			}

			if (!IsTargetInRange(CurrentTarget, AttackRange))
			{
				StartChase();
			}
			break;
		}
	}
}

void ATGEnemyGrunt::AttackTarget()
{
	if (!CurrentTarget || !IsValid(CurrentTarget) || IsDead())
	{
		return;
	}

	if (IsTargetInRange(CurrentTarget, AttackRange))
	{
		// Perform hitscan attack
		if (ATGPlayPawn* PlayerTarget = Cast<ATGPlayPawn>(CurrentTarget))
		{
			PlayerTarget->TakeDamage(Damage);
			OnAttack();
			
			UE_LOG(LogTemp, Log, TEXT("Enemy %s attacked player %s for %f damage"), 
				*GetName(), *PlayerTarget->GetName(), Damage);
		}
	}
}

void ATGEnemyGrunt::SetEnemyState(EEnemyState NewState)
{
	if (CurrentState != NewState)
	{
		CurrentState = NewState;
		OnStateChanged(CurrentState);
		
		UE_LOG(LogTemp, Log, TEXT("Enemy %s state changed to %s"), 
			*GetName(), *UEnum::GetValueAsString(CurrentState));
	}
}

void ATGEnemyGrunt::StartPatrol()
{
	SetEnemyState(EEnemyState::Patrolling);

	// Move to a random point within patrol radius
	FVector RandomDirection = FVector(FMath::RandRange(-1.0f, 1.0f), FMath::RandRange(-1.0f, 1.0f), 0.0f).GetSafeNormal();
	FVector PatrolDestination = StartLocation + (RandomDirection * FMath::RandRange(PatrolRadius * 0.3f, PatrolRadius));
	
	MoveTo(PatrolDestination);
}

void ATGEnemyGrunt::StartChase()
{
	SetEnemyState(EEnemyState::Chasing);
	
	if (CurrentTarget)
	{
		MoveTo(CurrentTarget->GetActorLocation());
	}
}

void ATGEnemyGrunt::StartAttack()
{
	SetEnemyState(EEnemyState::Attacking);

	// Start attack timer
	if (!GetWorld()->GetTimerManager().IsTimerActive(AttackTimerHandle))
	{
		GetWorld()->GetTimerManager().SetTimer(AttackTimerHandle, this, &ATGEnemyGrunt::AttackTarget, 1.0f / FireRate, true);
	}
}

void ATGEnemyGrunt::MoveTo(FVector Destination)
{
	if (AAIController* AIController = Cast<AAIController>(GetController()))
	{
		AIController->MoveToLocation(Destination, -1.0f, true);
	}
}

bool ATGEnemyGrunt::CanSeeTarget(AActor* Target) const
{
	if (!Target)
	{
		return false;
	}

	// Simple line trace to check if target is visible
	FHitResult HitResult;
	FVector StartTrace = GetActorLocation() + FVector(0, 0, 60); // Eye height
	FVector EndTrace = Target->GetActorLocation() + FVector(0, 0, 60);

	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);
	QueryParams.bTraceComplex = false;

	bool bHit = GetWorld()->LineTraceSingleByChannel(HitResult, StartTrace, EndTrace, ECC_WorldStatic, QueryParams);
	
	return !bHit || HitResult.GetActor() == Target;
}

bool ATGEnemyGrunt::IsTargetInRange(AActor* Target, float Range) const
{
	if (!Target)
	{
		return false;
	}

	float Distance = FVector::Dist(GetActorLocation(), Target->GetActorLocation());
	return Distance <= Range;
}

void ATGEnemyGrunt::TakeDamage(float DamageAmount)
{
	if (IsDead())
	{
		return;
	}

	Health = FMath::Clamp(Health - DamageAmount, 0.0f, MaxHealth);
	OnHealthChanged(Health, MaxHealth);

	if (Health <= 0.0f)
	{
		SetEnemyState(EEnemyState::Dead);
		OnDeath();

		// Notify the playtest game mode
		if (UWorld* World = GetWorld())
		{
			if (ATGPlaytestGameMode* PlaytestGameMode = Cast<ATGPlaytestGameMode>(World->GetAuthGameMode()))
			{
				PlaytestGameMode->OnEnemyDied(this);
			}
		}

		// Clear all timers
		GetWorld()->GetTimerManager().ClearTimer(AttackTimerHandle);
		GetWorld()->GetTimerManager().ClearTimer(PatrolTimerHandle);

		// Disable collision
		GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		DetectionRadius->SetCollisionEnabled(ECollisionEnabled::NoCollision);

		UE_LOG(LogTemp, Log, TEXT("Enemy %s has died"), *GetName());
	}
}

float ATGEnemyGrunt::TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser)
{
	// Call our custom damage function
	float OldHealth = Health;
	TakeDamage(DamageAmount);
	
	// Return the amount of damage actually taken
	return OldHealth - Health;
}