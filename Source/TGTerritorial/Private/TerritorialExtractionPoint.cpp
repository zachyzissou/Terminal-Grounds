// Copyright Terminal Grounds. All Rights Reserved.

#include "TerritorialExtractionPoint.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "TimerManager.h"
#include "TerritorialManager.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/Engine.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/DateTime.h"
#include "Math/UnrealMathUtility.h"
#include "Trust/TGTrustSubsystem.h"
#include "Subsystems/SubsystemBlueprintLibrary.h"

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
    FactionColors.Add(EFactionID::NomadClans, FLinearColor(0.6f, 0.3f, 0.1f, 1.0f));
    FactionColors.Add(EFactionID::VulturesUnion, FLinearColor(0.4f, 0.6f, 0.3f, 1.0f));
    FactionColors.Add(EFactionID::VaultedArchivists, FLinearColor(0.7f, 0.5f, 0.8f, 1.0f));
    FactionColors.Add(EFactionID::CorporateCombine, FLinearColor(0.9f, 0.9f, 0.2f, 1.0f));

    // Initialize faction-specific loot multipliers for performance optimization
    FactionLootMultipliers.Add(EFactionID::Directorate, 1.0f);        // Balanced
    FactionLootMultipliers.Add(EFactionID::Free77, 1.15f);           // Mercenary bonus
    FactionLootMultipliers.Add(EFactionID::NomadClans, 1.10f);       // Scavenging bonus
    FactionLootMultipliers.Add(EFactionID::CivicWardens, 0.95f);     // Civic duty penalty
    FactionLootMultipliers.Add(EFactionID::VulturesUnion, 1.25f);    // Scavenging expertise
    FactionLootMultipliers.Add(EFactionID::VaultedArchivists, 1.05f); // Knowledge bonus
    FactionLootMultipliers.Add(EFactionID::CorporateCombine, 1.20f);  // Corporate efficiency

    // Initialize performance optimization variables
    LastTerritorialCheck = 0.0f;
    LastBonusUpdate = 0.0f;
    CachedTerritorialController = EFactionID::None;
    bTerritorialStateValid = false;
    CachedTerritorialInfluenceMultiplier = 1.0f;
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

    // Initialize territorial system integration
    QueryTerritorialManager();
    
    // Initialize territorial state cache for performance
    UpdateTerritorialBonuses();
    ValidateTerritorialState();
    
    // Initialize visuals
    UpdateExtractionVisuals();

    UE_LOG(LogTemp, Log, TEXT("TerritorialExtractionPoint '%s' initialized for Territory %d"), *ExtractionPointName, TerritoryID);
}

