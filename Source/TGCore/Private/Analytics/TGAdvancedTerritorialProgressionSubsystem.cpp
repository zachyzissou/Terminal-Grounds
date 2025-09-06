#include "Analytics/TGAdvancedTerritorialProgressionSubsystem.h"
#include "Analytics/TGTerritorialResourceAnalytics.h"
#include "TerritorialProgressionSubsystem.h"
#include "Trust/TGTrustSubsystem.h"
#include "Codex/TGCodexSubsystem.h"
#include "TGWorld/Public/TGTerritorialManager.h"
#include "TGWorld/Public/Economy/TGConvoyEconomySubsystem.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/DateTime.h"
#include "Async/Async.h"

UTGAdvancedTerritorialProgressionSubsystem::UTGAdvancedTerritorialProgressionSubsystem()
{
    // Initialize advanced analytics collections with performance optimization
    FactionResourceBonuses.Reserve(7); // 7 factions
    ResourceMarketMetrics.Reserve(5); // 5 resource types
    FactionPerformanceCache.Reserve(7); // 7 factions
    PlayerTestAssignments.Reserve(1000); // Support 1000 concurrent players in A/B tests
    BalanceHistoryBuffer.Reserve(MaxBalanceHistorySize);
    
    bEmergencyBalanceMode = false;
    LastEmergencyAdjustment = FDateTime::Now() - FTimespan::FromHours(24); // Allow immediate emergency if needed
}

void UTGAdvancedTerritorialProgressionSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Initializing advanced analytics-driven territorial progression"));

    // Cache critical subsystem references
    BaseProgressionSubsystem = GetGameInstance()->GetSubsystem<UTGTerritorialProgressionSubsystem>();
    ResourceAnalytics = GetGameInstance()->GetSubsystem<UTGTerritorialResourceAnalytics>();
    TrustSubsystem = GetGameInstance()->GetSubsystem<UTGTrustSubsystem>();
    CodexSubsystem = GetGameInstance()->GetSubsystem<UTGCodexSubsystem>();
    
    if (UWorld* World = GetGameInstance()->GetWorld())
    {
        TerritorialManager = World->GetSubsystem<UTGTerritorialManager>();
        ConvoyEconomySubsystem = World->GetSubsystem<UTGConvoyEconomySubsystem>();
    }

    // Validate critical dependencies
    if (!BaseProgressionSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Base progression subsystem required but not available"));
        return;
    }

    if (!ResourceAnalytics)
    {
        UE_LOG(LogTemp, Error, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Resource analytics subsystem required but not available"));
        return;
    }

    if (!TerritorialManager)
    {
        UE_LOG(LogTemp, Error, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Territorial manager required but not available"));
        return;
    }

    // Initialize advanced data structures
    InitializeAdvancedResourceBonuses();
    InitializeMarketMetrics();
    LoadAdvancedHistoricalData();

    // Start advanced processing timers
    if (UWorld* World = GetGameInstance()->GetWorld())
    {
        // Advanced analytics processing (1 minute intervals)
        World->GetTimerManager().SetTimer(
            AdvancedAnalyticsTimer,
            this,
            &UTGAdvancedTerritorialProgressionSubsystem::ProcessAdvancedAnalytics,
            AnalyticsUpdateInterval,
            true
        );

        // Balance monitoring (5 minute intervals)
        World->GetTimerManager().SetTimer(
            BalanceMonitoringTimer,
            this,
            &UTGAdvancedTerritorialProgressionSubsystem::CheckBalanceHealth,
            BalanceMonitoringInterval,
            true
        );

        // Market equilibrium updates (3 minute intervals)
        World->GetTimerManager().SetTimer(
            MarketUpdateTimer,
            this,
            &UTGAdvancedTerritorialProgressionSubsystem::UpdateMarketEquilibrium,
            MarketUpdateInterval,
            true
        );

        UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Advanced processing started - Analytics: %.0fs, Balance: %.0fs, Market: %.0fs"), 
               AnalyticsUpdateInterval, BalanceMonitoringInterval, MarketUpdateInterval);
    }
}

void UTGAdvancedTerritorialProgressionSubsystem::Deinitialize()
{
    UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Shutting down advanced analytics system"));

    // Clear timers
    if (UWorld* World = GetGameInstance()->GetWorld())
    {
        World->GetTimerManager().ClearTimer(AdvancedAnalyticsTimer);
        World->GetTimerManager().ClearTimer(BalanceMonitoringTimer);
        World->GetTimerManager().ClearTimer(MarketUpdateTimer);
    }

    // Save advanced analytics state for persistence
    // In production, this would integrate with database save system

    Super::Deinitialize();
}

