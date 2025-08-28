#include "TGTerritorialManager.h"
#include "TGWorld.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "HAL/PlatformFilemanager.h"

UTGTerritorialManager::UTGTerritorialManager()
{
    TerritorialUpdateFrequency = 1.0f; // 1 second update cycle
    CacheRefreshInterval = 30.0f; // 30 second cache refresh
    LastUpdateTime = 0.0f;
    LastCacheRefresh = 0.0f;
    TerritorialWebSocket = nullptr;
    TerritorialDatabase = nullptr;
}

void UTGTerritorialManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    UE_LOG(LogTGWorld, Log, TEXT("Initializing Territorial Management System"));
    
    // Initialize territorial system
    if (!InitializeTerritorialSystem())
    {
        UE_LOG(LogTGWorld, Error, TEXT("Failed to initialize territorial system"));
        return;
    }

    // Connect to territorial database
    if (!ConnectToTerritorialDatabase())
    {
        UE_LOG(LogTGWorld, Warning, TEXT("Territorial database connection failed - operating in offline mode"));
    }

    // Load initial territorial data
    RefreshTerritorialCache();
    
    // Set up periodic update timer since WorldSubsystems don't tick
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(UpdateTimerHandle, 
            FTimerDelegate::CreateUObject(this, &UTGTerritorialManager::ProcessTerritorialUpdates), 
            TerritorialUpdateFrequency, true);
            
        World->GetTimerManager().SetTimer(CacheRefreshTimerHandle,
            FTimerDelegate::CreateUObject(this, &UTGTerritorialManager::RefreshTerritorialCache),
            CacheRefreshInterval, true);
    }
    
    UE_LOG(LogTGWorld, Log, TEXT("Territorial Management System initialized successfully"));
}

void UTGTerritorialManager::Deinitialize()
{
    UE_LOG(LogTGWorld, Log, TEXT("Deinitializing Territorial Management System"));
    
    // Clear periodic update timers
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(UpdateTimerHandle);
        World->GetTimerManager().ClearTimer(CacheRefreshTimerHandle);
    }
    
    // Cleanup WebSocket connection
    if (TerritorialWebSocket)
    {
        TerritorialWebSocket = nullptr;
    }
    
    // Cleanup database connection
    if (TerritorialDatabase)
    {
        TerritorialDatabase = nullptr;
    }
    
    // Clear caches
    TerritoryCache.Empty();
    LocationToTerritoryCache.Empty();
    
    Super::Deinitialize();
}

// Note: WorldSubsystems don't have Tick functionality like ActorComponents
// Territorial updates will be handled via timer delegates or other mechanisms

bool UTGTerritorialManager::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

bool UTGTerritorialManager::InitializeTerritorialSystem()
{
    UE_LOG(LogTGWorld, Log, TEXT("Initializing territorial system components"));
    
    // Initialize core territorial data structures
    TerritoryCache.Empty();
    LocationToTerritoryCache.Empty();
    
    // TODO: Initialize WebSocket client for real-time updates
    // This will connect to the territorial update service
    
    // TODO: Initialize database client for PostgreSQL connection
    // This will handle territorial data persistence
    
    return true;
}

FTGTerritoryData UTGTerritorialManager::GetTerritoryData(int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        return *TerritoryData;
    }
    
    // Return empty territory data if not found
    UE_LOG(LogTGWorld, Warning, TEXT("Territory data not found for ID: %d"), TerritoryId);
    return FTGTerritoryData();
}

TArray<FTGTerritoryData> UTGTerritorialManager::GetAllTerritories()
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    TArray<FTGTerritoryData> AllTerritories;
    for (const auto& TerritoryPair : TerritoryCache)
    {
        AllTerritories.Add(TerritoryPair.Value);
    }
    
    return AllTerritories;
}

TArray<FTGTerritoryData> UTGTerritorialManager::GetTerritoriesInRadius(FVector2D CenterPoint, float Radius)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    TArray<FTGTerritoryData> TerritoriesInRadius;
    
    for (const auto& TerritoryPair : TerritoryCache)
    {
        const FTGTerritoryData& Territory = TerritoryPair.Value;
        float Distance = FVector2D::Distance(CenterPoint, Territory.Bounds.CenterPoint);
        
        if (Distance <= Radius + Territory.Bounds.InfluenceRadius)
        {
            TerritoriesInRadius.Add(Territory);
        }
    }
    
    return TerritoriesInRadius;
}

int32 UTGTerritorialManager::GetControllingFaction(int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        return TerritoryData->CurrentControllerFactionId;
    }
    
    return 0; // No controlling faction
}

bool UTGTerritorialManager::IsTerritoryContested(int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        return TerritoryData->bContested;
    }
    
    return false;
}

