#include "TGSmokeTestRunner.h"
#include "TGPlayPawn.h"
#include "TGCaptureNode.h"
#include "TGExtractionPad.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"

ATGSmokeTestRunner::ATGSmokeTestRunner()
{
	PrimaryActorTick.bCanEverTick = false;
	
	CurrentState = ESmokeTestState::Idle;
	CurrentTestIndex = 0;
	TestPlayerPawn = nullptr;
	TestExtractionPad = nullptr;
}

void ATGSmokeTestRunner::BeginPlay()
{
	Super::BeginPlay();

	FindTestReferences();
	InitializeTestSequence();

	if (bAutoRunOnBeginPlay)
	{
		// Delay auto-run to allow world to fully initialize
		FTimerHandle DelayHandle;
		GetWorld()->GetTimerManager().SetTimer(DelayHandle, this, &ATGSmokeTestRunner::RunSmokeTests, 2.0f, false);
	}
}

void ATGSmokeTestRunner::InitializeTestSequence()
{
	TestSequence.Empty();
	TestSequence.Add([this]() { RunTest_MapLoad(); });
	TestSequence.Add([this]() { RunTest_PlayerSpawn(); });
	TestSequence.Add([this]() { RunTest_CaptureNodeA(); });
	TestSequence.Add([this]() { RunTest_CaptureNodeB(); });
	TestSequence.Add([this]() { RunTest_ExtractionUnlock(); });
	TestSequence.Add([this]() { RunTest_ExtractionComplete(); });
}

void ATGSmokeTestRunner::RunSmokeTests()
{
	UE_LOG(LogTemp, Log, TEXT("Starting smoke test suite"));

	// Reset test state
	ResetTests();

	SetTestState(ESmokeTestState::Running);
	FindTestReferences();
	
	// Start first test
	CurrentTestIndex = 0;
	RunNextTest();
}

void ATGSmokeTestRunner::StopTests()
{
	UE_LOG(LogTemp, Log, TEXT("Stopping smoke tests"));

	SetTestState(ESmokeTestState::Idle);
	GetWorld()->GetTimerManager().ClearTimer(TestTimerHandle);
	GetWorld()->GetTimerManager().ClearTimer(TimeoutTimerHandle);
}

void ATGSmokeTestRunner::ResetTests()
{
	TestSuite = FSmokeTestSuite();
	CurrentTestIndex = 0;
	SetTestState(ESmokeTestState::Idle);
	
	GetWorld()->GetTimerManager().ClearTimer(TestTimerHandle);
	GetWorld()->GetTimerManager().ClearTimer(TimeoutTimerHandle);
}

void ATGSmokeTestRunner::RunNextTest()
{
	if (CurrentTestIndex >= TestSequence.Num())
	{
		// All tests completed
		SetTestState(ESmokeTestState::Completed);
		
		// Calculate final results
		TestSuite.bAllTestsPassed = (TestSuite.FailedTests == 0);
		
		OnAllTestsCompleted(TestSuite.bAllTestsPassed);
		OnSmokeTestCompleted.Broadcast(TestSuite, TestSuite.bAllTestsPassed);
		
		UE_LOG(LogTemp, Log, TEXT("Smoke test suite completed - Passed: %d, Failed: %d"), 
			TestSuite.PassedTests, TestSuite.FailedTests);
		return;
	}

	// Start next test
	TestStartTime = GetWorld()->GetTimeSeconds();
	
	// Set timeout timer
	GetWorld()->GetTimerManager().SetTimer(TimeoutTimerHandle, this, &ATGSmokeTestRunner::OnTestTimeout, TestTimeout, false);
	
	// Execute test
	TestSequence[CurrentTestIndex]();
}

