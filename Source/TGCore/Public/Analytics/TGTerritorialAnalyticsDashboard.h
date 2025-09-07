#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Analytics/TGTerritorialResourceAnalytics.h"
#include "Analytics/TGAdvancedTerritorialProgressionSubsystem.h"
#include "TGTerritorialAnalyticsDashboard.generated.h"

/**
 * Comprehensive Analytics Dashboard and Configuration Management
 * Provides centralized control and monitoring for territorial resource analytics
 */

UENUM(BlueprintType)
enum class EAnalyticsReportType : uint8
{
    Performance     UMETA(DisplayName = "Faction Performance"),
    Balance         UMETA(DisplayName = "Competitive Balance"),
    Market          UMETA(DisplayName = "Resource Market"),
    Predictions     UMETA(DisplayName = "Predictive Analysis"),
    ABTesting       UMETA(DisplayName = "A/B Test Results"),
    Anomalies       UMETA(DisplayName = "Balance Anomalies"),
    BusinessIntel   UMETA(DisplayName = "Business Intelligence")
};

UENUM(BlueprintType)
enum class EAnalyticsAlertLevel : uint8
{
    Info            UMETA(DisplayName = "Information"),
    Warning         UMETA(DisplayName = "Warning"),
    Critical        UMETA(DisplayName = "Critical"),
    Emergency       UMETA(DisplayName = "Emergency")
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGAnalyticsAlert
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    FDateTime Timestamp;

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    EAnalyticsAlertLevel Level;

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    FString Title;

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    FString Description;

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    FString RecommendedAction;

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    TArray<int32> AffectedFactions;

    UPROPERTY(BlueprintReadOnly, Category = "Alert")
    bool bAutoResolved = false;

