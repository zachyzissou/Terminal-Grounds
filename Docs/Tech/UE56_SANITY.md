# UE 5.6 sanity checklist

Quick checks to keep Terminal Grounds healthy on UE 5.6.

- Validate engine and project plugins
  - VS Code task: UE: Validate Required Plugins
  - Expected engine set: GameplayAbilities, GameplayTags, Niagara, MovieRenderPipeline, PythonScriptPlugin, EditorScriptingUtilities, WorldPartitionEditor, Water, ControlRig, Fab
  - Expected project set: TGAttachments, TGModKit
  - If GameplayTags or WorldPartitionEditor are missing, Verify the engine in Epic Launcher (UE_5.6)

- Generate files, build, launch
  - UE5.6: Generate Project Files (VSCode)
  - UE5.6: Build Editor (Dev Win64)
  - UE5.6: Launch Editor

- In-editor automation (optional)
  - Tools/Unreal/python/tools_sanity_pass.py inside the Python console
  - Lookdev/Materials/Niagara helpers live in Tools/Unreal/python

Notes

- VS Code is configured for PowerShell with the UE engineRoot setting; tasks use the PowerShell invoke operator to handle spaces in paths.

- If a task prints "C:/Program not recognized", rerun the hardened UE5.6 tasks (they’re quoted and prefixed with &).

- For CI docs, run Docs: Build Asset Manifest and Docs: Run Docs Gate.
