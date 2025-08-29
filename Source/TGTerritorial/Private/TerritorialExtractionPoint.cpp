// Copyright Terminal Grounds. All Rights Reserved.

#include "TerritorialExtractionPoint.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "TimerManager.h"

ATerritorialExtractionPoint::ATerritorialExtractionPoint()
{
    PrimaryActorTick.bCanEverTick = true;

    // Create root component
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

    // Create extraction platform mesh
    ExtractionPlatform = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ExtractionPlatform"));
    ExtractionPlatform->SetupAttachment(RootComponent);

    // Create extraction trigger zone
    ExtractionTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("ExtractionTrigger"));
    ExtractionTrigger->SetupAttachment(RootComponent);
    ExtractionTrigger->SetSphereRadius(300.0f);
    ExtractionTrigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    ExtractionTrigger->SetCollisionResponseToAllChannels(ECR_Ignore);
    ExtractionTrigger->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

    // Create contestation zone (larger than extraction zone)
    ContestationZone = CreateDefaultSubobject<USphereComponent>(TEXT("ContestationZone"));
    ContestationZone->SetupAttachment(RootComponent);
    ContestationZone->SetSphereRadius(800.0f);
    ContestationZone->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    ContestationZone->SetCollisionResponseToAllChannels(ECR_Ignore);
    ContestationZone->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

    // Initialize faction colors
    FactionColors.Add(EFactionID::Directorate, FLinearColor(0.2f, 0.4f, 1.0f, 1.0f));
    FactionColors.Add(EFactionID::Free77, FLinearColor(1.0f, 0.3f, 0.2f, 1.0f));
    FactionColors.Add(EFactionID::CivicWardens, FLinearColor(0.8f, 0.8f, 0.8f, 1.0f));
}

void ATerritorialExtractionPoint::BeginPlay()
{
    Super::BeginPlay();

    // Bind overlap events
    if (ExtractionTrigger)
    {
        ExtractionTrigger->OnComponentBeginOverlap.AddDynamic(this, &ATerritorialExtractionPoint::OnExtractionTriggerBeginOverlap);
        ExtractionTrigger->OnComponentEndOverlap.AddDynamic(this, &ATerritorialExtractionPoint::OnExtractionTriggerEndOverlap);
    }

    if (ContestationZone)
    {
        ContestationZone->OnComponentBeginOverlap.AddDynamic(this, &ATerritorialExtractionPoint::OnContestationZoneBeginOverlap);
        ContestationZone->OnComponentEndOverlap.AddDynamic(this, &ATerritorialExtractionPoint::OnContestationZoneEndOverlap);
    }

    // Initialize visuals
    UpdateExtractionVisuals();
}

void ATerritorialExtractionPoint::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // Update extraction progress if in progress
    if (CurrentState == EExtractionState::InProgress && CurrentExtractingPlayer)
    {
        UpdateExtractionProgress(DeltaTime);
    }

    // Periodic state updates
    if (GetWorld()->GetTimeSeconds() - LastStateUpdate > 0.5f)
    {
        UpdateExtractionState();
        LastStateUpdate = GetWorld()->GetTimeSeconds();
    }
}

bool ATerritorialExtractionPoint::StartExtraction(APawn* Player)
{
    if (!CanPlayerExtract(Player))
    {
        return false;
    }

    CurrentExtractingPlayer = Player;
    CurrentState = EExtractionState::InProgress;
    ExtractionProgress = 0.0f;
    CurrentExtractionTime = CalculateExtractionTime(Player);

    EFactionID PlayerFaction = GetPlayerFaction(Player);
    int32 InfluenceGain = CalculateTerritorialInfluence(Player);

    OnExtractionStarted.Broadcast(Player, PlayerFaction, InfluenceGain, CurrentExtractionTime);
    UpdateExtractionVisuals();

    return true;
}