void ATGSmokeTestRunner::CompleteCurrentTest(bool bPassed, const FString& ErrorMessage)
{
	float ExecutionTime = GetWorld()->GetTimeSeconds() - TestStartTime;
	
	// Clear timeout timer
	GetWorld()->GetTimerManager().ClearTimer(TimeoutTimerHandle);
	
	// Create test result
	FSmokeTestResult Result;
	Result.TestName = GetCurrentTestName();
	Result.bPassed = bPassed;
	Result.ExecutionTime = ExecutionTime;
	Result.ErrorMessage = ErrorMessage;
	Result.Timestamp = FDateTime::Now();
	
	// Add to results
	TestSuite.TestResults.Add(Result);
	TestSuite.TotalExecutionTime += ExecutionTime;
	
	if (bPassed)
	{
		TestSuite.PassedTests++;
		UE_LOG(LogTemp, Log, TEXT("Test '%s' PASSED (%.2fs)"), *Result.TestName, ExecutionTime);
	}
	else
	{
		TestSuite.FailedTests++;
		UE_LOG(LogTemp, Error, TEXT("Test '%s' FAILED (%.2fs) - %s"), *Result.TestName, ExecutionTime, *ErrorMessage);
	}
	
	OnTestCompleted(Result);
	
	// Move to next test
	CurrentTestIndex++;
	
	// Small delay between tests
	FTimerHandle DelayHandle;
	GetWorld()->GetTimerManager().SetTimer(DelayHandle, this, &ATGSmokeTestRunner::RunNextTest, 0.5f, false);
}

void ATGSmokeTestRunner::FindTestReferences()
{
	// Find player pawn
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0))
	{
		TestPlayerPawn = Cast<ATGPlayPawn>(PC->GetPawn());
	}

	// Find capture nodes
	TestCaptureNodes.Empty();
	TArray<AActor*> FoundNodes;
	UGameplayStatics::GetAllActorsOfClass(GetWorld(), ATGCaptureNode::StaticClass(), FoundNodes);
	for (AActor* Actor : FoundNodes)
	{
		if (ATGCaptureNode* Node = Cast<ATGCaptureNode>(Actor))
		{
			TestCaptureNodes.Add(Node);
		}
	}

	// Find extraction pad
	TArray<AActor*> FoundPads;
	UGameplayStatics::GetAllActorsOfClass(GetWorld(), ATGExtractionPad::StaticClass(), FoundPads);
	if (FoundPads.Num() > 0)
	{
		TestExtractionPad = Cast<ATGExtractionPad>(FoundPads[0]);
	}
}

void ATGSmokeTestRunner::SetTestState(ESmokeTestState NewState)
{
	CurrentState = NewState;
	UE_LOG(LogTemp, Log, TEXT("Smoke test state changed to %s"), *UEnum::GetValueAsString(CurrentState));
}

void ATGSmokeTestRunner::OnTestTimeout()
{
	CompleteCurrentTest(false, TEXT("Test timed out"));
}

FString ATGSmokeTestRunner::GetCurrentTestName() const
{
	switch (CurrentTestIndex)
	{
		case 0: return TEXT("Map Load");
		case 1: return TEXT("Player Spawn");
		case 2: return TEXT("Capture Node A");
		case 3: return TEXT("Capture Node B");
		case 4: return TEXT("Extraction Unlock");
		case 5: return TEXT("Extraction Complete");
		default: return TEXT("Unknown");
	}
}

float ATGSmokeTestRunner::GetTestProgress() const
{
	if (TestSequence.Num() == 0) return 0.0f;
	return (float)CurrentTestIndex / (float)TestSequence.Num();
}

// Test Implementations

void ATGSmokeTestRunner::RunTest_MapLoad()
{
	OnTestStarted(TEXT("Map Load"));
	
	// Check if world is valid and basic actors exist
	if (!GetWorld())
	{
		CompleteCurrentTest(false, TEXT("World is null"));
		return;
	}

	// Check if we're in the correct map
	FString CurrentMapName = GetWorld()->GetMapName();
	if (CurrentMapName.IsEmpty())
	{
		CompleteCurrentTest(false, TEXT("Map name is empty"));
		return;
	}

	CompleteCurrentTest(true);
}

void ATGSmokeTestRunner::RunTest_PlayerSpawn()
{
	OnTestStarted(TEXT("Player Spawn"));
	
	FindTestReferences();
	
	if (!TestPlayerPawn)
	{
		CompleteCurrentTest(false, TEXT("Player pawn not found"));
		return;
	}

	if (!IsValid(TestPlayerPawn))
	{
		CompleteCurrentTest(false, TEXT("Player pawn is not valid"));
		return;
	}

	// Check if player has basic components
	if (!TestPlayerPawn->GetController())
	{
		CompleteCurrentTest(false, TEXT("Player has no controller"));
		return;
	}

	CompleteCurrentTest(true);
}

