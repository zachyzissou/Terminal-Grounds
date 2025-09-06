#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/TextBlock.h"
#include "Components/ProgressBar.h"
#include "Components/VerticalBox.h"
#include "Components/HorizontalBox.h"
#include "TGCore/Public/TGEconomicVictorySubsystem.h"
#include "TGEconomicVictoryWidget.generated.h"

UCLASS(BlueprintType, Blueprintable)
class TGUI_API UTGEconomicVictoryWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UTGEconomicVictoryWidget(const FObjectInitializer& ObjectInitializer);

    // Initialize the widget with faction data
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void InitializeWidget(int32 InFactionID);

    // Update display with current victory progress
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void UpdateVictoryProgress();

    // Show/hide specific victory conditions
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void SetVictoryTypeVisible(EEconomicVictoryType VictoryType, bool bVisible);

    // Highlight victory conditions that are close to completion
    UFUNCTION(BlueprintCallable, Category = "Economic Victory")
    void HighlightThreateningVictories();

    // Get localized victory type name
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FText GetVictoryTypeName(EEconomicVictoryType VictoryType) const;

    // Get localized victory description
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FText GetVictoryDescription(EEconomicVictoryType VictoryType) const;

    // Get progress color based on status
    UFUNCTION(BlueprintPure, Category = "Economic Victory")
    FLinearColor GetProgressColor(EEconomicVictoryStatus Status) const;

    // Blueprint events for UI binding
    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnVictoryProgressUpdated(int32 FactionID, EEconomicVictoryType VictoryType, float Progress);

    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnVictoryAchieved(int32 FactionID, EEconomicVictoryType VictoryType);

    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnVictoryThreatened(int32 ThreateningFactionID, EEconomicVictoryType VictoryType, float TimeToVictory);

    UFUNCTION(BlueprintImplementableEvent, Category = "Economic Victory Events")
    void OnEconomicMetricsChanged(int32 FactionID, const FEconomicMetrics& NewMetrics);

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display Options")
    bool bShowAllFactions = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display Options")
    bool bShowCompletedConditions = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display Options")
    bool bShowCounterStrategies = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display Options")
    float UpdateInterval = 2.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display Options")
    int32 MaxVisibleConditions = 6;

protected:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

    // Bind to economic victory subsystem events
    UFUNCTION()
    void OnEconomicVictoryProgressDelegate(int32 FactionID, EEconomicVictoryType VictoryType, float Progress);

    UFUNCTION()
    void OnEconomicVictoryAchievedDelegate(int32 FactionID, EEconomicVictoryType VictoryType, float CompletionTime);

    UFUNCTION()
    void OnEconomicVictoryThreatenedDelegate(int32 ThreateningFactionID, EEconomicVictoryType VictoryType, float TimeToVictory);

    UFUNCTION()
    void OnEconomicMetricsUpdatedDelegate(int32 FactionID, const FEconomicMetrics& NewMetrics);

private:
    // Widget state
    UPROPERTY()
    int32 CurrentFactionID = 0;

    UPROPERTY()
    UTGEconomicVictorySubsystem* EconomicVictorySubsystem;

    // Update tracking
    float LastUpdateTime = 0.0f;
    
    // UI Creation helpers
    void CreateVictoryConditionDisplay(const FEconomicVictoryCondition& Condition, const FEconomicVictoryProgress& Progress);
    void UpdateVictoryConditionDisplay(EEconomicVictoryType VictoryType, const FEconomicVictoryProgress& Progress);
    void CreateEconomicMetricsDisplay(const FEconomicMetrics& Metrics);
    void UpdateEconomicMetricsDisplay(const FEconomicMetrics& Metrics);
    
    // UI state management
    void RefreshAllDisplays();
    void ClearDisplays();
    
    // Victory condition widgets (dynamically created)
    UPROPERTY()
    TMap<EEconomicVictoryType, UWidget*> VictoryConditionWidgets;
    
    // Main container references (bind these in Blueprint)
    UPROPERTY(meta = (BindWidget))
    UVerticalBox* VictoryConditionsContainer;
    
    UPROPERTY(meta = (BindWidget))
    UVerticalBox* EconomicMetricsContainer;
    
    UPROPERTY(meta = (BindWidget))
    UTextBlock* FactionNameText;
    
    UPROPERTY(meta = (BindWidget))
    UTextBlock* CurrentStatusText;
};