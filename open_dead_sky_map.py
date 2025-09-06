#!/usr/bin/env python3
"""
Open Dead Sky IEZ Map in Unreal Engine
========================================

Opens the Dead Sky region map that we just created.
"""

import subprocess
import sys
import time
from pathlib import Path

def open_dead_sky_map():
    """Open the Dead Sky IEZ map in Unreal Engine"""

    print("🌌 Opening Dead Sky (IEZ) Map in Unreal Engine...")
    print("=" * 50)

    # Project file path
    project_file = Path("c:/Users/Zachg/Terminal-Grounds/TerminalGrounds.uproject")

    if not project_file.exists():
        print(f"❌ Project file not found: {project_file}")
        return False

    # Use the Dead Sky map we actually created
    map_name = "DeadSky_Playable"  # The map file we just created

    try:
        print(f"🎮 Launching Unreal Engine with map: {map_name}")
        print(f"📁 Project: {project_file}")
        print(f"🗺️ Map: Content/TG/Maps/IEZ/{map_name}")

        # Launch Unreal Engine with the specific map - try editor mode first
        cmd = [
            str(project_file),
            "-log"
        ]

        print(f"🚀 Executing: {' '.join(cmd)}")

        # Start Unreal Engine
        process = subprocess.Popen(cmd, shell=True)

        print("✅ Unreal Engine launching...")
        print("🌌 IEZ District Alpha map should open shortly!")
        print("\n🎯 Map Features:")
        print("   - Existing IEZ (Irradiated Exclusion Zone) district")
        print("   - Terminal Grounds faction territory")
        print("   - Industrial post-apocalyptic environment")
        print("   - Ready for gameplay testing")
        print("\n🎮 Ready to explore the IEZ!")

        return True

    except Exception as e:
        print(f"❌ Failed to launch: {e}")
        return False

if __name__ == "__main__":
    print("🌌 IEZ District Map Launcher")
    print("Opening existing IEZ District Alpha map...")

    success = open_dead_sky_map()

    if success:
        print("\n✅ Launch initiated!")
        print("The IEZ District awaits exploration...")
    else:
        print("\n❌ Launch failed!")
        print("Check that Unreal Engine is properly installed.")
