#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix plugin compilation issues for UE 5.5+
"""

import os
import json
import shutil

def fix_plugins():
    """Fix common plugin compilation issues"""
    
    print("Fixing Plugin Compilation Issues for UE 5.5+")
    print("=" * 60)
    
    # 1. Remove duplicate UnrealMCP folder
    duplicate_path = "Plugins/UnrealMCP/UnrealMCP"
    if os.path.exists(duplicate_path):
        print(f"[FIX] Removing duplicate folder: {duplicate_path}")
        try:
            shutil.rmtree(duplicate_path)
            print("  -> Duplicate removed")
        except Exception as e:
            print(f"  -> Could not remove: {e}")
    
    # 2. Clean intermediate and binary directories
    plugins_to_clean = [
        "Plugins/ProceduralDungeon",
        "Plugins/StreetMap",
        "Plugins/UnrealMCP"
    ]
    
    print("\n[CLEAN] Removing old build artifacts...")
    for plugin in plugins_to_clean:
        for folder in ["Intermediate", "Binaries"]:
            path = os.path.join(plugin, folder)
            if os.path.exists(path):
                print(f"  Cleaning {path}")
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"    -> Error: {e}")
    
    # 3. Verify .uplugin files
    print("\n[VERIFY] Checking plugin configurations...")
    plugin_files = [
        "Plugins/ProceduralDungeon/ProceduralDungeon.uplugin",
        "Plugins/StreetMap/StreetMap.uplugin",
        "Plugins/UnrealMCP/UnrealMCP.uplugin"
    ]
    
    for plugin_file in plugin_files:
        if os.path.exists(plugin_file):
            print(f"  Checking {plugin_file}")
            try:
                with open(plugin_file, 'r') as f:
                    data = json.load(f)
                
                # Ensure proper settings
                data["Installed"] = True
                if "EngineVersion" not in data:
                    data["EngineVersion"] = "5.5"
                
                # Fix module platform lists
                if "Modules" in data:
                    for module in data["Modules"]:
                        if "WhitelistPlatforms" in module:
                            module["PlatformAllowList"] = module.pop("WhitelistPlatforms")
                        elif "BlacklistPlatforms" in module:
                            module["PlatformDenyList"] = module.pop("BlacklistPlatforms")
                
                # Write back
                with open(plugin_file, 'w') as f:
                    json.dump(data, f, indent='\t')
                
                print(f"    -> Fixed: {os.path.basename(plugin_file)}")
                
            except Exception as e:
                print(f"    -> Error: {e}")
    
    # 4. Generate project files
    print("\n[SOLUTION] Steps to complete the fix:")
    print("  1. Close Unreal Editor if it's running")
    print("  2. Right-click TerminalGrounds.uproject")
    print("  3. Select 'Generate Visual Studio project files'")
    print("  4. Open the project in Unreal Editor")
    print("  5. When prompted about missing modules, click 'Yes' to rebuild")
    print("\n[PLUGINS TO ENABLE]")
    print("  - ProceduralDungeon")
    print("  - StreetMap")  
    print("  - UnrealMCP")
    print("\nIf compilation still fails:")
    print("  - Check the Output Log in Unreal for specific errors")
    print("  - Disable problematic plugins temporarily")
    print("  - Update plugin code for UE 5.5 API changes if needed")
    
    print("\n" + "=" * 60)
    print("Plugin fixes applied!")
    
if __name__ == "__main__":
    fix_plugins()