// Copyright Terminal Grounds. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGTerritorial/Public/TerritorialTypes.h"
#include "TerritorialControlWidget.generated.h"

USTRUCT(BlueprintType)
struct TGUI_API FTerritorialDisplayData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    int32 TerritoryID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    FString TerritoryName;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    int32 DominantFactionID = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    FString DominantFactionName;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    float ControlPercentage = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    bool bIsContested = false;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    FLinearColor FactionColor = FLinearColor::White;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial Display")
    TArray<int32> ContestingFactions;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTerritorialDisplayUpdate, const FTerritorialDisplayData&, TerritorialData);

/**
 * Territorial Control HUD Widget
 * Displays real-time territorial control information to players
 */
UCLASS(BlueprintType, Blueprintable)
class TGUI_API UTerritorialControlWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

protected:
    // Widget configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Widget")
    float UpdateInterval = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Widget")
    bool bShowDetailedInfo = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Widget")
    bool bShowContestationIndicators = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial Widget")
    int32 MaxTerritoriesToShow = 8;

    // Faction color mapping
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction Colors")
    TMap<int32, FLinearColor> FactionColorMap;

    // Current territorial data
    UPROPERTY(BlueprintReadOnly, Category = "Territorial Data")
    TArray<FTerritorialDisplayData> TerritorialData;

    UPROPERTY(BlueprintReadOnly, Category = "Territorial Data")
    FTerritorialDisplayData CurrentPlayerTerritory;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Territorial Events")
    FOnTerritorialDisplayUpdate OnTerritorialDisplayUpdate;

    // Update functions
    UFUNCTION(BlueprintCallable, Category = "Territorial Widget")
    void RefreshTerritorialData();

    UFUNCTION(BlueprintCallable, Category = "Territorial Widget")
    void UpdateTerritorialDisplay();

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Widget")
    void OnTerritorialDataUpdated(const TArray<FTerritorialDisplayData>& NewTerritorialData);

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Widget")
    void OnTerritoryControlChanged(const FTerritorialDisplayData& TerritoryData);

    UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Widget")
    void OnTerritoryContested(const FTerritorialDisplayData& TerritoryData);

    // Utility functions
    UFUNCTION(BlueprintPure, Category = "Territorial Widget")
    FLinearColor GetFactionColor(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Territorial Widget")
    FString GetFactionName(int32 FactionID) const;

    UFUNCTION(BlueprintPure, Category = "Territorial Widget")
    FString GetTerritoryStatusText(const FTerritorialDisplayData& TerritoryData) const;

    UFUNCTION(BlueprintPure, Category = "Territorial Widget")
    bool ShouldShowTerritoryDetails(const FTerritorialDisplayData& TerritoryData) const;

private:
    // Internal state
    float LastUpdateTime = 0.0f;
    
    // Cached references
    UPROPERTY()
    class UTerritorialManager* TerritorialManager = nullptr;

    UPROPERTY()
    class APawn* PlayerPawn = nullptr;

    // Internal data processing
    void InitializeFactionColors();
    void GetPlayerCurrentTerritory();
    FTerritorialDisplayData ConvertTerritorialState(const FTerritorialState& State);
};