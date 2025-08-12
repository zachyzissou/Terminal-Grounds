using UnrealBuildTool;
using System.Collections.Generic;

public class TerminalGroundsEditorTarget : TargetRules
{
    public TerminalGroundsEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
        ExtraModuleNames.AddRange(new string[] {
            "TGCore","TGNet","TGCombat","TGLoot","TGWorld","TGAI","TGMissions","TGBase","TGVehicles","TGUI","TGServer"
        });
    }
}
