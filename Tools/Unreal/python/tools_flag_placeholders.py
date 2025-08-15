import unreal, re

BAD_RX = re.compile(r"(temp|tmp|placeholder|dummy|sample|stock|lorem|test|wip|todo|untitled|draft|lowres|example)", re.I)

asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_reg.get_assets_by_path("/Game/TG", recursive=True)

count = 0
for a in assets:
    if a.asset_class != "Texture2D":
        continue
    path = a.object_path.string
    if BAD_RX.search(path):
        try:
            tex = a.get_asset()
            unreal.EditorAssetLibrary.set_metadata_tag(tex, "Placeholder", "True")
            unreal.EditorAssetLibrary.save_loaded_asset(tex)
            unreal.log_warning(f"[TG] Placeholder flagged: {path}")
            count += 1
        except Exception as e:
            unreal.log_error(f"[TG] Failed tagging {path}: {e}")

unreal.log(f"[TG] Placeholder textures flagged: {count}")
import re
import unreal

BAD_RX = re.compile(r"(temp|tmp|placeholder|dummy|sample|stock|lorem|test|wip|todo|untitled|draft|lowres|example)", re.I)

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_assets_by_path("/Game/TG", recursive=True)

collection_manager = getattr(unreal, "CollectionManager", None)
coll_type = getattr(unreal, "CollectionShareType", None)
if collection_manager and coll_type:
    try:
        unreal.CollectionManager.get().create_collection("TG_Placeholders", coll_type.CST_Local, True)
    except Exception:
        pass

count = 0
for a in assets:
    if a.asset_class != "Texture2D":
        continue
    path = a.object_path.string
    if BAD_RX.search(path):
        tex = a.get_asset()
        try:
            unreal.EditorAssetLibrary.set_metadata_tag(tex, "Placeholder", "True")
            unreal.EditorAssetLibrary.save_loaded_asset(tex)
            if collection_manager and coll_type:
                try:
                    unreal.CollectionManager.get().add_to_collection(coll_type.CST_Local, "TG_Placeholders", [path])
                except Exception:
                    pass
            unreal.log_warning(f"[TG] Placeholder flagged: {path}")
            count += 1
        except Exception as e:
            unreal.log_error(f"[TG] Failed to tag {path}: {e}")

unreal.log(f"[TG] Placeholder textures flagged: {count}")
import re
import unreal

BAD_RX = re.compile(r"(temp|tmp|placeholder|dummy|sample|stock|lorem|test|wip|todo|untitled|draft|lowres|example)", re.I)

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_assets_by_path("/Game/TG", recursive=True)

count = 0
for a in assets:
    if a.asset_class != "Texture2D":
        continue
    path = a.object_path.string
    if BAD_RX.search(path):
        tex = a.get_asset()
        try:
            unreal.EditorAssetLibrary.set_metadata_tag(tex, "Placeholder", "True")
            unreal.EditorAssetLibrary.save_loaded_asset(tex)
        except Exception:
            pass
        unreal.log_warning(f"[TG] Placeholder flagged: {path}")
        count += 1

unreal.log(f"[TG] Placeholder textures flagged: {count}")
import unreal, re

BAD_RX = re.compile(r"(temp|tmp|placeholder|dummy|sample|stock|lorem|test|wip|todo|untitled|draft|lowres|example)", re.I)

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_assets_by_path("/Game/TG", recursive=True)
count = 0

# Try to ensure a collection exists (best-effort)
collection_mgr = getattr(unreal, "CollectionManager", None)
if collection_mgr:
    try:
        collection_mgr.get().create_collection("StaticCollections", "TG_Placeholders", unreal.CollectionShareType.LOCAL)
    except Exception:
        pass

for a in assets:
    if a.asset_class != "Texture2D":
        continue
    path = a.object_path.string
    if BAD_RX.search(path):
        try:
            tex = a.get_asset()
            unreal.EditorAssetLibrary.set_metadata_tag(tex, "Placeholder", "True")
            unreal.EditorAssetLibrary.save_loaded_asset(tex)
            if collection_mgr:
                try:
                    collection_mgr.get().add_to_collection("StaticCollections", "TG_Placeholders", [path])
                except Exception:
                    pass
            unreal.log_warning(f"[TG] Placeholder flagged: {path}")
            count += 1
        except Exception as e:
            unreal.log_warning(f"[TG] Failed to flag placeholder {path}: {e}")

print(f"[TG] Placeholder textures flagged: {count}")
