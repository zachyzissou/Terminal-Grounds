// Copyright Terminal Grounds. All Rights Reserved.

using UnrealBuildTool;

public class TGTerritorial : ModuleRules
{
    public TGTerritorial(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicIncludePaths.AddRange(
            new string[] {
            }
        );

        PrivateIncludePaths.AddRange(
            new string[] {
            }
        );

        PublicDependencyModuleNames.AddRange(
            new string[] {
                "Core",
                "CoreUObject",
                "Engine",
                "UnrealEd",
                "Json",
                "JsonUtilities",
                "HTTP",
                "TGNet",
                "TGAI",
                "TGCore"
            }
        );
        
        PublicIncludePathModuleNames.AddRange(new string[] { "TGWorld" });

        PrivateDependencyModuleNames.AddRange(
            new string[] {
                "Slate",
                "SlateCore",
                "EditorStyle",
                "EditorWidgets",
                "UnrealEd",
                "ToolMenus",
                "PropertyEditor",
                "RenderCore",
                "RHI"
            }
        );

        DynamicallyLoadedModuleNames.AddRange(
            new string[] {
            }
        );

        // Enable PostgreSQL integration (will require custom plugin or third-party solution)
        PublicDefinitions.Add("WITH_POSTGRESQL=1");
        
        // Enable Redis integration
        PublicDefinitions.Add("WITH_REDIS=1");
        
        // Territorial system compile-time configuration
        PublicDefinitions.Add("TERRITORIAL_DEBUG=1");
        PublicDefinitions.Add("TERRITORIAL_MAX_FACTIONS=7");
        PublicDefinitions.Add("TERRITORIAL_MAX_REGIONS=8");
    }
}