void ATerritorialExtractionPoint::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    const float CurrentTime = GetWorld()->GetTimeSeconds();

    // Update extraction progress if in progress
    if (CurrentState == EExtractionState::InProgress && CurrentExtractingPlayer)
    {
        UpdateExtractionProgress(DeltaTime);
    }

    // Performance-optimized territorial checks (every 2 seconds instead of every frame)
    if (CurrentTime - LastTerritorialCheck > TERRITORIAL_CHECK_INTERVAL)
    {
        QueryTerritorialManager();
        ValidateTerritorialState();
        LastTerritorialCheck = CurrentTime;
    }

    // Update territorial bonuses less frequently (every 5 seconds)
    if (CurrentTime - LastBonusUpdate > BONUS_UPDATE_INTERVAL)
    {
        UpdateTerritorialBonuses();
        LastBonusUpdate = CurrentTime;
    }

    // Periodic state updates (reduced frequency for performance)
    if (CurrentTime - LastStateUpdate > 0.5f)
    {
        UpdateExtractionState();
        LastStateUpdate = CurrentTime;
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

    // Apply territorial trust modifiers to extraction time if player has trusted allies nearby
    if (UTGTrustSubsystem* TrustSystem = GetWorld()->GetGameInstance()->GetSubsystem<UTGTrustSubsystem>())
    {
        // Check for trusted allies in extraction zone who can provide trust bonus
        for (APawn* NearbyPlayer : PlayersInExtractionZone)
        {
            if (NearbyPlayer != Player)
            {
                float TrustModifier = TrustSystem->GetTerritorialTrustModifier(
                    Player->GetName(), 
                    NearbyPlayer->GetName(), 
                    TerritoryID
                );
                
                if (TrustModifier > 1.0f)
                {
                    // Trusted allies provide extraction speed bonus
                    CurrentExtractionTime = CurrentExtractionTime / FMath::Min(TrustModifier, 1.5f);
                    UE_LOG(LogTemp, Log, TEXT("Trust modifier applied: %f, new extraction time: %f"), TrustModifier, CurrentExtractionTime);
                }
            }
        }
    }

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

    // Record territorial betrayals if extraction was canceled due to ally attack
    if (UTGTrustSubsystem* TrustSystem = GetWorld()->GetGameInstance()->GetSubsystem<UTGTrustSubsystem>())
    {
        // Check if cancellation was due to betrayal by trusted ally
        if (Reason.Contains(TEXT("Attack")) || Reason.Contains(TEXT("Betrayal")) || Reason.Contains(TEXT("Combat")))
        {
            // Look for potential betrayers in contestation zone
            for (APawn* PotentialBetrayer : PlayersInContestationZone)
            {
                if (PotentialBetrayer != CurrentExtractingPlayer)
                {
                    EFactionID BetrayerFaction = GetPlayerFaction(PotentialBetrayer);
                    
                    // Check if this was a same-faction betrayal or ally betrayal
                    bool bSameFaction = (BetrayerFaction == PlayerFaction);
                    float CurrentTrust = TrustSystem->GetTrustIndex(
                        CurrentExtractingPlayer->GetName(), 
                        PotentialBetrayer->GetName()
                    );
                    
                    // Record betrayal if same faction or if there was existing trust
                    if (bSameFaction || CurrentTrust > 0.0f)
                    {
                        TrustSystem->RecordTerritorialBetrayal(
                            PotentialBetrayer->GetName(),
                            CurrentExtractingPlayer->GetName(),
                            TerritoryID,
                            bSameFaction ? 0.8f : 0.6f  // Higher penalty for same-faction betrayal
                        );
                        
                        UE_LOG(LogTemp, Warning, TEXT("Recorded territorial betrayal: %s betrayed %s during extraction (Reason: %s)"), 
                            *PotentialBetrayer->GetName(), *CurrentExtractingPlayer->GetName(), *Reason);
                    }
                }
            }
        }
    }

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

    // Record territorial trust for extraction assistance
    if (UTGTrustSubsystem* TrustSystem = GetWorld()->GetGameInstance()->GetSubsystem<UTGTrustSubsystem>())
    {
        // Record extraction assistance for any players who stayed in extraction zone during the process
        for (APawn* Helper : PlayersInExtractionZone)
        {
            if (Helper != CurrentExtractingPlayer)
            {
                TrustSystem->RecordExtractionAssistance(
                    Helper->GetName(),
                    CurrentExtractingPlayer->GetName(),
                    TerritoryID,
                    0.10f  // Standard extraction assistance bonus
                );
                
                UE_LOG(LogTemp, Log, TEXT("Recorded extraction assistance: %s helped %s"), 
                    *Helper->GetName(), *CurrentExtractingPlayer->GetName());
            }
        }

        // Record territorial cooperation for players in contestation zone who didn't interfere
        for (APawn* NearbyPlayer : PlayersInContestationZone)
        {
            if (NearbyPlayer != CurrentExtractingPlayer && 
                GetPlayerFaction(NearbyPlayer) != PlayerFaction && 
                !PlayersInExtractionZone.Contains(NearbyPlayer))
            {
                // Check if this was boundary respect (different faction, but didn't attack)
                TrustSystem->RecordBoundaryRespect(
                    CurrentExtractingPlayer->GetName(),
                    NearbyPlayer->GetName(),
                    TerritoryID,
                    0.04f  // Small trust gain for respecting extraction
                );
                
                UE_LOG(LogTemp, Log, TEXT("Recorded boundary respect: %s respected %s's extraction"), 
                    *NearbyPlayer->GetName(), *CurrentExtractingPlayer->GetName());
            }
        }
    }

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
    if (!Player)
    {
        return BaseExtractionTime;
    }

    float Time = BaseExtractionTime;
    const EFactionID PlayerFaction = GetPlayerFaction(Player);

    // Performance optimization: Use cached territorial state when available
    const EFactionID TerritoryController = bTerritorialStateValid ? CachedTerritorialController : GetTerritoryControllingFaction();

    // Apply faction bonus if player's faction controls the territory
    if (PlayerFaction == TerritoryController)
    {
        Time -= FactionBonusTime;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied faction control bonus: -%f seconds"), FactionBonusTime);
    }
    // Apply enemy territory penalty - significant risk/reward mechanic
    else if (IsPlayerInEnemyTerritory(Player))
    {
        Time *= EnemyTerritoryTimeMultiplier;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied enemy territory penalty: x%f multiplier"), EnemyTerritoryTimeMultiplier);
    }

    // Apply contestation penalty - dynamic based on threat level
    if (IsExtractionContested())
    {
        Time += ContestedPenaltyTime;
        
        // Additional vulnerability window in contested zones for enhanced risk/reward
        Time += VulnerabilityWindowTime;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied contestation penalties: +%f base, +%f vulnerability"), ContestedPenaltyTime, VulnerabilityWindowTime);
    }

    // Apply cached territorial influence multiplier for performance
    if (bTerritorialStateValid && CachedTerritorialInfluenceMultiplier != 1.0f)
    {
        Time *= (2.0f - CachedTerritorialInfluenceMultiplier); // Inverse relationship - higher influence = faster extraction
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied cached territorial influence: x%f"), (2.0f - CachedTerritorialInfluenceMultiplier));
    }

    // Faction-specific extraction bonuses for variety and balance
    switch (PlayerFaction)
    {
        case EFactionID::Free77:
            Time *= 0.95f; // Mercenary efficiency
            break;
        case EFactionID::VulturesUnion:
            Time *= 0.90f; // Scavenging expertise
            break;
        case EFactionID::CorporateCombine:
            Time *= 0.85f; // Corporate efficiency
            break;
        case EFactionID::CivicWardens:
            Time *= 1.05f; // Careful, methodical approach
            break;
        default:
            break; // No bonus/penalty
    }

    return FMath::Max(Time, 3.0f); // Minimum 3 seconds for competitive gameplay
}

