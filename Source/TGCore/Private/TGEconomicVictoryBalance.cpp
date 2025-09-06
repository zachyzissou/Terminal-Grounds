#include "TGEconomicVictoryBalance.h"
#include "TGEconomicVictorySubsystem.h"

UTGEconomicVictoryBalance::UTGEconomicVictoryBalance()
{
    InitializeDefaultValues();
}

FName UTGEconomicVictoryBalance::GetCategoryName() const
{
    return TEXT("Terminal Grounds");
}

FText UTGEconomicVictoryBalance::GetSectionText() const
{
    return FText::FromString(TEXT("Economic Victory Balance"));
}

#if WITH_EDITOR
void UTGEconomicVictoryBalance::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);
    
    // Validate configuration when changed in editor
    if (!ValidateBalanceConfig())
    {
        UE_LOG(LogTemp, Warning, TEXT("Economic Victory Balance configuration has invalid values"));
    }
}
#endif

FEconomicVictoryBalanceConfig UTGEconomicVictoryBalance::GetVictoryTypeBalance(EEconomicVictoryType VictoryType) const
{
    switch (VictoryType)
    {
        case EEconomicVictoryType::EconomicDominance:
            return EconomicDominanceBalance;
        case EEconomicVictoryType::SupplyMonopoly:
            return SupplyMonopolyBalance;
        case EEconomicVictoryType::EconomicCollapse:
            return EconomicCollapseBalance;
        case EEconomicVictoryType::TradeNetwork:
            return TradeNetworkBalance;
        case EEconomicVictoryType::ResourceControl:
            return ResourceControlBalance;
        case EEconomicVictoryType::ConvoySupremacy:
            return ConvoySupremacyBalance;
        default:
            return FEconomicVictoryBalanceConfig();
    }
}

float UTGEconomicVictoryBalance::GetFactionVictoryMultiplier(int32 FactionID) const
{
    if (const float* Multiplier = FactionVictoryMultipliers.Find(FactionID))
    {
        return *Multiplier;
    }
    
    return 1.0f; // Default multiplier
}

float UTGEconomicVictoryBalance::GetResourceTypeMultiplier(EResourceType ResourceType) const
{
    if (const float* Multiplier = ResourceTypeMultipliers.Find(ResourceType))
    {
        return *Multiplier;
    }
    
    return 1.0f; // Default multiplier
}

void UTGEconomicVictoryBalance::ApplyBalanceToSubsystem(UTGEconomicVictorySubsystem* Subsystem) const
{
    if (!Subsystem)
    {
        return;
    }
    
    // Apply general settings
    Subsystem->VictoryCheckInterval = VictoryCheckInterval;
    Subsystem->ThreatWarningThreshold = ThreatWarningThreshold;
    Subsystem->bPreventEconomicCamping = AntiCampingConfig.bEnableAntiCamping;
    Subsystem->MinimumEngagementThreshold = AntiCampingConfig.MinimumEngagementThreshold;
    
    // Remove existing victory conditions and add new ones with balance settings
    Subsystem->RemoveVictoryCondition(EEconomicVictoryType::EconomicDominance);
    Subsystem->RemoveVictoryCondition(EEconomicVictoryType::SupplyMonopoly);
    Subsystem->RemoveVictoryCondition(EEconomicVictoryType::EconomicCollapse);
    Subsystem->RemoveVictoryCondition(EEconomicVictoryType::TradeNetwork);
    Subsystem->RemoveVictoryCondition(EEconomicVictoryType::ResourceControl);
    Subsystem->RemoveVictoryCondition(EEconomicVictoryType::ConvoySupremacy);
    
    // Add balanced victory conditions
    CreateBalancedVictoryCondition(Subsystem, EEconomicVictoryType::EconomicDominance, EconomicDominanceBalance);
    CreateBalancedVictoryCondition(Subsystem, EEconomicVictoryType::SupplyMonopoly, SupplyMonopolyBalance);
    CreateBalancedVictoryCondition(Subsystem, EEconomicVictoryType::EconomicCollapse, EconomicCollapseBalance);
    CreateBalancedVictoryCondition(Subsystem, EEconomicVictoryType::TradeNetwork, TradeNetworkBalance);
    CreateBalancedVictoryCondition(Subsystem, EEconomicVictoryType::ResourceControl, ResourceControlBalance);
    CreateBalancedVictoryCondition(Subsystem, EEconomicVictoryType::ConvoySupremacy, ConvoySupremacyBalance);
}

void UTGEconomicVictoryBalance::ResetToDefaults()
{
    InitializeDefaultValues();
}

