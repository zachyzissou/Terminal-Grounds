#!/usr/bin/env python3
"""
Build a lore-aware prompt from lore_index.json and optional style.
Prints the positive and negative strings for use with runners.
"""
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LORE = ROOT / "Tools" / "ArtGen" / "lore_index.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--location", default="Metro_Maintenance_Corridor")
    ap.add_argument("--style", default="Clean_SciFi")
    ap.add_argument("--extra", default="")
    args = ap.parse_args()

    data = json.loads(LORE.read_text(encoding="utf-8"))
    styles = data["styles"]
    locs = data["locations"]
    disallow = data.get("disallow", "")

    st = styles.get(args.style, styles["Clean_SciFi"])
    loc = locs.get(args.location, {})

    parts = [
        f"Terminal Grounds {args.location}",
        loc.get("scene", ""),
        loc.get("composition", ""),
        loc.get("materials", ""),
        loc.get("lighting", ""),
        loc.get("mood", ""),
        st["positives"],
        args.extra,
    ]
    positive = ", ".join([p for p in parts if p])
    negative = ", ".join([st["negatives"], disallow])

    print("POSITIVE:\n" + positive)
    print("\nNEGATIVE:\n" + negative)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
