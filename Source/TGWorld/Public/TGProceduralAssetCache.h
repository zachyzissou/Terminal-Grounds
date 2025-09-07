// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInterface.h"
#include "TGProceduralAssetCache.generated.h"

// Forward declarations
enum class ELocalFactionID : uint8;
enum class ELocalTerritoryType : uint8;

UENUM(BlueprintType)
enum class EProceduralAssetType : uint8
{
    // Environmental Assets
    Building        UMETA(DisplayName = "Building"),
    Landscape       UMETA(DisplayName = "Landscape"),
    Detail          UMETA(DisplayName = "Detail"),
    Vegetation      UMETA(DisplayName = "Vegetation"),
    
    // Game Assets  
    Vehicle         UMETA(DisplayName = "Vehicle"),
    Weapon          UMETA(DisplayName = "Weapon"),
    Character       UMETA(DisplayName = "Character"),
    Props           UMETA(DisplayName = "Props"),
    
    // UI Assets
    HudElement      UMETA(DisplayName = "HUD Element"),
    UITexture       UMETA(DisplayName = "UI Texture"),
    IconSet         UMETA(DisplayName = "Icon Set"),
    
    // Branding Assets
    FactionEmblem   UMETA(DisplayName = "Faction Emblem"),
    Logo            UMETA(DisplayName = "Logo"),
    Signage         UMETA(DisplayName = "Signage"),
    
    // Art Assets
    ConceptArt      UMETA(DisplayName = "Concept Art"),
    Portrait        UMETA(DisplayName = "Portrait"),
    
    // Technical Assets
    Texture         UMETA(DisplayName = "Texture"),
    Material        UMETA(DisplayName = "Material")
};

UENUM(BlueprintType)
enum class EAssetCacheStatus : uint8
{
    NotCached       UMETA(DisplayName = "Not Cached"),
    Cached          UMETA(DisplayName = "Cached"),
    Generating      UMETA(DisplayName = "Generating"),
    Failed          UMETA(DisplayName = "Failed"),
    Expired         UMETA(DisplayName = "Expired")
};

USTRUCT(BlueprintType)
struct TGWORLD_API FProceduralAssetCacheEntry
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    FString CacheKey;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    EProceduralAssetType AssetType = EProceduralAssetType::Building;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    EAssetCacheStatus Status = EAssetCacheStatus::NotCached;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    FString AssetPath;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    TWeakObjectPtr<UObject> CachedAsset;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    FDateTime CreatedTime;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    FDateTime LastAccessTime;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    int32 AccessCount = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    float GenerationTime = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    FString GenerationRequestId;

    UPROPERTY(BlueprintReadWrite, Category = "Cache")
    TMap<FString, FString> Metadata;

    FProceduralAssetCacheEntry()
    {
        CacheKey = "";
        AssetType = EProceduralAssetType::Building;
        Status = EAssetCacheStatus::NotCached;
        AssetPath = "";
        CreatedTime = FDateTime::Now();
        LastAccessTime = FDateTime::Now();
        AccessCount = 0;
        GenerationTime = 0.0f;
        GenerationRequestId = "";
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FAssetGenerationRequest
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    FString RequestId;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    int32 TerritoryId = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    ELocalTerritoryType TerritoryType;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    ELocalFactionID DominantFaction;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    EProceduralAssetType AssetType = EProceduralAssetType::Building;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    FVector CenterLocation = FVector::ZeroVector;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    float GenerationRadius = 10000.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    int32 RandomSeed = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Generation")
    TMap<FString, FString> RequestMetadata;

    FAssetGenerationRequest()
    {
        RequestId = FGuid::NewGuid().ToString();
        TerritoryId = 0;
        AssetType = EProceduralAssetType::Building;
        CenterLocation = FVector::ZeroVector;
        GenerationRadius = 10000.0f;
        RandomSeed = FMath::Rand();
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAssetCached, FString, CacheKey, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnAssetGenerated, FString, RequestId, bool, bSuccess, FString, AssetPath);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCacheCleared, int32, EntriesCleared);

/**
 * Procedural Asset Cache Subsystem
 * Manages caching and streaming of procedurally generated assets
 * Integrates with external generation services via WebSocket
 */
