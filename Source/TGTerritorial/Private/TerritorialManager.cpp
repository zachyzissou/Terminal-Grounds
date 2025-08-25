// Copyright Terminal Grounds. All Rights Reserved.

#include "TerritorialManager.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "TimerManager.h"

UTerritorialManager::UTerritorialManager()
{
    bSystemInitialized = false;
    bWebSocketConnected = false;
    WebSocketConnection = nullptr;
    DatabaseConnection = nullptr;
    LastCacheUpdate = FDateTime::MinValue();
}

bool UTerritorialManager::UpdateTerritorialInfluence(int32 TerritoryID, ETerritoryType TerritoryType, int32 FactionID, int32 InfluenceChange, const FString& Cause)
{
    if (!bSystemInitialized)
    {
        UE_LOG(LogTemp, Warning, TEXT("TerritorialManager not initialized - cannot update influence"));
        return false;
    }

    // Validate input parameters
    if (TerritoryID <= 0 || FactionID <= 0 || FactionID > 7)
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid parameters for territorial influence update: Territory=%d, Faction=%d"), TerritoryID, FactionID);
        return false;
    }

    // For Phase 1 implementation, use simplified in-memory calculation
    // This will be replaced with database calls once CTO completes schema
    FString StateKey = FString::Printf(TEXT("%s_%d"), 
        TerritoryType == ETerritoryType::Region ? TEXT("region") :
        TerritoryType == ETerritoryType::District ? TEXT("district") : TEXT("control_point"),
        TerritoryID);

    // Get or create territorial state
    FTerritorialState* State = CachedTerritorialStates.Find(StateKey);
    if (!State)
    {
        FTerritorialState NewState;
        NewState.TerritoryID = TerritoryID;
        NewState.TerritoryType = TerritoryType;
        NewState.LastUpdated = FDateTime::Now();
        CachedTerritorialStates.Add(StateKey, NewState);
        State = CachedTerritorialStates.Find(StateKey);
    }

    // Calculate new influence with bounds checking
    int32 CurrentInfluence = State->FactionInfluences.FindRef(FactionID);
    int32 NewInfluence = FMath::Clamp(CurrentInfluence + InfluenceChange, 0, 100);
    
    // Update faction influences
    State->FactionInfluences.Add(FactionID, NewInfluence);
    State->LastUpdated = FDateTime::Now();
    
    // Recalculate dominant faction and contested status
    State->DominantFaction = FindDominantFaction(State->FactionInfluences);
    State->bIsContested = DetermineIfContested(State->FactionInfluences);

    // Create update record
    FTerritorialUpdate Update;
    Update.TerritoryID = TerritoryID;
    Update.TerritoryType = TerritoryType;
    Update.FactionID = FactionID;
    Update.InfluenceChange = InfluenceChange;
    Update.ChangeCause = Cause;
    Update.NewInfluenceValue = NewInfluence;
    Update.bControlChanged = (State->DominantFaction != FindDominantFaction(State->FactionInfluences));
    Update.Timestamp = FDateTime::Now();

    // Fire events for Blueprint/game code consumption
    if (Update.bControlChanged)
    {
        int32 OldDominant = State->DominantFaction;
        OnTerritorialControlChanged.Broadcast(TerritoryID, TerritoryType, OldDominant, State->DominantFaction);
    }

    if (State->bIsContested)
    {
        TArray<int32> ContestingFactions;
        for (const auto& Influence : State->FactionInfluences)
        {
            if (Influence.Value >= 40) // Contestation threshold
            {
                ContestingFactions.Add(Influence.Key);
            }
        }
        OnTerritoryContested.Broadcast(TerritoryID, TerritoryType, ContestingFactions);
    }

    UE_LOG(LogTemp, Log, TEXT("Territorial influence updated: %s %d, Faction %d: %d -> %d (%s)"), 
        *StateKey, TerritoryID, FactionID, CurrentInfluence, NewInfluence, *Cause);

    return true;
}

