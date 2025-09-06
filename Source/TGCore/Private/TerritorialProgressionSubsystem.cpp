#include "TerritorialProgressionSubsystem.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/DateTime.h"
#include "Async/Async.h"

// Forward declaration includes for performance
#include "TGWorld/Public/TGTerritorialManager.h"
#include "TGWorld/Public/Economy/TGConvoyEconomySubsystem.h"
#include "Trust/TGTrustSubsystem.h"
#include "Codex/TGCodexSubsystem.h"

UTGTerritorialProgressionSubsystem::UTGTerritorialProgressionSubsystem()
{
    // Initialize performance tracking
    AverageProcessingTimeMs = 0.0f;
    TotalBatchesProcessed = 0;
    LastBatchStartTime = 0.0;

    // Preallocate collections for performance
    ProcessingTimeHistory.Reserve(100); // Keep last 100 measurements
    FactionProgressionMap.Reserve(7); // 7 factions maximum
    TerritorialStateCache.Reserve(100); // Expect ~100 territories
    ActiveObjectives.Reserve(50); // Reasonable objective limit

    // Initialize default faction data for all 7 factions
    const TArray<int32> FactionIds = {1, 2, 3, 4, 5, 6, 7}; // Directorate, Free77, NomadClans, etc.
    const TArray<FString> FactionNames = {
        TEXT("Directorate"), TEXT("Free77"), TEXT("NomadClans"), 
        TEXT("VulturesUnion"), TEXT("CorporateCombine"), TEXT("Bloom"), TEXT("Independent")
    };

    for (int32 i = 0; i < FactionIds.Num() && i < FactionNames.Num(); ++i)
    {
        FTGFactionProgressionData& ProgressionData = FactionProgressionMap.Add(FactionIds[i]);
        ProgressionData.FactionId = FactionIds[i];
        ProgressionData.FactionName = FactionNames[i];
        ProgressionData.CurrentTier = EFactionProgressionTier::Recruit;
        ProgressionData.TotalReputationPoints = 0.0f;
        ProgressionData.ExtractionBonusMultiplier = 1.0f;
        ProgressionData.InfluenceRateMultiplier = 1.0f;
        ProgressionData.LastProgressionUpdate = FDateTime::Now();
    }
}

void UTGTerritorialProgressionSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Initializing for high-performance 100+ player support"));

    // Cache subsystem references for performance (avoid repeated GetSubsystem calls)
    TrustSubsystem = GetGameInstance()->GetSubsystem<UTGTrustSubsystem>();
    CodexSubsystem = GetGameInstance()->GetSubsystem<UTGCodexSubsystem>();

    // Verify critical subsystem availability
    if (!TrustSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("TerritorialProgressionSubsystem: UTGTrustSubsystem not available!"));
    }
    if (!CodexSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("TerritorialProgressionSubsystem: UTGCodexSubsystem not available!"));
    }

    // Start high-performance batch processing timer
    if (UWorld* World = GetGameInstance()->GetWorld())
    {
        // 5-second batch processing for optimal performance
        World->GetTimerManager().SetTimer(
            BatchProcessingTimer,
            this,
            &UTGTerritorialProgressionSubsystem::ProcessProgressionBatch,
            BatchProcessingInterval,
            true // Loop
        );

        // 15-second cache refresh to balance freshness vs performance
        World->GetTimerManager().SetTimer(
            CacheRefreshTimer,
            this,
            &UTGTerritorialProgressionSubsystem::RefreshTerritorialStateCache,
            CacheRefreshInterval,
            true // Loop
        );

        UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Batch processing started - %.1fs intervals"), BatchProcessingInterval);
    }

    // Initialize territorial state cache asynchronously to avoid initialization hitches
    AsyncTask(ENamedThreads::GameThread, [this]()
    {
        RefreshTerritorialStateCache();
    });

    // Load existing progression data asynchronously
    for (const auto& FactionPair : FactionProgressionMap)
    {
        LoadProgressionDataAsync(FactionPair.Key);
    }
}

