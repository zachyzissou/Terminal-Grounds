#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "Trust/TGTrustSubsystem.h"
#include "../TGTerritorial/Public/PhaseGateComponent.h"
#include "TGProfileSave.generated.h"

// Territory state for persistence
USTRUCT(BlueprintType)
struct FTGTerritoryState
{
    GENERATED_BODY()
    
    UPROPERTY()
    FString TerritoryID;
    
    UPROPERTY()
    FString ControllingFaction;
    
    UPROPERTY()
    ESiegePhase CurrentPhase;
    
    UPROPERTY()
    float PhaseProgress;
    
    UPROPERTY()
    float DominanceValue;
    
    UPROPERTY()
    int32 AttackerTickets;
    
    UPROPERTY()
    int32 DefenderTickets;
    
    UPROPERTY()
    FDateTime LastSiegeTime;
    
    UPROPERTY()
    bool bSiegeActive;
    
    UPROPERTY()
    TArray<FString> ParticipatingFactions;
    
    FTGTerritoryState()
    {
        CurrentPhase = ESiegePhase::Probe;
        PhaseProgress = 0.0f;
        DominanceValue = 0.5f;
        AttackerTickets = 100;
        DefenderTickets = 100;
        bSiegeActive = false;
        LastSiegeTime = FDateTime::Now();
    }
};

// Siege performance metrics for analysis
USTRUCT(BlueprintType)
struct FTGSiegePerformanceRecord
{
    GENERATED_BODY()
    
    UPROPERTY()
    FString SiegeID;
    
    UPROPERTY()
    FDateTime StartTime;
    
    UPROPERTY()
    FDateTime EndTime;
    
    UPROPERTY()
    TArray<FString> ParticipatingPlayers;
    
    UPROPERTY()
    float AverageFPS;
    
    UPROPERTY()
    float PeakLatency;
    
    UPROPERTY()
    int32 TotalPhaseTransitions;
    
    UPROPERTY()
    bool bVictoryAchieved;
    
    UPROPERTY()
    FString WinningFaction;
    
    FTGSiegePerformanceRecord()
    {
        StartTime = FDateTime::Now();
        EndTime = FDateTime::Now();
        AverageFPS = 60.0f;
        PeakLatency = 0.0f;
        TotalPhaseTransitions = 0;
        bVictoryAchieved = false;
    }
};

UCLASS()
class TGCORE_API UTGProfileSave : public USaveGame
{
	GENERATED_BODY()
public:
	// Simple placeholders for inventory/stash
	UPROPERTY()
	TMap<FName, int32> Inventory; // itemId -> count

	UPROPERTY()
	TMap<FName, int32> Stash; // secure stash

	// Bold systems persistence
	UPROPERTY()
	TArray<FTGTrustRecord> TrustRecords;

	UPROPERTY()
	TArray<FName> UnlockedCodexIds;

	UPROPERTY()
	float ConvoyIntegrityIndex = 0.5f;
	
	// Phase 7: Faction relationships
	UPROPERTY()
	TArray<FTGFactionRelation> FactionRelations;
	
	// Phase 8: Territorial siege persistence
	UPROPERTY()
	TArray<FTGTerritoryState> TerritoryStates;
	
	UPROPERTY()
	TArray<FTGSiegePerformanceRecord> SiegeHistory;
	
	UPROPERTY()
	float PlayerSiegeRating = 1000.0f;
	
	UPROPERTY()
	int32 SiegeVictories = 0;
	
	UPROPERTY()
	int32 SiegeParticipations = 0;
	
	UPROPERTY()
	FDateTime LastSiegeTime;
	
	// Phase 9: Territorial progression persistence
	UPROPERTY()
	TMap<int32, float> FactionReputationPoints;
	
	UPROPERTY()
	TMap<int32, int32> FactionProgressionTiers; // FactionId -> EFactionProgressionTier as int32
	
	UPROPERTY()
	TMap<int32, TArray<FName>> FactionUnlockedAbilities; // FactionId -> Array of unlocked ability names
	
	UPROPERTY()
	TMap<int32, int32> FactionTerritoryHours; // FactionId -> Total territory control hours
	
	UPROPERTY()
	TMap<int32, float> FactionExtractionBonuses; // FactionId -> Extraction bonus multiplier
	
	UPROPERTY()
	TMap<int32, float> FactionInfluenceRates; // FactionId -> Influence rate multiplier
	
	UPROPERTY()
	TArray<FName> CompletedTerritorialObjectives; // Completed objective IDs for persistence
	
	UTGProfileSave()
	{
		ConvoyIntegrityIndex = 0.5f;
		PlayerSiegeRating = 1000.0f;
		SiegeVictories = 0;
		SiegeParticipations = 0;
		LastSiegeTime = FDateTime::Now();
		
		// Initialize faction progression data for all 7 factions
		const TArray<int32> FactionIds = {1, 2, 3, 4, 5, 6, 7};
		for (int32 FactionId : FactionIds)
		{
			FactionReputationPoints.Add(FactionId, 0.0f);
			FactionProgressionTiers.Add(FactionId, 0); // EFactionProgressionTier::Recruit
			FactionTerritoryHours.Add(FactionId, 0);
			FactionExtractionBonuses.Add(FactionId, 1.0f);
			FactionInfluenceRates.Add(FactionId, 1.0f);
			FactionUnlockedAbilities.Add(FactionId, TArray<FName>());
		}
	}
};
