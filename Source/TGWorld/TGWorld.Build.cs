using UnrealBuildTool;

public class TGWorld : ModuleRules
{
    public TGWorld(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
        
        PublicIncludePathModuleNames.AddRange(new string[] { "TGTerritorial" });

        PrivateDependencyModuleNames.AddRange(new string[] { 
            "Json",
            "JsonUtilities", 
            "HTTP",
            "Sockets",
            "Networking",
            "Landscape",
            "Foliage",
            "ProceduralMeshComponent"
        });
    }
}