// Advanced Resource Bonus System - Analytics Integration
FTGAdvancedResourceBonus UTGAdvancedTerritorialProgressionSubsystem::CalculateAdvancedResourceBonus(int32 FactionId, ETerritoryResourceType ResourceType, int32 TerritoryId)
{
    FScopeLock Lock(&AdvancedAnalyticsMutex);

    // Get or create faction resource bonus entry
    TMap<ETerritoryResourceType, FTGAdvancedResourceBonus>& FactionBonuses = FactionResourceBonuses.FindOrAdd(FactionId);
    FTGAdvancedResourceBonus& ResourceBonus = FactionBonuses.FindOrAdd(ResourceType);

    // Update base values from base progression system
    if (BaseProgressionSubsystem)
    {
        int32 BaseResourceBonus = BaseProgressionSubsystem->GetResourceBonus(FactionId, ResourceType);
        ResourceBonus.BaseValue = FMath::Max(50.0f, BaseResourceBonus * 10.0f); // Scale appropriately
    }

    // Apply analytics-driven multipliers
    if (ResourceAnalytics)
    {
        // Get analytical resource value for this specific territory
        float AnalyticalValue = ResourceAnalytics->GenerateResourceValue(ResourceType, TerritoryId);
        ResourceBonus.AnalyticalMultiplier = AnalyticalValue / 100.0f; // Normalize around 1.0

        // Get current analytics for confidence level
        FTGResourceBonusAnalytics CurrentAnalytics = ResourceAnalytics->GetCurrentAnalytics(ResourceType);
        ResourceBonus.ConfidenceLevel = FMath::Clamp(CurrentAnalytics.CompetitiveBalance, 0.7f, 0.99f);
    }

    // Apply market equilibrium adjustments
    if (const FTGTerritorialResourceMetrics* MarketMetrics = ResourceMarketMetrics.Find(ResourceType))
    {
        // Market value adjustment
        float MarketAdjustment = (MarketMetrics->MarketValue - 1.0f) * 50.0f; // Scale market deviation
        ResourceBonus.EquilibriumAdjustment = MarketAdjustment;

        // Scarcity bonus
        ResourceBonus.AnalyticalMultiplier *= MarketMetrics->ScarcityMultiplier;
    }

    // Apply faction synergy bonuses
    if (TerritorialManager)
    {
        TArray<FTGTerritoryData> NearbyTerritories = TerritorialManager->GetTerritoriesInRadius(
            FVector2D::ZeroVector, 3000.0f); // 3km radius for synergy calculation
            
        for (const FTGTerritoryData& NearbyTerritory : NearbyTerritories)
        {
            if (NearbyTerritory.TerritoryId != TerritoryId && 
                NearbyTerritory.CurrentControllerFactionId != FactionId && 
                NearbyTerritory.CurrentControllerFactionId > 0)
            {
                float SynergyBonus = CalculateFactionSynergyBonus(FactionId, NearbyTerritory.CurrentControllerFactionId, ResourceType);
                if (SynergyBonus > MinSynergyThreshold)
                {
                    ResourceBonus.FactionSynergyBonuses.Add(NearbyTerritory.CurrentControllerFactionId, SynergyBonus);
                }
            }
        }
    }

    // Apply A/B test modifications
    // This would check if this faction is part of an active A/B test and apply test values

    // Apply time decay for dynamic bonuses
    if (ResourceBonus.BonusType == ETerritorialBonusType::Dynamic)
    {
        FDateTime Now = FDateTime::Now();
        // Simplified decay - in production would track last update time per bonus
        float HoursSinceUpdate = 1.0f; // Placeholder
        float DecayMultiplier = FMath::Exp(-ResourceBonus.DecayRate * HoursSinceUpdate);
        DecayMultiplier = FMath::Max(DecayMultiplier, ResourceBonus.MinDecayValue);
        ResourceBonus.AnalyticalMultiplier *= DecayMultiplier;
    }

    return ResourceBonus;
}

void UTGAdvancedTerritorialProgressionSubsystem::UpdateResourceBonusWithAnalytics(int32 FactionId, ETerritoryResourceType ResourceType, float AnalyticalMultiplier, float ConfidenceLevel)
{
    FScopeLock Lock(&AdvancedAnalyticsMutex);

    TMap<ETerritoryResourceType, FTGAdvancedResourceBonus>& FactionBonuses = FactionResourceBonuses.FindOrAdd(FactionId);
    FTGAdvancedResourceBonus& ResourceBonus = FactionBonuses.FindOrAdd(ResourceType);

    float OldValue = ResourceBonus.CalculateFinalValue();
    
    ResourceBonus.AnalyticalMultiplier = AnalyticalMultiplier;
    ResourceBonus.ConfidenceLevel = ConfidenceLevel;
    ResourceBonus.BonusType = ETerritorialBonusType::Dynamic; // Mark as analytics-driven

    float NewValue = ResourceBonus.CalculateFinalValue();

    // Broadcast update if significant change
    if (FMath::Abs(NewValue - OldValue) > 5.0f) // 5-point threshold
    {
        OnAdvancedResourceBonusUpdated.Broadcast(FactionId, ResourceType, NewValue, ConfidenceLevel);
        
        UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Updated resource bonus for Faction %d, %s: %.1f -> %.1f (Confidence: %.2f)"), 
               FactionId, *UEnum::GetValueAsString(ResourceType), OldValue, NewValue, ConfidenceLevel);
    }
}

float UTGAdvancedTerritorialProgressionSubsystem::GetAnalyticsAdjustedResourceBonus(int32 FactionId, ETerritoryResourceType ResourceType)
{
    FScopeLock Lock(&AdvancedAnalyticsMutex);

    const TMap<ETerritoryResourceType, FTGAdvancedResourceBonus>* FactionBonuses = FactionResourceBonuses.Find(FactionId);
    if (!FactionBonuses)
    {
        return 100.0f; // Default baseline value
    }

    const FTGAdvancedResourceBonus* ResourceBonus = FactionBonuses->Find(ResourceType);
    if (!ResourceBonus)
    {
        return 100.0f; // Default baseline value
    }

    return ResourceBonus->CalculateFinalValue();
}

