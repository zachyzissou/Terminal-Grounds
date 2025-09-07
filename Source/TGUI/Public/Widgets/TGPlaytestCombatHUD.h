#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGPlaytestGameMode.h"
#include "TGPlaytestCombatHUD.generated.h"

class ATGPlayPawn;
class ATGPlaytestGameMode;

UCLASS()
class TGUI_API UTGPlaytestCombatHUD : public UUserWidget
{
	GENERATED_BODY()

public:
	UTGPlaytestCombatHUD(const FObjectInitializer& ObjectInitializer);

protected:
	virtual void NativeConstruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	// Player reference
	UPROPERTY(BlueprintReadOnly, Category = "Player")
	TObjectPtr<ATGPlayPawn> PlayerPawn;

	// Game Mode reference
	UPROPERTY(BlueprintReadOnly, Category = "Game")
	TObjectPtr<ATGPlaytestGameMode> PlaytestGameMode;

	// Player Stats
	UPROPERTY(BlueprintReadOnly, Category = "Player Stats")
	float Health = 100.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Player Stats")
	float MaxHealth = 100.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Player Stats")
	float Ammo = 30.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Player Stats")
	float MaxAmmo = 30.0f;

	// Mission Stats
	UPROPERTY(BlueprintReadOnly, Category = "Mission")
	int32 RemainingEnemies = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Mission")
	int32 TotalEnemies = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Mission")
	EPlaytestMissionState MissionState = EPlaytestMissionState::Setup;

	UPROPERTY(BlueprintReadOnly, Category = "Mission")
	bool bCanExtract = false;

	UPROPERTY(BlueprintReadOnly, Category = "Mission")
	FString MissionObjective = TEXT("Eliminate all enemies, then reach extraction");

public:
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdatePlayerStats();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateMissionStats();

	// Data Getters
	UFUNCTION(BlueprintPure, Category = "Player Stats")
	float GetHealthPercentage() const { return MaxHealth > 0 ? Health / MaxHealth : 0.0f; }

	UFUNCTION(BlueprintPure, Category = "Player Stats")
	float GetAmmoPercentage() const { return MaxAmmo > 0 ? Ammo / MaxAmmo : 0.0f; }

	UFUNCTION(BlueprintPure, Category = "Player Stats")
	FString GetHealthText() const { return FString::Printf(TEXT("%.0f/%.0f"), Health, MaxHealth); }

	UFUNCTION(BlueprintPure, Category = "Player Stats")
	FString GetAmmoText() const { return FString::Printf(TEXT("%.0f/%.0f"), Ammo, MaxAmmo); }

	// Mission Status
	UFUNCTION(BlueprintPure, Category = "Mission")
	FString GetEnemyCountText() const { return FString::Printf(TEXT("%d Enemies Remaining"), RemainingEnemies); }

	UFUNCTION(BlueprintPure, Category = "Mission")
	FString GetMissionStateText() const;

	UFUNCTION(BlueprintPure, Category = "Mission")
	FLinearColor GetMissionStateColor() const;

	UFUNCTION(BlueprintPure, Category = "Mission")
	FString GetObjectiveText() const;

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "HUD Events")
	void OnHealthUpdated();

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD Events")
	void OnAmmoUpdated();

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD Events")
	void OnMissionStateUpdated(EPlaytestMissionState NewState);

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD Events")
	void OnEnemyCountUpdated(int32 NewRemainingEnemies, int32 NewTotalEnemies);

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD Events")
	void OnMissionComplete();

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD Events")
	void OnMissionFailed();

private:
	void FindPlayerPawn();
	void FindPlaytestGameMode();
	void BindToGameModeEvents();

	// Event handlers
	UFUNCTION()
	void HandleMissionStateChanged(EPlaytestMissionState NewState);

	UFUNCTION()
	void HandleEnemyCountChanged(int32 NewRemainingEnemies, int32 NewTotalEnemies);

	UFUNCTION()
	void HandleMissionComplete();

	UFUNCTION()
	void HandleMissionFailed();

	// Cached values for change detection
	float LastHealth = -1.0f;
	float LastMaxHealth = -1.0f;
	float LastAmmo = -1.0f;
	float LastMaxAmmo = -1.0f;
	int32 LastRemainingEnemies = -1;
	int32 LastTotalEnemies = -1;
	EPlaytestMissionState LastMissionState = EPlaytestMissionState::Setup;

	bool bEventsbound = false;
};