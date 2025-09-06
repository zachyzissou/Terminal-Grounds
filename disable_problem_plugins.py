#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temporarily disable problematic plugins to allow project to open
"""

import json
import os
import shutil

def disable_plugins():
    """Temporarily disable plugins that are causing compile errors"""
    
    print("Disabling problematic plugins to allow project to open...")
    print("=" * 60)
    
    # Read the uproject file
    uproject_file = "TerminalGrounds.uproject"
    
    with open(uproject_file, 'r') as f:
        project_data = json.load(f)
    
    # Add plugins section if it doesn't exist
    if "Plugins" not in project_data:
        project_data["Plugins"] = []
    
    # Disable the problematic plugins
    plugins_to_disable = ["ProceduralDungeon", "StreetMap", "UnrealMCP"]
    
    for plugin_name in plugins_to_disable:
        # Check if plugin is already in the list
        plugin_found = False
        for plugin in project_data["Plugins"]:
            if plugin.get("Name") == plugin_name:
                plugin["Enabled"] = False
                plugin_found = True
                print(f"  [DISABLED] {plugin_name}")
                break
        
        # If not found, add it as disabled
        if not plugin_found:
            project_data["Plugins"].append({
                "Name": plugin_name,
                "Enabled": False
            })
            print(f"  [DISABLED] {plugin_name}")
    
    # Backup original file
    backup_file = uproject_file + ".backup"
    shutil.copy2(uproject_file, backup_file)
    print(f"\n[BACKUP] Original saved to {backup_file}")
    
    # Write updated project file
    with open(uproject_file, 'w') as f:
        json.dump(project_data, f, indent='\t')
    
    print("\n[SUCCESS] Plugins disabled in project file")
    print("\nNow you can:")
    print("  1. Open the project (it should load without compile errors)")
    print("  2. Once in the editor, go to Edit -> Plugins")
    print("  3. Enable plugins one by one to identify which causes issues")
    print("  4. Check Output Log for specific error messages")
    
    # Also move the plugin folders temporarily
    print("\n[MOVING] Moving plugin folders temporarily...")
    plugins_dir = "Plugins"
    disabled_dir = "Plugins_Disabled"
    
    if not os.path.exists(disabled_dir):
        os.makedirs(disabled_dir)
    
    for plugin in plugins_to_disable:
        src = os.path.join(plugins_dir, plugin)
        dst = os.path.join(disabled_dir, plugin)
        if os.path.exists(src):
            try:
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.move(src, dst)
                print(f"  [MOVED] {plugin} -> {disabled_dir}")
            except Exception as e:
                print(f"  [ERROR] Could not move {plugin}: {e}")
    
    print("\n" + "=" * 60)
    print("Plugins disabled. Try opening the project again.")
    print("\nTo restore plugins later:")
    print("  Move folders back from Plugins_Disabled/ to Plugins/")

if __name__ == "__main__":
    disable_plugins()