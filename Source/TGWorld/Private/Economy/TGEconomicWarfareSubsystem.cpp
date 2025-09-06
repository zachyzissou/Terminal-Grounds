#include "Economy/TGEconomicWarfareSubsystem.h"
#include "Engine/World.h"
#include "TimerManager.h"

void UTGEconomicWarfareSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // Initialize faction specializations with default values
    InitializeFactionSpecializations();
    
    LastUpdateTime = GetWorld()->GetTimeSeconds();
    LastRecoveryTime = GetWorld()->GetTimeSeconds();
    
    UE_LOG(LogTemp, Log, TEXT("Economic Warfare Subsystem initialized"));
}

void UTGEconomicWarfareSubsystem::Deinitialize()
{
    // Clean up any active timers or delegates
    Super::Deinitialize();
}

bool UTGEconomicWarfareSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
    return true;
}

void UTGEconomicWarfareSubsystem::Tick(float DeltaTime)
{
    if (!GetWorld())
    {
        return;
    }

    float CurrentTime = GetWorld()->GetTimeSeconds();
    
    // Process route disruptions (check for expiration)
    ProcessRouteDisruptions(DeltaTime);
    
    // Update territorial blockades
    UpdateTerritorialBlockades(DeltaTime);
    
    // Update faction economic power every 30 seconds
    if (CurrentTime - LastUpdateTime >= 30.0f)
    {
        UpdateFactionEconomicPower();
        LastUpdateTime = CurrentTime;
    }
    
    // Process supply chain recovery every minute
    if (CurrentTime - LastRecoveryTime >= 60.0f)
    {
        ProcessSupplyChainRecovery(DeltaTime);
        LastRecoveryTime = CurrentTime;
    }
}

void UTGEconomicWarfareSubsystem::DisruptRoute(FName RouteId, ERouteDisruptionType DisruptionType, float DurationMinutes, int32 ResponsibleFactionID, float InvestmentCost)
{
    if (RouteId.IsNone())
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot disrupt route with invalid RouteId"));
        return;
    }

    FRouteDisruption Disruption;
    Disruption.DisruptionType = DisruptionType;
    Disruption.DurationMinutes = DurationMinutes;
    Disruption.ResponsibleFactionID = ResponsibleFactionID;
    Disruption.StartTime = GetWorld()->GetTimeSeconds();
    Disruption.EconomicImpact = InvestmentCost * DisruptionImpactMultiplier;
    Disruption.bPermanent = (DisruptionType == ERouteDisruptionType::Sabotage || DisruptionType == ERouteDisruptionType::BridgeOut);

    // Add to route disruptions
    if (!RouteDisruptions.Contains(RouteId))
    {
        RouteDisruptions.Add(RouteId, TArray<FRouteDisruption>());
    }
    RouteDisruptions[RouteId].Add(Disruption);

    // Update faction economic damage tracking
    if (ResponsibleFactionID >= 0)
    {
        if (!FactionEconomicDamageDealt.Contains(ResponsibleFactionID))
        {
            FactionEconomicDamageDealt.Add(ResponsibleFactionID, 0.0f);
        }
        FactionEconomicDamageDealt[ResponsibleFactionID] += Disruption.EconomicImpact;
    }

    // Broadcast event
    OnRouteDisrupted.Broadcast(RouteId, DisruptionType, ResponsibleFactionID, DurationMinutes);
    
    UE_LOG(LogTemp, Log, TEXT("Route %s disrupted by faction %d for %f minutes"), 
           *RouteId.ToString(), ResponsibleFactionID, DurationMinutes);
}

void UTGEconomicWarfareSubsystem::RepairRouteDisruption(FName RouteId, int32 RepairingFactionID, float RepairCost)
{
    if (!RouteDisruptions.Contains(RouteId))
    {
        return;
    }

    TArray<FRouteDisruption>& Disruptions = RouteDisruptions[RouteId];
    
    // Remove non-permanent disruptions (can be repaired)
    Disruptions.RemoveAll([](const FRouteDisruption& Disruption)
    {
        return !Disruption.bPermanent;
    });

    // If no disruptions remain, remove the route from the map
    if (Disruptions.Num() == 0)
    {
        RouteDisruptions.Remove(RouteId);
    }

    BroadcastEconomicEvent(TEXT("RouteRepaired"), RepairingFactionID, RepairCost);
    
    UE_LOG(LogTemp, Log, TEXT("Route %s repaired by faction %d"), *RouteId.ToString(), RepairingFactionID);
}

