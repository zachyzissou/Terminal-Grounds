#include "Widgets/TGEconomicVictoryWidget.h"
#include "TGCore/Public/TGEconomicVictorySubsystem.h"
#include "Components/TextBlock.h"
#include "Components/ProgressBar.h"
#include "Components/VerticalBox.h"
#include "Components/HorizontalBox.h"
#include "Components/Border.h"
#include "Engine/World.h"
#include "TimerManager.h"

UTGEconomicVictoryWidget::UTGEconomicVictoryWidget(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    CurrentFactionID = 0;
    EconomicVictorySubsystem = nullptr;
    LastUpdateTime = 0.0f;
}

void UTGEconomicVictoryWidget::NativeConstruct()
{
    Super::NativeConstruct();
    
    // Get economic victory subsystem
    if (UWorld* World = GetWorld())
    {
        EconomicVictorySubsystem = World->GetSubsystem<UTGEconomicVictorySubsystem>();
        
        if (EconomicVictorySubsystem)
        {
            // Bind to events
            EconomicVictorySubsystem->OnEconomicVictoryProgress.AddDynamic(this, &UTGEconomicVictoryWidget::OnEconomicVictoryProgressDelegate);
            EconomicVictorySubsystem->OnEconomicVictoryAchieved.AddDynamic(this, &UTGEconomicVictoryWidget::OnEconomicVictoryAchievedDelegate);
            EconomicVictorySubsystem->OnEconomicVictoryThreatened.AddDynamic(this, &UTGEconomicVictoryWidget::OnEconomicVictoryThreatenedDelegate);
            EconomicVictorySubsystem->OnEconomicMetricsUpdated.AddDynamic(this, &UTGEconomicVictoryWidget::OnEconomicMetricsUpdatedDelegate);
        }
    }
}

void UTGEconomicVictoryWidget::NativeDestruct()
{
    // Unbind from events
    if (EconomicVictorySubsystem)
    {
        EconomicVictorySubsystem->OnEconomicVictoryProgress.RemoveDynamic(this, &UTGEconomicVictoryWidget::OnEconomicVictoryProgressDelegate);
        EconomicVictorySubsystem->OnEconomicVictoryAchieved.RemoveDynamic(this, &UTGEconomicVictoryWidget::OnEconomicVictoryAchievedDelegate);
        EconomicVictorySubsystem->OnEconomicVictoryThreatened.RemoveDynamic(this, &UTGEconomicVictoryWidget::OnEconomicVictoryThreatenedDelegate);
        EconomicVictorySubsystem->OnEconomicMetricsUpdated.RemoveDynamic(this, &UTGEconomicVictoryWidget::OnEconomicMetricsUpdatedDelegate);
    }
    
    Super::NativeDestruct();
}

void UTGEconomicVictoryWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    
    // Update display at regular intervals
    float CurrentTime = GetWorld()->GetTimeSeconds();
    if (CurrentTime - LastUpdateTime >= UpdateInterval)
    {
        UpdateVictoryProgress();
        LastUpdateTime = CurrentTime;
    }
}

void UTGEconomicVictoryWidget::InitializeWidget(int32 InFactionID)
{
    CurrentFactionID = InFactionID;
    
    // Update faction name display
    if (FactionNameText)
    {
        FText FactionName = FText::FromString(FString::Printf(TEXT("Faction %d"), CurrentFactionID));
        FactionNameText->SetText(FactionName);
    }
    
    // Initial update
    UpdateVictoryProgress();
}

