"""
tools_sanity_pass.py
Run inside Unreal Editor Python. Validates UE version, key plugins, opens/creates a temp look-dev level,
spawns a cube and (if possible) a Niagara actor. Writes a report to docs/Tech/UE56_SANITY.md and appends to docs/Phase4_Implementation_Log.md.
"""
import os
from datetime import date
import unreal

ROOT = unreal.SystemLibrary.get_project_directory()
DOCS_DIR = os.path.normpath(os.path.join(ROOT, "../docs"))
TECH_DIR = os.path.join(DOCS_DIR, "Tech")
os.makedirs(TECH_DIR, exist_ok=True)
SANITY_MD = os.path.join(TECH_DIR, "UE56_SANITY.md")
LOG = os.path.join(DOCS_DIR, "Phase4_Implementation_Log.md")

LEVEL_DIR = "/Game/TG/LookDev"
LEVEL_PATH = f"{LEVEL_DIR}/L_TG_Sanity"

REQUIRED_PLUGINS = [
    "Niagara",
    "WorldPartitionEditor",
    "Water",
    "ControlRig",
    "ModelingToolsEditorMode",
    "Fab",  # Bridge/Fab
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
    return asset_tools.create_asset("L_TG_Sanity", LEVEL_DIR, unreal.World, world_factory)


def try_spawn_actors():
    # simple lighting if empty
    if len(unreal.EditorLevelLibrary.get_all_level_actors()) < 3:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000))
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000))
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))

    cube = unreal.EditorLevelLibrary.spawn_actor_from_object(
        unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube"), unreal.Vector(0, 0, 100)
    )
    niagara_ok = False
    try:
        # Try to spawn a default Niagara actor (system reference may vary by engine installation)
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(300, 0, 100))
        niagara_ok = True
    except Exception:
        niagara_ok = False
    return cube is not None, niagara_ok


def main():
    ver = unreal.SystemLibrary.get_engine_version()
    plug_mgr = unreal.Plugins.get()
    loaded = []
    missing = []
    for name in REQUIRED_PLUGINS:
        try:
            desc = plug_mgr.find_plugin(name)
            if desc and desc.is_enabled():
                loaded.append(name)
            else:
                missing.append(name)
        except Exception:
            missing.append(name)

    ensure_level()
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    cube_ok, niagara_ok = try_spawn_actors()

    lines = [
        "# UE 5.6 Sanity Pass",
        f"Date: {date.today().isoformat()}",
        f"Engine Version: {ver}",
        "",
        "## Plugins",
        f"Enabled: {', '.join(loaded) if loaded else '(none)'}",
        f"Disabled/Unavailable: {', '.join(missing) if missing else '(none)'}",
        "",
        "## Spawn Tests",
        f"Cube Spawn: {'OK' if cube_ok else 'FAIL'}",
        f"Niagara Actor Spawn: {'OK' if niagara_ok else 'FAIL'}",
        "",
        f"Level: {LEVEL_PATH}",
    ]
    with open(SANITY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    append_log(f"UE5.6 Sanity Pass -> docs/Tech/UE56_SANITY.md")
    unreal.SystemLibrary.print_string(None, "Sanity pass complete", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
