// Copyright Terminal Grounds. All Rights Reserved.

#include "TGProceduralAssetCache.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "UObject/ConstructorHelpers.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/FileHelper.h"
#include "Misc/DateTime.h"
#include "Misc/Guid.h"
#include "TimerManager.h"

// Include local enum definitions
#include "TGProceduralWorldSubsystem.h"

void UTGProceduralAssetCache::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // Load configuration
    LoadCacheConfiguration();

    // Initialize WebSocket connection
    InitializeWebSocketConnection();

    // Start maintenance timer
    StartMaintenanceTimer();

    UE_LOG(LogTemp, Log, TEXT("UTGProceduralAssetCache initialized with %d max entries"), MaxCacheEntries);
}

void UTGProceduralAssetCache::Deinitialize()
{
    // Clear timers
    if (GetGameInstance())
    {
        FTimerManager& TimerManager = GetGameInstance()->GetTimerManager();
        TimerManager.ClearTimer(MaintenanceTimerHandle);
        TimerManager.ClearTimer(ReconnectionTimerHandle);
    }

    // Clear cache
    ClearCache();

    Super::Deinitialize();
}

void UTGProceduralAssetCache::LoadCacheConfiguration()
{
    // Load configuration from project settings or config file
    // For now, use defaults
    MaxCacheEntries = 1000;
    CacheExpiryHours = 24.0f;
    WebSocketEndpoint = TEXT("ws://127.0.0.1:8766");
    bAutoImportAssets = true;
    AssetImportPath = TEXT("/Game/ProceduralAssets/");

    UE_LOG(LogTemp, Log, TEXT("Cache configuration loaded: Max=%d, Expiry=%.1fh"), MaxCacheEntries, CacheExpiryHours);
}

void UTGProceduralAssetCache::InitializeWebSocketConnection()
{
    // Initialize WebSocket connection to procedural generation service
    // This would require actual WebSocket implementation
    // For now, mark as disconnected and set up reconnection timer

    bWebSocketConnected = false;
    LastConnectionAttempt = FDateTime::Now();

    // Start reconnection timer
    if (GetGameInstance())
    {
        FTimerManager& TimerManager = GetGameInstance()->GetTimerManager();
        TimerManager.SetTimer(ReconnectionTimerHandle, [this]()
        {
            // Attempt WebSocket reconnection
            // Implementation would go here
            UE_LOG(LogTemp, Verbose, TEXT("Attempting WebSocket reconnection..."));
        }, 30.0f, true); // Try every 30 seconds
    }
}

void UTGProceduralAssetCache::StartMaintenanceTimer()
{
    if (GetGameInstance())
    {
        FTimerManager& TimerManager = GetGameInstance()->GetTimerManager();
        TimerManager.SetTimer(MaintenanceTimerHandle, [this]()
        {
            PerformCacheMaintenance();
        }, 300.0f, true); // Every 5 minutes
    }
}

bool UTGProceduralAssetCache::IsCached(const FString& CacheKey) const
{
    FScopeLock Lock(&CacheMutex);
    return CacheEntries.Contains(CacheKey);
}

EAssetCacheStatus UTGProceduralAssetCache::GetCacheStatus(const FString& CacheKey) const
{
    FScopeLock Lock(&CacheMutex);
    
    if (const FProceduralAssetCacheEntry* Entry = CacheEntries.Find(CacheKey))
    {
        // Check if expired
        FTimespan TimeSinceCreation = FDateTime::Now() - Entry->CreatedTime;
        if (TimeSinceCreation.GetTotalHours() > CacheExpiryHours)
        {
            return EAssetCacheStatus::Expired;
        }
        
        return Entry->Status;
    }
    
    return EAssetCacheStatus::NotCached;
}

UObject* UTGProceduralAssetCache::GetCachedAsset(const FString& CacheKey)
{
    FScopeLock Lock(&CacheMutex);
    
    FProceduralAssetCacheEntry* Entry = CacheEntries.Find(CacheKey);
    if (!Entry)
    {
        CacheMisses++;
        return nullptr;
    }

    // Check if expired
    FTimespan TimeSinceCreation = FDateTime::Now() - Entry->CreatedTime;
    if (TimeSinceCreation.GetTotalHours() > CacheExpiryHours)
    {
        Entry->Status = EAssetCacheStatus::Expired;
        CacheMisses++;
        return nullptr;
    }

    // Update access tracking
    UpdateAccessTime(CacheKey);
    CacheHits++;

    // Return cached asset
    if (Entry->CachedAsset.IsValid())
    {
        return Entry->CachedAsset.Get();
    }
    else if (!Entry->AssetPath.IsEmpty())
    {
        // Try to load asset from path
        UObject* LoadedAsset = LoadAssetFromPath(Entry->AssetPath, Entry->AssetType);
        if (LoadedAsset)
        {
            Entry->CachedAsset = LoadedAsset;
            return LoadedAsset;
        }
    }

    CacheMisses++;
    return nullptr;
}

