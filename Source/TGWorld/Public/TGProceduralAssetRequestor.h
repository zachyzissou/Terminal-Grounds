// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TGProceduralAssetCache.h"
#include "TGProceduralAssetRequestor.generated.h"

/**
 * Example component showing how to request different types of procedural assets
 * This demonstrates the comprehensive asset generation capabilities
 */
UCLASS(BlueprintType, ClassGroup=(ProceduralGeneration), meta=(BlueprintSpawnableComponent))
class TGWORLD_API UTGProceduralAssetRequestor : public UActorComponent
{
    GENERATED_BODY()

public:
    UTGProceduralAssetRequestor();

    // === VEHICLE GENERATION ===
    
    /**
     * Request procedural vehicle generation for a faction
     * Uses FIXED_faction_vehicle_concepts.py (100% success rate)
     */
    UFUNCTION(BlueprintCallable, Category = "Vehicles", meta = (CallInEditor = "true"))
    FString RequestFactionVehicle(ELocalFactionID Faction, const FString& VehicleType = TEXT("transport"));

    /**
     * Request multiple vehicle variants
     */
    UFUNCTION(BlueprintCallable, Category = "Vehicles")
    TArray<FString> RequestVehicleSet(ELocalFactionID Faction, int32 Count = 3);

    // === WEAPON GENERATION ===

    /**
     * Request procedural weapon generation
     * Uses terminal_grounds_pipeline.py weapon generation
     */
    UFUNCTION(BlueprintCallable, Category = "Weapons", meta = (CallInEditor = "true"))
    FString RequestFactionWeapon(ELocalFactionID Faction, const FString& WeaponType = TEXT("rifle"));

    /**
     * Request weapon progression tier (Field -> Splice -> Monolith)
     */
    UFUNCTION(BlueprintCallable, Category = "Weapons")
    TArray<FString> RequestWeaponTier(ELocalFactionID Faction, const FString& WeaponClass, int32 TierLevel = 1);

    // === UI/HUD GENERATION ===

    /**
     * Request UI/HUD elements for faction
     * Uses FIXED_faction_ui_hud_concepts.py (100% success rate, copyright-safe)
     */
    UFUNCTION(BlueprintCallable, Category = "UI", meta = (CallInEditor = "true"))
    FString RequestFactionHUD(ELocalFactionID Faction, const FString& ElementType = TEXT("status_overlay"));

    /**
     * Request complete UI theme for faction
     */
    UFUNCTION(BlueprintCallable, Category = "UI")
    TArray<FString> RequestFactionUITheme(ELocalFactionID Faction);

    // === CONCEPT ART GENERATION ===

    /**
     * Request concept art for game elements
     */
    UFUNCTION(BlueprintCallable, Category = "Concept Art", meta = (CallInEditor = "true"))
    FString RequestConceptArt(ELocalFactionID Faction, const FString& Subject = TEXT("operator"));

    /**
     * Request character portraits for faction
     */
    UFUNCTION(BlueprintCallable, Category = "Concept Art")
    TArray<FString> RequestCharacterPortraits(ELocalFactionID Faction, const TArray<FString>& CharacterTypes);

    // === EMBLEM/LOGO GENERATION ===

    /**
     * Request faction emblem generation
     * Uses faction_emblem_fixes.py or multi-seed logo generation (95% success)
     */
    UFUNCTION(BlueprintCallable, Category = "Branding", meta = (CallInEditor = "true"))
    FString RequestFactionEmblem(ELocalFactionID Faction);

    /**
     * Request logo variations (main, horizontal, icon, wordmark, etc.)
     */
    UFUNCTION(BlueprintCallable, Category = "Branding")
    TArray<FString> RequestLogoSet(ELocalFactionID Faction);

    // === ENVIRONMENT GENERATION ===

    /**
     * Request environmental assets
     * Uses terminal_grounds_generator.py (92% success rate with proven params)
     */
    UFUNCTION(BlueprintCallable, Category = "Environment", meta = (CallInEditor = "true"))
    FString RequestEnvironment(const FString& LocationType = TEXT("metro_corridor"));

    /**
     * Request faction-influenced environment
     */
    UFUNCTION(BlueprintCallable, Category = "Environment")
    FString RequestFactionEnvironment(ELocalFactionID Faction, const FString& LocationType);

    // === BATCH REQUESTS ===

    /**
     * Request complete asset package for faction (vehicles, weapons, UI, emblems)
     */
    UFUNCTION(BlueprintCallable, Category = "Batch Generation", meta = (CallInEditor = "true"))
    TArray<FString> RequestFactionAssetPackage(ELocalFactionID Faction);

    /**
     * Request territorial control assets (buildings, signage, props)
     */
    UFUNCTION(BlueprintCallable, Category = "Batch Generation")
    TArray<FString> RequestTerritorialAssets(int32 TerritoryID, ELocalFactionID ControllingFaction);

    // === MONITORING & STATISTICS ===

    /**
     * Get generation statistics and success rates
     */
    UFUNCTION(BlueprintPure, Category = "Statistics")
    TMap<FString, int32> GetGenerationStatistics();

    /**
     * Get active generation requests
     */
    UFUNCTION(BlueprintPure, Category = "Statistics")
    TArray<FString> GetActiveRequests();

    /**
     * Check if specific asset is cached and ready
     */
    UFUNCTION(BlueprintPure, Category = "Cache")
    bool IsAssetReady(const FString& RequestID);

    // === CONFIGURATION ===

    /**
     * Set generation priority for requests
     */
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetGenerationPriority(const FString& Priority = TEXT("normal"));

    /**
     * Enable/disable automatic caching
     */
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetAutoCaching(bool bEnabled = true);

protected:
    virtual void BeginPlay() override;

    // Helper functions
    FAssetGenerationRequest CreateBaseRequest(EProceduralAssetType AssetType, ELocalFactionID Faction, const FString& AssetName);
    FString SubmitGenerationRequest(const FAssetGenerationRequest& Request);

    // Event handlers
    UFUNCTION()
    void OnAssetGenerated(FString RequestId, bool bSuccess, FString AssetPath);

    UFUNCTION()
    void OnAssetCached(FString CacheKey, bool bSuccess);

private:
    // Asset cache subsystem reference
    UPROPERTY()
    UTGProceduralAssetCache* AssetCache;

    // Configuration
    UPROPERTY(EditAnywhere, Category = "Configuration")
    FString DefaultPriority = TEXT("normal");

    UPROPERTY(EditAnywhere, Category = "Configuration")
    bool bAutoCache = true;

    UPROPERTY(EditAnywhere, Category = "Configuration")
    int32 DefaultSeed = 0;

    // Tracking
    UPROPERTY()
    TArray<FString> PendingRequests;

    UPROPERTY()
    TMap<FString, FString> RequestToAssetType;
};