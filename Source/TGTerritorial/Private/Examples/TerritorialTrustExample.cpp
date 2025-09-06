// Copyright Terminal Grounds. All Rights Reserved.

#include "Examples/TerritorialTrustExample.h"
#include "Engine/World.h"
#include "Engine/Engine.h"

ATerritorialTrustExample::ATerritorialTrustExample()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ATerritorialTrustExample::BeginPlay()
{
    Super::BeginPlay();

    // Get trust system reference
    if (UWorld* World = GetWorld())
    {
        TrustSystem = World->GetGameInstance()->GetSubsystem<UTGTrustSubsystem>();
        
        if (TrustSystem && bAutoBindEvents)
        {
            BindTrustEvents();
        }
    }

    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Log, TEXT("TerritorialTrustExample initialized. Trust system: %s"), 
            TrustSystem ? TEXT("Found") : TEXT("Not Found"));
    }
}

void ATerritorialTrustExample::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void ATerritorialTrustExample::ExampleRecordCooperation(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID)
{
    if (!TrustSystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Trust system not available"));
        return;
    }

    // Record territorial cooperation with contextual bonus
    TrustSystem->RecordTerritorialCooperation(PlayerA, PlayerB, TerritoryID, 0.08f);
    
    LogTrustAction(TEXT("Cooperation"), PlayerA, PlayerB, 0.08f);
}

void ATerritorialTrustExample::ExampleRecordBetrayal(const FString& Betrayer, const FString& Victim, int32 TerritoryID)
{
    if (!TrustSystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Trust system not available"));
        return;
    }

    // Record territorial betrayal with severe penalty
    TrustSystem->RecordTerritorialBetrayal(Betrayer, Victim, TerritoryID, 0.6f);
    
    LogTrustAction(TEXT("Betrayal"), Betrayer, Victim, -0.6f);
}

void ATerritorialTrustExample::ExampleRecordExtractionAssist(const FString& Helper, const FString& Assisted, int32 ExtractionPointID)
{
    if (!TrustSystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Trust system not available"));
        return;
    }

    // Record extraction assistance with high trust bonus
    TrustSystem->RecordExtractionAssistance(Helper, Assisted, ExtractionPointID, 0.10f);
    
    LogTrustAction(TEXT("Extraction Assistance"), Helper, Assisted, 0.10f);
}

void ATerritorialTrustExample::ExampleCheckTrustModifier(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID)
{
    if (!TrustSystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Trust system not available"));
        return;
    }

    // Get current trust values
    float BaseTrust = TrustSystem->GetTrustIndex(PlayerA, PlayerB);
    float TerritorialModifier = TrustSystem->GetTerritorialTrustModifier(PlayerA, PlayerB, TerritoryID);
    int32 CooperationScore = TrustSystem->GetTerritorialCooperationScore(PlayerA, PlayerB);
    int32 BetrayalCount = TrustSystem->GetTerritorialBetrayalCount(PlayerA, PlayerB);

    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Log, TEXT("Trust Status for %s <-> %s:"), *PlayerA, *PlayerB);
        UE_LOG(LogTemp, Log, TEXT("  Base Trust: %f"), BaseTrust);
        UE_LOG(LogTemp, Log, TEXT("  Territorial Modifier: %f"), TerritorialModifier);
        UE_LOG(LogTemp, Log, TEXT("  Cooperation Score: %d"), CooperationScore);
        UE_LOG(LogTemp, Log, TEXT("  Betrayal Count: %d"), BetrayalCount);
    }
}

void ATerritorialTrustExample::OnTerritorialCooperationReceived(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustGain)
{
    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Log, TEXT("Territorial Cooperation Event: %s & %s cooperated in territory %d (Trust Gain: %f)"), 
            *PlayerA, *PlayerB, TerritoryID, TrustGain);
    }

    // Example: Trigger UI notification, sound effects, or other game responses
    // This is where you'd integrate with your game's feedback systems
}

void ATerritorialTrustExample::OnTerritorialBetrayalReceived(const FString& PlayerA, const FString& PlayerB, int32 TerritoryID, float TrustLoss)
{
    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Warning, TEXT("Territorial Betrayal Event: %s betrayed %s in territory %d (Trust Loss: %f)"), 
            *PlayerA, *PlayerB, TerritoryID, TrustLoss);
    }

    // Example: Trigger betrayal notifications, faction reputation changes, etc.
}

void ATerritorialTrustExample::OnExtractionAssistanceReceived(const FString& Helper, const FString& Assisted, float TrustBonus)
{
    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Log, TEXT("Extraction Assistance Event: %s helped %s extract (Trust Bonus: %f)"), 
            *Helper, *Assisted, TrustBonus);
    }

    // Example: Award experience points, trigger positive feedback, update leaderboards
}

void ATerritorialTrustExample::BindTrustEvents()
{
    if (!TrustSystem)
    {
        return;
    }

    // Bind to territorial trust events
    TrustSystem->OnTerritorialCooperation.AddDynamic(this, &ATerritorialTrustExample::OnTerritorialCooperationReceived);
    TrustSystem->OnTerritorialBetrayal.AddDynamic(this, &ATerritorialTrustExample::OnTerritorialBetrayalReceived);
    TrustSystem->OnExtractionAssistance.AddDynamic(this, &ATerritorialTrustExample::OnExtractionAssistanceReceived);

    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Log, TEXT("Trust events bound successfully"));
    }
}

void ATerritorialTrustExample::LogTrustAction(const FString& Action, const FString& PlayerA, const FString& PlayerB, float Value)
{
    if (bEnableLogging)
    {
        UE_LOG(LogTemp, Log, TEXT("Trust Action - %s: %s <-> %s (Value: %f)"), 
            *Action, *PlayerA, *PlayerB, Value);
    }
}