bool UTGEconomicWarfareSubsystem::IsRouteDisrupted(FName RouteId) const
{
    if (!RouteDisruptions.Contains(RouteId))
    {
        return false;
    }

    const TArray<FRouteDisruption>& Disruptions = RouteDisruptions[RouteId];
    float CurrentTime = GetWorld()->GetTimeSeconds();

    for (const FRouteDisruption& Disruption : Disruptions)
    {
        if (Disruption.bPermanent)
        {
            return true;
        }

        float ElapsedMinutes = (CurrentTime - Disruption.StartTime) / 60.0f;
        if (ElapsedMinutes < Disruption.DurationMinutes)
        {
            return true;
        }
    }

    return false;
}

TArray<FRouteDisruption> UTGEconomicWarfareSubsystem::GetActiveDisruptions(FName RouteId) const
{
    TArray<FRouteDisruption> ActiveDisruptions;
    
    if (!RouteDisruptions.Contains(RouteId))
    {
        return ActiveDisruptions;
    }

    const TArray<FRouteDisruption>& Disruptions = RouteDisruptions[RouteId];
    float CurrentTime = GetWorld()->GetTimeSeconds();

    for (const FRouteDisruption& Disruption : Disruptions)
    {
        if (Disruption.bPermanent)
        {
            ActiveDisruptions.Add(Disruption);
            continue;
        }

        float ElapsedMinutes = (CurrentTime - Disruption.StartTime) / 60.0f;
        if (ElapsedMinutes < Disruption.DurationMinutes)
        {
            ActiveDisruptions.Add(Disruption);
        }
    }

    return ActiveDisruptions;
}

float UTGEconomicWarfareSubsystem::CalculateRouteViability(FName RouteId) const
{
    if (!IsRouteDisrupted(RouteId))
    {
        return 1.0f; // Full viability
    }

    TArray<FRouteDisruption> ActiveDisruptions = GetActiveDisruptions(RouteId);
    float ViabilityMultiplier = 1.0f;

    for (const FRouteDisruption& Disruption : ActiveDisruptions)
    {
        switch (Disruption.DisruptionType)
        {
            case ERouteDisruptionType::SignalJam:
                ViabilityMultiplier *= 0.8f; // 20% reduction
                break;
            case ERouteDisruptionType::BridgeOut:
                ViabilityMultiplier *= 0.3f; // 70% reduction
                break;
            case ERouteDisruptionType::Blockade:
                ViabilityMultiplier *= 0.6f; // 40% reduction
                break;
            case ERouteDisruptionType::Sabotage:
                ViabilityMultiplier *= 0.4f; // 60% reduction
                break;
            case ERouteDisruptionType::Pirates:
                ViabilityMultiplier *= 0.7f; // 30% reduction
                break;
            case ERouteDisruptionType::Siege:
                ViabilityMultiplier *= 0.1f; // 90% reduction
                break;
            default:
                break;
        }
    }

    return FMath::Max(0.1f, ViabilityMultiplier); // Minimum 10% viability
}

bool UTGEconomicWarfareSubsystem::EstablishTerritorialBlockade(int32 TerritoryID, int32 BlockadingFactionID, float TaxRate)
{
    if (!ValidateBlockadeEstablishment(TerritoryID, BlockadingFactionID))
    {
        return false;
    }

    // Clamp tax rate to maximum allowed
    TaxRate = FMath::Clamp(TaxRate, 0.0f, MaxBlockadeTaxRate);

    FTerritorialBlockade Blockade;
    Blockade.TerritoryID = TerritoryID;
    Blockade.BlockadingFactionID = BlockadingFactionID;
    Blockade.TaxRate = TaxRate;
    Blockade.EstablishedTime = GetWorld()->GetTimeSeconds();

    TerritorialBlockades.Add(TerritoryID, Blockade);

    // Broadcast event
    OnTerritorialBlockadeEstablished.Broadcast(TerritoryID, BlockadingFactionID, TaxRate);

    UE_LOG(LogTemp, Log, TEXT("Territorial blockade established in territory %d by faction %d with %f%% tax rate"), 
           TerritoryID, BlockadingFactionID, TaxRate * 100.0f);

    return true;
}

void UTGEconomicWarfareSubsystem::RemoveTerritorialBlockade(int32 TerritoryID, int32 RemovingFactionID)
{
    if (!TerritorialBlockades.Contains(TerritoryID))
    {
        return;
    }

    TerritorialBlockades.Remove(TerritoryID);
    
    // Broadcast event
    OnTerritorialBlockadeRemoved.Broadcast(TerritoryID);

    UE_LOG(LogTemp, Log, TEXT("Territorial blockade removed from territory %d"), TerritoryID);
}

