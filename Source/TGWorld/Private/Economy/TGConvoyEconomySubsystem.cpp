#include "Economy/TGConvoyEconomySubsystem.h"
#include "TGTerritorialManager.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Async/Async.h"
#include "Algo/MinElement.h"
#include "Misc/CString.h"

UTGConvoyEconomySubsystem::UTGConvoyEconomySubsystem()
    : IntegrityIndex(0.5f)
    , TerritorialManager(nullptr)
    , LastRouteUpdate(0.0f)
{
}

void UTGConvoyEconomySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // Get reference to territorial manager
    if (UWorld* World = GetWorld())
    {
        TerritorialManager = World->GetSubsystem<UTGTerritorialManager>();
        if (TerritorialManager)
        {
            // Bind to territorial events for real-time route adaptation
            TerritorialManager->OnTerritoryControlChanged.AddDynamic(this, &UTGConvoyEconomySubsystem::OnTerritoryControlChanged);
            TerritorialManager->OnTerritoryContested.AddDynamic(this, &UTGConvoyEconomySubsystem::OnTerritoryContested);
            
            UE_LOG(LogTemp, Log, TEXT("Convoy Economy: Connected to Territorial Manager"));
        }
        
        // Set up periodic route update timer
        World->GetTimerManager().SetTimer(
            RouteUpdateTimerHandle,
            FTimerDelegate::CreateUObject(this, &UTGConvoyEconomySubsystem::ProcessRouteUpdates),
            RouteUpdateFrequency,
            true
        );
    }
    
    // Initialize territorial connections cache
    InitializeTerritorialConnections();
}

void UTGConvoyEconomySubsystem::Deinitialize()
{
    // Clear route update timer
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(RouteUpdateTimerHandle);
    }
    
    // Unbind from territorial events
    if (TerritorialManager)
    {
        TerritorialManager->OnTerritoryControlChanged.RemoveDynamic(this, &UTGConvoyEconomySubsystem::OnTerritoryControlChanged);
        TerritorialManager->OnTerritoryContested.RemoveDynamic(this, &UTGConvoyEconomySubsystem::OnTerritoryContested);
    }
    
    // Clear caches
    FScopeLock Lock(&RouteDataMutex);
    FactionRouteCache.Empty();
    RouteHashToIdCache.Empty();
    TerritorialConnections.Empty();
    
    Super::Deinitialize();
}

void UTGConvoyEconomySubsystem::ApplyConvoyOutcome(float Delta, FName RouteId, EJobType JobType, bool bSuccess)
{
    const float SignedDelta = bSuccess ? FMath::Abs(Delta) : -FMath::Abs(Delta);
    const float Old = IntegrityIndex;
    IntegrityIndex = FMath::Clamp(IntegrityIndex + SignedDelta, 0.f, 1.f);
    
    // Update route performance metrics
    if (!RouteId.IsNone())
    {
        FScopeLock Lock(&RouteDataMutex);
        if (FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))
        {
            // Adjust route profitability based on outcome
            float ProfitAdjustment = bSuccess ? 0.1f : -0.05f;
            Route->ProfitabilityScore = FMath::Clamp(Route->ProfitabilityScore + ProfitAdjustment, 0.0f, 10.0f);
            Route->LastValidated = FDateTime::Now();
        }
    }
    
    BroadcastChange(Old, IntegrityIndex);
    
    // Broadcast convoy outcome for route metrics
    OnConvoyOutcome.Broadcast(RouteId, JobType, bSuccess);
}

void UTGConvoyEconomySubsystem::SetIntegrityIndex(float NewValue)
{
    const float Old = IntegrityIndex;
    IntegrityIndex = FMath::Clamp(NewValue, 0.f, 1.f);
    BroadcastChange(Old, IntegrityIndex);
}

void UTGConvoyEconomySubsystem::AdvanceDecay(float DeltaSeconds)
{
    if (DecayHalfLifeSeconds <= 0.f)
    {
        return;
    }
    const float Lambda = FMath::Loge(2.0f) / DecayHalfLifeSeconds;
    const float Old = IntegrityIndex;
    IntegrityIndex = Equilibrium + (IntegrityIndex - Equilibrium) * FMath::Exp(-Lambda * DeltaSeconds);
    if (!FMath::IsNearlyEqual(Old, IntegrityIndex))
    {
        BroadcastChange(Old, IntegrityIndex);
    }
}

