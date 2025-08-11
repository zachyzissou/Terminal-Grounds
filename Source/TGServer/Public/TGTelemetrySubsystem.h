#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TGTelemetrySubsystem.generated.h"

USTRUCT(BlueprintType)
struct FTelemetryMatchData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Match")
    FString MatchId;

    UPROPERTY(BlueprintReadWrite, Category = "Match")
    FDateTime MatchStartTime;

    UPROPERTY(BlueprintReadWrite, Category = "Match")
    FDateTime MatchEndTime;

    UPROPERTY(BlueprintReadWrite, Category = "Match")
    int32 PlayerCount = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Match")
    FString MapName;

    UPROPERTY(BlueprintReadWrite, Category = "Match")
    FString GameMode;

    UPROPERTY(BlueprintReadWrite, Category = "Performance")
    float AverageFrameRate = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Performance")
    float MinFrameRate = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Performance")
    float MaxFrameRate = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Performance")
    float AverageLatency = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Performance")
    float PacketLossPercentage = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Gameplay")
    TMap<FString, int32> WeaponUsageStats;

    UPROPERTY(BlueprintReadWrite, Category = "Gameplay")
    TMap<FString, int32> FactionInteractionStats;

    UPROPERTY(BlueprintReadWrite, Category = "Gameplay")
    int32 MissionsCompleted = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Gameplay")
    int32 MissionsFailed = 0;
};

USTRUCT(BlueprintType)
struct FTelemetryPlayerData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Player")
    FString PlayerSessionId;

    UPROPERTY(BlueprintReadWrite, Category = "Player")
    FString HardwareHash; // Anonymized hardware fingerprint

    UPROPERTY(BlueprintReadWrite, Category = "Settings")
    FString GraphicsPreset;

    UPROPERTY(BlueprintReadWrite, Category = "Settings")
    int32 ResolutionWidth = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Settings")
    int32 ResolutionHeight = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Settings")
    bool bVSyncEnabled = false;

    UPROPERTY(BlueprintReadWrite, Category = "Input")
    FString InputMethod; // Mouse/Keyboard, Controller

    UPROPERTY(BlueprintReadWrite, Category = "Accessibility")
    bool bColorblindAssistEnabled = false;

    UPROPERTY(BlueprintReadWrite, Category = "Accessibility")
    bool bMotionReductionEnabled = false;

    UPROPERTY(BlueprintReadWrite, Category = "Accessibility")
    float UIScale = 1.0f;
};

/**
 * Telemetry subsystem for collecting anonymized gameplay and performance data
 */
UCLASS()
class TGSERVER_API UTGTelemetrySubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Match Data Collection
    UFUNCTION(BlueprintCallable, Category = "Telemetry")
    void StartMatchTelemetry(const FString& MatchId, const FString& MapName, const FString& GameMode);

    UFUNCTION(BlueprintCallable, Category = "Telemetry")
    void EndMatchTelemetry();

    UFUNCTION(BlueprintCallable, Category = "Telemetry")
    void RecordWeaponUsage(const FString& WeaponId);

    UFUNCTION(BlueprintCallable, Category = "Telemetry")
    void RecordFactionInteraction(const FString& FactionId);

    UFUNCTION(BlueprintCallable, Category = "Telemetry")
    void RecordMissionResult(bool bCompleted);

    // Performance Data Collection
    UFUNCTION(BlueprintCallable, Category = "Performance")
    void RecordFrameRate(float FrameRate);

    UFUNCTION(BlueprintCallable, Category = "Performance")
    void RecordNetworkLatency(float Latency);

    UFUNCTION(BlueprintCallable, Category = "Performance")
    void RecordPacketLoss(float PacketLossPercent);

    // Player Data Collection
    UFUNCTION(BlueprintCallable, Category = "Player")
    void SetPlayerHardwareInfo(const FString& GraphicsPreset, int32 Width, int32 Height, bool bVSync);

    UFUNCTION(BlueprintCallable, Category = "Player")
    void SetInputMethod(const FString& InputMethod);

    UFUNCTION(BlueprintCallable, Category = "Player")
    void SetAccessibilitySettings(bool bColorblind, bool bMotionReduction, float UIScale);

    // Data Submission
    UFUNCTION(BlueprintCallable, Category = "Submission")
    void SubmitTelemetryData();

    UFUNCTION(BlueprintPure, Category = "Privacy")
    bool IsTelemetryEnabled() const { return bTelemetryEnabled; }

    UFUNCTION(BlueprintCallable, Category = "Privacy")
    void SetTelemetryEnabled(bool bEnabled);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    FTelemetryMatchData CurrentMatchData;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    FTelemetryPlayerData PlayerData;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "State")
    bool bMatchActive = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Privacy")
    bool bTelemetryEnabled = false;

    // Performance tracking
    TArray<float> FrameRateHistory;
    TArray<float> LatencyHistory;
    
    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category = "Performance")
    int32 MaxHistorySize = 1000;

private:
    void ProcessPerformanceData();
    FString GenerateSessionId();
    FString GenerateHardwareHash();
    void SaveTelemetryToFile();
    bool LoadTelemetrySettings();
    void SaveTelemetrySettings();
};