bool UTGEconomicWarfareSubsystem::CanEstablishBlockade(int32 TerritoryID, int32 FactionID) const
{
    return ValidateBlockadeEstablishment(TerritoryID, FactionID);
}

FTerritorialBlockade UTGEconomicWarfareSubsystem::GetTerritorialBlockade(int32 TerritoryID) const
{
    if (TerritorialBlockades.Contains(TerritoryID))
    {
        return TerritorialBlockades[TerritoryID];
    }
    return FTerritorialBlockade(); // Return default (empty) blockade
}

TArray<FTerritorialBlockade> UTGEconomicWarfareSubsystem::GetActiveTerritorialBlockades() const
{
    TArray<FTerritorialBlockade> ActiveBlockades;
    
    for (const auto& Pair : TerritorialBlockades)
    {
        ActiveBlockades.Add(Pair.Value);
    }
    
    return ActiveBlockades;
}

float UTGEconomicWarfareSubsystem::ExecuteEconomicWarfareAction(const FEconomicWarfareAction& Action)
{
    float SuccessChance = CalculateActionSuccessChance(Action);
    float RandomValue = FMath::RandRange(0.0f, 1.0f);
    
    float ActualReturn = 0.0f;
    
    if (RandomValue <= SuccessChance)
    {
        // Action successful
        ActualReturn = Action.ExpectedReturn;
        
        // Apply faction specialization bonuses
        float SpecializationBonus = GetFactionEconomicEfficiencyBonus(Action.InitiatingFactionID, Action.ActionType);
        ActualReturn *= SpecializationBonus;
        
        // Update faction economic damage tracking
        if (!FactionEconomicDamageDealt.Contains(Action.InitiatingFactionID))
        {
            FactionEconomicDamageDealt.Add(Action.InitiatingFactionID, 0.0f);
        }
        FactionEconomicDamageDealt[Action.InitiatingFactionID] += ActualReturn;
        
        if (Action.TargetFactionID >= 0)
        {
            if (!FactionEconomicDamageReceived.Contains(Action.TargetFactionID))
            {
                FactionEconomicDamageReceived.Add(Action.TargetFactionID, 0.0f);
            }
            FactionEconomicDamageReceived[Action.TargetFactionID] += ActualReturn;
            
            // Trigger retaliation if enabled and threshold is met
            if (bEnableEconomicRetaliation && ActualReturn >= RetaliationThreshold)
            {
                TriggerEconomicRetaliation(Action.TargetFactionID, Action.InitiatingFactionID, ActualReturn);
            }
        }
        
        UE_LOG(LogTemp, Log, TEXT("Economic warfare action successful: Faction %d dealt %f economic damage"), 
               Action.InitiatingFactionID, ActualReturn);
    }
    else
    {
        // Action failed - return partial value
        ActualReturn = Action.ExpectedReturn * 0.2f; // 20% return on failure
        
        UE_LOG(LogTemp, Log, TEXT("Economic warfare action failed: Faction %d received %f economic return"), 
               Action.InitiatingFactionID, ActualReturn);
    }
    
    // Broadcast event
    OnEconomicWarfareAction.Broadcast(Action.InitiatingFactionID, Action.ActionType, Action.InvestmentCost, ActualReturn);
    
    return ActualReturn - Action.InvestmentCost; // Net profit/loss
}

float UTGEconomicWarfareSubsystem::CalculateActionSuccessChance(const FEconomicWarfareAction& Action) const
{
    float BaseSuccessChance = 0.7f; // 70% base success rate
    
    // Apply risk level modifier
    float RiskModifier = FMath::Lerp(1.2f, 0.5f, Action.RiskLevel); // Higher risk = lower success chance
    BaseSuccessChance *= RiskModifier;
    
    // Apply faction specialization bonus
    float SpecializationBonus = CalculateSpecializationBonus(Action.InitiatingFactionID, Action.ActionType);
    BaseSuccessChance *= SpecializationBonus;
    
    // Apply investment scaling (more investment = higher success chance)
    float InvestmentBonus = FMath::Clamp(Action.InvestmentCost / 1000.0f, 0.8f, 1.5f);
    BaseSuccessChance *= InvestmentBonus;
    
    return FMath::Clamp(BaseSuccessChance, 0.1f, 0.95f); // Between 10% and 95%
}