void UTGConvoyEconomySubsystem::BroadcastChange(float OldIndex, float NewIndex)
{
    const float Delta = NewIndex - OldIndex;
    OnIntegrityIndexChanged.Broadcast(NewIndex, Delta);
}

// Dynamic Route Generation - Performance Critical Implementation
void UTGConvoyEconomySubsystem::GenerateRoutesBetweenTerritories(const FRouteGenerationParameters& Parameters)
{
    if (!TerritorialManager)
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot generate routes: TerritorialManager not available"));
        OnRouteGenerated.Broadcast(NAME_None, false);
        return;
    }
    
    // Performance optimization: Check cache first
    const uint32 RouteHash = GenerateRouteHash(Parameters);
    if (FName* ExistingRouteId = RouteHashToIdCache.Find(RouteHash))
    {
        // Route already exists and is valid
        if (FConvoyRoute* ExistingRoute = RegisteredRoutes.Find(*ExistingRouteId))
        {
            if (ExistingRoute->bIsActive)
            {
                OnRouteGenerated.Broadcast(*ExistingRouteId, true);
                return;
            }
        }
    }
    
    // Find optimal path using A* with territorial considerations
    TArray<int32> OptimalPath = FindOptimalPath(
        Parameters.SourceTerritoryId,
        Parameters.DestinationTerritoryId,
        Parameters.RequestingFactionId,
        Parameters.MaxHops
    );
    
    if (OptimalPath.Num() < 2)
    {
        UE_LOG(LogTemp, Warning, TEXT("No viable path found between territories %d and %d"), 
               Parameters.SourceTerritoryId, Parameters.DestinationTerritoryId);
        OnRouteGenerated.Broadcast(NAME_None, false);
        return;
    }
    
    // Create new route with performance metrics
    FConvoyRoute NewRoute;
    NewRoute.RouteId = GenerateUniqueRouteId(Parameters.RequestingFactionId, 
                                           Parameters.SourceTerritoryId, 
                                           Parameters.DestinationTerritoryId);
    NewRoute.RouteName = FString::Printf(TEXT("Route_%d_%d_to_%d"), 
                                       Parameters.RequestingFactionId,
                                       Parameters.SourceTerritoryId, 
                                       Parameters.DestinationTerritoryId);
    NewRoute.TerritorialPath = OptimalPath;
    NewRoute.ControllingFactionId = Parameters.RequestingFactionId;
    NewRoute.RouteHash = RouteHash;
    NewRoute.LastValidated = FDateTime::Now();
    
    // Calculate route metrics
    NewRoute.SecurityRating = CalculateRouteSecurityRating(OptimalPath);
    NewRoute.ProfitabilityScore = CalculateRouteProfitability(NewRoute);
    
    // Validate route meets security threshold
    if (NewRoute.SecurityRating < Parameters.MinSecurityThreshold)
    {
        UE_LOG(LogTemp, Warning, TEXT("Route security %.2f below threshold %.2f"), 
               NewRoute.SecurityRating, Parameters.MinSecurityThreshold);
        OnRouteGenerated.Broadcast(NAME_None, false);
        return;
    }
    
    // Generate waypoints from territorial path
    NewRoute.Waypoints.Empty();
    NewRoute.TotalDistance = 0.0f;
    
    for (int32 i = 0; i < OptimalPath.Num(); i++)
    {
        FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(OptimalPath[i]);
        FVector TerritoryCenter(TerritoryData.Bounds.CenterPoint.X, TerritoryData.Bounds.CenterPoint.Y, 0.0f);
        NewRoute.Waypoints.Add(TerritoryCenter);
        
        if (i > 0)
        {
            float SegmentDistance = FVector::Distance(
                NewRoute.Waypoints[i-1], 
                NewRoute.Waypoints[i]
            );
            NewRoute.TotalDistance += SegmentDistance;
        }
    }
    
    NewRoute.bIsActive = true;
    
    // Thread-safe route registration
    {
        FScopeLock Lock(&RouteDataMutex);
        
        // Check faction route limits
        TArray<FName>& FactionRoutes = FactionRouteCache.FindOrAdd(Parameters.RequestingFactionId);
        if (FactionRoutes.Num() >= MaxRoutesPerFaction)
        {
            UE_LOG(LogTemp, Warning, TEXT("Faction %d at route limit (%d)"), 
                   Parameters.RequestingFactionId, MaxRoutesPerFaction);
            OnRouteGenerated.Broadcast(NAME_None, false);
            return;
        }
        
        // Register route
        RegisteredRoutes.Add(NewRoute.RouteId, NewRoute);
        RouteHashToIdCache.Add(RouteHash, NewRoute.RouteId);
        FactionRoutes.Add(NewRoute.RouteId);
    }
    
    UE_LOG(LogTemp, Log, TEXT("Generated route %s: Security %.2f, Profit %.2f, Distance %.0f"),
           *NewRoute.RouteId.ToString(), NewRoute.SecurityRating, NewRoute.ProfitabilityScore, NewRoute.TotalDistance);
    
    OnRouteGenerated.Broadcast(NewRoute.RouteId, true);
}