bool UTGTerritorialManager::UpdateFactionInfluence(int32 TerritoryId, int32 FactionId, int32 InfluenceChange)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId);
    if (!TerritoryData)
    {
        UE_LOG(LogTGWorld, Warning, TEXT("Cannot update influence - territory not found: %d"), TerritoryId);
        return false;
    }
    
    // Find or create faction influence entry
    FTGFactionInfluence* FactionInfluence = nullptr;
    for (FTGFactionInfluence& Influence : TerritoryData->FactionInfluences)
    {
        if (Influence.FactionId == FactionId)
        {
            FactionInfluence = &Influence;
            break;
        }
    }
    
    if (!FactionInfluence)
    {
        // Create new faction influence entry
        FTGFactionInfluence NewInfluence;
        NewInfluence.FactionId = FactionId;
        NewInfluence.InfluenceLevel = 0;
        TerritoryData->FactionInfluences.Add(NewInfluence);
        FactionInfluence = &TerritoryData->FactionInfluences.Last();
    }
    
    // Update influence level
    int32 OldInfluence = FactionInfluence->InfluenceLevel;
    FactionInfluence->InfluenceLevel = FMath::Clamp(OldInfluence + InfluenceChange, 0, 100);
    FactionInfluence->LastActionTime = FDateTime::Now();
    
    // Update influence trend
    if (InfluenceChange > 0)
    {
        FactionInfluence->InfluenceTrend = TEXT("growing");
    }
    else if (InfluenceChange < 0)
    {
        FactionInfluence->InfluenceTrend = TEXT("declining");
    }
    
    // Check for control changes
    if (FactionInfluence->InfluenceLevel > 50 && TerritoryData->CurrentControllerFactionId != FactionId)
    {
        int32 OldController = TerritoryData->CurrentControllerFactionId;
        TerritoryData->CurrentControllerFactionId = FactionId;
        
        // Broadcast control change event
        OnTerritoryControlChanged.Broadcast(TerritoryId, OldController, FactionId);
        
        UE_LOG(LogTGWorld, Log, TEXT("Territory %d control changed from faction %d to faction %d"), 
               TerritoryId, OldController, FactionId);
    }
    
    // Broadcast influence change event
    OnInfluenceChanged.Broadcast(TerritoryId, FactionId, FactionInfluence->InfluenceLevel);
    
    // TODO: Persist changes to database
    // TODO: Broadcast changes via WebSocket
    
    return true;
}

int32 UTGTerritorialManager::GetFactionInfluence(int32 TerritoryId, int32 FactionId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        for (const FTGFactionInfluence& Influence : TerritoryData->FactionInfluences)
        {
            if (Influence.FactionId == FactionId)
            {
                return Influence.InfluenceLevel;
            }
        }
    }
    
    return 0; // No influence
}

TArray<FTGFactionInfluence> UTGTerritorialManager::GetTerritoryInfluences(int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        return TerritoryData->FactionInfluences;
    }
    
    return TArray<FTGFactionInfluence>();
}

bool UTGTerritorialManager::AttemptTerritoryCapture(int32 TerritoryId, int32 AttackingFactionId)
{
    // TODO: Implement territory capture logic
    // This should involve:
    // 1. Checking capture requirements
    // 2. Calculating success probability based on faction stats
    // 3. Processing the capture attempt
    // 4. Updating territorial control
    // 5. Broadcasting the result
    
    UE_LOG(LogTGWorld, Log, TEXT("Territory capture attempt: Territory %d by Faction %d"), 
           TerritoryId, AttackingFactionId);
    
    return false; // Placeholder
}

int32 UTGTerritorialManager::GetTerritoryAtLocation(FVector2D WorldLocation)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    // Check cache first for performance
    if (int32* CachedTerritoryId = LocationToTerritoryCache.Find(WorldLocation))
    {
        return *CachedTerritoryId;
    }
    
    // Search through all territories
    for (const auto& TerritoryPair : TerritoryCache)
    {
        const FTGTerritoryData& Territory = TerritoryPair.Value;
        
        if (IsPointInPolygon(WorldLocation, Territory.Bounds.BoundaryPoints))
        {
            // Cache the result for future queries
            LocationToTerritoryCache.Add(WorldLocation, Territory.TerritoryId);
            return Territory.TerritoryId;
        }
    }
    
    return 0; // No territory found
}

bool UTGTerritorialManager::IsLocationInTerritory(FVector2D WorldLocation, int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        return IsPointInPolygon(WorldLocation, TerritoryData->Bounds.BoundaryPoints);
    }
    
    return false;
}

float UTGTerritorialManager::GetDistanceToTerritoryBorder(FVector2D WorldLocation, int32 TerritoryId)
{
    FScopeLock Lock(&TerritorialDataMutex);
    
    if (FTGTerritoryData* TerritoryData = TerritoryCache.Find(TerritoryId))
    {
        return CalculateDistanceToPolygon(WorldLocation, TerritoryData->Bounds.BoundaryPoints);
    }
    
    return -1.0f; // Invalid distance
}

void UTGTerritorialManager::RequestTerritorialUpdate()
{
    // TODO: Request update from WebSocket service
    UE_LOG(LogTGWorld, Log, TEXT("Requesting territorial update from server"));
}

