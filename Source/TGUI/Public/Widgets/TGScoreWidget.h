#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Engine/TimerHandle.h"
#include "TGScoreWidget.generated.h"

USTRUCT(BlueprintType)
struct FMatchStats
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Stats")
	float MatchTime = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Stats")
	int32 NodesCapured = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Stats")
	int32 EnemiesKilled = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Stats")
	int32 Deaths = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Stats")
	bool bExtractionSuccessful = false;

	UPROPERTY(BlueprintReadWrite, Category = "Stats")
	float ExtractionTime = 0.0f;

	FMatchStats()
	{
		MatchTime = 0.0f;
		NodesCapured = 0;
		EnemiesKilled = 0;
		Deaths = 0;
		bExtractionSuccessful = false;
		ExtractionTime = 0.0f;
	}
};

UCLASS()
class TGUI_API UTGScoreWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UTGScoreWidget(const FObjectInitializer& ObjectInitializer);

protected:
	virtual void NativeConstruct() override;

	// Match Statistics
	UPROPERTY(BlueprintReadOnly, Category = "Score")
	FMatchStats CurrentStats;

	UPROPERTY(BlueprintReadOnly, Category = "Score")
	bool bMatchActive = true;

	UPROPERTY(BlueprintReadOnly, Category = "Score")
	bool bShowingResults = false;

	// Timer
	FTimerHandle MatchTimerHandle;

public:
	// Match Control
	UFUNCTION(BlueprintCallable, Category = "Score")
	void StartMatch();

	UFUNCTION(BlueprintCallable, Category = "Score")
	void EndMatch(bool bExtractionSuccess = false);

	UFUNCTION(BlueprintCallable, Category = "Score")
	void ShowResults();

	UFUNCTION(BlueprintCallable, Category = "Score")
	void HideResults();

	// Stat Updates
	UFUNCTION(BlueprintCallable, Category = "Score")
	void IncrementNodesCaptured() { CurrentStats.NodesCapured++; }

	UFUNCTION(BlueprintCallable, Category = "Score")
	void IncrementEnemiesKilled() { CurrentStats.EnemiesKilled++; }

	UFUNCTION(BlueprintCallable, Category = "Score")
	void IncrementDeaths() { CurrentStats.Deaths++; }

	// Getters
	UFUNCTION(BlueprintPure, Category = "Score")
	FString GetMatchTimeText() const;

	UFUNCTION(BlueprintPure, Category = "Score")
	FString GetExtractionTimeText() const;

	UFUNCTION(BlueprintPure, Category = "Score")
	FString GetKDRatioText() const;

	UFUNCTION(BlueprintPure, Category = "Score")
	FString GetResultText() const;

	UFUNCTION(BlueprintPure, Category = "Score")
	FMatchStats GetMatchStats() const { return CurrentStats; }

	UFUNCTION(BlueprintPure, Category = "Score")
	bool IsMatchActive() const { return bMatchActive; }

	UFUNCTION(BlueprintPure, Category = "Score")
	bool IsShowingResults() const { return bShowingResults; }

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "Score")
	void OnMatchStarted();

	UFUNCTION(BlueprintImplementableEvent, Category = "Score")
	void OnMatchEnded(bool bSuccess);

	UFUNCTION(BlueprintImplementableEvent, Category = "Score")
	void OnStatsUpdated();

private:
	UFUNCTION()
	void UpdateMatchTime();

	float MatchStartTime = 0.0f;
};