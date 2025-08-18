using UnrealBuildTool;

public class TGMissions : ModuleRules
{
    public TGMissions(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "GameplayTags" });

        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
