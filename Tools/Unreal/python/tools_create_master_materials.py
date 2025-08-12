"""
tools_create_master_materials.py
Create master materials needed by the ArtGen import pipeline.

Run inside Unreal Editor's Python environment.
Creates:
    /Game/TG/Materials/M_TG_Decal_Master (Deferred Decal, Translucent, DBuffer Color)
        - Texture parameter: BaseTex
        - RGB -> BaseColor, A -> Opacity

    /Game/TG/Materials/Human/M_TG_Human_Master (Surface)
        - Scalar params: Dust, Wetness, Snow, HeatDiscolor, EdgeWear
        - Texture params: SerialStampMask

    /Game/TG/Materials/Hybrid/M_TG_Hybrid_Master (Surface)
        - Scalar params: EmissiveConduits, HeatGlow, OverloadBurn, ConduitPulseRate
        - Texture params: EMPScorchMask

    /Game/TG/Materials/Alien/M_TG_Alien_Master (Surface)
        - Scalar params: IridescenceLobe, RefractionWarp, PhaseJitter, NanoSheen
        - Texture params: BioVeinMask
"""

import os
from datetime import date
import unreal  # noqa: F401

ROOT = unreal.SystemLibrary.get_project_directory()
MATS_DIR = "/Game/TG/Materials"
MASTER_PATH = f"{MATS_DIR}/M_TG_Decal_Master"
HUMAN_DIR = f"{MATS_DIR}/Human"
HYBRID_DIR = f"{MATS_DIR}/Hybrid"
ALIEN_DIR = f"{MATS_DIR}/Alien"


def ensure_dir(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def append_log(msg: str) -> None:
    try:
        log_path = os.path.normpath(os.path.join(ROOT, "../Docs/Phase4_Implementation_Log.md"))
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] {msg}\n")
    except Exception:
        pass


def create_decal_master() -> str:
    ensure_dir(MATS_DIR)
    if unreal.EditorAssetLibrary.does_asset_exist(MASTER_PATH):
        return MASTER_PATH
    # Create material asset
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.MaterialFactoryNew()
    mat = asset_tools.create_asset("M_TG_Decal_Master", MATS_DIR, unreal.Material, factory)
    if not mat:
        raise RuntimeError("Failed to create M_TG_Decal_Master")
    # Configure as deferred decal
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    try:
        mat.set_editor_property("decal_blend_mode", unreal.DecalBlendMode.DBUFFER_TRANSLUCENT_COLOR)
    except Exception:
        pass
    # Build graph: Texture Sample Parameter 'BaseTex' -> BaseColor (RGB), Opacity (A)
    lib = unreal.MaterialEditingLibrary
    # Create parameter
    tex_param = lib.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -300, 0)
    tex_param.set_editor_property("parameter_name", "BaseTex")
    # Connect
    lib.connect_material_property(tex_param, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    lib.connect_material_property(tex_param, "A", unreal.MaterialProperty.MP_OPACITY)
    # Save
    unreal.EditorAssetLibrary.save_asset(MASTER_PATH)
    return MASTER_PATH


def _create_surface_master(dir_path: str, name: str, scalar_params: list[str], texture_params: list[str]) -> str:
    ensure_dir(dir_path)
    path = f"{dir_path}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return path
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = tools.create_asset(name, dir_path, unreal.Material, unreal.MaterialFactoryNew())
    if not mat:
        raise RuntimeError(f"Failed to create {name}")
    # Surface material
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_SURFACE)
    lib = unreal.MaterialEditingLibrary
    x = -600
    y = 0
    for s in scalar_params:
        node = lib.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
        node.set_editor_property("parameter_name", s)
        y += 200
    for t in texture_params:
        node = lib.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, x+300, 0)
        node.set_editor_property("parameter_name", t)
        x += 50
    unreal.EditorAssetLibrary.save_asset(path)
    return path


def create_family_masters() -> list[str]:
    created = []
    created.append(_create_surface_master(HUMAN_DIR, "M_TG_Human_Master",
                  ["Dust", "Wetness", "Snow", "HeatDiscolor", "EdgeWear"], ["SerialStampMask"]))
    created.append(_create_surface_master(HYBRID_DIR, "M_TG_Hybrid_Master",
                  ["EmissiveConduits", "HeatGlow", "OverloadBurn", "ConduitPulseRate"], ["EMPScorchMask"]))
    created.append(_create_surface_master(ALIEN_DIR, "M_TG_Alien_Master",
                  ["IridescenceLobe", "RefractionWarp", "PhaseJitter", "NanoSheen"], ["BioVeinMask"]))
    return created


def main():
    master = create_decal_master()
    fam = create_family_masters()
    unreal.SystemLibrary.print_string(None, f"Created/verified: {master} + {len(fam)} family masters", text_color=unreal.LinearColor.GREEN)
    append_log(f"Created/verified master material: {master}")
    append_log(f"Created/verified family masters: {', '.join(fam)}")


if __name__ == "__main__":
    main()
