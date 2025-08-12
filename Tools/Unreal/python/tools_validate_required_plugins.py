#!/usr/bin/env python3
"""
Validate required plugins and report which are missing from the selected UE 5.6 install.
Run inside the Unreal Editor Python console (preferred) or externally by passing UE path.

Usage (in-editor):
  py Tools/Unreal/python/tools_validate_required_plugins.py

Usage (external, Windows PowerShell):
  py "C:/Users/Zachg/Terminal-Grounds/Tools/Unreal/python/tools_validate_required_plugins.py" "C:/Program Files/Epic Games/UE_5.6"
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REQ = json.loads((ROOT / "Tools/Unreal/required_plugins.json").read_text())
OPTIONAL_ENGINE = set()

# Attempt to infer engine root if running in-editor
UE_ROOT = None
try:
    import unreal  # type: ignore
    UE_ROOT = Path(unreal.SystemLibrary.get_project_directory()).parents[2]
except Exception:
    pass

# Allow override from CLI
if len(sys.argv) > 1:
    UE_ROOT = Path(sys.argv[1])

if UE_ROOT is None:
    print("ERROR: Could not infer UE root. Pass it as an argument, e.g. 'C:/Program Files/Epic Games/UE_5.6'.")
    sys.exit(2)

ENGINE_PLUGINS = UE_ROOT / "Engine/Plugins"
PROJECT_PLUGINS = ROOT / "Plugins"

SEARCH_PARENTS = [
    ".", "Runtime", "Editor", "FX", "Experimental", "Developer",
    # Common special buckets
    "MovieScene", "Animation", "Marketplace"
]

missing_engine = []
for name in REQ["engine"]:
    found = False
    for parent in SEARCH_PARENTS:
        base = ENGINE_PLUGINS / parent / name
        if base.with_suffix(".uplugin").exists() or (base / f"{name}.uplugin").exists() or base.exists():
            found = True
            break
    # Also check one more level deep for some Marketplace layouts
    if not found:
        for parent in SEARCH_PARENTS:
            parent_dir = ENGINE_PLUGINS / parent
            candidate = parent_dir / name / f"{name}.uplugin"
            if candidate.exists():
                found = True
                break
    if not found:
        missing_engine.append(name)

missing_project = []
for name in REQ["project"]:
    # project plugins must exist under Plugins/<Name>/<Name>.uplugin
    if not (PROJECT_PLUGINS / name / f"{name}.uplugin").exists():
        missing_project.append(name)

print("UE Root:", UE_ROOT)
print("Engine Plugins root:", ENGINE_PLUGINS)
print("Project Plugins root:", PROJECT_PLUGINS)
print()
print("Required engine plugins:")
for n in REQ["engine"]:
    status = "(MISSING)" if n in missing_engine else "OK"
    if n in OPTIONAL_ENGINE and n in missing_engine:
        status = "(MISSING - optional)"
    print(" -", n, status)
print()
print("Required project plugins:")
for n in REQ["project"]:
    print(" -", n, "(MISSING)" if n in missing_project else "OK")

hard_missing = [n for n in missing_engine if n not in OPTIONAL_ENGINE]
if hard_missing or missing_project:
    print("\nNext steps:")
    if hard_missing:
        print(" - Install/verify these in your UE 5.6 instance via Epic Launcher:", ", ".join(hard_missing))
    soft_missing = [n for n in missing_engine if n in OPTIONAL_ENGINE]
    if soft_missing:
        print(" - Optional (but recommended) engine plugins missing:", ", ".join(soft_missing))
    if missing_project:
        print(" - Add these under the repo's Plugins/ folder:", ", ".join(missing_project))
    sys.exit(1)
else:
    print("\nAll required plugins present.")
