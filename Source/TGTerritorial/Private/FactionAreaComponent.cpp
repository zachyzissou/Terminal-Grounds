// Copyright Terminal Grounds. All Rights Reserved.

#include "FactionAreaComponent.h"
#include "Engine/World.h"
#include "Components/SphereComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/DecalComponent.h"
#include "GameFramework/Pawn.h"
#include "TerritorialManager.h"

UFactionAreaComponent::UFactionAreaComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 1.0f; // Update every second for performance

    // Default values
    FactionID = EFactionID::None;
    TerritoryID = 0;
    AreaName = TEXT("Unnamed Area");
    AreaDescription = TEXT("Faction controlled territory");
    FactionColor = FLinearColor::White;
    LightingIntensity = 1.0f;
    bEnableFactionLighting = true;
    SpawnPointRadius = 100.0f;
    MaxPlayersInArea = 8;
    bAllowEnemySpawning = false;
    InfluenceRadius = 1000.0f;
    BaseInfluenceRate = 1.0f;
    ContestInfluenceRate = 0.5f;
    MaxPlayersForInfluence = 4;
    AreaCenter = FVector::ZeroVector;
    AreaRadius = 2000.0f;
    bUseComplexBoundary = false;
    LastInfluenceUpdate = 0.0f;
}

void UFactionAreaComponent::BeginPlay()
{
    Super::BeginPlay();

    // Create sphere boundary component if we don't have complex boundary
    if (!bUseComplexBoundary && !AreaBoundary)
    {
        AreaBoundary = NewObject<USphereComponent>(GetOwner());
        if (AreaBoundary)
        {
            AreaBoundary->SetupAttachment(GetOwner()->GetRootComponent());
            AreaBoundary->SetSphereRadius(AreaRadius);
            AreaBoundary->SetRelativeLocation(AreaCenter);
            AreaBoundary->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
            AreaBoundary->SetCollisionResponseToAllChannels(ECR_Ignore);
            AreaBoundary->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
            
            // Bind overlap events
            AreaBoundary->OnComponentBeginOverlap.AddDynamic(this, &UFactionAreaComponent::OnAreaBeginOverlap);
            AreaBoundary->OnComponentEndOverlap.AddDynamic(this, &UFactionAreaComponent::OnAreaEndOverlap);
        }
    }

    // Apply visual identity
    if (bEnableFactionLighting)
    {
        ApplyFactionLighting();
    }

    // Initialize default spawn points if none are set
    if (SpawnPoints.Num() == 0)
    {
        // Create basic spawn grid around area center
        for (int32 i = 0; i < 4; i++)
        {
            float Angle = (i * 90.0f) * PI / 180.0f;
            FVector SpawnOffset = FVector(
                FMath::Cos(Angle) * (AreaRadius * 0.7f),
                FMath::Sin(Angle) * (AreaRadius * 0.7f),
                0.0f
            );
            SpawnPoints.Add(AreaCenter + SpawnOffset);
        }
    }
}

void UFactionAreaComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // Update territorial influence
    UpdateTerritorialInfluence(DeltaTime);

    // Clean up invalid player references
    PlayersInArea.RemoveAll([](const TWeakObjectPtr<APawn>& Player) {
        return !Player.IsValid();
    });
}

void UFactionAreaComponent::InitializeFactionArea(EFactionID InFactionID, int32 InTerritoryID, const FVector& InAreaCenter, float InAreaRadius)
{
    FactionID = InFactionID;
    TerritoryID = InTerritoryID;
    AreaCenter = InAreaCenter;
    AreaRadius = InAreaRadius;

    // Set faction-specific defaults
    switch (FactionID)
    {
    case EFactionID::Directorate:
        FactionColor = FLinearColor(0.2f, 0.4f, 1.0f, 1.0f); // Corporate blue
        AreaName = TEXT("Directorate Sector");
        BaseInfluenceRate = 1.1f; // Corporate efficiency bonus
        break;
    case EFactionID::Free77:
        FactionColor = FLinearColor(1.0f, 0.3f, 0.2f, 1.0f); // Resistance red
        AreaName = TEXT("Free77 Territory");
        BaseInfluenceRate = 1.0f; // Baseline
        break;
    case EFactionID::CivicWardens:
        FactionColor = FLinearColor(0.7f, 0.7f, 0.7f, 1.0f); // Neutral gray
        AreaName = TEXT("Civilian Zone");
        BaseInfluenceRate = 0.8f; // Reduced influence
        bAllowEnemySpawning = true; // Neutral areas allow all factions
        break;
    default:
        FactionColor = FLinearColor::White;
        AreaName = TEXT("Unknown Territory");
        break;
    }

    UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Initialized %s (ID: %d) at %s with radius %f"), 
        *AreaName, TerritoryID, *AreaCenter.ToString(), AreaRadius);
}

