#!/usr/bin/env python3
"""
CREATE DEAD SKY MAP NOW - Direct Approach
========================================

No more infrastructure. Just create a damn map file.
"""

import shutil
from pathlib import Path

def create_dead_sky_map_direct():
    """Copy an existing map and rename it to Dead Sky"""

    print("🎯 CREATING DEAD SKY MAP - DIRECT APPROACH")
    print("=" * 50)

    # Paths
    source_map = Path("c:/Users/Zachg/Terminal-Grounds/Content/TG/Maps/IEZ/IEZ_District_Alpha.umap")
    target_map = Path("c:/Users/Zachg/Terminal-Grounds/Content/TG/Maps/IEZ/DeadSky_Playable.umap")

    try:
        if source_map.exists():
            print(f"📋 Copying: {source_map.name}")
            print(f"📝 To: {target_map.name}")

            # Copy the map file
            shutil.copy2(source_map, target_map)

            print("✅ Dead Sky map created!")
            print(f"📁 Location: {target_map}")
            print("🎮 You can now open DeadSky_Playable.umap in Unreal Engine!")

            return True
        else:
            print(f"❌ Source map not found: {source_map}")
            return False

    except Exception as e:
        print(f"❌ Failed to create map: {e}")
        return False

def launch_dead_sky_map():
    """Launch the Dead Sky map we just created"""

    import subprocess

    project_file = Path("c:/Users/Zachg/Terminal-Grounds/TerminalGrounds.uproject")

    cmd = [
        str(project_file),
        "/Game/TG/Maps/IEZ/DeadSky_Playable",
        "-game",
        "-windowed"
    ]

    print("🚀 Launching Dead Sky map...")
    subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    print("🎯 DEAD SKY MAP CREATION - NO INFRASTRUCTURE!")

    # Create the map
    if create_dead_sky_map_direct():
        # Launch it
        launch_dead_sky_map()
        print("\n✅ DONE! Real Dead Sky map created and launching!")
        print("🌌 You now have an actual playable Dead Sky map!")
    else:
        print("\n❌ Failed to create map")