    FTGAnalyticsAlert()
    {
        Timestamp = FDateTime::Now();
        Level = EAnalyticsAlertLevel::Info;
        bAutoResolved = false;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGAnalyticsConfiguration
{
    GENERATED_BODY()

    // Performance monitoring settings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance")
    bool bEnableRealTimeAnalytics = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance")
    bool bEnablePerformanceLogging = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance")
    float AnalyticsTargetUpdateTime = 5.0f; // Target <5ms for analytics queries

    // Balance monitoring settings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    bool bEnableAutoBalance = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    bool bEnableEmergencyBalance = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    float BalanceThreshold = 0.15f; // 15% imbalance threshold

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Balance")
    float EmergencyThreshold = 0.05f; // 5% balance triggers emergency

    // A/B Testing settings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Testing")
    bool bEnableABTesting = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Testing")
    int32 MinSampleSizeForSignificance = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Testing")
    float StatisticalSignificanceAlpha = 0.05f; // 95% confidence

    // Prediction settings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Predictions")
    bool bEnablePredictiveModels = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Predictions")
    float PredictionAccuracyTarget = 0.85f; // Target 85% accuracy

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Predictions")
    int32 PredictionHorizonHours = 168; // 1 week default

    // Alert settings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alerts")
    bool bEnableAnalyticsAlerts = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alerts")
    int32 MaxAlertsPerHour = 10;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alerts")
    bool bAutoResolveAlerts = true;

    FTGAnalyticsConfiguration()
    {
        bEnableRealTimeAnalytics = true;
        bEnablePerformanceLogging = true;
        AnalyticsTargetUpdateTime = 5.0f;
        bEnableAutoBalance = true;
        bEnableEmergencyBalance = true;
        BalanceThreshold = 0.15f;
        EmergencyThreshold = 0.05f;
        bEnableABTesting = true;
        MinSampleSizeForSignificance = 100;
        StatisticalSignificanceAlpha = 0.05f;
        bEnablePredictiveModels = true;
        PredictionAccuracyTarget = 0.85f;
        PredictionHorizonHours = 168;
        bEnableAnalyticsAlerts = true;
        MaxAlertsPerHour = 10;
        bAutoResolveAlerts = true;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGAnalyticsReport
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    EAnalyticsReportType ReportType;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    FDateTime GeneratedTime;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    FString ReportTitle;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    FString ExecutiveSummary;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    TArray<FString> KeyFindings;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    TArray<FString> Recommendations;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    TMap<FString, float> Metrics;

    UPROPERTY(BlueprintReadOnly, Category = "Report")
    float OverallScore = 0.0f; // 0-1 scale

    FTGAnalyticsReport()
    {
        GeneratedTime = FDateTime::Now();
        OverallScore = 0.0f;
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGBusinessIntelligence
{
    GENERATED_BODY()

    // Player engagement metrics
    UPROPERTY(BlueprintReadOnly, Category = "Engagement")
    float AverageSessionDuration = 0.0f; // Hours

    UPROPERTY(BlueprintReadOnly, Category = "Engagement")
    float TerritorialEngagementRate = 0.0f; // 0-1 scale

    UPROPERTY(BlueprintReadOnly, Category = "Engagement")
    float PlayerRetentionRate = 0.0f; // 0-1 scale

    // Revenue correlation metrics
    UPROPERTY(BlueprintReadOnly, Category = "Revenue")
    float RevenuePerPlayer = 0.0f; // Average revenue

    UPROPERTY(BlueprintReadOnly, Category = "Revenue")
    float TerritorialEngagementRevenueCorrelation = 0.0f; // -1 to 1

    UPROPERTY(BlueprintReadOnly, Category = "Revenue")
    float BalanceQualityRevenueImpact = 0.0f; // Revenue impact of balance

    // Competitive health metrics
    UPROPERTY(BlueprintReadOnly, Category = "Competition")
    float CompetitiveBalanceScore = 0.0f; // 0-1 scale

    UPROPERTY(BlueprintReadOnly, Category = "Competition")
    float FactionDiversityIndex = 0.0f; // 0-1 scale, 1=perfect diversity

    UPROPERTY(BlueprintReadOnly, Category = "Competition")
    float MatchQualityScore = 0.0f; // 0-1 scale

    // Churn prediction
    UPROPERTY(BlueprintReadOnly, Category = "Churn")
    TMap<int32, float> FactionChurnRisk; // FactionId -> Risk (0-1)

    UPROPERTY(BlueprintReadOnly, Category = "Churn")
    float OverallChurnRisk = 0.0f; // 0-1 scale

    UPROPERTY(BlueprintReadOnly, Category = "Churn")
    TArray<FString> ChurnPreventionRecommendations;

    FTGBusinessIntelligence()
    {
        AverageSessionDuration = 0.0f;
        TerritorialEngagementRate = 0.0f;
        PlayerRetentionRate = 0.0f;
        RevenuePerPlayer = 0.0f;
        TerritorialEngagementRevenueCorrelation = 0.0f;
        BalanceQualityRevenueImpact = 0.0f;
        CompetitiveBalanceScore = 0.0f;
        FactionDiversityIndex = 0.0f;
        MatchQualityScore = 0.0f;
        OverallChurnRisk = 0.0f;
    }
};

// Wrapper for TArray in TMap (UE5 reflection system requirement)
USTRUCT(BlueprintType)
struct TGCORE_API FTGPerformanceMetricsArray
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<float> ProcessingTimes;

    FTGPerformanceMetricsArray()
    {
        ProcessingTimes.Empty();
    }
};

// Dashboard events
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAnalyticsAlert, FTGAnalyticsAlert, Alert);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAnalyticsReportGenerated, EAnalyticsReportType, ReportType, FTGAnalyticsReport, Report);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnBusinessIntelligenceUpdated, FTGBusinessIntelligence, BusinessIntel);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnAnalyticsPerformanceAlert, FString, SystemName, float, ActualTime, float, TargetTime);