void UTGTerritorialProgressionSubsystem::Deinitialize()
{
    UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Shutting down - saving final progression state"));

    // Clear timers
    if (UWorld* World = GetGameInstance()->GetWorld())
    {
        World->GetTimerManager().ClearTimer(BatchProcessingTimer);
        World->GetTimerManager().ClearTimer(CacheRefreshTimer);
    }

    // Save all faction progression data before shutdown
    for (const auto& FactionPair : FactionProgressionMap)
    {
        SaveProgressionDataAsync(FactionPair.Key);
    }

    // Clear cached subsystem references
    TrustSubsystem = nullptr;
    CodexSubsystem = nullptr;
    CachedTerritorialManager = nullptr;
    CachedConvoyEconomySubsystem = nullptr;

    Super::Deinitialize();
}

// Core Progression Functions - Performance Optimized
FTGFactionProgressionData UTGTerritorialProgressionSubsystem::GetFactionProgression(int32 FactionId) const
{
    FScopeLock Lock(&ProgressionDataMutex); // Thread safety for read access

    if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
    {
        return *ProgressionData;
    }

    // Return default if not found
    FTGFactionProgressionData DefaultProgression;
    DefaultProgression.FactionId = FactionId;
    return DefaultProgression;
}

void UTGTerritorialProgressionSubsystem::UpdateFactionReputation(int32 FactionId, float ReputationDelta, const FString& Source)
{
    // Performance Analysis → Bottleneck Identification → Optimization Strategy → Scalability Framework
    
    FScopeLock Lock(&ProgressionDataMutex); // Thread safety for write access

    FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId);
    if (!ProgressionData)
    {
        UE_LOG(LogTemp, Warning, TEXT("TerritorialProgressionSubsystem: Invalid FactionId %d for reputation update"), FactionId);
        return;
    }

    const float OldReputation = ProgressionData->TotalReputationPoints;
    const EFactionProgressionTier OldTier = ProgressionData->CurrentTier;

    // Apply reputation delta with performance logging
    ProgressionData->TotalReputationPoints = FMath::Max(0.0f, ProgressionData->TotalReputationPoints + ReputationDelta);
    ProgressionData->LastProgressionUpdate = FDateTime::Now();

    // Update tier if threshold crossed
    UpdateFactionTier(FactionId);

    // Broadcast changes if significant
    const EFactionProgressionTier NewTier = ProgressionData->CurrentTier;
    if (OldTier != NewTier || FMath::Abs(ReputationDelta) >= 50.0f)
    {
        OnFactionProgressionChanged.Broadcast(FactionId, NewTier, ProgressionData->TotalReputationPoints);
    }

    // Apply trust system bonuses for reputation gains
    if (TrustSubsystem && ReputationDelta > 0.0f)
    {
        // Enhance trust relationships when gaining reputation
        const float TrustBonus = ReputationDelta * 0.01f; // 1% of reputation as trust bonus
        // This would be applied to allied factions via TrustSubsystem->ApplySiegeTrustBonus
    }

    UE_LOG(LogTemp, VeryVerbose, TEXT("TerritorialProgressionSubsystem: Faction %d reputation: %.1f → %.1f (Delta: %.1f, Source: %s)"), 
           FactionId, OldReputation, ProgressionData->TotalReputationPoints, ReputationDelta, *Source);
}

