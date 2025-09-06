#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/Engine.h"
#include "Stats/Stats.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/DateTime.h"
#include "TGPerformanceProfiler.generated.h"

// Performance metrics structure
USTRUCT(BlueprintType)
struct TGCORE_API FTGPerformanceMetrics
{
    GENERATED_BODY()

    // Frame rate metrics
    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float CurrentFPS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float AverageFPS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float MinFPS;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float FrameTime;

    // GPU metrics
    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float GPUTime;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float RenderThreadTime;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    int32 DrawCalls;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    int32 Triangles;

    // Memory metrics
    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float UsedPhysicalMemoryMB;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float UsedVirtualMemoryMB;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float TextureMemoryMB;

    // Network metrics
    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float NetworkLatency;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    int32 PacketsPerSecond;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float NetworkBandwidth;

    // Territorial system metrics
    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    float TerritorialQueryTime;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    int32 ActiveTerritories;

    UPROPERTY(BlueprintReadOnly, Category = "Performance")
    int32 TerritorialUpdatesPerSecond;

    FTGPerformanceMetrics()
    {
        CurrentFPS = 0.0f;
        AverageFPS = 0.0f;
        MinFPS = 0.0f;
        FrameTime = 0.0f;
        GPUTime = 0.0f;
        RenderThreadTime = 0.0f;
        DrawCalls = 0;
        Triangles = 0;
        UsedPhysicalMemoryMB = 0.0f;
        UsedVirtualMemoryMB = 0.0f;
        TextureMemoryMB = 0.0f;
        NetworkLatency = 0.0f;
        PacketsPerSecond = 0;
        NetworkBandwidth = 0.0f;
        TerritorialQueryTime = 0.0f;
        ActiveTerritories = 0;
        TerritorialUpdatesPerSecond = 0;
    }
};

// Performance alert levels
UENUM(BlueprintType)
enum class ETGPerformanceAlertLevel : uint8
{
    None = 0,
    Warning = 1,
    Critical = 2,
    Emergency = 3
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGPerformanceAlert
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Performance Alert")
    ETGPerformanceAlertLevel AlertLevel;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Alert")
    FString AlertMessage;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Alert")
    FString SystemName;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Alert")
    float Value;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Alert")
    float Threshold;

    UPROPERTY(BlueprintReadOnly, Category = "Performance Alert")
    FDateTime Timestamp;

    FTGPerformanceAlert()
    {
        AlertLevel = ETGPerformanceAlertLevel::None;
        Value = 0.0f;
        Threshold = 0.0f;
        Timestamp = FDateTime::Now();
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPerformanceAlert, const FTGPerformanceAlert&, Alert);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPerformanceMetricsUpdate, const FTGPerformanceMetrics&, Metrics);

/**
 * Terminal Grounds Performance Profiler
 * Comprehensive performance monitoring system for 60+ FPS targets
 * Monitors CPU, GPU, Memory, Network, and Territorial subsystem performance
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGPerformanceProfiler : public UWorldSubsystem, public FTickableGameObject
{
    GENERATED_BODY()

public:
    UTGPerformanceProfiler();

    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;

    // FTickableGameObject interface
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UTGPerformanceProfiler, STATGROUP_Tickables); }
    virtual bool IsTickable() const override { return !IsTemplate() && bProfilingEnabled; }

    // Profiling controls
    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    void StartProfiling();

    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    void StopProfiling();

    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    bool IsProfilingEnabled() const { return bProfilingEnabled; }

    // Metrics access
    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    FTGPerformanceMetrics GetCurrentMetrics() const { return CurrentMetrics; }

    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    TArray<FTGPerformanceAlert> GetActiveAlerts() const;

    // Performance thresholds configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MinAcceptableFPS = 60.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float CriticalFPSThreshold = 45.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxAcceptableFrameTime = 16.67f; // 60 FPS target

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxAcceptableGPUTime = 12.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxMemoryUsageMB = 8192.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxNetworkLatency = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxTerritorialQueryTime = 1.0f;

    // Monitoring configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    float UpdateFrequency = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    bool bEnableAutomaticOptimization = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    bool bLogPerformanceMetrics = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    bool bSavePerformanceLogs = true;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Performance Events")
    FOnPerformanceAlert OnPerformanceAlert;

    UPROPERTY(BlueprintAssignable, Category = "Performance Events")
    FOnPerformanceMetricsUpdate OnMetricsUpdate;

    // Manual optimization triggers
    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void TriggerGarbageCollection();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeRenderingSettings();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void FlushTerritorialCache();

    // Detailed profiling
    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    void StartDetailedProfiling(float Duration);

    UFUNCTION(BlueprintCallable, Category = "Performance Profiler")
    void ExportPerformanceReport(const FString& FilePath);

protected:
    // Internal state
    UPROPERTY()
    FTGPerformanceMetrics CurrentMetrics;

    UPROPERTY()
    TArray<FTGPerformanceAlert> ActiveAlerts;

    bool bProfilingEnabled;
    float LastUpdateTime;
    float ProfilingStartTime;
    
    // Performance history for averaging
    TArray<float> FPSHistory;
    TArray<float> FrameTimeHistory;
    int32 MaxHistorySize = 60; // 1 minute at 1Hz updates

    // Detailed profiling
    bool bDetailedProfilingActive;
    float DetailedProfilingEndTime;
    TArray<FTGPerformanceMetrics> DetailedMetricsHistory;

    // Internal metric collection
    void CollectFrameMetrics();
    void CollectGPUMetrics();
    void CollectMemoryMetrics();
    void CollectNetworkMetrics();
    void CollectTerritorialMetrics();

    // Alert system
    void CheckPerformanceThresholds();
    void TriggerAlert(ETGPerformanceAlertLevel Level, const FString& System, const FString& Message, float Value, float Threshold);
    void ClearResolvedAlerts();

    // Automatic optimization
    void AttemptAutomaticOptimization();
    void ApplyLODOptimizations();
    void ApplyRenderingOptimizations();
    void ApplyMemoryOptimizations();

    // Logging and reporting
    void LogCurrentMetrics();
    void SavePerformanceData();

private:
    // Performance tracking
    double LastFrameTime;
    TArray<double> RecentFrameTimes;
    
    // System references (cached for performance)
    UPROPERTY()
    class UTGTerritorialManager* TerritorialManager;

    UPROPERTY()
    class APlayerController* PlayerController;

    // File I/O for performance logs
    FString GetPerformanceLogPath() const;
    void InitializePerformanceLogging();
};