#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "TGProfileSave.generated.h"

UCLASS()
class TGCORE_API UTGProfileSave : public USaveGame
{
	GENERATED_BODY()
public:
	// Simple placeholders for inventory/stash
	UPROPERTY()
	TMap<FName, int32> Inventory; // itemId -> count

	UPROPERTY()
	TMap<FName, int32> Stash; // secure stash
};
