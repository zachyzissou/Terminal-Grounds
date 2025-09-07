#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Net/UnrealNetwork.h"
#include "TGPerformanceProfiler.h"
#include "PhaseGateComponent.h"
#include "TGSiegePerformanceMonitor.generated.h"

// Siege-specific performance metrics
USTRUCT(BlueprintType)
struct TGCORE_API FTGSiegePerformanceData
{
    GENERATED_BODY()
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    FString SiegeID;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    ESiegePhase CurrentPhase;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    int32 ParticipantCount;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    float PhaseTransitionTime;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    float DominanceCalculationTime;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    float TicketUpdateTime;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    int32 NetworkMessagesPerSecond;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    float ReplicationBandwidth;
    
    UPROPERTY(BlueprintReadOnly, Category = "Siege Performance")
    bool bPerformanceTargetsMet;
    
    FTGSiegePerformanceData()
    {
        CurrentPhase = ESiegePhase::Probe;
        ParticipantCount = 0;
        PhaseTransitionTime = 0.0f;
        DominanceCalculationTime = 0.0f;
        TicketUpdateTime = 0.0f;
        NetworkMessagesPerSecond = 0;
        ReplicationBandwidth = 0.0f;
        bPerformanceTargetsMet = true;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSiegePerformanceUpdate, const FTGSiegePerformanceData&, PerformanceData);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnSiegePerformanceThresholdViolation, const FString&, Metric, float, Value);

/**
 * Siege Performance Monitor Component
 * Specialized monitoring for siege warfare performance metrics
 * Tracks phase transitions, dominance calculations, and network replication efficiency
 * Integrates with TGPerformanceProfiler for comprehensive analysis
 */
UCLASS(ClassGroup=(TG), meta=(BlueprintSpawnableComponent))
class TGCORE_API UTGSiegePerformanceMonitor : public UActorComponent
{
    GENERATED_BODY()

public:
    UTGSiegePerformanceMonitor();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    // Siege monitoring controls
    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void StartSiegeMonitoring(const FString& SiegeID);

    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void StopSiegeMonitoring();

    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    bool IsSiegeMonitoringActive() const { return bMonitoringActive; }

    // Performance measurement
    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void RecordPhaseTransition(ESiegePhase FromPhase, ESiegePhase ToPhase, float TransitionTime);

    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void RecordDominanceCalculation(float CalculationTime);

    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void RecordTicketUpdate(float UpdateTime);

    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void RecordNetworkActivity(int32 MessagesPerSecond, float BandwidthKBps);

    // Performance queries
    UFUNCTION(BlueprintPure, Category = "Siege Performance")
    FTGSiegePerformanceData GetCurrentPerformanceData() const { return CurrentPerformanceData; }

    UFUNCTION(BlueprintPure, Category = "Siege Performance")
    float GetAveragePhaseTransitionTime() const;

    UFUNCTION(BlueprintPure, Category = "Siege Performance")
    float GetAverageDominanceCalculationTime() const;

    UFUNCTION(BlueprintPure, Category = "Siege Performance")
    bool ArePerformanceTargetsMet() const;

    // Integration with main performance profiler
    UFUNCTION(BlueprintCallable, Category = "Siege Performance")
    void BindToPerformanceProfiler(UTGPerformanceProfiler* Profiler);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Siege Performance")
    FOnSiegePerformanceUpdate OnPerformanceUpdate;

    UPROPERTY(BlueprintAssignable, Category = "Siege Performance")
    FOnSiegePerformanceThresholdViolation OnThresholdViolation;

    // Performance thresholds
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxPhaseTransitionTime = 2000.0f; // 2 seconds

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxDominanceCalculationTime = 16.67f; // One frame at 60 FPS

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxTicketUpdateTime = 5.0f; // 5ms

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    int32 MaxNetworkMessagesPerSecond = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Thresholds")
    float MaxReplicationBandwidth = 1024.0f; // 1MB/s

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    float UpdateFrequency = 2.0f; // Updates per second

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Configuration")
    int32 HistorySize = 100; // Number of samples to keep

protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(ReplicatedUsing = OnRep_PerformanceData, BlueprintReadOnly, Category = "Siege Performance")
    FTGSiegePerformanceData CurrentPerformanceData;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege Performance")
    bool bMonitoringActive;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege Performance")
    FDateTime MonitoringStartTime;

    UFUNCTION()
    void OnRep_PerformanceData();

private:
    // Performance history for averaging
    TArray<float> PhaseTransitionTimes;
    TArray<float> DominanceCalculationTimes;
    TArray<float> TicketUpdateTimes;
    TArray<int32> NetworkMessageHistory;
    TArray<float> BandwidthHistory;

    // Integration
    UPROPERTY()
    UTGPerformanceProfiler* BoundProfiler;

    // Timing
    float LastUpdateTime;
    int32 NetworkMessageCounter;
    float NetworkBandwidthAccumulator;

    // Internal methods
    void UpdatePerformanceData();
    void CheckThresholds();
    void OptimizeHistoryArrays();
    void ReportToProfiler();
    void BroadcastPerformanceUpdate();

    // Threshold checking helpers
    void CheckPhaseTransitionThreshold();
    void CheckDominanceCalculationThreshold();
    void CheckTicketUpdateThreshold();
    void CheckNetworkThresholds();

    // Statistics calculation
    float CalculateAverage(const TArray<float>& Values) const;
    int32 CalculateAverageInt(const TArray<int32>& Values) const;
};