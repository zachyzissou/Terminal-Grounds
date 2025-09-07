#include "Performance/TGPerformanceProfiler.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Stats/StatsData.h"
#include "RenderingThread.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/GameNetworkManager.h"
#include "Net/UnrealNetwork.h"
#include "PhaseGateComponent.h"
#include "DominanceMeterComponent.h"
#include "Persistence/TGTerritorialPersistenceSubsystem.h"

UTGPerformanceProfiler::UTGPerformanceProfiler()
{
    bProfilingEnabled = false;
    LastUpdateTime = 0.0f;
    ProfilingStartTime = 0.0f;
    LastFrameTime = 0.0;
    
    bDetailedProfilingActive = false;
    DetailedProfilingEndTime = 0.0f;
    
    TerritorialManager = nullptr;
    PlayerController = nullptr;
    
    // Performance thresholds optimized for siege warfare
    MinAcceptableFPS = 60.0f;
    CriticalFPSThreshold = 45.0f;
    MaxAcceptableFrameTime = 16.67f; // 60 FPS target
    MaxAcceptableGPUTime = 12.0f;
    MaxMemoryUsageMB = 8192.0f; // 8GB limit
    MaxNetworkLatency = 50.0f; // <50ms for territorial updates
    MaxTerritorialQueryTime = 1.0f; // <1ms for database queries
}

bool UTGPerformanceProfiler::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void UTGPerformanceProfiler::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    InitializePerformanceLogging();
    
    // Cache system references for performance
    if (UWorld* World = GetWorld())
    {
        TerritorialManager = World->GetSubsystem<class UTGTerritorialManager>();
        if (World->GetFirstPlayerController())
        {
            PlayerController = World->GetFirstPlayerController();
        }
    }
    
    // Start profiling automatically
    StartProfiling();
}

void UTGPerformanceProfiler::Deinitialize()
{
    StopProfiling();
    
    // Final save of performance data
    if (bSavePerformanceLogs)
    {
        SavePerformanceData();
    }
    
    Super::Deinitialize();
}

void UTGPerformanceProfiler::StartProfiling()
{
    if (bProfilingEnabled)
    {
        return;
    }
    
    bProfilingEnabled = true;
    ProfilingStartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
    LastUpdateTime = ProfilingStartTime;
    
    // Clear previous data
    ActiveAlerts.Empty();
    FPSHistory.Empty();
    FrameTimeHistory.Empty();
    RecentFrameTimes.Empty();
    
    UE_LOG(LogTemp, Log, TEXT("Performance Profiler Started - Target: 60+ FPS, <50ms Network Latency"));
}

void UTGPerformanceProfiler::StopProfiling()
{
    if (!bProfilingEnabled)
    {
        return;
    }
    
    bProfilingEnabled = false;
    
    // Save final metrics
    if (bSavePerformanceLogs)
    {
        SavePerformanceData();
    }
    
    UE_LOG(LogTemp, Log, TEXT("Performance Profiler Stopped"));
}

void UTGPerformanceProfiler::Tick(float DeltaTime)
{
    if (!bProfilingEnabled)
    {
        return;
    }
    
    float CurrentTime = GetWorld()->GetTimeSeconds();
    
    // Update at specified frequency
    if (CurrentTime - LastUpdateTime >= (1.0f / UpdateFrequency))
    {
        // Collect all performance metrics
        CollectFrameMetrics();
        CollectGPUMetrics();
        CollectMemoryMetrics();
        CollectNetworkMetrics();
        CollectTerritorialMetrics();
        
        // Check thresholds and trigger alerts
        CheckPerformanceThresholds();
        
        // Automatic optimization if enabled
        if (bEnableAutomaticOptimization)
        {
            AttemptAutomaticOptimization();
        }
        
        // Log metrics if enabled
        if (bLogPerformanceMetrics)
        {
            LogCurrentMetrics();
        }
        
        // Broadcast metrics update
        OnMetricsUpdate.Broadcast(CurrentMetrics);
        
        LastUpdateTime = CurrentTime;
    }
    
    // Handle detailed profiling timeout
    if (bDetailedProfilingActive && CurrentTime >= DetailedProfilingEndTime)
    {
        bDetailedProfilingActive = false;
        
        // Export detailed profiling report
        FString DetailedReportPath = GetPerformanceLogPath() + TEXT("_DetailedProfile.csv");
        ExportPerformanceReport(DetailedReportPath);
    }
}