FTerritorialState UTerritorialManager::GetTerritorialState(int32 TerritoryID, ETerritoryType TerritoryType)
{
    FString StateKey = FString::Printf(TEXT("%s_%d"), 
        TerritoryType == ETerritoryType::Region ? TEXT("region") :
        TerritoryType == ETerritoryType::District ? TEXT("district") : TEXT("control_point"),
        TerritoryID);

    FTerritorialState* State = CachedTerritorialStates.Find(StateKey);
    if (State)
    {
        return *State;
    }

    // Return empty state if not found
    FTerritorialState EmptyState;
    EmptyState.TerritoryID = TerritoryID;
    EmptyState.TerritoryType = TerritoryType;
    return EmptyState;
}

TArray<FTerritorialUpdate> UTerritorialManager::GetRecentTerritorialUpdates()
{
    // Phase 1 implementation - return empty array
    // Will be implemented with database integration
    return TArray<FTerritorialUpdate>();
}

int32 UTerritorialManager::GetFactionInfluence(int32 TerritoryID, ETerritoryType TerritoryType, int32 FactionID)
{
    FTerritorialState State = GetTerritorialState(TerritoryID, TerritoryType);
    return State.FactionInfluences.FindRef(FactionID);
}

int32 UTerritorialManager::GetDominantFaction(int32 TerritoryID, ETerritoryType TerritoryType)
{
    FTerritorialState State = GetTerritorialState(TerritoryID, TerritoryType);
    return State.DominantFaction;
}

bool UTerritorialManager::IsTerritoryContested(int32 TerritoryID, ETerritoryType TerritoryType)
{
    FTerritorialState State = GetTerritorialState(TerritoryID, TerritoryType);
    return State.bIsContested;
}

TArray<int32> UTerritorialManager::GetDistrictsInRegion(int32 RegionID)
{
    // Phase 1 implementation - return hardcoded structure
    // Will be replaced with database queries
    TArray<int32> Districts;
    
    switch (RegionID)
    {
        case 1: // Tech Wastes
            Districts = {1, 2, 3};
            break;
        case 2: // Metro Corridors  
            Districts = {4, 5, 6};
            break;
        case 3: // Corporate Zones
            Districts = {7, 8, 9};
            break;
        default:
            // Generic districts for other regions
            Districts.Add(RegionID * 10);
            Districts.Add(RegionID * 10 + 1);
            break;
    }
    
    return Districts;
}

TArray<int32> UTerritorialManager::GetControlPointsInDistrict(int32 DistrictID)
{
    // Phase 1 implementation - return hardcoded structure
    TArray<int32> ControlPoints;
    
    // Each district has 2-3 control points
    ControlPoints.Add(DistrictID * 100);
    ControlPoints.Add(DistrictID * 100 + 1);
    
    if (DistrictID <= 9) // Strategic districts get additional control point
    {
        ControlPoints.Add(DistrictID * 100 + 2);
    }
    
    return ControlPoints;
}

FTerritorialInfo UTerritorialManager::GetTerritoryInfo(int32 TerritoryID, ETerritoryType TerritoryType)
{
    // Phase 1 implementation - return basic info
    FTerritorialInfo Info;
    Info.TerritoryID = TerritoryID;
    Info.TerritoryType = TerritoryType;
    Info.Name = FString::Printf(TEXT("Territory_%d"), TerritoryID);
    Info.Description = FString::Printf(TEXT("Territorial unit %d"), TerritoryID);
    
    return Info;
}

