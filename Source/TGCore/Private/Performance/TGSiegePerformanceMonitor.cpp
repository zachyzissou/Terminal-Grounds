#include "Performance/TGSiegePerformanceMonitor.h"
#include "Net/UnrealNetwork.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Persistence/TGTerritorialPersistenceSubsystem.h"

UTGSiegePerformanceMonitor::UTGSiegePerformanceMonitor()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 0.5f; // Update every 0.5 seconds
    
    bReplicates = true;
    SetIsReplicatedByDefault(true);
    
    bMonitoringActive = false;
    LastUpdateTime = 0.0f;
    NetworkMessageCounter = 0;
    NetworkBandwidthAccumulator = 0.0f;
    BoundProfiler = nullptr;
    
    // Optimized thresholds for siege warfare
    MaxPhaseTransitionTime = 2000.0f; // 2 seconds max for phase transitions
    MaxDominanceCalculationTime = 16.67f; // Target one frame at 60 FPS
    MaxTicketUpdateTime = 5.0f; // 5ms max for ticket updates
    MaxNetworkMessagesPerSecond = 100; // Reasonable for 100+ players
    MaxReplicationBandwidth = 1024.0f; // 1MB/s per client
    
    UpdateFrequency = 2.0f; // 2 updates per second
    HistorySize = 100; // Keep 50 seconds of history at 2 Hz
}

void UTGSiegePerformanceMonitor::BeginPlay()
{
    Super::BeginPlay();
    
    LastUpdateTime = GetWorld()->GetTimeSeconds();
    
    // Auto-bind to performance profiler if available
    if (UWorld* World = GetWorld())
    {
        if (UTGPerformanceProfiler* Profiler = World->GetSubsystem<UTGPerformanceProfiler>())
        {
            BindToPerformanceProfiler(Profiler);
        }
    }
}

void UTGSiegePerformanceMonitor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (bMonitoringActive)
    {
        StopSiegeMonitoring();
    }
    
    Super::EndPlay(EndPlayReason);
}

void UTGSiegePerformanceMonitor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    
    DOREPLIFETIME(UTGSiegePerformanceMonitor, CurrentPerformanceData);
    DOREPLIFETIME(UTGSiegePerformanceMonitor, bMonitoringActive);
    DOREPLIFETIME(UTGSiegePerformanceMonitor, MonitoringStartTime);
}

void UTGSiegePerformanceMonitor::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    
    if (!bMonitoringActive)
    {
        return;
    }
    
    float CurrentTime = GetWorld()->GetTimeSeconds();
    
    // Update at specified frequency
    if (CurrentTime - LastUpdateTime >= (1.0f / UpdateFrequency))
    {
        UpdatePerformanceData();
        CheckThresholds();
        BroadcastPerformanceUpdate();
        ReportToProfiler();
        
        LastUpdateTime = CurrentTime;
    }
}

void UTGSiegePerformanceMonitor::StartSiegeMonitoring(const FString& SiegeID)
{
    if (bMonitoringActive)
    {
        UE_LOG(LogTemp, Warning, TEXT("Siege Performance Monitor: Already monitoring siege %s"), *CurrentPerformanceData.SiegeID);
        return;
    }
    
    bMonitoringActive = true;
    CurrentPerformanceData.SiegeID = SiegeID;
    MonitoringStartTime = FDateTime::Now();
    
    // Reset all metrics
    CurrentPerformanceData.ParticipantCount = 0;
    CurrentPerformanceData.PhaseTransitionTime = 0.0f;
    CurrentPerformanceData.DominanceCalculationTime = 0.0f;
    CurrentPerformanceData.TicketUpdateTime = 0.0f;
    CurrentPerformanceData.NetworkMessagesPerSecond = 0;
    CurrentPerformanceData.ReplicationBandwidth = 0.0f;
    CurrentPerformanceData.bPerformanceTargetsMet = true;
    
    // Clear history
    PhaseTransitionTimes.Empty();
    DominanceCalculationTimes.Empty();
    TicketUpdateTimes.Empty();
    NetworkMessageHistory.Empty();
    BandwidthHistory.Empty();
    
    NetworkMessageCounter = 0;
    NetworkBandwidthAccumulator = 0.0f;
    
    UE_LOG(LogTemp, Log, TEXT("Siege Performance Monitor: Started monitoring siege %s"), *SiegeID);
}

void UTGSiegePerformanceMonitor::StopSiegeMonitoring()
{
    if (!bMonitoringActive)
    {
        return;
    }
    
    // Final performance report
    if (BoundProfiler)
    {
        ReportToProfiler();
    }
    
    // Save to persistence system
    if (UWorld* World = GetWorld())
    {
        if (UTGTerritorialPersistenceSubsystem* PersistenceSystem = World->GetGameInstance()->GetSubsystem<UTGTerritorialPersistenceSubsystem>())
        {
            FTGSiegePerformanceRecord Record;
            Record.SiegeID = CurrentPerformanceData.SiegeID;
            Record.StartTime = MonitoringStartTime;
            Record.EndTime = FDateTime::Now();
            Record.AverageFPS = BoundProfiler ? BoundProfiler->GetCurrentMetrics().AverageFPS : 60.0f;
            Record.PeakLatency = BoundProfiler ? BoundProfiler->GetCurrentMetrics().NetworkLatency : 0.0f;
            Record.bVictoryAchieved = false; // Set by external siege completion logic
            
            PersistenceSystem->RecordSiegePerformance(CurrentPerformanceData.SiegeID, Record);
        }
    }
    
    bMonitoringActive = false;
    
    UE_LOG(LogTemp, Log, TEXT("Siege Performance Monitor: Stopped monitoring siege %s"), *CurrentPerformanceData.SiegeID);
}

