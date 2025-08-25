#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"
#include "Subsystems/WorldSubsystem.h"
#include "Components/ActorComponent.h"
#include "Engine/DataTable.h"
#include "TGTerritorialManager.generated.h"

// Forward declarations
class ATGTerritoryZone;
class ATGControlStructure;
struct FTGFactionData;

USTRUCT(BlueprintType)
struct TGWORLD_API FTGTerritorialBounds
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    TArray<FVector2D> BoundaryPoints;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FVector2D CenterPoint;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    float InfluenceRadius;

    FTGTerritorialBounds()
    {
        CenterPoint = FVector2D::ZeroVector;
        InfluenceRadius = 1000.0f;
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FTGFactionInfluence
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    int32 FactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Faction")
    FString FactionName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 InfluenceLevel; // 0-100

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 ControlPoints;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FDateTime LastActionTime;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FString InfluenceTrend; // "growing", "declining", "stable"

    FTGFactionInfluence()
    {
        FactionId = 0;
        InfluenceLevel = 0;
        ControlPoints = 0;
        LastActionTime = FDateTime::Now();
        InfluenceTrend = TEXT("stable");
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FTGTerritoryData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 TerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FString TerritoryName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FString TerritoryType; // region, district, zone, outpost

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 ParentTerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FTGTerritorialBounds Bounds;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 CurrentControllerFactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    bool bContested;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 StrategicValue; // 1-10

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    float ResourceMultiplier;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    TArray<FTGFactionInfluence> FactionInfluences;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FDateTime LastContestedTime;

    FTGTerritoryData()
    {
        TerritoryId = 0;
        ParentTerritoryId = 0;
        CurrentControllerFactionId = 0;
        bContested = false;
        StrategicValue = 1;
        ResourceMultiplier = 1.0f;
        LastContestedTime = FDateTime::Now();
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTerritoryControlChanged, int32, TerritoryId, int32, OldControllerFactionId, int32, NewControllerFactionId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTerritoryContested, int32, TerritoryId, bool, bContested);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnInfluenceChanged, int32, TerritoryId, int32, FactionId, int32, NewInfluenceLevel);

/**
 * World Subsystem for managing territorial control and faction influence
 * Integrates with PostgreSQL backend via TGServer module
 * Provides real-time territorial updates via TGNet WebSocket system
 */
UCLASS(BlueprintType, Blueprintable)
class TGWORLD_API UTGTerritorialManager : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    UTGTerritorialManager();

    // UWorldSubsystem interface
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;

    // Territory Management - C++ Performance Critical
    UFUNCTION(BlueprintCallable, Category = "Territory")
    bool InitializeTerritorialSystem();

    UFUNCTION(BlueprintCallable, Category = "Territory")
    FTGTerritoryData GetTerritoryData(int32 TerritoryId);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    TArray<FTGTerritoryData> GetAllTerritories();

    UFUNCTION(BlueprintCallable, Category = "Territory")
    TArray<FTGTerritoryData> GetTerritoriesInRadius(FVector2D CenterPoint, float Radius);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    int32 GetControllingFaction(int32 TerritoryId);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    bool IsTerritoryContested(int32 TerritoryId);

    // Influence System - C++ Core with Blueprint Access
    UFUNCTION(BlueprintCallable, Category = "Territory")
    bool UpdateFactionInfluence(int32 TerritoryId, int32 FactionId, int32 InfluenceChange);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    int32 GetFactionInfluence(int32 TerritoryId, int32 FactionId);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    TArray<FTGFactionInfluence> GetTerritoryInfluences(int32 TerritoryId);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    bool AttemptTerritoryCapture(int32 TerritoryId, int32 AttackingFactionId);

    // Spatial Queries - Performance Critical C++
    UFUNCTION(BlueprintCallable, Category = "Territory")
    int32 GetTerritoryAtLocation(FVector2D WorldLocation);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    bool IsLocationInTerritory(FVector2D WorldLocation, int32 TerritoryId);

    UFUNCTION(BlueprintCallable, Category = "Territory")
    float GetDistanceToTerritoryBorder(FVector2D WorldLocation, int32 TerritoryId);

    // Real-time Updates - WebSocket Integration
    UFUNCTION(BlueprintCallable, Category = "Network")
    void RequestTerritorialUpdate();

    UFUNCTION(BlueprintCallable, Category = "Network")
    void BroadcastTerritorialChange(int32 TerritoryId, const FString& ChangeType);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Territory Events")
    FOnTerritoryControlChanged OnTerritoryControlChanged;

    UPROPERTY(BlueprintAssignable, Category = "Territory Events")
    FOnTerritoryContested OnTerritoryContested;

    UPROPERTY(BlueprintAssignable, Category = "Territory Events")
    FOnInfluenceChanged OnInfluenceChanged;

protected:
    // Core territorial data cache
    UPROPERTY()
    TMap<int32, FTGTerritoryData> TerritoryCache;

    // Performance optimization
    UPROPERTY()
    TMap<FVector2D, int32> LocationToTerritoryCache;

    // Update frequency control
    UPROPERTY(EditAnywhere, Category = "Performance")
    float TerritorialUpdateFrequency;

    UPROPERTY(EditAnywhere, Category = "Performance")
    float CacheRefreshInterval;

    // Internal state
    float LastUpdateTime;
    float LastCacheRefresh;

    // Database integration
    bool ConnectToTerritorialDatabase();
    void RefreshTerritorialCache();
    void ProcessTerritorialUpdates();

    // Spatial calculations - High performance C++
    bool IsPointInPolygon(const FVector2D& Point, const TArray<FVector2D>& Polygon);
    float CalculateDistanceToPolygon(const FVector2D& Point, const TArray<FVector2D>& Polygon);
    FVector2D GetClosestPointOnPolygon(const FVector2D& Point, const TArray<FVector2D>& Polygon);

private:
    // WebSocket connection for real-time updates
    class UTGWebSocketClient* TerritorialWebSocket;
    
    // Database connection
    class UTGDatabaseClient* TerritorialDatabase;

    // Thread safety
    mutable FCriticalSection TerritorialDataMutex;
};