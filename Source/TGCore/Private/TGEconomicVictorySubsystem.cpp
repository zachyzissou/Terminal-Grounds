#include "TGEconomicVictorySubsystem.h"
#include "TGWorld/Public/Economy/TGConvoyEconomySubsystem.h"
#include "TGTerritorial/Public/TerritorialManager.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"

void UTGEconomicVictorySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // Get references to other subsystems
    ConvoyEconomySubsystem = GetWorld()->GetSubsystem<UTGConvoyEconomySubsystem>();
    
    // Initialize default victory conditions
    InitializeDefaultVictoryConditions();
    
    // Reset session state
    SessionStartTime = GetWorld()->GetTimeSeconds();
    LastVictoryCheck = 0.0f;
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Subsystem initialized"));
}

void UTGEconomicVictorySubsystem::Deinitialize()
{
    EndEconomicVictorySession();
    VictoryConditions.Empty();
    VictoryProgress.Empty();
    FactionMetrics.Empty();
    
    Super::Deinitialize();
}

bool UTGEconomicVictorySubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
    return Super::ShouldCreateSubsystem(Outer);
}

void UTGEconomicVictorySubsystem::Tick(float DeltaTime)
{
    if (!bEconomicVictoryEnabled)
    {
        return;
    }
    
    float CurrentTime = GetWorld()->GetTimeSeconds();
    
    // Check victory conditions at regular intervals
    if (CurrentTime - LastVictoryCheck >= VictoryCheckInterval)
    {
        EvaluateVictoryConditions();
        LastVictoryCheck = CurrentTime;
    }
    
    // Update victory progress timers
    UpdateVictoryProgress(DeltaTime);
}

void UTGEconomicVictorySubsystem::RegisterVictoryCondition(const FEconomicVictoryCondition& Condition)
{
    if (!ValidateVictoryCondition(Condition))
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid victory condition: %s"), *Condition.ConditionName);
        return;
    }
    
    // Remove existing condition of same type
    VictoryConditions.RemoveAll([&Condition](const FEconomicVictoryCondition& Existing) {
        return Existing.VictoryType == Condition.VictoryType;
    });
    
    // Add new condition
    VictoryConditions.Add(Condition);
    
    // Sort by priority
    VictoryConditions.Sort([](const FEconomicVictoryCondition& A, const FEconomicVictoryCondition& B) {
        return A.Priority < B.Priority;
    });
    
    UE_LOG(LogTemp, Log, TEXT("Registered victory condition: %s"), *Condition.ConditionName);
}

void UTGEconomicVictorySubsystem::RemoveVictoryCondition(EEconomicVictoryType VictoryType)
{
    int32 RemovedCount = VictoryConditions.RemoveAll([VictoryType](const FEconomicVictoryCondition& Condition) {
        return Condition.VictoryType == VictoryType;
    });
    
    if (RemovedCount > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Removed victory condition of type: %d"), (int32)VictoryType);
    }
}

void UTGEconomicVictorySubsystem::SetVictoryConditionActive(EEconomicVictoryType VictoryType, bool bActive)
{
    for (FEconomicVictoryCondition& Condition : VictoryConditions)
    {
        if (Condition.VictoryType == VictoryType)
        {
            Condition.bActiveCondition = bActive;
            UE_LOG(LogTemp, Log, TEXT("Set victory condition %d active: %s"), (int32)VictoryType, bActive ? TEXT("true") : TEXT("false"));
            break;
        }
    }
}

TArray<FEconomicVictoryCondition> UTGEconomicVictorySubsystem::GetActiveVictoryConditions() const
{
    TArray<FEconomicVictoryCondition> ActiveConditions;
    
    for (const FEconomicVictoryCondition& Condition : VictoryConditions)
    {
        if (Condition.bActiveCondition)
        {
            ActiveConditions.Add(Condition);
        }
    }
    
    return ActiveConditions;
}

FEconomicVictoryProgress UTGEconomicVictorySubsystem::GetFactionVictoryProgress(int32 FactionID, EEconomicVictoryType VictoryType) const
{
    FString ProgressKey = GenerateProgressKey(FactionID, VictoryType);
    
    if (const FEconomicVictoryProgress* Progress = VictoryProgress.Find(ProgressKey))
    {
        return *Progress;
    }
    
    // Return default progress
    FEconomicVictoryProgress DefaultProgress;
    DefaultProgress.FactionID = FactionID;
    DefaultProgress.VictoryType = VictoryType;
    return DefaultProgress;
}

