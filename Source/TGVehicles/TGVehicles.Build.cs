using UnrealBuildTool;

public class TGVehicles : ModuleRules
{
    public TGVehicles(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "ChaosVehicles" });
    }
}
