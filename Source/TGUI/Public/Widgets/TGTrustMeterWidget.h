#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TGTrustMeterWidget.generated.h"

class UTGTrustSubsystem;

UCLASS(BlueprintType)
class TGUI_API UTGTrustMeterWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Trust")
    FString PlayerA;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Trust")
    FString PlayerB;

    UPROPERTY(BlueprintReadOnly, Category="Trust")
    float TrustIndex = 0.f;

    UFUNCTION(BlueprintImplementableEvent, Category="Trust")
    void OnTrustUpdated(float NewTrust);

protected:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;

private:
    UFUNCTION()
    void HandleTrustChanged(const FString& A, const FString& B, float NewTrust);

    TWeakObjectPtr<UTGTrustSubsystem> TrustSubsystem;
};
