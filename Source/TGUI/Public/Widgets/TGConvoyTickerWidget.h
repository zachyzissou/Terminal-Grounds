#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGConvoyTickerWidget.generated.h"

class UTGConvoyEconomySubsystem;

UCLASS(BlueprintType)
class TGUI_API UTGConvoyTickerWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, Category="Convoy")
    float IntegrityIndex = 0.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Convoy")
    FName RouteIdFilter;

    UFUNCTION(BlueprintImplementableEvent, Category="Convoy")
    void OnIntegrityIndexUpdated(float NewIndex, float Delta);

protected:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;

private:
    UFUNCTION()
    void HandleIntegrityChanged(float NewIndex, float Delta);

    TWeakObjectPtr<UTGConvoyEconomySubsystem> ConvoySubsystem;
};
