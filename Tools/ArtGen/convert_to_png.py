#!/usr/bin/env python3
"""
Convert an image to PNG (supports WebP, JPEG, etc.).

Usage:
  python Tools/ArtGen/convert_to_png.py <input_image> <output_png>

If Pillow (PIL) is not installed, prints a friendly message.
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    from PIL import Image  # type: ignore
except Exception:
    print("[convert_to_png] Missing dependency: Pillow. Install with: pip install pillow", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python Tools/ArtGen/convert_to_png.py <input_image> <output_png>")
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    if not src.exists():
        print(f"[convert_to_png] Input not found: {src}", file=sys.stderr)
        return 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im.save(dst, format="PNG")
    print(f"[convert_to_png] Wrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