// Territorial Performance Analytics
FTGFactionTerritorialPerformance UTGAdvancedTerritorialProgressionSubsystem::AnalyzeFactionPerformance(int32 FactionId)
{
    FTGFactionTerritorialPerformance Performance;
    Performance.FactionId = FactionId;

    if (!BaseProgressionSubsystem || !TerritorialManager || !ResourceAnalytics)
    {
        return Performance;
    }

    FScopeLock Lock(&AdvancedAnalyticsMutex);

    // Get base progression data
    FTGFactionProgressionData BaseProgression = BaseProgressionSubsystem->GetFactionProgression(FactionId);
    Performance.TerritoriesControlled = BaseProgression.TerritoriesControlled;

    // Analyze controlled territories
    TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();
    TArray<FTGTerritoryData> ControlledTerritories = AllTerritories.FilterByPredicate([FactionId](const FTGTerritoryData& Territory)
    {
        return Territory.CurrentControllerFactionId == FactionId && !Territory.bContested;
    });

    // Calculate high-value territory count
    Performance.HighValueTerritories = ControlledTerritories.FilterByPredicate([](const FTGTerritoryData& Territory)
    {
        return Territory.StrategicValue >= 7; // High-value threshold
    }).Num();

    // Calculate average territory value
    if (ControlledTerritories.Num() > 0)
    {
        float TotalValue = 0.0f;
        for (const FTGTerritoryData& Territory : ControlledTerritories)
        {
            TotalValue += Territory.StrategicValue;
        }
        Performance.AverageTerritoryValue = TotalValue / ControlledTerritories.Num();
    }

    // Calculate resource efficiency for each resource type
    const TArray<ETerritoryResourceType> ResourceTypes = {
        ETerritoryResourceType::Industrial,
        ETerritoryResourceType::Military,
        ETerritoryResourceType::Research,
        ETerritoryResourceType::Economic,
        ETerritoryResourceType::Strategic
    };

    for (ETerritoryResourceType ResourceType : ResourceTypes)
    {
        float Efficiency = ResourceAnalytics->CalculateFactionResourceEfficiency(FactionId);
        Performance.ResourceEfficiency.Add(ResourceType, Efficiency);
        Performance.TotalResourceGeneration += Efficiency * GetAnalyticsAdjustedResourceBonus(FactionId, ResourceType);
    }

    // Calculate competitive metrics using predictive analytics
    TMap<int32, float> WinRatePredictions = ResourceAnalytics->PredictFactionWinRates(168.0f);
    if (const float* PredictedWinRate = WinRatePredictions.Find(FactionId))
    {
        Performance.TerritorialWinRate = *PredictedWinRate;
    }

    // Estimate defense and attack success rates based on territorial data
    // In production, this would use historical battle outcome data
    Performance.DefenseSuccessRate = FMath::Clamp(Performance.TerritorialWinRate * 1.1f, 0.0f, 1.0f); // Slight advantage for defenders
    Performance.AttackSuccessRate = FMath::Clamp(Performance.TerritorialWinRate * 0.9f, 0.0f, 1.0f); // Slight disadvantage for attackers

    // Predictive growth calculation
    float CurrentBalance = ResourceAnalytics->CalculateCompetitiveBalance();
    float FactionBalance = Performance.TerritorialWinRate;
    
    // Growth prediction based on current performance relative to balance
    Performance.PredictedGrowth = (FactionBalance - (1.0f / 7.0f)) * 100.0f; // Compare to equal 1/7 share

    // Retention risk calculation
    if (Performance.TerritorialWinRate < 0.3f) // Performing poorly
    {
        Performance.RetentionRisk = 0.7f + (0.3f - Performance.TerritorialWinRate); // High risk
    }
    else if (Performance.TerritorialWinRate > 0.7f) // Performing too well
    {
        Performance.RetentionRisk = 0.3f; // Moderate risk (boredom from lack of challenge)
    }
    else
    {
        Performance.RetentionRisk = 0.1f; // Low risk in balanced range
    }

    // Balance score relative to overall game balance
    Performance.BalanceScore = CurrentBalance * FactionBalance;

    // Cache performance for quick access
    FactionPerformanceCache.Add(FactionId, Performance);

    return Performance;
}

TArray<FTGFactionTerritorialPerformance> UTGAdvancedTerritorialProgressionSubsystem::GeneratePerformanceReport()
{
    TArray<FTGFactionTerritorialPerformance> PerformanceReport;
    
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    
    for (int32 FactionId : AllFactionIds)
    {
        FTGFactionTerritorialPerformance Performance = AnalyzeFactionPerformance(FactionId);
        TArray<FString> Recommendations = GenerateFactionRecommendations(FactionId);
        
        PerformanceReport.Add(Performance);
        
        // Broadcast individual performance analysis
        OnTerritorialPerformanceAnalyzed.Broadcast(FactionId, Performance, Recommendations);
    }
    
    return PerformanceReport;
}

TArray<FString> UTGAdvancedTerritorialProgressionSubsystem::GenerateFactionRecommendations(int32 FactionId)
{
    TArray<FString> Recommendations;
    
    FTGFactionTerritorialPerformance Performance = AnalyzeFactionPerformance(FactionId);
    
    // Performance-based recommendations
    if (Performance.TerritorialWinRate < 0.25f)
    {
        Recommendations.Add(TEXT("CRITICAL: Faction severely underperforming - increase resource bonuses by 20%"));
        Recommendations.Add(TEXT("Consider faction-specific territorial objectives to boost engagement"));
    }
    else if (Performance.TerritorialWinRate < 0.4f)
    {
        Recommendations.Add(TEXT("MODERATE: Faction underperforming - increase resource bonuses by 10%"));
        Recommendations.Add(TEXT("Analyze faction synergies for potential alliance bonuses"));
    }
    else if (Performance.TerritorialWinRate > 0.7f)
    {
        Recommendations.Add(TEXT("BALANCE: Faction overperforming - consider reducing resource bonuses by 5%"));
        Recommendations.Add(TEXT("Monitor for player retention issues due to lack of challenge"));
    }

    // Resource efficiency recommendations
    for (const auto& EfficiencyPair : Performance.ResourceEfficiency)
    {
        ETerritoryResourceType ResourceType = EfficiencyPair.Key;
        float Efficiency = EfficiencyPair.Value;
        
        if (Efficiency < 0.8f)
        {
            FString ResourceName = UEnum::GetValueAsString(ResourceType);
            Recommendations.Add(FString::Printf(TEXT("Low efficiency in %s resources (%.1f%%) - investigate territorial positioning"), *ResourceName, Efficiency * 100.0f));
        }
    }

    // Retention risk recommendations
    if (Performance.RetentionRisk > 0.5f)
    {
        Recommendations.Add(TEXT("HIGH RETENTION RISK: Priority faction for balance improvements"));
        Recommendations.Add(TEXT("Consider special events or bonuses to improve player experience"));
    }

    // Territory distribution recommendations
    if (Performance.TerritoriesControlled == 0)
    {
        Recommendations.Add(TEXT("URGENT: Faction has no territories - provide starting territory guarantee"));
    }
    else if (Performance.HighValueTerritories == 0 && Performance.TerritoriesControlled > 2)
    {
        Recommendations.Add(TEXT("Faction lacks high-value territories despite territorial presence - adjust strategic value calculations"));
    }

    return Recommendations;
}

