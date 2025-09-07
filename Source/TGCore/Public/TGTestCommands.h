#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "TGTestCommands.generated.h"

/**
 * Developer settings for Terminal Grounds testing
 * Provides console commands for testing Phase 1 and Procedural systems
 */
UCLASS(config = Game, defaultconfig, meta = (DisplayName = "Terminal Grounds Test Commands"))
class TGCORE_API UTGTestCommands : public UDeveloperSettings
{
    GENERATED_BODY()

public:
    UTGTestCommands();

    // Console command implementations
    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_SpawnCompleteTest(const UObject* WorldContext);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_GenerateTerritory(const UObject* WorldContext, int32 TerritoryID = 1, int32 FactionID = 1);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_ClearTerritory(const UObject* WorldContext, int32 TerritoryID = 1);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_SpawnEnemies(const UObject* WorldContext, int32 Count = 5);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_RestartMission(const UObject* WorldContext);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_ShowStatus(const UObject* WorldContext);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_TestDirectorateVsFree77(const UObject* WorldContext);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_TestMultiFaction(const UObject* WorldContext);

    UFUNCTION(Exec, Category = "Terminal Grounds")
    static void TG_Help(const UObject* WorldContext);

private:
    static class UWorld* GetWorldFromContext(const UObject* WorldContext);
};