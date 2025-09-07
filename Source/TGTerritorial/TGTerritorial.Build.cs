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
                "Json",
                "JsonUtilities",
                "HTTP",
                "TGNet",
                "TGCore"
            }
        );
        
        // Forward declarations for other TG modules (avoid circular dependencies)
        PublicIncludePathModuleNames.AddRange(new string[] { "TGAI" });
        
        PublicIncludePathModuleNames.AddRange(new string[] { "TGWorld" });

        PrivateDependencyModuleNames.AddRange(
            new string[] {
                "Slate",
                "SlateCore",
                "RenderCore",
                "RHI"
            }
        );
        
        // Editor-only dependencies
        if (Target.bBuildEditor)
        {
            PrivateDependencyModuleNames.AddRange(
                new string[] {
                    "UnrealEd",
                    "EditorStyle",
                    "EditorWidgets",
                    "ToolMenus",
                    "PropertyEditor"
                }
            );
        }

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