// Market Equilibrium Analysis
FTGTerritorialResourceMetrics UTGAdvancedTerritorialProgressionSubsystem::GetResourceMarketMetrics(ETerritoryResourceType ResourceType)
{
    FScopeLock Lock(&AdvancedAnalyticsMutex);

    if (const FTGTerritorialResourceMetrics* Metrics = ResourceMarketMetrics.Find(ResourceType))
    {
        return *Metrics;
    }

    // Return default metrics if not found
    return FTGTerritorialResourceMetrics();
}

void UTGAdvancedTerritorialProgressionSubsystem::UpdateMarketEquilibrium()
{
    if (!TerritorialManager || !ResourceAnalytics)
    {
        return;
    }

    FScopeLock Lock(&AdvancedAnalyticsMutex);
    
    const TArray<ETerritoryResourceType> ResourceTypes = {
        ETerritoryResourceType::Industrial,
        ETerritoryResourceType::Military,
        ETerritoryResourceType::Research,
        ETerritoryResourceType::Economic,
        ETerritoryResourceType::Strategic
    };

    TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();

    for (ETerritoryResourceType ResourceType : ResourceTypes)
    {
        FTGTerritorialResourceMetrics& Metrics = ResourceMarketMetrics.FindOrAdd(ResourceType);
        
        // Calculate resource generation rate across all territories
        float TotalGeneration = 0.0f;
        int32 ResourceTerritoryCount = 0;
        
        for (const FTGTerritoryData& Territory : AllTerritories)
        {
            // Map territory type to resource type
            ETerritoryResourceType TerritoryResourceType = ETerritoryResourceType::Economic;
            if (Territory.TerritoryType == TEXT("military"))
                TerritoryResourceType = ETerritoryResourceType::Military;
            else if (Territory.TerritoryType == TEXT("industrial"))
                TerritoryResourceType = ETerritoryResourceType::Industrial;
            else if (Territory.TerritoryType == TEXT("research"))
                TerritoryResourceType = ETerritoryResourceType::Research;
            else if (Territory.TerritoryType == TEXT("district"))
                TerritoryResourceType = ETerritoryResourceType::Strategic;
                
            if (TerritoryResourceType == ResourceType)
            {
                ResourceTerritoryCount++;
                if (Territory.CurrentControllerFactionId > 0 && !Territory.bContested)
                {
                    float TerritoryGeneration = ResourceAnalytics->GenerateResourceValue(ResourceType, Territory.TerritoryId);
                    TotalGeneration += TerritoryGeneration;
                }
            }
        }
        
        // Calculate metrics
        Metrics.GenerationRate = ResourceTerritoryCount > 0 ? TotalGeneration / ResourceTerritoryCount : 0.0f;
        
        // Calculate scarcity multiplier
        EResourceScarcityLevel ScarcityLevel = ResourceAnalytics->AnalyzeResourceScarcity(ResourceType);
        switch (ScarcityLevel)
        {
            case EResourceScarcityLevel::Abundant: Metrics.ScarcityMultiplier = 0.8f; break;
            case EResourceScarcityLevel::Common: Metrics.ScarcityMultiplier = 1.0f; break;
            case EResourceScarcityLevel::Scarce: Metrics.ScarcityMultiplier = 1.3f; break;
            case EResourceScarcityLevel::Critical: Metrics.ScarcityMultiplier = 1.8f; break;
        }
        
        // Calculate market value relative to other resources
        float BaselineGeneration = 100.0f; // Baseline expectation
        Metrics.MarketValue = Metrics.GenerationRate > 0.0f ? BaselineGeneration / Metrics.GenerationRate : 1.0f;
        Metrics.MarketValue = FMath::Clamp(Metrics.MarketValue, 0.5f, 2.0f); // Reasonable market value range
        
        // Calculate strategic importance based on faction preferences
        float StrategicSum = 0.0f;
        int32 FactionCount = 0;
        const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
        
        for (int32 FactionId : AllFactionIds)
        {
            const TMap<ETerritoryResourceType, FTGAdvancedResourceBonus>* FactionBonuses = FactionResourceBonuses.Find(FactionId);
            if (FactionBonuses)
            {
                const FTGAdvancedResourceBonus* ResourceBonus = FactionBonuses->Find(ResourceType);
                if (ResourceBonus)
                {
                    StrategicSum += ResourceBonus->CalculateFinalValue();
                    FactionCount++;
                }
            }
        }
        
        Metrics.StrategicImportance = FactionCount > 0 ? StrategicSum / (FactionCount * 10.0f) : 5.0f; // Normalize to 0-10 scale
        
        // Calculate competition intensity (how contested this resource type is)
        int32 ContestedResourceTerritories = 0;
        for (const FTGTerritoryData& Territory : AllTerritories)
        {
            ETerritoryResourceType TerritoryResourceType = ETerritoryResourceType::Economic;
            if (Territory.TerritoryType == TEXT("military"))
                TerritoryResourceType = ETerritoryResourceType::Military;
            else if (Territory.TerritoryType == TEXT("industrial"))
                TerritoryResourceType = ETerritoryResourceType::Industrial;
            else if (Territory.TerritoryType == TEXT("research"))
                TerritoryResourceType = ETerritoryResourceType::Research;
            else if (Territory.TerritoryType == TEXT("district"))
                TerritoryResourceType = ETerritoryResourceType::Strategic;
                
            if (TerritoryResourceType == ResourceType && Territory.bContested)
            {
                ContestedResourceTerritories++;
            }
        }
        
        Metrics.CompetitionIntensity = ResourceTerritoryCount > 0 ? 
            (float)ContestedResourceTerritories / (float)ResourceTerritoryCount : 0.0f;
        
        // Efficiency calculation (simplified for now)
        Metrics.Efficiency = 1.0f; // Would be calculated from production vs consumption
        
        UE_LOG(LogTemp, VeryVerbose, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Updated market metrics for %s - Generation: %.1f, Market Value: %.2f, Scarcity: %.2f"), 
               *UEnum::GetValueAsString(ResourceType), Metrics.GenerationRate, Metrics.MarketValue, Metrics.ScarcityMultiplier);
    }

    // Broadcast market shifts for significant changes
    for (const auto& MetricsPair : ResourceMarketMetrics)
    {
        ETerritoryResourceType ResourceType = MetricsPair.Key;
        const FTGTerritorialResourceMetrics& Metrics = MetricsPair.Value;
        
        // Would compare with previous values and broadcast if significant change
        OnResourceMarketShift.Broadcast(ResourceType, Metrics.MarketValue);
    }
}