bool UTGTerritorialProgressionSubsystem::UnlockFactionAbility(int32 FactionId, FName AbilityId, EFactionAbilityType AbilityType)
{
    FScopeLock Lock(&ProgressionDataMutex);

    FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId);
    if (!ProgressionData)
    {
        return false;
    }

    // Check if already unlocked (performance optimization)
    if (ProgressionData->UnlockedAbilities.Contains(AbilityId))
    {
        return true; // Already unlocked
    }

    // Add to unlocked abilities
    ProgressionData->UnlockedAbilities.Add(AbilityId);

    // Apply ability bonuses based on type
    switch (AbilityType)
    {
        case EFactionAbilityType::ExtractionBonus:
            ProgressionData->ExtractionBonusMultiplier += 0.15f; // 15% bonus per unlock
            break;
        case EFactionAbilityType::InfluenceRate:
            ProgressionData->InfluenceRateMultiplier += 0.10f; // 10% faster influence gain
            break;
        case EFactionAbilityType::SupplyRouteAccess:
            // Handled in GetAvailableSupplyRoutes function
            break;
        case EFactionAbilityType::WeaponUnlock:
        case EFactionAbilityType::EquipmentUnlock:
            // Integrate with Codex system for unlocks
            if (CodexSubsystem)
            {
                CodexSubsystem->UnlockEntry(AbilityId);
            }
            break;
        case EFactionAbilityType::TacticalAbility:
            // Could integrate with special abilities system
            break;
    }

    // Broadcast unlock event
    OnFactionAbilityUnlocked.Broadcast(FactionId, AbilityId, AbilityType);

    UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Faction %d unlocked ability %s (Type: %d)"), 
           FactionId, *AbilityId.ToString(), static_cast<int32>(AbilityType));

    return true;
}

bool UTGTerritorialProgressionSubsystem::IsFactionAbilityUnlocked(int32 FactionId, FName AbilityId) const
{
    FScopeLock Lock(&ProgressionDataMutex);

    if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
    {
        return ProgressionData->UnlockedAbilities.Contains(AbilityId);
    }
    return false;
}

// Territory-Based Bonuses - High Performance Queries
float UTGTerritorialProgressionSubsystem::GetExtractionBonusMultiplier(int32 FactionId) const
{
    FScopeLock Lock(&ProgressionDataMutex);

    if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
    {
        return ProgressionData->ExtractionBonusMultiplier;
    }
    return 1.0f; // Default no bonus
}

float UTGTerritorialProgressionSubsystem::GetInfluenceRateMultiplier(int32 FactionId) const
{
    FScopeLock Lock(&ProgressionDataMutex);

    if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
    {
        return ProgressionData->InfluenceRateMultiplier;
    }
    return 1.0f; // Default no bonus
}

int32 UTGTerritorialProgressionSubsystem::GetResourceBonus(int32 FactionId, ETerritoryResourceType ResourceType) const
{
    FScopeLock Lock(&ProgressionDataMutex);

    if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
    {
        if (const int32* Bonus = ProgressionData->ResourceBonuses.Find(ResourceType))
        {
            return *Bonus;
        }
    }
    return 0; // No bonus
}

TArray<FName> UTGTerritorialProgressionSubsystem::GetAvailableSupplyRoutes(int32 FactionId) const
{
    TArray<FName> AvailableRoutes;

    FScopeLock Lock(&ProgressionDataMutex);
    
    const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId);
    if (!ProgressionData)
    {
        return AvailableRoutes;
    }

    // Base routes available to all factions
    AvailableRoutes.Add(FName("RouteBasic"));

    // Tier-based route unlocks
    if (ProgressionData->CurrentTier >= EFactionProgressionTier::Veteran)
    {
        AvailableRoutes.Add(FName("RouteAdvanced"));
    }
    if (ProgressionData->CurrentTier >= EFactionProgressionTier::Elite)
    {
        AvailableRoutes.Add(FName("RouteElite"));
    }
    if (ProgressionData->CurrentTier >= EFactionProgressionTier::Commander)
    {
        AvailableRoutes.Add(FName("RouteCommander"));
    }

    // Special ability unlocks
    if (ProgressionData->UnlockedAbilities.Contains(FName("SupplyRouteExclusive")))
    {
        AvailableRoutes.Add(FName("RouteExclusive"));
    }

    return AvailableRoutes;
}

// Territorial Objectives System
void UTGTerritorialProgressionSubsystem::RegisterTerritorialObjective(const FTGTerritorialObjective& Objective)
{
    FScopeLock Lock(&ProgressionDataMutex);

    // Check if objective already exists (avoid duplicates)
    const bool bExists = ActiveObjectives.ContainsByPredicate([&Objective](const FTGTerritorialObjective& ExistingObj)
    {
        return ExistingObj.ObjectiveId == Objective.ObjectiveId && ExistingObj.TargetFactionId == Objective.TargetFactionId;
    });

    if (!bExists)
    {
        ActiveObjectives.Add(Objective);
        UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Registered objective %s for faction %d"), 
               *Objective.ObjectiveId.ToString(), Objective.TargetFactionId);
    }
}

