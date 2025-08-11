#include "TGLagCompensationComponent.h"
#include "GameFramework/Actor.h"

UTGLagCompensationComponent::UTGLagCompensationComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UTGLagCompensationComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (AActor* Owner = GetOwner())
	{
		FTGCapsuleSample S; S.Time = GetWorld()->GetTimeSeconds(); S.Location = Owner->GetActorLocation(); S.Rotation = Owner->GetActorRotation();
		Buffer.Add(S);
		if (Buffer.Num() > MaxSamples)
		{
			Buffer.RemoveAt(0, Buffer.Num() - MaxSamples);
		}
	}
}

bool UTGLagCompensationComponent::GetSampleAt(float QueryTime, FTGCapsuleSample& OutSample) const
{
	for (int32 i = Buffer.Num()-1; i >= 0; --i)
	{
		if (Buffer[i].Time <= QueryTime)
		{
			OutSample = Buffer[i];
			return true;
		}
	}
	return false;
}