float UTGEconomicWarfareSubsystem::CalculateActionRiskLevel(const FEconomicWarfareAction& Action) const
{
    float BaseRiskLevel = 1.0f;
    
    // Different action types have different inherent risks
    switch (Action.ActionType)
    {
        case EEconomicWarfareAction::SupplyInterdiction:
            BaseRiskLevel = 0.8f; // Medium-low risk
            break;
        case EEconomicWarfareAction::InfrastructureSabotage:
            BaseRiskLevel = 1.5f; // High risk
            break;
        case EEconomicWarfareAction::TerritorialBlockade:
            BaseRiskLevel = 1.2f; // Medium-high risk
            break;
        case EEconomicWarfareAction::ConvoyProtection:
            BaseRiskLevel = 0.6f; // Low risk
            break;
        case EEconomicWarfareAction::EconomicEspionage:
            BaseRiskLevel = 1.0f; // Medium risk
            break;
        case EEconomicWarfareAction::MarketManipulation:
            BaseRiskLevel = 0.7f; // Medium-low risk
            break;
        case EEconomicWarfareAction::SupplyChainHardening:
            BaseRiskLevel = 0.4f; // Low risk
            break;
    }
    
    // Scale by investment amount (higher investment = higher risk)
    float InvestmentRiskMultiplier = FMath::Clamp(Action.InvestmentCost / 2000.0f, 0.5f, 2.0f);
    
    return BaseRiskLevel * InvestmentRiskMultiplier;
}

FEconomicWarfareAction UTGEconomicWarfareSubsystem::CreateEconomicWarfareAction(EEconomicWarfareAction ActionType, int32 InitiatingFactionID, int32 TargetFactionID, const FString& TargetData, float InvestmentCost) const
{
    FEconomicWarfareAction Action;
    Action.ActionType = ActionType;
    Action.InitiatingFactionID = InitiatingFactionID;
    Action.TargetFactionID = TargetFactionID;
    Action.TargetData = TargetData;
    Action.InvestmentCost = InvestmentCost;
    Action.ExecutionTime = GetWorld()->GetTimeSeconds();
    
    // Calculate expected return based on action type and investment
    float BaseReturnMultiplier = 1.8f; // 180% return on investment
    
    switch (ActionType)
    {
        case EEconomicWarfareAction::SupplyInterdiction:
            BaseReturnMultiplier = 2.0f; // High return
            break;
        case EEconomicWarfareAction::InfrastructureSabotage:
            BaseReturnMultiplier = 2.5f; // Very high return, high risk
            break;
        case EEconomicWarfareAction::TerritorialBlockade:
            BaseReturnMultiplier = 1.5f; // Steady return over time
            break;
        case EEconomicWarfareAction::ConvoyProtection:
            BaseReturnMultiplier = 1.3f; // Lower but safer return
            break;
        case EEconomicWarfareAction::EconomicEspionage:
            BaseReturnMultiplier = 1.6f; // Information value
            break;
        case EEconomicWarfareAction::MarketManipulation:
            BaseReturnMultiplier = 2.2f; // High return through market control
            break;
        case EEconomicWarfareAction::SupplyChainHardening:
            BaseReturnMultiplier = 1.2f; // Long-term defensive value
            break;
    }
    
    Action.ExpectedReturn = InvestmentCost * BaseReturnMultiplier;
    Action.RiskLevel = CalculateActionRiskLevel(Action);
    
    return Action;
}

