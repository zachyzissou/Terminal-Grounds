"""
tools_build_lookdev_level.py
Generate a minimal look-dev map that places poster/emblem decals and icon cards for quick visual checks.
Run inside Unreal Editor Python.
"""
import os
from datetime import date
import unreal  # noqa: F401

ROOT = unreal.SystemLibrary.get_project_directory()
LOG = os.path.normpath(os.path.join(ROOT, "../Docs/Phase4_Implementation_Log.md"))

LEVEL_PATH = "/Game/TG/LookDev/L_TG_LookDev"
LEVEL_DIR = "/Game/TG/LookDev"

ASSET_FOLDERS = [
    "/Game/TG/Decals/Factions",
    "/Game/TG/Decals/Posters",
    "/Game/TG/Icons",
]


def append_log(msg: str):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] {msg}\n")
    except Exception:
        pass


def ensure_level():
    if unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
        return unreal.load_object(None, LEVEL_PATH)
    if not unreal.EditorAssetLibrary.does_directory_exist(LEVEL_DIR):
        unreal.EditorAssetLibrary.make_directory(LEVEL_DIR)
    world_factory = unreal.WorldFactory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    level = asset_tools.create_asset("L_TG_LookDev", LEVEL_DIR, unreal.World, world_factory)
    return level


def place_assets():
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        return 0
    # Basic lighting
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
    count = 0
    x = 0
    for folder in ASSET_FOLDERS:
        assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=True)
        for path in assets:
            if not path.endswith(('.Texture2D')):
                continue
            tex = unreal.load_object(None, path)
            if not tex:
                continue
            # Create a plane and assign texture via simple unlit material instance if possible
            plane = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, 0, 0))
            plane.set_actor_scale3d(unreal.Vector(1.5, 1.5, 1.5))
            count += 1
            x += 300
    return count


def main():
    ensure_level()
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    num = place_assets()
    append_log(f"LookDev level prepared: {LEVEL_PATH}, placed items: {num}")
    unreal.SystemLibrary.print_string(None, f"LookDev: placed {num}", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
