"""
tools_capture_lookdev_renders.py
Run from UE Editor Python to capture a set of high-res renders from the LookDev level using HighResScreenshot.
"""
import os
from datetime import date
import unreal  # noqa: F401

ROOT = unreal.SystemLibrary.get_project_directory()
LOG = os.path.normpath(os.path.join(ROOT, "../Docs/Phase4_Implementation_Log.md"))
# Default single-level capture; other multi-biome captures handled by tools_build_lookdev_levels
LEVEL_PATH = "/Game/TG/LookDev/L_TG_LookDev"
OUT_DIR = os.path.normpath(os.path.join(ROOT, "../Docs/Concepts/Renders"))


def append_log(msg: str):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{date.today().isoformat()}] {msg}\n")
    except Exception:
        pass


def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def capture(name: str, res_mult: int = 1):
    ensure_out_dir()
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    filename = os.path.join(OUT_DIR, f"{name}.png")
    unreal.AutomationLibrary.take_high_res_screenshot(1920 * res_mult, 1080 * res_mult, filename)
    append_log(f"Captured lookdev render: {filename}")


def main():
    capture("lookdev_overview", 1)
    capture("lookdev_detail", 2)
    unreal.SystemLibrary.print_string(None, "LookDev renders captured", text_color=unreal.LinearColor.GREEN)


if __name__ == "__main__":
    main()