void UTGEconomicWarfareSubsystem::SetFactionEconomicSpecialization(int32 FactionID, EFactionEconomicSpecialty SpecialtyType)
{
    if (!FactionSpecializations.Contains(FactionID))
    {
        FactionSpecializations.Add(FactionID, FFactionEconomicSpecialization());
    }
    
    FFactionEconomicSpecialization& Specialization = FactionSpecializations[FactionID];
    Specialization.FactionID = FactionID;
    Specialization.SpecialtyType = SpecialtyType;
    
    // Set specialization-specific bonuses
    switch (SpecialtyType)
    {
        case EFactionEconomicSpecialty::ScrapEconomics:
            Specialization.EfficiencyBonus = 1.5f;
            Specialization.TerritoryBonusMultiplier = 1.3f;
            Specialization.BonusActions = {EEconomicWarfareAction::SupplyInterdiction};
            Specialization.SpecialtyDescription = "Enhanced salvage from disrupted convoys";
            break;
            
        case EFactionEconomicSpecialty::MarketManipulation:
            Specialization.EfficiencyBonus = 1.4f;
            Specialization.TerritoryBonusMultiplier = 1.2f;
            Specialization.BonusActions = {EEconomicWarfareAction::MarketManipulation, EEconomicWarfareAction::EconomicEspionage};
            Specialization.SpecialtyDescription = "Economic intelligence and price control";
            break;
            
        case EFactionEconomicSpecialty::GuerrillaDisruption:
            Specialization.EfficiencyBonus = 1.6f;
            Specialization.TerritoryBonusMultiplier = 1.1f;
            Specialization.BonusActions = {EEconomicWarfareAction::InfrastructureSabotage, EEconomicWarfareAction::SupplyInterdiction};
            Specialization.SpecialtyDescription = "Low-cost, high-impact supply disruption";
            break;
            
        case EFactionEconomicSpecialty::CorporateLogistics:
            Specialization.EfficiencyBonus = 1.3f;
            Specialization.TerritoryBonusMultiplier = 1.4f;
            Specialization.BonusActions = {EEconomicWarfareAction::SupplyChainHardening, EEconomicWarfareAction::ConvoyProtection};
            Specialization.SpecialtyDescription = "Fortified supply networks with defensive bonuses";
            break;
            
        case EFactionEconomicSpecialty::MobileTradeNetworks:
            Specialization.EfficiencyBonus = 1.2f;
            Specialization.TerritoryBonusMultiplier = 1.5f;
            Specialization.BonusActions = {EEconomicWarfareAction::ConvoyProtection};
            Specialization.SpecialtyDescription = "Adaptive routing and rapid reconfiguration";
            break;
            
        case EFactionEconomicSpecialty::InformationEconomy:
            Specialization.EfficiencyBonus = 1.3f;
            Specialization.TerritoryBonusMultiplier = 1.3f;
            Specialization.BonusActions = {EEconomicWarfareAction::EconomicEspionage, EEconomicWarfareAction::MarketManipulation};
            Specialization.SpecialtyDescription = "Economic intelligence and supply optimization";
            break;
            
        case EFactionEconomicSpecialty::CommunityLogistics:
            Specialization.EfficiencyBonus = 1.2f;
            Specialization.TerritoryBonusMultiplier = 1.6f;
            Specialization.BonusActions = {EEconomicWarfareAction::ConvoyProtection, EEconomicWarfareAction::SupplyChainHardening};
            Specialization.SpecialtyDescription = "Collective resource sharing and mutual protection";
            break;
    }
    
    UE_LOG(LogTemp, Log, TEXT("Faction %d set to specialization: %s"), FactionID, *Specialization.SpecialtyDescription);
}

FFactionEconomicSpecialization UTGEconomicWarfareSubsystem::GetFactionEconomicSpecialization(int32 FactionID) const
{
    if (FactionSpecializations.Contains(FactionID))
    {
        return FactionSpecializations[FactionID];
    }
    return FFactionEconomicSpecialization(); // Return default specialization
}

float UTGEconomicWarfareSubsystem::GetFactionEconomicEfficiencyBonus(int32 FactionID, EEconomicWarfareAction ActionType) const
{
    if (!FactionSpecializations.Contains(FactionID))
    {
        return 1.0f; // No bonus
    }
    
    const FFactionEconomicSpecialization& Specialization = FactionSpecializations[FactionID];
    
    // Check if this action type is a bonus action for this faction
    if (Specialization.BonusActions.Contains(ActionType))
    {
        return Specialization.EfficiencyBonus;
    }
    
    return 1.0f; // No bonus for non-specialized actions
}

float UTGEconomicWarfareSubsystem::GetFactionTerritoryEconomicBonus(int32 FactionID, int32 TerritoryID) const
{
    if (!FactionSpecializations.Contains(FactionID))
    {
        return 1.0f; // No bonus
    }
    
    // Check if faction controls or has significant influence in territory
    float TerritorialInfluence = GetTerritorialInfluence(TerritoryID, FactionID);
    
    if (TerritorialInfluence >= 0.5f) // 50% influence threshold
    {
        const FFactionEconomicSpecialization& Specialization = FactionSpecializations[FactionID];
        return Specialization.TerritoryBonusMultiplier * TerritorialInfluence;
    }
    
    return 1.0f; // No territorial bonus
}

