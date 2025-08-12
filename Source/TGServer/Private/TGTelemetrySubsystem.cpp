#include "TGTelemetrySubsystem.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Guid.h"

void UTGTelemetrySubsystem::Initialize(FSubsystemCollectionBase &Collection) {
  Super::Initialize(Collection);
  bTelemetryEnabled = LoadTelemetrySettings();
}

void UTGTelemetrySubsystem::Deinitialize() { Super::Deinitialize(); }

void UTGTelemetrySubsystem::StartMatchTelemetry(const FString &MatchId,
                                                const FString &MapName,
                                                const FString &GameMode) {
  CurrentMatchData = FTelemetryMatchData();
  CurrentMatchData.MatchId = MatchId;
  CurrentMatchData.MatchStartTime = FDateTime::UtcNow();
  CurrentMatchData.MapName = MapName;
  CurrentMatchData.GameMode = GameMode;
  bMatchActive = true;
}

void UTGTelemetrySubsystem::EndMatchTelemetry() {
  CurrentMatchData.MatchEndTime = FDateTime::UtcNow();
  bMatchActive = false;
}

void UTGTelemetrySubsystem::RecordWeaponUsage(const FString &WeaponId) {
  CurrentMatchData.WeaponUsageStats.FindOrAdd(WeaponId)++;
}

void UTGTelemetrySubsystem::RecordFactionInteraction(const FString &FactionId) {
  CurrentMatchData.FactionInteractionStats.FindOrAdd(FactionId)++;
}

void UTGTelemetrySubsystem::RecordMissionResult(bool bCompleted) {
  if (bCompleted) {
    CurrentMatchData.MissionsCompleted++;
  } else {
    CurrentMatchData.MissionsFailed++;
  }
}

void UTGTelemetrySubsystem::RecordFrameRate(float FrameRate) {
  FrameRateHistory.Add(FrameRate);
  CurrentMatchData.AverageFrameRate = FrameRate; // Simplified
}

void UTGTelemetrySubsystem::RecordNetworkLatency(float Latency) {
  LatencyHistory.Add(Latency);
  CurrentMatchData.AverageLatency = Latency; // Simplified
}

void UTGTelemetrySubsystem::RecordPacketLoss(float PacketLossPercent) {
  CurrentMatchData.PacketLossPercentage = PacketLossPercent;
}

void UTGTelemetrySubsystem::SetPlayerHardwareInfo(const FString &GraphicsPreset,
                                                  int32 Width, int32 Height,
                                                  bool bVSync) {
  PlayerData.GraphicsPreset = GraphicsPreset;
  PlayerData.ResolutionWidth = Width;
  PlayerData.ResolutionHeight = Height;
  PlayerData.bVSyncEnabled = bVSync;
}

void UTGTelemetrySubsystem::SetInputMethod(const FString &InInputMethod) {
  PlayerData.InputMethod = InInputMethod;
}

void UTGTelemetrySubsystem::SetAccessibilitySettings(bool bColorblind,
                                                     bool bMotionReduction,
                                                     float UIScale) {
  PlayerData.bColorblindAssistEnabled = bColorblind;
  PlayerData.bMotionReductionEnabled = bMotionReduction;
  PlayerData.UIScale = UIScale;
}

void UTGTelemetrySubsystem::SubmitTelemetryData() {
  if (!bTelemetryEnabled) {
    return;
  }
  SaveTelemetryToFile();
}

void UTGTelemetrySubsystem::SetTelemetryEnabled(bool bEnabled) {
  bTelemetryEnabled = bEnabled;
  SaveTelemetrySettings();
}

void UTGTelemetrySubsystem::ProcessPerformanceData() {}

FString UTGTelemetrySubsystem::GenerateSessionId() {
  return FGuid::NewGuid().ToString(EGuidFormats::Digits);
}

FString UTGTelemetrySubsystem::GenerateHardwareHash() {
  return FGuid::NewGuid().ToString(EGuidFormats::Digits);
}

void UTGTelemetrySubsystem::SaveTelemetryToFile() {
  FString OutputDir = FPaths::ProjectSavedDir() / TEXT("Telemetry");
  IPlatformFile &PF = FPlatformFileManager::Get().GetPlatformFile();
  if (!PF.DirectoryExists(*OutputDir)) {
    PF.CreateDirectoryTree(*OutputDir);
  }

  const FString FilePath =
      OutputDir / FString::Printf(TEXT("%s.json"), *GenerateSessionId());
  FString Data = FString::Printf(
      TEXT("{\"MatchId\":\"%s\",\"Map\":\"%s\",\"Mode\":\"%s\"}"),
      *CurrentMatchData.MatchId, *CurrentMatchData.MapName,
      *CurrentMatchData.GameMode);
  FFileHelper::SaveStringToFile(Data, *FilePath);
}

bool UTGTelemetrySubsystem::LoadTelemetrySettings() {
  // Stub: load from config
  return true;
}

void UTGTelemetrySubsystem::SaveTelemetrySettings() {
  // Stub: save to config
}
