#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/DataTable.h"
#include "Engine/TimerHandle.h"
#include "Components/StaticMeshComponent.h"
#include "TGProceduralArena.h"
#include "TGTerritorialProceduralSystem.generated.h"

// Forward declarations
class UTGTerritorialManager;
class ATGProceduralArena;
struct FTGTerritoryData;
struct FTGFactionInfluence;

UENUM(BlueprintType)
enum class ETGTerritorialModificationType : uint8
{
    None UMETA(DisplayName = "None"),
    Cosmetic UMETA(DisplayName = "Cosmetic Overlay"),
    AssetPlacement UMETA(DisplayName = "Dynamic Asset Placement"), 
    StructuralChange UMETA(DisplayName = "Structural Modification")
};

UENUM(BlueprintType)
enum class ETGFactionArchitecturalStyle : uint8
{
    Neutral UMETA(DisplayName = "Neutral"),
    CorporateHegemony UMETA(DisplayName = "Corporate - Clean Geometric"),
    Free77 UMETA(DisplayName = "Free77 - Military Tactical"),
    IronScavengers UMETA(DisplayName = "Iron Scavengers - Improvised Salvage"),
    NomadClans UMETA(DisplayName = "Nomad Clans - Adaptive Mobile"),
    ArchiveKeepers UMETA(DisplayName = "Archive Keepers - Information Secure"),
    CivicWardens UMETA(DisplayName = "Civic Wardens - Community Defense")
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGTerritorialModification
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    int32 TerritoryId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial") 
    int32 ControllingFactionId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    ETGTerritorialModificationType ModificationType = ETGTerritorialModificationType::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    ETGFactionArchitecturalStyle ArchitecturalStyle = ETGFactionArchitecturalStyle::Neutral;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    TArray<FVector> ModificationLocations;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    TArray<AActor*> PlacedAssets;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    float InfluenceIntensity = 0.0f; // 0.0 to 1.0

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    FDateTime LastModificationTime;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territorial")
    bool bContested = false;

    FTGTerritorialModification()
    {
        LastModificationTime = FDateTime::Now();
    }
};

USTRUCT(BlueprintType)
struct TGCORE_API FTGFactionAssetLibrary
{
    GENERATED_BODY()

    // Cosmetic overlays
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_FactionBanner;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_TerritorialMarker;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_InfluenceSignage;

    // Dynamic asset placement
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_DefensiveBarrier;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_SupplyCache;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_CommunicationRelay;

    // Structural modifications
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_FactionDoor;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_SecurityCheckpoint;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TSubclassOf<AActor> BP_FortificationWall;

    // Atmospheric elements
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    TArray<TSubclassOf<AActor>> AtmosphericProps;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    FLinearColor FactionPrimaryColor = FLinearColor::White;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Assets")
    FLinearColor FactionSecondaryColor = FLinearColor::Black;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritorialProcGenerationStarted, int32, TerritoryId, int32, FactionId, ETGTerritorialModificationType, ModType);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritorialProcGenerationComplete, int32, TerritoryId, int32, FactionId, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerritorialAssetsRequested, int32, TerritoryId, int32, FactionId);

/**
 * Territorial Procedural System
 * 
 * Integrates real-time territorial control changes with procedural map generation.
 * Responds to faction control shifts by modifying arena environments with 
 * faction-specific assets, maintaining competitive balance while enhancing
 * environmental storytelling and territorial immersion.
 * 
 * System Architecture:
 * - Listens to UTGTerritorialManager control change events via WebSocket (port 8765)
 * - Triggers procedural modifications through ATGProceduralArena integration
 * - Generates faction-specific assets via proven production pipeline (92% success rate)
 * - Maintains competitive balance through spatial validation algorithms
 * - Supports real-time updates for 100+ concurrent players
 */
UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGTerritorialProceduralSystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    UTGTerritorialProceduralSystem();

    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;

    // Core Territorial-Procedural Integration
    UFUNCTION(BlueprintCallable, Category = "Territorial Procedural")
    bool InitializeTerritorialProceduralSystem();

    UFUNCTION(BlueprintCallable, Category = "Territorial Procedural") 
    void ProcessTerritorialChange(int32 TerritoryId, int32 OldFactionId, int32 NewFactionId);

    UFUNCTION(BlueprintCallable, Category = "Territorial Procedural")
    void UpdateTerritorialInfluence(int32 TerritoryId, int32 FactionId, float InfluenceLevel);

    UFUNCTION(BlueprintCallable, Category = "Territorial Procedural")
    bool ApplyTerritorialModification(const FTGTerritorialModification& Modification);

    // Asset Generation Integration
    UFUNCTION(BlueprintCallable, Category = "Asset Generation")
    void RequestTerritorialAssets(int32 TerritoryId, int32 FactionId, ETGTerritorialModificationType ModType);

    UFUNCTION(BlueprintCallable, Category = "Asset Generation")
    void OnAssetGenerationComplete(int32 TerritoryId, int32 FactionId, const TArray<FString>& GeneratedAssetPaths);

    // Competitive Balance Validation
    UFUNCTION(BlueprintCallable, Category = "Validation")
    bool ValidateTerritorialModification(const FTGTerritorialModification& Modification);

    UFUNCTION(BlueprintCallable, Category = "Validation")
    TArray<FVector> GetValidPlacementLocations(int32 TerritoryId, ETGTerritorialModificationType ModType);

    UFUNCTION(BlueprintCallable, Category = "Validation")
    bool CheckCompetitiveBalance(const TArray<FVector>& ProposedLocations);

    // Faction Asset Libraries
    UFUNCTION(BlueprintCallable, Category = "Faction Assets")
    FTGFactionAssetLibrary GetFactionAssetLibrary(int32 FactionId);

    UFUNCTION(BlueprintCallable, Category = "Faction Assets")
    ETGFactionArchitecturalStyle GetFactionArchitecturalStyle(int32 FactionId);

    // Real-time Integration
    UFUNCTION(BlueprintCallable, Category = "Network")
    void ConnectToTerritorialWebSocket();

    UFUNCTION(BlueprintCallable, Category = "Network") 
    void OnTerritorialWebSocketMessage(const FString& Message);

    // Seasonal Evolution Support
    UFUNCTION(BlueprintCallable, Category = "Seasonal")
    void ProcessSeasonalTerritorialEvolution();

    UFUNCTION(BlueprintCallable, Category = "Seasonal")
    void ApplyConvoyRouteModifications(int32 TerritoryId);

    // Performance Optimization
    UFUNCTION(BlueprintCallable, Category = "Performance")
    void UpdateTerritorialLOD(const FVector& ViewerLocation, float MaxDistance);

    UFUNCTION(BlueprintCallable, Category = "Performance")
    void OptimizeTerritorialAssets(int32 MaxVisibleAssets);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnTerritorialProcGenerationStarted OnTerritorialProcGenerationStarted;

    UPROPERTY(BlueprintAssignable, Category = "Events") 
    FOnTerritorialProcGenerationComplete OnTerritorialProcGenerationComplete;

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnTerritorialAssetsRequested OnTerritorialAssetsRequested;

protected:
    // Core system references
    UPROPERTY()
    UTGTerritorialManager* TerritorialManager;

    UPROPERTY() 
    ATGProceduralArena* ProceduralArena;

    // Territorial modification state
    UPROPERTY()
    TMap<int32, FTGTerritorialModification> TerritorialModifications;

    // Faction asset libraries
    UPROPERTY(EditAnywhere, Category = "Faction Assets")
    TMap<int32, FTGFactionAssetLibrary> FactionAssetLibraries;

    // Performance settings
    UPROPERTY(EditAnywhere, Category = "Performance")
    float TerritorialUpdateInterval = 1.0f;

    UPROPERTY(EditAnywhere, Category = "Performance")
    float AssetGenerationCooldown = 5.0f;

    UPROPERTY(EditAnywhere, Category = "Performance")
    int32 MaxConcurrentModifications = 3;

    UPROPERTY(EditAnywhere, Category = "Performance")
    int32 MaxTerritorialAssetsPerTerritory = 20;

    // Competitive balance constraints  
    UPROPERTY(EditAnywhere, Category = "Balance")
    float MinDistanceFromCaptureNodes = 500.0f;

    UPROPERTY(EditAnywhere, Category = "Balance")
    float MinDistanceFromExtractionPads = 750.0f;

    UPROPERTY(EditAnywhere, Category = "Balance")
    float MaxSightlineBlockagePercentage = 15.0f;

    UPROPERTY(EditAnywhere, Category = "Balance")
    TArray<FVector> ProtectedGameplayAreas;

private:
    // Timer handles for periodic updates
    FTimerHandle TerritorialUpdateTimer;
    FTimerHandle AssetGenerationTimer;
    FTimerHandle PerformanceOptimizationTimer;

    // Asset generation tracking
    TMap<int32, FDateTime> LastAssetGenerationTime;
    TArray<int32> PendingAssetGeneration;

    // WebSocket integration
    class UTGWebSocketClient* TerritorialWebSocket;

    // Thread safety
    mutable FCriticalSection TerritorialModificationMutex;

    // Internal methods
    void InitializeFactionAssetLibraries();
    void RegisterTerritorialEvents();
    void ProcessPendingModifications();
    bool CanPlaceAssetAtLocation(const FVector& Location, ETGTerritorialModificationType ModType);
    void ClearTerritorialAssets(int32 TerritoryId);
    void ApplyFactionStyling(AActor* Asset, int32 FactionId);
    FVector FindOptimalPlacementLocation(int32 TerritoryId, ETGTerritorialModificationType ModType);

    // Spatial algorithms
    bool IsLocationInProtectedArea(const FVector& Location);
    float CalculateSightlineImpact(const FVector& Location, const FVector& AssetBounds);
    TArray<FVector> FilterValidLocations(const TArray<FVector>& Candidates, ETGTerritorialModificationType ModType);

    // Asset generation pipeline integration
    void TriggerAssetGeneration(int32 TerritoryId, int32 FactionId, const FString& AssetType);
    bool LoadGeneratedAssets(const TArray<FString>& AssetPaths, int32 TerritoryId);
    void ApplyGeneratedAssetsToTerritory(int32 TerritoryId, const TArray<UStaticMesh*>& GeneratedMeshes);
};