float UTGEconomicWarfareSubsystem::GetFactionEconomicPower(int32 FactionID) const
{
    if (FactionEconomicPower.Contains(FactionID))
    {
        return FactionEconomicPower[FactionID];
    }
    return 100.0f; // Default economic power
}

float UTGEconomicWarfareSubsystem::CalculateSupplyChainEfficiency(int32 FactionID) const
{
    float BaseEfficiency = 1.0f;
    
    // Factor in economic damage received (reduces efficiency)
    if (FactionEconomicDamageReceived.Contains(FactionID))
    {
        float DamageRatio = FactionEconomicDamageReceived[FactionID] / 10000.0f; // Normalize to 0-1 range
        BaseEfficiency -= FMath::Clamp(DamageRatio, 0.0f, 0.8f); // Max 80% efficiency loss
    }
    
    // Factor in specialization bonuses
    if (FactionSpecializations.Contains(FactionID))
    {
        const FFactionEconomicSpecialization& Specialization = FactionSpecializations[FactionID];
        BaseEfficiency *= (Specialization.EfficiencyBonus - 1.0f) * 0.5f + 1.0f; // Reduced impact on base efficiency
    }
    
    return FMath::Max(0.2f, BaseEfficiency); // Minimum 20% efficiency
}

TArray<int32> UTGEconomicWarfareSubsystem::GetVulnerableSupplyRoutes(int32 FactionID) const
{
    // This would integrate with convoy economy subsystem to identify vulnerable routes
    // For now, return placeholder data
    TArray<int32> VulnerableRoutes;
    
    // Implementation would analyze:
    // - Routes with low protection
    // - Routes through contested territory
    // - Routes with recent disruption history
    
    return VulnerableRoutes;
}

float UTGEconomicWarfareSubsystem::CalculateEconomicDamageDealt(int32 FactionID) const
{
    if (FactionEconomicDamageDealt.Contains(FactionID))
    {
        return FactionEconomicDamageDealt[FactionID];
    }
    return 0.0f;
}

float UTGEconomicWarfareSubsystem::CalculateEconomicDamageReceived(int32 FactionID) const
{
    if (FactionEconomicDamageReceived.Contains(FactionID))
    {
        return FactionEconomicDamageReceived[FactionID];
    }
    return 0.0f;
}

void UTGEconomicWarfareSubsystem::TriggerEconomicRetaliation(int32 AttackedFactionID, int32 AttackingFactionID, float EconomicDamage)
{
    if (!bEnableEconomicRetaliation)
    {
        return;
    }
    
    float RetaliationSeverity = CalculateRetaliationSeverity(AttackedFactionID, EconomicDamage);
    
    // Process retaliation based on faction specialization and economic power
    ProcessRetaliationEscalation(AttackedFactionID, AttackingFactionID, RetaliationSeverity);
    
    // Broadcast retaliation event
    FString RetaliationType = RetaliationSeverity > 1000.0f ? TEXT("Major") : TEXT("Minor");
    OnEconomicRetaliation.Broadcast(AttackedFactionID, AttackingFactionID, RetaliationSeverity, RetaliationType);
    
    UE_LOG(LogTemp, Log, TEXT("Economic retaliation triggered: Faction %d retaliating against faction %d with severity %f"), 
           AttackedFactionID, AttackingFactionID, RetaliationSeverity);
}

float UTGEconomicWarfareSubsystem::CalculateRetaliationSeverity(int32 AttackedFactionID, float EconomicDamage) const
{
    float BaseSeverity = EconomicDamage * 1.2f; // 120% retaliation by default
    
    // Factor in faction economic power (stronger factions retaliate more)
    float EconomicPower = GetFactionEconomicPower(AttackedFactionID);
    float PowerMultiplier = FMath::Clamp(EconomicPower / 100.0f, 0.5f, 2.0f);
    
    return BaseSeverity * PowerMultiplier;
}

void UTGEconomicWarfareSubsystem::ProcessSupplyChainRecovery(float DeltaTime)
{
    // Gradual recovery of economic damage over time
    float RecoveryAmount = SupplyChainRecoveryRate * (DeltaTime / 3600.0f); // Per hour rate
    
    for (auto& Pair : FactionEconomicDamageReceived)
    {
        float& Damage = Pair.Value;
        Damage = FMath::Max(0.0f, Damage - RecoveryAmount);
    }
    
    // Broadcast recovery events for significant recovery
    if (RecoveryAmount > 10.0f) // Significant recovery threshold
    {
        for (const auto& Pair : FactionEconomicDamageReceived)
        {
            if (Pair.Value > 0.0f)
            {
                BroadcastEconomicEvent(TEXT("SupplyChainRecovery"), Pair.Key, RecoveryAmount);
            }
        }
    }
}