void UTGSiegePerformanceMonitor::RecordPhaseTransition(ESiegePhase FromPhase, ESiegePhase ToPhase, float TransitionTime)
{
    if (!bMonitoringActive)
    {
        return;
    }
    
    PhaseTransitionTimes.Add(TransitionTime);
    CurrentPerformanceData.CurrentPhase = ToPhase;
    CurrentPerformanceData.PhaseTransitionTime = TransitionTime;
    
    OptimizeHistoryArrays();
    
    UE_LOG(LogTemp, VeryVerbose, TEXT("Siege Performance: Phase transition %d->%d took %.2fms"), 
        (int32)FromPhase, (int32)ToPhase, TransitionTime);
}

void UTGSiegePerformanceMonitor::RecordDominanceCalculation(float CalculationTime)
{
    if (!bMonitoringActive)
    {
        return;
    }
    
    DominanceCalculationTimes.Add(CalculationTime);
    CurrentPerformanceData.DominanceCalculationTime = CalculationTime;
    
    OptimizeHistoryArrays();
}

void UTGSiegePerformanceMonitor::RecordTicketUpdate(float UpdateTime)
{
    if (!bMonitoringActive)
    {
        return;
    }
    
    TicketUpdateTimes.Add(UpdateTime);
    CurrentPerformanceData.TicketUpdateTime = UpdateTime;
    
    OptimizeHistoryArrays();
}

void UTGSiegePerformanceMonitor::RecordNetworkActivity(int32 MessagesPerSecond, float BandwidthKBps)
{
    if (!bMonitoringActive)
    {
        return;
    }
    
    NetworkMessageHistory.Add(MessagesPerSecond);
    BandwidthHistory.Add(BandwidthKBps);
    
    CurrentPerformanceData.NetworkMessagesPerSecond = MessagesPerSecond;
    CurrentPerformanceData.ReplicationBandwidth = BandwidthKBps;
    
    OptimizeHistoryArrays();
}

float UTGSiegePerformanceMonitor::GetAveragePhaseTransitionTime() const
{
    return CalculateAverage(PhaseTransitionTimes);
}

float UTGSiegePerformanceMonitor::GetAverageDominanceCalculationTime() const
{
    return CalculateAverage(DominanceCalculationTimes);
}

bool UTGSiegePerformanceMonitor::ArePerformanceTargetsMet() const
{
    if (!bMonitoringActive)
    {
        return true;
    }
    
    // Check all current metrics against thresholds
    bool bPhaseTransitionOK = CurrentPerformanceData.PhaseTransitionTime <= MaxPhaseTransitionTime;
    bool bDominanceCalculationOK = CurrentPerformanceData.DominanceCalculationTime <= MaxDominanceCalculationTime;
    bool bTicketUpdateOK = CurrentPerformanceData.TicketUpdateTime <= MaxTicketUpdateTime;
    bool bNetworkMessagesOK = CurrentPerformanceData.NetworkMessagesPerSecond <= MaxNetworkMessagesPerSecond;
    bool bBandwidthOK = CurrentPerformanceData.ReplicationBandwidth <= MaxReplicationBandwidth;
    
    return bPhaseTransitionOK && bDominanceCalculationOK && bTicketUpdateOK && bNetworkMessagesOK && bBandwidthOK;
}

void UTGSiegePerformanceMonitor::BindToPerformanceProfiler(UTGPerformanceProfiler* Profiler)
{
    BoundProfiler = Profiler;
    
    if (Profiler)
    {
        UE_LOG(LogTemp, Log, TEXT("Siege Performance Monitor: Bound to Performance Profiler"));
    }
}

void UTGSiegePerformanceMonitor::OnRep_PerformanceData()
{
    // Client-side response to performance data updates
    OnPerformanceUpdate.Broadcast(CurrentPerformanceData);
}

// Private Methods

void UTGSiegePerformanceMonitor::UpdatePerformanceData()
{
    if (!GetOwner() || !GetOwner()->HasAuthority())
    {
        return; // Server only
    }
    
    // Update participant count (simplified - would query actual player count)
    CurrentPerformanceData.ParticipantCount = 10; // Placeholder
    
    // Update performance targets met flag
    CurrentPerformanceData.bPerformanceTargetsMet = ArePerformanceTargetsMet();
}

void UTGSiegePerformanceMonitor::CheckThresholds()
{
    if (!GetOwner() || !GetOwner()->HasAuthority())
    {
        return;
    }
    
    CheckPhaseTransitionThreshold();
    CheckDominanceCalculationThreshold();
    CheckTicketUpdateThreshold();
    CheckNetworkThresholds();
}

