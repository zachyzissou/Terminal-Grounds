#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGPlaytestMenu.generated.h"

class ATGPlayPawn;
class ATGExtractionPad;
class UTGScoreWidget;

UCLASS()
class TGUI_API UTGPlaytestMenu : public UUserWidget
{
	GENERATED_BODY()

public:
	UTGPlaytestMenu(const FObjectInitializer& ObjectInitializer);

protected:
	virtual void NativeConstruct() override;

	// References
	UPROPERTY(BlueprintReadOnly, Category = "Playtest")
	ATGPlayPawn* PlayerPawn;

	UPROPERTY(BlueprintReadOnly, Category = "Playtest")
	ATGExtractionPad* ExtractionPad;

	UPROPERTY(BlueprintReadOnly, Category = "Playtest")
	UTGScoreWidget* ScoreWidget;

	// Menu State
	UPROPERTY(BlueprintReadOnly, Category = "Playtest")
	bool bIsMenuVisible = false;

	UPROPERTY(BlueprintReadOnly, Category = "Playtest")
	bool bGodModeEnabled = false;

public:
	// Menu Control
	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void ToggleMenu();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void ShowMenu();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void HideMenu();

	// Playtest Functions
	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void RestartMatch();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void TeleportToExtractPad();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void ToggleGodMode();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void FastCaptureAllNodes();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void SpawnTestEnemies();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void KillAllEnemies();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void AddAmmo();

	UFUNCTION(BlueprintCallable, Category = "Playtest")
	void RestoreHealth();

	// Getters
	UFUNCTION(BlueprintPure, Category = "Playtest")
	bool IsMenuVisible() const { return bIsMenuVisible; }

	UFUNCTION(BlueprintPure, Category = "Playtest")
	bool IsGodModeEnabled() const { return bGodModeEnabled; }

	UFUNCTION(BlueprintPure, Category = "Playtest")
	FString GetGodModeButtonText() const;

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "Playtest")
	void OnMenuToggled(bool bVisible);

	UFUNCTION(BlueprintImplementableEvent, Category = "Playtest")
	void OnGodModeToggled(bool bEnabled);

	UFUNCTION(BlueprintImplementableEvent, Category = "Playtest")
	void OnMatchRestarted();

private:
	void FindReferences();
};