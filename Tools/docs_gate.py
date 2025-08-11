"""
docs_gate.py
Simple docs gate to assert required files exist and are non-empty.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "Docs/Phase4_Implementation_Log.md",
    ROOT / "docs/Art/ART_BIBLE.md",
    ROOT / "docs/Art/UI_STYLE_GUIDE.md",
    ROOT / "HOWTO-BUILD.md",
    ROOT / "HOWTO-HOST.md",
]


def _report(title: str, items: list[Path]):
    if not items:
        return
    print(title)
    for p in items:
        print(f" - {p}")


def check():
    missing = [p for p in REQUIRED if not p.exists()]
    empty = [p for p in REQUIRED if p.exists() and p.stat().st_size == 0]
    if missing or empty:
        print("Docs Gate FAILED")
        _report("Missing:", missing)
        _report("Empty:", empty)
        sys.exit(1)
    print("Docs Gate OK")


if __name__ == "__main__":
    check()