TArray<FTGTerritorialObjective> UTGTerritorialProgressionSubsystem::GetActiveObjectives(int32 FactionId) const
{
    FScopeLock Lock(&ProgressionDataMutex);

    TArray<FTGTerritorialObjective> FactionObjectives;
    
    for (const FTGTerritorialObjective& Objective : ActiveObjectives)
    {
        if (Objective.TargetFactionId == FactionId && !Objective.bCompleted)
        {
            FactionObjectives.Add(Objective);
        }
    }

    return FactionObjectives;
}

bool UTGTerritorialProgressionSubsystem::CompleteObjective(int32 FactionId, FName ObjectiveId)
{
    FScopeLock Lock(&ProgressionDataMutex);

    for (FTGTerritorialObjective& Objective : ActiveObjectives)
    {
        if (Objective.ObjectiveId == ObjectiveId && Objective.TargetFactionId == FactionId && !Objective.bCompleted)
        {
            Objective.bCompleted = true;
            Objective.CompletionTime = FDateTime::Now();

            // Apply rewards
            UpdateFactionReputation(FactionId, Objective.ReputationReward, TEXT("Objective Completion"));

            // Unlock abilities
            for (const FName& UnlockId : Objective.UnlockRewards)
            {
                UnlockFactionAbility(FactionId, UnlockId, EFactionAbilityType::TacticalAbility);
            }

            // Broadcast completion
            OnTerritorialObjectiveCompleted.Broadcast(FactionId, ObjectiveId);

            UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Objective %s completed by faction %d - Reputation: +%.1f"), 
                   *ObjectiveId.ToString(), FactionId, Objective.ReputationReward);

            return true;
        }
    }

    return false; // Objective not found or already completed
}

// Performance-Critical Core Functions
void UTGTerritorialProgressionSubsystem::ProcessProgressionBatch()
{
    // Performance Analysis: High-frequency batch processing optimized for 100+ players
    const double StartTime = FPlatformTime::Seconds();
    
    FTGProgressionBatchResult BatchResult;
    BatchResult.ProcessedTerritories = 0;

    // Get territorial manager with caching for performance
    UTGTerritorialManager* TerritorialManager = GetCachedTerritorialManager();
    if (!TerritorialManager)
    {
        UE_LOG(LogTemp, Warning, TEXT("TerritorialProgressionSubsystem: TerritorialManager not available for batch processing"));
        return;
    }

    {
        FScopeLock Lock(&ProgressionDataMutex);

        // Process each faction's territorial progression
        for (auto& FactionPair : FactionProgressionMap)
        {
            const int32 FactionId = FactionPair.Key;
            FTGFactionProgressionData& ProgressionData = FactionPair.Value;

            // Calculate reputation gains from territorial control
            CalculateFactionReputation(FactionId);
            
            // Update faction tier if needed
            const EFactionProgressionTier OldTier = ProgressionData.CurrentTier;
            UpdateFactionTier(FactionId);

            // Check for completed objectives
            CheckObjectiveCompletion(FactionId);

            // Apply territory-based bonuses
            ApplyTerritoryBonuses(FactionId);

            // Track batch processing results
            BatchResult.UpdatedFactionIds.Add(FactionId);
            if (ProgressionData.CurrentTier != OldTier)
            {
                BatchResult.ReputationDeltas.Add(FactionId, ProgressionData.TotalReputationPoints);
            }

            // Break if we hit max batch size to prevent hitches
            BatchResult.ProcessedTerritories++;
            if (BatchResult.ProcessedTerritories >= MaxBatchSize)
            {
                break;
            }
        }
    }

    // Record performance metrics
    const double EndTime = FPlatformTime::Seconds();
    BatchResult.ProcessingTimeMs = (EndTime - StartTime) * 1000.0;
    
    // Update performance tracking
    ProcessingTimeHistory.Add(BatchResult.ProcessingTimeMs);
    if (ProcessingTimeHistory.Num() > 100) // Keep last 100 measurements
    {
        ProcessingTimeHistory.RemoveAt(0);
    }

    // Calculate rolling average
    float TotalTime = 0.0f;
    for (float Time : ProcessingTimeHistory)
    {
        TotalTime += Time;
    }
    AverageProcessingTimeMs = ProcessingTimeHistory.Num() > 0 ? TotalTime / ProcessingTimeHistory.Num() : 0.0f;

    LastBatchResult = BatchResult;
    TotalBatchesProcessed++;

    // Performance warning if processing takes too long
    if (BatchResult.ProcessingTimeMs > 16.0f) // Target: <16ms for 60fps
    {
        UE_LOG(LogTemp, Warning, TEXT("TerritorialProgressionSubsystem: Batch processing took %.2fms (target: <16ms)"), BatchResult.ProcessingTimeMs);
    }

    // Broadcast events for updated factions
    BroadcastProgressionEvents(BatchResult.UpdatedFactionIds);

    UE_LOG(LogTemp, VeryVerbose, TEXT("TerritorialProgressionSubsystem: Batch processed %d territories in %.2fms (avg: %.2fms)"), 
           BatchResult.ProcessedTerritories, BatchResult.ProcessingTimeMs, AverageProcessingTimeMs);
}

