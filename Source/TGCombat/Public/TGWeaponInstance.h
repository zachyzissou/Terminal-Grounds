#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "TGWeaponInstance.generated.h"

UCLASS(BlueprintType)
class TGCOMBAT_API UTGWeaponInstance : public UObject
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Weapon") FName WeaponId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Weapon") int32 MagazineSize = 30;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Weapon") float FireRate = 0.1f; // seconds between shots
};
