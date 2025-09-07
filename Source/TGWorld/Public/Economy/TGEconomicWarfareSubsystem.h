#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/DataTable.h"
#include "GameplayTagContainer.h"
#include "TGEconomicWarfareSubsystem.generated.h"

UENUM(BlueprintType)
enum class ERouteDisruptionType : uint8
{
    None            UMETA(DisplayName = "No Disruption"),
    SignalJam       UMETA(DisplayName = "Signal Jamming"),
    BridgeOut       UMETA(DisplayName = "Bridge Destroyed"),
    Blockade        UMETA(DisplayName = "Territorial Blockade"),
    Sabotage        UMETA(DisplayName = "Infrastructure Sabotage"),
    Pirates         UMETA(DisplayName = "Pirate Activity"),
    Siege           UMETA(DisplayName = "Territory Under Siege")
};

UENUM(BlueprintType)
enum class EEconomicWarfareAction : uint8
{
    SupplyInterdiction      UMETA(DisplayName = "Supply Interdiction"),
    InfrastructureSabotage  UMETA(DisplayName = "Infrastructure Sabotage"),
    TerritorialBlockade     UMETA(DisplayName = "Territorial Blockade"),
    ConvoyProtection        UMETA(DisplayName = "Convoy Protection"),
    EconomicEspionage       UMETA(DisplayName = "Economic Espionage"),
    MarketManipulation      UMETA(DisplayName = "Market Manipulation"),
    SupplyChainHardening    UMETA(DisplayName = "Supply Chain Hardening")
};

UENUM(BlueprintType)
enum class EFactionEconomicSpecialty : uint8
{
    ScrapEconomics          UMETA(DisplayName = "Scrap Economics"),
    MarketManipulation      UMETA(DisplayName = "Market Manipulation"),
    GuerrillaDisruption     UMETA(DisplayName = "Guerrilla Disruption"),
    CorporateLogistics      UMETA(DisplayName = "Corporate Logistics"),
    MobileTradeNetworks     UMETA(DisplayName = "Mobile Trade Networks"),
    InformationEconomy      UMETA(DisplayName = "Information Economy"),
    CommunityLogistics      UMETA(DisplayName = "Community Logistics")
};

USTRUCT(BlueprintType)
struct FRouteDisruption
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    ERouteDisruptionType DisruptionType = ERouteDisruptionType::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    float DurationMinutes = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    float SeverityMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    int32 ResponsibleFactionID = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    float StartTime = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    float EconomicImpact = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disruption")
    bool bPermanent = false;

    FRouteDisruption()
    {
        DisruptionType = ERouteDisruptionType::None;
        DurationMinutes = 0.0f;
        SeverityMultiplier = 1.0f;
        ResponsibleFactionID = -1;
        StartTime = 0.0f;
        EconomicImpact = 0.0f;
        bPermanent = false;
    }
};

USTRUCT(BlueprintType)
struct FTerritorialBlockade
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blockade")
    int32 TerritoryID = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blockade")
    int32 BlockadingFactionID = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blockade")
    float TaxRate = 0.15f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blockade")
    float EstablishedTime = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blockade")
    float TotalRevenue = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blockade")
    int32 ConvoysAffected = 0;

    FTerritorialBlockade()
    {
        TerritoryID = -1;
        BlockadingFactionID = -1;
        TaxRate = 0.15f;
        EstablishedTime = 0.0f;
        TotalRevenue = 0.0f;
        ConvoysAffected = 0;
    }
};

USTRUCT(BlueprintType)
struct FEconomicWarfareAction
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    EEconomicWarfareAction ActionType = EEconomicWarfareAction::SupplyInterdiction;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    int32 InitiatingFactionID = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    int32 TargetFactionID = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    float InvestmentCost = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    float ExpectedReturn = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    float RiskLevel = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    FString TargetData;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Action")
    float ExecutionTime = 0.0f;

    FEconomicWarfareAction()
    {
        ActionType = EEconomicWarfareAction::SupplyInterdiction;
        InitiatingFactionID = -1;
        TargetFactionID = -1;
        InvestmentCost = 0.0f;
        ExpectedReturn = 0.0f;
        RiskLevel = 1.0f;
        TargetData = "";
        ExecutionTime = 0.0f;
    }
};