float ATerritorialExtractionPoint::CalculateSuccessRate(APawn* Player) const
{
    if (!Player)
    {
        return ExtractionSuccessRate;
    }

    float Rate = ExtractionSuccessRate;
    const EFactionID PlayerFaction = GetPlayerFaction(Player);
    const EFactionID TerritoryController = bTerritorialStateValid ? CachedTerritorialController : GetTerritoryControllingFaction();

    // Apply faction control bonus - significant advantage in controlled territory
    if (PlayerFaction == TerritoryController)
    {
        Rate += FactionControlledBonus;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied faction control bonus: +%f"), FactionControlledBonus);
    }
    // Apply enemy territory penalty - high risk, high reward
    else if (IsPlayerInEnemyTerritory(Player))
    {
        Rate -= EnemyTerritoryPenalty;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied enemy territory penalty: -%f"), EnemyTerritoryPenalty);
    }

    // Apply contestation penalty - dynamic threat assessment
    if (IsExtractionContested())
    {
        Rate -= ContestedSuccessRatePenalty;
        
        // Additional penalty based on number of contesting factions
        const TSet<EFactionID> ContestingFactions = GetContestingFactions();
        if (ContestingFactions.Num() > 2)
        {
            Rate -= 0.05f * (ContestingFactions.Num() - 2); // -5% per additional faction
        }
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied contestation penalty: -%f, additional factions: %d"), ContestedSuccessRatePenalty, FMath::Max(0, ContestingFactions.Num() - 2));
    }

    // Apply territorial influence multiplier from cache for performance
    if (bTerritorialStateValid)
    {
        Rate *= CachedTerritorialInfluenceMultiplier;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied territorial influence multiplier: x%f"), CachedTerritorialInfluenceMultiplier);
    }

    // Faction-specific success rate modifiers
    switch (PlayerFaction)
    {
        case EFactionID::Directorate:
            Rate += 0.05f; // Military precision
            break;
        case EFactionID::VaultedArchivists:
            Rate += 0.03f; // Methodical approach
            break;
        case EFactionID::NomadClans:
            Rate += 0.02f; // Survival instincts
            break;
        case EFactionID::VulturesUnion:
            Rate -= 0.02f; // Reckless scavenging
            break;
        default:
            break;
    }

    // Territory type modifiers for strategic depth
    const ETerritoryType ZoneType = GetTerritorialZoneType();
    switch (ZoneType)
    {
        case ETerritoryType::Region:
            Rate += 0.05f; // Major strategic points are well-maintained
            break;
        case ETerritoryType::District:
            // No modifier - balanced
            break;
        case ETerritoryType::ControlPoint:
            Rate -= 0.03f; // Contested control points are dangerous
            break;
    }

    return FMath::Clamp(Rate, 0.05f, 0.98f); // 5% minimum, 98% maximum for gameplay balance
}

