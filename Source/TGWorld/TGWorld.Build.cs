using UnrealBuildTool;

public class TGWorld : ModuleRules
{
    public TGWorld(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
        
        PublicDependencyModuleNames.AddRange(new string[] { "TGCore" });

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
