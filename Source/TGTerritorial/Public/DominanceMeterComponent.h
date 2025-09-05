#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Net/UnrealNetwork.h"
#include "DominanceMeterComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnDominanceChanged, float, OldDominance, float, NewDominance);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDominanceThresholdReached, float, Threshold);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnDominanceComplete);

/**
 * Dominance Meter Component
 * Tracks territorial control progress from 0.0 (defenders) to 1.0 (attackers)
 * Server-authoritative with client replication and interpolation
 */
UCLASS(ClassGroup=(TG), meta=(BlueprintSpawnableComponent))
class TGTERRITORIAL_API UDominanceMeterComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UDominanceMeterComponent();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnDominanceChanged OnDominanceChanged;

    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnDominanceThresholdReached OnDominanceThresholdReached;

    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnDominanceComplete OnDominanceComplete;

    // Dominance Management
    UFUNCTION(BlueprintCallable, Category = "Siege|Dominance", BlueprintAuthorityOnly)
    void AddDominanceDelta(float Delta);

    UFUNCTION(BlueprintCallable, Category = "Siege|Dominance", BlueprintAuthorityOnly)
    void SetDominance(float NewDominance);

    UFUNCTION(BlueprintPure, Category = "Siege|Dominance")
    float GetDominance() const { return CurrentDominance; }

    UFUNCTION(BlueprintPure, Category = "Siege|Dominance")
    float GetDominancePercentage() const { return CurrentDominance * 100.0f; }

    UFUNCTION(BlueprintPure, Category = "Siege|Dominance")
    bool IsAttackerDominant() const { return CurrentDominance > 0.5f; }

    UFUNCTION(BlueprintPure, Category = "Siege|Dominance")
    bool IsDominanceComplete() const { return CurrentDominance >= 1.0f || CurrentDominance <= 0.0f; }

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float DominanceDecayRate = 0.01f; // Per second when not contested

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    bool bEnableDecay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    TArray<float> NotificationThresholds = {0.25f, 0.5f, 0.75f, 0.9f};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config", meta = (ClampMin = "0.01"))
    float InterpolationSpeed = 2.0f;

    // Modifiers
    UFUNCTION(BlueprintCallable, Category = "Siege|Modifiers", BlueprintAuthorityOnly)
    void ApplyDominanceModifier(float Multiplier, float Duration);

    UFUNCTION(BlueprintPure, Category = "Siege|Modifiers")
    float GetCurrentModifier() const { return ActiveModifier; }

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(ReplicatedUsing = OnRep_Dominance, BlueprintReadOnly, Category = "Siege|State")
    float CurrentDominance;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege|State")
    float ActiveModifier;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege|State")
    float ModifierEndTime;

    UFUNCTION()
    void OnRep_Dominance(float OldDominance);

private:
    float ClientDisplayDominance;
    TSet<float> TriggeredThresholds;

    void ProcessDecay(float DeltaTime);
    void ProcessModifiers(float DeltaTime);
    void CheckThresholds(float OldValue, float NewValue);
    void InterpolateClientDisplay(float DeltaTime);
};