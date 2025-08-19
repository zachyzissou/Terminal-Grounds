using UnrealBuildTool;

public class TGInterfaces : ModuleRules
{
    public TGInterfaces(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core", 
            "CoreUObject", 
            "Engine" 
        });
        
        // This module provides interfaces only - no implementations
        PrivateDependencyModuleNames.AddRange(new string[] { });
        
        // Interface module should be available to all other modules
        PublicIncludePaths.AddRange(new string[] {
            "TGInterfaces/Public"
        });
    }
}