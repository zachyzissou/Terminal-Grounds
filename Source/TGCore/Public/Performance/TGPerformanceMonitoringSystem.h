#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/World.h"
#include "HAL/Platform.h"
#include "TGPerformanceMonitoringSystem.generated.h"

class UTGPerformanceProfiler;
class UTGPerformanceOptimizer;
class UTGSiegePerformanceMonitor;

UENUM(BlueprintType)
enum class ETGPerformanceState : uint8
{
    Optimal = 0,        // 60+ FPS, <50ms latency, <8GB memory
    Good = 1,           // 45+ FPS, <100ms latency, <12GB memory  
    Degraded = 2,       // 30+ FPS, <200ms latency, <16GB memory
    Critical = 3,       // <30 FPS, >200ms latency, >16GB memory
    Emergency = 4       // System failure imminent
};

UENUM(BlueprintType)
enum class ETGMonitoringMode : uint8
{
    Production = 0,     // Minimal overhead monitoring
    Development = 1,    // Detailed profiling with metrics
    Debugging = 2,      // Full diagnostic monitoring
    Benchmarking = 3    // Maximum detail for performance testing
};

USTRUCT(BlueprintType)
struct FTGSystemPerformanceSnapshot
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    float FPS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    float FrameTimeMS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    float GPUTimeMS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    float MemoryUsageMB;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    float NetworkLatencyMS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    float TerritorialQueryTimeMS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    int32 ActivePlayers;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    int32 ProceduralChunksActive;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    int32 AssetGenerationQueueSize;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    ETGPerformanceState PerformanceState;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Snapshot")
    FDateTime Timestamp;

    FTGSystemPerformanceSnapshot()
    {
        FPS = 0.0f;
        FrameTimeMS = 0.0f;
        GPUTimeMS = 0.0f;
        MemoryUsageMB = 0.0f;
        NetworkLatencyMS = 0.0f;
        TerritorialQueryTimeMS = 0.0f;
        ActivePlayers = 0;
        ProceduralChunksActive = 0;
        AssetGenerationQueueSize = 0;
        PerformanceState = ETGPerformanceState::Optimal;
        Timestamp = FDateTime::Now();
    }
};

USTRUCT(BlueprintType)
struct FTGPerformanceBenchmark
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    FString BenchmarkName;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    float DurationSeconds;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    float AverageFPS;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    float MinimumFPS;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    float AverageFrameTimeMS;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    float PeakMemoryMB;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    float AverageLatencyMS;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    int32 MaxConcurrentPlayers;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    bool bPassedTargets;

    UPROPERTY(BlueprintReadOnly, Category = "Benchmark")
    FDateTime ExecutedAt;

    FTGPerformanceBenchmark()
    {
        BenchmarkName = TEXT("");
        DurationSeconds = 0.0f;
        AverageFPS = 0.0f;
        MinimumFPS = 0.0f;
        AverageFrameTimeMS = 0.0f;
        PeakMemoryMB = 0.0f;
        AverageLatencyMS = 0.0f;
        MaxConcurrentPlayers = 0;
        bPassedTargets = false;
        ExecutedAt = FDateTime::MinValue();
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPerformanceStateChanged, ETGPerformanceState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPerformanceSnapshot, const FTGSystemPerformanceSnapshot&, Snapshot);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnBenchmarkCompleted, const FTGPerformanceBenchmark&, Benchmark);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPerformanceAlert, const FString&, AlertMessage);

UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGPerformanceMonitoringSystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UTGPerformanceMonitoringSystem();

    // Subsystem overrides
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;

    // Monitoring control
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void StartMonitoring(ETGMonitoringMode Mode = ETGMonitoringMode::Production);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void StopMonitoring();

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void SetMonitoringMode(ETGMonitoringMode Mode);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void TakePerformanceSnapshot();

    // Performance state management
    UFUNCTION(BlueprintPure, Category = "Performance Monitoring")
    ETGPerformanceState GetCurrentPerformanceState() const { return CurrentPerformanceState; }

    UFUNCTION(BlueprintPure, Category = "Performance Monitoring")
    FTGSystemPerformanceSnapshot GetLatestSnapshot() const { return LatestSnapshot; }

    UFUNCTION(BlueprintPure, Category = "Performance Monitoring")
    TArray<FTGSystemPerformanceSnapshot> GetPerformanceHistory(int32 MaxEntries = 100) const;

    // Benchmarking system
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void StartBenchmark(const FString& BenchmarkName, float DurationSeconds = 60.0f);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void StopBenchmark();

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    TArray<FTGPerformanceBenchmark> GetBenchmarkHistory() const { return BenchmarkHistory; }

    // Automated testing scenarios
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void RunTerritorialWarfareStressTest(int32 PlayerCount = 100, float DurationMinutes = 10.0f);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void RunProceduralGenerationStressTest(int32 ChunkCount = 50, float DurationMinutes = 5.0f);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void RunAssetGenerationStressTest(int32 AssetCount = 100, float DurationMinutes = 15.0f);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void RunComprehensiveStressTest(float DurationMinutes = 30.0f);

    // Performance targets and SLA
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void SetPerformanceTargets(float TargetFPS, float MaxLatencyMS, float MaxMemoryMB);

    UFUNCTION(BlueprintPure, Category = "Performance Monitoring")
    bool ArePerformanceTargetsMet() const;

    UFUNCTION(BlueprintPure, Category = "Performance Monitoring")
    float GetCurrentSLAScore() const; // 0-100% score based on target adherence

    // Real-time alerts and notifications
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void EnablePerformanceAlerts(bool bEnabled);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void SetAlertThresholds(float MinFPS, float MaxLatencyMS, float MaxMemoryMB);

    // Integration with existing systems
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void BindToProfiler(UTGPerformanceProfiler* Profiler);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void BindToOptimizer(UTGPerformanceOptimizer* Optimizer);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    void BindToSiegeMonitor(UTGSiegePerformanceMonitor* SiegeMonitor);

    // Data export and reporting
    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    bool ExportPerformanceReport(const FString& FilePath, bool bIncludeDetailedMetrics = false);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    bool ExportBenchmarkResults(const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category = "Performance Monitoring")
    FString GeneratePerformanceRecommendations();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Performance Monitoring")
    FOnPerformanceStateChanged OnPerformanceStateChanged;

    UPROPERTY(BlueprintAssignable, Category = "Performance Monitoring")
    FOnPerformanceSnapshot OnPerformanceSnapshot;

    UPROPERTY(BlueprintAssignable, Category = "Performance Monitoring")
    FOnBenchmarkCompleted OnBenchmarkCompleted;

    UPROPERTY(BlueprintAssignable, Category = "Performance Monitoring")
    FOnPerformanceAlert OnPerformanceAlert;

protected:
    // Internal monitoring logic
    void UpdatePerformanceState();
    void CheckPerformanceTargets();
    void ProcessPerformanceAlerts();
    
    // Benchmarking implementation
    void UpdateBenchmarkMetrics();
    void CompleteBenchmark();
    
    // Stress test implementations
    void ExecuteTerritorialStressTest();
    void ExecuteProceduralStressTest();
    void ExecuteAssetGenerationStressTest();
    
    // Data collection
    void CollectSystemMetrics(FTGSystemPerformanceSnapshot& Snapshot);
    void AnalyzePerformanceTrends();
    
    // Alert processing
    void TriggerPerformanceAlert(const FString& AlertMessage, ETGPerformanceState Severity);
    void CheckFPSAlert();
    void CheckMemoryAlert();
    void CheckLatencyAlert();
    void CheckTerritorialAlert();

private:
    // Component references
    UPROPERTY()
    UTGPerformanceProfiler* BoundProfiler;

    UPROPERTY()
    UTGPerformanceOptimizer* BoundOptimizer;

    UPROPERTY()
    UTGSiegePerformanceMonitor* BoundSiegeMonitor;

    // Monitoring state
    UPROPERTY()
    bool bMonitoringActive;

    UPROPERTY()
    ETGMonitoringMode CurrentMonitoringMode;

    UPROPERTY()
    ETGPerformanceState CurrentPerformanceState;

    UPROPERTY()
    FTGSystemPerformanceSnapshot LatestSnapshot;

    UPROPERTY()
    TArray<FTGSystemPerformanceSnapshot> PerformanceHistory;

    // Benchmarking state
    UPROPERTY()
    bool bBenchmarkActive;

    UPROPERTY()
    FTGPerformanceBenchmark CurrentBenchmark;

    UPROPERTY()
    TArray<FTGPerformanceBenchmark> BenchmarkHistory;

    UPROPERTY()
    float BenchmarkStartTime;

    // Performance targets
    UPROPERTY()
    float TargetFPS;

    UPROPERTY()
    float MaxLatencyMS;

    UPROPERTY()
    float MaxMemoryMB;

    // Alert settings
    UPROPERTY()
    bool bAlertsEnabled;

    UPROPERTY()
    float AlertMinFPS;

    UPROPERTY()
    float AlertMaxLatencyMS;

    UPROPERTY()
    float AlertMaxMemoryMB;

    // Stress testing state
    UPROPERTY()
    bool bStressTestActive;

    UPROPERTY()
    FString ActiveStressTestName;

    UPROPERTY()
    float StressTestStartTime;

    UPROPERTY()
    float StressTestDuration;

    // Internal timers and counters
    float LastMonitoringUpdate;
    float MonitoringUpdateFrequency;
    int32 MaxHistorySize;
    int32 MaxBenchmarkHistory;
    
    // Performance trend analysis
    float PerformanceTrendWindow;
    TArray<float> FPSTrend;
    TArray<float> MemoryTrend;
    TArray<float> LatencyTrend;
};