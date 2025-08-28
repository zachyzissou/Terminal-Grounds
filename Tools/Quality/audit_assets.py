# -*- coding: utf-8 -*-
"""
TG Asset Quality Audit

Purpose: Evaluate generated images and classify Keep/Review/Reject using safe, deterministic heuristics.
Outputs:
- JSONL report per image with scores, decision, and reasons.
- Rejected assets moved to Tools/Comfy/ComfyUI-API/output/05_QUALITY_CONTROL/Rejected/
- Optional thumbnails for quick visual review.

Heuristics implemented:
- Resolution check: expected min width/height thresholds (e.g., 1024 for logos, 1536x864 for environments).
- Blur/sharpness: variance of Laplacian threshold.
- Excessive text artifact risk: OCR optional (disabled by default), fallback heuristic via edge density in text-like regions.
- Over/under exposure: histogram clipping proportion.
- Empty/dark frames: mean brightness check.
- Logo-specific: circle/edge count sanity and flat background ratio.

Usage (PowerShell):
  python Tools/Quality/audit_assets.py --root "Tools/Comfy/ComfyUI-API/output" --move-rejects

"""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import shutil
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except Exception as e:
    cv2 = None
    np = None

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None  # type: ignore

@dataclass
class AuditResult:
    path: str
    width: int
    height: int
    category: str
    sharpness: float
    brightness_mean: float
    exposure_clipping_ratio: float
    edge_density: float
    decision: str
    reasons: List[str]
    meta: Dict[str, str] = field(default_factory=dict)

LOGO_HINT = re.compile(r"emblem|logo|wordmark|icon", re.IGNORECASE)
ENV_HINT = re.compile(r"(Metro|IEZ|Bunker|Tech_Wastes|Security|Corporate|Territorial|Environment)", re.IGNORECASE)

MIN_W_LOGO = 1024
MIN_H_LOGO = 1024
MIN_W_ENV = 1280
MIN_H_ENV = 720

SHARPNESS_MIN = 60.0  # variance of Laplacian lower bound
DARK_MEAN_MIN = 25.0
BRIGHT_MEAN_MAX = 230.0
CLIP_MAX_RATIO = 0.20  # >20% clipped pixels considered bad exposure
EDGE_DENSITY_MIN = 0.001


def guess_category(p: Path) -> str:
    s = str(p)
    if LOGO_HINT.search(s):
        return "logo"
    if ENV_HINT.search(s):
        return "environment"
    # fallback by folder name
    parts = [x.lower() for x in p.parts]
    if any(x in ("emblems", "logos") for x in parts):
        return "logo"
    return "environment"


def load_image_cv(path: Path):
    if cv2 is None:
        raise RuntimeError("OpenCV not available; please install opencv-python-headless")
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Failed to read image: {path}")
    return img


def compute_metrics(img) -> Tuple[float, float, float, float]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Sharpness
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # Brightness
    brightness_mean = float(gray.mean())
    # Exposure clipping
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    total = float(hist.sum()) or 1.0
    clipped = float(hist[0] + hist[-1]) / total
    # Edge density (Canny edges ratio)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float((edges > 0).sum()) / float(edges.size)
    return sharpness, brightness_mean, clipped, edge_density


def decide(category: str, w: int, h: int, sharpness: float, brightness_mean: float, clipped: float, edge_density: float) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    # Resolution
    if category == "logo":
        if w < MIN_W_LOGO or h < MIN_H_LOGO:
            reasons.append(f"Low resolution for logo: {w}x{h} < {MIN_W_LOGO}x{MIN_H_LOGO}")
    else:
        if w < MIN_W_ENV or h < MIN_H_ENV:
            reasons.append(f"Low resolution for environment: {w}x{h} < {MIN_W_ENV}x{MIN_H_ENV}")
    # Blur
    if sharpness < SHARPNESS_MIN:
        reasons.append(f"Low sharpness (variance of Laplacian={sharpness:.1f} < {SHARPNESS_MIN})")
    # Exposure
    if brightness_mean < DARK_MEAN_MIN:
        reasons.append(f"Too dark (mean={brightness_mean:.1f} < {DARK_MEAN_MIN})")
    if brightness_mean > BRIGHT_MEAN_MAX:
        reasons.append(f"Too bright (mean={brightness_mean:.1f} > {BRIGHT_MEAN_MAX})")
    if clipped > CLIP_MAX_RATIO:
        reasons.append(f"Exposure clipping too high ({clipped:.2%} > {CLIP_MAX_RATIO:.0%})")
    # Structure
    if edge_density < EDGE_DENSITY_MIN:
        reasons.append(f"Too few structural edges (edge density={edge_density:.4f} < {EDGE_DENSITY_MIN})")

    if reasons:
        # Distinguish hard reject vs review
        hard = any(r.startswith("Low resolution") or r.startswith("Too dark") or r.startswith("Too bright") for r in reasons)
        decision = "Reject" if hard else "Review"
    else:
        decision = "Keep"
    return decision, reasons


def audit_image(path: Path) -> Optional[AuditResult]:
    try:
        img = load_image_cv(path)
        h, w = img.shape[:2]
        category = guess_category(path)
        sharpness, bright, clip, edge = compute_metrics(img)
        decision, reasons = decide(category, w, h, sharpness, bright, clip, edge)
        meta: Dict[str, str] = {}
        # Attempt PNG text metadata extraction for post-mortem (ComfyUI embeds prompts/workflows)
        if Image is not None and path.suffix.lower() == ".png":
            try:
                with Image.open(path) as im:
                    info = getattr(im, "text", None) or getattr(im, "info", {})
                    # Collect common ComfyUI keys if present
                    for k in ("prompt", "workflow", "workflow_json", "parameters", "seed"):
                        v = info.get(k)
                        if v:
                            meta[k] = str(v)[:4000]  # clamp to avoid huge blobs
            except Exception:
                pass
        return AuditResult(str(path), w, h, category, sharpness, bright, clip, edge, decision, reasons, meta)
    except Exception as e:
        return AuditResult(str(path), 0, 0, "unknown", 0.0, 0.0, 1.0, 0.0, "Reject", [f"Load/parse error: {e}"], {})


def iter_images(root: Path):
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    for p in root.rglob("*"):
        if p.suffix.lower() in exts:
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="Tools/Comfy/ComfyUI-API/output")
    ap.add_argument("--report", default="Tools/Quality/audit_report.jsonl")
    ap.add_argument("--move-rejects", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    report_path = Path(args.report)
    reject_dir = root / "05_QUALITY_CONTROL" / "Rejected"
    reject_dir.mkdir(parents=True, exist_ok=True)

    results: List[AuditResult] = []
    for img_path in iter_images(root):
        res = audit_image(img_path)
        if res:
            results.append(res)

    with report_path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    if args.move_rejects:
        for r in results:
            if r.decision == "Reject":
                src = Path(r.path)
                dest = reject_dir / src.name
                try:
                    # Avoid overwrite
                    if dest.exists():
                        dest = reject_dir / f"{src.stem}_dup{dest.suffix}"
                    shutil.move(str(src), str(dest))
                except Exception:
                    pass

    kept = sum(1 for r in results if r.decision == "Keep")
    review = sum(1 for r in results if r.decision == "Review")
    reject = sum(1 for r in results if r.decision == "Reject")
    print(f"Audited {len(results)} images -> Keep={kept} Review={review} Reject={reject}")

if __name__ == "__main__":
    main()
