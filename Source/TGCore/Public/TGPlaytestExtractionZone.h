#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "TGPlaytestExtractionZone.generated.h"

class ATGPlayPawn;
class ATGPlaytestGameMode;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPlayerEnteredZone, ATGPlayPawn*, Player);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPlayerExitedZone, ATGPlayPawn*, Player);

UCLASS(BlueprintType)
class TGCORE_API ATGPlaytestExtractionZone : public AActor
{
    GENERATED_BODY()
    
public:    
    ATGPlaytestExtractionZone();

protected:
    virtual void BeginPlay() override;

    // Components
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UBoxComponent* ExtractionZone;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UStaticMeshComponent* ZoneMesh;

    // Extraction Properties
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    bool bRequiresAllEnemiesDead = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Extraction")
    bool bShowDebugMessages = true;

    // State
    UPROPERTY(BlueprintReadOnly, Category = "Extraction")
    bool bPlayerInZone = false;

    UPROPERTY(BlueprintReadOnly, Category = "Extraction")
    TObjectPtr<ATGPlayPawn> PlayerInZone = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "Extraction")
    TObjectPtr<ATGPlaytestGameMode> PlaytestGameMode = nullptr;

    // Functions
    UFUNCTION()
    void OnExtractionZoneBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

    UFUNCTION()
    void OnExtractionZoneEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

public:    
    virtual void Tick(float DeltaTime) override;

    // Public Interface
    UFUNCTION(BlueprintPure, Category = "Extraction")
    bool IsPlayerInZone() const { return bPlayerInZone; }

    UFUNCTION(BlueprintPure, Category = "Extraction")
    ATGPlayPawn* GetPlayerInZone() const { return PlayerInZone; }

    UFUNCTION(BlueprintCallable, Category = "Extraction")
    void SetExtractionEnabled(bool bEnabled);

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Extraction Events")
    FOnPlayerEnteredZone OnPlayerEnteredZone;

    UPROPERTY(BlueprintAssignable, Category = "Extraction Events")
    FOnPlayerExitedZone OnPlayerExitedZone;

    // Blueprint Events
    UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
    void OnPlayerEntered(ATGPlayPawn* Player);

    UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
    void OnPlayerExited(ATGPlayPawn* Player);

    UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
    void OnZoneActivated();

    UFUNCTION(BlueprintImplementableEvent, Category = "Extraction")
    void OnZoneDeactivated();

private:
    void FindPlaytestGameMode();
    void UpdateZoneState();
};