TArray<FEconomicVictoryProgress> UTGEconomicVictorySubsystem::GetAllVictoryProgress() const
{
    TArray<FEconomicVictoryProgress> AllProgress;
    
    for (const auto& ProgressPair : VictoryProgress)
    {
        AllProgress.Add(ProgressPair.Value);
    }
    
    // Sort by progress descending
    AllProgress.Sort([](const FEconomicVictoryProgress& A, const FEconomicVictoryProgress& B) {
        return A.Progress > B.Progress;
    });
    
    return AllProgress;
}

FEconomicVictoryProgress UTGEconomicVictorySubsystem::GetClosestVictoryToCompletion() const
{
    FEconomicVictoryProgress ClosestVictory;
    float HighestProgress = 0.0f;
    
    for (const auto& ProgressPair : VictoryProgress)
    {
        const FEconomicVictoryProgress& Progress = ProgressPair.Value;
        if (Progress.Progress > HighestProgress && Progress.Status == EEconomicVictoryStatus::InProgress)
        {
            HighestProgress = Progress.Progress;
            ClosestVictory = Progress;
        }
    }
    
    return ClosestVictory;
}

FEconomicMetrics UTGEconomicVictorySubsystem::GetFactionEconomicMetrics(int32 FactionID) const
{
    if (const FEconomicMetrics* Metrics = FactionMetrics.Find(FactionID))
    {
        return *Metrics;
    }
    
    return FEconomicMetrics();
}

void UTGEconomicVictorySubsystem::UpdateEconomicMetrics(int32 FactionID)
{
    if (!ConvoyEconomySubsystem)
    {
        return;
    }
    
    FEconomicMetrics Metrics;
    
    // Get all convoy routes
    TArray<FConvoyRoute> AllRoutes = ConvoyEconomySubsystem->GetAllRoutes();
    TArray<FConvoyRoute> FactionRoutes = ConvoyEconomySubsystem->GetRoutesByFaction(FactionID);
    
    // Calculate basic route control
    Metrics.TotalRoutes = AllRoutes.Num();
    Metrics.ControlledRoutes = FactionRoutes.Num();
    
    // Calculate route values
    float TotalValue = 0.0f;
    float ControlledValue = 0.0f;
    
    for (const FConvoyRoute& Route : AllRoutes)
    {
        float RouteValue = Route.BaseIntegrityImpact * Route.DifficultyMultiplier;
        TotalValue += RouteValue;
        
        if (Route.FactionControllerID == FactionID)
        {
            ControlledValue += RouteValue;
        }
    }
    
    Metrics.TotalRouteValue = TotalValue;
    Metrics.ControlledRouteValue = ControlledValue;
    Metrics.RouteControlPercentage = TotalValue > 0.0f ? (ControlledValue / TotalValue) : 0.0f;
    
    // Calculate resource control percentages
    for (int32 ResourceIndex = 0; ResourceIndex < (int32)EResourceType::Personnel + 1; ResourceIndex++)
    {
        EResourceType ResourceType = (EResourceType)ResourceIndex;
        float ResourceControl = GetRouteControlPercentage(FactionID, ResourceType);
        Metrics.ResourceControlPercentage.Add(ResourceType, ResourceControl);
    }
    
    // Calculate network connectivity
    Metrics.NetworkConnectivity = CalculateNetworkConnectivity(FactionID);
    
    // Calculate enemy economic output impact
    TArray<int32> AllFactionIDs = {0, 1, 2, 3, 4, 5, 6}; // Assuming 7 factions
    for (int32 EnemyFactionID : AllFactionIDs)
    {
        if (EnemyFactionID != FactionID)
        {
            float EconomicOutput = CalculateEconomicOutput(EnemyFactionID);
            Metrics.EnemyEconomicOutput.Add(EnemyFactionID, EconomicOutput);
        }
    }
    
    // Store updated metrics
    FactionMetrics.Add(FactionID, Metrics);
    
    // Broadcast update
    OnEconomicMetricsUpdated.Broadcast(FactionID, Metrics);
}

