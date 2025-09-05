// Copyright Terminal Grounds. All Rights Reserved.

#include "TerritorialControlWidget.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "TGTerritorial/Public/TerritorialManager.h"
#include "TGTerritorial/Public/PhaseGateComponent.h"
#include "TGTerritorial/Public/DominanceMeterComponent.h"
#include "TGTerritorial/Public/TicketPoolComponent.h"

void UTerritorialControlWidget::NativeConstruct()
{
    Super::NativeConstruct();

    // Initialize faction colors
    InitializeFactionColors();

    // Get territorial manager reference
    if (UWorld* World = GetWorld())
    {
        if (UTerritorialSubsystem* TerritorialSubsystem = World->GetSubsystem<UTerritorialSubsystem>())
        {
            TerritorialManager = TerritorialSubsystem->GetTerritorialManager(this);
        }

        // Get player pawn reference
        if (APlayerController* PC = World->GetFirstPlayerController())
        {
            PlayerPawn = PC->GetPawn();
        }
    }

    // Initial data refresh
    RefreshTerritorialData();

    UE_LOG(LogTemp, Log, TEXT("TerritorialControlWidget constructed"));
}

void UTerritorialControlWidget::NativeDestruct()
{
    Super::NativeDestruct();
    
    TerritorialManager = nullptr;
    PlayerPawn = nullptr;
}

void UTerritorialControlWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);

    LastUpdateTime += InDeltaTime;

    // Update territorial data at specified interval
    if (LastUpdateTime >= UpdateInterval)
    {
        RefreshTerritorialData();
        LastUpdateTime = 0.0f;
    }
}

void UTerritorialControlWidget::RefreshTerritorialData()
{
    if (!TerritorialManager)
    {
        return;
    }

    TArray<FTerritorialDisplayData> NewTerritorialData;

    // Get territorial data for all regions (hardcoded for Phase 1)
    for (int32 RegionID = 1; RegionID <= 8; RegionID++)
    {
        FTerritorialState State = TerritorialManager->GetTerritorialState(RegionID, ETerritoryType::Region);
        
        FTerritorialDisplayData DisplayData = ConvertTerritorialState(State);
        DisplayData.TerritoryName = GetTerritoryName(RegionID);
        
        NewTerritorialData.Add(DisplayData);
    }

    // Sort by strategic importance (contested territories first)
    NewTerritorialData.Sort([](const FTerritorialDisplayData& A, const FTerritorialDisplayData& B)
    {
        if (A.bIsContested != B.bIsContested)
        {
            return A.bIsContested > B.bIsContested; // Contested territories first
        }
        return A.ControlPercentage > B.ControlPercentage; // Then by control percentage
    });

    // Limit to max territories to show
    if (NewTerritorialData.Num() > MaxTerritoriesToShow)
    {
        NewTerritorialData.SetNum(MaxTerritoriesToShow);
    }

    // Update territorial data
    TerritorialData = NewTerritorialData;

    // Get current player territory
    GetPlayerCurrentTerritory();

    // Update display
    UpdateTerritorialDisplay();
}

void UTerritorialControlWidget::UpdateTerritorialDisplay()
{
    // Fire Blueprint event for UI updates
    OnTerritorialDataUpdated(TerritorialData);

    // Fire individual events for territory changes
    for (const FTerritorialDisplayData& Data : TerritorialData)
    {
        OnTerritorialDisplayUpdate.Broadcast(Data);
        
        if (Data.bIsContested)
        {
            OnTerritoryContested(Data);
        }
    }
}

