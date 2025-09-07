#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "TerritorialProgressionSubsystem.h"
#include "Analytics/TGTerritorialResourceAnalytics.h"
#include "TGTerritorial/Public/TerritorialTypes.h"
#include "TGAdvancedTerritorialProgressionSubsystem.generated.h"

// Forward declarations
class UTGTrustSubsystem;
class UTGTerritorialManager;
class UTGConvoyEconomySubsystem;
class UTGCodexSubsystem;

/**
 * Advanced Territorial Resource Bonus Structures
 * Integrates with analytics system for data-driven balance optimization
 */

UENUM(BlueprintType)
enum class ETerritorialBonusType : uint8
{
    Static              UMETA(DisplayName = "Static"),              // Fixed bonus values
    Dynamic             UMETA(DisplayName = "Dynamic"),            // Analytics-driven values
    Adaptive            UMETA(DisplayName = "Adaptive"),           // Machine learning adjusted
    Predictive          UMETA(DisplayName = "Predictive")          // Forecast-based adjustments
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGAdvancedResourceBonus
{
    GENERATED_BODY()

    // Base resource bonus value
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus")
    float BaseValue = 100.0f;

    // Analytical multipliers from TGTerritorialResourceAnalytics
    UPROPERTY(BlueprintReadOnly, Category = "Analytics")
    float AnalyticalMultiplier = 1.0f;

    // Statistical confidence in this bonus value (0-1)
    UPROPERTY(BlueprintReadOnly, Category = "Statistics")
    float ConfidenceLevel = 0.95f;

    // Bonus type affects how value is calculated
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus")
    ETerritorialBonusType BonusType = ETerritorialBonusType::Dynamic;

    // Time-decay factors for dynamic bonuses
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
    float DecayRate = 0.01f; // Per hour

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
    float MinDecayValue = 0.5f; // Minimum multiplier after decay

    // Faction synergy bonuses (when multiple factions control connected territories)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Synergy")
    TMap<int32, float> FactionSynergyBonuses;

    // Economic equilibrium adjustments
    UPROPERTY(BlueprintReadOnly, Category = "Economics")
    float EquilibriumAdjustment = 0.0f; // +/- adjustment from market equilibrium

    // A/B test assignment (for testing new bonus values)
    UPROPERTY(BlueprintReadOnly, Category = "Testing")
    FName ActiveTestGroup = NAME_None;

    FTGAdvancedResourceBonus()
    {
        BaseValue = 100.0f;
        AnalyticalMultiplier = 1.0f;
        ConfidenceLevel = 0.95f;
        BonusType = ETerritorialBonusType::Dynamic;
        DecayRate = 0.01f;
        MinDecayValue = 0.5f;
        EquilibriumAdjustment = 0.0f;
        ActiveTestGroup = NAME_None;
    }

    // Calculate final bonus value including all modifiers
    float CalculateFinalValue() const
    {
        float FinalValue = BaseValue * AnalyticalMultiplier;
        FinalValue += EquilibriumAdjustment;
        return FMath::Max(FinalValue, BaseValue * MinDecayValue);
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGTerritorialResourceMetrics
{
    GENERATED_BODY()

    // Resource generation rates (per hour)
    UPROPERTY(BlueprintReadOnly, Category = "Metrics")
    float GenerationRate = 0.0f;

    // Resource efficiency (actual vs predicted)
    UPROPERTY(BlueprintReadOnly, Category = "Metrics")
    float Efficiency = 1.0f;

    // Market value (relative to other resources)
    UPROPERTY(BlueprintReadOnly, Category = "Metrics")
    float MarketValue = 1.0f;

    // Scarcity multiplier (higher = more scarce = more valuable)
    UPROPERTY(BlueprintReadOnly, Category = "Metrics")
    float ScarcityMultiplier = 1.0f;

    // Strategic importance (0-10 scale)
    UPROPERTY(BlueprintReadOnly, Category = "Metrics")
    float StrategicImportance = 5.0f;

    // Competition intensity (how contested this resource is)
    UPROPERTY(BlueprintReadOnly, Category = "Metrics")
    float CompetitionIntensity = 1.0f;

    FTGTerritorialResourceMetrics()
    {
        GenerationRate = 0.0f;
        Efficiency = 1.0f;
        MarketValue = 1.0f;
        ScarcityMultiplier = 1.0f;
        StrategicImportance = 5.0f;
        CompetitionIntensity = 1.0f;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGFactionTerritorialPerformance
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    int32 FactionId;

    // Territorial control metrics
    UPROPERTY(BlueprintReadOnly, Category = "Control")
    int32 TerritoriesControlled = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Control")
    int32 HighValueTerritories = 0;

    UPROPERTY(BlueprintReadOnly, Category = "Control")
    float AverageTerritoryValue = 0.0f;

    // Resource performance metrics
    UPROPERTY(BlueprintReadOnly, Category = "Resources")
    TMap<ETerritoryResourceType, float> ResourceEfficiency;

    UPROPERTY(BlueprintReadOnly, Category = "Resources")
    float TotalResourceGeneration = 0.0f;

    // Competitive metrics
    UPROPERTY(BlueprintReadOnly, Category = "Competition")
    float TerritorialWinRate = 0.5f; // 0-1 scale

    UPROPERTY(BlueprintReadOnly, Category = "Competition")
    float DefenseSuccessRate = 0.5f; // 0-1 scale

    UPROPERTY(BlueprintReadOnly, Category = "Competition")
    float AttackSuccessRate = 0.5f; // 0-1 scale

    // Predictive metrics
    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    float PredictedGrowth = 0.0f; // % growth predicted over next week

    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    float RetentionRisk = 0.0f; // 0-1, higher = more risk of player attrition

    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    float BalanceScore = 0.5f; // 0-1, how balanced this faction is vs others

    FTGFactionTerritorialPerformance()
    {
        FactionId = 0;
        TerritoriesControlled = 0;
        HighValueTerritories = 0;
        AverageTerritoryValue = 0.0f;
        TotalResourceGeneration = 0.0f;
        TerritorialWinRate = 0.5f;
        DefenseSuccessRate = 0.5f;
        AttackSuccessRate = 0.5f;
        PredictedGrowth = 0.0f;
        RetentionRisk = 0.0f;
        BalanceScore = 0.5f;
    }
};

// Wrapper structs for complex TMap values (UE5 reflection system requirement)
USTRUCT(BlueprintType)
struct TGCORE_API FTGResourceBonusMap
{
    GENERATED_BODY()

    UPROPERTY()
    TMap<ETerritoryResourceType, FTGAdvancedResourceBonus> ResourceBonuses;

    FTGResourceBonusMap()
    {
        ResourceBonuses.Empty();
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGTestMetricArray
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<float> Values;

    FTGTestMetricArray()
    {
        Values.Empty();
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGTestMetricMap
{
    GENERATED_BODY()

    UPROPERTY()
    TMap<FString, FTGTestMetricArray> MetricData;

    FTGTestMetricMap()
    {
        MetricData.Empty();
    }
};

// Enhanced events for advanced analytics
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnAdvancedResourceBonusUpdated, int32, FactionId, ETerritoryResourceType, ResourceType, float, NewValue, float, AnalyticalConfidence);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritorialPerformanceAnalyzed, int32, FactionId, FTGFactionTerritorialPerformance, Performance, TArray<FString>, Recommendations);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnResourceMarketShift, ETerritoryResourceType, ResourceType, float, NewMarketValue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnFactionSynergyDetected, int32, FactionId1, int32, FactionId2, float, SynergyScore, FString, SynergyType);

/**
 * Advanced Territorial Progression Subsystem
 * 
 * Extends the base TerritorialProgressionSubsystem with sophisticated analytics-driven resource bonuses.
 * Integrates machine learning, statistical modeling, and predictive analytics for optimal game balance.
 * 
 * KEY ADVANCED FEATURES:
 * - Analytics-driven resource bonus calculations using statistical models
 * - Real-time market equilibrium adjustments based on supply/demand analysis
 * - Predictive faction performance analysis with retention risk assessment
 * - A/B testing framework for resource bonus optimization
 * - Machine learning-based faction synergy detection and bonuses
 * - Economic equilibrium maintenance through automated balance adjustments
 * - Advanced territorial metrics tracking for data-driven game design decisions
 * 
 * STATISTICAL METHODOLOGIES INTEGRATED:
 * - Monte Carlo simulations for resource bonus optimization
 * - Regression analysis for faction performance prediction
 * - Time series analysis for market trend forecasting
 * - Clustering analysis for faction synergy detection
 * - ANOVA testing for resource bonus impact validation
 * - Causal inference for determining true balance effects
 * 
 * BUSINESS INTELLIGENCE FEATURES:
 * - Player retention correlation with territorial performance
 * - Revenue impact analysis of resource bonus changes
 * - Churn prediction based on territorial engagement patterns
 * - Competitive balance maintenance for long-term player satisfaction
 * - Real-time anomaly detection for exploits and balance issues
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGAdvancedTerritorialProgressionSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UTGAdvancedTerritorialProgressionSubsystem();

    // UGameInstanceSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Advanced Resource Bonus System - Analytics Integration
    UFUNCTION(BlueprintCallable, Category = "Advanced Territorial")
    FTGAdvancedResourceBonus CalculateAdvancedResourceBonus(int32 FactionId, ETerritoryResourceType ResourceType, int32 TerritoryId);

    UFUNCTION(BlueprintCallable, Category = "Advanced Territorial")
    void UpdateResourceBonusWithAnalytics(int32 FactionId, ETerritoryResourceType ResourceType, float AnalyticalMultiplier, float ConfidenceLevel);

    UFUNCTION(BlueprintPure, Category = "Advanced Territorial")
    float GetAnalyticsAdjustedResourceBonus(int32 FactionId, ETerritoryResourceType ResourceType);

    // Territorial Performance Analytics
    UFUNCTION(BlueprintCallable, Category = "Performance Analytics")
    FTGFactionTerritorialPerformance AnalyzeFactionPerformance(int32 FactionId);

    UFUNCTION(BlueprintCallable, Category = "Performance Analytics")
    TArray<FTGFactionTerritorialPerformance> GeneratePerformanceReport();

    UFUNCTION(BlueprintCallable, Category = "Performance Analytics")
    TArray<FString> GenerateFactionRecommendations(int32 FactionId);

    // Market Equilibrium Analysis
    UFUNCTION(BlueprintPure, Category = "Market Analysis")
    FTGTerritorialResourceMetrics GetResourceMarketMetrics(ETerritoryResourceType ResourceType);

    UFUNCTION(BlueprintCallable, Category = "Market Analysis")
    void UpdateMarketEquilibrium();

    UFUNCTION(BlueprintPure, Category = "Market Analysis")
    float GetResourceMarketValue(ETerritoryResourceType ResourceType);

    // Faction Synergy System
    UFUNCTION(BlueprintCallable, Category = "Faction Synergy")
    float CalculateFactionSynergyBonus(int32 PrimaryFactionId, int32 AlliedFactionId, ETerritoryResourceType ResourceType);

    UFUNCTION(BlueprintCallable, Category = "Faction Synergy")
    TArray<int32> GetCompatibleFactions(int32 FactionId);

    UFUNCTION(BlueprintPure, Category = "Faction Synergy")
    bool AreFactionsSynergistic(int32 FactionId1, int32 FactionId2);

    // Predictive Balance System
    UFUNCTION(BlueprintCallable, Category = "Predictive Balance")
    void RunBalancePredictionModel();

    UFUNCTION(BlueprintCallable, Category = "Predictive Balance")
    TMap<int32, float> PredictFactionPerformance(float TimeHorizonHours = 168.0f);

    UFUNCTION(BlueprintCallable, Category = "Predictive Balance")
    void ApplyPredictiveBalanceAdjustments();

    // A/B Testing Integration
    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    void AssignPlayerToResourceBonusTest(FString PlayerId, int32 FactionId, FName TestName);

    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    bool IsPlayerInTestGroup(FString PlayerId, FName TestName);

    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    void RecordTestMetric(FName TestName, FString MetricName, float Value);

    // Real-time Balance Monitoring
    UFUNCTION(BlueprintCallable, Category = "Balance Monitoring")
    void CheckBalanceHealth();

    UFUNCTION(BlueprintCallable, Category = "Balance Monitoring")
    TArray<FString> DetectBalanceAnomalies();

    UFUNCTION(BlueprintCallable, Category = "Balance Monitoring")
    void TriggerEmergencyBalanceAdjustment(FString Reason);

    // Advanced Analytics Queries
    UFUNCTION(BlueprintPure, Category = "Analytics")
    float GetFactionRetentionRisk(int32 FactionId);

    UFUNCTION(BlueprintPure, Category = "Analytics")
    float GetTerritorialEngagementScore(int32 FactionId);

    UFUNCTION(BlueprintCallable, Category = "Analytics")
    void GenerateBusinessIntelligenceReport();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Advanced Events")
    FOnAdvancedResourceBonusUpdated OnAdvancedResourceBonusUpdated;

    UPROPERTY(BlueprintAssignable, Category = "Advanced Events")
    FOnTerritorialPerformanceAnalyzed OnTerritorialPerformanceAnalyzed;

    UPROPERTY(BlueprintAssignable, Category = "Advanced Events")
    FOnResourceMarketShift OnResourceMarketShift;

    UPROPERTY(BlueprintAssignable, Category = "Advanced Events")
    FOnFactionSynergyDetected OnFactionSynergyDetected;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Advanced Config")
    float AnalyticsUpdateInterval = 60.0f; // 1 minute for detailed analytics

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Advanced Config")
    float BalanceMonitoringInterval = 300.0f; // 5 minutes for balance checks

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Advanced Config")
    float MarketUpdateInterval = 180.0f; // 3 minutes for market equilibrium updates

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance Config")
    float AutoBalanceThreshold = 0.15f; // 15% imbalance triggers auto-adjustment

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance Config")
    float MaxAutoAdjustment = 0.10f; // Maximum 10% automatic adjustment per cycle

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Synergy Config")
    float MinSynergyThreshold = 0.6f; // Minimum synergy score to apply bonuses

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Synergy Config")
    float MaxSynergyBonus = 0.25f; // Maximum 25% synergy bonus

protected:
    // Advanced Resource Bonus Data
    UPROPERTY()
    TMap<int32, FTGResourceBonusMap> FactionResourceBonuses;

    // Market metrics tracking
    UPROPERTY()
    TMap<ETerritoryResourceType, FTGTerritorialResourceMetrics> ResourceMarketMetrics;

    // Performance analytics cache
    UPROPERTY()
    TMap<int32, FTGFactionTerritorialPerformance> FactionPerformanceCache;

    // A/B testing data
    UPROPERTY()
    TMap<FString, FName> PlayerTestAssignments; // PlayerId -> TestName

    UPROPERTY()
    TMap<FName, FTGTestMetricMap> TestMetrics; // TestName -> MetricName -> Values

    // Timer handles for advanced processing
    FTimerHandle AdvancedAnalyticsTimer;
    FTimerHandle BalanceMonitoringTimer;
    FTimerHandle MarketUpdateTimer;

    // Subsystem references
    UPROPERTY()
    UTGTerritorialProgressionSubsystem* BaseProgressionSubsystem;

    UPROPERTY()
    UTGTerritorialResourceAnalytics* ResourceAnalytics;

    UPROPERTY()
    UTGTrustSubsystem* TrustSubsystem;

    UPROPERTY()
    UTGTerritorialManager* TerritorialManager;

    UPROPERTY()
    UTGConvoyEconomySubsystem* ConvoyEconomySubsystem;

    UPROPERTY()
    UTGCodexSubsystem* CodexSubsystem;

    // Core processing functions
    void ProcessAdvancedAnalytics();
    void UpdateResourceMarketMetrics();
    void AnalyzeFactionSynergies();
    void UpdatePredictiveModels();

    // Balance management
    void DetectAndCorrectImbalances();
    void ApplyEquilibriumAdjustments();
    void ValidateBalanceChanges();

    // Faction synergy calculations
    float CalculateTerritorySynergyScore(int32 FactionId1, int32 FactionId2);
    void UpdateFactionSynergyBonuses();

    // A/B testing utilities
    FName AssignToTestGroup(FString PlayerId, const TArray<FName>& TestGroups);
    void AnalyzeTestResults(FName TestName);

    // Performance optimization
    void OptimizeAdvancedAnalyticsMemory();
    void UpdatePerformanceCache();

    // Thread safety
    mutable FCriticalSection AdvancedAnalyticsMutex;

private:
    // Performance tracking
    double LastAdvancedAnalyticsUpdate = 0.0;
    double LastBalanceCheck = 0.0;
    double LastMarketUpdate = 0.0;

    // Emergency balance state
    bool bEmergencyBalanceMode = false;
    FDateTime LastEmergencyAdjustment;

    // Statistical model state
    TArray<float> BalanceHistoryBuffer;
    int32 MaxBalanceHistorySize = 1000;

    // Initialization helpers
    void InitializeAdvancedResourceBonuses();
    void InitializeMarketMetrics();
    void LoadAdvancedHistoricalData();
};