using UnrealBuildTool;

public class TGCore : ModuleRules
{
    public TGCore(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core", 
            "CoreUObject", 
            "Engine", 
            "DeveloperSettings", 
            "GameplayTags", 
            "EnhancedInput", 
            "TGTerritorial",
            "TGWorld",
            "RenderCore",
            "RHI"
        });
        PrivateDependencyModuleNames.AddRange(new string[] { 
            "Slate",
            "SlateCore",
            "UnrealEd",
            "ToolMenus",
            "EditorStyle",
            "EditorWidgets",
            "PropertyEditor",
            "BlueprintGraph",
            "KismetCompiler",
            "NavigationSystem"
        });
    }
}