UCLASS(BlueprintType)
class TGWORLD_API UTGProceduralAssetCache : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // Subsystem lifecycle
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Cache management
    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    bool IsCached(const FString& CacheKey) const;

    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    EAssetCacheStatus GetCacheStatus(const FString& CacheKey) const;

    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    UObject* GetCachedAsset(const FString& CacheKey);

    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    bool CacheAsset(const FString& CacheKey, UObject* Asset, EProceduralAssetType AssetType);

    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    void InvalidateCache(const FString& CacheKey);

    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    void InvalidateTerritoryCache(int32 TerritoryId);

    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    void InvalidateFactionCache(ELocalFactionID FactionId);

    UFUNCTION(BlueprintCallable, Category = "Asset Cache")
    void ClearCache();

    // Asset generation
    UFUNCTION(BlueprintCallable, Category = "Asset Generation")
    FString RequestAssetGeneration(const FAssetGenerationRequest& Request);

    UFUNCTION(BlueprintCallable, Category = "Asset Generation")
    bool CancelGenerationRequest(const FString& RequestId);

    UFUNCTION(BlueprintPure, Category = "Asset Generation")
    TArray<FString> GetActiveGenerationRequests() const;

    // Cache queries
    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    TArray<FString> GetCachedAssetKeys() const;

    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    FProceduralAssetCacheEntry GetCacheEntry(const FString& CacheKey) const;

    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    int32 GetCacheSize() const;

    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    float GetCacheHitRate() const;

    // Cache key generation
    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    FString BuildCacheKey(int32 TerritoryId, ELocalTerritoryType TerritoryType, ELocalFactionID FactionId, EProceduralAssetType AssetType, int32 Seed = 0) const;

    UFUNCTION(BlueprintPure, Category = "Asset Cache")
    FString BuildAssetCacheKey(const FAssetGenerationRequest& Request) const;

    // Configuration
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetCacheMaxSize(int32 MaxEntries);

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetCacheExpiryTime(float ExpiryHours);

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetGenerationServiceEndpoint(const FString& WebSocketUrl);

    // Statistics
    UFUNCTION(BlueprintPure, Category = "Statistics")
    TMap<FString, int32> GetCacheStatistics() const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAssetCached OnAssetCached;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAssetGenerated OnAssetGenerated;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnCacheCleared OnCacheCleared;

protected:
    // Initialization
    void InitializeWebSocketConnection();
    void LoadCacheConfiguration();
    void StartMaintenanceTimer();

    // WebSocket communication
    void SendGenerationRequest(const FAssetGenerationRequest& Request);
    void HandleWebSocketMessage(const FString& Message);
    void HandleGenerationComplete(const FString& RequestId, const FString& AssetPath, bool bSuccess);

    // Cache maintenance
    void PerformCacheMaintenance();
    void EvictExpiredEntries();
    void EvictLRUEntries();
    void ValidateAssetReferences();

    // Asset loading
    UObject* LoadAssetFromPath(const FString& AssetPath, EProceduralAssetType AssetType);
    bool ImportGeneratedAsset(const FString& SourcePath, const FString& TargetPath);

    // Utility functions
    FString GenerateRequestId() const;
    bool IsAssetPathValid(const FString& AssetPath) const;
    void UpdateAccessTime(const FString& CacheKey);

private:
    // Cache storage
    UPROPERTY()
    TMap<FString, FProceduralAssetCacheEntry> CacheEntries;

    // Active generation requests
    UPROPERTY()
    TMap<FString, FAssetGenerationRequest> ActiveRequests;

    // Configuration
    UPROPERTY()
    int32 MaxCacheEntries = 1000;

    UPROPERTY()
    float CacheExpiryHours = 24.0f;

    UPROPERTY()
    FString WebSocketEndpoint = "ws://127.0.0.1:8766";

    UPROPERTY()
    bool bAutoImportAssets = true;

    UPROPERTY()
    FString AssetImportPath = "/Game/ProceduralAssets/";

    // Statistics
    UPROPERTY()
    int32 CacheHits = 0;

    UPROPERTY()
    int32 CacheMisses = 0;

    UPROPERTY()
    int32 GenerationRequests = 0;

    UPROPERTY()
    int32 SuccessfulGenerations = 0;

    // Timers
    FTimerHandle MaintenanceTimerHandle;
    FTimerHandle ReconnectionTimerHandle;

    // WebSocket connection (would need actual WebSocket implementation)
    bool bWebSocketConnected = false;
    FDateTime LastConnectionAttempt;

    // Thread safety
    mutable FCriticalSection CacheMutex;
    mutable FCriticalSection RequestMutex;
};