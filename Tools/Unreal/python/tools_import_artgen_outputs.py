"""
tools_import_artgen_outputs.py
Unreal Python: Import ArtGen PNG outputs into /Game/TG paths.

Usage:
  - Run inside Unreal Editor Python console or from a Python script action.
  - It will scan these source folders and import PNGs:
      Content/TG/Decals/Factions  -> /Game/TG/Decals/Factions
      Content/TG/Decals/Posters   -> /Game/TG/Decals/Posters
      Content/TG/Icons            -> /Game/TG/Icons
  - Safe to re-run; uses replace_existing = True.
"""

import os
import glob
import traceback
from datetime import date
import unreal  # noqa: F401  # resolved in Unreal Editor runtime

# Project directory on disk (with trailing slash)
ROOT = unreal.SystemLibrary.get_project_directory()

MATERIAL_MASTER = "/Game/TG/Materials/M_TG_Decal_Master"  # optional, created later

MAPPINGS = [
    ("Content/TG/Decals/Factions", "/Game/TG/Decals/Factions"),
    ("Content/TG/Decals/Posters", "/Game/TG/Decals/Posters"),
    ("Content/TG/Icons", "/Game/TG/Icons"),
]

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def _ensure_path(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def _collect_pngs(src_dir_abs: str) -> list[str]:
    return glob.glob(os.path.join(src_dir_abs, "**", "*.png"), recursive=True)


def import_png_folder(src_rel: str, dest_path: str) -> list[unreal.Object]:
    """Import all PNGs from a content-relative folder into a /Game destination path."""
    _ensure_path(dest_path)
    src_abs = os.path.join(ROOT, os.path.normpath(src_rel))
    files = _collect_pngs(src_abs)
    if not files:
        return []
    tasks: list[unreal.AssetImportTask] = []
    for f in files:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", f)
        task.set_editor_property("destination_path", dest_path)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("replace_existing", True)
        tasks.append(task)
    asset_tools.import_asset_tasks(tasks)
    imported: list[unreal.Object] = []
    for t in tasks:
        for obj in t.imported_object_paths:
            loaded = unreal.load_object(None, obj)
            if loaded:
                imported.append(loaded)
    return imported


def try_create_decal_mi_for_textures(textures: list[unreal.Object], dest_folder: str) -> int:
    """Optional: If a master material exists, create material instances binding a texture parameter.
    Will look for a scalar/texture parameter named 'BaseTex' or 'DecalTex'.
    Returns number of created instances.
    """
    # Check master exists
    master = unreal.load_object(None, MATERIAL_MASTER)
    if not master:
        return 0
    created = 0
    _ensure_path(dest_folder)
    lib = unreal.MaterialEditingLibrary
    for tex in textures:
        if not isinstance(tex, unreal.Texture):
            continue
        name = os.path.splitext(os.path.basename(tex.get_path_name()))[0]
        mi_name = f"MI_{name}"
        pkg_path = f"{dest_folder}/{mi_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(pkg_path):
            continue
        mi = asset_tools.create_asset(mi_name, dest_folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        if not mi:
            continue
        unreal.MaterialInstanceConstant.set_editor_property(mi, "parent", master)
        # Try common parameter names; ignore if missing
        for p in ("BaseTex", "DecalTex"):
            try:
                lib.set_material_instance_texture_parameter_value(mi, p, tex)
                break
            except Exception:
                continue
        unreal.EditorAssetLibrary.save_asset(mi.get_path_name(), only_if_is_dirty=True)
        created += 1
    return created


def append_log(message: str) -> None:
    try:
        log_path = os.path.normpath(os.path.join(ROOT, "../Docs/Phase4_Implementation_Log.md"))
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] {message}\n")
    except Exception:
        pass


def main():
    total_imported = 0
    decal_mis = 0
    summaries = []
    try:
        for src_rel, dest in MAPPINGS:
            imported = import_png_folder(src_rel, dest)
            total_imported += len(imported)
            # Try to create MIs for decals folders only
            if dest.startswith("/Game/TG/Decals"):
                decal_mis += try_create_decal_mi_for_textures(imported, dest)
            summaries.append(f"{dest}: {len(imported)} textures")
        unreal.SystemLibrary.print_string(None, f"Imported {total_imported} textures; created {decal_mis} decal MIs", text_color=unreal.LinearColor.GREEN)
        append_log(f"UE import: {'; '.join(summaries)}; decal MIs: {decal_mis}")
    except Exception as e:
        unreal.SystemLibrary.print_string(None, f"Import failed: {e}", text_color=unreal.LinearColor.RED)
        append_log(f"UE import failed: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
