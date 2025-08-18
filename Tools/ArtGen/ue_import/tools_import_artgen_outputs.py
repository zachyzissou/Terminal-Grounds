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
            meta = json.loads(img.with_suffix(img.suffix + ".json").read_text())
            for asset in imported:
                set_metadata(asset, meta)


if __name__ == "__main__":
    run_batch(r"C:\\Path\\to\\Docs\\Concepts")

