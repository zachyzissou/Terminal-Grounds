#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "Sound/SoundCue.h"
#include "TGAugmentData.generated.h"

UENUM(BlueprintType)
enum class EAugmentType : uint8
{
    ReflexSplice     UMETA(DisplayName = "Reflex Splice"),
    OcularSuite      UMETA(DisplayName = "Ocular Suite"),
    SubdermalPlating UMETA(DisplayName = "Subdermal Plating"),
    NeuralSlicer     UMETA(DisplayName = "Neural Slicer")
};

UENUM(BlueprintType)
enum class EAugmentRisk : uint8
{
    None        UMETA(DisplayName = "No Risk"),
    Low         UMETA(DisplayName = "Low Risk"),
    Moderate    UMETA(DisplayName = "Moderate Risk"),
    High        UMETA(DisplayName = "High Risk"),
    Extreme     UMETA(DisplayName = "Extreme Risk")
};

USTRUCT(BlueprintType)
struct FAugmentEffects
{
    GENERATED_BODY()

    // Movement augmentation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    float MovementSpeedBonus = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    float JumpHeightBonus = 0.0f;

    // Combat augmentation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
    float ReactionTimeBonus = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
    float AccuracyBonus = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
    float RecoilReductionBonus = 0.0f;

    // Vision augmentation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Vision")
    float ZoomCapability = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Vision")
    bool ThermalVision = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Vision")
    bool NightVision = false;

    // Defense augmentation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Defense")
    float DamageReductionPercentage = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Defense")
    float ExplosiveResistanceBonus = 0.0f;

    // Neural augmentation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Neural")
    float HackingSpeedBonus = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Neural")
    float DataProcessingBonus = 0.0f;
};

USTRUCT(BlueprintType)
struct FAugmentRisks
{
    GENERATED_BODY()

    // Installation risks
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Installation")
    float BlackoutChance = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Installation")
    float GlareChance = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Installation")
    float InfectionChance = 0.0f;

    // Operation risks
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Operation")
    float MalfunctionChance = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Operation")
    float EMPVulnerability = 0.0f;

    // Conflict risks (incompatible augments)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conflict")
    FGameplayTagContainer ConflictTags;
};

/**
 * Data asset defining player augmentation options
 */
UCLASS(BlueprintType)
class TGCOMBAT_API UTGAugmentData : public UDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    FString AugmentName;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    EAugmentType AugmentType;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    FText Description;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Basic Info")
    EAugmentRisk RiskLevel;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effects")
    FAugmentEffects PositiveEffects;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Risks")
    FAugmentRisks InstallationRisks;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Requirements")
    int32 RequiredMedicalLevel = 1;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Requirements")
    int32 InstallationCost = 1000;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Requirements")
    FGameplayTagContainer PrerequisiteAugments;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Requirements")
    FGameplayTagContainer ExclusiveWith;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Visual")
    TSoftObjectPtr<UTexture2D> AugmentIcon;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Visual")
    TSoftObjectPtr<UMaterialInstance> SkinModification;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    TSoftObjectPtr<USoundCue> InstallationSound;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    TSoftObjectPtr<USoundCue> OperationSound;
};