void UTGEconomicVictoryWidget::UpdateVictoryProgress()
{
    if (!EconomicVictorySubsystem)
    {
        return;
    }
    
    // Clear existing displays
    ClearDisplays();
    
    // Get active victory conditions
    TArray<FEconomicVictoryCondition> ActiveConditions = EconomicVictorySubsystem->GetActiveVictoryConditions();
    
    // Display victory conditions for current faction (or all factions if enabled)
    TArray<int32> FactionsToShow;
    if (bShowAllFactions)
    {
        FactionsToShow = {0, 1, 2, 3, 4, 5, 6}; // All factions
    }
    else
    {
        FactionsToShow.Add(CurrentFactionID);
    }
    
    for (int32 FactionID : FactionsToShow)
    {
        for (const FEconomicVictoryCondition& Condition : ActiveConditions)
        {
            FEconomicVictoryProgress Progress = EconomicVictorySubsystem->GetFactionVictoryProgress(FactionID, Condition.VictoryType);
            
            // Skip completed conditions if not showing them
            if (!bShowCompletedConditions && Progress.Status == EEconomicVictoryStatus::Completed)
            {
                continue;
            }
            
            CreateVictoryConditionDisplay(Condition, Progress);
        }
        
        // Update economic metrics
        FEconomicMetrics Metrics = EconomicVictorySubsystem->GetFactionEconomicMetrics(FactionID);
        CreateEconomicMetricsDisplay(Metrics);
    }
    
    // Update status text
    UpdateStatusText();
}