void ATerritorialExtractionPoint::CancelExtraction(const FString& Reason)
{
    if (CurrentState != EExtractionState::InProgress || !CurrentExtractingPlayer)
    {
        return;
    }

    EFactionID PlayerFaction = GetPlayerFaction(CurrentExtractingPlayer);
    OnExtractionCanceled.Broadcast(CurrentExtractingPlayer, PlayerFaction, Reason);

    CurrentExtractingPlayer = nullptr;
    ExtractionProgress = 0.0f;
    CurrentState = EExtractionState::Available;
    UpdateExtractionVisuals();
}

void ATerritorialExtractionPoint::CompleteExtraction()
{
    if (CurrentState != EExtractionState::InProgress || !CurrentExtractingPlayer)
    {
        return;
    }

    EFactionID PlayerFaction = GetPlayerFaction(CurrentExtractingPlayer);
    int32 InfluenceGain = CalculateTerritorialInfluence(CurrentExtractingPlayer);

    OnExtractionCompleted.Broadcast(CurrentExtractingPlayer, PlayerFaction, InfluenceGain);
    NotifyTerritorialInfluenceGain(CurrentExtractingPlayer, InfluenceGain);

    CurrentExtractingPlayer = nullptr;
    ExtractionProgress = 0.0f;
    CurrentState = EExtractionState::Available;
    UpdateExtractionVisuals();
}

bool ATerritorialExtractionPoint::CanPlayerExtract(APawn* Player) const
{
    if (!Player || CurrentState != EExtractionState::Available)
    {
        return false;
    }

    if (!IsPlayerInExtractionZone(Player))
    {
        return false;
    }

    // Check if too many simultaneous extractions
    if (PlayersInExtractionZone.Num() > MaxSimultaneousExtractions)
    {
        return false;
    }

    return true;
}

float ATerritorialExtractionPoint::CalculateExtractionTime(APawn* Player) const
{
    float Time = BaseExtractionTime;

    // Apply faction bonus if player's faction controls the territory
    if (GetPlayerFaction(Player) == OwningFaction)
    {
        Time -= FactionBonusTime;
    }

    // Apply penalty if contested
    if (IsExtractionContested())
    {
        Time += ContestedPenaltyTime;
    }

    return FMath::Max(Time, 5.0f); // Minimum 5 seconds
}

float ATerritorialExtractionPoint::CalculateSuccessRate(APawn* Player) const
{
    float Rate = ExtractionSuccessRate;

    // Apply faction control bonus
    if (GetPlayerFaction(Player) == OwningFaction)
    {
        Rate += FactionControlledBonus;
    }

    // Apply contested penalty
    if (IsExtractionContested())
    {
        Rate -= ContestedSuccessRatePenalty;
    }

    return FMath::Clamp(Rate, 0.1f, 1.0f);
}

int32 ATerritorialExtractionPoint::CalculateTerritorialInfluence(APawn* Player) const
{
    int32 Influence = BaseTerritorialInfluence;

    // Add bonus if faction controls territory
    if (GetPlayerFaction(Player) == OwningFaction)
    {
        Influence += ControlleredTerritoryBonus;
    }

    return Influence;
}

bool ATerritorialExtractionPoint::IsExtractionContested() const
{
    // Check if multiple factions are present in contestation zone
    TSet<EFactionID> FactionsPresent;
    for (APawn* Player : PlayersInContestationZone)
    {
        if (Player)
        {
            FactionsPresent.Add(GetPlayerFaction(Player));
        }
    }

    return FactionsPresent.Num() > 1;
}

EFactionID ATerritorialExtractionPoint::GetTerritoryControllingFaction() const
{
    return OwningFaction;
}

void ATerritorialExtractionPoint::UpdateExtractionVisuals()
{
    // This would update visual elements based on current state
    // Implementation depends on specific visual components
}

void ATerritorialExtractionPoint::SetFactionControlVisuals(EFactionID ControllingFaction)
{
    OwningFaction = ControllingFaction;
    
    // Update visual elements to show faction control
    if (FLinearColor* Color = FactionColors.Find(ControllingFaction))
    {
        // Apply faction color to visual elements
        if (ExtractionPlatform)
        {
            // Would set material parameters here
        }
    }
    
    UpdateExtractionVisuals();
}