void UTGConvoyEconomySubsystem::RegenerateAllFactionRoutes(int32 FactionId)
{
    if (!TerritorialManager)
    {
        return;
    }
    
    // Get all territories controlled by faction
    TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();
    TArray<int32> ControlledTerritories;
    
    for (const FTGTerritoryData& Territory : AllTerritories)
    {
        if (Territory.CurrentControllerFactionId == FactionId)
        {
            ControlledTerritories.Add(Territory.TerritoryId);
        }
    }
    
    // Clear existing routes for faction
    InvalidateRouteCache(FactionId);
    
    // Generate routes between all controlled territories
    int32 RoutesGenerated = 0;
    for (int32 i = 0; i < ControlledTerritories.Num() && RoutesGenerated < RouteGenerationBatchSize; i++)
    {
        for (int32 j = i + 1; j < ControlledTerritories.Num() && RoutesGenerated < RouteGenerationBatchSize; j++)
        {
            FRouteGenerationParameters Params;
            Params.RequestingFactionId = FactionId;
            Params.SourceTerritoryId = ControlledTerritories[i];
            Params.DestinationTerritoryId = ControlledTerritories[j];
            Params.MinSecurityThreshold = MinRouteSecurityThreshold;
            Params.bRequireDirectControl = false;
            
            GenerateRoutesBetweenTerritories(Params);
            RoutesGenerated++;
        }
    }
    
    // Update faction route statistics
    float TotalProfitability = GetFactionTotalProfitability(FactionId);
    int32 ActiveRouteCount = GetActiveRouteCount(FactionId);
    
    OnRoutesUpdated.Broadcast(FactionId, ActiveRouteCount, TotalProfitability);
    
    UE_LOG(LogTemp, Log, TEXT("Regenerated %d routes for faction %d (Total Active: %d, Profit: %.2f)"),
           RoutesGenerated, FactionId, ActiveRouteCount, TotalProfitability);
}

void UTGConvoyEconomySubsystem::InvalidateRoutesInTerritory(int32 TerritoryId)
{
    TArray<FName> RoutesToInvalidate;
    
    {
        FScopeLock Lock(&RouteDataMutex);
        
        // Find all routes passing through this territory
        for (auto& RouteEntry : RegisteredRoutes)
        {
            FConvoyRoute& Route = RouteEntry.Value;
            if (Route.TerritorialPath.Contains(TerritoryId) && Route.bIsActive)
            {
                RoutesToInvalidate.Add(Route.RouteId);
            }
        }
        
        // Invalidate routes
        for (const FName& RouteId : RoutesToInvalidate)
        {
            if (FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))
            {
                Route->bIsActive = false;
                Route->LastValidated = FDateTime::Now();
                
                // Remove from caches
                RouteHashToIdCache.Remove(Route->RouteHash);
                
                // Remove from faction cache
                if (TArray<FName>* FactionRoutes = FactionRouteCache.Find(Route->ControllingFactionId))
                {
                    FactionRoutes->Remove(RouteId);
                }
            }
        }
    }
    
    // Broadcast invalidation events
    for (const FName& RouteId : RoutesToInvalidate)
    {
        OnRouteInvalidated.Broadcast(RouteId, FString::Printf(TEXT("Territory %d control changed"), TerritoryId));
    }
    
    UE_LOG(LogTemp, Log, TEXT("Invalidated %d routes in territory %d"), RoutesToInvalidate.Num(), TerritoryId);
}

