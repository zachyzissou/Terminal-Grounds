using UnrealBuildTool;

public class TGUI : ModuleRules
{
    public TGUI(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "UMG", "Slate", "SlateCore", "EnhancedInput", "TGCombat", "TGTerritorial", "TGWorld", "TGCore" });
        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
