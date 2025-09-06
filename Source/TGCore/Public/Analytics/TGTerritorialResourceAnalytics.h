#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Stats/Stats.h"
#include "TerritorialProgressionSubsystem.h"
#include "TGTerritorialResourceAnalytics.generated.h"

// Forward declarations
class UTGTrustSubsystem;
class UTGTerritorialManager;
class UTGConvoyEconomySubsystem;

DECLARE_STATS_GROUP(TEXT("TGTerritorialResourceAnalytics"), STATGROUP_TGTerritorialResourceAnalytics, STATCAT_Advanced);

/**
 * Statistical Models for Resource Distribution Analysis
 * Data-driven approach to territorial resource bonus optimization
 */

UENUM(BlueprintType)
enum class ETerritoryEconomicClass : uint8
{
    HighValue       UMETA(DisplayName = "High Value"),      // Strategic/Military territories
    MediumValue     UMETA(DisplayName = "Medium Value"),    // Industrial/Research territories  
    LowValue        UMETA(DisplayName = "Low Value"),       // Economic territories
    SpecialValue    UMETA(DisplayName = "Special Value")    // Unique/Event territories
};

UENUM(BlueprintType)
enum class EResourceScarcityLevel : uint8
{
    Abundant        UMETA(DisplayName = "Abundant"),        // 80%+ availability
    Common          UMETA(DisplayName = "Common"),          // 50-80% availability
    Scarce          UMETA(DisplayName = "Scarce"),          // 20-50% availability
    Critical        UMETA(DisplayName = "Critical")         // <20% availability
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGResourceValueDistribution
{
    GENERATED_BODY()

    // Statistical distribution parameters for resource generation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Statistics")
    float MeanValue = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Statistics")
    float StandardDeviation = 25.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Statistics")
    float MinValue = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Statistics")
    float MaxValue = 200.0f;

    // Temporal variance for dynamic resource generation
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Statistics")
    float TemporalVariance = 0.15f; // 15% variance over time

    // Economic equilibrium target
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economics")
    float EquilibriumTarget = 100.0f;

    FTGResourceValueDistribution()
    {
        MeanValue = 100.0f;
        StandardDeviation = 25.0f;
        MinValue = 50.0f;
        MaxValue = 200.0f;
        TemporalVariance = 0.15f;
        EquilibriumTarget = 100.0f;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGFactionResourcePreference
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    int32 FactionId;

    // Resource type preference multipliers (statistical weights)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Preferences")
    TMap<ETerritoryResourceType, float> ResourceAffinityMultipliers;

    // Territory control probability modifiers based on resource value
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Probability")
    float TerritoryControlProbabilityBase = 0.5f; // Base 50% control chance

    // Faction-specific strategic preferences (affects AI behavior)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Strategy")
    float AggressionFactor = 1.0f; // How likely to contest territories

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Strategy")
    float EconomicFocus = 1.0f; // Preference for economic territories

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Strategy")
    float MilitaryFocus = 1.0f; // Preference for military territories

    FTGFactionResourcePreference()
    {
        FactionId = 0;
        TerritoryControlProbabilityBase = 0.5f;
        AggressionFactor = 1.0f;
        EconomicFocus = 1.0f;
        MilitaryFocus = 1.0f;
        
        // Initialize default resource affinities
        ResourceAffinityMultipliers.Add(ETerritoryResourceType::Industrial, 1.0f);
        ResourceAffinityMultipliers.Add(ETerritoryResourceType::Military, 1.0f);
        ResourceAffinityMultipliers.Add(ETerritoryResourceType::Research, 1.0f);
        ResourceAffinityMultipliers.Add(ETerritoryResourceType::Economic, 1.0f);
        ResourceAffinityMultipliers.Add(ETerritoryResourceType::Strategic, 1.0f);
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGTerritorialControlPrediction
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    int32 TerritoryId;

    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    int32 CurrentControllerFactionId;

    // Probability each faction will control this territory (0.0-1.0)
    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    TMap<int32, float> FactionControlProbabilities;

    // Predicted resource output under different control scenarios
    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    TMap<int32, float> PredictedResourceOutput;

    // Strategic value to each faction
    UPROPERTY(BlueprintReadOnly, Category = "Prediction")
    TMap<int32, float> StrategicValueToFaction;

    // Confidence intervals for predictions
    UPROPERTY(BlueprintReadOnly, Category = "Statistics")
    float ConfidenceLevel = 0.95f;

    UPROPERTY(BlueprintReadOnly, Category = "Statistics")
    float PredictionAccuracy = 0.0f; // Historical accuracy tracking

    FTGTerritorialControlPrediction()
    {
        TerritoryId = 0;
        CurrentControllerFactionId = 0;
        ConfidenceLevel = 0.95f;
        PredictionAccuracy = 0.0f;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGResourceBonusAnalytics
{
    GENERATED_BODY()

    // Performance metrics for A/B testing
    UPROPERTY(BlueprintReadOnly, Category = "Analytics")
    float PlayerRetentionImpact = 0.0f; // Correlation with retention

    UPROPERTY(BlueprintReadOnly, Category = "Analytics")
    float EngagementScore = 0.0f; // Player engagement with territorial content

    UPROPERTY(BlueprintReadOnly, Category = "Analytics")
    float CompetitiveBalance = 0.0f; // Measure of faction balance (0-1, 1=perfect balance)

    // Statistical significance testing results
    UPROPERTY(BlueprintReadOnly, Category = "Statistics")
    float StatisticalSignificance = 0.0f; // P-value for bonus impact

    UPROPERTY(BlueprintReadOnly, Category = "Statistics")
    float EffectSize = 0.0f; // Cohen's d for practical significance

    UPROPERTY(BlueprintReadOnly, Category = "Statistics")
    int32 SampleSize = 0; // Number of observations

    // Real-time balance monitoring
    UPROPERTY(BlueprintReadOnly, Category = "Balance")
    float GiniCoefficient = 0.0f; // Resource distribution inequality measure

    UPROPERTY(BlueprintReadOnly, Category = "Balance")
    float HerfindahlIndex = 0.0f; // Market concentration measure for territories

    FTGResourceBonusAnalytics()
    {
        PlayerRetentionImpact = 0.0f;
        EngagementScore = 0.0f;
        CompetitiveBalance = 0.0f;
        StatisticalSignificance = 0.0f;
        EffectSize = 0.0f;
        SampleSize = 0;
        GiniCoefficient = 0.0f;
        HerfindahlIndex = 0.0f;
    }
};

// Event declarations for analytics integration
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnResourceBonusAnalyticsUpdated, ETerritoryResourceType, ResourceType, float, NewValue, float, ConfidenceInterval);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerritorialPredictionGenerated, int32, TerritoryId, FTGTerritorialControlPrediction, Prediction);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnBalanceAnomalyDetected, FString, AnomalyType, float, Severity, FString, RecommendedAction);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnFactionPerformancePrediction, int32, FactionId, float, PredictedWinRate, float, RetentionRisk, FString, Recommendations);

/**
 * Territorial Resource Analytics Subsystem
 * 
 * Provides data-driven statistical analysis for territorial resource systems.
 * Uses advanced statistical modeling to predict faction performance, balance competitive play,
 * and optimize resource bonus values through A/B testing and machine learning techniques.
 * 
 * KEY ANALYTICS FEATURES:
 * - Statistical resource value distribution modeling with confidence intervals
 * - Faction-specific preference analysis using collaborative filtering approaches  
 * - Territorial control probability models using logistic regression
 * - Economic equilibrium analysis with real-time balance monitoring
 * - Predictive analytics for faction performance and player retention
 * - A/B testing framework with statistical significance testing
 * - Anomaly detection for cheating, exploits, and balance issues
 * 
 * STATISTICAL METHODOLOGIES:
 * - Monte Carlo simulations for resource generation optimization
 * - Bayesian inference for faction preference modeling
 * - Time series analysis for territorial control forecasting
 * - Chi-square tests for competitive balance validation
 * - ANOVA for resource bonus impact assessment
 * - Causal inference for true effect measurement
 * 
 * PERFORMANCE TARGETS:
 * - <5ms analytics query response time
 * - >95% prediction accuracy for territorial control
 * - <0.05 p-value threshold for statistical significance
 * - Real-time processing for 100+ concurrent players
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGTerritorialResourceAnalytics : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UTGTerritorialResourceAnalytics();

    // UGameInstanceSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Statistical Resource Distribution Analysis
    UFUNCTION(BlueprintCallable, Category = "Resource Analytics")
    FTGResourceValueDistribution CalculateResourceDistribution(ETerritoryResourceType ResourceType, ETerritoryEconomicClass EconomicClass);

    UFUNCTION(BlueprintCallable, Category = "Resource Analytics") 
    float GenerateResourceValue(ETerritoryResourceType ResourceType, int32 TerritoryId, float RandomSeed = -1.0f);

    UFUNCTION(BlueprintCallable, Category = "Resource Analytics")
    EResourceScarcityLevel AnalyzeResourceScarcity(ETerritoryResourceType ResourceType, int32 RegionId = -1);

    // Faction Performance Prediction
    UFUNCTION(BlueprintCallable, Category = "Faction Analytics")
    FTGTerritorialControlPrediction PredictTerritorialControl(int32 TerritoryId, float TimeHorizonHours = 24.0f);

    UFUNCTION(BlueprintCallable, Category = "Faction Analytics")
    TMap<int32, float> PredictFactionWinRates(float TimeHorizonHours = 168.0f); // 1 week default

    UFUNCTION(BlueprintCallable, Category = "Faction Analytics")
    float CalculateFactionResourceEfficiency(int32 FactionId);

    // Competitive Balance Analysis
    UFUNCTION(BlueprintPure, Category = "Balance Analytics")
    float CalculateCompetitiveBalance(); // Returns 0-1, 1 = perfect balance

    UFUNCTION(BlueprintCallable, Category = "Balance Analytics")
    TArray<FString> GenerateBalanceRecommendations();

    UFUNCTION(BlueprintCallable, Category = "Balance Analytics")
    bool DetectBalanceAnomaly(FString& AnomalyType, float& Severity);

    // A/B Testing Framework
    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    void StartResourceBonusTest(FName TestName, ETerritoryResourceType ResourceType, float ControlValue, float TestValue, int32 DurationHours = 72);

    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    FTGResourceBonusAnalytics AnalyzeTestResults(FName TestName);

    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    bool IsTestStatisticallySignificant(FName TestName, float Alpha = 0.05f);

    // Real-time Analytics Integration
    UFUNCTION(BlueprintCallable, Category = "Real-time Analytics")
    void RecordTerritorialEvent(FString EventType, int32 TerritoryId, int32 FactionId, float Value, const FString& Context);

    UFUNCTION(BlueprintCallable, Category = "Real-time Analytics")
    void UpdatePlayerRetentionMetrics(FString PlayerId, int32 SessionDuration, bool bTerritorialEngagement);

    UFUNCTION(BlueprintPure, Category = "Real-time Analytics")
    FTGResourceBonusAnalytics GetCurrentAnalytics(ETerritoryResourceType ResourceType);

    // Economic Equilibrium Analysis
    UFUNCTION(BlueprintPure, Category = "Economics")
    float CalculateGiniCoefficient(); // Resource inequality measure

    UFUNCTION(BlueprintPure, Category = "Economics")
    float CalculateHerfindahlIndex(); // Territory concentration measure

    UFUNCTION(BlueprintCallable, Category = "Economics")
    TMap<ETerritoryResourceType, float> PredictMarketEquilibrium(float TimeHorizonHours = 24.0f);

    // Faction Synergy Analysis
    UFUNCTION(BlueprintCallable, Category = "Faction Synergy")
    TMap<int32, TArray<int32>> AnalyzeFactionSynergies(); // Returns faction -> compatible factions

    UFUNCTION(BlueprintCallable, Category = "Faction Synergy")
    float CalculateFactionPairSynergyScore(int32 FactionId1, int32 FactionId2);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Analytics Events")
    FOnResourceBonusAnalyticsUpdated OnResourceBonusAnalyticsUpdated;

    UPROPERTY(BlueprintAssignable, Category = "Analytics Events")
    FOnTerritorialPredictionGenerated OnTerritorialPredictionGenerated;

    UPROPERTY(BlueprintAssignable, Category = "Analytics Events")
    FOnBalanceAnomalyDetected OnBalanceAnomalyDetected;

    UPROPERTY(BlueprintAssignable, Category = "Analytics Events")
    FOnFactionPerformancePrediction OnFactionPerformancePrediction;

    // Configuration - Statistical Parameters
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Analytics Config")
    float AnalyticsUpdateInterval = 30.0f; // 30 seconds for real-time updates

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Analytics Config")
    float PredictionConfidenceThreshold = 0.95f; // 95% confidence level

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Analytics Config")
    float BalanceAnomalyThreshold = 0.1f; // 10% deviation triggers anomaly

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Analytics Config")
    int32 MinSampleSizeForSignificance = 30; // Minimum samples for statistical tests

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Statistical Config")
    TMap<ETerritoryResourceType, FTGResourceValueDistribution> ResourceDistributions;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction Config")
    TMap<int32, FTGFactionResourcePreference> FactionPreferences;

protected:
    // Core Analytics Data
    UPROPERTY()
    TMap<FName, FTGResourceBonusAnalytics> ActiveTests;

    UPROPERTY()
    TArray<FDateTime> EventTimestamps; // For time series analysis

    UPROPERTY()
    TMap<FString, float> PlayerRetentionData; // PlayerId -> retention score

    // Cached Analytics Results
    UPROPERTY()
    TMap<ETerritoryResourceType, FTGResourceBonusAnalytics> CachedAnalytics;

    UPROPERTY()
    TMap<int32, FTGTerritorialControlPrediction> CachedPredictions;

    // Performance Tracking
    UPROPERTY()
    TArray<float> AnalyticsProcessingTimes; // For performance monitoring

    // Timer Handles
    FTimerHandle AnalyticsUpdateTimer;
    FTimerHandle PredictionUpdateTimer;

    // Subsystem References
    UPROPERTY()
    UTGTrustSubsystem* TrustSubsystem;

    UPROPERTY()
    UTGTerritorialManager* TerritorialManager;

    UPROPERTY()
    UTGConvoyEconomySubsystem* ConvoyEconomySubsystem;

    UPROPERTY()
    class UTGTerritorialProgressionSubsystem* ProgressionSubsystem;

    // Core Statistical Functions
    void ProcessAnalyticsUpdate();
    void UpdatePredictions();
    void PerformStatisticalAnalysis();
    
    // Statistical Utilities
    float CalculateNormalDistribution(float Mean, float StdDev, float Value);
    float GenerateNormalRandom(float Mean, float StdDev);
    float CalculateCorrelation(const TArray<float>& X, const TArray<float>& Y);
    float PerformTTest(const TArray<float>& Group1, const TArray<float>& Group2);
    float CalculateChiSquare(const TMap<int32, int32>& Observed, const TMap<int32, float>& Expected);

    // Economic Analysis Functions
    void AnalyzeResourceFlows();
    void DetectMarketManipulation();
    void UpdateEconomicEquilibrium();

    // Machine Learning Functions
    void TrainFactionPreferenceModel();
    void UpdatePredictionAccuracy();
    void PerformAnomalyDetection();

    // Thread Safety
    mutable FCriticalSection AnalyticsDataMutex;

private:
    // Performance Optimization
    double LastAnalyticsUpdate = 0.0;
    double LastPredictionUpdate = 0.0;
    
    // Statistical Validation
    bool ValidateStatisticalSignificance(const TArray<float>& ControlGroup, const TArray<float>& TestGroup, float Alpha);
    float CalculateEffectSize(const TArray<float>& ControlGroup, const TArray<float>& TestGroup);
    
    // Initialization
    void InitializeFactionPreferences();
    void InitializeResourceDistributions();
    void LoadHistoricalData();
};