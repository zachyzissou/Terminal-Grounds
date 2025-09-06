#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/World.h"
#include "Misc/DateTime.h"
#include "TGIntegratedTerritorialTestSuite.generated.h"

// Forward declarations
class UTGTerritorialProgressionSubsystem;
class UTGTrustSubsystem;
class UTGConvoyEconomySubsystem;
class UTGPerformanceMonitoringSystem;

// Performance targets for integrated testing
USTRUCT(BlueprintType)
struct TGCORE_API FTGIntegratedPerformanceTargets
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    float TargetFPS = 60.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    float MaxFrameTimeMS = 16.67f; // 60 FPS target

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    float MaxMemoryUsageMB = 8192.0f; // 8GB target

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    float MaxNetworkLatencyMS = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    float MaxDatabaseQueryTimeMS = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    int32 MinConcurrentPlayers = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets")
    float MaxCrossSystemSyncTimeMS = 100.0f; // Max time for cross-system synchronization
};

// Integration test result structure
USTRUCT(BlueprintType)
struct TGCORE_API FTGIntegrationTestResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Test Result")
    FString PhaseName;

    UPROPERTY(BlueprintReadOnly, Category = "Test Result")
    FDateTime TestStartTime;

    UPROPERTY(BlueprintReadOnly, Category = "Test Result")
    FDateTime TestEndTime;

    UPROPERTY(BlueprintReadOnly, Category = "Test Result")
    TMap<FString, bool> TestResults;

    UPROPERTY(BlueprintReadOnly, Category = "Test Result")
    bool OverallSuccess = false;

    FTGIntegrationTestResult()
    {
        TestStartTime = FDateTime::Now();
        TestEndTime = FDateTime::Now();
        OverallSuccess = false;
    }
};

// Test scenario definition for load testing
USTRUCT(BlueprintType)
struct TGCORE_API FTGLoadTestScenario
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test")
    FString ScenarioName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test")
    int32 ConcurrentPlayers = 25;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test")
    float TestDurationSeconds = 60.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test")
    float TerritorialUpdatesPerSecond = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test")
    float EconomicTransactionsPerSecond = 5.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test")
    float AIDecisionsPerSecond = 7.0f;

    FTGLoadTestScenario()
    {
        ScenarioName = TEXT("Default Test");
        ConcurrentPlayers = 25;
        TestDurationSeconds = 60.0f;
        TerritorialUpdatesPerSecond = 10.0f;
        EconomicTransactionsPerSecond = 5.0f;
        AIDecisionsPerSecond = 7.0f;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnIntegrationTestCompleted, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTestPhaseCompleted, FString, PhaseName, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnPerformanceViolation, FString, ViolationType, float, MeasuredValue, float, TargetValue);

/**
 * Integrated Territorial Test Suite
 * 
 * Comprehensive integration testing framework for all three phases of the territorial warfare system.
 * Validates cross-system data flow, performance under load, and production readiness.
 * 
 * TESTING SCOPE:
 * - Phase 1: Enhanced TerritorialExtractionPoint, Trust system integration, Splice events, TerritorialProgressionSubsystem
 * - Phase 2: Dynamic convoy routes, supply chain disruption, economic victory conditions, territorial resource bonuses
 * - Phase 3: Cross-faction diplomacy, seasonal campaigns, adaptive AI, territorial cascade effects
 * - Cross-Phase: End-to-end integration, database consistency, WebSocket integration, performance validation
 * 
 * PERFORMANCE VALIDATION:
 * - 100+ concurrent players (120 for stress testing - 20% above target)
 * - 60+ FPS frame rate validation under full load
 * - <1ms database query performance with all systems active
 * - <50ms network latency with all territorial updates
 * - <8GB memory usage optimization
 * 
 * INTEGRATION POINTS TESTED:
 * - TerritorialExtractionPoint ↔ Trust system coordination
 * - Convoy routes ↔ Territorial control synchronization  
 * - Economic warfare ↔ Diplomatic alliance integration
 * - AI behavior ↔ Cascade effects coordination
 * - Seasonal campaigns ↔ All subsystem adaptation
 */