float UTGAdvancedTerritorialProgressionSubsystem::GetResourceMarketValue(ETerritoryResourceType ResourceType)
{
    FScopeLock Lock(&AdvancedAnalyticsMutex);

    if (const FTGTerritorialResourceMetrics* Metrics = ResourceMarketMetrics.Find(ResourceType))
    {
        return Metrics->MarketValue;
    }

    return 1.0f; // Default market value
}

// Faction Synergy System
float UTGAdvancedTerritorialProgressionSubsystem::CalculateFactionSynergyBonus(int32 PrimaryFactionId, int32 AlliedFactionId, ETerritoryResourceType ResourceType)
{
    if (!TrustSubsystem)
    {
        return 0.0f;
    }

    // Get trust relationship between factions
    float TrustLevel = 0.5f; // Baseline neutral trust
    // In production, would call TrustSubsystem->GetTrustIndex(PrimaryFactionId, AlliedFactionId)

    if (TrustLevel < 0.3f) // Low trust = negative synergy
    {
        return -0.1f; // 10% penalty for hostile neighbors
    }

    if (TrustLevel < 0.6f) // Neutral trust = no synergy
    {
        return 0.0f;
    }

    // Calculate synergy based on faction compatibility
    float SynergyScore = CalculateTerritorySynergyScore(PrimaryFactionId, AlliedFactionId);

    // Scale synergy by trust level
    float FinalSynergy = SynergyScore * ((TrustLevel - 0.6f) / 0.4f); // Scale 0.6-1.0 trust to 0-1 multiplier

    // Apply resource-specific modifiers
    switch (ResourceType)
    {
        case ETerritoryResourceType::Economic:
            FinalSynergy *= 1.2f; // Economic resources benefit more from cooperation
            break;
        case ETerritoryResourceType::Research:
            FinalSynergy *= 1.3f; // Research benefits significantly from knowledge sharing
            break;
        case ETerritoryResourceType::Military:
            FinalSynergy *= 0.8f; // Military resources less likely to be shared
            break;
        case ETerritoryResourceType::Strategic:
            FinalSynergy *= 0.6f; // Strategic resources rarely shared
            break;
        default:
            break;
    }

    return FMath::Clamp(FinalSynergy, -0.2f, MaxSynergyBonus);
}

TArray<int32> UTGAdvancedTerritorialProgressionSubsystem::GetCompatibleFactions(int32 FactionId)
{
    TArray<int32> CompatibleFactions;
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    
    for (int32 OtherFactionId : AllFactionIds)
    {
        if (OtherFactionId != FactionId)
        {
            float SynergyScore = CalculateTerritorySynergyScore(FactionId, OtherFactionId);
            if (SynergyScore > MinSynergyThreshold)
            {
                CompatibleFactions.Add(OtherFactionId);
            }
        }
    }
    
    return CompatibleFactions;
}

bool UTGAdvancedTerritorialProgressionSubsystem::AreFactionsSynergistic(int32 FactionId1, int32 FactionId2)
{
    float SynergyScore = CalculateTerritorySynergyScore(FactionId1, FactionId2);
    return SynergyScore > MinSynergyThreshold;
}

// Balance Monitoring and Correction
void UTGAdvancedTerritorialProgressionSubsystem::CheckBalanceHealth()
{
    if (!ResourceAnalytics)
    {
        return;
    }

    float CurrentBalance = ResourceAnalytics->CalculateCompetitiveBalance();
    
    // Record balance history for trend analysis
    BalanceHistoryBuffer.Add(CurrentBalance);
    if (BalanceHistoryBuffer.Num() > MaxBalanceHistorySize)
    {
        BalanceHistoryBuffer.RemoveAt(0);
    }

    // Check for balance issues
    if (CurrentBalance < AutoBalanceThreshold)
    {
        UE_LOG(LogTemp, Warning, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Balance below threshold (%.2f < %.2f) - triggering corrections"), 
               CurrentBalance, AutoBalanceThreshold);
        
        DetectAndCorrectImbalances();
    }

    // Check for emergency balance conditions
    if (CurrentBalance < 0.05f && !bEmergencyBalanceMode)
    {
        FDateTime Now = FDateTime::Now();
        FTimespan TimeSinceLastEmergency = Now - LastEmergencyAdjustment;
        
        if (TimeSinceLastEmergency.GetTotalHours() >= 1.0) // Cooldown period
        {
            UE_LOG(LogTemp, Error, TEXT("UTGAdvancedTerritorialProgressionSubsystem: CRITICAL balance failure (%.2f) - triggering emergency adjustments"), CurrentBalance);
            TriggerEmergencyBalanceAdjustment(TEXT("Critical balance failure detected"));
        }
    }

    // Generate performance reports periodically
    if (FMath::Fmod(LastAdvancedAnalyticsUpdate, 600.0) < 60.0) // Every 10 minutes
    {
        GeneratePerformanceReport();
    }
}

