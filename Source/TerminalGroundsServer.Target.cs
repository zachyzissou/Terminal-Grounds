using UnrealBuildTool;
using System.Collections.Generic;

public class TerminalGroundsServerTarget : TargetRules
{
    public TerminalGroundsServerTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Server;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
        bUsesSteam = false;
        bUseLoggingInShipping = true;
        ExtraModuleNames.AddRange(new string[] {
            "TGCore","TGNet","TGCombat","TGLoot","TGWorld","TGAI","TGMissions","TGBase","TGVehicles","TGUI","TGServer"
        });
    }
}
