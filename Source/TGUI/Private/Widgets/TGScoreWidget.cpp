#include "Widgets/TGScoreWidget.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "TimerManager.h"

UTGScoreWidget::UTGScoreWidget(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	// Initialize default values
	CurrentStats = FMatchStats();
	bMatchActive = false;
	bShowingResults = false;
}

void UTGScoreWidget::NativeConstruct()
{
	Super::NativeConstruct();

	// Auto-start match when widget is constructed
	StartMatch();
}

void UTGScoreWidget::StartMatch()
{
	// Reset stats
	CurrentStats = FMatchStats();
	bMatchActive = true;
	bShowingResults = false;
	MatchStartTime = GetWorld()->GetTimeSeconds();

	// Start match timer
	GetWorld()->GetTimerManager().SetTimer(MatchTimerHandle, this, &UTGScoreWidget::UpdateMatchTime, 0.1f, true);

	OnMatchStarted();

	UE_LOG(LogTemp, Log, TEXT("Match started"));
}

void UTGScoreWidget::EndMatch(bool bExtractionSuccess)
{
	if (!bMatchActive)
	{
		return;
	}

	bMatchActive = false;
	CurrentStats.bExtractionSuccessful = bExtractionSuccess;
	CurrentStats.ExtractionTime = GetWorld()->GetTimeSeconds() - MatchStartTime;

	// Stop match timer
	GetWorld()->GetTimerManager().ClearTimer(MatchTimerHandle);

	OnMatchEnded(bExtractionSuccess);

	UE_LOG(LogTemp, Log, TEXT("Match ended - Success: %s, Time: %.1f seconds"), 
		bExtractionSuccess ? TEXT("Yes") : TEXT("No"), CurrentStats.ExtractionTime);

	// Show results after a brief delay
	FTimerHandle DelayHandle;
	GetWorld()->GetTimerManager().SetTimer(DelayHandle, this, &UTGScoreWidget::ShowResults, 1.0f, false);
}

void UTGScoreWidget::ShowResults()
{
	bShowingResults = true;
	UE_LOG(LogTemp, Log, TEXT("Showing match results"));
}

void UTGScoreWidget::HideResults()
{
	bShowingResults = false;
	UE_LOG(LogTemp, Log, TEXT("Hiding match results"));
}

FString UTGScoreWidget::GetMatchTimeText() const
{
	float TimeToDisplay = bMatchActive ? CurrentStats.MatchTime : CurrentStats.ExtractionTime;
	
	int32 Minutes = FMath::FloorToInt(TimeToDisplay / 60.0f);
	int32 Seconds = FMath::FloorToInt(TimeToDisplay) % 60;
	int32 Milliseconds = FMath::FloorToInt((TimeToDisplay - FMath::FloorToInt(TimeToDisplay)) * 100);
	
	return FString::Printf(TEXT("%02d:%02d:%02d"), Minutes, Seconds, Milliseconds);
}

FString UTGScoreWidget::GetExtractionTimeText() const
{
	if (!CurrentStats.bExtractionSuccessful)
	{
		return TEXT("Failed");
	}

	int32 Minutes = FMath::FloorToInt(CurrentStats.ExtractionTime / 60.0f);
	int32 Seconds = FMath::FloorToInt(CurrentStats.ExtractionTime) % 60;
	
	return FString::Printf(TEXT("%02d:%02d"), Minutes, Seconds);
}

FString UTGScoreWidget::GetKDRatioText() const
{
	if (CurrentStats.Deaths == 0)
	{
		return CurrentStats.EnemiesKilled > 0 ? FString::Printf(TEXT("%.1f"), (float)CurrentStats.EnemiesKilled) : TEXT("0.0");
	}
	
	float Ratio = (float)CurrentStats.EnemiesKilled / (float)CurrentStats.Deaths;
	return FString::Printf(TEXT("%.1f"), Ratio);
}

FString UTGScoreWidget::GetResultText() const
{
	if (!bShowingResults)
	{
		return TEXT("");
	}

	if (CurrentStats.bExtractionSuccessful)
	{
		return TEXT("MISSION SUCCESS");
	}
	else
	{
		return TEXT("MISSION FAILED");
	}
}

void UTGScoreWidget::UpdateMatchTime()
{
	if (bMatchActive)
	{
		CurrentStats.MatchTime = GetWorld()->GetTimeSeconds() - MatchStartTime;
		OnStatsUpdated();
	}
}