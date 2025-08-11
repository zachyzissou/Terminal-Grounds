#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "TGExosuitData.generated.h"

UENUM(BlueprintType)
enum class EExosuitFrame : uint8
{
    Light       UMETA(DisplayName = "Light Frame"),
    Assault     UMETA(DisplayName = "Assault Frame"), 
    Heavy       UMETA(DisplayName = "Heavy Frame")
};

UENUM(BlueprintType)
enum class EExosuitDamageStage : uint8
{
    Pristine    UMETA(DisplayName = "Pristine"),
    Minor       UMETA(DisplayName = "Minor Damage"),
    Moderate    UMETA(DisplayName = "Moderate Damage"),
    Heavy       UMETA(DisplayName = "Heavy Damage"),
    Critical    UMETA(DisplayName = "Critical Damage")
};

USTRUCT(BlueprintType)
struct FExosuitStats
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    float MovementSpeedMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    float SprintSpeedMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
    float ADSStabilityBonus = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
    float RecoilReductionPercentage = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Defense")
    float ArmorRating = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Defense")
    float ExplosiveResistance = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Systems")
    int32 AugmentSlots = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Systems")
    float PowerConsumption = 100.0f;
};

/**
 * Data asset defining exosuit frame configurations
 */
UCLASS(BlueprintType)
class TGCOMBAT_API UTGExosuitData : public UDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    FString ExosuitName;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    EExosuitFrame FrameType;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    FText Description;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Stats")
    FExosuitStats BaseStats;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Stats")
    TMap<EExosuitDamageStage, FExosuitStats> DamageStageModifiers;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Visual")
    TSoftObjectPtr<USkeletalMesh> ExosuitMesh;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Visual")
    TMap<EExosuitDamageStage, TSoftObjectPtr<UMaterialInstance>> DamageStageMaterials;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    TSoftObjectPtr<USoundCue> MovementSounds;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    TSoftObjectPtr<USoundCue> ServoSounds;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Compatibility")
    FGameplayTagContainer AllowedAugments;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Compatibility")
    FGameplayTagContainer FactionRestrictions;
};