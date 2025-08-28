# -*- coding: utf-8 -*-
"""
Build a lightweight JSON index for manual visual review.
Scans Tools/Comfy/ComfyUI-API/output and emits review_index.json with relative paths for index.html.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2] / 'Comfy' / 'ComfyUI-API' / 'output'
OUT = Path(__file__).resolve().parent / 'review_index.json'

LOGO_HINT = re.compile(r"emblem|logo|wordmark|icon", re.IGNORECASE)
ENV_HINT = re.compile(r"(Metro|IEZ|Bunker|Tech_Wastes|Security|Corporate|Territorial|Environment)", re.IGNORECASE)


def guess_category(p: Path) -> str:
    s = str(p)
    if LOGO_HINT.search(s):
        return 'logo'
    if ENV_HINT.search(s):
        return 'environment'
    parts = [x.lower() for x in p.parts]
    if any(x in ('emblems','logos') for x in parts):
        return 'logo'
    return 'environment'


def main():
    items = []
    exts = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
    for p in ROOT.rglob('*'):
        if p.suffix.lower() in exts and p.is_file():
            try:
                from PIL import Image  # type: ignore
                with Image.open(p) as im:
                    w, h = im.size
            except Exception:
                w = h = 0
            rel = p.relative_to(ROOT)
            items.append({
                'id': rel.as_posix(),
                'name': rel.name,
                'rel': f"../../Comfy/ComfyUI-API/output/{rel.as_posix()}",
                'width': w,
                'height': h,
                'category': guess_category(p),
                # Optional metrics loaded if our audit exists
                'sharpness': None,
                'edge_density': 0.0,
            })
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(items)} items to {OUT}")


if __name__ == '__main__':
    main()
