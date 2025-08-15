#!/usr/bin/env python3
"""
validate_placeholders.py

Repo scanner to detect placeholder/low-quality images and fail CI if present.
- Writes Docs/.placeholder_report.json
- Always prints a clear summary and per-item reasons to stdout
- Exit codes: 0 OK, 2 when flagged items exist, 1 on unexpected error
"""
from __future__ import annotations

import os
import re
import json
from typing import List, Dict, Any, Tuple

# Resolve repo root (project root is one level up from this file) and operate from there
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)

# Optional Pillow import (size checks best-effort if missing)
try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore

# Heuristics
BAD_RX = re.compile(r"(temp|tmp|placeholder|dummy|sample|stock|lorem|test|wip|todo|untitled|draft|lowres|example)", re.I)
CLASSES: Dict[str, Dict[str, Any]] = {
    "icon": {"paths": ["Content/TG/Icons"], "min": (512, 512), "square": True},
    "emblem": {"paths": ["Content/TG/Decals/Factions"], "min": (1024, 1024), "square": True},
    "poster": {"paths": ["Docs/Concepts/Posters", "Content/TG/Decals/Posters"], "min": (1024, 1536)},
    "concept": {
        "paths": [
            "Docs/Concepts",
            "Docs/Concepts/AI",
            "Docs/Concepts/Renders",
            "Docs/Concepts/StyleTiles",
            "Docs/Concepts/Palettes",
        ],
        "min": (1280, 720),
    },
}
IMG_EXT = (".png", ".jpg", ".jpeg", ".tga", ".webp", ".bmp", ".svg")

# Limit scanning to project asset roots only
SCAN_ROOTS = [
    "Content",
    "Docs",
    os.path.join("Tools", "ArtGen", "outputs"),
]


def classify(path: str) -> str | None:
    p = path.replace("\\", "/").lower()
    for k, v in CLASSES.items():
        if any(p.startswith(x.lower()) for x in v["paths"]):
            return k
    return None


def size_of(path: str, klass: str | None) -> Tuple[int, int]:
    # SVG: assume nominal target sizes by class (so squareness/min checks still apply)
    if path.lower().endswith(".svg"):
        if klass in ("icon", "emblem"):
            return 2048, 2048
        return 1536, 1024
    if Image is None:
        return 0, 0
    try:
        with Image.open(path) as im:
            return int(im.width), int(im.height)
    except Exception:
        return 0, 0


def scan_images() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for root in SCAN_ROOTS:
        if not os.path.isdir(root):
            continue
        for base, _, files in os.walk(root):
            for fn in files:
                if os.path.splitext(fn)[1].lower() in IMG_EXT:
                    p = os.path.join(base, fn)
                    klass = classify(p)
                    w, h = size_of(p, klass)
                    flags: List[str] = []
                    if BAD_RX.search(p):
                        flags.append("name_placeholder")
                    if klass:
                        mn = CLASSES[klass]["min"]
                        if w and h and (w < mn[0] or h < mn[1]):
                            flags.append("too_small")
                        if CLASSES[klass].get("square") and w and h and w != h:
                            flags.append("not_square")
                    # If we couldn't read size and class defines mins, surface as info
                    if (w, h) == (0, 0) and klass:
                        flags.append("size_unknown")
                    results.append({
                        "path": p.replace("\\", "/"),
                        "class": klass,
                        "w": w,
                        "h": h,
                        "flags": flags,
                    })
    return results


def print_report(report: Dict[str, Any]) -> None:
    total = report["total"]
    flagged = report["flagged"]
    print(f"[validate_placeholders] Scanned {total} images. Flagged {flagged}.")
    if flagged:
        print("[validate_placeholders] Flagged items (path [class WxH]): reasons")
        for item in report["items"]:
            path = item["path"]
            klass = item.get("class") or "unknown"
            w, h = item.get("w", 0), item.get("h", 0)
            reasons = ", ".join(item.get("flags", [])) or "(none)"
            print(f" - {path} [{klass} {w}x{h}]: {reasons}")


def main() -> int:
    try:
        results = scan_images()
        bad = [r for r in results if r["flags"]]
        report = {"total": len(results), "flagged": len(bad), "items": bad}
        os.makedirs("Docs", exist_ok=True)
        with open("Docs/.placeholder_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print_report(report)
        return 2 if bad else 0
    except Exception as e:  # pragma: no cover
        print(f"[validate_placeholders] ERROR: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