void UFactionAreaComponent::SetFactionVisualIdentity(FLinearColor Color, float Intensity)
{
    FactionColor = Color;
    LightingIntensity = Intensity;
    
    if (bEnableFactionLighting)
    {
        ApplyFactionLighting();
    }
}

void UFactionAreaComponent::AddSpawnPoint(const FVector& SpawnLocation)
{
    SpawnPoints.Add(SpawnLocation);
    UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Added spawn point at %s"), *SpawnLocation.ToString());
}

void UFactionAreaComponent::RemoveSpawnPoint(int32 SpawnIndex)
{
    if (SpawnPoints.IsValidIndex(SpawnIndex))
    {
        SpawnPoints.RemoveAt(SpawnIndex);
        UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Removed spawn point at index %d"), SpawnIndex);
    }
}

TArray<FVector> UFactionAreaComponent::GetAvailableSpawnPoints() const
{
    return SpawnPoints;
}

FVector UFactionAreaComponent::GetBestSpawnPoint(const TArray<APawn*>& ExistingPlayers) const
{
    if (SpawnPoints.Num() == 0)
    {
        return AreaCenter;
    }

    // Find spawn point with maximum distance from existing players
    FVector BestSpawn = SpawnPoints[0];
    float BestDistance = 0.0f;

    for (const FVector& SpawnPoint : SpawnPoints)
    {
        float MinDistanceToPlayers = FLT_MAX;
        
        for (const APawn* Player : ExistingPlayers)
        {
            if (Player)
            {
                float Distance = FVector::Dist(SpawnPoint, Player->GetActorLocation());
                MinDistanceToPlayers = FMath::Min(MinDistanceToPlayers, Distance);
            }
        }

        if (MinDistanceToPlayers > BestDistance)
        {
            BestDistance = MinDistanceToPlayers;
            BestSpawn = SpawnPoint;
        }
    }

    return BestSpawn;
}

bool UFactionAreaComponent::IsLocationInArea(const FVector& Location) const
{
    if (bUseComplexBoundary && BoundaryPoints.Num() > 2)
    {
        // Complex polygon boundary check (simplified 2D check)
        // This is a basic implementation - could be enhanced for 3D polygons
        return FVector::Dist2D(Location, AreaCenter) <= AreaRadius;
    }
    else
    {
        // Simple sphere boundary
        return FVector::Dist(Location, AreaCenter) <= AreaRadius;
    }
}

TArray<APawn*> UFactionAreaComponent::GetPlayersInArea() const
{
    TArray<APawn*> ValidPlayers;
    
    for (const TWeakObjectPtr<APawn>& WeakPlayer : PlayersInArea)
    {
        if (WeakPlayer.IsValid())
        {
            ValidPlayers.Add(WeakPlayer.Get());
        }
    }
    
    return ValidPlayers;
}

int32 UFactionAreaComponent::GetFactionPlayerCount(EFactionID CheckFactionID) const
{
    int32 Count = 0;
    
    for (const TWeakObjectPtr<APawn>& WeakPlayer : PlayersInArea)
    {
        if (WeakPlayer.IsValid() && GetPlayerFaction(WeakPlayer.Get()) == CheckFactionID)
        {
            Count++;
        }
    }
    
    return Count;
}

bool UFactionAreaComponent::IsAreaContested() const
{
    int32 FactionCounts[8] = {0}; // Support up to 8 factions
    
    for (const TWeakObjectPtr<APawn>& WeakPlayer : PlayersInArea)
    {
        if (WeakPlayer.IsValid())
        {
            EFactionID PlayerFaction = GetPlayerFaction(WeakPlayer.Get());
            int32 FactionIndex = static_cast<int32>(PlayerFaction);
            if (FactionIndex >= 0 && FactionIndex < 8)
            {
                FactionCounts[FactionIndex]++;
            }
        }
    }
    
    // Area is contested if more than one faction has players present
    int32 FactionsWithPlayers = 0;
    for (int32 i = 1; i < 8; i++) // Skip None faction
    {
        if (FactionCounts[i] > 0)
        {
            FactionsWithPlayers++;
        }
    }
    
    return FactionsWithPlayers > 1;
}

void UFactionAreaComponent::UpdateTerritorialInfluence(float DeltaTime)
{
    LastInfluenceUpdate += DeltaTime;
    
    // Update influence every second
    if (LastInfluenceUpdate >= 1.0f)
    {
        LastInfluenceUpdate = 0.0f;
        
        int32 FriendlyPlayers = GetFactionPlayerCount(FactionID);
        if (FriendlyPlayers > 0)
        {
            float InfluenceRate = IsAreaContested() ? ContestInfluenceRate : BaseInfluenceRate;
            float PlayerMultiplier = FMath::Min(static_cast<float>(FriendlyPlayers), static_cast<float>(MaxPlayersForInfluence)) / MaxPlayersForInfluence;
            
            int32 InfluenceGain = FMath::RoundToInt(InfluenceRate * PlayerMultiplier);
            
            if (InfluenceGain > 0)
            {
                FString Cause = FString::Printf(TEXT("Area Control (%d players)"), FriendlyPlayers);
                NotifyTerritorialManager(InfluenceGain, Cause);
            }
        }
    }
}

