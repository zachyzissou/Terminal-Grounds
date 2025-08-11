#pragma once
#include "CoreMinimal.h"
#include "Engine/PrimaryDataAsset.h"
#include "TGItemDef.generated.h"

UCLASS(BlueprintType)
class TGLOOT_API UTGItemDef : public UPrimaryDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName Id;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName Type;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName Tier;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) int32 Stack = 1;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float Weight = 0.f;
};