bool UTGEconomicVictoryBalance::ValidateBalanceConfig() const
{
    // Validate general settings
    if (VictoryCheckInterval < 1.0f || VictoryCheckInterval > 30.0f)
    {
        return false;
    }
    
    if (ThreatWarningThreshold < 0.5f || ThreatWarningThreshold > 1.0f)
    {
        return false;
    }
    
    if (MaxSessionDuration < 300.0f || MaxSessionDuration > 7200.0f)
    {
        return false;
    }
    
    // Validate victory condition configs
    TArray<FEconomicVictoryBalanceConfig> Configs = {
        EconomicDominanceBalance,
        SupplyMonopolyBalance,
        EconomicCollapseBalance,
        TradeNetworkBalance,
        ResourceControlBalance,
        ConvoySupremacyBalance
    };
    
    for (const FEconomicVictoryBalanceConfig& Config : Configs)
    {
        if (Config.RequiredThreshold < 0.1f || Config.RequiredThreshold > 1.0f)
        {
            return false;
        }
        
        if (Config.TimeRequirement < 0.0f || Config.TimeRequirement > 600.0f)
        {
            return false;
        }
        
        if (Config.DifficultyMultiplier < 0.1f || Config.DifficultyMultiplier > 2.0f)
        {
            return false;
        }
    }
    
    // Validate faction multipliers
    for (const auto& FactionMultiplier : FactionVictoryMultipliers)
    {
        if (FactionMultiplier.Value < 0.5f || FactionMultiplier.Value > 2.0f)
        {
            return false;
        }
    }
    
    return true;
}

void UTGEconomicVictoryBalance::InitializeDefaultValues()
{
    // Initialize victory condition balance configs
    EconomicDominanceBalance = FEconomicVictoryBalanceConfig();
    EconomicDominanceBalance.RequiredThreshold = 0.75f;
    EconomicDominanceBalance.TimeRequirement = 120.0f;
    EconomicDominanceBalance.Priority = 1;
    EconomicDominanceBalance.bEnabled = true;
    EconomicDominanceBalance.Description = TEXT("Control 75% of total convoy route economic value for 2 minutes");
    EconomicDominanceBalance.DifficultyMultiplier = 1.0f;
    
    SupplyMonopolyBalance = FEconomicVictoryBalanceConfig();
    SupplyMonopolyBalance.RequiredThreshold = 1.0f;
    SupplyMonopolyBalance.TimeRequirement = 180.0f;
    SupplyMonopolyBalance.Priority = 2;
    SupplyMonopolyBalance.bEnabled = true;
    SupplyMonopolyBalance.Description = TEXT("Control all convoy routes of a specific resource type for 3 minutes");
    SupplyMonopolyBalance.DifficultyMultiplier = 1.2f;
    
    EconomicCollapseBalance = FEconomicVictoryBalanceConfig();
    EconomicCollapseBalance.RequiredThreshold = 0.6f;
    EconomicCollapseBalance.TimeRequirement = 90.0f;
    EconomicCollapseBalance.Priority = 3;
    EconomicCollapseBalance.bEnabled = true;
    EconomicCollapseBalance.Description = TEXT("Reduce enemy faction economic output by 60% for 1.5 minutes");
    EconomicCollapseBalance.DifficultyMultiplier = 0.9f;
    
    TradeNetworkBalance = FEconomicVictoryBalanceConfig();
    TradeNetworkBalance.RequiredThreshold = 0.8f;
    TradeNetworkBalance.TimeRequirement = 150.0f;
    TradeNetworkBalance.Priority = 4;
    TradeNetworkBalance.bEnabled = true;
    TradeNetworkBalance.Description = TEXT("Establish profitable trade routes across 5 territories with 80% connectivity");
    TradeNetworkBalance.DifficultyMultiplier = 1.1f;
    
    ResourceControlBalance = FEconomicVictoryBalanceConfig();
    ResourceControlBalance.RequiredThreshold = 0.85f;
    ResourceControlBalance.TimeRequirement = 120.0f;
    ResourceControlBalance.Priority = 5;
    ResourceControlBalance.bEnabled = true;
    ResourceControlBalance.Description = TEXT("Control 85% of a specific resource type for 2 minutes");
    ResourceControlBalance.DifficultyMultiplier = 1.15f;
    
    ConvoySupremacyBalance = FEconomicVictoryBalanceConfig();
    ConvoySupremacyBalance.RequiredThreshold = 0.8f;
    ConvoySupremacyBalance.TimeRequirement = 120.0f;
    ConvoySupremacyBalance.Priority = 6;
    ConvoySupremacyBalance.bEnabled = true;
    ConvoySupremacyBalance.Description = TEXT("Achieve 80% convoy operation supremacy for 2 minutes");
    ConvoySupremacyBalance.DifficultyMultiplier = 1.0f;
    
    // Initialize general settings
    VictoryCheckInterval = 5.0f;
    ThreatWarningThreshold = 0.8f;
    bAllowMultipleVictoryTypes = true;
    MaxSessionDuration = 1800.0f;
    CounterStrategyEffectiveness = 1.2f;
    CounterStrategyWindow = 30.0f;
    
    // Initialize counter-strategies
    InitializeDefaultCounterStrategies();
    
    // Initialize faction and resource multipliers
    InitializeDefaultFactionMultipliers();
    InitializeDefaultResourceMultipliers();
}