bool UTGProceduralAssetCache::CacheAsset(const FString& CacheKey, UObject* Asset, EProceduralAssetType AssetType, const TMap<FString, FString>& Metadata)
{
    if (!Asset)
    {
        UE_LOG(LogTemp, Warning, TEXT("Attempted to cache null asset with key: %s"), *CacheKey);
        return false;
    }

    FScopeLock Lock(&CacheMutex);

    // Create cache entry
    FProceduralAssetCacheEntry NewEntry;
    NewEntry.CacheKey = CacheKey;
    NewEntry.AssetType = AssetType;
    NewEntry.Status = EAssetCacheStatus::Cached;
    NewEntry.CachedAsset = Asset;
    NewEntry.CreatedTime = FDateTime::Now();
    NewEntry.LastAccessTime = FDateTime::Now();
    NewEntry.AccessCount = 1;
    NewEntry.Metadata = Metadata;

    // Get asset path if available
    if (Asset->GetPackage())
    {
        NewEntry.AssetPath = Asset->GetPackage()->GetName();
    }

    // Add to cache (or replace existing)
    CacheEntries.Add(CacheKey, NewEntry);

    // Perform cache size maintenance if needed
    if (CacheEntries.Num() > MaxCacheEntries)
    {
        EvictLRUEntries();
    }

    UE_LOG(LogTemp, Log, TEXT("Cached asset: %s (Type: %d)"), *CacheKey, (int32)AssetType);

    // Broadcast event
    OnAssetCached.Broadcast(CacheKey, true);

    return true;
}

void UTGProceduralAssetCache::InvalidateCache(const FString& CacheKey)
{
    FScopeLock Lock(&CacheMutex);
    
    if (CacheEntries.Remove(CacheKey) > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Invalidated cache entry: %s"), *CacheKey);
    }
}

void UTGProceduralAssetCache::InvalidateTerritoryCache(int32 TerritoryId)
{
    FScopeLock Lock(&CacheMutex);
    
    TArray<FString> KeysToRemove;
    FString TerritoryPrefix = FString::Printf(TEXT("territory_%d_"), TerritoryId);
    
    for (const auto& Entry : CacheEntries)
    {
        if (Entry.Key.StartsWith(TerritoryPrefix))
        {
            KeysToRemove.Add(Entry.Key);
        }
    }
    
    for (const FString& Key : KeysToRemove)
    {
        CacheEntries.Remove(Key);
    }
    
    if (KeysToRemove.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Invalidated %d cache entries for territory %d"), KeysToRemove.Num(), TerritoryId);
    }
}

void UTGProceduralAssetCache::InvalidateFactionCache(ELocalFactionID FactionId)
{
    FScopeLock Lock(&CacheMutex);
    
    TArray<FString> KeysToRemove;
    FString FactionPrefix = FString::Printf(TEXT("faction_%d_"), (int32)FactionId);
    
    for (const auto& Entry : CacheEntries)
    {
        if (Entry.Key.Contains(FactionPrefix))
        {
            KeysToRemove.Add(Entry.Key);
        }
    }
    
    for (const FString& Key : KeysToRemove)
    {
        CacheEntries.Remove(Key);
    }
    
    if (KeysToRemove.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Invalidated %d cache entries for faction %d"), KeysToRemove.Num(), (int32)FactionId);
    }
}

void UTGProceduralAssetCache::ClearCache()
{
    FScopeLock Lock(&CacheMutex);
    
    int32 ClearedEntries = CacheEntries.Num();
    CacheEntries.Empty();
    
    UE_LOG(LogTemp, Log, TEXT("Cleared cache: %d entries removed"), ClearedEntries);
    
    // Broadcast event
    OnCacheCleared.Broadcast(ClearedEntries);
}

