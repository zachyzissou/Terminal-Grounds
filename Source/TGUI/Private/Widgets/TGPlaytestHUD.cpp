#include "Widgets/TGPlaytestHUD.h"
#include "TGCore/Public/TGPlayPawn.h"
#include "TGCore/Public/TGCaptureNode.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Engine.h"

UTGPlaytestHUD::UTGPlaytestHUD(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
}

void UTGPlaytestHUD::NativeConstruct()
{
	Super::NativeConstruct();

	// Find player pawn and capture nodes
	FindPlayerPawn();
	FindCaptureNodes();

	// Initial update
	UpdatePlayerStats();
	UpdateNodeStatus();
}

void UTGPlaytestHUD::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	// Update HUD data every frame
	UpdatePlayerStats();
	UpdateNodeStatus();
}

void UTGPlaytestHUD::FindPlayerPawn()
{
	if (!PlayerPawn)
	{
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		{
			PlayerPawn = Cast<ATGPlayPawn>(PC->GetPawn());
		}
	}
}

void UTGPlaytestHUD::FindCaptureNodes()
{
	if (CaptureNodes.Num() == 0)
	{
		TArray<AActor*> FoundNodes;
		UGameplayStatics::GetAllActorsOfClass(this, ATGCaptureNode::StaticClass(), FoundNodes);
		
		for (AActor* Actor : FoundNodes)
		{
			if (ATGCaptureNode* CaptureNode = Cast<ATGCaptureNode>(Actor))
			{
				CaptureNodes.Add(CaptureNode);
			}
		}

		TotalNodes = CaptureNodes.Num();
	}
}

void UTGPlaytestHUD::UpdatePlayerStats()
{
	FindPlayerPawn();

	if (PlayerPawn)
	{
		float NewHealth = PlayerPawn->GetHealth();
		float NewMaxHealth = PlayerPawn->GetMaxHealth();
		float NewAmmo = PlayerPawn->GetAmmo();
		float NewMaxAmmo = PlayerPawn->GetMaxAmmo();

		// Check if values changed
		bool bHealthChanged = (Health != NewHealth || MaxHealth != NewMaxHealth);
		bool bAmmoChanged = (Ammo != NewAmmo || MaxAmmo != NewMaxAmmo);

		// Update values
		Health = NewHealth;
		MaxHealth = NewMaxHealth;
		Ammo = NewAmmo;
		MaxAmmo = NewMaxAmmo;

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

void UTGPlaytestHUD::UpdateNodeStatus()
{
	FindCaptureNodes();

	if (CaptureNodes.Num() > 0)
	{
		int32 OwnedCount = 0;
		TArray<FString> NodeStatuses;

		for (int32 i = 0; i < CaptureNodes.Num(); i++)
		{
			if (IsValid(CaptureNodes[i]))
			{
				FString StatusString;
				switch (CaptureNodes[i]->GetCaptureState())
				{
					case ECaptureNodeState::Neutral:
						StatusString = TEXT("Neutral");
						break;
					case ECaptureNodeState::Capturing:
						StatusString = FString::Printf(TEXT("Capturing (%.0f%%)"), 
							CaptureNodes[i]->GetCaptureProgress() * 100.0f);
						break;
					case ECaptureNodeState::Hostile:
						StatusString = TEXT("Hostile");
						break;
					case ECaptureNodeState::Owned:
						StatusString = TEXT("Owned");
						OwnedCount++;
						break;
					default:
						StatusString = TEXT("Unknown");
						break;
				}

				NodeStatuses.Add(StatusString);
			}
		}

		// Update individual node status strings
		if (NodeStatuses.Num() > 0) NodeStatusA = NodeStatuses[0];
		if (NodeStatuses.Num() > 1) NodeStatusB = NodeStatuses[1];
		if (NodeStatuses.Num() > 2) NodeStatusC = NodeStatuses[2];

		// Check if owned count changed
		if (NodesOwned != OwnedCount)
		{
			NodesOwned = OwnedCount;
			OnNodeStatusUpdated();
		}
	}
}