FLinearColor UTerritorialControlWidget::GetFactionColor(int32 FactionID) const
{
    if (const FLinearColor* Color = FactionColorMap.Find(FactionID))
    {
        return *Color;
    }

    // Default colors if not found in map
    switch (FactionID)
    {
    case 1: return FLinearColor(0.2f, 0.4f, 0.8f, 1.0f); // Sky Bastion Directorate - Blue
    case 2: return FLinearColor(0.6f, 0.3f, 0.1f, 1.0f); // Iron Scavengers - Orange/Brown
    case 3: return FLinearColor(0.3f, 0.3f, 0.3f, 1.0f); // The Seventy-Seven - Gray
    case 4: return FLinearColor(0.0f, 0.7f, 0.9f, 1.0f); // Corporate Hegemony - Cyan
    case 5: return FLinearColor(0.4f, 0.2f, 0.0f, 1.0f); // Nomad Clans - Brown
    case 6: return FLinearColor(0.5f, 0.2f, 0.7f, 1.0f); // Archive Keepers - Purple
    case 7: return FLinearColor(0.1f, 0.6f, 0.2f, 1.0f); // Civic Wardens - Green
    default: return FLinearColor(1.0f, 1.0f, 1.0f, 1.0f); // Neutral - White
    }
}

FString UTerritorialControlWidget::GetFactionName(int32 FactionID) const
{
    switch (FactionID)
    {
    case 1: return TEXT("Sky Bastion Directorate");
    case 2: return TEXT("Iron Scavengers");
    case 3: return TEXT("The Seventy-Seven");
    case 4: return TEXT("Corporate Hegemony");
    case 5: return TEXT("Nomad Clans");
    case 6: return TEXT("Archive Keepers");
    case 7: return TEXT("Civic Wardens");
    default: return TEXT("Neutral");
    }
}

FString UTerritorialControlWidget::GetTerritoryName(int32 TerritoryID) const
{
    switch (TerritoryID)
    {
    case 1: return TEXT("Tech Wastes");
    case 2: return TEXT("Metro Corridors");
    case 3: return TEXT("Corporate Zones");
    case 4: return TEXT("Residential Districts");
    case 5: return TEXT("Military Compounds");
    case 6: return TEXT("Research Facilities");
    case 7: return TEXT("Trade Routes");
    case 8: return TEXT("Neutral Ground");
    default: return FString::Printf(TEXT("Territory %d"), TerritoryID);
    }
}

FString UTerritorialControlWidget::GetTerritoryStatusText(const FTerritorialDisplayData& TerritoryData) const
{
    if (TerritoryData.bIsContested)
    {
        return TEXT("CONTESTED");
    }
    else if (TerritoryData.ControlPercentage >= 75.0f)
    {
        return TEXT("SECURE");
    }
    else if (TerritoryData.ControlPercentage >= 50.0f)
    {
        return TEXT("CONTROLLED");
    }
    else if (TerritoryData.ControlPercentage >= 25.0f)
    {
        return TEXT("DISPUTED");
    }
    else
    {
        return TEXT("NEUTRAL");
    }
}

bool UTerritorialControlWidget::ShouldShowTerritoryDetails(const FTerritorialDisplayData& TerritoryData) const
{
    if (!bShowDetailedInfo)
    {
        return false;
    }

    // Always show contested territories
    if (TerritoryData.bIsContested && bShowContestationIndicators)
    {
        return true;
    }

    // Show territories with significant control
    return TerritoryData.ControlPercentage >= 25.0f;
}

void UTerritorialControlWidget::InitializeFactionColors()
{
    // Initialize default faction colors
    FactionColorMap.Add(1, FLinearColor(0.2f, 0.4f, 0.8f, 1.0f)); // Directorate - Blue
    FactionColorMap.Add(2, FLinearColor(0.6f, 0.3f, 0.1f, 1.0f)); // Iron Scavengers - Orange
    FactionColorMap.Add(3, FLinearColor(0.3f, 0.3f, 0.3f, 1.0f)); // Seventy-Seven - Gray
    FactionColorMap.Add(4, FLinearColor(0.0f, 0.7f, 0.9f, 1.0f)); // Corporate - Cyan
    FactionColorMap.Add(5, FLinearColor(0.4f, 0.2f, 0.0f, 1.0f)); // Nomads - Brown
    FactionColorMap.Add(6, FLinearColor(0.5f, 0.2f, 0.7f, 1.0f)); // Archivists - Purple
    FactionColorMap.Add(7, FLinearColor(0.1f, 0.6f, 0.2f, 1.0f)); // Wardens - Green
}