// Route Query Functions
TArray<FConvoyRoute> UTGConvoyEconomySubsystem::GetActiveRoutes() const
{
    FScopeLock Lock(&RouteDataMutex);
    
    TArray<FConvoyRoute> ActiveRoutes;
    for (const auto& RouteEntry : RegisteredRoutes)
    {
        if (RouteEntry.Value.bIsActive)
        {
            ActiveRoutes.Add(RouteEntry.Value);
        }
    }
    
    return ActiveRoutes;
}

float UTGConvoyEconomySubsystem::GetFactionTotalProfitability(int32 FactionId) const
{
    FScopeLock Lock(&RouteDataMutex);
    
    float TotalProfitability = 0.0f;
    
    if (const TArray<FName>* FactionRoutes = FactionRouteCache.Find(FactionId))
    {
        for (const FName& RouteId : *FactionRoutes)
        {
            if (const FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))
            {
                if (Route->bIsActive)
                {
                    TotalProfitability += Route->ProfitabilityScore;
                }
            }
        }
    }
    
    return TotalProfitability;
}

int32 UTGConvoyEconomySubsystem::GetActiveRouteCount(int32 FactionId) const
{
    FScopeLock Lock(&RouteDataMutex);
    
    int32 ActiveCount = 0;
    
    if (const TArray<FName>* FactionRoutes = FactionRouteCache.Find(FactionId))
    {
        for (const FName& RouteId : *FactionRoutes)
        {
            if (const FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))
            {
                if (Route->bIsActive)
                {
                    ActiveCount++;
                }
            }
        }
    }
    
    return ActiveCount;
}

