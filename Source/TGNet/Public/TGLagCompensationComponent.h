#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TGLagCompensationComponent.generated.h"

USTRUCT()
struct FTGCapsuleSample
{
	GENERATED_BODY()
	UPROPERTY() float Time = 0.f;
	UPROPERTY() FVector_NetQuantize10 Location = FVector::ZeroVector;
	UPROPERTY() FRotator Rotation = FRotator::ZeroRotator;
};

UCLASS(ClassGroup=(TG), meta=(BlueprintSpawnableComponent))
class TGNET_API UTGLagCompensationComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UTGLagCompensationComponent();
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// Returns the best sample at or before QueryTime
	bool GetSampleAt(float QueryTime, FTGCapsuleSample& OutSample) const;

private:
	UPROPERTY() TArray<FTGCapsuleSample> Buffer;
	UPROPERTY(EditAnywhere, Category="LagComp") int32 MaxSamples = 64;
};
