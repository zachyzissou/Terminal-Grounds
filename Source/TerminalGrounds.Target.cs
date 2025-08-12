using UnrealBuildTool;
using System.Collections.Generic;

public class TerminalGroundsTarget : TargetRules
{
    public TerminalGroundsTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
        ExtraModuleNames.AddRange(new string[] {
            "TGCore","TGNet","TGCombat","TGLoot","TGWorld","TGAI","TGMissions","TGBase","TGVehicles","TGUI","TGServer"
        });
    }
}