FString UTGProceduralAssetCache::RequestAssetGeneration(const FAssetGenerationRequest& Request)
{
    // Check if already cached
    FString CacheKey = BuildAssetCacheKey(Request);
    if (IsCached(CacheKey))
    {
        UE_LOG(LogTemp, Log, TEXT("Asset already cached for request: %s"), *Request.RequestId);
        return Request.RequestId;
    }

    FScopeLock Lock(&RequestMutex);
    
    // Add to active requests
    ActiveRequests.Add(Request.RequestId, Request);
    GenerationRequests++;
    
    // Create pending cache entry
    {
        FScopeLock CacheLock(&CacheMutex);
        FProceduralAssetCacheEntry PendingEntry;
        PendingEntry.CacheKey = CacheKey;
        PendingEntry.AssetType = Request.AssetType;
        PendingEntry.Status = EAssetCacheStatus::Generating;
        PendingEntry.GenerationRequestId = Request.RequestId;
        PendingEntry.CreatedTime = FDateTime::Now();
        PendingEntry.LastAccessTime = FDateTime::Now();
        
        CacheEntries.Add(CacheKey, PendingEntry);
    }
    
    // Send request to generation service
    SendGenerationRequest(Request);
    
    UE_LOG(LogTemp, Log, TEXT("Requested asset generation: %s"), *Request.RequestId);
    
    return Request.RequestId;
}

bool UTGProceduralAssetCache::CancelGenerationRequest(const FString& RequestId)
{
    FScopeLock Lock(&RequestMutex);
    
    if (ActiveRequests.Remove(RequestId) > 0)
    {
        // Update cache entry status
        FScopeLock CacheLock(&CacheMutex);
        for (auto& Entry : CacheEntries)
        {
            if (Entry.Value.GenerationRequestId == RequestId)
            {
                Entry.Value.Status = EAssetCacheStatus::Failed;
                break;
            }
        }
        
        UE_LOG(LogTemp, Log, TEXT("Cancelled generation request: %s"), *RequestId);
        return true;
    }
    
    return false;
}

TArray<FString> UTGProceduralAssetCache::GetActiveGenerationRequests() const
{
    FScopeLock Lock(&RequestMutex);
    
    TArray<FString> RequestIds;
    ActiveRequests.GetKeys(RequestIds);
    return RequestIds;
}

TArray<FString> UTGProceduralAssetCache::GetCachedAssetKeys() const
{
    FScopeLock Lock(&CacheMutex);
    
    TArray<FString> Keys;
    CacheEntries.GetKeys(Keys);
    return Keys;
}

FProceduralAssetCacheEntry UTGProceduralAssetCache::GetCacheEntry(const FString& CacheKey) const
{
    FScopeLock Lock(&CacheMutex);
    
    if (const FProceduralAssetCacheEntry* Entry = CacheEntries.Find(CacheKey))
    {
        return *Entry;
    }
    
    return FProceduralAssetCacheEntry(); // Return default entry
}

int32 UTGProceduralAssetCache::GetCacheSize() const
{
    FScopeLock Lock(&CacheMutex);
    return CacheEntries.Num();
}

float UTGProceduralAssetCache::GetCacheHitRate() const
{
    int32 TotalRequests = CacheHits + CacheMisses;
    return TotalRequests > 0 ? (float)CacheHits / TotalRequests : 0.0f;
}

FString UTGProceduralAssetCache::BuildCacheKey(int32 TerritoryId, ELocalTerritoryType TerritoryType, ELocalFactionID FactionId, EProceduralAssetType AssetType, int32 Seed) const
{
    return FString::Printf(TEXT("territory_%d_type_%d_faction_%d_asset_%d_seed_%d"), 
                          TerritoryId, (int32)TerritoryType, (int32)FactionId, (int32)AssetType, Seed);
}

FString UTGProceduralAssetCache::BuildAssetCacheKey(const FAssetGenerationRequest& Request) const
{
    return BuildCacheKey(Request.TerritoryId, Request.TerritoryType, Request.DominantFaction, Request.AssetType, Request.RandomSeed);
}

void UTGProceduralAssetCache::SetCacheMaxSize(int32 MaxEntries)
{
    MaxCacheEntries = FMath::Max(1, MaxEntries);
    UE_LOG(LogTemp, Log, TEXT("Cache max size set to: %d"), MaxCacheEntries);
}

void UTGProceduralAssetCache::SetCacheExpiryTime(float ExpiryHours)
{
    CacheExpiryHours = FMath::Max(0.1f, ExpiryHours);
    UE_LOG(LogTemp, Log, TEXT("Cache expiry time set to: %.1f hours"), CacheExpiryHours);
}