void UTGEconomicWarfareSubsystem::EstablishEconomicAlliance(int32 FactionA, int32 FactionB, float BenefitMultiplier)
{
    // Add bidirectional alliance relationship
    if (!EconomicAlliances.Contains(FactionA))
    {
        EconomicAlliances.Add(FactionA, TArray<int32>());
    }
    if (!EconomicAlliances.Contains(FactionB))
    {
        EconomicAlliances.Add(FactionB, TArray<int32>());
    }
    
    EconomicAlliances[FactionA].AddUnique(FactionB);
    EconomicAlliances[FactionB].AddUnique(FactionA);
    
    BroadcastEconomicEvent(TEXT("EconomicAllianceEstablished"), FactionA, BenefitMultiplier);
    BroadcastEconomicEvent(TEXT("EconomicAllianceEstablished"), FactionB, BenefitMultiplier);
    
    UE_LOG(LogTemp, Log, TEXT("Economic alliance established between faction %d and faction %d"), FactionA, FactionB);
}

void UTGEconomicWarfareSubsystem::BreakEconomicAlliance(int32 FactionA, int32 FactionB, float PenaltyMultiplier)
{
    if (EconomicAlliances.Contains(FactionA))
    {
        EconomicAlliances[FactionA].Remove(FactionB);
    }
    if (EconomicAlliances.Contains(FactionB))
    {
        EconomicAlliances[FactionB].Remove(FactionA);
    }
    
    BroadcastEconomicEvent(TEXT("EconomicAllianceBroken"), FactionA, PenaltyMultiplier);
    BroadcastEconomicEvent(TEXT("EconomicAllianceBroken"), FactionB, PenaltyMultiplier);
    
    UE_LOG(LogTemp, Log, TEXT("Economic alliance broken between faction %d and faction %d"), FactionA, FactionB);
}

bool UTGEconomicWarfareSubsystem::AreFactionsEconomicAllies(int32 FactionA, int32 FactionB) const
{
    if (EconomicAlliances.Contains(FactionA))
    {
        return EconomicAlliances[FactionA].Contains(FactionB);
    }
    return false;
}

float UTGEconomicWarfareSubsystem::GetAllianceBenefit(int32 FactionA, int32 FactionB) const
{
    if (AreFactionsEconomicAllies(FactionA, FactionB))
    {
        return AllianceBenefitBaseMultiplier;
    }
    return 1.0f; // No benefit
}

void UTGEconomicWarfareSubsystem::ProcessRouteDisruptions(float DeltaTime)
{
    float CurrentTime = GetWorld()->GetTimeSeconds();
    TArray<FName> RoutesToCleanup;
    
    for (auto& RoutePair : RouteDisruptions)
    {
        TArray<FRouteDisruption>& Disruptions = RoutePair.Value;
        
        // Remove expired non-permanent disruptions
        Disruptions.RemoveAll([CurrentTime](const FRouteDisruption& Disruption)
        {
            if (Disruption.bPermanent)
            {
                return false; // Keep permanent disruptions
            }
            
            float ElapsedMinutes = (CurrentTime - Disruption.StartTime) / 60.0f;
            return ElapsedMinutes >= Disruption.DurationMinutes;
        });
        
        // Mark routes with no remaining disruptions for cleanup
        if (Disruptions.Num() == 0)
        {
            RoutesToCleanup.Add(RoutePair.Key);
        }
    }
    
    // Clean up routes with no active disruptions
    for (FName RouteId : RoutesToCleanup)
    {
        RouteDisruptions.Remove(RouteId);
    }
}

void UTGEconomicWarfareSubsystem::UpdateTerritorialBlockades(float DeltaTime)
{
    // Update blockade revenue and statistics
    for (auto& BlockadePair : TerritorialBlockades)
    {
        FTerritorialBlockade& Blockade = BlockadePair.Value;
        
        // Simulate revenue generation (this would integrate with actual convoy traffic)
        float RevenueThisUpdate = Blockade.TaxRate * 10.0f * DeltaTime; // Placeholder calculation
        Blockade.TotalRevenue += RevenueThisUpdate;
    }
}