void UTGEconomicVictoryBalance::InitializeDefaultCounterStrategies()
{
    EconomicDominanceBalance.CounterStrategies = {
        TEXT("Form temporary alliances to share route control"),
        TEXT("Focus on high-value route disruption"),
        TEXT("Coordinate simultaneous raids on multiple routes"),
        TEXT("Establish defensive positions on key chokepoints")
    };
    
    SupplyMonopolyBalance.CounterStrategies = {
        TEXT("Develop alternative resource sources"),
        TEXT("Sabotage monopolized supply infrastructure"),
        TEXT("Create coalition to break monopoly control"),
        TEXT("Focus on resource stockpiling before monopoly establishes")
    };
    
    EconomicCollapseBalance.CounterStrategies = {
        TEXT("Diversify economic dependencies"),
        TEXT("Establish protected supply corridors"),
        TEXT("Counter-attack enemy economic infrastructure"),
        TEXT("Form mutual defense pacts with other factions")
    };
    
    TradeNetworkBalance.CounterStrategies = {
        TEXT("Target key network connection nodes"),
        TEXT("Establish competing trade networks"),
        TEXT("Disrupt network coordination through intelligence warfare"),
        TEXT("Control strategic territory to fragment network")
    };
    
    ResourceControlBalance.CounterStrategies = {
        TEXT("Shift focus to alternative resource types"),
        TEXT("Develop resource efficiency technologies"),
        TEXT("Form resource-sharing agreements"),
        TEXT("Target resource production facilities directly")
    };
    
    ConvoySupremacyBalance.CounterStrategies = {
        TEXT("Specialize in convoy interception tactics"),
        TEXT("Develop fast-response convoy raid teams"),
        TEXT("Use decoy convoys to confuse enemy operations"),
        TEXT("Focus on convoy route intelligence gathering")
    };
}

void UTGEconomicVictoryBalance::InitializeDefaultFactionMultipliers()
{
    // Assuming 7 factions (0-6) with different economic strengths
    FactionVictoryMultipliers.Add(0, 1.0f);  // Directorate - balanced
    FactionVictoryMultipliers.Add(1, 0.9f);  // Free77 - slightly easier (mercenary efficiency)
    FactionVictoryMultipliers.Add(2, 1.1f);  // CorporateCombine - slightly harder (bureaucracy)
    FactionVictoryMultipliers.Add(3, 1.0f);  // NomadClans - balanced
    FactionVictoryMultipliers.Add(4, 0.95f); // VulturesUnion - slightly easier (scavenging efficiency)
    FactionVictoryMultipliers.Add(5, 1.05f); // Unknown faction - slightly harder
    FactionVictoryMultipliers.Add(6, 1.0f);  // Unknown faction - balanced
}

void UTGEconomicVictoryBalance::InitializeDefaultResourceMultipliers()
{
    ResourceTypeMultipliers.Add(EResourceType::Supplies, 1.0f);      // Standard difficulty
    ResourceTypeMultipliers.Add(EResourceType::Intelligence, 1.2f);  // Harder to monopolize
    ResourceTypeMultipliers.Add(EResourceType::Technology, 1.15f);   // Moderately harder
    ResourceTypeMultipliers.Add(EResourceType::Energy, 0.95f);       // Slightly easier
    ResourceTypeMultipliers.Add(EResourceType::Materials, 1.0f);     // Standard difficulty
    ResourceTypeMultipliers.Add(EResourceType::Personnel, 1.1f);     // Moderately harder
}

void UTGEconomicVictoryBalance::CreateBalancedVictoryCondition(UTGEconomicVictorySubsystem* Subsystem, EEconomicVictoryType VictoryType, const FEconomicVictoryBalanceConfig& Balance) const
{
    if (!Balance.bEnabled)
    {
        return;
    }
    
    FEconomicVictoryCondition Condition;
    Condition.VictoryType = VictoryType;
    Condition.ConditionName = GetVictoryTypeName(VictoryType);
    Condition.Description = Balance.Description;
    Condition.RequiredThreshold = Balance.RequiredThreshold * Balance.DifficultyMultiplier;
    Condition.TimeRequirement = Balance.TimeRequirement;
    Condition.Priority = Balance.Priority;
    Condition.bActiveCondition = Balance.bEnabled;
    
    // Apply resource type specific settings
    if (VictoryType == EEconomicVictoryType::SupplyMonopoly || VictoryType == EEconomicVictoryType::ResourceControl)
    {
        Condition.TargetResourceType = EResourceType::Supplies; // Default, can be customized
    }
    
    Subsystem->RegisterVictoryCondition(Condition);
}

FString UTGEconomicVictoryBalance::GetVictoryTypeName(EEconomicVictoryType VictoryType) const
{
    switch (VictoryType)
    {
        case EEconomicVictoryType::EconomicDominance:
            return TEXT("Economic Dominance");
        case EEconomicVictoryType::SupplyMonopoly:
            return TEXT("Supply Monopoly");
        case EEconomicVictoryType::EconomicCollapse:
            return TEXT("Economic Collapse");
        case EEconomicVictoryType::TradeNetwork:
            return TEXT("Trade Network");
        case EEconomicVictoryType::ResourceControl:
            return TEXT("Resource Control");
        case EEconomicVictoryType::ConvoySupremacy:
            return TEXT("Convoy Supremacy");
        default:
            return TEXT("Unknown Victory");
    }
}