TArray<FTGPerformanceAlert> UTGPerformanceProfiler::GetActiveAlerts() const
{
    return ActiveAlerts;
}

void UTGPerformanceProfiler::TriggerGarbageCollection()
{
    UE_LOG(LogTemp, Warning, TEXT("Performance Profiler: Triggering Garbage Collection"));
    
    if (GEngine)
    {
        GEngine->ForceGarbageCollection(true);
    }
}

void UTGPerformanceProfiler::OptimizeRenderingSettings()
{
    UE_LOG(LogTemp, Warning, TEXT("Performance Profiler: Applying Rendering Optimizations"));
    
    ApplyRenderingOptimizations();
}

void UTGPerformanceProfiler::FlushTerritorialCache()
{
    UE_LOG(LogTemp, Warning, TEXT("Performance Profiler: Flushing Territorial Cache"));
    
    if (TerritorialManager)
    {
        // Flush any cached territorial data
        // TerritorialManager->FlushCache();
    }
}

void UTGPerformanceProfiler::StartDetailedProfiling(float Duration)
{
    bDetailedProfilingActive = true;
    DetailedProfilingEndTime = GetWorld()->GetTimeSeconds() + Duration;
    DetailedMetricsHistory.Empty();
    
    UE_LOG(LogTemp, Log, TEXT("Starting Detailed Performance Profiling for %.1f seconds"), Duration);
}

void UTGPerformanceProfiler::ExportPerformanceReport(const FString& FilePath)
{
    TArray<FString> ReportLines;
    
    // CSV Header
    ReportLines.Add(TEXT("Timestamp,FPS,FrameTime,GPUTime,MemoryMB,NetworkLatency,TerritorialQueryTime,ActiveTerritories"));
    
    // Add detailed metrics if available
    for (const FTGPerformanceMetrics& Metrics : DetailedMetricsHistory)
    {
        FString Line = FString::Printf(TEXT("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.3f,%d"),
            GetWorld()->GetTimeSeconds(),
            Metrics.CurrentFPS,
            Metrics.FrameTime,
            Metrics.GPUTime,
            Metrics.UsedPhysicalMemoryMB,
            Metrics.NetworkLatency,
            Metrics.TerritorialQueryTime,
            Metrics.ActiveTerritories
        );
        ReportLines.Add(Line);
    }
    
    // Add current metrics summary
    ReportLines.Add(TEXT(""));
    ReportLines.Add(TEXT("SUMMARY"));
    ReportLines.Add(FString::Printf(TEXT("Average FPS,%.2f"), CurrentMetrics.AverageFPS));
    ReportLines.Add(FString::Printf(TEXT("Minimum FPS,%.2f"), CurrentMetrics.MinFPS));
    ReportLines.Add(FString::Printf(TEXT("Average GPU Time,%.2f"), CurrentMetrics.GPUTime));
    ReportLines.Add(FString::Printf(TEXT("Peak Memory Usage,%.2f MB"), CurrentMetrics.UsedPhysicalMemoryMB));
    ReportLines.Add(FString::Printf(TEXT("Peak Network Latency,%.2f ms"), CurrentMetrics.NetworkLatency));
    
    FString ReportContent = FString::Join(ReportLines, TEXT("\n"));
    FFileHelper::SaveStringToFile(ReportContent, *FilePath);
    
    UE_LOG(LogTemp, Log, TEXT("Performance Report Exported to: %s"), *FilePath);
}

// Protected Methods

void UTGPerformanceProfiler::CollectFrameMetrics()
{
    if (!GEngine || !GEngine->GameViewport)
    {
        return;
    }
    
    // Get frame rate from engine
    float CurrentFPS = 1.0f / FApp::GetDeltaTime();
    CurrentMetrics.CurrentFPS = CurrentFPS;
    CurrentMetrics.FrameTime = FApp::GetDeltaTime() * 1000.0f; // Convert to milliseconds
    
    // Update FPS history
    FPSHistory.Add(CurrentFPS);
    FrameTimeHistory.Add(CurrentMetrics.FrameTime);
    
    if (FPSHistory.Num() > MaxHistorySize)
    {
        FPSHistory.RemoveAt(0);
        FrameTimeHistory.RemoveAt(0);
    }
    
    // Calculate average and minimum FPS
    if (FPSHistory.Num() > 0)
    {
        float TotalFPS = 0.0f;
        float MinFPS = FPSHistory[0];
        
        for (float FPS : FPSHistory)
        {
            TotalFPS += FPS;
            MinFPS = FMath::Min(MinFPS, FPS);
        }
        
        CurrentMetrics.AverageFPS = TotalFPS / FPSHistory.Num();
        CurrentMetrics.MinFPS = MinFPS;
    }
}