int32 ATerritorialExtractionPoint::CalculateTerritorialInfluence(APawn* Player) const
{
    if (!Player)
    {
        return BaseTerritorialInfluence;
    }

    int32 Influence = BaseTerritorialInfluence;
    const EFactionID PlayerFaction = GetPlayerFaction(Player);
    const EFactionID TerritoryController = bTerritorialStateValid ? CachedTerritorialController : GetTerritoryControllingFaction();

    // Base territorial influence with performance-optimized calculations
    if (PlayerFaction == TerritoryController)
    {
        Influence += ControlleredTerritoryBonus;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied controlled territory bonus: +%d"), ControlleredTerritoryBonus);
    }
    else if (IsPlayerInEnemyTerritory(Player))
    {
        // Higher influence gain in enemy territory as risk/reward
        Influence = FMath::RoundToInt(Influence * 1.5f);
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied enemy territory risk bonus: x1.5"));
    }

    // Apply cached territorial multiplier for consistent performance
    if (bTerritorialStateValid)
    {
        Influence = FMath::RoundToInt(Influence * CachedTerritorialInfluenceMultiplier);
    }

    // Faction-specific influence modifiers based on faction strengths
    switch (PlayerFaction)
    {
        case EFactionID::Directorate:
            Influence = FMath::RoundToInt(Influence * 1.10f); // Military efficiency
            break;
        case EFactionID::Free77:
            Influence = FMath::RoundToInt(Influence * 1.05f); // Mercenary reputation
            break;
        case EFactionID::CorporateCombine:
            Influence = FMath::RoundToInt(Influence * 1.15f); // Corporate resources
            break;
        case EFactionID::NomadClans:
            Influence = FMath::RoundToInt(Influence * 0.95f); // Decentralized structure
            break;
        case EFactionID::VulturesUnion:
            Influence = FMath::RoundToInt(Influence * 0.90f); // Scavenging focus over politics
            break;
        case EFactionID::VaultedArchivists:
            Influence = FMath::RoundToInt(Influence * 1.08f); // Knowledge is power
            break;
        case EFactionID::CivicWardens:
            Influence = FMath::RoundToInt(Influence * 1.12f); // Civic legitimacy
            break;
        default:
            break;
    }

    // Contest penalty - reduced influence when fighting multiple factions
    if (IsExtractionContested())
    {
        const TSet<EFactionID> ContestingFactions = GetContestingFactions();
        if (ContestingFactions.Num() > 2)
        {
            const float Penalty = 1.0f - (0.1f * (ContestingFactions.Num() - 2));
            Influence = FMath::RoundToInt(Influence * FMath::Max(0.5f, Penalty));
        }
    }

    return FMath::Max(Influence, 1); // Minimum 1 influence point
}

bool ATerritorialExtractionPoint::IsExtractionContested() const
{
    // Performance-optimized contestation check with early exit
    if (PlayersInContestationZone.Num() < 2)
    {
        return false; // Need at least 2 players for potential contest
    }
    
    // Use cached faction detection for performance
    TSet<EFactionID> FactionsPresent;
    FactionsPresent.Reserve(7); // Reserve space for all possible factions
    
    for (const APawn* Player : PlayersInContestationZone)
    {
        if (Player)
        {
            const EFactionID PlayerFaction = GetPlayerFaction(Player);
            if (PlayerFaction != EFactionID::None)
            {
                FactionsPresent.Add(PlayerFaction);
                
                // Early exit optimization - if we already have 2+ factions, it's contested
                if (FactionsPresent.Num() >= 2)
                {
                    return true;
                }
            }
        }
    }
    
    return false;
}

EFactionID ATerritorialExtractionPoint::GetTerritoryControllingFaction() const
{
    // Performance optimization: Use cached value when available
    if (bTerritorialStateValid)
    {
        return CachedTerritorialController;
    }
    
    // Fallback to OwningFaction if cache is invalid
    return OwningFaction;
}