void UTGProceduralAssetCache::SetGenerationServiceEndpoint(const FString& WebSocketUrl)
{
    WebSocketEndpoint = WebSocketUrl;
    bWebSocketConnected = false; // Force reconnection
    UE_LOG(LogTemp, Log, TEXT("Generation service endpoint set to: %s"), *WebSocketUrl);
}

TMap<FString, int32> UTGProceduralAssetCache::GetCacheStatistics() const
{
    TMap<FString, int32> Stats;
    
    Stats.Add(TEXT("CacheEntries"), GetCacheSize());
    Stats.Add(TEXT("CacheHits"), CacheHits);
    Stats.Add(TEXT("CacheMisses"), CacheMisses);
    Stats.Add(TEXT("ActiveRequests"), GetActiveGenerationRequests().Num());
    Stats.Add(TEXT("GenerationRequests"), GenerationRequests);
    Stats.Add(TEXT("SuccessfulGenerations"), SuccessfulGenerations);
    Stats.Add(TEXT("HitRatePercent"), FMath::RoundToInt(GetCacheHitRate() * 100.0f));
    
    return Stats;
}

void UTGProceduralAssetCache::SendGenerationRequest(const FAssetGenerationRequest& Request)
{
    // Send WebSocket message to generation service
    // This would require actual WebSocket implementation
    UE_LOG(LogTemp, Log, TEXT("Sending generation request: %s (WebSocket not implemented)"), *Request.RequestId);
}

void UTGProceduralAssetCache::HandleWebSocketMessage(const FString& Message)
{
    // Parse WebSocket message from generation service
    // This would handle JSON parsing and dispatch to appropriate handlers
    UE_LOG(LogTemp, Verbose, TEXT("Received WebSocket message: %s"), *Message);
}