void UTGPerformanceProfiler::CollectGPUMetrics()
{
    // GPU timing from render thread
    if (IsInGameThread())
    {
        ENQUEUE_RENDER_COMMAND(CollectGPUMetrics)(
            [this](FRHICommandListImmediate& RHICmdList)
            {
                // Collect GPU timing data
                // This is a simplified version - real implementation would use GPU timing queries
                CurrentMetrics.GPUTime = 10.0f; // Placeholder - implement proper GPU timing
                CurrentMetrics.RenderThreadTime = 8.0f; // Placeholder
            });
    }
    
    // Draw call and triangle count (estimated)
    CurrentMetrics.DrawCalls = 1000; // Placeholder - get from render stats
    CurrentMetrics.Triangles = 50000; // Placeholder - get from render stats
}

void UTGPerformanceProfiler::CollectMemoryMetrics()
{
    // Physical memory usage
    FPlatformMemoryStats MemStats = FPlatformMemory::GetStats();
    CurrentMetrics.UsedPhysicalMemoryMB = (float)MemStats.UsedPhysical / (1024.0f * 1024.0f);
    CurrentMetrics.UsedVirtualMemoryMB = (float)MemStats.UsedVirtual / (1024.0f * 1024.0f);
    
    // Texture memory (estimated)
    CurrentMetrics.TextureMemoryMB = 1024.0f; // Placeholder - get from texture streaming
}

void UTGPerformanceProfiler::CollectNetworkMetrics()
{
    if (PlayerController && PlayerController->PlayerState)
    {
        // Network latency (ping)
        CurrentMetrics.NetworkLatency = PlayerController->PlayerState->ExactPing;
        
        // Network bandwidth estimation
        if (AGameNetworkManager* NetworkManager = GetWorld()->GetGameNetworkManager())
        {
            CurrentMetrics.PacketsPerSecond = 60; // Placeholder
            CurrentMetrics.NetworkBandwidth = 1024.0f; // Placeholder - KB/s
        }
    }
}

void UTGPerformanceProfiler::CollectTerritorialMetrics()
{
    double StartTime = FPlatformTime::Seconds();
    
    // Simulate territorial query timing
    if (TerritorialManager)
    {
        // Measure time for territorial operations
        // This would call actual territorial query functions
        CurrentMetrics.ActiveTerritories = 10; // Placeholder
        CurrentMetrics.TerritorialUpdatesPerSecond = 5; // Placeholder
    }
    
    double EndTime = FPlatformTime::Seconds();
    CurrentMetrics.TerritorialQueryTime = (EndTime - StartTime) * 1000.0f; // Convert to milliseconds
    
    // Store for detailed profiling
    if (bDetailedProfilingActive)
    {
        DetailedMetricsHistory.Add(CurrentMetrics);
    }
}