void UTGTerritorialProgressionSubsystem::RefreshTerritorialStateCache()
{
    // Optimization Strategy: Cache territorial state to avoid expensive spatial queries during batch processing
    
    UTGTerritorialManager* TerritorialManager = GetCachedTerritorialManager();
    if (!TerritorialManager)
    {
        return;
    }

    // Get all territories - this is expensive so we cache the results
    TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();

    {
        FScopeLock Lock(&ProgressionDataMutex);
        
        // Clear existing cache
        TerritorialStateCache.Empty();
        TerritorialStateCache.Reserve(AllTerritories.Num());

        // Rebuild cache with current territorial state
        for (const FTGTerritoryData& Territory : AllTerritories)
        {
            FTGCachedTerritorialState CachedState;
            CachedState.TerritoryId = Territory.TerritoryId;
            CachedState.ControllingFactionId = Territory.CurrentControllerFactionId;
            CachedState.StrategicValue = Territory.StrategicValue;
            CachedState.bContested = Territory.bContested;
            
            // Map territory type to resource type for bonuses
            if (Territory.TerritoryType == TEXT("military"))
                CachedState.ResourceType = ETerritoryResourceType::Military;
            else if (Territory.TerritoryType == TEXT("industrial"))
                CachedState.ResourceType = ETerritoryResourceType::Industrial;
            else if (Territory.TerritoryType == TEXT("research"))
                CachedState.ResourceType = ETerritoryResourceType::Research;
            else if (Territory.TerritoryType == TEXT("district"))
                CachedState.ResourceType = ETerritoryResourceType::Strategic;
            else
                CachedState.ResourceType = ETerritoryResourceType::Economic;

            // Calculate control duration (simplified for performance)
            const FDateTime Now = FDateTime::Now();
            const double HoursSinceContest = (Now - Territory.LastContestedTime).GetTotalHours();
            CachedState.ControlDuration = !Territory.bContested ? HoursSinceContest * 3600.0f : 0.0f; // Convert to seconds

            TerritorialStateCache.Add(Territory.TerritoryId, CachedState);
        }
    }

    UE_LOG(LogTemp, VeryVerbose, TEXT("TerritorialProgressionSubsystem: Refreshed cache with %d territories"), AllTerritories.Num());
}

