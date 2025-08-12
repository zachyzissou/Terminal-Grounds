"""
tools_build_lookdev_levels.py
Create four biome look-dev maps with basic lighting, decal walls, and empty VFX lanes.
Biomes: IEZ, TechWastes, SkyBastion, BlackVault
Creates two variants per biome: _Day and _Night (simple light intensity/color change)
"""
import os
from datetime import date
import unreal

ROOT = unreal.SystemLibrary.get_project_directory()
LOG = os.path.normpath(os.path.join(ROOT, "../Docs/Phase4_Implementation_Log.md"))
BASE_DIR = "/Game/TG/LookDev"
MASTER_MAT = "/Game/TG/Materials/M_TG_Decal_Master"

BIOMES = ["IEZ", "TechWastes", "SkyBastion", "BlackVault"]


def append_log(msg: str):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] {msg}\n")
    except Exception:
        pass


def ensure_dir(path: str):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def ensure_level(name: str) -> str:
    ensure_dir(BASE_DIR)
    level_path = f"{BASE_DIR}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        return level_path
    factory = unreal.WorldFactory()
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.create_asset(name, BASE_DIR, unreal.World, factory)
    return level_path


def _ensure_lighting(day: bool):
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    if any(isinstance(a, unreal.DirectionalLight) for a in actors):
        # tweak for time of day
        for a in actors:
            if isinstance(a, unreal.DirectionalLight):
                lc = a.get_component_by_class(unreal.DirectionalLightComponent)
                if lc:
                    lc.set_editor_property("intensity", 10_000.0 if day else 500.0)
                    lc.set_editor_property("light_color", unreal.LinearColor(1.0, 0.95, 0.9, 1.0) if day else unreal.LinearColor(0.6, 0.7, 1.0, 1.0))
        return
    # create default stack
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000))
    if sun:
        lc = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if lc:
            lc.set_editor_property("intensity", 10_000.0 if day else 500.0)
            lc.set_editor_property("light_color", unreal.LinearColor(1.0, 0.95, 0.9, 1.0) if day else unreal.LinearColor(0.6, 0.7, 1.0, 1.0))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))


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


def _iter_textures() -> list[str]:
    all_tex_paths = []
    for folder in ("/Game/TG/Decals/Factions", "/Game/TG/Decals/Posters"):
        assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
        all_tex_paths.extend([p for p in assets if p.endswith('.Texture2D')])
    return all_tex_paths


def _spawn_decal_grid(cols=6, rows=3, spacing=450, z=150):
    tex_paths = _iter_textures()
    placed = 0
    r = c = 0
    for p in tex_paths[: cols * rows]:
        tex = unreal.load_object(None, p)
        if not tex:
            continue
        loc = unreal.Vector(c * spacing, r * spacing, z)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DecalActor, loc)
        comp = actor.get_component_by_class(unreal.DecalComponent)
        if comp:
            comp.set_editor_property("decal_size", unreal.Vector(256, 256, 256))
            mid = _make_mid_for_texture(tex)
            if mid:
                comp.set_decal_material(mid)
        placed += 1
        c += 1
        if c >= cols:
            c = 0
            r += 1
    return placed


def build_biome(name: str):
    for tod in ("Day", "Night"):
        lvl = ensure_level(f"L_TG_{name}_{tod}")
        unreal.EditorLevelLibrary.load_level(lvl)
        _ensure_lighting(day=(tod == "Day"))
        placed = _spawn_decal_grid()
        append_log(f"LookDev biome {name} ({tod}) prepared: {lvl}, decals placed: {placed}")


def main():
    for b in BIOMES:
        build_biome(b)
    unreal.SystemLibrary.print_string(None, f"Built lookdev levels for {len(BIOMES)} biomes", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