float UTGEconomicVictorySubsystem::GetRouteControlPercentage(int32 FactionID, EResourceType ResourceType) const
{
    if (!ConvoyEconomySubsystem)
    {
        return 0.0f;
    }
    
    TArray<FConvoyRoute> AllRoutes = ConvoyEconomySubsystem->GetAllRoutes();
    
    float TotalResourceRoutes = 0.0f;
    float ControlledResourceRoutes = 0.0f;
    
    for (const FConvoyRoute& Route : AllRoutes)
    {
        // For now, consider all routes as supply routes
        // In a more advanced system, routes would have specific resource types
        TotalResourceRoutes += 1.0f;
        
        if (Route.FactionControllerID == FactionID)
        {
            ControlledResourceRoutes += 1.0f;
        }
    }
    
    return TotalResourceRoutes > 0.0f ? (ControlledResourceRoutes / TotalResourceRoutes) : 0.0f;
}

void UTGEconomicVictorySubsystem::EvaluateVictoryConditions()
{
    TArray<int32> ActiveFactions = {0, 1, 2, 3, 4, 5, 6}; // Assuming 7 factions
    
    for (int32 FactionID : ActiveFactions)
    {
        // Update economic metrics for this faction
        UpdateEconomicMetrics(FactionID);
        
        // Check each victory condition
        for (const FEconomicVictoryCondition& Condition : VictoryConditions)
        {
            if (!Condition.bActiveCondition)
            {
                continue;
            }
            
            bool bConditionMet = CheckVictoryCondition(FactionID, Condition);
            FString ProgressKey = GenerateProgressKey(FactionID, Condition.VictoryType);
            
            // Get or create progress tracking
            FEconomicVictoryProgress* Progress = VictoryProgress.Find(ProgressKey);
            if (!Progress)
            {
                FEconomicVictoryProgress NewProgress;
                NewProgress.FactionID = FactionID;
                NewProgress.VictoryType = Condition.VictoryType;
                VictoryProgress.Add(ProgressKey, NewProgress);
                Progress = &VictoryProgress[ProgressKey];
            }
            
            // Calculate current progress
            float NewProgress = 0.0f;
            switch (Condition.VictoryType)
            {
                case EEconomicVictoryType::EconomicDominance:
                    NewProgress = CalculateEconomicDominance(FactionID);
                    break;
                case EEconomicVictoryType::SupplyMonopoly:
                    NewProgress = CalculateSupplyMonopoly(FactionID, Condition.TargetResourceType);
                    break;
                case EEconomicVictoryType::EconomicCollapse:
                    NewProgress = CalculateEconomicCollapse(FactionID, Condition.TargetFactions);
                    break;
                case EEconomicVictoryType::TradeNetwork:
                    NewProgress = CalculateTradeNetwork(FactionID);
                    break;
                case EEconomicVictoryType::ResourceControl:
                    NewProgress = CalculateResourceControl(FactionID, Condition.TargetResourceType);
                    break;
                case EEconomicVictoryType::ConvoySupremacy:
                    NewProgress = CalculateConvoySupremacy(FactionID);
                    break;
            }
            
            // Update progress
            Progress->Progress = NewProgress;
            Progress->LastUpdateTime = GetWorld()->GetTimeSeconds();
            
            // Update status based on progress
            if (NewProgress >= Condition.RequiredThreshold)
            {
                if (Condition.TimeRequirement > 0.0f)
                {
                    Progress->TimeHeld += VictoryCheckInterval;
                    Progress->Status = EEconomicVictoryStatus::NearComplete;
                    
                    if (Progress->TimeHeld >= Condition.TimeRequirement)
                    {
                        Progress->Status = EEconomicVictoryStatus::Completed;
                        TriggerEconomicVictory(FactionID, Condition.VictoryType);
                    }
                }
                else
                {
                    Progress->Status = EEconomicVictoryStatus::Completed;
                    TriggerEconomicVictory(FactionID, Condition.VictoryType);
                }
            }
            else
            {
                Progress->TimeHeld = 0.0f;
                Progress->Status = NewProgress > 0.0f ? EEconomicVictoryStatus::InProgress : EEconomicVictoryStatus::NotStarted;
            }
            
            // Check for camping prevention
            if (bPreventEconomicCamping && Progress->Progress > MinimumEngagementThreshold)
            {
                CheckForEconomicCamping(FactionID);
            }
            
            // Broadcast progress updates
            OnEconomicVictoryProgress.Broadcast(FactionID, Condition.VictoryType, NewProgress);
            
            // Check for threat warnings
            if (NewProgress >= ThreatWarningThreshold && Progress->Status != EEconomicVictoryStatus::Completed)
            {
                float EstimatedTimeToVictory = Condition.TimeRequirement - Progress->TimeHeld;
                OnEconomicVictoryThreatened.Broadcast(FactionID, Condition.VictoryType, EstimatedTimeToVictory);
            }
        }
    }
}