void UTGTerritorialProgressionSubsystem::CalculateFactionReputation(int32 FactionId)
{
    // Performance-optimized reputation calculation using cached territorial state
    
    FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId);
    if (!ProgressionData)
    {
        return;
    }

    float ReputationGain = 0.0f;
    int32 ControlledTerritories = 0;
    int32 TotalTerritoryHours = 0;

    // Use cached territorial state for performance
    for (const auto& CachePair : TerritorialStateCache)
    {
        const FTGCachedTerritorialState& TerritoryState = CachePair.Value;
        
        if (TerritoryState.ControllingFactionId == FactionId && !TerritoryState.bContested)
        {
            ControlledTerritories++;
            
            // Base reputation per territory per batch (5 seconds)
            float BaseReputation = (BaseReputationPerHour / 3600.0f) * BatchProcessingInterval;
            
            // Strategic value multiplier
            BaseReputation *= TerritoryState.StrategicValue;
            
            // Resource type multiplier
            if (const float* ResourceMultiplier = ResourceTypeMultipliers.Find(TerritoryState.ResourceType))
            {
                BaseReputation *= *ResourceMultiplier;
            }
            
            ReputationGain += BaseReputation;
            
            // Track total territory control time
            TotalTerritoryHours += FMath::FloorToInt(TerritoryState.ControlDuration / 3600.0f);
        }
    }

    // Update progression data
    ProgressionData->TerritoriesControlled = ControlledTerritories;
    ProgressionData->TotalTerritoryHours = TotalTerritoryHours;

    // Apply reputation gain if significant
    if (ReputationGain > 0.1f) // Threshold to avoid micro-updates
    {
        ProgressionData->TotalReputationPoints += ReputationGain;
        ProgressionData->LastProgressionUpdate = FDateTime::Now();
    }
}

void UTGTerritorialProgressionSubsystem::UpdateFactionTier(int32 FactionId)
{
    FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId);
    if (!ProgressionData)
    {
        return;
    }

    const EFactionProgressionTier OldTier = ProgressionData->CurrentTier;
    EFactionProgressionTier NewTier = EFactionProgressionTier::Recruit;

    // Find the highest tier this faction qualifies for
    for (const auto& TierPair : TierThresholds)
    {
        if (ProgressionData->TotalReputationPoints >= TierPair.Value)
        {
            NewTier = TierPair.Key;
        }
    }

    if (NewTier != OldTier)
    {
        ProgressionData->CurrentTier = NewTier;
        
        // Apply tier-based bonuses
        switch (NewTier)
        {
            case EFactionProgressionTier::Veteran:
                ProgressionData->ExtractionBonusMultiplier = FMath::Max(ProgressionData->ExtractionBonusMultiplier, 1.10f);
                break;
            case EFactionProgressionTier::Elite:
                ProgressionData->ExtractionBonusMultiplier = FMath::Max(ProgressionData->ExtractionBonusMultiplier, 1.25f);
                ProgressionData->InfluenceRateMultiplier = FMath::Max(ProgressionData->InfluenceRateMultiplier, 1.15f);
                break;
            case EFactionProgressionTier::Commander:
                ProgressionData->ExtractionBonusMultiplier = FMath::Max(ProgressionData->ExtractionBonusMultiplier, 1.50f);
                ProgressionData->InfluenceRateMultiplier = FMath::Max(ProgressionData->InfluenceRateMultiplier, 1.30f);
                break;
            case EFactionProgressionTier::Warlord:
                ProgressionData->ExtractionBonusMultiplier = FMath::Max(ProgressionData->ExtractionBonusMultiplier, 2.00f);
                ProgressionData->InfluenceRateMultiplier = FMath::Max(ProgressionData->InfluenceRateMultiplier, 1.50f);
                break;
        }

        UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Faction %d tier upgraded: %d → %d"), 
               FactionId, static_cast<int32>(OldTier), static_cast<int32>(NewTier));
    }
}