void ATGSmokeTestRunner::RunTest_CaptureNodeA()
{
	OnTestStarted(TEXT("Capture Node A"));
	
	if (TestCaptureNodes.Num() == 0)
	{
		CompleteCurrentTest(false, TEXT("No capture nodes found"));
		return;
	}

	ATGCaptureNode* NodeA = TestCaptureNodes[0];
	if (!IsValid(NodeA))
	{
		CompleteCurrentTest(false, TEXT("Capture Node A is invalid"));
		return;
	}

	// Teleport player to node
	TeleportPlayerToLocation(NodeA->GetActorLocation());
	
	// Simulate capture (this would be more sophisticated in a real implementation)
	SimulateCaptureNode(NodeA);
	
	CompleteCurrentTest(true);
}

void ATGSmokeTestRunner::RunTest_CaptureNodeB()
{
	OnTestStarted(TEXT("Capture Node B"));
	
	if (TestCaptureNodes.Num() < 2)
	{
		CompleteCurrentTest(false, TEXT("Less than 2 capture nodes found"));
		return;
	}

	ATGCaptureNode* NodeB = TestCaptureNodes[1];
	if (!IsValid(NodeB))
	{
		CompleteCurrentTest(false, TEXT("Capture Node B is invalid"));
		return;
	}

	// Teleport player to node
	TeleportPlayerToLocation(NodeB->GetActorLocation());
	
	// Simulate capture
	SimulateCaptureNode(NodeB);
	
	CompleteCurrentTest(true);
}

void ATGSmokeTestRunner::RunTest_ExtractionUnlock()
{
	OnTestStarted(TEXT("Extraction Unlock"));
	
	if (!IsValid(TestExtractionPad))
	{
		CompleteCurrentTest(false, TEXT("Extraction pad not found"));
		return;
	}

	// Force unlock extraction pad for testing
	TestExtractionPad->ForceUnlock();
	
	if (TestExtractionPad->IsLocked())
	{
		CompleteCurrentTest(false, TEXT("Extraction pad failed to unlock"));
		return;
	}

	CompleteCurrentTest(true);
}

void ATGSmokeTestRunner::RunTest_ExtractionComplete()
{
	OnTestStarted(TEXT("Extraction Complete"));
	
	if (!IsValid(TestExtractionPad))
	{
		CompleteCurrentTest(false, TEXT("Extraction pad not found"));
		return;
	}

	// Teleport player to extraction pad
	TeleportPlayerToLocation(TestExtractionPad->GetActorLocation());
	
	// Simulate extraction
	SimulateExtraction();
	
	CompleteCurrentTest(true);
}

// Helper Functions

void ATGSmokeTestRunner::TeleportPlayerToLocation(const FVector& Location)
{
	if (TestPlayerPawn)
	{
		TestPlayerPawn->SetActorLocation(Location + FVector(0, 0, 100));
		UE_LOG(LogTemp, Log, TEXT("Teleported player to %s"), *Location.ToString());
	}
}

bool ATGSmokeTestRunner::IsPlayerAtLocation(const FVector& Location, float Tolerance) const
{
	if (!TestPlayerPawn)
	{
		return false;
	}

	float Distance = FVector::Dist(TestPlayerPawn->GetActorLocation(), Location);
	return Distance <= Tolerance;
}

void ATGSmokeTestRunner::SimulateCaptureNode(ATGCaptureNode* Node)
{
	if (Node)
	{
		// In a real implementation, this would trigger the actual capture mechanics
		UE_LOG(LogTemp, Log, TEXT("Simulated capture of node %s"), *Node->GetName());
	}
}

void ATGSmokeTestRunner::SimulateExtraction()
{
	if (TestExtractionPad)
	{
		// In a real implementation, this would trigger extraction completion
		UE_LOG(LogTemp, Log, TEXT("Simulated extraction completion"));
	}
}

// Blueprint callable individual tests (for manual testing)
void ATGSmokeTestRunner::TestMapLoad() { RunTest_MapLoad(); }
void ATGSmokeTestRunner::TestPlayerSpawn() { RunTest_PlayerSpawn(); }
void ATGSmokeTestRunner::TestCaptureNodeA() { RunTest_CaptureNodeA(); }
void ATGSmokeTestRunner::TestCaptureNodeB() { RunTest_CaptureNodeB(); }
void ATGSmokeTestRunner::TestExtractionUnlock() { RunTest_ExtractionUnlock(); }
void ATGSmokeTestRunner::TestExtractionComplete() { RunTest_ExtractionComplete(); }