void UTerritorialManager::InitializeTerritorialSystem()
{
    if (bSystemInitialized)
    {
        UE_LOG(LogTemp, Warning, TEXT("TerritorialManager already initialized"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Initializing Terminal Grounds Territorial Control System"));

    // Initialize basic territorial structure for Phase 1
    InitializeBasicTerritorialStructure();

    // TODO: Initialize WebSocket connection when ready
    // TODO: Initialize database connection when ready

    bSystemInitialized = true;
    UE_LOG(LogTemp, Log, TEXT("TerritorialManager initialization complete"));
}

void UTerritorialManager::ShutdownTerritorialSystem()
{
    if (!bSystemInitialized)
    {
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Shutting down Territorial Control System"));

    // Clean up connections
    if (WebSocketConnection)
    {
        // TODO: Close WebSocket connection
        WebSocketConnection = nullptr;
        bWebSocketConnected = false;
    }

    if (DatabaseConnection)
    {
        // TODO: Close database connection
        DatabaseConnection = nullptr;
    }

    // Clear cached data
    CachedTerritorialStates.Empty();

    bSystemInitialized = false;
    UE_LOG(LogTemp, Log, TEXT("TerritorialManager shutdown complete"));
}

bool UTerritorialManager::IsSystemOnline()
{
    return bSystemInitialized;
}

void UTerritorialManager::InitializeBasicTerritorialStructure()
{
    // Create initial territorial states for Phase 1 testing
    struct RegionData
    {
        int32 RegionID;
        FString Name;
        TArray<int32> InitialInfluences; // Index = FactionID-1, Value = Influence
    };

    TArray<RegionData> Regions = {
        {1, TEXT("Tech Wastes"), {25, 30, 20, 15, 25, 10, 15}},
        {2, TEXT("Metro Corridors"), {20, 35, 25, 20, 10, 15, 20}},
        {3, TEXT("Corporate Zones"), {40, 15, 10, 25, 15, 20, 35}},
        {4, TEXT("Residential Districts"), {15, 25, 20, 35, 15, 25, 10}},
        {5, TEXT("Military Compounds"), {30, 20, 15, 40, 10, 15, 20}},
        {6, TEXT("Research Facilities"), {25, 20, 15, 25, 20, 35, 25}},
        {7, TEXT("Trade Routes"), {20, 25, 20, 20, 30, 20, 30}},
        {8, TEXT("Neutral Ground"), {15, 15, 15, 15, 15, 15, 15}}
    };

    for (const RegionData& Region : Regions)
    {
        FTerritorialState State;
        State.TerritoryID = Region.RegionID;
        State.TerritoryType = ETerritoryType::Region;
        State.LastUpdated = FDateTime::Now();

        // Set faction influences
        for (int32 FactionIndex = 0; FactionIndex < Region.InitialInfluences.Num() && FactionIndex < 7; FactionIndex++)
        {
            int32 FactionID = FactionIndex + 1;
            int32 Influence = Region.InitialInfluences[FactionIndex];
            State.FactionInfluences.Add(FactionID, Influence);
        }

        State.DominantFaction = FindDominantFaction(State.FactionInfluences);
        State.bIsContested = DetermineIfContested(State.FactionInfluences);

        FString StateKey = FString::Printf(TEXT("region_%d"), Region.RegionID);
        CachedTerritorialStates.Add(StateKey, State);

        UE_LOG(LogTemp, Log, TEXT("Initialized region %d (%s) - Dominant: Faction %d, Contested: %s"),
            Region.RegionID, *Region.Name, State.DominantFaction, State.bIsContested ? TEXT("Yes") : TEXT("No"));
    }
}

int32 UTerritorialManager::FindDominantFaction(const TMap<int32, int32>& FactionInfluences)
{
    int32 DominantFaction = 0;
    int32 HighestInfluence = 0;

    for (const auto& Influence : FactionInfluences)
    {
        if (Influence.Value > HighestInfluence)
        {
            HighestInfluence = Influence.Value;
            DominantFaction = Influence.Key;
        }
    }

    return DominantFaction;
}

bool UTerritorialManager::DetermineIfContested(const TMap<int32, int32>& FactionInfluences)
{
    int32 ContestingFactions = 0;
    for (const auto& Influence : FactionInfluences)
    {
        if (Influence.Value >= 40) // Contestation threshold
        {
            ContestingFactions++;
        }
    }

    return ContestingFactions > 1;
}

// Subsystem implementation
void UTerritorialSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    TerritorialManager = NewObject<UTerritorialManager>(this);
    if (TerritorialManager)
    {
        TerritorialManager->InitializeTerritorialSystem();
        UE_LOG(LogTemp, Log, TEXT("TerritorialSubsystem initialized successfully"));
    }
}

void UTerritorialSubsystem::Deinitialize()
{
    if (TerritorialManager)
    {
        TerritorialManager->ShutdownTerritorialSystem();
        TerritorialManager = nullptr;
    }
    
    Super::Deinitialize();
}

UTerritorialManager* UTerritorialSubsystem::GetTerritorialManager(const UObject* WorldContext)
{
    if (UWorld* World = GEngine->GetWorldFromContextObject(WorldContext, EGetWorldErrorMode::LogAndReturnNull))
    {
        if (UTerritorialSubsystem* Subsystem = World->GetSubsystem<UTerritorialSubsystem>())
        {
            return Subsystem->TerritorialManager;
        }
    }
    return nullptr;
}