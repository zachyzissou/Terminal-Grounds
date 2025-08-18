using UnrealBuildTool;

public class TGAI : ModuleRules
{
    public TGAI(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "AIModule" });

        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