void UTGProceduralAssetCache::HandleGenerationComplete(const FString& RequestId, const FString& AssetPath, bool bSuccess)
{
    FScopeLock RequestLock(&RequestMutex);
    
    // Remove from active requests
    FAssetGenerationRequest* Request = ActiveRequests.Find(RequestId);
    if (!Request)
    {
        UE_LOG(LogTemp, Warning, TEXT("Received completion for unknown request: %s"), *RequestId);
        return;
    }
    
    FAssetGenerationRequest CompletedRequest = *Request;
    ActiveRequests.Remove(RequestId);
    
    // Update cache entry
    {
        FScopeLock CacheLock(&CacheMutex);
        
        FString CacheKey = BuildAssetCacheKey(CompletedRequest);
        FProceduralAssetCacheEntry* Entry = CacheEntries.Find(CacheKey);
        
        if (Entry)
        {
            if (bSuccess)
            {
                Entry->Status = EAssetCacheStatus::Cached;
                Entry->AssetPath = AssetPath;
                
                // Try to load the asset
                if (bAutoImportAssets && !AssetPath.IsEmpty())
                {
                    UObject* LoadedAsset = LoadAssetFromPath(AssetPath, Entry->AssetType);
                    if (LoadedAsset)
                    {
                        Entry->CachedAsset = LoadedAsset;
                        SuccessfulGenerations++;
                    }
                }
            }
            else
            {
                Entry->Status = EAssetCacheStatus::Failed;
            }
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("Generation completed: %s, Success: %s"), *RequestId, bSuccess ? TEXT("Yes") : TEXT("No"));
    
    // Broadcast completion event
    OnAssetGenerated.Broadcast(RequestId, bSuccess, AssetPath);
}

void UTGProceduralAssetCache::PerformCacheMaintenance()
{
    UE_LOG(LogTemp, Verbose, TEXT("Performing cache maintenance..."));
    
    EvictExpiredEntries();
    ValidateAssetReferences();
    
    // Log statistics
    TMap<FString, int32> Stats = GetCacheStatistics();
    UE_LOG(LogTemp, Log, TEXT("Cache Stats - Entries: %d, Hits: %d, Misses: %d, Hit Rate: %d%%"), 
           Stats[TEXT("CacheEntries")], Stats[TEXT("CacheHits")], Stats[TEXT("CacheMisses")], Stats[TEXT("HitRatePercent")]);
}

void UTGProceduralAssetCache::EvictExpiredEntries()
{
    FScopeLock Lock(&CacheMutex);
    
    TArray<FString> ExpiredKeys;
    FDateTime CurrentTime = FDateTime::Now();
    
    for (const auto& Entry : CacheEntries)
    {
        FTimespan TimeSinceCreation = CurrentTime - Entry.Value.CreatedTime;
        if (TimeSinceCreation.GetTotalHours() > CacheExpiryHours)
        {
            ExpiredKeys.Add(Entry.Key);
        }
    }
    
    for (const FString& Key : ExpiredKeys)
    {
        CacheEntries.Remove(Key);
    }
    
    if (ExpiredKeys.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Evicted %d expired cache entries"), ExpiredKeys.Num());
    }
}

void UTGProceduralAssetCache::EvictLRUEntries()
{
    FScopeLock Lock(&CacheMutex);
    
    if (CacheEntries.Num() <= MaxCacheEntries)
    {
        return;
    }
    
    // Sort by last access time and remove oldest
    TArray<TPair<FString, FProceduralAssetCacheEntry>> SortedEntries;
    for (const auto& Entry : CacheEntries)
    {
        SortedEntries.Add(TPair<FString, FProceduralAssetCacheEntry>(Entry.Key, Entry.Value));
    }
    
    SortedEntries.Sort([](const TPair<FString, FProceduralAssetCacheEntry>& A, const TPair<FString, FProceduralAssetCacheEntry>& B)
    {
        return A.Value.LastAccessTime < B.Value.LastAccessTime;
    });
    
    int32 EntriesToRemove = CacheEntries.Num() - MaxCacheEntries;
    for (int32 i = 0; i < EntriesToRemove; i++)
    {
        CacheEntries.Remove(SortedEntries[i].Key);
    }
    
    UE_LOG(LogTemp, Log, TEXT("Evicted %d LRU cache entries"), EntriesToRemove);
}

void UTGProceduralAssetCache::ValidateAssetReferences()
{
    FScopeLock Lock(&CacheMutex);
    
    TArray<FString> InvalidKeys;
    
    for (const auto& Entry : CacheEntries)
    {
        if (Entry.Value.CachedAsset.IsValid() && !IsValid(Entry.Value.CachedAsset.Get()))
        {
            InvalidKeys.Add(Entry.Key);
        }
    }
    
    for (const FString& Key : InvalidKeys)
    {
        CacheEntries.Remove(Key);
    }
    
    if (InvalidKeys.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Removed %d invalid asset references from cache"), InvalidKeys.Num());
    }
}

UObject* UTGProceduralAssetCache::LoadAssetFromPath(const FString& AssetPath, EProceduralAssetType AssetType)
{
    if (AssetPath.IsEmpty())
    {
        return nullptr;
    }
    
    // Try to load asset using asset registry
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    
    FAssetData AssetData = AssetRegistryModule.Get().GetAssetByObjectPath(FSoftObjectPath(AssetPath));
    if (AssetData.IsValid())
    {
        UObject* LoadedAsset = AssetData.GetAsset();
        if (LoadedAsset)
        {
            UE_LOG(LogTemp, Verbose, TEXT("Loaded asset from path: %s"), *AssetPath);
            return LoadedAsset;
        }
    }
    
    // Try direct load
    UObject* LoadedAsset = LoadObject<UObject>(nullptr, *AssetPath);
    if (LoadedAsset)
    {
        UE_LOG(LogTemp, Verbose, TEXT("Direct loaded asset: %s"), *AssetPath);
        return LoadedAsset;
    }
    
    UE_LOG(LogTemp, Warning, TEXT("Failed to load asset from path: %s"), *AssetPath);
    return nullptr;
}

bool UTGProceduralAssetCache::ImportGeneratedAsset(const FString& SourcePath, const FString& TargetPath)
{
    // Import generated asset into UE5 content directory
    // This would require integration with UE5's asset import system
    UE_LOG(LogTemp, Log, TEXT("Asset import not implemented: %s -> %s"), *SourcePath, *TargetPath);
    return false;
}

FString UTGProceduralAssetCache::GenerateRequestId() const
{
    return FGuid::NewGuid().ToString();
}

bool UTGProceduralAssetCache::IsAssetPathValid(const FString& AssetPath) const
{
    return !AssetPath.IsEmpty() && FPlatformFileManager::Get().GetPlatformFile().FileExists(*AssetPath);
}

void UTGProceduralAssetCache::UpdateAccessTime(const FString& CacheKey)
{
    FProceduralAssetCacheEntry* Entry = CacheEntries.Find(CacheKey);
    if (Entry)
    {
        Entry->LastAccessTime = FDateTime::Now();
        Entry->AccessCount++;
    }
}