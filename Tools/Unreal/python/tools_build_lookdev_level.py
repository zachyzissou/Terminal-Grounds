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
MASTER_MAT = "/Game/TG/Materials/M_TG_Decal_Master"
GRID_COLS = 8
SPACING = 450

ASSET_FOLDERS = [
    "/Game/TG/Decals/Factions",
    "/Game/TG/Decals/Posters",
    "/Game/TG/Icons",
]


def _iter_textures() -> list[str]:
    all_tex_paths = []
    for folder in ASSET_FOLDERS:
        assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
        all_tex_paths.extend([p for p in assets if p.endswith('.Texture2D')])
    return all_tex_paths


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


def _make_mid_for_texture(tex: unreal.Texture):
    master = unreal.load_object(None, MASTER_MAT)
    if not master:
        return None
    try:
        mid = unreal.MaterialInstanceDynamic.create(master)
        mid.set_texture_parameter_value("BaseTex", tex)
        return mid
    except Exception:
        return None


def _ensure_lighting():
    if len(unreal.EditorLevelLibrary.get_all_level_actors()) >= 5:
        return
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))


def _spawn_decal_at(tex: unreal.Texture, x: int, y: int) -> bool:
    loc = unreal.Vector(x, y, 150)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DecalActor, loc)
    try:
        comp = actor.get_component_by_class(unreal.DecalComponent)
        comp.set_editor_property("decal_size", unreal.Vector(256, 256, 256))
        mid = _make_mid_for_texture(tex)
        if mid:
            comp.set_decal_material(mid)
        return True
    except Exception:
        return False


def place_assets():
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        return 0
    _ensure_lighting()
    count = 0
    row = 0
    col = 0
    for path in _iter_textures():
        tex = unreal.load_object(None, path)
        if not tex:
            continue
        x = col * SPACING
        y = row * SPACING
        if _spawn_decal_at(tex, x, y):
            count += 1
        col += 1
        if col >= GRID_COLS:
            col = 0
            row += 1
    return count


def main():
    ensure_level()
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    num = place_assets()
    append_log(f"LookDev level prepared: {LEVEL_PATH}, placed items: {num}")
    unreal.SystemLibrary.print_string(None, f"LookDev: placed {num}", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
