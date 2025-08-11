#pragma once
#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "TGGameSettings.generated.h"

UCLASS(Config=TerminalGrounds, DefaultConfig, meta=(DisplayName="TG Game Settings"))
class TGCORE_API UTGGameSettings : public UDeveloperSettings
{
	GENERATED_BODY()
public:
	UTGGameSettings();

	// General tuning scalars
	UPROPERTY(EditAnywhere, Config, Category="Combat")
	float RecoilScale = 1.0f;

	UPROPERTY(EditAnywhere, Config, Category="Combat")
	float DamageScale = 1.0f;

	UPROPERTY(EditAnywhere, Config, Category="Movement")
	float MovementSpeedScale = 1.0f;

	// Helper to fetch settings quickly
	static const UTGGameSettings* Get();
};
