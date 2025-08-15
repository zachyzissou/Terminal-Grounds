#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h" // UDataAsset
#include "TGAttachmentDef.generated.h"

class USkeletalMesh;
class UGameplayEffect;

UCLASS(BlueprintType)
class TGATTACHMENTS_API UTGAttachmentDef : public UDataAsset {
  GENERATED_BODY()
public:
  // Muzzle/Barrel/Optic/Underbarrel/Mag/Stock/Grip/Laser
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Attachment")
  FName Slot;

  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
  float RecoilMultiplier = 1.f;
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
  int32 ADS_ms_Add = 0;
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
  float MoveSpeedMultiplier = 1.f;
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
  int32 Velocity_Add = 0;
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
  float IRVisibility = 1.f;

  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Visual")
  TObjectPtr<USkeletalMesh> Mesh;

  // Optional gameplay effect to apply when equipped (e.g., recoil reduction)
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "GAS")
  TSubclassOf<UGameplayEffect> EffectGE;
};