void UTGTerritorialManager::BroadcastTerritorialChange(int32 TerritoryId, const FString& ChangeType)
{
    // TODO: Broadcast change via WebSocket
    UE_LOG(LogTGWorld, Log, TEXT("Broadcasting territorial change: Territory %d, Type: %s"), 
           TerritoryId, *ChangeType);
}

bool UTGTerritorialManager::ConnectToTerritorialDatabase()
{
    // TODO: Implement PostgreSQL connection
    // This should connect to the territorial database schema
    UE_LOG(LogTGWorld, Log, TEXT("Connecting to territorial database"));
    return true; // Placeholder
}

void UTGTerritorialManager::RefreshTerritorialCache()
{
    // TODO: Load territorial data from database
    // For now, create sample data for testing
    
    FScopeLock Lock(&TerritorialDataMutex);
    
    // Sample Metro Territory (from existing lore)
    FTGTerritoryData MetroTerritory;
    MetroTerritory.TerritoryId = 1;
    MetroTerritory.TerritoryName = TEXT("Metro Region");
    MetroTerritory.TerritoryType = TEXT("region");
    MetroTerritory.Bounds.CenterPoint = FVector2D(0.0f, 0.0f);
    MetroTerritory.Bounds.InfluenceRadius = 2000.0f;
    MetroTerritory.Bounds.BoundaryPoints = {
        FVector2D(-2000.0f, -2000.0f),
        FVector2D(2000.0f, -2000.0f),
        FVector2D(2000.0f, 2000.0f),
        FVector2D(-2000.0f, 2000.0f)
    };
    MetroTerritory.CurrentControllerFactionId = 7; // Civic Wardens
    MetroTerritory.StrategicValue = 8;
    MetroTerritory.ResourceMultiplier = 1.2f;
    
    TerritoryCache.Add(1, MetroTerritory);
    
    UE_LOG(LogTGWorld, Log, TEXT("Territorial cache refreshed - %d territories loaded"), TerritoryCache.Num());
}

void UTGTerritorialManager::ProcessTerritorialUpdates()
{
    // TODO: Process real-time updates from WebSocket
    // This should handle incoming territorial changes
}

bool UTGTerritorialManager::IsPointInPolygon(const FVector2D& Point, const TArray<FVector2D>& Polygon)
{
    // Ray casting algorithm for point-in-polygon test
    bool bInside = false;
    int32 j = Polygon.Num() - 1;
    
    for (int32 i = 0; i < Polygon.Num(); i++)
    {
        const FVector2D& Vi = Polygon[i];
        const FVector2D& Vj = Polygon[j];
        
        if (((Vi.Y > Point.Y) != (Vj.Y > Point.Y)) &&
            (Point.X < (Vj.X - Vi.X) * (Point.Y - Vi.Y) / (Vj.Y - Vi.Y) + Vi.X))
        {
            bInside = !bInside;
        }
        j = i;
    }
    
    return bInside;
}

float UTGTerritorialManager::CalculateDistanceToPolygon(const FVector2D& Point, const TArray<FVector2D>& Polygon)
{
    float MinDistance = FLT_MAX;
    
    for (int32 i = 0; i < Polygon.Num(); i++)
    {
        int32 j = (i + 1) % Polygon.Num();
        
        // Calculate distance from point to line segment
        const FVector2D& A = Polygon[i];
        const FVector2D& B = Polygon[j];
        
        FVector2D AB = B - A;
        FVector2D AP = Point - A;
        
        float t = FVector2D::DotProduct(AP, AB) / FVector2D::DotProduct(AB, AB);
        t = FMath::Clamp(t, 0.0f, 1.0f);
        
        FVector2D ClosestPoint = A + t * AB;
        float Distance = FVector2D::Distance(Point, ClosestPoint);
        
        MinDistance = FMath::Min(MinDistance, Distance);
    }
    
    return MinDistance;
}

FVector2D UTGTerritorialManager::GetClosestPointOnPolygon(const FVector2D& Point, const TArray<FVector2D>& Polygon)
{
    float MinDistance = FLT_MAX;
    FVector2D ClosestPoint = Point;
    
    for (int32 i = 0; i < Polygon.Num(); i++)
    {
        int32 j = (i + 1) % Polygon.Num();
        
        const FVector2D& A = Polygon[i];
        const FVector2D& B = Polygon[j];
        
        FVector2D AB = B - A;
        FVector2D AP = Point - A;
        
        float t = FVector2D::DotProduct(AP, AB) / FVector2D::DotProduct(AB, AB);
        t = FMath::Clamp(t, 0.0f, 1.0f);
        
        FVector2D CandidatePoint = A + t * AB;
        float Distance = FVector2D::Distance(Point, CandidatePoint);
        
        if (Distance < MinDistance)
        {
            MinDistance = Distance;
            ClosestPoint = CandidatePoint;
        }
    }
    
    return ClosestPoint;
}