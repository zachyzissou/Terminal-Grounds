#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/TimerHandle.h"
#include "TGSmokeTestRunner.generated.h"

class ATGPlayPawn;
class ATGCaptureNode;
class ATGExtractionPad;

USTRUCT(BlueprintType)
struct FSmokeTestResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	FString TestName = TEXT("");

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	bool bPassed = false;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	float ExecutionTime = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	FString ErrorMessage = TEXT("");

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	FDateTime Timestamp;

	FSmokeTestResult()
	{
		TestName = TEXT("");
		bPassed = false;
		ExecutionTime = 0.0f;
		ErrorMessage = TEXT("");
		Timestamp = FDateTime::Now();
	}
};

USTRUCT(BlueprintType)
struct FSmokeTestSuite
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	TArray<FSmokeTestResult> TestResults;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	int32 PassedTests = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	int32 FailedTests = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	float TotalExecutionTime = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	bool bAllTestsPassed = false;

	FSmokeTestSuite()
	{
		TestResults.Empty();
		PassedTests = 0;
		FailedTests = 0;
		TotalExecutionTime = 0.0f;
		bAllTestsPassed = false;
	}
};

UENUM(BlueprintType)
enum class ESmokeTestState : uint8
{
	Idle			UMETA(DisplayName = "Idle"),
	Running			UMETA(DisplayName = "Running"),
	WaitingForUser	UMETA(DisplayName = "Waiting For User"),
	Completed		UMETA(DisplayName = "Completed"),
	Failed			UMETA(DisplayName = "Failed")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnSmokeTestCompleted, FSmokeTestSuite, Results, bool, bAllPassed);

UCLASS()
class TGCORE_API ATGSmokeTestRunner : public AActor
{
	GENERATED_BODY()
	
public:	
	ATGSmokeTestRunner();

protected:
	virtual void BeginPlay() override;

	// Test State
	UPROPERTY(BlueprintReadOnly, Category = "Test")
	ESmokeTestState CurrentState = ESmokeTestState::Idle;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	FSmokeTestSuite TestSuite;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	int32 CurrentTestIndex = 0;

	// Test References
	UPROPERTY(BlueprintReadOnly, Category = "Test")
	ATGPlayPawn* TestPlayerPawn;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	TArray<ATGCaptureNode*> TestCaptureNodes;

	UPROPERTY(BlueprintReadOnly, Category = "Test")
	ATGExtractionPad* TestExtractionPad;

	// Test Configuration
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test")
	bool bAutoRunOnBeginPlay = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Test")
	float TestTimeout = 30.0f;

	// Timers
	FTimerHandle TestTimerHandle;
	FTimerHandle TimeoutTimerHandle;
	float TestStartTime = 0.0f;

	// Events
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnSmokeTestCompleted OnSmokeTestCompleted;

public:
	// Test Control
	UFUNCTION(BlueprintCallable, Category = "Test", CallInEditor)
	void RunSmokeTests();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void StopTests();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void ResetTests();

	// Individual Tests
	UFUNCTION(BlueprintCallable, Category = "Test")
	void TestMapLoad();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void TestPlayerSpawn();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void TestCaptureNodeA();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void TestCaptureNodeB();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void TestExtractionUnlock();

	UFUNCTION(BlueprintCallable, Category = "Test")
	void TestExtractionComplete();

	// Getters
	UFUNCTION(BlueprintPure, Category = "Test")
	ESmokeTestState GetCurrentState() const { return CurrentState; }

	UFUNCTION(BlueprintPure, Category = "Test")
	FSmokeTestSuite GetTestResults() const { return TestSuite; }

	UFUNCTION(BlueprintPure, Category = "Test")
	float GetTestProgress() const;

	UFUNCTION(BlueprintPure, Category = "Test")
	FString GetCurrentTestName() const;

	// Blueprint Events
	UFUNCTION(BlueprintImplementableEvent, Category = "Test")
	void OnTestStarted(const FString& TestName);

	UFUNCTION(BlueprintImplementableEvent, Category = "Test")
	void OnTestCompleted(const FSmokeTestResult& Result);

	UFUNCTION(BlueprintImplementableEvent, Category = "Test")
	void OnAllTestsCompleted(bool bAllPassed);

private:
	void RunNextTest();
	void CompleteCurrentTest(bool bPassed, const FString& ErrorMessage = TEXT(""));
	void FindTestReferences();
	void SetTestState(ESmokeTestState NewState);
	void OnTestTimeout();
	
	// Test implementations
	void RunTest_MapLoad();
	void RunTest_PlayerSpawn();
	void RunTest_CaptureNodeA();
	void RunTest_CaptureNodeB();
	void RunTest_ExtractionUnlock();
	void RunTest_ExtractionComplete();

	// Helper functions
	void TeleportPlayerToLocation(const FVector& Location);
	bool IsPlayerAtLocation(const FVector& Location, float Tolerance = 200.0f) const;
	void SimulateCaptureNode(ATGCaptureNode* Node);
	void SimulateExtraction();

	// Test sequence
	TArray<TFunction<void()>> TestSequence;
	void InitializeTestSequence();
};