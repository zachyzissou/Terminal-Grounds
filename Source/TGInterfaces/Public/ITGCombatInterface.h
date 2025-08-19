#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "ITGCombatInterface.generated.h"

UINTERFACE(MinimalAPI, Blueprintable)
class UTGCombatInterface : public UInterface
{
    GENERATED_BODY()
};

class TGINTERFACES_API ITGCombatInterface
{
    GENERATED_BODY()

public:
    // Thermal system interface
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    float GetCurrentHeat() const;
    
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    float GetMaxHeat() const;
    
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    bool IsOverheated() const;
    
    // Charge system interface
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    float GetCurrentCharge() const;
    
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    float GetMaxCharge() const;
    
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    float GetChargePercent() const;
    
    // Exosuit interface
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    bool HasExosuit() const;
    
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    FName GetExosuitType() const;
    
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "TG|Combat")
    int32 GetAugmentSlotCount() const;
};