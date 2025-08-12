#!/usr/bin/env python3
"""
tools_find_ue_roots.py
Locate Unreal Engine 5.6 installs and report whether GameplayTags and WorldPartitionEditor plugins exist.
Run externally via Python.
"""
from pathlib import Path

CANDIDATES = [
    Path(r"C:/Program Files/Epic Games/UE_5.6"),
    Path(r"C:/Epic Games/UE_5.6"),
    Path(r"D:/Epic Games/UE_5.6"),
    Path(r"E:/ Epic Games/UE_5.6"),
    Path(r"D:/UE_5.6"),
    Path(r"E:/UE_5.6"),
]

def check(root: Path) -> dict:
    tags = root / "Engine/Plugins/Runtime/GameplayTags/GameplayTags.uplugin"
    wpe = root / "Engine/Plugins/Editor/WorldPartitionEditor/WorldPartitionEditor.uplugin"
    editor = root / "Engine/Binaries/Win64/UnrealEditor.exe"
    return {
        "root": str(root),
        "exists": root.exists(),
        "editor": editor.exists(),
        "GameplayTags": tags.exists(),
        "WorldPartitionEditor": wpe.exists(),
    }

def main():
    any_found = False
    print("Scanning UE_5.6 candidates...\n")
    for c in CANDIDATES:
        info = check(c)
        if info["exists"]:
            any_found = True
            print(f"{info['root']}")
            print(f"  UnrealEditor.exe: {info['editor']}")
            print(f"  GameplayTags:     {info['GameplayTags']}")
            print(f"  WorldPartition:   {info['WorldPartitionEditor']}")
            print()
    if not any_found:
        print("No UE_5.6 candidate roots exist among common paths.")

if __name__ == "__main__":
    main()
