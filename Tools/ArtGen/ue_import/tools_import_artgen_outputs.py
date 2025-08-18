"""Import generated images into Unreal and tag metadata."""

from __future__ import annotations

import json
import pathlib

import unreal


ASSET_DST_PATH = "/Game/ArtGen/Concepts"


def import_image(img_path: pathlib.Path) -> list[str]:
    task = unreal.AssetImportTask()
    task.filename = str(img_path)
    task.destination_path = ASSET_DST_PATH
    task.automated = True
    task.replace_identical = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return task.imported_object_paths


def set_metadata(asset_path: str, meta: dict) -> None:
    asset = unreal.load_asset(asset_path)
    for key, value in meta.items():
        unreal.EditorAssetLibrary.set_metadata_tag(
            asset, str(key), json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        )
    unreal.EditorAssetLibrary.save_loaded_asset(asset)


def run_batch(folder: str) -> None:
    for img in pathlib.Path(folder).rglob("*.png"):
        imported = import_image(img)
        if imported:
            meta_path = img.with_suffix(img.suffix + ".json")
            try:
                meta = json.loads(meta_path.read_text())
            except FileNotFoundError:
                print(f"Warning: Metadata file not found for {img}. Skipping metadata tagging.")
                continue
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in {meta_path}: {e}. Skipping metadata tagging.")
                continue
            for asset in imported:
                set_metadata(asset, meta)


if __name__ == "__main__":
    run_batch(r"C:\\Path\\to\\Docs\\Concepts")