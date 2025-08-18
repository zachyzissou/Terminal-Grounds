using UnrealBuildTool;

public class TGCombat : ModuleRules
{
    public TGCombat(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "GameplayTags" });

        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
