using UnrealBuildTool;

public class TGCore : ModuleRules
{
    public TGCore(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "DeveloperSettings", "EnhancedInput" });
        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
