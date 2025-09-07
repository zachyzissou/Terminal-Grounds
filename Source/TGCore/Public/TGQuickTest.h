#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

// Simple static functions that can be called from console
class TGCORE_API UTGQuickTest
{
public:
    // Simple procedural test that should work
    static void SpawnBasicCubes(UWorld* World, int32 Count = 10);
    
    // Test the procedural subsystem directly
    static void TestProceduralSubsystem(UWorld* World);
};