bool UTGEconomicVictorySubsystem::CheckVictoryCondition(int32 FactionID, const FEconomicVictoryCondition& Condition) const
{
    float Progress = 0.0f;
    
    switch (Condition.VictoryType)
    {
        case EEconomicVictoryType::EconomicDominance:
            Progress = CalculateEconomicDominance(FactionID);
            break;
        case EEconomicVictoryType::SupplyMonopoly:
            Progress = CalculateSupplyMonopoly(FactionID, Condition.TargetResourceType);
            break;
        case EEconomicVictoryType::EconomicCollapse:
            Progress = CalculateEconomicCollapse(FactionID, Condition.TargetFactions);
            break;
        case EEconomicVictoryType::TradeNetwork:
            Progress = CalculateTradeNetwork(FactionID);
            break;
        case EEconomicVictoryType::ResourceControl:
            Progress = CalculateResourceControl(FactionID, Condition.TargetResourceType);
            break;
        case EEconomicVictoryType::ConvoySupremacy:
            Progress = CalculateConvoySupremacy(FactionID);
            break;
    }
    
    return Progress >= Condition.RequiredThreshold;
}

void UTGEconomicVictorySubsystem::TriggerEconomicVictory(int32 FactionID, EEconomicVictoryType VictoryType)
{
    float CompletionTime = GetWorld()->GetTimeSeconds() - SessionStartTime;
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Achieved! Faction %d achieved %s victory in %.2f seconds"), 
           FactionID, *UEnum::GetValueAsString(VictoryType), CompletionTime);
    
    // Broadcast victory achievement
    OnEconomicVictoryAchieved.Broadcast(FactionID, VictoryType, CompletionTime);
    
    // End the session
    EndEconomicVictorySession();
}

TArray<FString> UTGEconomicVictorySubsystem::GetCounterStrategies(EEconomicVictoryType VictoryType) const
{
    TArray<FString> Strategies;
    
    switch (VictoryType)
    {
        case EEconomicVictoryType::EconomicDominance:
            Strategies.Add(TEXT("Raid enemy convoy routes to reduce their economic output"));
            Strategies.Add(TEXT("Form alliance to share resources and counter dominance"));
            Strategies.Add(TEXT("Focus on territorial control to gain route bonuses"));
            break;
            
        case EEconomicVictoryType::SupplyMonopoly:
            Strategies.Add(TEXT("Capture alternative supply routes"));
            Strategies.Add(TEXT("Sabotage monopolized supply lines"));
            Strategies.Add(TEXT("Develop independent resource production"));
            break;
            
        case EEconomicVictoryType::EconomicCollapse:
            Strategies.Add(TEXT("Establish protected supply corridors"));
            Strategies.Add(TEXT("Diversify economic dependencies"));
            Strategies.Add(TEXT("Counter-attack enemy economic infrastructure"));
            break;
            
        case EEconomicVictoryType::TradeNetwork:
            Strategies.Add(TEXT("Disrupt key network nodes"));
            Strategies.Add(TEXT("Create competing trade networks"));
            Strategies.Add(TEXT("Target network connection points"));
            break;
            
        case EEconomicVictoryType::ResourceControl:
            Strategies.Add(TEXT("Develop alternative resource sources"));
            Strategies.Add(TEXT("Sabotage resource extraction facilities"));
            Strategies.Add(TEXT("Form coalition to break resource monopoly"));
            break;
            
        case EEconomicVictoryType::ConvoySupremacy:
            Strategies.Add(TEXT("Focus on convoy interception and disruption"));
            Strategies.Add(TEXT("Develop fast strike teams for convoy raids"));
            Strategies.Add(TEXT("Create decoy convoys to confuse enemy"));
            break;
    }
    
    return Strategies;
}