void UTGEconomicVictoryWidget::SetVictoryTypeVisible(EEconomicVictoryType VictoryType, bool bVisible)
{
    if (UWidget** FoundWidget = VictoryConditionWidgets.Find(VictoryType))
    {
        if (*FoundWidget)
        {
            (*FoundWidget)->SetVisibility(bVisible ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
        }
    }
}

void UTGEconomicVictoryWidget::HighlightThreateningVictories()
{
    if (!EconomicVictorySubsystem)
    {
        return;
    }
    
    // Get all victory progress
    TArray<FEconomicVictoryProgress> AllProgress = EconomicVictorySubsystem->GetAllVictoryProgress();
    
    for (const FEconomicVictoryProgress& Progress : AllProgress)
    {
        if (Progress.Progress >= EconomicVictorySubsystem->ThreatWarningThreshold)
        {
            // Highlight this victory condition
            if (UWidget** FoundWidget = VictoryConditionWidgets.Find(Progress.VictoryType))
            {
                if (*FoundWidget)
                {
                    // Add highlight styling (this would be implemented in Blueprint)
                    // For now, just ensure it's visible
                    (*FoundWidget)->SetVisibility(ESlateVisibility::Visible);
                }
            }
        }
    }
}

FText UTGEconomicVictoryWidget::GetVictoryTypeName(EEconomicVictoryType VictoryType) const
{
    switch (VictoryType)
    {
        case EEconomicVictoryType::EconomicDominance:
            return FText::FromString(TEXT("Economic Dominance"));
        case EEconomicVictoryType::SupplyMonopoly:
            return FText::FromString(TEXT("Supply Monopoly"));
        case EEconomicVictoryType::EconomicCollapse:
            return FText::FromString(TEXT("Economic Collapse"));
        case EEconomicVictoryType::TradeNetwork:
            return FText::FromString(TEXT("Trade Network"));
        case EEconomicVictoryType::ResourceControl:
            return FText::FromString(TEXT("Resource Control"));
        case EEconomicVictoryType::ConvoySupremacy:
            return FText::FromString(TEXT("Convoy Supremacy"));
        default:
            return FText::FromString(TEXT("Unknown Victory"));
    }
}

FText UTGEconomicVictoryWidget::GetVictoryDescription(EEconomicVictoryType VictoryType) const
{
    switch (VictoryType)
    {
        case EEconomicVictoryType::EconomicDominance:
            return FText::FromString(TEXT("Control majority of convoy route economic value"));
        case EEconomicVictoryType::SupplyMonopoly:
            return FText::FromString(TEXT("Control all routes of a specific resource type"));
        case EEconomicVictoryType::EconomicCollapse:
            return FText::FromString(TEXT("Reduce enemy faction economic output significantly"));
        case EEconomicVictoryType::TradeNetwork:
            return FText::FromString(TEXT("Establish profitable routes across multiple territories"));
        case EEconomicVictoryType::ResourceControl:
            return FText::FromString(TEXT("Dominate control of specific resource types"));
        case EEconomicVictoryType::ConvoySupremacy:
            return FText::FromString(TEXT("Achieve superiority in convoy operations"));
        default:
            return FText::FromString(TEXT("Unknown victory condition"));
    }
}

FLinearColor UTGEconomicVictoryWidget::GetProgressColor(EEconomicVictoryStatus Status) const
{
    switch (Status)
    {
        case EEconomicVictoryStatus::NotStarted:
            return FLinearColor::Gray;
        case EEconomicVictoryStatus::InProgress:
            return FLinearColor::Yellow;
        case EEconomicVictoryStatus::NearComplete:
            return FLinearColor::Red;
        case EEconomicVictoryStatus::Completed:
            return FLinearColor::Green;
        case EEconomicVictoryStatus::Failed:
            return FLinearColor::Black;
        default:
            return FLinearColor::White;
    }
}

void UTGEconomicVictoryWidget::OnEconomicVictoryProgressDelegate(int32 FactionID, EEconomicVictoryType VictoryType, float Progress)
{
    // Update the specific victory condition display
    UpdateVictoryConditionDisplay(VictoryType, EconomicVictorySubsystem->GetFactionVictoryProgress(FactionID, VictoryType));
    
    // Call Blueprint event
    OnVictoryProgressUpdated(FactionID, VictoryType, Progress);
}

void UTGEconomicVictoryWidget::OnEconomicVictoryAchievedDelegate(int32 FactionID, EEconomicVictoryType VictoryType, float CompletionTime)
{
    // Update status text
    if (CurrentStatusText)
    {
        FText StatusText = FText::FromString(FString::Printf(TEXT("VICTORY ACHIEVED: %s by Faction %d!"), 
                                                             *GetVictoryTypeName(VictoryType).ToString(), 
                                                             FactionID));
        CurrentStatusText->SetText(StatusText);
        CurrentStatusText->SetColorAndOpacity(FLinearColor::Green);
    }
    
    // Call Blueprint event
    OnVictoryAchieved(FactionID, VictoryType);
}

void UTGEconomicVictoryWidget::OnEconomicVictoryThreatenedDelegate(int32 ThreateningFactionID, EEconomicVictoryType VictoryType, float TimeToVictory)
{
    // Update status text with warning
    if (CurrentStatusText)
    {
        FText StatusText = FText::FromString(FString::Printf(TEXT("WARNING: Faction %d approaching %s victory! Time: %.1fs"), 
                                                             ThreateningFactionID, 
                                                             *GetVictoryTypeName(VictoryType).ToString(), 
                                                             TimeToVictory));
        CurrentStatusText->SetText(StatusText);
        CurrentStatusText->SetColorAndOpacity(FLinearColor::Red);
    }
    
    // Highlight the threatening victory
    HighlightThreateningVictories();
    
    // Call Blueprint event
    OnVictoryThreatened(ThreateningFactionID, VictoryType, TimeToVictory);
}

void UTGEconomicVictoryWidget::OnEconomicMetricsUpdatedDelegate(int32 FactionID, const FEconomicMetrics& NewMetrics)
{
    // Update economic metrics display
    UpdateEconomicMetricsDisplay(NewMetrics);
    
    // Call Blueprint event
    OnEconomicMetricsChanged(FactionID, NewMetrics);
}

void UTGEconomicVictoryWidget::CreateVictoryConditionDisplay(const FEconomicVictoryCondition& Condition, const FEconomicVictoryProgress& Progress)
{
    if (!VictoryConditionsContainer)
    {
        return;
    }
    
    // Create horizontal box for this victory condition
    UHorizontalBox* ConditionBox = NewObject<UHorizontalBox>(this);
    VictoryConditionsContainer->AddChild(ConditionBox);
    
    // Victory type name
    UTextBlock* NameText = NewObject<UTextBlock>(this);
    NameText->SetText(GetVictoryTypeName(Condition.VictoryType));
    ConditionBox->AddChild(NameText);
    
    // Progress bar
    UProgressBar* ProgressBarWidget = NewObject<UProgressBar>(this);
    ProgressBarWidget->SetPercent(Progress.Progress);
    ProgressBarWidget->SetFillColorAndOpacity(GetProgressColor(Progress.Status));
    ConditionBox->AddChild(ProgressBarWidget);
    
    // Progress text
    UTextBlock* ProgressText = NewObject<UTextBlock>(this);
    FText ProgressTextContent = FText::FromString(FString::Printf(TEXT("%.1f%%"), Progress.Progress * 100.0f));
    ProgressText->SetText(ProgressTextContent);
    ConditionBox->AddChild(ProgressText);
    
    // Store widget reference
    VictoryConditionWidgets.Add(Condition.VictoryType, ConditionBox);
}

void UTGEconomicVictoryWidget::UpdateVictoryConditionDisplay(EEconomicVictoryType VictoryType, const FEconomicVictoryProgress& Progress)
{
    if (UWidget** FoundWidget = VictoryConditionWidgets.Find(VictoryType))
    {
        // Update existing widget - this would need more detailed implementation
        // For now, just refresh the entire display
        UpdateVictoryProgress();
    }
}

void UTGEconomicVictoryWidget::CreateEconomicMetricsDisplay(const FEconomicMetrics& Metrics)
{
    if (!EconomicMetricsContainer)
    {
        return;
    }
    
    // Clear existing metrics
    EconomicMetricsContainer->ClearChildren();
    
    // Route control
    UHorizontalBox* RouteBox = NewObject<UHorizontalBox>(this);
    EconomicMetricsContainer->AddChild(RouteBox);
    
    UTextBlock* RouteLabel = NewObject<UTextBlock>(this);
    RouteLabel->SetText(FText::FromString(TEXT("Route Control: ")));
    RouteBox->AddChild(RouteLabel);
    
    UTextBlock* RouteValue = NewObject<UTextBlock>(this);
    FText RouteText = FText::FromString(FString::Printf(TEXT("%.1f%% (%d/%d)"), 
                                                        Metrics.RouteControlPercentage * 100.0f,
                                                        Metrics.ControlledRoutes,
                                                        Metrics.TotalRoutes));
    RouteValue->SetText(RouteText);
    RouteBox->AddChild(RouteValue);
    
    // Network connectivity
    UHorizontalBox* NetworkBox = NewObject<UHorizontalBox>(this);
    EconomicMetricsContainer->AddChild(NetworkBox);
    
    UTextBlock* NetworkLabel = NewObject<UTextBlock>(this);
    NetworkLabel->SetText(FText::FromString(TEXT("Network Connectivity: ")));
    NetworkBox->AddChild(NetworkLabel);
    
    UTextBlock* NetworkValue = NewObject<UTextBlock>(this);
    FText NetworkText = FText::FromString(FString::Printf(TEXT("%.1f%%"), Metrics.NetworkConnectivity * 100.0f));
    NetworkValue->SetText(NetworkText);
    NetworkBox->AddChild(NetworkValue);
}

void UTGEconomicVictoryWidget::UpdateEconomicMetricsDisplay(const FEconomicMetrics& Metrics)
{
    // For now, just recreate the entire display
    CreateEconomicMetricsDisplay(Metrics);
}

void UTGEconomicVictoryWidget::RefreshAllDisplays()
{
    UpdateVictoryProgress();
}

void UTGEconomicVictoryWidget::ClearDisplays()
{
    if (VictoryConditionsContainer)
    {
        VictoryConditionsContainer->ClearChildren();
    }
    
    if (EconomicMetricsContainer)
    {
        EconomicMetricsContainer->ClearChildren();
    }
    
    VictoryConditionWidgets.Empty();
}

void UTGEconomicVictoryWidget::UpdateStatusText()
{
    if (!CurrentStatusText || !EconomicVictorySubsystem)
    {
        return;
    }
    
    // Get the closest victory to completion
    FEconomicVictoryProgress ClosestVictory = EconomicVictorySubsystem->GetClosestVictoryToCompletion();
    
    if (ClosestVictory.Progress > 0.0f)
    {
        FText StatusText = FText::FromString(FString::Printf(TEXT("Closest Victory: %s by Faction %d (%.1f%%)"),
                                                             *GetVictoryTypeName(ClosestVictory.VictoryType).ToString(),
                                                             ClosestVictory.FactionID,
                                                             ClosestVictory.Progress * 100.0f));
        CurrentStatusText->SetText(StatusText);
        CurrentStatusText->SetColorAndOpacity(GetProgressColor(ClosestVictory.Status));
    }
    else
    {
        CurrentStatusText->SetText(FText::FromString(TEXT("No active victory progress")));
        CurrentStatusText->SetColorAndOpacity(FLinearColor::White);
    }
}