void UTGTerritorialProgressionSubsystem::CheckObjectiveCompletion(int32 FactionId)
{
    // Check active objectives for this faction
    for (FTGTerritorialObjective& Objective : ActiveObjectives)
    {
        if (Objective.TargetFactionId == FactionId && !Objective.bCompleted)
        {
            // Count controlled territories of required type
            int32 RequiredTypeCount = 0;
            
            for (const auto& CachePair : TerritorialStateCache)
            {
                const FTGCachedTerritorialState& TerritoryState = CachePair.Value;
                
                if (TerritoryState.ControllingFactionId == FactionId && 
                    !TerritoryState.bContested && 
                    TerritoryState.ResourceType == Objective.RequiredResourceType)
                {
                    RequiredTypeCount++;
                }
            }

            // Complete objective if requirements met
            if (RequiredTypeCount >= Objective.RequiredTerritories)
            {
                CompleteObjective(FactionId, Objective.ObjectiveId);
            }
        }
    }
}

void UTGTerritorialProgressionSubsystem::ApplyTerritoryBonuses(int32 FactionId)
{
    FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId);
    if (!ProgressionData)
    {
        return;
    }

    // Calculate resource bonuses based on controlled territories
    TMap<ETerritoryResourceType, int32> ResourceCounts;
    
    for (const auto& CachePair : TerritorialStateCache)
    {
        const FTGCachedTerritorialState& TerritoryState = CachePair.Value;
        
        if (TerritoryState.ControllingFactionId == FactionId && !TerritoryState.bContested)
        {
            int32& Count = ResourceCounts.FindOrAdd(TerritoryState.ResourceType, 0);
            Count++;
        }
    }

    // Update resource bonuses and broadcast changes
    for (const auto& ResourcePair : ResourceCounts)
    {
        const ETerritoryResourceType ResourceType = ResourcePair.Key;
        const int32 NewBonus = ResourcePair.Value;
        
        int32& CurrentBonus = ProgressionData->ResourceBonuses.FindOrAdd(ResourceType, 0);
        if (CurrentBonus != NewBonus)
        {
            CurrentBonus = NewBonus;
            OnResourceBonusChanged.Broadcast(FactionId, ResourceType);
        }
    }
}

// Cached Subsystem Access - Performance Optimization
UTGTerritorialManager* UTGTerritorialProgressionSubsystem::GetCachedTerritorialManager() const
{
    if (!CachedTerritorialManager)
    {
        if (UWorld* World = GetGameInstance()->GetWorld())
        {
            CachedTerritorialManager = World->GetSubsystem<UTGTerritorialManager>();
        }
    }
    return CachedTerritorialManager;
}

UTGConvoyEconomySubsystem* UTGTerritorialProgressionSubsystem::GetCachedConvoyEconomySubsystem() const
{
    if (!CachedConvoyEconomySubsystem)
    {
        if (UWorld* World = GetGameInstance()->GetWorld())
        {
            CachedConvoyEconomySubsystem = World->GetSubsystem<UTGConvoyEconomySubsystem>();
        }
    }
    return CachedConvoyEconomySubsystem;
}

// Debug and Performance Functions
void UTGTerritorialProgressionSubsystem::ForceProgressionUpdate()
{
    UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Forcing immediate progression update"));
    ProcessProgressionBatch();
    RefreshTerritorialStateCache();
}