void UTGEconomicVictorySubsystem::ApplyCounterStrategy(int32 FactionID, EEconomicVictoryType TargetVictoryType, const FString& Strategy)
{
    UE_LOG(LogTemp, Log, TEXT("Faction %d applying counter-strategy against %s: %s"), 
           FactionID, *UEnum::GetValueAsString(TargetVictoryType), *Strategy);
    
    // This would integrate with other gameplay systems to actually apply the strategy effects
    // For now, we just log the action
}

void UTGEconomicVictorySubsystem::StartEconomicVictorySession()
{
    bEconomicVictoryEnabled = true;
    SessionStartTime = GetWorld()->GetTimeSeconds();
    LastVictoryCheck = 0.0f;
    
    // Clear previous session data
    VictoryProgress.Empty();
    FactionMetrics.Empty();
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Session Started"));
}

void UTGEconomicVictorySubsystem::EndEconomicVictorySession()
{
    bEconomicVictoryEnabled = false;
    
    UE_LOG(LogTemp, Log, TEXT("Economic Victory Session Ended"));
}

void UTGEconomicVictorySubsystem::InitializeDefaultVictoryConditions()
{
    // Economic Dominance - Control 75% of total convoy route value
    FEconomicVictoryCondition EconomicDominance;
    EconomicDominance.VictoryType = EEconomicVictoryType::EconomicDominance;
    EconomicDominance.ConditionName = TEXT("Economic Dominance");
    EconomicDominance.Description = TEXT("Control 75% of total convoy route economic value");
    EconomicDominance.RequiredThreshold = 0.75f;
    EconomicDominance.TimeRequirement = 120.0f; // Hold for 2 minutes
    EconomicDominance.Priority = 1;
    RegisterVictoryCondition(EconomicDominance);
    
    // Supply Monopoly - Control all routes of a specific resource type
    FEconomicVictoryCondition SupplyMonopoly;
    SupplyMonopoly.VictoryType = EEconomicVictoryType::SupplyMonopoly;
    SupplyMonopoly.ConditionName = TEXT("Supply Monopoly");
    SupplyMonopoly.Description = TEXT("Control all convoy routes of a specific resource type");
    SupplyMonopoly.RequiredThreshold = 1.0f; // 100% control
    SupplyMonopoly.TimeRequirement = 180.0f; // Hold for 3 minutes
    SupplyMonopoly.TargetResourceType = EResourceType::Supplies;
    SupplyMonopoly.Priority = 2;
    RegisterVictoryCondition(SupplyMonopoly);
    
    // Economic Collapse - Reduce enemy economic output by 60%
    FEconomicVictoryCondition EconomicCollapse;
    EconomicCollapse.VictoryType = EEconomicVictoryType::EconomicCollapse;
    EconomicCollapse.ConditionName = TEXT("Economic Collapse");
    EconomicCollapse.Description = TEXT("Reduce enemy faction economic output by 60%");
    EconomicCollapse.RequiredThreshold = 0.6f;
    EconomicCollapse.TimeRequirement = 90.0f; // Hold for 1.5 minutes
    EconomicCollapse.Priority = 3;
    RegisterVictoryCondition(EconomicCollapse);
    
    // Trade Network - Establish profitable routes across 5 territories
    FEconomicVictoryCondition TradeNetwork;
    TradeNetwork.VictoryType = EEconomicVictoryType::TradeNetwork;
    TradeNetwork.ConditionName = TEXT("Trade Network");
    TradeNetwork.Description = TEXT("Establish profitable trade routes across 5 territories");
    TradeNetwork.RequiredThreshold = 0.8f; // 80% network connectivity
    TradeNetwork.RequiredTerritories = 5;
    TradeNetwork.TimeRequirement = 150.0f; // Hold for 2.5 minutes
    TradeNetwork.Priority = 4;
    RegisterVictoryCondition(TradeNetwork);
}

void UTGEconomicVictorySubsystem::UpdateVictoryProgress(float DeltaTime)
{
    // Update time-based progress tracking
    for (auto& ProgressPair : VictoryProgress)
    {
        FEconomicVictoryProgress& Progress = ProgressPair.Value;
        
        if (Progress.Status == EEconomicVictoryStatus::NearComplete)
        {
            // Time held is updated in EvaluateVictoryConditions
        }
    }
}