void UFactionAreaComponent::ApplyFactionLighting()
{
    // Clean up existing lights
    for (UPointLightComponent* Light : FactionLights)
    {
        if (Light)
        {
            Light->DestroyComponent();
        }
    }
    FactionLights.Empty();

    // Create new faction lights
    if (GetOwner())
    {
        for (int32 i = 0; i < 4; i++) // 4 lights around the area
        {
            UPointLightComponent* Light = NewObject<UPointLightComponent>(GetOwner());
            if (Light)
            {
                Light->SetupAttachment(GetOwner()->GetRootComponent());
                
                // Position lights in a circle around the area
                float Angle = (i * 90.0f) * PI / 180.0f;
                FVector LightOffset = FVector(
                    FMath::Cos(Angle) * (AreaRadius * 0.8f),
                    FMath::Sin(Angle) * (AreaRadius * 0.8f),
                    200.0f // Height offset
                );
                Light->SetRelativeLocation(AreaCenter + LightOffset);
                
                // Configure light properties
                Light->SetLightColor(FactionColor);
                Light->SetIntensity(LightingIntensity * 1000.0f); // UE5 light intensity scale
                Light->SetAttenuationRadius(AreaRadius * 0.5f);
                Light->SetCastShadows(false); // Performance optimization
                
                FactionLights.Add(Light);
            }
        }
    }
}

void UFactionAreaComponent::SpawnFactionDecals()
{
    // Implementation for faction decals would go here
    // This would place faction logos and signage around the area
    UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Spawning faction decals for %s"), *AreaName);
}

void UFactionAreaComponent::UpdateAreaBoundaryEffects()
{
    // Implementation for boundary effects (particle systems, etc.) would go here
    UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Updating boundary effects for %s"), *AreaName);
}

void UFactionAreaComponent::OnAreaBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, 
    UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
    if (APawn* Player = Cast<APawn>(OtherActor))
    {
        OnPlayerEntered(Player);
    }
}

void UFactionAreaComponent::OnAreaEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, 
    UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
    if (APawn* Player = Cast<APawn>(OtherActor))
    {
        OnPlayerExited(Player);
    }
}

void UFactionAreaComponent::OnPlayerEntered(APawn* Player)
{
    if (Player && !PlayersInArea.Contains(Player))
    {
        PlayersInArea.Add(Player);
        
        EFactionID PlayerFaction = GetPlayerFaction(Player);
        OnPlayerEnteredArea.Broadcast(Player, PlayerFaction, TerritoryID);
        
        UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Player entered %s (Faction: %d)"), 
            *AreaName, static_cast<int32>(PlayerFaction));
    }
}

void UFactionAreaComponent::OnPlayerExited(APawn* Player)
{
    if (Player)
    {
        PlayersInArea.RemoveAll([Player](const TWeakObjectPtr<APawn>& WeakPlayer) {
            return WeakPlayer.Get() == Player;
        });
        
        EFactionID PlayerFaction = GetPlayerFaction(Player);
        OnPlayerExitedArea.Broadcast(Player, PlayerFaction, TerritoryID);
        
        UE_LOG(LogTemp, Log, TEXT("FactionAreaComponent: Player exited %s (Faction: %d)"), 
            *AreaName, static_cast<int32>(PlayerFaction));
    }
}

EFactionID UFactionAreaComponent::GetPlayerFaction(APawn* Player) const
{
    // This would integrate with the player's faction system
    // For now, return a placeholder based on player name or other identifier
    if (!Player)
    {
        return EFactionID::None;
    }

    // This is a simplified implementation - in the real game this would
    // check the player's faction component or game state
    return EFactionID::None;
}

float UFactionAreaComponent::CalculateInfluenceMultiplier() const
{
    int32 PlayersInAreaCount = GetPlayersInArea().Num();
    if (PlayersInAreaCount == 0)
    {
        return 0.0f;
    }
    
    // Diminishing returns for too many players
    float Multiplier = FMath::Min(static_cast<float>(PlayersInAreaCount), static_cast<float>(MaxPlayersForInfluence));
    return Multiplier / MaxPlayersForInfluence;
}

void UFactionAreaComponent::NotifyTerritorialManager(int32 InfluenceChange, const FString& Cause)
{
    if (UWorld* World = GetWorld())
    {
        if (UTerritorialManager* TerritorialManager = UTerritorialSubsystem::GetTerritorialManager(World))
        {
            TerritorialManager->UpdateTerritorialInfluence(
                TerritoryID, 
                ETerritoryType::ControlPoint, 
                static_cast<int32>(FactionID), 
                InfluenceChange, 
                Cause
            );
        }
    }
}