// Performance-Critical Route Calculation Functions
void UTGConvoyEconomySubsystem::InitializeTerritorialConnections()
{
    if (!TerritorialManager)
    {
        return;
    }
    
    TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();
    
    // Clear existing connections
    TerritorialConnections.Empty();
    
    // Calculate connections between all territories (adjacency matrix approach)
    for (int32 i = 0; i < AllTerritories.Num(); i++)
    {
        const FTGTerritoryData& TerritoryA = AllTerritories[i];
        TMap<int32, FTerritorialConnection>& ConnectionsFromA = TerritorialConnections.FindOrAdd(TerritoryA.TerritoryId);
        
        for (int32 j = i + 1; j < AllTerritories.Num(); j++)
        {
            const FTGTerritoryData& TerritoryB = AllTerritories[j];
            
            // Calculate distance between territory centers
            float Distance = FVector2D::Distance(TerritoryA.Bounds.CenterPoint, TerritoryB.Bounds.CenterPoint);
            
            // Check if territories are adjacent (overlapping influence radius)
            float MaxConnectionDistance = FMath::Max(TerritoryA.Bounds.InfluenceRadius, TerritoryB.Bounds.InfluenceRadius) * 1.5f;
            bool bDirectConnection = Distance <= MaxConnectionDistance;
            
            // Create bidirectional connections
            FTerritorialConnection ConnectionAB;
            ConnectionAB.FromTerritoryId = TerritoryA.TerritoryId;
            ConnectionAB.ToTerritoryId = TerritoryB.TerritoryId;
            ConnectionAB.Distance = Distance;
            ConnectionAB.bDirectConnection = bDirectConnection;
            ConnectionAB.SecurityLevel = 0.5f; // Default security, updated dynamically
            
            FTerritorialConnection ConnectionBA;
            ConnectionBA.FromTerritoryId = TerritoryB.TerritoryId;
            ConnectionBA.ToTerritoryId = TerritoryA.TerritoryId;
            ConnectionBA.Distance = Distance;
            ConnectionBA.bDirectConnection = bDirectConnection;
            ConnectionBA.SecurityLevel = 0.5f;
            
            ConnectionsFromA.Add(TerritoryB.TerritoryId, ConnectionAB);
            TerritorialConnections.FindOrAdd(TerritoryB.TerritoryId).Add(TerritoryA.TerritoryId, ConnectionBA);
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("Initialized territorial connections: %d territories, %d total connections"),
           AllTerritories.Num(), TerritorialConnections.Num());
}

void UTGConvoyEconomySubsystem::UpdateTerritorialConnections()
{
    if (!TerritorialManager)
    {
        return;
    }
    
    // Update security levels for all connections based on current territorial control
    for (auto& TerritoryConnectionsEntry : TerritorialConnections)
    {
        int32 FromTerritoryId = TerritoryConnectionsEntry.Key;
        int32 FromController = TerritorialManager->GetControllingFaction(FromTerritoryId);
        bool bFromContested = TerritorialManager->IsTerritoryContested(FromTerritoryId);
        
        for (auto& ConnectionEntry : TerritoryConnectionsEntry.Value)
        {
            int32 ToTerritoryId = ConnectionEntry.Key;
            FTerritorialConnection& Connection = ConnectionEntry.Value;
            
            int32 ToController = TerritorialManager->GetControllingFaction(ToTerritoryId);
            bool bToContested = TerritorialManager->IsTerritoryContested(ToTerritoryId);
            
            // Calculate security based on territorial control
            float SecurityLevel = 1.0f;
            
            // Reduce security for contested territories
            if (bFromContested || bToContested)
            {
                SecurityLevel *= 0.3f;
            }
            
            // Reduce security for connections between different factions
            if (FromController != ToController && FromController != 0 && ToController != 0)
            {
                SecurityLevel *= 0.1f; // Very dangerous to cross faction lines
            }
            
            // Bonus security for same-faction controlled territories
            if (FromController == ToController && FromController != 0)
            {
                SecurityLevel *= 1.2f;
            }
            
            Connection.SecurityLevel = FMath::Clamp(SecurityLevel, 0.0f, 1.0f);
        }
    }
}

void UTGConvoyEconomySubsystem::ProcessRouteUpdates()
{
    float CurrentTime = GetWorld()->GetTimeSeconds();
    
    // Throttle updates to maintain performance
    if (CurrentTime - LastRouteUpdate < RouteUpdateFrequency)
    {
        return;
    }
    
    LastRouteUpdate = CurrentTime;
    
    // Update territorial connections
    UpdateTerritorialConnections();
    
    // Clean up inactive routes
    CleanupInactiveRoutes();
    
    // Validate active routes and update metrics
    {
        FScopeLock Lock(&RouteDataMutex);
        TArray<FName> RoutesToRevalidate;
        
        for (auto& RouteEntry : RegisteredRoutes)
        {
            FConvoyRoute& Route = RouteEntry.Value;
            if (Route.bIsActive)
            {
                // Check if route needs revalidation (every 30 seconds)
                FTimespan TimeSinceValidation = FDateTime::Now() - Route.LastValidated;
                if (TimeSinceValidation.GetTotalSeconds() > 30.0)
                {
                    RoutesToRevalidate.Add(Route.RouteId);
                }
            }
        }
        
        // Revalidate routes that need it
        for (const FName& RouteId : RoutesToRevalidate)
        {
            if (FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))
            {
                float NewSecurityRating = CalculateRouteSecurityRating(Route->TerritorialPath);
                
                // If security dropped too low, invalidate route
                if (NewSecurityRating < MinRouteSecurityThreshold)
                {
                    Route->bIsActive = false;
                    OnRouteInvalidated.Broadcast(RouteId, TEXT("Security threshold breach"));
                }
                else
                {
                    Route->SecurityRating = NewSecurityRating;
                    Route->ProfitabilityScore = CalculateRouteProfitability(*Route);
                    Route->LastValidated = FDateTime::Now();
                }
            }
        }
    }
}

