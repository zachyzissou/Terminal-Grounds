#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Engine/World.h"
#include "HAL/Platform.h"
#include "Stats/StatsData.h"
#include "TGPerformanceOptimizer.generated.h"

class UTGPerformanceProfiler;
class UTGProceduralArena;
class UTGTerritorialManager;
class UGameViewportClient;

UENUM(BlueprintType)
enum class ETGOptimizationLevel : uint8
{
    None = 0,
    Conservative = 1,
    Aggressive = 2,
    Emergency = 3
};

UENUM(BlueprintType)
enum class ETGOptimizationStrategy : uint8
{
    Safe = 0,
    Bold = 1,
    Experimental = 2
};

USTRUCT(BlueprintType)
struct FTGPerformanceOptimization
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    FString OptimizationName;

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    ETGOptimizationLevel Level;

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    ETGOptimizationStrategy Strategy;

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    float ExpectedFPSImprovement;

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    float ExpectedMemoryReduction;

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    FDateTime AppliedAt;

    UPROPERTY(BlueprintReadOnly, Category = "Optimization")
    bool bRequiresRestart;

    FTGPerformanceOptimization()
    {
        OptimizationName = TEXT("");
        Level = ETGOptimizationLevel::None;
        Strategy = ETGOptimizationStrategy::Safe;
        ExpectedFPSImprovement = 0.0f;
        ExpectedMemoryReduction = 0.0f;
        AppliedAt = FDateTime::MinValue();
        bRequiresRestart = false;
    }
};

USTRUCT(BlueprintType)
struct FTGAssetOptimizationResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Asset Optimization")
    FString AssetPath;

    UPROPERTY(BlueprintReadOnly, Category = "Asset Optimization")
    int32 OriginalMemoryMB;

    UPROPERTY(BlueprintReadOnly, Category = "Asset Optimization")
    int32 OptimizedMemoryMB;

    UPROPERTY(BlueprintReadOnly, Category = "Asset Optimization")
    float MemoryReduction;

    UPROPERTY(BlueprintReadOnly, Category = "Asset Optimization")
    bool bSuccess;

    FTGAssetOptimizationResult()
    {
        AssetPath = TEXT("");
        OriginalMemoryMB = 0;
        OptimizedMemoryMB = 0;
        MemoryReduction = 0.0f;
        bSuccess = false;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnOptimizationApplied, const FTGPerformanceOptimization&, Optimization);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAssetOptimized, const FTGAssetOptimizationResult&, Result);

UCLASS(BlueprintType, Blueprintable)
class TGCORE_API UTGPerformanceOptimizer : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    UTGPerformanceOptimizer();

    // Subsystem overrides
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // Main optimization interface
    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void ApplyOptimizationStrategy(ETGOptimizationStrategy Strategy);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeForTargetFPS(float TargetFPS);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeForMemoryTarget(float MaxMemoryMB);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeForPlayerCount(int32 PlayerCount);

    // Specific optimization categories
    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeProcGen(ETGOptimizationLevel Level);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeTerritorialSystem(ETGOptimizationLevel Level);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeAssetGeneration(ETGOptimizationLevel Level);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeNetworking(ETGOptimizationLevel Level);

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void OptimizeRendering(ETGOptimizationLevel Level);

    // Asset-specific optimizations
    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    TArray<FTGAssetOptimizationResult> OptimizeAssetMemoryUsage();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    bool OptimizeTextureStreaming();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    bool OptimizeMeshLODs();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    bool OptimizeShaderCompilation();

    // Emergency optimizations
    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void EmergencyOptimization();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void RevertOptimizations();

    // Monitoring and analysis
    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    void AnalyzePerformanceBottlenecks();

    UFUNCTION(BlueprintCallable, Category = "Performance Optimization")
    TArray<FString> GetOptimizationRecommendations() const;

    UFUNCTION(BlueprintPure, Category = "Performance Optimization")
    TArray<FTGPerformanceOptimization> GetAppliedOptimizations() const;

    UFUNCTION(BlueprintPure, Category = "Performance Optimization")
    bool IsOptimizationActive(const FString& OptimizationName) const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Performance Optimization")
    FOnOptimizationApplied OnOptimizationApplied;

    UPROPERTY(BlueprintAssignable, Category = "Performance Optimization") 
    FOnAssetOptimized OnAssetOptimized;