UCLASS(BlueprintType, Blueprintable, ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class TGCORE_API UTGIntegratedTerritorialTestSuite : public UActorComponent
{
    GENERATED_BODY()

public:
    UTGIntegratedTerritorialTestSuite();

protected:
    virtual void BeginPlay() override;

public:
    // Main Testing Interface
    UFUNCTION(BlueprintCallable, Category = "Integration Testing")
    void RunComprehensiveIntegrationTest();

    UFUNCTION(BlueprintCallable, Category = "Integration Testing")
    void RunPhaseSpecificTest(int32 PhaseNumber);

    UFUNCTION(BlueprintCallable, Category = "Integration Testing")
    void RunPerformanceStressTest(int32 ConcurrentPlayers = 120);

    UFUNCTION(BlueprintCallable, Category = "Integration Testing")
    void RunLoadTestScenario(const FTGLoadTestScenario& Scenario);

    // Phase-Specific Testing
    UFUNCTION(BlueprintCallable, Category = "Phase Testing")
    void ExecutePhase1IntegrationTests();

    UFUNCTION(BlueprintCallable, Category = "Phase Testing")
    void ExecutePhase2IntegrationTests();

    UFUNCTION(BlueprintCallable, Category = "Phase Testing")
    void ExecutePhase3IntegrationTests();

    UFUNCTION(BlueprintCallable, Category = "Phase Testing")
    void ExecuteCrossPhaseIntegrationTests();

    UFUNCTION(BlueprintCallable, Category = "Performance Testing")
    void ExecutePerformanceStressTests();

    // Individual Integration Test Methods
    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestTerritorialExtractionTrustIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestSpliceEventsTerritorialIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestProgressionSubsystemPerformance(int32 SimulatedPlayerCount);

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestPhase1DataConsistency();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestConvoyTerritorialSynchronization();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestSupplyChainDisruptionIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestEconomicVictoryConditionsIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestTerritorialResourceBonusPerformance();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestCrossFactionDiplomacyIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestSeasonalCampaignSystemIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestAdaptiveAIPerformanceIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestTerritorialCascadeEffectsIntegration();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestEndToEndTerritorialWarfareScenario();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestAllSystemsDataFlowValidation();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestCrossPhasesDatabaseConsistency();

    UFUNCTION(BlueprintCallable, Category = "Individual Tests")
    bool TestWebSocketServerIntegrationLoad();

    // Performance Stress Tests
    UFUNCTION(BlueprintCallable, Category = "Performance Tests")
    bool TestConcurrentPlayersLoad(int32 PlayerCount);

    UFUNCTION(BlueprintCallable, Category = "Performance Tests")
    bool TestFrameRateValidationUnderLoad();

    UFUNCTION(BlueprintCallable, Category = "Performance Tests")
    bool TestMemoryUsageOptimization();

    UFUNCTION(BlueprintCallable, Category = "Performance Tests")
    bool TestNetworkLatencyValidation();

    UFUNCTION(BlueprintCallable, Category = "Performance Tests")
    bool TestDatabaseQueryPerformanceUnderLoad();

    // Results and Reporting
    UFUNCTION(BlueprintPure, Category = "Test Results")
    TArray<FTGIntegrationTestResult> GetTestResults() const { return TestResults; }

    UFUNCTION(BlueprintPure, Category = "Test Results")
    bool GetOverallTestSuccess() const { return OverallTestSuccess; }

    UFUNCTION(BlueprintPure, Category = "Test Results")
    FTGIntegratedPerformanceTargets GetPerformanceTargets() const { return IntegratedPerformanceTargets; }

    UFUNCTION(BlueprintCallable, Category = "Test Results")
    void GenerateIntegrationTestReport();

    UFUNCTION(BlueprintCallable, Category = "Test Results")
    void GenerateOptimizationRecommendations();

    UFUNCTION(BlueprintCallable, Category = "Test Results")
    void ExportTestResultsToFile(const FString& FilePath);

    // Configuration
    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void SetPerformanceTargets(const FTGIntegratedPerformanceTargets& NewTargets);

    UFUNCTION(BlueprintCallable, Category = "Configuration")
    void ConfigureLoadTestScenario(const FTGLoadTestScenario& Scenario);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Test Events")
    FOnIntegrationTestCompleted OnIntegrationTestCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Test Events")
    FOnTestPhaseCompleted OnTestPhaseCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Test Events")
    FOnPerformanceViolation OnPerformanceViolation;

    // Performance Targets Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    FTGIntegratedPerformanceTargets IntegratedPerformanceTargets;

    // Load Test Scenarios
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Load Test Configuration")
    TArray<FTGLoadTestScenario> LoadTestScenarios;

    // Test Results Storage
    UPROPERTY(BlueprintReadOnly, Category = "Test Results")
    TArray<FTGIntegrationTestResult> TestResults;

    UPROPERTY(BlueprintReadOnly, Category = "Test Results")
    bool OverallTestSuccess = true;

    UPROPERTY(BlueprintReadOnly, Category = "Test Results")
    FDateTime TestStartTime;

protected:
    // Internal test environment setup
    void InitializeTestEnvironment();
    bool IsTestEnvironmentReady() const;

    // Helper functions
    bool CalculatePhaseSuccess(const TMap<FString, bool>& TestResults) const;
    void LogTestProgress(const FString& TestName, bool bSuccess) const;

    // Subsystem access helpers - cached for performance
    UTGTerritorialProgressionSubsystem* GetTerritorialProgressionSubsystem() const;
    UTGTrustSubsystem* GetTrustSubsystem() const;
    UTGConvoyEconomySubsystem* GetConvoyEconomySubsystem() const;
    UTGPerformanceMonitoringSystem* GetPerformanceMonitoringSystem() const;

private:
    // Cached subsystem references for performance
    UPROPERTY()
    UTGTerritorialProgressionSubsystem* TerritorialProgressionSubsystem;

    UPROPERTY()
    UTGTrustSubsystem* TrustSubsystem;

    UPROPERTY()
    UTGConvoyEconomySubsystem* ConvoyEconomySubsystem;

    UPROPERTY()
    UTGPerformanceMonitoringSystem* PerformanceMonitoringSystem;

    // Test execution state
    bool bTestEnvironmentReady = false;
    int32 CurrentTestPhase = 0;
    float TestExecutionProgress = 0.0f;
};