TArray<FString> UTGAdvancedTerritorialProgressionSubsystem::DetectBalanceAnomalies()
{
    TArray<FString> Anomalies;
    
    if (!ResourceAnalytics || !BaseProgressionSubsystem)
    {
        Anomalies.Add(TEXT("Unable to detect anomalies - required subsystems not available"));
        return Anomalies;
    }

    // Check faction dominance
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    TMap<int32, int32> FactionTerritoryCount;
    
    for (int32 FactionId : AllFactionIds)
    {
        FTGFactionProgressionData ProgressionData = BaseProgressionSubsystem->GetFactionProgression(FactionId);
        FactionTerritoryCount.Add(FactionId, ProgressionData.TerritoriesControlled);
    }
    
    // Find dominant and weak factions
    int32 MaxTerritories = 0;
    int32 DominantFaction = 0;
    int32 WeakFactionsCount = 0;
    
    for (const auto& CountPair : FactionTerritoryCount)
    {
        if (CountPair.Value > MaxTerritories)
        {
            MaxTerritories = CountPair.Value;
            DominantFaction = CountPair.Key;
        }
        
        if (CountPair.Value <= 1)
        {
            WeakFactionsCount++;
        }
    }
    
    // Detect domination anomaly
    float AverageTerritories = (float)MaxTerritories * 7.0f / 7.0f; // Total territories / 7 factions
    if (MaxTerritories > AverageTerritories * 2.0f)
    {
        Anomalies.Add(FString::Printf(TEXT("DOMINANCE ANOMALY: Faction %d controls %d territories (%.1fx average)"), 
                      DominantFaction, MaxTerritories, MaxTerritories / AverageTerritories));
    }
    
    // Detect weakness anomaly
    if (WeakFactionsCount >= 3)
    {
        Anomalies.Add(FString::Printf(TEXT("WEAKNESS ANOMALY: %d factions control ≤1 territory"), WeakFactionsCount));
    }
    
    // Check resource market anomalies
    for (const auto& MetricsPair : ResourceMarketMetrics)
    {
        ETerritoryResourceType ResourceType = MetricsPair.Key;
        const FTGTerritorialResourceMetrics& Metrics = MetricsPair.Value;
        
        if (Metrics.MarketValue > 2.5f)
        {
            Anomalies.Add(FString::Printf(TEXT("MARKET ANOMALY: %s resources severely overvalued (%.2fx normal)"), 
                          *UEnum::GetValueAsString(ResourceType), Metrics.MarketValue));
        }
        
        if (Metrics.CompetitionIntensity > 0.8f)
        {
            Anomalies.Add(FString::Printf(TEXT("COMPETITION ANOMALY: %s resources heavily contested (%.1f%%)"), 
                          *UEnum::GetValueAsString(ResourceType), Metrics.CompetitionIntensity * 100.0f));
        }
    }
    
    return Anomalies;
}

void UTGAdvancedTerritorialProgressionSubsystem::TriggerEmergencyBalanceAdjustment(FString Reason)
{
    UE_LOG(LogTemp, Error, TEXT("UTGAdvancedTerritorialProgressionSubsystem: EMERGENCY BALANCE ADJUSTMENT: %s"), *Reason);
    
    bEmergencyBalanceMode = true;
    LastEmergencyAdjustment = FDateTime::Now();
    
    // Apply emergency balance corrections
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    
    for (int32 FactionId : AllFactionIds)
    {
        FTGFactionTerritorialPerformance Performance = AnalyzeFactionPerformance(FactionId);
        
        // Boost weak factions significantly
        if (Performance.TerritorialWinRate < 0.15f)
        {
            const TArray<ETerritoryResourceType> ResourceTypes = {
                ETerritoryResourceType::Industrial,
                ETerritoryResourceType::Military,
                ETerritoryResourceType::Research,
                ETerritoryResourceType::Economic,
                ETerritoryResourceType::Strategic
            };
            
            for (ETerritoryResourceType ResourceType : ResourceTypes)
            {
                UpdateResourceBonusWithAnalytics(FactionId, ResourceType, 1.5f, 0.8f); // 50% emergency boost
            }
            
            UE_LOG(LogTemp, Warning, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Applied emergency boost to faction %d (Win Rate: %.2f)"), 
                   FactionId, Performance.TerritorialWinRate);
        }
        // Reduce dominant factions moderately
        else if (Performance.TerritorialWinRate > 0.75f)
        {
            const TArray<ETerritoryResourceType> ResourceTypes = {
                ETerritoryResourceType::Industrial,
                ETerritoryResourceType::Military,
                ETerritoryResourceType::Research,
                ETerritoryResourceType::Economic,
                ETerritoryResourceType::Strategic
            };
            
            for (ETerritoryResourceType ResourceType : ResourceTypes)
            {
                UpdateResourceBonusWithAnalytics(FactionId, ResourceType, 0.85f, 0.9f); // 15% emergency reduction
            }
            
            UE_LOG(LogTemp, Warning, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Applied emergency reduction to faction %d (Win Rate: %.2f)"), 
                   FactionId, Performance.TerritorialWinRate);
        }
    }
    
    // Schedule emergency mode exit
    if (UWorld* World = GetGameInstance()->GetWorld())
    {
        World->GetTimerManager().SetTimerForNextTick([this]()
        {
            bEmergencyBalanceMode = false;
        });
    }
}