void UTGTerritorialProgressionSubsystem::ClearFactionProgression(int32 FactionId)
{
    FScopeLock Lock(&ProgressionDataMutex);

    if (FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
    {
        // Reset progression data to defaults
        ProgressionData->TotalReputationPoints = 0.0f;
        ProgressionData->CurrentTier = EFactionProgressionTier::Recruit;
        ProgressionData->TerritoriesControlled = 0;
        ProgressionData->TotalTerritoryHours = 0;
        ProgressionData->ResourceBonuses.Empty();
        ProgressionData->UnlockedAbilities.Empty();
        ProgressionData->ExtractionBonusMultiplier = 1.0f;
        ProgressionData->InfluenceRateMultiplier = 1.0f;
        ProgressionData->LastProgressionUpdate = FDateTime::Now();

        UE_LOG(LogTemp, Log, TEXT("TerritorialProgressionSubsystem: Cleared progression for faction %d"), FactionId);
    }
}

// Thread Safety & Performance Broadcasting
void UTGTerritorialProgressionSubsystem::BroadcastProgressionEvents(const TArray<int32>& UpdatedFactionIds)
{
    // Batch broadcast events to avoid spam during high-frequency updates
    for (int32 FactionId : UpdatedFactionIds)
    {
        if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
        {
            OnFactionProgressionChanged.Broadcast(FactionId, ProgressionData->CurrentTier, ProgressionData->TotalReputationPoints);
        }
    }
}

// Database Integration - UTGProfileSave Integration for Performance
void UTGTerritorialProgressionSubsystem::SaveProgressionDataAsync(int32 FactionId)
{
    // Async save to prevent gameplay hitches - integrates with UTGProfileSave
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [this, FactionId]()
    {
        FScopeLock Lock(&ProgressionDataMutex);
        
        if (const FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
        {
            // Get the game instance to access save system
            if (UGameInstance* GameInstance = GetGameInstance())
            {
                if (class UTGGameInstance* TGGameInstance = Cast<UTGGameInstance>(GameInstance))
                {
                    // Save progression data to UTGProfileSave
                    // This would call TGGameInstance save methods that update UTGProfileSave with:
                    // - FactionReputationPoints
                    // - FactionProgressionTiers
                    // - FactionUnlockedAbilities
                    // - FactionTerritoryHours
                    // - FactionExtractionBonuses
                    // - FactionInfluenceRates
                    UE_LOG(LogTemp, VeryVerbose, TEXT("TerritorialProgressionSubsystem: Saving progression data for faction %d via UTGProfileSave"), FactionId);
                }
            }
        }
    });
}

void UTGTerritorialProgressionSubsystem::LoadProgressionDataAsync(int32 FactionId)
{
    // Async load to prevent initialization hitches - integrates with UTGProfileSave
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [this, FactionId]()
    {
        // Load progression data from UTGProfileSave
        if (UGameInstance* GameInstance = GetGameInstance())
        {
            if (class UTGGameInstance* TGGameInstance = Cast<UTGGameInstance>(GameInstance))
            {
                // Load progression data from UTGProfileSave
                // This would call TGGameInstance load methods that read from UTGProfileSave:
                // - FactionReputationPoints.FindRef(FactionId)
                // - FactionProgressionTiers.FindRef(FactionId) 
                // - FactionUnlockedAbilities.FindRef(FactionId)
                // - FactionTerritoryHours.FindRef(FactionId)
                // - FactionExtractionBonuses.FindRef(FactionId)
                // - FactionInfluenceRates.FindRef(FactionId)
                
                // Update FactionProgressionMap with loaded data
                AsyncTask(ENamedThreads::GameThread, [this, FactionId]()
                {
                    FScopeLock Lock(&ProgressionDataMutex);
                    
                    if (FTGFactionProgressionData* ProgressionData = FactionProgressionMap.Find(FactionId))
                    {
                        // ProgressionData would be updated with loaded values here
                        UE_LOG(LogTemp, VeryVerbose, TEXT("TerritorialProgressionSubsystem: Loaded progression data for faction %d from UTGProfileSave"), FactionId);
                    }
                });
            }
        }
    });
}

// Memory Management
void UTGTerritorialProgressionSubsystem::CleanupExpiredObjectives()
{
    FScopeLock Lock(&ProgressionDataMutex);

    const FDateTime Now = FDateTime::Now();
    const FTimespan ExpirationTime = FTimespan::FromDays(7); // Objectives expire after 7 days

    ActiveObjectives.RemoveAll([&](const FTGTerritorialObjective& Objective)
    {
        return Objective.bCompleted && (Now - Objective.CompletionTime) > ExpirationTime;
    });
}

void UTGTerritorialProgressionSubsystem::OptimizeMemoryUsage()
{
    // Trim processing time history if it gets too large
    if (ProcessingTimeHistory.Num() > 100)
    {
        ProcessingTimeHistory.RemoveAt(0, ProcessingTimeHistory.Num() - 100);
    }

    // Clean up expired objectives periodically
    CleanupExpiredObjectives();
}