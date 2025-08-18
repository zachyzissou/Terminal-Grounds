using UnrealBuildTool;

public class TGNet : ModuleRules
{
    public TGNet(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "NetCore" });

        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
