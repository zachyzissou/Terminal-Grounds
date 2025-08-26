#include "Widgets/TGTrustMeterWidget.h"
#include "Trust/TGTrustSubsystem.h"
#include "Engine/World.h"

void UTGTrustMeterWidget::NativeConstruct()
{
    Super::NativeConstruct();
    if (UWorld* World = GetWorld())
    {
        if (UTGTrustSubsystem* Trust = World->GetGameInstance() ? World->GetGameInstance()->GetSubsystem<UTGTrustSubsystem>() : nullptr)
        {
            TrustSubsystem = Trust;
            Trust->OnTrustChanged.AddDynamic(this, &UTGTrustMeterWidget::HandleTrustChanged);
            TrustIndex = Trust->GetTrustIndex(PlayerA, PlayerB);
            OnTrustUpdated(TrustIndex);
        }
    }
}

void UTGTrustMeterWidget::NativeDestruct()
{
    if (TrustSubsystem.IsValid())
    {
        TrustSubsystem->OnTrustChanged.RemoveDynamic(this, &UTGTrustMeterWidget::HandleTrustChanged);
    }
    Super::NativeDestruct();
}

void UTGTrustMeterWidget::HandleTrustChanged(const FString& A, const FString& B, float NewTrust)
{
    if ((A == PlayerA && B == PlayerB) || (A == PlayerB && B == PlayerA))
    {
        TrustIndex = NewTrust;
        OnTrustUpdated(NewTrust);
    }
}
