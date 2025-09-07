#include "TGPlaytestExtractionZone.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "TGPlayPawn.h"
#include "TGPlaytestGameMode.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"

ATGPlaytestExtractionZone::ATGPlaytestExtractionZone()
{
    PrimaryActorTick.bCanEverTick = true;

    // Create root component
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));

    // Create extraction zone
    ExtractionZone = CreateDefaultSubobject<UBoxComponent>(TEXT("ExtractionZone"));
    ExtractionZone->SetupAttachment(RootComponent);
    ExtractionZone->SetBoxExtent(FVector(400.0f, 400.0f, 250.0f));
    ExtractionZone->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    ExtractionZone->SetCollisionResponseToAllChannels(ECR_Ignore);
    ExtractionZone->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

    // Create zone mesh (visual representation)
    ZoneMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ZoneMesh"));
    ZoneMesh->SetupAttachment(RootComponent);
    ZoneMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    // Initialize state
    bPlayerInZone = false;
    PlayerInZone = nullptr;
    PlaytestGameMode = nullptr;
    bRequiresAllEnemiesDead = true;
    bShowDebugMessages = true;
}

void ATGPlaytestExtractionZone::BeginPlay()
{
    Super::BeginPlay();

    // Bind overlap events
    ExtractionZone->OnComponentBeginOverlap.AddDynamic(this, &ATGPlaytestExtractionZone::OnExtractionZoneBeginOverlap);
    ExtractionZone->OnComponentEndOverlap.AddDynamic(this, &ATGPlaytestExtractionZone::OnExtractionZoneEndOverlap);

    // Find the playtest game mode
    FindPlaytestGameMode();

    // Initial state update
    UpdateZoneState();
}

void ATGPlaytestExtractionZone::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // Update zone state based on game conditions
    UpdateZoneState();
}

void ATGPlaytestExtractionZone::OnExtractionZoneBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
    if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
    {
        bPlayerInZone = true;
        PlayerInZone = Player;

        // Notify game mode
        if (PlaytestGameMode)
        {
            PlaytestGameMode->PlayerEnteredExtractionZone();
        }

        // Broadcast events
        OnPlayerEnteredZone.Broadcast(Player);
        OnPlayerEntered(Player);

        if (bShowDebugMessages && GEngine)
        {
            if (bRequiresAllEnemiesDead && PlaytestGameMode && !PlaytestGameMode->CanExtract())
            {
                GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Orange, 
                    FString::Printf(TEXT("EXTRACTION ZONE - Eliminate %d more enemies to extract!"), 
                                   PlaytestGameMode->GetRemainingEnemies()));
            }
            else
            {
                GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Green, 
                                               TEXT("EXTRACTION ZONE - Ready for extraction!"));
            }
        }

        UE_LOG(LogTemp, Log, TEXT("Player %s entered extraction zone"), *Player->GetName());
    }
}

void ATGPlaytestExtractionZone::OnExtractionZoneEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
    if (ATGPlayPawn* Player = Cast<ATGPlayPawn>(OtherActor))
    {
        if (PlayerInZone == Player)
        {
            bPlayerInZone = false;
            PlayerInZone = nullptr;

            // Notify game mode
            if (PlaytestGameMode)
            {
                PlaytestGameMode->PlayerExitedExtractionZone();
            }

            // Broadcast events
            OnPlayerExitedZone.Broadcast(Player);
            OnPlayerExited(Player);

            if (bShowDebugMessages && GEngine)
            {
                GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow, 
                                               TEXT("Left extraction zone"));
            }

            UE_LOG(LogTemp, Log, TEXT("Player %s exited extraction zone"), *Player->GetName());
        }
    }
}

void ATGPlaytestExtractionZone::FindPlaytestGameMode()
{
    if (UWorld* World = GetWorld())
    {
        PlaytestGameMode = Cast<ATGPlaytestGameMode>(World->GetAuthGameMode());
        
        if (PlaytestGameMode)
        {
            UE_LOG(LogTemp, Log, TEXT("Found ATGPlaytestGameMode for extraction zone"));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Could not find ATGPlaytestGameMode - extraction zone may not function properly"));
        }
    }
}

void ATGPlaytestExtractionZone::UpdateZoneState()
{
    // Update visual state based on extraction availability
    if (PlaytestGameMode)
    {
        bool bCanExtract = PlaytestGameMode->CanExtract();
        
        // Visual updates will be handled in Blueprint through OnZoneActivated/Deactivated events
        static bool bPreviousCanExtract = false;
        if (bCanExtract != bPreviousCanExtract)
        {
            if (bCanExtract)
            {
                OnZoneActivated();
            }
            else
            {
                OnZoneDeactivated();
            }
            bPreviousCanExtract = bCanExtract;
        }
    }
}

void ATGPlaytestExtractionZone::SetExtractionEnabled(bool bEnabled)
{
    ExtractionZone->SetCollisionEnabled(bEnabled ? ECollisionEnabled::QueryOnly : ECollisionEnabled::NoCollision);
    
    if (!bEnabled && bPlayerInZone)
    {
        // Force player out of zone if disabling
        bPlayerInZone = false;
        if (PlayerInZone && PlaytestGameMode)
        {
            PlaytestGameMode->PlayerExitedExtractionZone();
        }
        PlayerInZone = nullptr;
    }
}