USTRUCT(BlueprintType)
struct FFactionEconomicSpecialization
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Specialization")
    int32 FactionID = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Specialization")
    EFactionEconomicSpecialty SpecialtyType = EFactionEconomicSpecialty::ScrapEconomics;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Specialization")
    float EfficiencyBonus = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Specialization")
    TArray<EEconomicWarfareAction> BonusActions;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Specialization")
    float TerritoryBonusMultiplier = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Specialization")
    FString SpecialtyDescription;

    FFactionEconomicSpecialization()
    {
        FactionID = -1;
        SpecialtyType = EFactionEconomicSpecialty::ScrapEconomics;
        EfficiencyBonus = 1.0f;
        TerritoryBonusMultiplier = 1.0f;
        SpecialtyDescription = "";
    }
};

// Wrappers for TArray in TMap (UE5 reflection system requirement)
USTRUCT(BlueprintType)
struct TGWORLD_API FTGRouteDisruptionArray
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<FRouteDisruption> Disruptions;

    FTGRouteDisruptionArray()
    {
        Disruptions.Empty();
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FTGEconomicAllianceArray
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<int32> AlliedFactionIds;

    FTGEconomicAllianceArray()
    {
        AlliedFactionIds.Empty();
    }
};

// Event Delegates
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnRouteDisrupted, FName, RouteId, ERouteDisruptionType, DisruptionType, int32, ResponsibleFactionID, float, Duration);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritorialBlockadeEstablished, int32, TerritoryID, int32, BlockadingFactionID, float, TaxRate);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTerritorialBlockadeRemoved, int32, TerritoryID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnEconomicWarfareAction, int32, InitiatingFactionID, EEconomicWarfareAction, ActionType, float, InvestmentCost, float, ExpectedReturn);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnSupplyChainEvent, FString, EventType, int32, AffectedFactionID, float, EconomicImpact);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnEconomicRetaliation, int32, RetaliatingFactionID, int32, TargetFactionID, float, RetaliationSeverity, FString, RetaliationType);

/**
 * Economic Warfare Subsystem
 * Manages territorial supply chain disruption, economic warfare actions, and faction-specific economic specializations
 * Integrates with territorial control system and convoy economy for comprehensive economic gameplay
 */