void UTGEconomicWarfareSubsystem::UpdateFactionEconomicPower()
{
    // Calculate economic power based on damage dealt/received and territorial control
    for (int32 FactionID = 1; FactionID <= 7; ++FactionID) // Assuming 7 factions
    {
        float BasePower = 100.0f;
        
        // Add damage dealt (aggressive economic warfare increases power)
        if (FactionEconomicDamageDealt.Contains(FactionID))
        {
            BasePower += FactionEconomicDamageDealt[FactionID] * 0.01f;
        }
        
        // Subtract damage received (being attacked reduces power)
        if (FactionEconomicDamageReceived.Contains(FactionID))
        {
            BasePower -= FactionEconomicDamageReceived[FactionID] * 0.02f;
        }
        
        // Factor in territorial control (would integrate with territorial system)
        // Placeholder: assume some territorial bonus
        BasePower += 20.0f; // Territorial control bonus
        
        FactionEconomicPower.Add(FactionID, FMath::Max(10.0f, BasePower));
    }
}

void UTGEconomicWarfareSubsystem::InitializeFactionSpecializations()
{
    // Initialize faction specializations based on existing faction data
    SetFactionEconomicSpecialization(1, EFactionEconomicSpecialty::CorporateLogistics);     // Sky Bastion Directorate
    SetFactionEconomicSpecialization(2, EFactionEconomicSpecialty::ScrapEconomics);        // Iron Scavengers (VulturesUnion)
    SetFactionEconomicSpecialization(3, EFactionEconomicSpecialty::GuerrillaDisruption);   // Free77
    SetFactionEconomicSpecialization(4, EFactionEconomicSpecialty::MarketManipulation);    // Corporate Hegemony
    SetFactionEconomicSpecialization(5, EFactionEconomicSpecialty::MobileTradeNetworks);   // Nomad Clans
    SetFactionEconomicSpecialization(6, EFactionEconomicSpecialty::InformationEconomy);    // Archive Keepers
    SetFactionEconomicSpecialization(7, EFactionEconomicSpecialty::CommunityLogistics);    // Civic Wardens
    
    UE_LOG(LogTemp, Log, TEXT("Faction economic specializations initialized"));
}

float UTGEconomicWarfareSubsystem::CalculateSpecializationBonus(int32 FactionID, EEconomicWarfareAction ActionType) const
{
    return GetFactionEconomicEfficiencyBonus(FactionID, ActionType);
}

bool UTGEconomicWarfareSubsystem::ValidateBlockadeEstablishment(int32 TerritoryID, int32 FactionID) const
{
    // Check if faction has sufficient territorial influence
    float TerritorialInfluence = GetTerritorialInfluence(TerritoryID, FactionID);
    
    if (TerritorialInfluence < BlockadeInfluenceThreshold)
    {
        return false; // Insufficient influence
    }
    
    // Check if territory is already blockaded
    if (TerritorialBlockades.Contains(TerritoryID))
    {
        return false; // Already blockaded
    }
    
    return true;
}

void UTGEconomicWarfareSubsystem::ProcessRetaliationEscalation(int32 AttackedFactionID, int32 AttackingFactionID, float Severity)
{
    // Create and execute automatic retaliation action
    FEconomicWarfareAction RetaliationAction = CreateEconomicWarfareAction(
        EEconomicWarfareAction::SupplyInterdiction,
        AttackedFactionID,
        AttackingFactionID,
        TEXT("AutomaticRetaliation"),
        Severity * 0.8f // 80% of severity as investment
    );
    
    // Execute retaliation with reduced randomness (more predictable)
    float RetaliationReturn = ExecuteEconomicWarfareAction(RetaliationAction);
    
    UE_LOG(LogTemp, Log, TEXT("Automatic retaliation executed: %f economic damage"), RetaliationReturn);
}

float UTGEconomicWarfareSubsystem::GetTerritorialInfluence(int32 TerritoryID, int32 FactionID) const
{
    // This would integrate with the territorial system to get actual influence values
    // For now, return placeholder values based on faction ID and territory ID
    
    if (TerritoryID <= 0 || FactionID <= 0)
    {
        return 0.0f;
    }
    
    // Placeholder: simulate some territorial influence based on faction and territory
    float MockInfluence = 0.3f + (FactionID % 3) * 0.2f + (TerritoryID % 2) * 0.3f;
    return FMath::Clamp(MockInfluence, 0.0f, 1.0f);
}

void UTGEconomicWarfareSubsystem::BroadcastEconomicEvent(const FString& EventType, int32 AffectedFactionID, float EconomicImpact)
{
    OnSupplyChainEvent.Broadcast(EventType, AffectedFactionID, EconomicImpact);
}