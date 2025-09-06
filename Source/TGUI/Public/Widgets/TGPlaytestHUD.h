#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGPlaytestHUD.generated.h"

class ATGPlayPawn;
class ATGCaptureNode;

UCLASS()
class TGUI_API UTGPlaytestHUD : public UUserWidget
{
	GENERATED_BODY()

public:
	UTGPlaytestHUD(const FObjectInitializer& ObjectInitializer);

protected:
	virtual void NativeConstruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	// Player reference
	UPROPERTY(BlueprintReadOnly, Category = "Player")
	ATGPlayPawn* PlayerPawn;

	// HUD Data
	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	float Health = 100.0f;

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	float MaxHealth = 100.0f;

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	float Ammo = 30.0f;

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	float MaxAmmo = 30.0f;

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	int32 NodesOwned = 0;

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	int32 TotalNodes = 3;

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	FString NodeStatusA = TEXT("Neutral");

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	FString NodeStatusB = TEXT("Neutral");

	UPROPERTY(BlueprintReadOnly, Category = "HUD")
	FString NodeStatusC = TEXT("Neutral");

public:
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdatePlayerStats();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateNodeStatus();

	UFUNCTION(BlueprintPure, Category = "HUD")
	float GetHealthPercentage() const { return MaxHealth > 0 ? Health / MaxHealth : 0.0f; }

	UFUNCTION(BlueprintPure, Category = "HUD")
	float GetAmmoPercentage() const { return MaxAmmo > 0 ? Ammo / MaxAmmo : 0.0f; }

	UFUNCTION(BlueprintPure, Category = "HUD")
	FString GetHealthText() const { return FString::Printf(TEXT("%.0f/%.0f"), Health, MaxHealth); }

	UFUNCTION(BlueprintPure, Category = "HUD")
	FString GetAmmoText() const { return FString::Printf(TEXT("%.0f/%.0f"), Ammo, MaxAmmo); }

	UFUNCTION(BlueprintPure, Category = "HUD")
	FString GetNodeProgressText() const { return FString::Printf(TEXT("%d/%d"), NodesOwned, TotalNodes); }

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
	void OnHealthUpdated();

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
	void OnAmmoUpdated();

	UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
	void OnNodeStatusUpdated();

private:
	void FindPlayerPawn();
	void FindCaptureNodes();

	UPROPERTY()
	TArray<ATGCaptureNode*> CaptureNodes;
};