void UTGPerformanceProfiler::CheckPerformanceThresholds()
{
    ClearResolvedAlerts();
    
    // Frame rate alerts
    if (CurrentMetrics.CurrentFPS < CriticalFPSThreshold)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Critical, TEXT("Frame Rate"), 
            TEXT("FPS below critical threshold"), CurrentMetrics.CurrentFPS, CriticalFPSThreshold);
    }
    else if (CurrentMetrics.CurrentFPS < MinAcceptableFPS)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Warning, TEXT("Frame Rate"),
            TEXT("FPS below target"), CurrentMetrics.CurrentFPS, MinAcceptableFPS);
    }
    
    // Frame time alerts
    if (CurrentMetrics.FrameTime > MaxAcceptableFrameTime * 1.5f)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Critical, TEXT("Frame Time"),
            TEXT("Frame time significantly above target"), CurrentMetrics.FrameTime, MaxAcceptableFrameTime);
    }
    else if (CurrentMetrics.FrameTime > MaxAcceptableFrameTime)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Warning, TEXT("Frame Time"),
            TEXT("Frame time above target"), CurrentMetrics.FrameTime, MaxAcceptableFrameTime);
    }
    
    // Memory alerts
    if (CurrentMetrics.UsedPhysicalMemoryMB > MaxMemoryUsageMB)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Critical, TEXT("Memory"),
            TEXT("Memory usage above limit"), CurrentMetrics.UsedPhysicalMemoryMB, MaxMemoryUsageMB);
    }
    else if (CurrentMetrics.UsedPhysicalMemoryMB > MaxMemoryUsageMB * 0.8f)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Warning, TEXT("Memory"),
            TEXT("High memory usage"), CurrentMetrics.UsedPhysicalMemoryMB, MaxMemoryUsageMB);
    }
    
    // Network alerts
    if (CurrentMetrics.NetworkLatency > MaxNetworkLatency * 2.0f)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Critical, TEXT("Network"),
            TEXT("Network latency critically high"), CurrentMetrics.NetworkLatency, MaxNetworkLatency);
    }
    else if (CurrentMetrics.NetworkLatency > MaxNetworkLatency)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Warning, TEXT("Network"),
            TEXT("Network latency above target"), CurrentMetrics.NetworkLatency, MaxNetworkLatency);
    }
    
    // Territorial system alerts
    if (CurrentMetrics.TerritorialQueryTime > MaxTerritorialQueryTime * 2.0f)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Critical, TEXT("Territorial"),
            TEXT("Territorial queries too slow"), CurrentMetrics.TerritorialQueryTime, MaxTerritorialQueryTime);
    }
    else if (CurrentMetrics.TerritorialQueryTime > MaxTerritorialQueryTime)
    {
        TriggerAlert(ETGPerformanceAlertLevel::Warning, TEXT("Territorial"),
            TEXT("Territorial query time above target"), CurrentMetrics.TerritorialQueryTime, MaxTerritorialQueryTime);
    }
}

void UTGPerformanceProfiler::TriggerAlert(ETGPerformanceAlertLevel Level, const FString& System, const FString& Message, float Value, float Threshold)
{
    FTGPerformanceAlert Alert;
    Alert.AlertLevel = Level;
    Alert.SystemName = System;
    Alert.AlertMessage = Message;
    Alert.Value = Value;
    Alert.Threshold = Threshold;
    Alert.Timestamp = FDateTime::Now();
    
    ActiveAlerts.Add(Alert);
    OnPerformanceAlert.Broadcast(Alert);
    
    // Log alert
    FString LevelText;
    switch (Level)
    {
        case ETGPerformanceAlertLevel::Warning:
            LevelText = TEXT("WARNING");
            break;
        case ETGPerformanceAlertLevel::Critical:
            LevelText = TEXT("CRITICAL");
            break;
        case ETGPerformanceAlertLevel::Emergency:
            LevelText = TEXT("EMERGENCY");
            break;
        default:
            LevelText = TEXT("INFO");
            break;
    }
    
    UE_LOG(LogTemp, Warning, TEXT("PERFORMANCE %s [%s]: %s (%.2f > %.2f)"), 
        *LevelText, *System, *Message, Value, Threshold);
}

void UTGPerformanceProfiler::ClearResolvedAlerts()
{
    // Remove alerts that are no longer applicable
    ActiveAlerts.RemoveAll([this](const FTGPerformanceAlert& Alert) {
        // Check if the alert condition is resolved
        if (Alert.SystemName == TEXT("Frame Rate") && CurrentMetrics.CurrentFPS >= Alert.Threshold)
            return true;
        if (Alert.SystemName == TEXT("Memory") && CurrentMetrics.UsedPhysicalMemoryMB <= Alert.Threshold)
            return true;
        if (Alert.SystemName == TEXT("Network") && CurrentMetrics.NetworkLatency <= Alert.Threshold)
            return true;
        if (Alert.SystemName == TEXT("Territorial") && CurrentMetrics.TerritorialQueryTime <= Alert.Threshold)
            return true;
            
        return false;
    });
}

void UTGPerformanceProfiler::AttemptAutomaticOptimization()
{
    // Only optimize if we have critical performance issues
    bool bHasCriticalAlert = ActiveAlerts.ContainsByPredicate([](const FTGPerformanceAlert& Alert) {
        return Alert.AlertLevel == ETGPerformanceAlertLevel::Critical;
    });
    
    if (!bHasCriticalAlert)
    {
        return;
    }
    
    UE_LOG(LogTemp, Warning, TEXT("Performance Profiler: Attempting Automatic Optimization"));
    
    // Apply optimizations in order of effectiveness
    ApplyMemoryOptimizations();
    ApplyRenderingOptimizations();
    ApplyLODOptimizations();
}

