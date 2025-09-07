#include "Widgets/TGPlaytestCombatHUD.h"
#include "TGPlayPawn.h"
#include "TGPlaytestGameMode.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

UTGPlaytestCombatHUD::UTGPlaytestCombatHUD(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
}

void UTGPlaytestCombatHUD::NativeConstruct()
{
	Super::NativeConstruct();

	// Find references
	FindPlayerPawn();
	FindPlaytestGameMode();
	BindToGameModeEvents();

	// Initial update
	UpdatePlayerStats();
	UpdateMissionStats();
}

void UTGPlaytestCombatHUD::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	// Update HUD data every frame
	UpdatePlayerStats();
	UpdateMissionStats();
}

void UTGPlaytestCombatHUD::FindPlayerPawn()
{
	if (!PlayerPawn)
	{
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		{
			PlayerPawn = Cast<ATGPlayPawn>(PC->GetPawn());
		}
	}
}

void UTGPlaytestCombatHUD::FindPlaytestGameMode()
{
	if (!PlaytestGameMode)
	{
		if (UWorld* World = GetWorld())
		{
			PlaytestGameMode = Cast<ATGPlaytestGameMode>(World->GetAuthGameMode());
		}
	}
}

void UTGPlaytestCombatHUD::BindToGameModeEvents()
{
	if (PlaytestGameMode && !bEventsbound)
	{
		PlaytestGameMode->OnMissionStateChanged.AddDynamic(this, &UTGPlaytestCombatHUD::HandleMissionStateChanged);
		PlaytestGameMode->OnEnemyCountChanged.AddDynamic(this, &UTGPlaytestCombatHUD::HandleEnemyCountChanged);
		PlaytestGameMode->OnMissionComplete.AddDynamic(this, &UTGPlaytestCombatHUD::HandleMissionComplete);
		PlaytestGameMode->OnMissionFailed.AddDynamic(this, &UTGPlaytestCombatHUD::HandleMissionFailed);
		
		bEventsbound = true;
		UE_LOG(LogTemp, Log, TEXT("UTGPlaytestCombatHUD: Bound to game mode events"));
	}
}

void UTGPlaytestCombatHUD::UpdatePlayerStats()
{
	FindPlayerPawn();

	if (PlayerPawn)
	{
		float NewHealth = PlayerPawn->GetHealth();
		float NewMaxHealth = PlayerPawn->GetMaxHealth();
		float NewAmmo = PlayerPawn->GetAmmo();
		float NewMaxAmmo = PlayerPawn->GetMaxAmmo();

		// Check for changes
		bool bHealthChanged = (LastHealth != NewHealth || LastMaxHealth != NewMaxHealth);
		bool bAmmoChanged = (LastAmmo != NewAmmo || LastMaxAmmo != NewMaxAmmo);

		// Update values
		Health = NewHealth;
		MaxHealth = NewMaxHealth;
		Ammo = NewAmmo;
		MaxAmmo = NewMaxAmmo;

		// Store last values
		LastHealth = NewHealth;
		LastMaxHealth = NewMaxHealth;
		LastAmmo = NewAmmo;
		LastMaxAmmo = NewMaxAmmo;

		// Trigger Blueprint events if values changed
		if (bHealthChanged)
		{
			OnHealthUpdated();
		}

		if (bAmmoChanged)
		{
			OnAmmoUpdated();
		}
	}
}

void UTGPlaytestCombatHUD::UpdateMissionStats()
{
	FindPlaytestGameMode();
	BindToGameModeEvents();

	if (PlaytestGameMode)
	{
		// Update mission data
		RemainingEnemies = PlaytestGameMode->GetRemainingEnemies();
		TotalEnemies = PlaytestGameMode->GetTotalEnemies();
		MissionState = PlaytestGameMode->GetMissionState();
		bCanExtract = PlaytestGameMode->CanExtract();
	}
}

FString UTGPlaytestCombatHUD::GetMissionStateText() const
{
	switch (MissionState)
	{
		case EPlaytestMissionState::Setup:
			return TEXT("Setting up mission...");
		case EPlaytestMissionState::InProgress:
			return FString::Printf(TEXT("Eliminate %d enemies"), RemainingEnemies);
		case EPlaytestMissionState::WaitingForExtraction:
			return TEXT("All enemies eliminated - Reach extraction zone!");
		case EPlaytestMissionState::Success:
			return TEXT("MISSION SUCCESS!");
		case EPlaytestMissionState::Failed:
			return TEXT("MISSION FAILED");
		default:
			return TEXT("Unknown");
	}
}

FLinearColor UTGPlaytestCombatHUD::GetMissionStateColor() const
{
	switch (MissionState)
	{
		case EPlaytestMissionState::Setup:
			return FLinearColor::Yellow;
		case EPlaytestMissionState::InProgress:
			return FLinearColor::White;
		case EPlaytestMissionState::WaitingForExtraction:
			return FLinearColor::Green;
		case EPlaytestMissionState::Success:
			return FLinearColor::Green;
		case EPlaytestMissionState::Failed:
			return FLinearColor::Red;
		default:
			return FLinearColor::Gray;
	}
}

FString UTGPlaytestCombatHUD::GetObjectiveText() const
{
	switch (MissionState)
	{
		case EPlaytestMissionState::Setup:
			return TEXT("Preparing...");
		case EPlaytestMissionState::InProgress:
			return FString::Printf(TEXT("Eliminate %d/%d enemies"), TotalEnemies - RemainingEnemies, TotalEnemies);
		case EPlaytestMissionState::WaitingForExtraction:
			return TEXT("Reach the extraction zone");
		case EPlaytestMissionState::Success:
			return TEXT("Mission Complete!");
		case EPlaytestMissionState::Failed:
			return TEXT("Mission Failed - Press R to restart");
		default:
			return MissionObjective;
	}
}

void UTGPlaytestCombatHUD::HandleMissionStateChanged(EPlaytestMissionState NewState)
{
	if (LastMissionState != NewState)
	{
		LastMissionState = NewState;
		MissionState = NewState;
		OnMissionStateUpdated(NewState);
		
		UE_LOG(LogTemp, Log, TEXT("UTGPlaytestCombatHUD: Mission state changed to %s"), 
			*UEnum::GetValueAsString(NewState));
	}
}

void UTGPlaytestCombatHUD::HandleEnemyCountChanged(int32 NewRemainingEnemies, int32 NewTotalEnemies)
{
	if (LastRemainingEnemies != NewRemainingEnemies || LastTotalEnemies != NewTotalEnemies)
	{
		LastRemainingEnemies = NewRemainingEnemies;
		LastTotalEnemies = NewTotalEnemies;
		RemainingEnemies = NewRemainingEnemies;
		TotalEnemies = NewTotalEnemies;
		
		OnEnemyCountUpdated(NewRemainingEnemies, NewTotalEnemies);
		
		UE_LOG(LogTemp, Log, TEXT("UTGPlaytestCombatHUD: Enemy count updated - %d/%d remaining"), 
			NewRemainingEnemies, NewTotalEnemies);
	}
}

void UTGPlaytestCombatHUD::HandleMissionComplete()
{
	OnMissionComplete();
	UE_LOG(LogTemp, Log, TEXT("UTGPlaytestCombatHUD: Mission complete event received"));
}

void UTGPlaytestCombatHUD::HandleMissionFailed()
{
	OnMissionFailed();
	UE_LOG(LogTemp, Log, TEXT("UTGPlaytestCombatHUD: Mission failed event received"));
}