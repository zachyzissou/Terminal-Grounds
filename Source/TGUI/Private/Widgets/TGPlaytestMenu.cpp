#include "Widgets/TGPlaytestMenu.h"
#include "TGCore/Public/TGPlayPawn.h"
#include "TGCore/Public/TGExtractionPad.h"
#include "TGCore/Public/TGCaptureNode.h"
#include "Widgets/TGScoreWidget.h"
#include "TGAI/Public/TGEnemyGrunt.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Components/InputComponent.h"
#include "GameFramework/PlayerController.h"

UTGPlaytestMenu::UTGPlaytestMenu(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	bIsMenuVisible = false;
	bGodModeEnabled = false;
}

void UTGPlaytestMenu::NativeConstruct()
{
	Super::NativeConstruct();

	FindReferences();
	HideMenu(); // Start with menu hidden
}

void UTGPlaytestMenu::FindReferences()
{
	// Find player pawn
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		PlayerPawn = Cast<ATGPlayPawn>(PC->GetPawn());
	}

	// Find extraction pad
	TArray<AActor*> FoundPads;
	UGameplayStatics::GetAllActorsOfClass(this, ATGExtractionPad::StaticClass(), FoundPads);
	if (FoundPads.Num() > 0)
	{
		ExtractionPad = Cast<ATGExtractionPad>(FoundPads[0]);
	}

	// Find score widget (assuming it's also in the scene)
	if (UWidget* FoundWidget = GetWidgetFromName(TEXT("ScoreWidget")))
	{
		ScoreWidget = Cast<UTGScoreWidget>(FoundWidget);
	}
}

void UTGPlaytestMenu::ToggleMenu()
{
	if (bIsMenuVisible)
	{
		HideMenu();
	}
	else
	{
		ShowMenu();
	}
}

void UTGPlaytestMenu::ShowMenu()
{
	bIsMenuVisible = true;
	SetVisibility(ESlateVisibility::Visible);
	
	// Pause game and show mouse cursor
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		PC->SetPause(true);
		PC->bShowMouseCursor = true;
		PC->SetInputMode(FInputModeGameAndUI());
	}

	OnMenuToggled(true);
	UE_LOG(LogTemp, Log, TEXT("Playtest menu shown"));
}

void UTGPlaytestMenu::HideMenu()
{
	bIsMenuVisible = false;
	SetVisibility(ESlateVisibility::Hidden);
	
	// Unpause game and hide mouse cursor
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		PC->SetPause(false);
		PC->bShowMouseCursor = false;
		PC->SetInputMode(FInputModeGameOnly());
	}

	OnMenuToggled(false);
	UE_LOG(LogTemp, Log, TEXT("Playtest menu hidden"));
}

void UTGPlaytestMenu::RestartMatch()
{
	FindReferences();

	// Respawn player at start location
	if (PlayerPawn && PlayerPawn->GetController())
	{
		// Find player start
		TArray<AActor*> PlayerStarts;
		UGameplayStatics::GetAllActorsOfClass(this, APlayerStart::StaticClass(), PlayerStarts);
		
		if (PlayerStarts.Num() > 0)
		{
			PlayerPawn->SetActorLocation(PlayerStarts[0]->GetActorLocation());
		}

		// Reset player health and ammo
		RestoreHealth();
		AddAmmo();
	}

	// Reset all capture nodes
	TArray<AActor*> CaptureNodes;
	UGameplayStatics::GetAllActorsOfClass(this, ATGCaptureNode::StaticClass(), CaptureNodes);
	
	for (AActor* Actor : CaptureNodes)
	{
		if (ATGCaptureNode* Node = Cast<ATGCaptureNode>(Actor))
		{
			// Reset node state (this might need to be implemented in the capture node)
			UE_LOG(LogTemp, Log, TEXT("Reset capture node: %s"), *Node->GetName());
		}
	}

	// Restart score tracking
	if (ScoreWidget)
	{
		ScoreWidget->StartMatch();
	}

	OnMatchRestarted();
	HideMenu();

	UE_LOG(LogTemp, Log, TEXT("Match restarted"));
}