void UTGPerformanceProfiler::ApplyLODOptimizations()
{
    // Reduce LOD distances for better performance
    if (UWorld* World = GetWorld())
    {
        // Implementation would adjust LOD settings
        UE_LOG(LogTemp, Warning, TEXT("Applying LOD Optimizations"));
    }
}

void UTGPerformanceProfiler::ApplyRenderingOptimizations()
{
    // Reduce shadow quality, post-processing effects, etc.
    UE_LOG(LogTemp, Warning, TEXT("Applying Rendering Optimizations"));
    
    // Implementation would adjust console variables
    // IConsoleManager::Get().FindConsoleVariable(TEXT("r.ShadowQuality"))->Set(2);
}

void UTGPerformanceProfiler::ApplyMemoryOptimizations()
{
    // Trigger garbage collection and flush caches
    UE_LOG(LogTemp, Warning, TEXT("Applying Memory Optimizations"));
    
    TriggerGarbageCollection();
    FlushTerritorialCache();
}

void UTGPerformanceProfiler::LogCurrentMetrics()
{
    UE_LOG(LogTemp, Log, TEXT("PERFORMANCE METRICS - FPS: %.1f | Frame: %.1fms | GPU: %.1fms | Memory: %.0fMB | Latency: %.0fms | Territorial: %.2fms"),
        CurrentMetrics.CurrentFPS,
        CurrentMetrics.FrameTime,
        CurrentMetrics.GPUTime,
        CurrentMetrics.UsedPhysicalMemoryMB,
        CurrentMetrics.NetworkLatency,
        CurrentMetrics.TerritorialQueryTime);
}

void UTGPerformanceProfiler::SavePerformanceData()
{
    if (!bSavePerformanceLogs)
    {
        return;
    }
    
    FString LogPath = GetPerformanceLogPath();
    TArray<FString> LogLines;
    
    // Performance summary
    LogLines.Add(FString::Printf(TEXT("Performance Summary - %s"), *FDateTime::Now().ToString()));
    LogLines.Add(FString::Printf(TEXT("Session Duration: %.1f seconds"), GetWorld()->GetTimeSeconds() - ProfilingStartTime));
    LogLines.Add(FString::Printf(TEXT("Average FPS: %.2f"), CurrentMetrics.AverageFPS));
    LogLines.Add(FString::Printf(TEXT("Minimum FPS: %.2f"), CurrentMetrics.MinFPS));
    LogLines.Add(FString::Printf(TEXT("Peak Memory: %.0f MB"), CurrentMetrics.UsedPhysicalMemoryMB));
    LogLines.Add(FString::Printf(TEXT("Peak Latency: %.0f ms"), CurrentMetrics.NetworkLatency));
    LogLines.Add(FString::Printf(TEXT("Max Territorial Query Time: %.3f ms"), CurrentMetrics.TerritorialQueryTime));
    
    // Active alerts
    LogLines.Add(TEXT(""));
    LogLines.Add(TEXT("Active Alerts:"));
    for (const FTGPerformanceAlert& Alert : ActiveAlerts)
    {
        LogLines.Add(FString::Printf(TEXT("  [%s] %s: %s"), 
            *Alert.SystemName, *UEnum::GetValueAsString(Alert.AlertLevel), *Alert.AlertMessage));
    }
    
    FString LogContent = FString::Join(LogLines, TEXT("\n"));
    FFileHelper::SaveStringToFile(LogContent, *LogPath);
}

FString UTGPerformanceProfiler::GetPerformanceLogPath() const
{
    FString LogDir = FPaths::ProjectLogDir() / TEXT("Performance");
    FString LogFile = FString::Printf(TEXT("SiegePerformance_%s.txt"), 
        *FDateTime::Now().ToString(TEXT("%Y%m%d_%H%M%S")));
    return LogDir / LogFile;
}

void UTGPerformanceProfiler::InitializePerformanceLogging()
{
    if (bSavePerformanceLogs)
    {
        FString LogDir = FPaths::ProjectLogDir() / TEXT("Performance");
        IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
        
        if (!PlatformFile.DirectoryExists(*LogDir))
        {
            PlatformFile.CreateDirectoryTree(*LogDir);
        }
    }
}