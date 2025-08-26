#include "Widgets/TGConvoyTickerWidget.h"
#include "Economy/TGConvoyEconomySubsystem.h"
#include "Engine/World.h"

void UTGConvoyTickerWidget::NativeConstruct()
{
    Super::NativeConstruct();
    if (UWorld* World = GetWorld())
    {
        if (UTGConvoyEconomySubsystem* Convoy = World->GetSubsystem<UTGConvoyEconomySubsystem>())
        {
            ConvoySubsystem = Convoy;
            IntegrityIndex = Convoy->GetIntegrityIndex();
            Convoy->OnIntegrityIndexChanged.AddDynamic(this, &UTGConvoyTickerWidget::HandleIntegrityChanged);
        }
    }
}

void UTGConvoyTickerWidget::NativeDestruct()
{
    if (ConvoySubsystem.IsValid())
    {
        ConvoySubsystem->OnIntegrityIndexChanged.RemoveDynamic(this, &UTGConvoyTickerWidget::HandleIntegrityChanged);
    }
    Super::NativeDestruct();
}

void UTGConvoyTickerWidget::HandleIntegrityChanged(float NewIndex, float Delta)
{
    IntegrityIndex = NewIndex;
    OnIntegrityIndexUpdated(NewIndex, Delta);
}