void UTerritorialControlWidget::GetPlayerCurrentTerritory()
{
    if (!PlayerPawn || !TerritorialManager)
    {
        return;
    }

    // For Phase 1, determine player territory based on location
    // This would be enhanced with actual territorial boundary detection
    FVector PlayerLocation = PlayerPawn->GetActorLocation();
    
    // Simplified territory detection (would be replaced with proper spatial queries)
    int32 PlayerTerritoryID = 1; // Default to Tech Wastes
    
    // Get territorial state for player's current territory
    FTerritorialState PlayerState = TerritorialManager->GetTerritorialState(PlayerTerritoryID, ETerritoryType::Region);
    CurrentPlayerTerritory = ConvertTerritorialState(PlayerState);
    CurrentPlayerTerritory.TerritoryName = GetTerritoryName(PlayerTerritoryID);
}

FTerritorialDisplayData UTerritorialControlWidget::ConvertTerritorialState(const FTerritorialState& State)
{
    FTerritorialDisplayData DisplayData;
    
    DisplayData.TerritoryID = State.TerritoryID;
    DisplayData.DominantFactionID = State.DominantFaction;
    DisplayData.DominantFactionName = GetFactionName(State.DominantFaction);
    DisplayData.bIsContested = State.bIsContested;
    DisplayData.FactionColor = GetFactionColor(State.DominantFaction);

    // Calculate control percentage from faction influences
    int32 TotalInfluence = 0;
    int32 DominantInfluence = 0;
    
    for (const auto& Influence : State.FactionInfluences)
    {
        TotalInfluence += Influence.Value;
        if (Influence.Key == State.DominantFaction)
        {
            DominantInfluence = Influence.Value;
        }
    }

    DisplayData.ControlPercentage = TotalInfluence > 0 ? (float)DominantInfluence / (float)TotalInfluence * 100.0f : 0.0f;

    // Get contesting factions (factions with >30% influence)
    for (const auto& Influence : State.FactionInfluences)
    {
        if (Influence.Value >= 30 && Influence.Key != State.DominantFaction)
        {
            DisplayData.ContestingFactions.Add(Influence.Key);
        }
    }

    return DisplayData;
}

// Siege Implementation Methods
void UTerritorialControlWidget::RefreshSiegeData()
{
    if (!ShouldShowSiegeUI())
    {
        return;
    }

    FSiegeDisplayData NewSiegeData;
    NewSiegeData.bSiegeActive = true;

    // Update Phase Data
    if (BoundPhaseGate)
    {
        NewSiegeData.CurrentPhase = BoundPhaseGate->GetPhase();
        NewSiegeData.PhaseName = GetPhaseDisplayName(NewSiegeData.CurrentPhase);
        NewSiegeData.PhaseColor = GetPhaseColor(NewSiegeData.CurrentPhase);
    }

    // Update Dominance Data
    if (BoundDominanceMeter)
    {
        NewSiegeData.DominanceValue = BoundDominanceMeter->GetDominance();
        NewSiegeData.DominancePercentage = BoundDominanceMeter->GetDominancePercentage();
    }

    // Update Ticket Data
    if (BoundTicketPool)
    {
        NewSiegeData.AttackerTickets = BoundTicketPool->GetAttackerTickets();
        NewSiegeData.DefenderTickets = BoundTicketPool->GetDefenderTickets();
        NewSiegeData.AttackerTicketPercentage = BoundTicketPool->GetAttackerTicketPercentage() * 100.0f;
        NewSiegeData.DefenderTicketPercentage = BoundTicketPool->GetDefenderTicketPercentage() * 100.0f;
    }

    CurrentSiegeData = NewSiegeData;
}

void UTerritorialControlWidget::UpdateSiegeDisplay()
{
    RefreshSiegeData();
    OnSiegeDataUpdated(CurrentSiegeData);
    OnSiegeDisplayUpdate.Broadcast(CurrentSiegeData);
}

