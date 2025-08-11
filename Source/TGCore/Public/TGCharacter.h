#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TGCharacter.generated.h"

UCLASS()
class TGCORE_API ATGCharacter : public ACharacter
{
	GENERATED_BODY()
public:
	ATGCharacter();
protected:
	virtual void BeginPlay() override;
};
