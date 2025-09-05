#include "TGMissionDirector2.h"
#include "SiegeHelpers.h"
#include "TimerManager.h"

ATGMissionDirector2::ATGMissionDirector2() {
  PrimaryActorTick.bCanEverTick = true;
  CurrentStageIndex = INDEX_NONE;
  CurrentStage = EMissionStage::Briefing;
  CurrentThreatLevel = EThreatLevel::Low;
  StageStartTime = 0.0f;
  bMissionActive = false;
  bSiegeMode = false;
}

void ATGMissionDirector2::BeginPlay() {
  Super::BeginPlay();
  if (EventCheckInterval > 0.0f) {
    GetWorldTimerManager().SetTimer(EventCheckTimer, this,
                                    &ATGMissionDirector2::CheckEventTriggers,
                                    EventCheckInterval, true);
  }
}

void ATGMissionDirector2::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);
  if (bMissionActive) {
    ProcessStageTimeLimit(DeltaTime);
    UpdateStageProgress();
  }
}

void ATGMissionDirector2::StartMission(
    const TArray<FMissionStageData> &InMissionStages) {
  MissionStages = InMissionStages;
  bMissionActive = MissionStages.Num() > 0;
  CurrentStageIndex = bMissionActive ? 0 : INDEX_NONE;
  StageStartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
  CurrentStage =
      bMissionActive ? MissionStages[0].StageType : EMissionStage::Completed;
  OnMissionStageChanged.Broadcast(CurrentStage);
}

void ATGMissionDirector2::AdvanceToNextStage() {
  if (!bMissionActive) {
    return;
  }
  if (CurrentStageIndex + 1 < MissionStages.Num()) {
    CurrentStageIndex++;
    CurrentStage = MissionStages[CurrentStageIndex].StageType;
    StageStartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
    OnMissionStageChanged.Broadcast(CurrentStage);
  } else {
    CompleteMission();
  }
}

void ATGMissionDirector2::CompleteMission() {
  bMissionActive = false;
  CurrentStage = EMissionStage::Completed;
  OnMissionCompleted.Broadcast();
}

void ATGMissionDirector2::FailMission() {
  bMissionActive = false;
  CurrentStage = EMissionStage::Failed;
  OnMissionFailed.Broadcast();
}

void ATGMissionDirector2::AbortMission() { bMissionActive = false; }

FMissionStageData ATGMissionDirector2::GetCurrentStageData() const {
  return (MissionStages.IsValidIndex(CurrentStageIndex))
             ? MissionStages[CurrentStageIndex]
             : FMissionStageData();
}

float ATGMissionDirector2::GetStageProgress() const {
  const FMissionStageData Data = GetCurrentStageData();
  if (Data.TimeLimit <= 0.0f || !GetWorld()) {
    return 0.0f;
  }
  const float Elapsed = GetWorld()->GetTimeSeconds() - StageStartTime;
  return FMath::Clamp(Elapsed / Data.TimeLimit, 0.0f, 1.0f);
}

float ATGMissionDirector2::GetStageTimeRemaining() const {
  const FMissionStageData Data = GetCurrentStageData();
  if (Data.TimeLimit <= 0.0f || !GetWorld()) {
    return 0.0f;
  }
  const float Elapsed = GetWorld()->GetTimeSeconds() - StageStartTime;
  return FMath::Max(0.0f, Data.TimeLimit - Elapsed);
}

void ATGMissionDirector2::RegisterDynamicEvent(const FDynamicEvent &Event) {
  RegisteredEvents.Add(Event);
}

void ATGMissionDirector2::TriggerDynamicEvent(const FString &EventName,
                                              float IntensityModifier) {
  if (TriggeredEventNames.Contains(EventName)) {
    return;
  }
  for (const FDynamicEvent &Evt : RegisteredEvents) {
    if (Evt.EventName == EventName) {
      OnDynamicEventTriggered.Broadcast(Evt, IntensityModifier);
      TriggeredEventNames.Add(EventName);
      if (Evt.AdditionalStages.Num() > 0) {
        MissionStages.Append(Evt.AdditionalStages);
      }
      break;
    }
  }
}

void ATGMissionDirector2::CheckEventTriggers() {
  for (const FDynamicEvent &Evt : RegisteredEvents) {
    if (EvaluateEventTrigger(Evt)) {
      TriggerDynamicEvent(Evt.EventName);
    }
  }
}

