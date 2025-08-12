"""
tools_build_niagara_baselines.py
Run inside Unreal Editor Python. Creates baseline Niagara systems (assets only, minimal placeholders)
under /Game/TG/VFX.

Also appends the created UE paths to docs/VFX/VFX_BIBLE.md and docs/Phase4_Implementation_Log.md.
"""
import os
from datetime import date
import unreal

ROOT = unreal.SystemLibrary.get_project_directory()
DOCS = os.path.normpath(os.path.join(ROOT, "../docs"))
VFX_BIBLE = os.path.join(DOCS, "VFX/VFX_BIBLE.md")
LOG = os.path.join(DOCS, "Phase4_Implementation_Log.md")

BASE_DIR = "/Game/TG/VFX"
SYS_NAMES = [
    # Human
    "NS_TG_Muzzle_S", "NS_TG_Muzzle_M", "NS_TG_Muzzle_LMG",
    "NS_TG_Impact_Concrete", "NS_TG_Impact_Metal", "NS_TG_Impact_Dirt", "NS_TG_Impact_Glass",
    "NS_TG_Brass", "NS_TG_HeatShimmer",
    # Hybrid
    "NS_TG_CoilCharge", "NS_TG_PlasmaBolt", "NS_TG_OverheatVent", "NS_TG_EMPArc",
    # Alien
    "NS_TG_BeamRibbon", "NS_TG_GravWell", "NS_TG_VoidBlade",
    # Env
    "NS_TG_RustStorm", "NS_TG_Ashfall", "NS_TG_EMI_Lightning", "NS_TG_ReactorPlume", "NS_TG_APC_Dust",
]


def ensure_dir(path: str):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def create_system(name: str) -> str:
    ensure_dir(BASE_DIR)
    path = f"{BASE_DIR}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return path
    factory = unreal.NiagaraSystemFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    sys = asset_tools.create_asset(name, BASE_DIR, unreal.NiagaraSystem, factory)
    if sys:
        unreal.EditorAssetLibrary.save_asset(path)
        return path
    raise RuntimeError(f"Failed creating {path}")


def append(path: str, text: str):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass


def main():
    created = []
    for n in SYS_NAMES:
        p = create_system(n)
        created.append(p)

    # Append to VFX Bible
    block = ["\n\n## Baseline Systems (auto)\n"] + [f"- {p}\n" for p in created]
    append(VFX_BIBLE, "".join(block))
    append(LOG, f"\n[{date.today().isoformat()}] Created Niagara baselines: {len(created)} systems under {BASE_DIR}\n")
    unreal.SystemLibrary.print_string(None, f"Niagara baselines: {len(created)}", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