void ATerritorialExtractionPoint::UpdateExtractionVisuals()
{
    // Performance-optimized visual updates with state change detection
    static EExtractionState LastVisualState = EExtractionState::Available;
    static EFactionID LastVisualFaction = EFactionID::None;
    
    // Only update visuals if state or controlling faction changed
    const EFactionID CurrentController = GetTerritoryControllingFaction();
    if (CurrentState != LastVisualState || CurrentController != LastVisualFaction)
    {
        // Update extraction platform materials based on state
        if (ExtractionPlatform && ExtractionPlatform->GetMaterial(0))
        {
            UMaterialInstanceDynamic* DynamicMaterial = ExtractionPlatform->CreateAndSetMaterialInstanceDynamic(0);
            if (DynamicMaterial)
            {
                // Set faction color
                if (const FLinearColor* FactionColor = FactionColors.Find(CurrentController))
                {
                    DynamicMaterial->SetVectorParameterValue(TEXT("FactionColor"), *FactionColor);
                }
                
                // Set extraction state parameters
                switch (CurrentState)
                {
                    case EExtractionState::Available:
                        DynamicMaterial->SetScalarParameterValue(TEXT("EmissiveIntensity"), 1.0f);
                        DynamicMaterial->SetScalarParameterValue(TEXT("PulseRate"), 0.5f);
                        break;
                    case EExtractionState::InProgress:
                        DynamicMaterial->SetScalarParameterValue(TEXT("EmissiveIntensity"), 2.0f);
                        DynamicMaterial->SetScalarParameterValue(TEXT("PulseRate"), 2.0f);
                        break;
                    case EExtractionState::Contested:
                        DynamicMaterial->SetVectorParameterValue(TEXT("FactionColor"), FLinearColor::Red);
                        DynamicMaterial->SetScalarParameterValue(TEXT("EmissiveIntensity"), 3.0f);
                        DynamicMaterial->SetScalarParameterValue(TEXT("PulseRate"), 4.0f);
                        break;
                    case EExtractionState::Unavailable:
                        DynamicMaterial->SetScalarParameterValue(TEXT("EmissiveIntensity"), 0.2f);
                        DynamicMaterial->SetScalarParameterValue(TEXT("PulseRate"), 0.0f);
                        break;
                    case EExtractionState::Compromised:
                        DynamicMaterial->SetVectorParameterValue(TEXT("FactionColor"), FLinearColor::Yellow);
                        DynamicMaterial->SetScalarParameterValue(TEXT("EmissiveIntensity"), 1.5f);
                        DynamicMaterial->SetScalarParameterValue(TEXT("PulseRate"), 3.0f);
                        break;
                }
            }
        }
        
        LastVisualState = CurrentState;
        LastVisualFaction = CurrentController;
        
        UE_LOG(LogTemp, VeryVerbose, TEXT("Updated extraction visuals: State=%d, Controller=%d"), 
            static_cast<int32>(CurrentState), static_cast<int32>(CurrentController));
    }
    
    // Update extraction progress visualization if in progress
    if (CurrentState == EExtractionState::InProgress && ExtractionProgress > 0.0f)
    {
        // Update progress ring or bar materials
        if (ExtractionPlatform)
        {
            UMaterialInstanceDynamic* DynamicMaterial = ExtractionPlatform->CreateAndSetMaterialInstanceDynamic(0);
            if (DynamicMaterial)
            {
                DynamicMaterial->SetScalarParameterValue(TEXT("ExtractionProgress"), ExtractionProgress);
            }
        }
    }
}

void ATerritorialExtractionPoint::SetFactionControlVisuals(EFactionID ControllingFaction)
{
    // Performance optimization: Only update if faction actually changed
    if (OwningFaction == ControllingFaction)
    {
        return;
    }
    
    const EFactionID PreviousFaction = OwningFaction;
    OwningFaction = ControllingFaction;
    
    // Update cached territorial controller for performance
    CachedTerritorialController = ControllingFaction;
    bTerritorialStateValid = true;
    
    // Batch visual updates for performance
    if (const FLinearColor* FactionColor = FactionColors.Find(ControllingFaction))
    {
        // Update extraction platform materials
        if (ExtractionPlatform)
        {
            UMaterialInstanceDynamic* DynamicMaterial = ExtractionPlatform->CreateAndSetMaterialInstanceDynamic(0);
            if (DynamicMaterial)
            {
                DynamicMaterial->SetVectorParameterValue(TEXT("FactionColor"), *FactionColor);
                DynamicMaterial->SetScalarParameterValue(TEXT("FactionControlStrength"), 1.0f);
            }
        }
        
        // Update trigger zone materials for better player feedback
        if (ExtractionTrigger)
        {
            // Optional: Add visual ring around extraction trigger
        }
    }
    
    // Update territorial display
    UpdateTerritorialDisplay();
    UpdateExtractionVisuals();
    
    UE_LOG(LogTemp, Log, TEXT("Faction control visuals updated for %s: %d -> %d"), 
        *ExtractionPointName, static_cast<int32>(PreviousFaction), static_cast<int32>(ControllingFaction));
}

