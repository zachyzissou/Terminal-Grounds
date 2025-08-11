"""
tools_create_master_materials.py
Create master materials needed by the ArtGen import pipeline.

Run inside Unreal Editor's Python environment.
Creates:
  /Game/TG/Materials/M_TG_Decal_Master (Deferred Decal, Translucent, DBuffer Color)
    - Texture parameter: BaseTex
    - RGB -> BaseColor, A -> Opacity
"""

import os
from datetime import date
import unreal  # noqa: F401

ROOT = unreal.SystemLibrary.get_project_directory()
MATS_DIR = "/Game/TG/Materials"
MASTER_PATH = f"{MATS_DIR}/M_TG_Decal_Master"


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


def main():
    master = create_decal_master()
    unreal.SystemLibrary.print_string(None, f"Created/verified: {master}", text_color=unreal.LinearColor.GREEN)
    append_log(f"Created/verified master material: {master}")


if __name__ == "__main__":
    main()
