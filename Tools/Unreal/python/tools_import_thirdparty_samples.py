"""
tools_import_thirdparty_samples.py
Run inside Unreal Editor Python. Ensures ThirdParty folders exist and annotates look-dev maps with a
placeholder 'ThirdParty Wall' using Engine basic shapes, so you can compare alongside canon decals.

Note: Actual asset pulls should be done via Fab/Bridge (Megascans) and Epic Marketplace.
"""
import os
from datetime import date
import unreal

ROOT = unreal.SystemLibrary.get_project_directory()
LOG = os.path.normpath(os.path.join(ROOT, "../docs/Phase4_Implementation_Log.md"))
BASE_DIR = "/Game/TG/ThirdParty"
LOOKDEV_DIR = "/Game/TG/LookDev"

SUBS = ["Megascans", "Paragon", "CitySample", "InfinityBlade"]


def append_log(msg: str):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] {msg}\n")
    except Exception:
        pass


def ensure_dirs():
    if not unreal.EditorAssetLibrary.does_directory_exist(BASE_DIR):
        unreal.EditorAssetLibrary.make_directory(BASE_DIR)
    for s in SUBS:
        p = f"{BASE_DIR}/{s}"
        if not unreal.EditorAssetLibrary.does_directory_exist(p):
            unreal.EditorAssetLibrary.make_directory(p)


def place_placeholder_wall():
    # Create a simple wall of cubes labeled ThirdParty
    for level_path in unreal.EditorAssetLibrary.list_assets(LOOKDEV_DIR, recursive=False, include_folder=False):
        if not level_path.endswith(".World"):
            continue
        unreal.EditorLevelLibrary.load_level(level_path)
        # spawn a row of cubes
        for i in range(6):
            cube = unreal.EditorLevelLibrary.spawn_actor_from_object(
                unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube"),
                unreal.Vector(2000 + i * 220, 0, 120),
            )
            cube.set_actor_label(f"ThirdPartyWall_{i}")
    append_log("ThirdParty placeholder walls placed in look-dev maps (use for Megascans/Paragon comparisons)")


def main():
    ensure_dirs()
    place_placeholder_wall()
    unreal.SystemLibrary.print_string(None, "ThirdParty placeholders ready", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