void UTGSiegePerformanceMonitor::CheckPhaseTransitionThreshold()
{
    if (CurrentPerformanceData.PhaseTransitionTime > MaxPhaseTransitionTime)
    {
        OnThresholdViolation.Broadcast(TEXT("Phase Transition"), CurrentPerformanceData.PhaseTransitionTime);
        
        UE_LOG(LogTemp, Warning, TEXT("Siege Performance: Phase transition time %.2fms exceeds threshold %.2fms"),
            CurrentPerformanceData.PhaseTransitionTime, MaxPhaseTransitionTime);
    }
}

void UTGSiegePerformanceMonitor::CheckDominanceCalculationThreshold()
{
    if (CurrentPerformanceData.DominanceCalculationTime > MaxDominanceCalculationTime)
    {
        OnThresholdViolation.Broadcast(TEXT("Dominance Calculation"), CurrentPerformanceData.DominanceCalculationTime);
        
        UE_LOG(LogTemp, Warning, TEXT("Siege Performance: Dominance calculation time %.2fms exceeds threshold %.2fms"),
            CurrentPerformanceData.DominanceCalculationTime, MaxDominanceCalculationTime);
    }
}

void UTGSiegePerformanceMonitor::CheckTicketUpdateThreshold()
{
    if (CurrentPerformanceData.TicketUpdateTime > MaxTicketUpdateTime)
    {
        OnThresholdViolation.Broadcast(TEXT("Ticket Update"), CurrentPerformanceData.TicketUpdateTime);
        
        UE_LOG(LogTemp, Warning, TEXT("Siege Performance: Ticket update time %.2fms exceeds threshold %.2fms"),
            CurrentPerformanceData.TicketUpdateTime, MaxTicketUpdateTime);
    }
}

void UTGSiegePerformanceMonitor::CheckNetworkThresholds()
{
    if (CurrentPerformanceData.NetworkMessagesPerSecond > MaxNetworkMessagesPerSecond)
    {
        OnThresholdViolation.Broadcast(TEXT("Network Messages"), (float)CurrentPerformanceData.NetworkMessagesPerSecond);
    }
    
    if (CurrentPerformanceData.ReplicationBandwidth > MaxReplicationBandwidth)
    {
        OnThresholdViolation.Broadcast(TEXT("Replication Bandwidth"), CurrentPerformanceData.ReplicationBandwidth);
    }
}

void UTGSiegePerformanceMonitor::OptimizeHistoryArrays()
{
    // Maintain history size limits
    if (PhaseTransitionTimes.Num() > HistorySize)
    {
        PhaseTransitionTimes.RemoveAt(0);
    }
    
    if (DominanceCalculationTimes.Num() > HistorySize)
    {
        DominanceCalculationTimes.RemoveAt(0);
    }
    
    if (TicketUpdateTimes.Num() > HistorySize)
    {
        TicketUpdateTimes.RemoveAt(0);
    }
    
    if (NetworkMessageHistory.Num() > HistorySize)
    {
        NetworkMessageHistory.RemoveAt(0);
    }
    
    if (BandwidthHistory.Num() > HistorySize)
    {
        BandwidthHistory.RemoveAt(0);
    }
}

void UTGSiegePerformanceMonitor::ReportToProfiler()
{
    if (!BoundProfiler)
    {
        return;
    }
    
    // Report siege-specific metrics to the main profiler
    FTGPerformanceMetrics ProfilerMetrics = BoundProfiler->GetCurrentMetrics();
    
    // Update territorial metrics with our siege-specific data
    ProfilerMetrics.TerritorialQueryTime = FMath::Max(ProfilerMetrics.TerritorialQueryTime, CurrentPerformanceData.DominanceCalculationTime);
    ProfilerMetrics.ActiveTerritories = FMath::Max(ProfilerMetrics.ActiveTerritories, 1); // At least one active siege
    ProfilerMetrics.TerritorialUpdatesPerSecond = CurrentPerformanceData.NetworkMessagesPerSecond;
    
    // The profiler will handle this data in its next update cycle
}

void UTGSiegePerformanceMonitor::BroadcastPerformanceUpdate()
{
    if (GetOwner() && GetOwner()->HasAuthority())
    {
        // Replicated data will automatically trigger OnRep_PerformanceData on clients
        OnPerformanceUpdate.Broadcast(CurrentPerformanceData);
    }
}

float UTGSiegePerformanceMonitor::CalculateAverage(const TArray<float>& Values) const
{
    if (Values.Num() == 0)
    {
        return 0.0f;
    }
    
    float Total = 0.0f;
    for (float Value : Values)
    {
        Total += Value;
    }
    
    return Total / (float)Values.Num();
}

int32 UTGSiegePerformanceMonitor::CalculateAverageInt(const TArray<int32>& Values) const
{
    if (Values.Num() == 0)
    {
        return 0;
    }
    
    int32 Total = 0;
    for (int32 Value : Values)
    {
        Total += Value;
    }
    
    return Total / Values.Num();
}