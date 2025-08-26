using UnrealBuildTool;

public class TGMissions : ModuleRules
{
    public TGMissions(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "GameplayTags" });

    // Access Codex (TGCore) and Convoy Economy (TGWorld) subsystems from Splice implementation
    PrivateDependencyModuleNames.AddRange(new string[] { "TGCore", "TGWorld" });
    }
}