protected:
    // Internal optimization methods - Safe Strategy
    void ApplySafeRenderingOptimizations();
    void ApplySafeProcGenOptimizations(); 
    void ApplySafeNetworkingOptimizations();
    void ApplySafeAssetOptimizations();
    void ApplySafeTerritorialOptimizations();

    // Internal optimization methods - Bold Strategy
    void ApplyBoldRenderingOptimizations();
    void ApplyBoldProcGenOptimizations();
    void ApplyBoldNetworkingOptimizations(); 
    void ApplyBoldAssetOptimizations();
    void ApplyBoldTerritorialOptimizations();

    // Internal optimization methods - Experimental Strategy
    void ApplyExperimentalRenderingOptimizations();
    void ApplyExperimentalProcGenOptimizations();
    void ApplyExperimentalNetworkingOptimizations();
    void ApplyExperimentalAssetOptimizations();
    void ApplyExperimentalTerritorialOptimizations();

    // Specific optimization implementations
    void OptimizeLODDistances(ETGOptimizationLevel Level);
    void OptimizeShadowSettings(ETGOptimizationLevel Level);
    void OptimizePostProcessing(ETGOptimizationLevel Level);
    void OptimizeLightingQuality(ETGOptimizationLevel Level);
    void OptimizeTextureQuality(ETGOptimizationLevel Level);
    void OptimizeParticleEffects(ETGOptimizationLevel Level);

    // Procedural generation optimizations
    void OptimizeProcGenChunkSize(ETGOptimizationLevel Level);
    void OptimizeProcGenUpdateFrequency(ETGOptimizationLevel Level);
    void OptimizeProcGenMemoryFootprint(ETGOptimizationLevel Level);
    void OptimizeNavMeshGeneration(ETGOptimizationLevel Level);

    // Networking optimizations
    void OptimizeReplicationFrequency(ETGOptimizationLevel Level);
    void OptimizeNetworkCulling(ETGOptimizationLevel Level);
    void OptimizePacketSizes(ETGOptimizationLevel Level);
    void OptimizeTerritorialUpdates(ETGOptimizationLevel Level);

    // Memory management
    void OptimizeGarbageCollection(ETGOptimizationLevel Level);
    void OptimizeObjectPooling(ETGOptimizationLevel Level);
    void OptimizeStreamingDistances(ETGOptimizationLevel Level);
    void FlushUnusedAssets();

    // Analysis and monitoring
    void AnalyzeRenderingBottlenecks();
    void AnalyzeMemoryBottlenecks();
    void AnalyzeNetworkBottlenecks();
    void AnalyzeProcGenBottlenecks();
    void AnalyzeTerritorialBottlenecks();

    // Utility methods
    void RecordOptimization(const FString& Name, ETGOptimizationLevel Level, ETGOptimizationStrategy Strategy, float ExpectedFPSGain, float ExpectedMemorySaving, bool bRequiresRestart = false);
    bool CanApplyOptimization(const FString& OptimizationName) const;
    void NotifyOptimizationApplied(const FTGPerformanceOptimization& Optimization);

private:
    // Component references
    UPROPERTY()
    UTGPerformanceProfiler* BoundProfiler;

    UPROPERTY()
    UTGProceduralArena* ProceduralArena;

    UPROPERTY()
    UTGTerritorialManager* TerritorialManager;

    // Optimization tracking
    UPROPERTY()
    TArray<FTGPerformanceOptimization> AppliedOptimizations;

    UPROPERTY()
    TArray<FString> OptimizationRecommendations;

    // Performance targets
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets", meta = (AllowPrivateAccess = "true"))
    float TargetFPS;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets", meta = (AllowPrivateAccess = "true"))
    float MaxMemoryUsageMB;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets", meta = (AllowPrivateAccess = "true"))
    float MaxNetworkLatency;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance Targets", meta = (AllowPrivateAccess = "true"))
    int32 MaxConcurrentPlayers;

    // Optimization settings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Optimization Settings", meta = (AllowPrivateAccess = "true"))
    bool bEnableAutomaticOptimization;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Optimization Settings", meta = (AllowPrivateAccess = "true"))
    bool bEnableExperimentalOptimizations;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Optimization Settings", meta = (AllowPrivateAccess = "true"))
    ETGOptimizationStrategy DefaultOptimizationStrategy;

    // Internal state
    bool bInitialized;
    float LastOptimizationTime;
    ETGOptimizationLevel CurrentOptimizationLevel;
    
    // Console variable storage for reversion
    TMap<FString, FString> OriginalConsoleValues;
    
    // Performance baseline measurements
    float BaselineFPS;
    float BaselineMemoryMB;
    float BaselineLatency;
};