void ATGMissionDirector2::SetThreatLevel(EThreatLevel NewThreatLevel) {
  if (CurrentThreatLevel != NewThreatLevel) {
    EThreatLevel Old = CurrentThreatLevel;
    CurrentThreatLevel = NewThreatLevel;
    OnThreatLevelChanged.Broadcast(Old, CurrentThreatLevel);
  }
}

void ATGMissionDirector2::IncreaseThreatLevel(int32 LevelsToIncrease) {
  int32 NewLevel =
      FMath::Clamp(static_cast<int32>(CurrentThreatLevel) + LevelsToIncrease, 0,
                   static_cast<int32>(EThreatLevel::Critical));
  SetThreatLevel(static_cast<EThreatLevel>(NewLevel));
}

float ATGMissionDirector2::GetThreatScaling() const {
  return BaseThreatScaling +
         (static_cast<int32>(CurrentThreatLevel) * ThreatScalingIncrement);
}

void ATGMissionDirector2::CompleteObjective(const FString &ObjectiveId) {
  if (FText *Text = ActiveObjectives.Find(ObjectiveId)) {
    CompletedObjectives.Add(ObjectiveId);
    ActiveObjectives.Remove(ObjectiveId);
  }
}

void ATGMissionDirector2::AddObjective(const FText &ObjectiveText,
                                       const FString &ObjectiveId) {
  ActiveObjectives.Add(ObjectiveId, ObjectiveText);
}

TArray<FText> ATGMissionDirector2::GetActiveObjectives() const {
  TArray<FText> Values;
  ActiveObjectives.GenerateValueArray(Values);
  return Values;
}

void ATGMissionDirector2::AddConditionTag(const FGameplayTag &Tag) {
  ActiveConditions.AddTag(Tag);
}

void ATGMissionDirector2::RemoveConditionTag(const FGameplayTag &Tag) {
  ActiveConditions.RemoveTag(Tag);
}

bool ATGMissionDirector2::CheckConditions(
    const FGameplayTagContainer &RequiredTags) const {
  return ActiveConditions.HasAll(RequiredTags);
}

void ATGMissionDirector2::UpdateStageProgress() {}

void ATGMissionDirector2::ProcessStageTimeLimit(float DeltaTime) {
  if (!GetWorld())
    return;
  const FMissionStageData Data = GetCurrentStageData();
  if (bMissionActive && Data.TimeLimit > 0.0f) {
    const float Elapsed = GetWorld()->GetTimeSeconds() - StageStartTime;
    if (Elapsed >= Data.TimeLimit) {
      AdvanceToNextStage();
    }
  }
}

bool ATGMissionDirector2::EvaluateEventTrigger(
    const FDynamicEvent &Event) const {
  if (!ActiveConditions.HasAll(Event.TriggerConditions)) {
    return false;
  }
  const float Rnd = FMath::FRand();
  return Rnd <= Event.TriggerProbability;
}

void ATGMissionDirector2::ApplyThreatScaling() {}

// Siege Integration Methods
void ATGMissionDirector2::StartSiege(const FSiegePlan& Plan) {
  bSiegeMode = true;
  
  // Start with Probe phase stages
  if (Plan.ProbeStages.Num() > 0) {
    StartMission(Plan.ProbeStages);
  }
  
  UE_LOG(LogTemp, Log, TEXT("Siege started in MissionDirector2 with %d Probe stages"), Plan.ProbeStages.Num());
}

EMissionStage ATGMissionDirector2::MapExtractionToSiege(EMissionStage OriginalStage) const {
  if (!bSiegeMode) {
    return OriginalStage;
  }
  
  // Map Extraction stage to Dominate in siege mode
  if (OriginalStage == EMissionStage::Extraction) {
    return EMissionStage::Dynamic; // Use Dynamic as "Dominate" equivalent
  }
  
  return OriginalStage;
}

void ATGMissionDirector2::ProcessSiegeStageCompletion(EMissionStage CompletedStage) {
  if (!bSiegeMode) {
    return;
  }
  
  // Log siege stage completion
  UE_LOG(LogTemp, Log, TEXT("Siege stage completed: %s"), 
    *UEnum::GetValueAsString(CompletedStage));
  
  // Additional siege-specific processing can be added here
  // This is called by the SiegeHelperComponent for integration
}