// A* Pathfinding Implementation for Territorial Routes
TArray<int32> UTGConvoyEconomySubsystem::FindOptimalPath(int32 SourceTerritoryId, int32 DestinationTerritoryId, int32 FactionId, int32 MaxHops) const
{
    if (SourceTerritoryId == DestinationTerritoryId)
    {
        return {SourceTerritoryId};
    }
    
    // A* pathfinding with territorial considerations
    struct FPathNode
    {
        int32 TerritoryId;
        float GScore; // Cost from start
        float FScore; // Total estimated cost
        int32 ParentId;
        int32 Depth;
        
        FPathNode(int32 InTerritoryId, float InGScore, float InFScore, int32 InParentId, int32 InDepth)
            : TerritoryId(InTerritoryId), GScore(InGScore), FScore(InFScore), ParentId(InParentId), Depth(InDepth) {}
    };
    
    TArray<FPathNode> OpenSet;
    TSet<int32> ClosedSet;
    TMap<int32, FPathNode> NodeMap;
    
    // Get destination territory for heuristic calculation
    FTGTerritoryData DestinationData = TerritorialManager->GetTerritoryData(DestinationTerritoryId);
    
    // Initialize with source territory
    FTGTerritoryData SourceData = TerritorialManager->GetTerritoryData(SourceTerritoryId);
    float HeuristicCost = FVector2D::Distance(SourceData.Bounds.CenterPoint, DestinationData.Bounds.CenterPoint);
    
    FPathNode StartNode(SourceTerritoryId, 0.0f, HeuristicCost, -1, 0);
    OpenSet.Add(StartNode);
    NodeMap.Add(SourceTerritoryId, StartNode);
    
    while (OpenSet.Num() > 0)
    {
        // Find node with lowest F score
        int32 CurrentIndex = 0;
        for (int32 i = 1; i < OpenSet.Num(); i++)
        {
            if (OpenSet[i].FScore < OpenSet[CurrentIndex].FScore)
            {
                CurrentIndex = i;
            }
        }
        
        FPathNode CurrentNode = OpenSet[CurrentIndex];
        OpenSet.RemoveAt(CurrentIndex);
        ClosedSet.Add(CurrentNode.TerritoryId);
        
        // Check if we reached destination
        if (CurrentNode.TerritoryId == DestinationTerritoryId)
        {
            // Reconstruct path
            TArray<int32> Path;
            int32 PathNode = DestinationTerritoryId;
            
            while (PathNode != -1)
            {
                Path.Insert(PathNode, 0);
                PathNode = NodeMap[PathNode].ParentId;
            }
            
            return Path;
        }
        
        // Don't exceed max hops
        if (CurrentNode.Depth >= MaxHops)
        {
            continue;
        }
        
        // Explore neighbors
        if (const TMap<int32, FTerritorialConnection>* Connections = TerritorialConnections.Find(CurrentNode.TerritoryId))
        {
            for (const auto& ConnectionEntry : *Connections)
            {
                int32 NeighborId = ConnectionEntry.Key;
                const FTerritorialConnection& Connection = ConnectionEntry.Value;
                
                if (ClosedSet.Contains(NeighborId))
                {
                    continue;
                }
                
                // Calculate movement cost with territorial considerations
                float MovementCost = Connection.Distance;
                
                // Apply faction-specific modifiers
                int32 NeighborController = TerritorialManager->GetControllingFaction(NeighborId);
                if (NeighborController != FactionId && NeighborController != 0)
                {
                    MovementCost *= 3.0f; // High cost for enemy territory
                }
                
                // Apply security cost
                MovementCost *= (2.0f - Connection.SecurityLevel); // Lower security = higher cost
                
                float TentativeGScore = CurrentNode.GScore + MovementCost;
                
                // Calculate heuristic for neighbor
                FTGTerritoryData NeighborData = TerritorialManager->GetTerritoryData(NeighborId);
                float NeighborHeuristic = FVector2D::Distance(NeighborData.Bounds.CenterPoint, DestinationData.Bounds.CenterPoint);
                float TentativeFScore = TentativeGScore + NeighborHeuristic;
                
                // Check if this is a better path to neighbor
                bool bBetterPath = true;
                if (FPathNode* ExistingNode = NodeMap.Find(NeighborId))
                {
                    if (TentativeGScore >= ExistingNode->GScore)
                    {
                        bBetterPath = false;
                    }
                }
                
                if (bBetterPath)
                {
                    FPathNode NeighborNode(NeighborId, TentativeGScore, TentativeFScore, CurrentNode.TerritoryId, CurrentNode.Depth + 1);
                    NodeMap.Add(NeighborId, NeighborNode);
                    
                    // Add to open set if not already there
                    bool bFoundInOpenSet = false;
                    for (int32 i = 0; i < OpenSet.Num(); i++)
                    {
                        if (OpenSet[i].TerritoryId == NeighborId)
                        {
                            OpenSet[i] = NeighborNode;
                            bFoundInOpenSet = true;
                            break;
                        }\n                    }\n                    \n                    if (!bFoundInOpenSet)\n                    {\n                        OpenSet.Add(NeighborNode);\n                    }\n                }\n            }\n        }\n    }\n    \n    return TArray<int32>(); // No path found\n}\n\nfloat UTGConvoyEconomySubsystem::CalculateRouteProfitability(const FConvoyRoute& Route) const\n{\n    if (!TerritorialManager || Route.TerritorialPath.Num() < 2)\n    {\n        return 0.0f;\n    }\n    \n    float BaseProfitability = 1.0f;\n    \n    // Calculate profitability based on route characteristics\n    float DistanceFactor = FMath::Clamp(10000.0f / FMath::Max(Route.TotalDistance, 1.0f), 0.1f, 2.0f);\n    float SecurityFactor = Route.SecurityRating * 2.0f;\n    \n    // Strategic value bonus for connecting high-value territories\n    float StrategicValueBonus = 0.0f;\n    for (int32 TerritoryId : Route.TerritorialPath)\n    {\n        FTGTerritoryData TerritoryData = TerritorialManager->GetTerritoryData(TerritoryId);\n        StrategicValueBonus += TerritoryData.StrategicValue * TerritoryData.ResourceMultiplier;\n    }\n    StrategicValueBonus /= Route.TerritorialPath.Num(); // Average strategic value\n    \n    float TotalProfitability = BaseProfitability * DistanceFactor * SecurityFactor * (1.0f + StrategicValueBonus * 0.1f);\n    \n    return FMath::Clamp(TotalProfitability, 0.0f, 10.0f);\n}\n\nfloat UTGConvoyEconomySubsystem::CalculateRouteSecurityRating(const TArray<int32>& TerritorialPath) const\n{\n    if (TerritorialPath.Num() < 2)\n    {\n        return 0.0f;\n    }\n    \n    float TotalSecurity = 0.0f;\n    int32 ConnectionCount = 0;\n    \n    // Calculate average security of all connections in path\n    for (int32 i = 0; i < TerritorialPath.Num() - 1; i++)\n    {\n        int32 FromTerritoryId = TerritorialPath[i];\n        int32 ToTerritoryId = TerritorialPath[i + 1];\n        \n        if (const TMap<int32, FTerritorialConnection>* Connections = TerritorialConnections.Find(FromTerritoryId))\n        {\n            if (const FTerritorialConnection* Connection = Connections->Find(ToTerritoryId))\n            {\n                TotalSecurity += Connection->SecurityLevel;\n                ConnectionCount++;\n            }\n        }\n    }\n    \n    return ConnectionCount > 0 ? (TotalSecurity / ConnectionCount) : 0.0f;\n}\n\nuint32 UTGConvoyEconomySubsystem::GenerateRouteHash(const FRouteGenerationParameters& Parameters) const\n{\n    // Create deterministic hash for route parameters\n    uint32 Hash = 0;\n    Hash = HashCombine(Hash, GetTypeHash(Parameters.RequestingFactionId));\n    Hash = HashCombine(Hash, GetTypeHash(Parameters.SourceTerritoryId));\n    Hash = HashCombine(Hash, GetTypeHash(Parameters.DestinationTerritoryId));\n    Hash = HashCombine(Hash, GetTypeHash(Parameters.bRequireDirectControl));\n    \n    return Hash;\n}\n\nFName UTGConvoyEconomySubsystem::GenerateUniqueRouteId(int32 FactionId, int32 SourceId, int32 DestinationId) const\n{\n    static int32 RouteCounter = 0;\n    RouteCounter++;\n    \n    FString RouteIdString = FString::Printf(TEXT(\"R_%d_%d_%d_%d\"), \n                                          FactionId, SourceId, DestinationId, RouteCounter);\n    return FName(*RouteIdString);\n}\n\n// Territorial Event Handlers\nvoid UTGConvoyEconomySubsystem::OnTerritoryControlChanged(int32 TerritoryId, int32 OldControllerFactionId, int32 NewControllerFactionId)\n{\n    UE_LOG(LogTemp, Log, TEXT(\"Territory %d control changed: %d -> %d\"), TerritoryId, OldControllerFactionId, NewControllerFactionId);\n    \n    // Invalidate routes passing through this territory\n    InvalidateRoutesInTerritory(TerritoryId);\n    \n    // Regenerate routes for both old and new controlling factions\n    if (OldControllerFactionId != 0)\n    {\n        RegenerateAllFactionRoutes(OldControllerFactionId);\n    }\n    \n    if (NewControllerFactionId != 0)\n    {\n        RegenerateAllFactionRoutes(NewControllerFactionId);\n    }\n    \n    // Update territorial connections to reflect new control state\n    UpdateTerritorialConnections();\n}\n\nvoid UTGConvoyEconomySubsystem::OnTerritoryContested(int32 TerritoryId, bool bContested)\n{\n    UE_LOG(LogTemp, Log, TEXT(\"Territory %d contested status changed: %s\"), TerritoryId, bContested ? TEXT(\"Contested\") : TEXT(\"Secure\"));\n    \n    // Update territorial connections (contested territories have lower security)\n    UpdateTerritorialConnections();\n    \n    // If territory is now contested, reduce security of routes passing through\n    if (bContested)\n    {\n        FScopeLock Lock(&RouteDataMutex);\n        \n        for (auto& RouteEntry : RegisteredRoutes)\n        {\n            FConvoyRoute& Route = RouteEntry.Value;\n            if (Route.bIsActive && Route.TerritorialPath.Contains(TerritoryId))\n            {\n                // Recalculate security rating\n                Route.SecurityRating = CalculateRouteSecurityRating(Route.TerritorialPath);\n                Route.LastValidated = FDateTime::Now();\n                \n                // If security dropped too low, invalidate route\n                if (Route.SecurityRating < MinRouteSecurityThreshold)\n                {\n                    Route.bIsActive = false;\n                    OnRouteInvalidated.Broadcast(Route.RouteId, TEXT(\"Territory contested - security breach\"));\n                }\n            }\n        }\n    }\n}\n\n// Cache Management\nvoid UTGConvoyEconomySubsystem::InvalidateRouteCache(int32 FactionId)\n{\n    FScopeLock Lock(&RouteDataMutex);\n    \n    if (TArray<FName>* FactionRoutes = FactionRouteCache.Find(FactionId))\n    {\n        // Remove all faction routes from main registry\n        for (const FName& RouteId : *FactionRoutes)\n        {\n            if (FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))\n            {\n                RouteHashToIdCache.Remove(Route->RouteHash);\n                RegisteredRoutes.Remove(RouteId);\n            }\n        }\n        \n        // Clear faction cache\n        FactionRoutes->Empty();\n    }\n}\n\nvoid UTGConvoyEconomySubsystem::CleanupInactiveRoutes()\n{\n    FScopeLock Lock(&RouteDataMutex);\n    \n    TArray<FName> RoutesToRemove;\n    FDateTime CurrentTime = FDateTime::Now();\n    \n    // Find routes that have been inactive for more than 5 minutes\n    for (const auto& RouteEntry : RegisteredRoutes)\n    {\n        const FConvoyRoute& Route = RouteEntry.Value;\n        if (!Route.bIsActive)\n        {\n            FTimespan InactiveTime = CurrentTime - Route.LastValidated;\n            if (InactiveTime.GetTotalMinutes() > 5.0)\n            {\n                RoutesToRemove.Add(Route.RouteId);\n            }\n        }\n    }\n    \n    // Remove old inactive routes\n    for (const FName& RouteId : RoutesToRemove)\n    {\n        if (const FConvoyRoute* Route = RegisteredRoutes.Find(RouteId))\n        {\n            // Remove from hash cache\n            RouteHashToIdCache.Remove(Route->RouteHash);\n            \n            // Remove from faction cache\n            if (TArray<FName>* FactionRoutes = FactionRouteCache.Find(Route->ControllingFactionId))\n            {\n                FactionRoutes->Remove(RouteId);\n            }\n            \n            // Remove from main registry\n            RegisteredRoutes.Remove(RouteId);\n        }\n    }\n    \n    if (RoutesToRemove.Num() > 0)\n    {\n        UE_LOG(LogTemp, Log, TEXT(\"Cleaned up %d inactive routes\"), RoutesToRemove.Num());\n    }\n}