UCLASS()
class TGWORLD_API UTGEconomicWarfareSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;

    // Route Disruption Management
    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void DisruptRoute(FName RouteId, ERouteDisruptionType DisruptionType, float DurationMinutes, int32 ResponsibleFactionID = -1, float InvestmentCost = 0.0f);

    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void RepairRouteDisruption(FName RouteId, int32 RepairingFactionID, float RepairCost = 0.0f);

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    bool IsRouteDisrupted(FName RouteId) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    TArray<FRouteDisruption> GetActiveDisruptions(FName RouteId) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateRouteViability(FName RouteId) const;

    // Territorial Blockade Management
    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    bool EstablishTerritorialBlockade(int32 TerritoryID, int32 BlockadingFactionID, float TaxRate = 0.15f);

    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void RemoveTerritorialBlockade(int32 TerritoryID, int32 RemovingFactionID = -1);

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    bool CanEstablishBlockade(int32 TerritoryID, int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    FTerritorialBlockade GetTerritorialBlockade(int32 TerritoryID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    TArray<FTerritorialBlockade> GetActiveTerritorialBlockades() const;

    // Economic Warfare Actions
    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    float ExecuteEconomicWarfareAction(const FEconomicWarfareAction& Action);

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateActionSuccessChance(const FEconomicWarfareAction& Action) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateActionRiskLevel(const FEconomicWarfareAction& Action) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    FEconomicWarfareAction CreateEconomicWarfareAction(EEconomicWarfareAction ActionType, int32 InitiatingFactionID, int32 TargetFactionID, const FString& TargetData, float InvestmentCost) const;

    // Faction Economic Specializations
    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void SetFactionEconomicSpecialization(int32 FactionID, EFactionEconomicSpecialty SpecialtyType);

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    FFactionEconomicSpecialization GetFactionEconomicSpecialization(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float GetFactionEconomicEfficiencyBonus(int32 FactionID, EEconomicWarfareAction ActionType) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float GetFactionTerritoryEconomicBonus(int32 FactionID, int32 TerritoryID) const;

    // Economic Intelligence and Analytics
    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float GetFactionEconomicPower(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateSupplyChainEfficiency(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    TArray<int32> GetVulnerableSupplyRoutes(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateEconomicDamageDealt(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateEconomicDamageReceived(int32 FactionID) const;

    // Retaliation and Recovery Systems
    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void TriggerEconomicRetaliation(int32 AttackedFactionID, int32 AttackingFactionID, float EconomicDamage);

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float CalculateRetaliationSeverity(int32 AttackedFactionID, float EconomicDamage) const;

    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void ProcessSupplyChainRecovery(float DeltaTime);

    // Alliance and Cooperation Systems
    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void EstablishEconomicAlliance(int32 FactionA, int32 FactionB, float BenefitMultiplier = 1.2f);

    UFUNCTION(BlueprintCallable, Category = "Economic Warfare")
    void BreakEconomicAlliance(int32 FactionA, int32 FactionB, float PenaltyMultiplier = 0.8f);

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    bool AreFactionsEconomicAllies(int32 FactionA, int32 FactionB) const;

    UFUNCTION(BlueprintPure, Category = "Economic Warfare")
    float GetAllianceBenefit(int32 FactionA, int32 FactionB) const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Economic Warfare Events")
    FOnRouteDisrupted OnRouteDisrupted;

    UPROPERTY(BlueprintAssignable, Category = "Economic Warfare Events")
    FOnTerritorialBlockadeEstablished OnTerritorialBlockadeEstablished;

    UPROPERTY(BlueprintAssignable, Category = "Economic Warfare Events")
    FOnTerritorialBlockadeRemoved OnTerritorialBlockadeRemoved;

    UPROPERTY(BlueprintAssignable, Category = "Economic Warfare Events")
    FOnEconomicWarfareAction OnEconomicWarfareAction;

    UPROPERTY(BlueprintAssignable, Category = "Economic Warfare Events")
    FOnSupplyChainEvent OnSupplyChainEvent;

    UPROPERTY(BlueprintAssignable, Category = "Economic Warfare Events")
    FOnEconomicRetaliation OnEconomicRetaliation;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float BlockadeInfluenceThreshold = 0.75f; // Minimum influence to establish blockade

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float MaxBlockadeTaxRate = 0.25f; // Maximum tax rate for territorial blockades

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float DisruptionImpactMultiplier = 1.5f; // Multiplier for disruption economic impact

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float RetaliationThreshold = 0.1f; // Economic damage threshold to trigger retaliation

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    bool bEnableEconomicRetaliation = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float SupplyChainRecoveryRate = 0.05f; // Per hour recovery rate for disrupted routes

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float AllianceBenefitBaseMultiplier = 1.2f; // Base multiplier for economic alliance benefits

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economic Warfare Config")
    float AllianceBreakPenaltyMultiplier = 0.7f; // Penalty multiplier when breaking alliances

protected:
    virtual void Tick(float DeltaTime) override;
    virtual bool IsTickable() const override { return true; }
    virtual TStatId GetStatID() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UTGEconomicWarfareSubsystem, STATGROUP_Tickables); }

private:
    // Core state management
    UPROPERTY()
    TMap<FName, FTGRouteDisruptionArray> RouteDisruptions;

    UPROPERTY()
    TMap<int32, FTerritorialBlockade> TerritorialBlockades; // TerritoryID -> Blockade

    UPROPERTY()
    TMap<int32, FFactionEconomicSpecialization> FactionSpecializations; // FactionID -> Specialization

    UPROPERTY()
    TMap<int32, float> FactionEconomicPower; // FactionID -> Economic Power Score

    UPROPERTY()
    TMap<int32, FTGEconomicAllianceArray> EconomicAlliances; // FactionID -> Allied Faction IDs

    UPROPERTY()
    TMap<int32, float> FactionEconomicDamageDealt; // FactionID -> Total Damage Dealt

    UPROPERTY()
    TMap<int32, float> FactionEconomicDamageReceived; // FactionID -> Total Damage Received

    // Timing and persistence
    float LastUpdateTime = 0.0f;
    float LastRecoveryTime = 0.0f;

    // Internal systems
    void ProcessRouteDisruptions(float DeltaTime);
    void UpdateTerritorialBlockades(float DeltaTime);
    void UpdateFactionEconomicPower();
    void InitializeFactionSpecializations();
    float CalculateSpecializationBonus(int32 FactionID, EEconomicWarfareAction ActionType) const;
    bool ValidateBlockadeEstablishment(int32 TerritoryID, int32 FactionID) const;
    void ProcessRetaliationEscalation(int32 AttackedFactionID, int32 AttackingFactionID, float Severity);
    float GetTerritorialInfluence(int32 TerritoryID, int32 FactionID) const;
    void BroadcastEconomicEvent(const FString& EventType, int32 AffectedFactionID, float EconomicImpact);
};