void UTGPlaytestMenu::TeleportToExtractPad()
{
	FindReferences();

	if (PlayerPawn && ExtractionPad)
	{
		FVector TeleportLocation = ExtractionPad->GetActorLocation() + FVector(0, 0, 100);
		PlayerPawn->SetActorLocation(TeleportLocation);
		
		UE_LOG(LogTemp, Log, TEXT("Player teleported to extraction pad"));
		HideMenu();
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("Could not find player pawn or extraction pad for teleport"));
	}
}

void UTGPlaytestMenu::ToggleGodMode()
{
	bGodModeEnabled = !bGodModeEnabled;
	
	if (PlayerPawn)
	{
		// Implementation depends on how god mode is handled in the player pawn
		// For now, just log the state change
		UE_LOG(LogTemp, Log, TEXT("God mode %s"), bGodModeEnabled ? TEXT("enabled") : TEXT("disabled"));
	}

	OnGodModeToggled(bGodModeEnabled);
}

void UTGPlaytestMenu::FastCaptureAllNodes()
{
	TArray<AActor*> CaptureNodes;
	UGameplayStatics::GetAllActorsOfClass(this, ATGCaptureNode::StaticClass(), CaptureNodes);
	
	for (AActor* Actor : CaptureNodes)
	{
		if (ATGCaptureNode* Node = Cast<ATGCaptureNode>(Actor))
		{
			// This would need a cheat function in the capture node
			UE_LOG(LogTemp, Log, TEXT("Fast captured node: %s"), *Node->GetName());
		}
	}

	UE_LOG(LogTemp, Log, TEXT("All nodes fast captured"));
}

void UTGPlaytestMenu::SpawnTestEnemies()
{
	if (!PlayerPawn)
	{
		return;
	}

	FVector PlayerLocation = PlayerPawn->GetActorLocation();
	
	// Spawn 5 test enemies around the player
	for (int32 i = 0; i < 5; i++)
	{
		FVector SpawnLocation = PlayerLocation + FVector(
			FMath::RandRange(-1000.0f, 1000.0f),
			FMath::RandRange(-1000.0f, 1000.0f),
			100.0f
		);

		if (ATGEnemyGrunt* Enemy = GetWorld()->SpawnActor<ATGEnemyGrunt>(ATGEnemyGrunt::StaticClass(), SpawnLocation, FRotator::ZeroRotator))
		{
			UE_LOG(LogTemp, Log, TEXT("Spawned test enemy at %s"), *SpawnLocation.ToString());
		}
	}

	UE_LOG(LogTemp, Log, TEXT("Spawned 5 test enemies"));
}

void UTGPlaytestMenu::KillAllEnemies()
{
	TArray<AActor*> Enemies;
	UGameplayStatics::GetAllActorsOfClass(this, ATGEnemyGrunt::StaticClass(), Enemies);
	
	for (AActor* Actor : Enemies)
	{
		if (ATGEnemyGrunt* Enemy = Cast<ATGEnemyGrunt>(Actor))
		{
			Enemy->TakeDamage(9999.0f); // Overkill damage
		}
	}

	UE_LOG(LogTemp, Log, TEXT("Killed all enemies (%d)"), Enemies.Num());
}

void UTGPlaytestMenu::AddAmmo()
{
	FindReferences();

	if (PlayerPawn)
	{
		// This would need to be implemented in the player pawn
		UE_LOG(LogTemp, Log, TEXT("Added ammo to player"));
	}
}

void UTGPlaytestMenu::RestoreHealth()
{
	FindReferences();

	if (PlayerPawn)
	{
		PlayerPawn->Heal(9999.0f); // Full heal
		UE_LOG(LogTemp, Log, TEXT("Restored player health"));
	}
}

FString UTGPlaytestMenu::GetGodModeButtonText() const
{
	return bGodModeEnabled ? TEXT("Disable God Mode") : TEXT("Enable God Mode");
}