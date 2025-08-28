using UnrealBuildTool;

public class TGWorld : ModuleRules
{
    public TGWorld(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });

        PrivateDependencyModuleNames.AddRange(new string[] { 
            "Json",
            "JsonUtilities", 
            "HTTP",
            "Sockets",
            "Networking"
        });
    }
}
