using UnrealBuildTool;

public class TGAttachments : ModuleRules
{
    public TGAttachments(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "GameplayAbilities", "GameplayTags", "GameplayTasks" });
    }
}