void UTGEconomicVictorySubsystem::CheckForEconomicCamping(int32 FactionID)
{
    // Check if faction is actively engaging in economic activities
    // This would need integration with activity tracking systems
    // For now, just log the check
    UE_LOG(LogTemp, VeryVerbose, TEXT("Checking economic camping for faction %d"), FactionID);
}

float UTGEconomicVictorySubsystem::CalculateNetworkConnectivity(int32 FactionID) const
{
    // Calculate how well connected the faction's trade routes are
    // For now, return a placeholder value based on route control
    float RouteControl = GetRouteControlPercentage(FactionID);
    return FMath::Sqrt(RouteControl); // Non-linear scaling
}

float UTGEconomicVictorySubsystem::CalculateEconomicOutput(int32 FactionID) const
{
    // Calculate the economic output of a faction
    if (!ConvoyEconomySubsystem)
    {
        return 0.0f;
    }
    
    TArray<FConvoyRoute> FactionRoutes = ConvoyEconomySubsystem->GetRoutesByFaction(FactionID);
    float TotalOutput = 0.0f;
    
    for (const FConvoyRoute& Route : FactionRoutes)
    {
        TotalOutput += Route.BaseIntegrityImpact * Route.DifficultyMultiplier;
    }
    
    // Factor in convoy system integrity
    float IntegrityIndex = ConvoyEconomySubsystem->GetIntegrityIndex();
    return TotalOutput * IntegrityIndex;
}

bool UTGEconomicVictorySubsystem::ValidateVictoryCondition(const FEconomicVictoryCondition& Condition) const
{
    // Basic validation
    if (Condition.VictoryType == EEconomicVictoryType::None)
    {
        return false;
    }
    
    if (Condition.RequiredThreshold <= 0.0f || Condition.RequiredThreshold > 1.0f)
    {
        return false;
    }
    
    if (Condition.ConditionName.IsEmpty())
    {
        return false;
    }
    
    return true;
}

FString UTGEconomicVictorySubsystem::GenerateProgressKey(int32 FactionID, EEconomicVictoryType VictoryType) const
{
    return FString::Printf(TEXT("%d_%d"), FactionID, (int32)VictoryType);
}

// Victory-specific calculation methods

float UTGEconomicVictorySubsystem::CalculateEconomicDominance(int32 FactionID) const
{
    const FEconomicMetrics* Metrics = FactionMetrics.Find(FactionID);
    if (!Metrics)
    {
        return 0.0f;
    }
    
    return Metrics->RouteControlPercentage;
}

float UTGEconomicVictorySubsystem::CalculateSupplyMonopoly(int32 FactionID, EResourceType ResourceType) const
{
    return GetRouteControlPercentage(FactionID, ResourceType);
}

float UTGEconomicVictorySubsystem::CalculateEconomicCollapse(int32 FactionID, const TArray<int32>& TargetFactions) const
{
    if (TargetFactions.Num() == 0)
    {
        return 0.0f;
    }
    
    float TotalReduction = 0.0f;
    
    for (int32 TargetFaction : TargetFactions)
    {
        float BaseOutput = CalculateEconomicOutput(TargetFaction);
        float CurrentOutput = BaseOutput; // This would need historical tracking
        
        // For now, assume reduction based on route control disruption
        float DisruptionLevel = 1.0f - GetRouteControlPercentage(TargetFaction);
        TotalReduction += DisruptionLevel;
    }
    
    return TotalReduction / TargetFactions.Num();
}

float UTGEconomicVictorySubsystem::CalculateTradeNetwork(int32 FactionID) const
{
    return CalculateNetworkConnectivity(FactionID);
}

float UTGEconomicVictorySubsystem::CalculateResourceControl(int32 FactionID, EResourceType ResourceType) const
{
    return GetRouteControlPercentage(FactionID, ResourceType);
}

float UTGEconomicVictorySubsystem::CalculateConvoySupremacy(int32 FactionID) const
{
    const FEconomicMetrics* Metrics = FactionMetrics.Find(FactionID);
    if (!Metrics)
    {
        return 0.0f;
    }
    
    // Consider both route control and network efficiency
    float RouteControl = Metrics->RouteControlPercentage;
    float NetworkEfficiency = Metrics->NetworkConnectivity;
    
    return (RouteControl * 0.7f) + (NetworkEfficiency * 0.3f);
}