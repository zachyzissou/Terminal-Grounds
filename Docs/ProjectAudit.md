# UE5.6 Project Audit — Terminal Grounds

Date: 2025-08-12

## Summary

This document tracks configuration and dependency adjustments to align the project with Epic's UE 5.6 guidance for rendering, input, plugins, and build dependencies.

## Changes

1. Plugins — TerminalGrounds.uproject

- Enabled: GameplayTags, TGAttachments, EnhancedInput. Rationale: Runtime modules are required by code and DefaultInput.ini. Docs: Input system — Enhanced Input (UE 5.3+): <https://docs.unrealengine.com/5.3/en-US/enhanced-input-in-unreal-engine/>
- Enabled (Editor only): GameplayTagsEditor, WorldPartitionEditor for authoring. Docs: Gameplay Tags Editor UI.

2. Rendering defaults — Config/DefaultEngine.ini

- Enabled Lumen GI/Reflections, Nanite, Virtual Shadow Maps; set DX12 RHI; disabled RT by default. Docs: Lumen and Nanite setup: <https://docs.unrealengine.com/5.3/en-US/lumen-global-illumination-and-reflections-in-unreal-engine/> , <https://docs.unrealengine.com/5.3/en-US/nanite-in-unreal-engine/>

3. Maps & Modes — Config/DefaultEngine.ini

- Set fallback GameDefaultMap and EditorStartupMap to existing IEZ_District_Alpha. Docs: Project Settings > Maps & Modes.

4. Build dependencies

- TGCore: +EnhancedInput
- TGUI: +Slate, SlateCore, EnhancedInput
- TGServer: +NetCore, Networking
Docs: Module dependencies: <https://docs.unrealengine.com/5.3/en-US/unreal-build-system-in-unreal-engine/>

## Notes

- GameplayAbilities is enabled and referenced by TGAttachments.
- Validate content redirectors via Fix Up Redirectors in Content Browser.
- Packaging and Dedicated Server build should be tested following these updates.

## Next Steps

- Close editor (to disable Live Coding), run a clean Development build, then package Win64 and build -server target. Capture warnings.
- In Editor: enable Show Engine Content & Show Plugin Content, run Validation: Gameplay Tags load and World Partition tools accessible.