void ATerritorialExtractionPoint::UpdateExtractionState()
{
    CheckContestationStatus();
    
    // Update state based on current conditions
    if (CurrentState == EExtractionState::InProgress && IsExtractionContested())
    {
        CurrentState = EExtractionState::Contested;
        UpdateExtractionVisuals();
    }
    else if (CurrentState == EExtractionState::Contested && !IsExtractionContested())
    {
        CurrentState = EExtractionState::InProgress;
        UpdateExtractionVisuals();
    }
}

void ATerritorialExtractionPoint::UpdateExtractionProgress(float DeltaTime)
{
    if (CurrentState != EExtractionState::InProgress || !CurrentExtractingPlayer)
    {
        return;
    }

    // Update progress
    ExtractionProgress += (DeltaTime / CurrentExtractionTime);

    // Check if extraction is complete
    if (ExtractionProgress >= 1.0f)
    {
        CompleteExtraction();
    }
}

void ATerritorialExtractionPoint::CheckContestationStatus()
{
    // Already handled by IsExtractionContested()
}

EFactionID ATerritorialExtractionPoint::GetPlayerFaction(APawn* Player) const
{
    // This would need to be implemented based on your player faction system
    // For now, return a default
    return EFactionID::Free77;
}

bool ATerritorialExtractionPoint::IsPlayerInExtractionZone(APawn* Player) const
{
    return PlayersInExtractionZone.Contains(Player);
}

bool ATerritorialExtractionPoint::IsPlayerInContestationZone(APawn* Player) const
{
    return PlayersInContestationZone.Contains(Player);
}

void ATerritorialExtractionPoint::NotifyTerritorialInfluenceGain(APawn* Player, int32 InfluenceAmount)
{
    // This would integrate with the territorial manager
    // TODO: Call UTerritorialManager::UpdateTerritorialInfluence
    UE_LOG(LogTemp, Log, TEXT("Player gained %d territorial influence at %s"), InfluenceAmount, *ExtractionPointName);
}

void ATerritorialExtractionPoint::UpdateTerritorialDisplay()
{
    // Update UI elements showing territorial control
}

void ATerritorialExtractionPoint::OnExtractionTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, 
    AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, 
    bool bFromSweep, const FHitResult& SweepResult)
{
    APawn* Player = Cast<APawn>(OtherActor);
    if (Player && !PlayersInExtractionZone.Contains(Player))
    {
        PlayersInExtractionZone.Add(Player);
        UpdateExtractionState();
    }
}

void ATerritorialExtractionPoint::OnExtractionTriggerEndOverlap(UPrimitiveComponent* OverlappedComponent, 
    AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
    APawn* Player = Cast<APawn>(OtherActor);
    if (Player)
    {
        PlayersInExtractionZone.Remove(Player);
        
        // Cancel extraction if this was the extracting player
        if (Player == CurrentExtractingPlayer)
        {
            CancelExtraction(TEXT("Player left extraction zone"));
        }
        
        UpdateExtractionState();
    }
}

void ATerritorialExtractionPoint::OnContestationZoneBeginOverlap(UPrimitiveComponent* OverlappedComponent, 
    AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, 
    bool bFromSweep, const FHitResult& SweepResult)
{
    APawn* Player = Cast<APawn>(OtherActor);
    if (Player && !PlayersInContestationZone.Contains(Player))
    {
        PlayersInContestationZone.Add(Player);
        UpdateExtractionState();
    }
}

void ATerritorialExtractionPoint::OnContestationZoneEndOverlap(UPrimitiveComponent* OverlappedComponent, 
    AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
    APawn* Player = Cast<APawn>(OtherActor);
    if (Player)
    {
        PlayersInContestationZone.Remove(Player);
        UpdateExtractionState();
    }
}