// Core Processing Functions
void UTGAdvancedTerritorialProgressionSubsystem::ProcessAdvancedAnalytics()
{
    const double StartTime = FPlatformTime::Seconds();
    
    // Update resource market metrics
    UpdateResourceMarketMetrics();
    
    // Analyze faction synergies
    AnalyzeFactionSynergies();
    
    // Update predictive models
    UpdatePredictiveModels();
    
    // Update performance cache
    UpdatePerformanceCache();
    
    // Optimize memory usage
    OptimizeAdvancedAnalyticsMemory();
    
    const double EndTime = FPlatformTime::Seconds();
    double ProcessingTime = (EndTime - StartTime) * 1000.0; // Convert to milliseconds
    
    LastAdvancedAnalyticsUpdate = EndTime;
    
    UE_LOG(LogTemp, VeryVerbose, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Advanced analytics processed in %.2fms"), ProcessingTime);
}

// Utility Functions
float UTGAdvancedTerritorialProgressionSubsystem::CalculateTerritorySynergyScore(int32 FactionId1, int32 FactionId2)
{
    // Simplified synergy calculation based on faction characteristics
    // In production, this would use machine learning models trained on historical data
    
    // Faction synergy matrix (symmetric)
    TMap<int32, TMap<int32, float>> SynergyMatrix = {
        {1, {{2, 0.3f}, {3, 0.1f}, {4, 0.2f}, {5, 0.6f}, {6, 0.4f}, {7, 0.3f}}}, // Directorate
        {2, {{1, 0.3f}, {3, 0.7f}, {4, 0.5f}, {5, 0.2f}, {6, 0.4f}, {7, 0.8f}}}, // Free77
        {3, {{1, 0.1f}, {2, 0.7f}, {4, 0.4f}, {5, 0.3f}, {6, 0.8f}, {7, 0.6f}}}, // NomadClans
        {4, {{1, 0.2f}, {2, 0.5f}, {3, 0.4f}, {5, 0.7f}, {6, 0.3f}, {7, 0.7f}}}, // VulturesUnion
        {5, {{1, 0.6f}, {2, 0.2f}, {3, 0.3f}, {4, 0.7f}, {6, 0.1f}, {7, 0.4f}}}, // CorporateCombine
        {6, {{1, 0.4f}, {2, 0.4f}, {3, 0.8f}, {4, 0.3f}, {5, 0.1f}, {7, 0.5f}}}, // Bloom
        {7, {{1, 0.3f}, {2, 0.8f}, {3, 0.6f}, {4, 0.7f}, {5, 0.4f}, {6, 0.5f}}}  // Independent
    };
    
    if (const TMap<int32, float>* Faction1Synergies = SynergyMatrix.Find(FactionId1))
    {
        if (const float* SynergyScore = Faction1Synergies->Find(FactionId2))
        {
            return *SynergyScore;
        }
    }
    
    return 0.0f; // No synergy data available
}

void UTGAdvancedTerritorialProgressionSubsystem::AnalyzeFactionSynergies()
{
    // Analyze current territorial positions for synergy opportunities
    if (!TerritorialManager)
    {
        return;
    }
    
    TArray<FTGTerritoryData> AllTerritories = TerritorialManager->GetAllTerritories();
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    
    // Find adjacent faction pairs
    for (int32 i = 0; i < AllFactionIds.Num(); ++i)
    {
        for (int32 j = i + 1; j < AllFactionIds.Num(); ++j)
        {
            int32 FactionId1 = AllFactionIds[i];
            int32 FactionId2 = AllFactionIds[j];
            
            // Check for territorial adjacency
            bool bAreAdjacent = false;
            for (const FTGTerritoryData& Territory1 : AllTerritories)
            {
                if (Territory1.CurrentControllerFactionId == FactionId1)
                {
                    TArray<FTGTerritoryData> NearbyTerritories = TerritorialManager->GetTerritoriesInRadius(
                        Territory1.Bounds.CenterPoint, Territory1.Bounds.InfluenceRadius + 1000.0f);
                        
                    for (const FTGTerritoryData& Territory2 : NearbyTerritories)
                    {
                        if (Territory2.CurrentControllerFactionId == FactionId2)
                        {
                            bAreAdjacent = true;
                            break;
                        }
                    }
                    
                    if (bAreAdjacent) break;
                }
            }
            
            if (bAreAdjacent)
            {
                float SynergyScore = CalculateTerritorySynergyScore(FactionId1, FactionId2);
                if (SynergyScore > MinSynergyThreshold)
                {
                    FString SynergyType = SynergyScore > 0.7f ? TEXT("Strong") : (SynergyScore > 0.4f ? TEXT("Moderate") : TEXT("Weak"));
                    OnFactionSynergyDetected.Broadcast(FactionId1, FactionId2, SynergyScore, SynergyType);
                }
            }
        }
    }
}

void UTGAdvancedTerritorialProgressionSubsystem::UpdatePredictiveModels()
{
    // Update predictive models with latest data
    // In production, this would train/update machine learning models
    
    // For now, we'll update the faction performance cache which serves as our "model"
    GeneratePerformanceReport();
}

void UTGAdvancedTerritorialProgressionSubsystem::UpdatePerformanceCache()
{
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    
    for (int32 FactionId : AllFactionIds)
    {
        FTGFactionTerritorialPerformance Performance = AnalyzeFactionPerformance(FactionId);
        FactionPerformanceCache.Add(FactionId, Performance);
    }
}

void UTGAdvancedTerritorialProgressionSubsystem::DetectAndCorrectImbalances()
{
    TArray<FString> Anomalies = DetectBalanceAnomalies();
    
    if (Anomalies.Num() > 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Detected %d balance anomalies - applying corrections"), Anomalies.Num());
        
        // Apply gradual balance corrections
        const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
        
        for (int32 FactionId : AllFactionIds)
        {
            FTGFactionTerritorialPerformance Performance = AnalyzeFactionPerformance(FactionId);
            
            // Apply moderate corrections based on performance
            if (Performance.TerritorialWinRate < 0.3f)
            {
                // Boost underperforming factions
                const TArray<ETerritoryResourceType> ResourceTypes = {
                    ETerritoryResourceType::Industrial,
                    ETerritoryResourceType::Military,
                    ETerritoryResourceType::Research,
                    ETerritoryResourceType::Economic,
                    ETerritoryResourceType::Strategic
                };
                
                for (ETerritoryResourceType ResourceType : ResourceTypes)
                {
                    float CurrentMultiplier = GetAnalyticsAdjustedResourceBonus(FactionId, ResourceType) / 100.0f;
                    float NewMultiplier = FMath::Min(CurrentMultiplier * 1.05f, CurrentMultiplier + MaxAutoAdjustment);
                    UpdateResourceBonusWithAnalytics(FactionId, ResourceType, NewMultiplier, 0.85f);
                }
            }
            else if (Performance.TerritorialWinRate > 0.7f)
            {
                // Slightly reduce overperforming factions
                const TArray<ETerritoryResourceType> ResourceTypes = {
                    ETerritoryResourceType::Industrial,
                    ETerritoryResourceType::Military,
                    ETerritoryResourceType::Research,
                    ETerritoryResourceType::Economic,
                    ETerritoryResourceType::Strategic
                };
                
                for (ETerritoryResourceType ResourceType : ResourceTypes)
                {
                    float CurrentMultiplier = GetAnalyticsAdjustedResourceBonus(FactionId, ResourceType) / 100.0f;
                    float NewMultiplier = FMath::Max(CurrentMultiplier * 0.98f, CurrentMultiplier - (MaxAutoAdjustment * 0.5f));
                    UpdateResourceBonusWithAnalytics(FactionId, ResourceType, NewMultiplier, 0.9f);
                }
            }
        }
    }
}

void UTGAdvancedTerritorialProgressionSubsystem::OptimizeAdvancedAnalyticsMemory()
{
    // Clean up old test data
    const FDateTime CutoffTime = FDateTime::Now() - FTimespan::FromHours(24);
    
    // Remove old player test assignments (simplified cleanup)
    if (PlayerTestAssignments.Num() > 5000) // Keep reasonable size
    {
        PlayerTestAssignments.Empty(1000);
    }
    
    // Trim balance history if too large
    if (BalanceHistoryBuffer.Num() > MaxBalanceHistorySize)
    {
        int32 ExcessCount = BalanceHistoryBuffer.Num() - MaxBalanceHistorySize;
        BalanceHistoryBuffer.RemoveAt(0, ExcessCount);
    }
}

// Initialization Functions
void UTGAdvancedTerritorialProgressionSubsystem::InitializeAdvancedResourceBonuses()
{
    const TArray<int32> AllFactionIds = {1, 2, 3, 4, 5, 6, 7};
    const TArray<ETerritoryResourceType> ResourceTypes = {
        ETerritoryResourceType::Industrial,
        ETerritoryResourceType::Military,
        ETerritoryResourceType::Research,
        ETerritoryResourceType::Economic,
        ETerritoryResourceType::Strategic
    };
    
    // Initialize default advanced resource bonuses
    for (int32 FactionId : AllFactionIds)
    {
        TMap<ETerritoryResourceType, FTGAdvancedResourceBonus>& FactionBonuses = FactionResourceBonuses.Add(FactionId);
        
        for (ETerritoryResourceType ResourceType : ResourceTypes)
        {
            FTGAdvancedResourceBonus& ResourceBonus = FactionBonuses.Add(ResourceType);
            ResourceBonus.BaseValue = 100.0f; // Standard baseline
            ResourceBonus.AnalyticalMultiplier = 1.0f; // No adjustment initially
            ResourceBonus.ConfidenceLevel = 0.8f; // Moderate initial confidence
            ResourceBonus.BonusType = ETerritorialBonusType::Dynamic; // Enable analytics
            ResourceBonus.DecayRate = 0.01f; // 1% decay per hour
            ResourceBonus.MinDecayValue = 0.7f; // Don't decay below 70%
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Initialized advanced resource bonuses for %d factions x %d resource types"), 
           AllFactionIds.Num(), ResourceTypes.Num());
}

void UTGAdvancedTerritorialProgressionSubsystem::InitializeMarketMetrics()
{
    const TArray<ETerritoryResourceType> ResourceTypes = {
        ETerritoryResourceType::Industrial,
        ETerritoryResourceType::Military,
        ETerritoryResourceType::Research,
        ETerritoryResourceType::Economic,
        ETerritoryResourceType::Strategic
    };
    
    for (ETerritoryResourceType ResourceType : ResourceTypes)
    {
        FTGTerritorialResourceMetrics& Metrics = ResourceMarketMetrics.Add(ResourceType);
        
        // Initialize with baseline values
        Metrics.GenerationRate = 100.0f;
        Metrics.Efficiency = 1.0f;
        Metrics.MarketValue = 1.0f;
        Metrics.ScarcityMultiplier = 1.0f;
        Metrics.StrategicImportance = 5.0f;
        Metrics.CompetitionIntensity = 0.3f; // Moderate baseline competition
    }
    
    UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Initialized market metrics for %d resource types"), ResourceTypes.Num());
}

void UTGAdvancedTerritorialProgressionSubsystem::LoadAdvancedHistoricalData()
{
    // In production, this would load historical balance data, test results, and model parameters
    // For now, initialize with reasonable baseline values
    
    // Initialize balance history with neutral values
    for (int32 i = 0; i < 20; ++i)
    {
        BalanceHistoryBuffer.Add(0.7f); // Baseline 70% balance
    }
    
    UE_LOG(LogTemp, Log, TEXT("UTGAdvancedTerritorialProgressionSubsystem: Loaded historical data - Balance history: %d entries"), BalanceHistoryBuffer.Num());
}