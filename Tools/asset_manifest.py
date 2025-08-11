"""
asset_manifest.py
Generate a JSON manifest of ArtGen and UE content assets.
- Scans Tools/ArtGen/outputs, Tools/ArtGen/svg, and Content/TG/* for files of interest.
- Outputs to Docs/Tech/asset_manifest.json and logs a summary line to Phase4_Implementation_Log.md
"""
from pathlib import Path
import json
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "Docs/Tech/asset_manifest.json"
LOG = ROOT / "Docs/Phase4_Implementation_Log.md"

INCLUDE_EXT = {".svg", ".png", ".uasset", ".umap"}
SCAN_DIRS = [
    ROOT / "Tools/ArtGen/svg",
    ROOT / "Tools/ArtGen/outputs",
    ROOT / "Content/TG",
]


def collect():
    entries = []
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in INCLUDE_EXT:
                entries.append({
                    "path": str(p.relative_to(ROOT).as_posix()),
                    "bytes": p.stat().st_size,
                    "ext": p.suffix.lower(),
                })
    return {
        "date": date.today().isoformat(),
        "count": len(entries),
        "entries": sorted(entries, key=lambda e: e["path"])
    }


def write_manifest(data):
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n[{date.today().isoformat()}] Asset manifest updated: {OUT_JSON} ({data['count']} items)\n")


if __name__ == "__main__":
    write_manifest(collect())
