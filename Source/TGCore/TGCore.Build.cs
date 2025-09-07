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
            "UMG",
            "AIModule",
            "NavigationSystem",
            "RenderCore",
            "RHI"
        });
        
        // Forward declarations for other TG modules (avoid circular dependencies)
        PublicIncludePathModuleNames.AddRange(new string[] { 
            "TGTerritorial",
            "TGWorld",
            "TGCombat",
            "TGAI"
        });
        PrivateDependencyModuleNames.AddRange(new string[] { 
            "Slate",
            "SlateCore"
        });
        
        // Editor-only dependencies
        if (Target.bBuildEditor)
        {
            PrivateDependencyModuleNames.AddRange(new string[] { 
                "UnrealEd",
                "ToolMenus",
                "EditorStyle",
                "EditorWidgets",
                "PropertyEditor",
                "BlueprintGraph",
                "KismetCompiler"
            });
        }
    }
}