void ATerritorialExtractionPoint::UpdateExtractionState()
{
    // Performance-optimized state updates with batch processing
    const EExtractionState PreviousState = CurrentState;
    
    // Batch check contestation status for performance
    const bool bIsContested = IsExtractionContested();
    const bool bHasExtractingPlayer = (CurrentExtractingPlayer != nullptr);
    
    // Determine new state based on conditions
    if (bHasExtractingPlayer && CurrentState == EExtractionState::InProgress)
    {
        if (bIsContested)
        {
            CurrentState = EExtractionState::Contested;
        }
        // Check if player left extraction zone
        else if (!IsPlayerInExtractionZone(CurrentExtractingPlayer))
        {
            CancelExtraction(TEXT("Player left extraction zone during state update"));
            return;
        }
    }
    else if (CurrentState == EExtractionState::Contested)
    {
        if (!bIsContested && bHasExtractingPlayer)
        {
            CurrentState = EExtractionState::InProgress;
        }
        else if (!bHasExtractingPlayer)
        {
            CurrentState = EExtractionState::Available;
        }
    }
    else if (!bHasExtractingPlayer && PlayersInExtractionZone.Num() == 0)
    {
        CurrentState = EExtractionState::Available;
    }
    
    // Only update visuals if state actually changed (performance optimization)
    if (PreviousState != CurrentState)
    {
        UpdateExtractionVisuals();
        UE_LOG(LogTemp, VeryVerbose, TEXT("Extraction state changed: %d -> %d"), static_cast<int32>(PreviousState), static_cast<int32>(CurrentState));
    }
    
    // Batch territorial validation less frequently
    static float LastValidationCheck = 0.0f;
    const float CurrentTime = GetWorld()->GetTimeSeconds();
    if (CurrentTime - LastValidationCheck > 10.0f) // Validate every 10 seconds
    {
        ValidateTerritorialState();
        LastValidationCheck = CurrentTime;
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
    // Performance-optimized contestation checking with caching
    static TSet<EFactionID> LastContestingFactions;
    static float LastContestationCheck = 0.0f;
    const float CurrentTime = GetWorld()->GetTimeSeconds();
    
    // Only perform expensive contestation check every 0.5 seconds
    if (CurrentTime - LastContestationCheck > 0.5f)
    {
        const TSet<EFactionID> CurrentContestingFactions = GetContestingFactions();
        
        // Only log if contestation status changed
        if (CurrentContestingFactions != LastContestingFactions)
        {
            const bool bWasContested = LastContestingFactions.Num() > 1;
            const bool bIsContested = CurrentContestingFactions.Num() > 1;
            
            if (bWasContested != bIsContested)
            {
                UE_LOG(LogTemp, Log, TEXT("Contestation status changed for %s: %s (%d factions)"), 
                    *ExtractionPointName, 
                    bIsContested ? TEXT("CONTESTED") : TEXT("UNCONTESTED"), 
                    CurrentContestingFactions.Num());
            }
            
            LastContestingFactions = CurrentContestingFactions;
        }
        
        LastContestationCheck = CurrentTime;
    }
}

EFactionID ATerritorialExtractionPoint::GetPlayerFaction(APawn* Player) const
{
    if (!Player)
    {
        return EFactionID::None;
    }

    // Performance-optimized faction lookup
    // This implementation assumes faction is stored on the player controller or pawn
    // Replace with actual faction system integration
    
    // Method 1: Try to get faction from player controller
    if (APlayerController* PC = Cast<APlayerController>(Player->GetController()))
    {
        // Attempt to get faction from player state or controller
        // This is a placeholder - replace with actual faction system call
        // Example: return PC->GetPlayerState<ATGPlayerState>()->GetFaction();
    }
    
    // Method 2: Try to get faction from pawn directly
    // Example: if (ITGFactionInterface* FactionInterface = Cast<ITGFactionInterface>(Player))
    // {
    //     return FactionInterface->GetFaction();
    // }
    
    // Method 3: Fallback to team-based faction mapping
    if (Player->GetActorNameOrLabel().Contains(TEXT("Directorate")))
        return EFactionID::Directorate;
    else if (Player->GetActorNameOrLabel().Contains(TEXT("Free77")))
        return EFactionID::Free77;
    else if (Player->GetActorNameOrLabel().Contains(TEXT("Nomad")))
        return EFactionID::NomadClans;
    else if (Player->GetActorNameOrLabel().Contains(TEXT("Civic")))
        return EFactionID::CivicWardens;
    else if (Player->GetActorNameOrLabel().Contains(TEXT("Vulture")))
        return EFactionID::VulturesUnion;
    else if (Player->GetActorNameOrLabel().Contains(TEXT("Archive")))
        return EFactionID::VaultedArchivists;
    else if (Player->GetActorNameOrLabel().Contains(TEXT("Corporate")))
        return EFactionID::CorporateCombine;
    
    // Default fallback - in production this should integrate with actual faction system
    UE_LOG(LogTemp, VeryVerbose, TEXT("Unable to determine faction for player %s - defaulting to Free77"), *Player->GetName());
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

float ATerritorialExtractionPoint::CalculateLootMultiplier(APawn* Player) const
{
    if (!Player)
    {
        return 1.0f;
    }

    float Multiplier = 1.0f;
    const EFactionID PlayerFaction = GetPlayerFaction(Player);
    const EFactionID TerritoryController = bTerritorialStateValid ? CachedTerritorialController : GetTerritoryControllingFaction();

    // Base territory control bonuses - performance optimized with caching
    if (PlayerFaction == TerritoryController)
    {
        Multiplier *= ControlledTerritoryLootBonus; // 25% bonus in controlled territory
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied controlled territory loot bonus: x%f"), ControlledTerritoryLootBonus);
    }
    else if (IsPlayerInEnemyTerritory(Player))
    {
        Multiplier *= EnemyTerritoryLootBonus; // 75% bonus in enemy territory (high risk/reward)
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied enemy territory loot bonus: x%f"), EnemyTerritoryLootBonus);
    }

    // Faction-specific loot multipliers - cached for performance
    if (const float* FactionMultiplier = FactionLootMultipliers.Find(PlayerFaction))
    {
        Multiplier *= *FactionMultiplier;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied faction loot multiplier: x%f"), *FactionMultiplier);
    }

    // Contestation bonus - more valuable loot in dangerous areas
    if (IsExtractionContested())
    {
        const TSet<EFactionID> ContestingFactions = GetContestingFactions();
        const float ContestMultiplier = 1.0f + (0.15f * ContestingFactions.Num()); // 15% per contesting faction
        Multiplier *= ContestMultiplier;
        UE_LOG(LogTemp, VeryVerbose, TEXT("Applied contestation loot bonus: x%f (%d factions)"), ContestMultiplier, ContestingFactions.Num());
    }

    // Territory type modifiers for strategic depth
    const ETerritoryType ZoneType = GetTerritorialZoneType();
    switch (ZoneType)
    {
        case ETerritoryType::Region:
            Multiplier *= 1.20f; // Major strategic locations have better loot
            break;
        case ETerritoryType::District:
            Multiplier *= 1.10f; // Moderate bonus
            break;
        case ETerritoryType::ControlPoint:
            Multiplier *= 1.30f; // Highest risk, highest reward
            break;
    }

    // Apply cached territorial influence for performance
    if (bTerritorialStateValid)
    {
        Multiplier *= FMath::Lerp(0.95f, 1.05f, CachedTerritorialInfluenceMultiplier);
    }

    return FMath::Clamp(Multiplier, 0.5f, 3.0f); // Reasonable bounds for gameplay balance
}

bool ATerritorialExtractionPoint::IsPlayerInEnemyTerritory(APawn* Player) const
{
    if (!Player)
    {
        return false;
    }

    const EFactionID PlayerFaction = GetPlayerFaction(Player);
    const EFactionID TerritoryController = bTerritorialStateValid ? CachedTerritorialController : GetTerritoryControllingFaction();

    // Performance optimization: Use cached territorial controller when available
    return (PlayerFaction != EFactionID::None && 
            TerritoryController != EFactionID::None && 
            PlayerFaction != TerritoryController);
}

ETerritoryType ATerritorialExtractionPoint::GetTerritorialZoneType() const
{
    // This would normally query the territorial manager for zone type
    // For now, determine based on TerritoryID ranges (can be optimized further with caching)
    if (TerritoryID < 100)
    {
        return ETerritoryType::Region;
    }
    else if (TerritoryID < 1000)
    {
        return ETerritoryType::District;
    }
    else
    {
        return ETerritoryType::ControlPoint;
    }
}

void ATerritorialExtractionPoint::ApplyTerritorialExtractionBonuses(APawn* Player, TArray<UObject*>& LootItems) const
{
    if (!Player || LootItems.Num() == 0)
    {
        return;
    }

    const float LootMultiplier = CalculateLootMultiplier(Player);
    
    // Apply loot multiplier effects (implementation depends on UItem class structure)
    // This is a placeholder for the actual loot modification logic
    UE_LOG(LogTemp, Log, TEXT("Applied territorial loot bonuses with multiplier %f to %d items"), LootMultiplier, LootItems.Num());
    
    // Example implementation:
    // for (UItem* Item : LootItems)
    // {
    //     if (Item)
    //     {
    //         Item->ApplyQuantityMultiplier(LootMultiplier);
    //         Item->ApplyQualityBonus(GetTerritorialQualityBonus());
    //     }
    // }
}

void ATerritorialExtractionPoint::NotifyTerritorialInfluenceGain(APawn* Player, int32 InfluenceAmount)
{
    if (!Player)
    {
        return;
    }

    // Integration with UTerritorialManager for real influence updates
    if (UTerritorialSubsystem* TerritorialSubsystem = GetWorld()->GetSubsystem<UTerritorialSubsystem>())
    {
        if (UTerritorialManager* TerritorialManager = TerritorialSubsystem->GetTerritorialManager(this))
        {
            const EFactionID PlayerFaction = GetPlayerFaction(Player);
            const ETerritoryType ZoneType = GetTerritorialZoneType();
            
            // Update territorial influence through the manager
            const bool bUpdateSuccess = TerritorialManager->UpdateTerritorialInfluence(
                TerritoryID, 
                ZoneType, 
                static_cast<int32>(PlayerFaction), 
                InfluenceAmount, 
                FString::Printf(TEXT("Extraction at %s"), *ExtractionPointName)
            );

            if (bUpdateSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Successfully updated territorial influence: Player faction %d gained %d influence in territory %d"), 
                    static_cast<int32>(PlayerFaction), InfluenceAmount, TerritoryID);
                
                // Invalidate cache to force refresh on next check
                bTerritorialStateValid = false;
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("Failed to update territorial influence for territory %d"), TerritoryID);
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("TerritorialSubsystem not available - influence gain not recorded"));
    }
}

TSet<EFactionID> ATerritorialExtractionPoint::GetContestingFactions() const
{
    TSet<EFactionID> ContestingFactions;
    
    // Performance-optimized faction detection
    for (const APawn* Player : PlayersInContestationZone)
    {
        if (Player)
        {
            ContestingFactions.Add(GetPlayerFaction(Player));
        }
    }
    
    // Remove 'None' faction if present
    ContestingFactions.Remove(EFactionID::None);
    
    return ContestingFactions;
}

void ATerritorialExtractionPoint::QueryTerritorialManager()
{
    // Performance-optimized territorial manager queries
    if (UTerritorialSubsystem* TerritorialSubsystem = GetWorld()->GetSubsystem<UTerritorialSubsystem>())
    {
        if (UTerritorialManager* TerritorialManager = TerritorialSubsystem->GetTerritorialManager(this))
        {
            const ETerritoryType ZoneType = GetTerritorialZoneType();
            const FTerritorialState TerritorialState = TerritorialManager->GetTerritorialState(TerritoryID, ZoneType);
            
            // Update cached state for performance
            if (TerritorialState.TerritoryID == TerritoryID)
            {
                CachedTerritorialController = static_cast<EFactionID>(TerritorialState.DominantFaction);
                bTerritorialStateValid = true;
                
                // Calculate influence multiplier for performance caching
                float MaxInfluence = 0.0f;
                for (const auto& InfluencePair : TerritorialState.FactionInfluences)
                {
                    MaxInfluence = FMath::Max(MaxInfluence, static_cast<float>(InfluencePair.Value));
                }
                CachedTerritorialInfluenceMultiplier = FMath::Clamp(MaxInfluence / 100.0f, 0.5f, 1.5f);
                
                UE_LOG(LogTemp, VeryVerbose, TEXT("Updated territorial cache: Controller=%d, Multiplier=%f"), 
                    static_cast<int32>(CachedTerritorialController), CachedTerritorialInfluenceMultiplier);
            }
        }
    }
}

void ATerritorialExtractionPoint::UpdateTerritorialBonuses()
{
    // Batch update territorial bonuses for performance
    QueryTerritorialManager();
    
    // Update visual elements based on cached territorial state
    if (bTerritorialStateValid)
    {
        SetFactionControlVisuals(CachedTerritorialController);
    }
    
    UpdateTerritorialDisplay();
}

bool ATerritorialExtractionPoint::ValidateTerritorialState()
{
    // Validate that our cached territorial state is consistent
    if (!bTerritorialStateValid)
    {
        QueryTerritorialManager();
    }
    
    // Check for state consistency
    const bool bStateConsistent = (CachedTerritorialController != EFactionID::None) && 
                                   (CachedTerritorialInfluenceMultiplier > 0.0f) &&
                                   (TerritoryID > 0);
    
    if (!bStateConsistent)
    {
        UE_LOG(LogTemp, Warning, TEXT("Territorial state validation failed for territory %d - forcing refresh"), TerritoryID);
        bTerritorialStateValid = false;
        QueryTerritorialManager();
    }
    
    return bStateConsistent;
}

void ATerritorialExtractionPoint::OnTerritorialControlChanged(int32 ChangedTerritoryID, EFactionID OldFaction, EFactionID NewFaction)
{
    // Handle territorial control changes for this extraction point
    if (ChangedTerritoryID == TerritoryID)
    {
        UE_LOG(LogTemp, Log, TEXT("Territorial control changed for extraction point %s: %d -> %d"), 
            *ExtractionPointName, static_cast<int32>(OldFaction), static_cast<int32>(NewFaction));
        
        // Invalidate cache and update immediately
        bTerritorialStateValid = false;
        QueryTerritorialManager();
        UpdateTerritorialBonuses();
        
        // Cancel any ongoing extractions if control changed to hostile faction
        if (CurrentExtractingPlayer && GetPlayerFaction(CurrentExtractingPlayer) != NewFaction)
        {
            CancelExtraction(TEXT("Territorial control changed to hostile faction"));
        }
    }
}

void ATerritorialExtractionPoint::UpdateTerritorialDisplay()
{
    // Update UI elements showing territorial control with performance optimization
    if (bTerritorialStateValid)
    {
        // Only update display if territorial state has changed
        static EFactionID LastDisplayedController = EFactionID::None;
        if (CachedTerritorialController != LastDisplayedController)
        {
            // Update faction colors and indicators
            SetFactionControlVisuals(CachedTerritorialController);
            LastDisplayedController = CachedTerritorialController;
            
            UE_LOG(LogTemp, VeryVerbose, TEXT("Updated territorial display for controller %d"), static_cast<int32>(CachedTerritorialController));
        }
    }
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