/**
 * Territorial Analytics Dashboard
 * 
 * Centralized command and control center for all territorial resource analytics.
 * Provides comprehensive monitoring, alerting, reporting, and configuration management
 * for the sophisticated analytics systems powering Terminal Grounds' competitive balance.
 * 
 * KEY DASHBOARD FEATURES:
 * - Real-time analytics monitoring with performance tracking
 * - Automated alert system for balance anomalies and system issues
 * - Comprehensive reporting suite for different stakeholder needs
 * - Business intelligence integration for revenue and engagement correlation
 * - A/B testing management and statistical significance validation
 * - Configuration management for all analytics parameters
 * - Emergency response system for critical balance failures
 * 
 * BUSINESS INTELLIGENCE CAPABILITIES:
 * - Player retention correlation with territorial engagement
 * - Revenue impact analysis of balance changes
 * - Churn prediction and prevention recommendations
 * - Competitive health assessment and optimization
 * - Faction diversity monitoring for long-term game health
 * 
 * STAKEHOLDER REPORTING:
 * - Executive dashboards with high-level KPIs and trends
 * - Designer reports with detailed balance metrics and recommendations
 * - Developer reports with performance metrics and technical alerts
 * - Business reports with revenue correlation and player behavior insights
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGTerritorialAnalyticsDashboard : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UTGTerritorialAnalyticsDashboard();

    // UGameInstanceSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Dashboard Management
    UFUNCTION(BlueprintCallable, Category = "Analytics Dashboard")
    void InitializeDashboard();

    UFUNCTION(BlueprintCallable, Category = "Analytics Dashboard")
    void UpdateDashboard();

    UFUNCTION(BlueprintPure, Category = "Analytics Dashboard")
    bool IsDashboardHealthy();

    // Configuration Management
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void UpdateAnalyticsConfiguration(const FTGAnalyticsConfiguration& NewConfig);

    UFUNCTION(BlueprintPure, Category = "Configuration")
    FTGAnalyticsConfiguration GetAnalyticsConfiguration() const { return AnalyticsConfig; }

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void ResetToDefaultConfiguration();

    // Alert Management
    UFUNCTION(BlueprintCallable, Category = "Alerts")
    void CreateAlert(EAnalyticsAlertLevel Level, const FString& Title, const FString& Description, const FString& RecommendedAction, const TArray<int32>& AffectedFactions);

    UFUNCTION(BlueprintCallable, Category = "Alerts", CallInEditor)
    void CreateAlertSimple(EAnalyticsAlertLevel Level, const FString& Title, const FString& Description, const FString& RecommendedAction) { CreateAlert(Level, Title, Description, RecommendedAction, TArray<int32>()); }

    UFUNCTION(BlueprintPure, Category = "Alerts")
    TArray<FTGAnalyticsAlert> GetActiveAlerts() const;

    UFUNCTION(BlueprintPure, Category = "Alerts")
    TArray<FTGAnalyticsAlert> GetRecentAlerts(int32 Hours = 24) const;

    UFUNCTION(BlueprintCallable, Category = "Alerts")
    void ResolveAlert(int32 AlertIndex);

    UFUNCTION(BlueprintCallable, Category = "Alerts")
    void ClearOldAlerts(int32 MaxAgeHours = 168); // 1 week default

    // Reporting System
    UFUNCTION(BlueprintCallable, Category = "Reports")
    FTGAnalyticsReport GenerateReport(EAnalyticsReportType ReportType);

    UFUNCTION(BlueprintCallable, Category = "Reports")
    TArray<FTGAnalyticsReport> GenerateAllReports();

    UFUNCTION(BlueprintCallable, Category = "Reports")
    FString ExportReportToJSON(const FTGAnalyticsReport& Report);

    UFUNCTION(BlueprintCallable, Category = "Reports")
    void ScheduleAutomaticReports(EAnalyticsReportType ReportType, int32 IntervalHours);

    // Business Intelligence
    UFUNCTION(BlueprintCallable, Category = "Business Intelligence")
    FTGBusinessIntelligence GenerateBusinessIntelligence();

    UFUNCTION(BlueprintPure, Category = "Business Intelligence")
    float GetPlayerRetentionCorrelation(int32 FactionId);

    UFUNCTION(BlueprintPure, Category = "Business Intelligence")
    TArray<FString> GetChurnPreventionRecommendations();

    UFUNCTION(BlueprintCallable, Category = "Business Intelligence")
    void UpdateRevenueMetrics(float TotalRevenue, int32 ActivePlayers);

    // Performance Monitoring
    UFUNCTION(BlueprintPure, Category = "Performance")
    float GetAnalyticsPerformanceScore(); // 0-1 scale

    UFUNCTION(BlueprintPure, Category = "Performance")
    TMap<FString, float> GetSystemPerformanceMetrics();

    UFUNCTION(BlueprintCallable, Category = "Performance")
    void RecordAnalyticsPerformance(const FString& SystemName, float ProcessingTimeMs);

    // A/B Testing Management
    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    void CreateABTest(const FString& TestName, const FString& Description, int32 DurationHours);

    UFUNCTION(BlueprintPure, Category = "A/B Testing")
    TArray<FString> GetActiveABTests();

    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    FTGAnalyticsReport AnalyzeABTestResults(const FString& TestName);

    UFUNCTION(BlueprintCallable, Category = "A/B Testing")
    void EndABTest(const FString& TestName, bool bImplementWinner);

    // Emergency Response
    UFUNCTION(BlueprintCallable, Category = "Emergency Response")
    void TriggerEmergencyResponse(const FString& Reason);

    UFUNCTION(BlueprintPure, Category = "Emergency Response")
    bool IsInEmergencyMode() const { return bEmergencyMode; }

    UFUNCTION(BlueprintCallable, Category = "Emergency Response")
    void ExitEmergencyMode();

    // Analytics System Health
    UFUNCTION(BlueprintPure, Category = "System Health")
    float GetOverallSystemHealth(); // 0-1 scale

    UFUNCTION(BlueprintPure, Category = "System Health")
    TArray<FString> GetSystemHealthIssues();

    UFUNCTION(BlueprintCallable, Category = "System Health")
    void RunSystemHealthCheck();

    // Data Export and Integration
    UFUNCTION(BlueprintCallable, Category = "Data Export")
    FString ExportAnalyticsDataToCSV(int32 DaysBack = 7);

    UFUNCTION(BlueprintCallable, Category = "Data Export")
    void SendTelemetryData(); // Send to external analytics service

    UFUNCTION(BlueprintCallable, Category = "Data Export")
    void BackupAnalyticsDatabase();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Dashboard Events")
    FOnAnalyticsAlert OnAnalyticsAlert;

    UPROPERTY(BlueprintAssignable, Category = "Dashboard Events")
    FOnAnalyticsReportGenerated OnAnalyticsReportGenerated;

    UPROPERTY(BlueprintAssignable, Category = "Dashboard Events")
    FOnBusinessIntelligenceUpdated OnBusinessIntelligenceUpdated;

    UPROPERTY(BlueprintAssignable, Category = "Dashboard Events")
    FOnAnalyticsPerformanceAlert OnAnalyticsPerformanceAlert;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dashboard Config")
    FTGAnalyticsConfiguration AnalyticsConfig;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dashboard Config")
    float DashboardUpdateInterval = 30.0f; // 30 seconds

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dashboard Config")
    int32 MaxAlertHistory = 500;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dashboard Config")
    bool bEnableAdvancedLogging = false;

protected:
    // Core data
    UPROPERTY()
    TArray<FTGAnalyticsAlert> AlertHistory;

    UPROPERTY()
    TMap<EAnalyticsReportType, FTGAnalyticsReport> CachedReports;

    UPROPERTY()
    FTGBusinessIntelligence CurrentBusinessIntel;

    UPROPERTY()
    TMap<FString, FTGPerformanceMetricsArray> PerformanceMetrics; // SystemName -> ProcessingTimes

    UPROPERTY()
    TArray<FString> ActiveABTests;

    // Emergency state
    UPROPERTY()
    bool bEmergencyMode = false;

    UPROPERTY()
    FDateTime EmergencyModeStartTime;

    // Timer handles
    FTimerHandle DashboardUpdateTimer;
    FTimerHandle ReportGenerationTimer;
    FTimerHandle SystemHealthTimer;

    // Subsystem references
    UPROPERTY()
    UTGTerritorialResourceAnalytics* ResourceAnalytics;

    UPROPERTY()
    UTGAdvancedTerritorialProgressionSubsystem* AdvancedProgression;

    // Core dashboard functions
    void ProcessDashboardUpdate();
    void GenerateAutomaticReports();
    void MonitorSystemHealth();
    void CheckAlertThresholds();

    // Report generation functions
    FTGAnalyticsReport GeneratePerformanceReport();
    FTGAnalyticsReport GenerateBalanceReport();
    FTGAnalyticsReport GenerateMarketReport();
    FTGAnalyticsReport GeneratePredictionsReport();
    FTGAnalyticsReport GenerateABTestingReport();
    FTGAnalyticsReport GenerateAnomaliesReport();
    FTGAnalyticsReport GenerateBusinessIntelReport();

    // Business intelligence functions
    void UpdateBusinessIntelligence();
    float CalculatePlayerRetentionCorrelation();
    TArray<FString> GenerateChurnPreventionRecommendations();

    // Performance tracking
    void UpdatePerformanceMetrics();
    float CalculateSystemHealth();

    // Emergency response
    void HandleEmergencyCondition(const FString& Condition);
    void ExecuteEmergencyProtocols();

    // Thread safety
    mutable FCriticalSection DashboardMutex;

private:
    // Performance tracking
    double LastDashboardUpdate = 0.0;
    int32 TotalAlertsThisHour = 0;
    FDateTime HourlyAlertReset;

    // Health monitoring
    TArray<float> SystemHealthHistory;
    static constexpr int32 MaxHealthHistorySize = 100;

    // Revenue tracking (simplified for demonstration)
    float TotalRevenue = 0.0f;
    int32 TotalActivePlayers = 0;
};