void UTerritorialControlWidget::BindToSiegeComponents(UPhaseGateComponent* PhaseGate, UDominanceMeterComponent* DominanceMeter, UTicketPoolComponent* TicketPool)
{
    // Unbind from previous components
    if (BoundPhaseGate)
    {
        BoundPhaseGate->OnPhaseChanged.RemoveDynamic(this, &UTerritorialControlWidget::OnSiegePhaseAdvanced);
    }
    if (BoundDominanceMeter)
    {
        BoundDominanceMeter->OnDominanceChanged.RemoveDynamic(this, &UTerritorialControlWidget::OnDominanceChanged);
    }
    if (BoundTicketPool)
    {
        BoundTicketPool->OnTicketsConsumed.RemoveDynamic(this, &UTerritorialControlWidget::OnTicketsChanged);
    }

    // Bind to new components
    BoundPhaseGate = PhaseGate;
    BoundDominanceMeter = DominanceMeter;
    BoundTicketPool = TicketPool;

    if (BoundPhaseGate)
    {
        BoundPhaseGate->OnPhaseChanged.AddDynamic(this, &UTerritorialControlWidget::OnSiegePhaseAdvanced);
    }
    if (BoundDominanceMeter)
    {
        BoundDominanceMeter->OnDominanceChanged.AddDynamic(this, &UTerritorialControlWidget::OnDominanceChanged);
    }
    if (BoundTicketPool)
    {
        BoundTicketPool->OnTicketsConsumed.AddDynamic(this, &UTerritorialControlWidget::OnTicketsChanged);
    }

    // Initial data refresh
    RefreshSiegeData();
}

FString UTerritorialControlWidget::GetPhaseDisplayName(ESiegePhase Phase) const
{
    switch (Phase)
    {
    case ESiegePhase::Probe:
        return TEXT("PROBE");
    case ESiegePhase::Interdict:
        return TEXT("INTERDICT");
    case ESiegePhase::Dominate:
        return TEXT("DOMINATE");
    case ESiegePhase::Locked:
        return TEXT("LOCKED");
    default:
        return TEXT("UNKNOWN");
    }
}

FLinearColor UTerritorialControlWidget::GetPhaseColor(ESiegePhase Phase) const
{
    switch (Phase)
    {
    case ESiegePhase::Probe:
        return FLinearColor::Green;  // Starting phase - green
    case ESiegePhase::Interdict:
        return FLinearColor::Yellow; // Middle phase - yellow
    case ESiegePhase::Dominate:
        return FLinearColor(1.0f, 0.5f, 0.0f); // Final phase - orange
    case ESiegePhase::Locked:
        return FLinearColor::Red;    // Locked - red
    default:
        return FLinearColor::White;
    }
}

FString UTerritorialControlWidget::GetDominanceStatusText(float DominanceValue) const
{
    if (DominanceValue >= 0.9f)
    {
        return TEXT("ATTACKER OVERWHELMING");
    }
    else if (DominanceValue >= 0.75f)
    {
        return TEXT("ATTACKER DOMINANT");
    }
    else if (DominanceValue >= 0.6f)
    {
        return TEXT("ATTACKER ADVANTAGE");
    }
    else if (DominanceValue >= 0.4f)
    {
        return TEXT("CONTESTED");
    }
    else if (DominanceValue >= 0.25f)
    {
        return TEXT("DEFENDER ADVANTAGE");
    }
    else if (DominanceValue >= 0.1f)
    {
        return TEXT("DEFENDER DOMINANT");
    }
    else
    {
        return TEXT("DEFENDER OVERWHELMING");
    }
}

bool UTerritorialControlWidget::ShouldShowSiegeUI() const
{
    return (BoundPhaseGate != nullptr || BoundDominanceMeter != nullptr || BoundTicketPool != nullptr) &&
           CurrentSiegeData.bSiegeActive;
}