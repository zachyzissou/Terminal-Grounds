#!/usr/bin/env python3
"""
Unified HQ pipeline for Terminal Grounds concept art
---------------------------------------------------
One command to generate 1440p lore-aligned images with the locked baseline
(Euler/normal s30 cfg4.0), then optionally refine-sharpen, upscale, and
downscale to staging with a refreshed gallery index.

Usage examples (PowerShell):
  # Process the latest image only: refine + UltraSharp + 1920 downscale
  python Tools/ArtGen/pipeline_hq_batch.py --use-latest --refine --upscale-model 4x-UltraSharp.pth --downscale

  # Small batch: two locations x two seeds → refine + UltraSharp + downscale
  python Tools/ArtGen/pipeline_hq_batch.py --locations Metro_Maintenance_Corridor IEZ_Facility_Interior --seeds 94887 94890 --refine --upscale-model 4x-UltraSharp.pth --downscale
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
import urllib.request
import urllib.error
import socket
from typing import List, Dict, Tuple
import time

from PIL import Image, ImageFilter

from comfyui_api_client import ComfyUIAPIClient, COMFYUI_OUTPUT, STAGING_ROOT
from atmospheric_concept_workflow import create_atmospheric_concept_workflow
from upscale_image_once import (
    build_upscale_workflow,
    resolve_model_name,
    COMFY_IN,
    COMFY_IN_ALT,
    COMFY_OUT,
)

ROOT = Path(__file__).resolve().parents[2]
LORE = ROOT / "Tools" / "ArtGen" / "lore_index.json"
STAGING_RECENT = STAGING_ROOT / "_Recent_Generations"

ANTI_BLUR_POS = "sharp focus, crisp edges, high micro-contrast, fine surface detail"
ANTI_BLUR_NEG = "soft focus, gaussian blur, bokeh, shallow depth of field, motion blur, heavy bloom, washed out, low-contrast, haze, foggy veil, text, watermark"
EXPOSURE_POS = "balanced exposure, visible midtone detail, clear shadow detail, neutral grade"
EXPOSURE_NEG = "underexposed, crushed blacks, heavy vignette, banding"


def parse_context_from_filename(name: str) -> Tuple[str | None, str | None]:
    """Best-effort parse of location and style from an HQ_* filename.
    Expected pattern: HQ_{Location}_{Style}_{WxH}_s{steps}_cfg{cfg}_...
    We identify style by matching known styles from lore_index.json; all tokens
    between HQ_ and the style token are treated as the location.
    """
    try:
        base = Path(name).stem
        if not base.startswith("HQ_"):
            return None, None
        tokens = base.split("_")
        # tokens[0] == 'HQ'
        # Load style keys
        data = json.loads(LORE.read_text(encoding="utf-8"))
        styles = set(data.get("styles", {}).keys())
        # Find first index that matches a style name (underscores in names are preserved)
        # Some style keys contain underscores (e.g., Clean_SciFi)
        # We'll rebuild candidates by cumulative tokens
        # Seek a multi-token match for a known style key (e.g., Clean_SciFi)
        n = len(tokens)
        # stop before WxH token (contains 'x') to avoid matching size as style
        stop_idx = n
        for idx in range(2, n):
            if 'x' in tokens[idx]:
                stop_idx = idx
                break
        for i in range(2, stop_idx):
            for j in range(stop_idx - 1, i - 1, -1):
                candidate = "_".join(tokens[i:j+1])
                if candidate in styles:
                    style = candidate
                    location = "_".join(tokens[1:i])
                    return location, style
        return None, None
    except Exception:
        return None, None


def build_lore_prompt(location: str, style: str, extra: str = "") -> tuple[str, str]:
    data = json.loads(LORE.read_text(encoding="utf-8"))
    st = data["styles"].get(style, data["styles"]["Clean_SciFi"])
    loc = data["locations"].get(location, {})
    disallow = data.get("disallow", "")
    parts = [
        f"Terminal Grounds {location}",
        loc.get("scene", ""),
        loc.get("composition", ""),
        loc.get("materials", ""),
        loc.get("lighting", ""),
        loc.get("mood", ""),
        st["positives"],
        ANTI_BLUR_POS,
        EXPOSURE_POS,
        extra,
    ]
    positive = ", ".join([p for p in parts if p])
    negative = ", ".join([st["negatives"], ANTI_BLUR_NEG, EXPOSURE_NEG, disallow])
    return positive, negative


def write_prompt_sidecar(staged_filename: str, meta: Dict):
    """Write a JSON sidecar with prompts and generation params next to the staged image."""
    try:
        STAGING_RECENT.mkdir(parents=True, exist_ok=True)
        stem = Path(staged_filename).stem
        out = STAGING_RECENT / f"{stem}_meta.json"
        out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except Exception as e:
        print("Warning: couldn't write sidecar:", e)


def read_prompt_sidecar(staged_filename: str) -> Tuple[str | None, str | None]:
    """Read a JSON sidecar next to the staged image and return (positive, negative)."""
    try:
        stem = Path(staged_filename).stem
        path = STAGING_RECENT / f"{stem}_meta.json"
        if not path.exists():
            return None, None
        meta = json.loads(path.read_text(encoding="utf-8"))
        return meta.get("positive"), meta.get("negative")
    except Exception:
        return None, None


def queue_and_wait(client: ComfyUIAPIClient, wf, timeout: int = 1200) -> List[str]:
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{client.base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
    # Debug: echo CLIPTextEncode contents and dump outgoing workflow if enabled
    try:
        # Lazy global flags set in main()
        dump_workflow = globals().get("_DUMP_WORKFLOW", False)
        if dump_workflow:
            STAGING_RECENT.mkdir(parents=True, exist_ok=True)
            ts = int(time.time())
            out_path = STAGING_RECENT / f"last_workflow_{ts}.json"
            out_path.write_text(json.dumps({"prompt": wf}, indent=2), encoding="utf-8")
        # Print any CLIPTextEncode texts embedded in the workflow we are sending
        if isinstance(wf, dict):
            for node_id, node in wf.items():
                if isinstance(node, dict) and node.get("class_type") == "CLIPTextEncode":
                    txt = str(node.get("inputs", {}).get("text", ""))
                    if txt:
                        print(f"  [WF text] {txt[:200]}{'…' if len(txt) > 200 else ''}")
    except Exception as _e:
        pass
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8", errors="ignore"))
            print("HTTP 400:", json.dumps(err, indent=2))
        except Exception:
            print("HTTP error:", e)
        return []
    except urllib.error.URLError as e:
        # Connection problems (server down, refused, name resolution, etc.)
        print("Connection error posting prompt:", getattr(e, 'reason', e))
        return []
    except socket.timeout:
        print("Connection timed out posting prompt to ComfyUI")
        return []
    pid = body.get("prompt_id", "")
    if not pid:
        return []
    else:
        print("Queued prompt_id:", pid)
    outs = client.wait_for_completion(pid, timeout=timeout)
    # Debug: dump history of this prompt if enabled
    try:
        dump_history = globals().get("_DUMP_HISTORY", False)
        if dump_history and pid:
            url = f"{client.base_url}/history/{pid}"
            with urllib.request.urlopen(url, timeout=30) as r:
                hist = json.loads(r.read().decode("utf-8", errors="ignore"))
            STAGING_RECENT.mkdir(parents=True, exist_ok=True)
            hist_path = STAGING_RECENT / f"prompt_history_{pid}.json"
            hist_path.write_text(json.dumps(hist, indent=2), encoding="utf-8")
    except Exception:
        pass
    return outs


def build_refine_workflow(
    image_name: str,
    pos_prompt: str,
    neg_prompt: str,
    steps: int = 12,
    cfg: float = 4.2,
    denoise: float = 0.18,
    filename_prefix: str = "REFINE_SHARP",
    sampler_name: str = "euler",
    scheduler: str = "normal",
):
    ckpt = "FLUX1\\flux1-dev-fp8.safetensors"
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos_prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg_prompt, "clip": ["1", 1]}},
        "4": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "5": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}},
    "6": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 94887,
                "steps": steps,
                "cfg": cfg,
        "sampler_name": sampler_name,
        "scheduler": scheduler,
                "denoise": denoise,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["5", 0],
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix}},
    }


def ensure_in_input(image_name: str):
    src = (COMFY_OUT / image_name) if (COMFY_OUT / image_name).exists() else (COMFYUI_OUTPUT / image_name)
    if not src.exists():
        return False
    try:
        COMFY_IN.mkdir(parents=True, exist_ok=True)
        dst = COMFY_IN / image_name
        if (not dst.exists()) or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(src, dst)
        if COMFY_IN_ALT:
            COMFY_IN_ALT.mkdir(parents=True, exist_ok=True)
            dst2 = COMFY_IN_ALT / image_name
            if (not dst2.exists()) or src.stat().st_mtime > dst2.stat().st_mtime:
                shutil.copy2(src, dst2)
        return True
    except Exception as e:
        print("Warning: couldn't copy to input:", e)
        return False


def downscale_write(src_file: Path, width: int = 1920, unsharp: bool = True) -> Path:
    STAGING_RECENT.mkdir(parents=True, exist_ok=True)
    with Image.open(src_file) as im:
        w, h = im.size
        ratio = width / float(w)
        new_h = int(h * ratio)
        im2 = im.resize((width, new_h), resample=Image.Resampling.LANCZOS)
        if unsharp:
            im2 = im2.filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=2))
        out = STAGING_RECENT / (src_file.stem + f"_{width}w" + src_file.suffix)
        im2.save(out)
        return out


def find_latest(folder: Path) -> Path | None:
    imgs = sorted([p for p in folder.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}], key=lambda p: p.stat().st_mtime, reverse=True)
    return imgs[0] if imgs else None


def apply_tone_curve_write(src_file: Path, exposure: float = 1.08, contrast: float = 1.06, gamma: float = 0.92) -> Path:
    """Apply deterministic exposure/contrast/gamma to lift midtones and avoid underexposure.
    Writes a sibling file in staging with _Toned suffix.
    """
    from PIL import ImageEnhance

    STAGING_RECENT.mkdir(parents=True, exist_ok=True)
    with Image.open(src_file) as im:
        # Brightness (linear exposure-like)
        im2 = ImageEnhance.Brightness(im).enhance(exposure)
        # Contrast
        im2 = ImageEnhance.Contrast(im2).enhance(contrast)
        # Gamma correction via LUT
        g = max(0.01, gamma)
        inv = 1.0 / g
        lut = [min(255, int(((i / 255.0) ** inv) * 255 + 0.5)) for i in range(256)]
        if im2.mode in ("L", "P"):
            im2 = im2.point(lut)
        else:
            r, gch, b = im2.split()
            r = r.point(lut)
            gch = gch.point(lut)
            b = b.point(lut)
            im2 = Image.merge("RGB", (r, gch, b))
        out = STAGING_RECENT / (src_file.stem + "_Toned" + src_file.suffix)
        im2.save(out)
        return out


def apply_microcontrast_write(src_file: Path, radius: float = 1.6, percent: int = 60, threshold: int = 1) -> Path:
    """Apply an extra UnsharpMask pass to increase local micro-contrast.
    Writes a sibling file in staging with _MC suffix.
    """
    STAGING_RECENT.mkdir(parents=True, exist_ok=True)
    with Image.open(src_file) as im:
        im2 = im.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
        out = STAGING_RECENT / (src_file.stem + "_MC" + src_file.suffix)
        im2.save(out)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locations", nargs="*", default=["Metro_Maintenance_Corridor", "IEZ_Facility_Interior"])
    ap.add_argument("--style", default="Clean_SciFi")
    ap.add_argument("--seeds", nargs="*", type=int, default=[94887, 94890])
    ap.add_argument("--width", type=int, default=2560)
    ap.add_argument("--height", type=int, default=1440)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=4.0)
    ap.add_argument("--sampler", default="euler", help="Base sampler (e.g., euler, dpmpp_2m, heun)")
    ap.add_argument("--scheduler", default="normal", help="Base scheduler (e.g., normal, karras)")
    ap.add_argument("--profile", choices=["baseline", "clarity", "crisp-dev"], default="baseline", help="Preset for base generation")
    ap.add_argument("--vram-safe", action="store_true", help="Reduce base resolution to stay under VRAM limits")
    ap.add_argument("--vram-1080", action="store_true", help="Force base generation at 1920x1080 for maximum VRAM headroom")
    ap.add_argument("--extra", default="professional game art")
    # Optional explicit prompt overrides
    ap.add_argument("--prompt", default="", help="Override the positive prompt text entirely (verbatim)")
    ap.add_argument("--negative", default="", help="Override the negative prompt text entirely (verbatim)")
    ap.add_argument("--echo-prompt", action="store_true", help="Print the full positive/negative prompt without truncation")
    ap.add_argument("--timeout", type=int, default=1800)

    ap.add_argument("--use-latest", action="store_true", help="Skip base generation; operate on latest ComfyUI output")
    ap.add_argument("--refine", action="store_true")
    ap.add_argument("--refine-steps", type=int, default=12)
    ap.add_argument("--refine-cfg", type=float, default=4.2)
    ap.add_argument("--refine-denoise", type=float, default=0.18)
    ap.add_argument("--refine-sampler", default="euler", help="Refine sampler (e.g., euler, dpmpp_2m)")
    ap.add_argument("--refine-scheduler", default="normal", help="Refine scheduler (e.g., normal, karras)")
    # Default: reuse base prompt in refine; provide an opt-out switch
    ap.add_argument("--no-refine-base-prompt", dest="refine_use_base_prompt", action="store_false",
                    help="Do not reuse the original base positive/negative prompts in refine")
    ap.add_argument("--upscale-model", default="")
    ap.add_argument("--downscale", action="store_true")
    ap.add_argument("--downscale-width", type=int, default=1920)
    ap.add_argument("--tone", action="store_true", help="Apply exposure/contrast/gamma tone mapping to final images")
    ap.add_argument("--tone-exposure", type=float, default=1.08)
    ap.add_argument("--tone-contrast", type=float, default=1.06)
    ap.add_argument("--tone-gamma", type=float, default=0.92)
    ap.add_argument("--microcontrast", action="store_true", help="Apply extra micro-contrast sharpening pass after tone")
    ap.add_argument("--micro-radius", type=float, default=1.6)
    ap.add_argument("--micro-percent", type=int, default=60)
    ap.add_argument("--micro-threshold", type=int, default=1)
    # Debugging: dump the exact JSON sent to /prompt and the returned history
    ap.add_argument("--dump-workflow", action="store_true", help="Write the exact workflow JSON sent to ComfyUI into Style_Staging/_Recent_Generations")
    ap.add_argument("--dump-history", action="store_true", help="After completion, write the /history response JSON for this prompt into Style_Staging/_Recent_Generations")

    args = ap.parse_args()
    # Ensure default True unless explicitly disabled
    if not hasattr(args, "refine_use_base_prompt"):
        args.refine_use_base_prompt = True

    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2
    # Expose debug flags to queue_and_wait()
    globals()["_DUMP_WORKFLOW"] = bool(args.dump_workflow)
    globals()["_DUMP_HISTORY"] = bool(args.dump_history)

    produced: List[str] = []
    # Track prompts used to generate each base output (only for this run)
    base_prompts: Dict[str, Tuple[str, str]] = {}

    base_images: List[str] = []
    if args.use_latest:
        latest = find_latest(COMFYUI_OUTPUT)
        if not latest:
            print("No latest image found in ComfyUI/output")
            return 3
        base_images = [latest.name]
        print("Using latest:", base_images[0])
    else:
        # Apply preset adjustments
        sampler = args.sampler
        scheduler = args.scheduler
        width = args.width
        height = args.height
        steps = args.steps
        cfg = args.cfg

        if args.profile == "clarity":
            # Sharper base: slightly smaller res + fewer steps + karras curve
            if args.width == 2560 and args.height == 1440:
                width, height = 2048, 1152
            if args.steps == 30:
                steps = 22
            if args.cfg == 4.0:
                cfg = 4.2
            if args.sampler == "euler":
                sampler = "dpmpp_2m"
            if args.scheduler == "normal":
                scheduler = "karras"

        if args.profile == "crisp-dev":
            # Flux-friendly base for crisp concept art
            if (args.width, args.height) == (2560, 1440):
                width, height = 1536, 864  # keep 16:9, stable attention maps
            if args.steps == 30:
                steps = 34
            if abs(args.cfg - 4.0) < 1e-6:
                cfg = 4.9
            if args.sampler == "euler":
                sampler = "dpmpp_2m"
            if args.scheduler == "normal":
                scheduler = "karras"

        if args.vram_safe:
            # Keep within VRAM by capping width
            if width > 2048:
                height = int(height * (2048 / float(width)))
                width = 2048
        if args.vram_1080:
            width, height = 1920, 1080

        # If refine is requested, align refine defaults for crisp-dev when user didn't override
        if args.refine and args.profile == "crisp-dev":
            if args.refine_steps == 12:  # default unchanged
                pass  # keep 12
            if abs(args.refine_cfg - 4.2) < 1e-6:
                args.refine_cfg = float(cfg) - 0.2
            if abs(args.refine_denoise - 0.18) < 1e-6:
                args.refine_denoise = 0.26
            if args.refine_sampler == "euler":
                args.refine_sampler = "dpmpp_2m"
            if args.refine_scheduler == "normal":
                args.refine_scheduler = "karras"

        for location in args.locations:
            # Build prompts: explicit overrides take precedence
            if args.prompt:
                pos = args.prompt
                # If override lacks a TG anchor, add it once to preserve identity
                if not pos.lower().startswith("terminal grounds"):
                    pos = f"Terminal Grounds {pos}"
                if args.extra:
                    pos = f"{pos}, {args.extra}"
            else:
                pos, _neg = build_lore_prompt(location, args.style, extra=args.extra)
                if not pos.lower().startswith("terminal grounds"):
                    pos = f"Terminal Grounds {pos}"
            if args.negative:
                neg = args.negative
            else:
                # Build full negative from lore
                _pos2, neg = build_lore_prompt(location, args.style, extra="")
            for seed in args.seeds:
                prefix = f"HQ_{location}_{args.style}_{width}x{height}_s{steps}_cfg{cfg}"
                print(f"Base→ {location} seed={seed} {width}x{height} {sampler}/{scheduler} s{steps} cfg{cfg}")
                # Log prompts for visibility
                if args.echo_prompt:
                    print("  +", pos)
                    print("  -", neg)
                else:
                    print("  +", pos[:220] + ("…" if len(pos) > 220 else ""))
                    print("  -", neg[:220] + ("…" if len(neg) > 220 else ""))
                wf = create_atmospheric_concept_workflow(
                    prompt=pos,
                    seed=seed,
                    width=width,
                    height=height,
                    steps=steps,
                    cfg=cfg,
                    sampler_name=sampler,
                    scheduler=scheduler,
                    filename_prefix=prefix,
                    negative_text=neg,
                )
                outs = queue_and_wait(client, wf, timeout=args.timeout)
                for fn in outs:
                    base_images.append(fn)
                    client.copy_to_staging(fn)
                    # Remember prompts for refine phase
                    base_prompts[fn] = (pos, neg)
                    # Write sidecar metadata in staging for audit
                    meta = {
                        "filename": fn,
                        "location": location,
                        "style": args.style,
                        "width": width,
                        "height": height,
                        "steps": steps,
                        "cfg": cfg,
                        "sampler": sampler,
                        "scheduler": scheduler,
                        "seed": seed,
                        "profile": args.profile,
                        "vram_safe": args.vram_safe,
                        "vram_1080": args.vram_1080,
                        "positive": pos,
                        "negative": neg,
                    }
                    write_prompt_sidecar(fn, meta)

    # Post steps
    working_images = list(base_images)

    # Refine
    if args.refine:
        refined: List[str] = []
        for fn in working_images:
            # Prefer base prompts from this run to retain scene fidelity
            if args.refine_use_base_prompt and fn in base_prompts:
                bpos, bneg = base_prompts[fn]
                pos = f"{bpos}, {ANTI_BLUR_POS}, {EXPOSURE_POS}"
                neg = f"{bneg}, {ANTI_BLUR_NEG}, {EXPOSURE_NEG}"
            else:
                # 1) Try reading prompts from an existing sidecar for this image (works for REFINE_* or HQ_* across runs)
                spos, sneg = read_prompt_sidecar(fn)
                if spos and sneg:
                    pos = f"{spos}, {ANTI_BLUR_POS}, {EXPOSURE_POS}"
                    neg = f"{sneg}, {ANTI_BLUR_NEG}, {EXPOSURE_NEG}"
                else:
                    # 2) Attempt to parse location/style from filename to build a full lore-aware prompt
                    loc, sty = parse_context_from_filename(fn)
                    if loc and sty:
                        bpos, bneg = build_lore_prompt(loc, sty)
                        pos = f"{bpos}, {ANTI_BLUR_POS}, {EXPOSURE_POS}"
                        neg = f"{bneg}, {ANTI_BLUR_NEG}, {EXPOSURE_NEG}"
                    else:
                        # 3) Last resort: guardrails only (avoid empty content)
                        pos = f"Terminal Grounds concept art, {ANTI_BLUR_POS}, {EXPOSURE_POS}"
                        neg = f"{ANTI_BLUR_NEG}, {EXPOSURE_NEG}"
            print("Refine prompts→")
            print("  +", pos[:220] + ("…" if len(pos) > 220 else ""))
            print("  -", neg[:220] + ("…" if len(neg) > 220 else ""))
            ensure_in_input(fn)
            wf = build_refine_workflow(
                image_name=fn,
                pos_prompt=pos,
                neg_prompt=neg,
                steps=args.refine_steps,
                cfg=args.refine_cfg,
                denoise=args.refine_denoise,
                filename_prefix="REFINE_SHARP",
                sampler_name=args.refine_sampler,
                scheduler=args.refine_scheduler,
            )
            outs = queue_and_wait(client, wf, timeout=args.timeout)
            for o in outs:
                refined.append(o)
                client.copy_to_staging(o)
                # Write sidecar for refine outputs as well, so future runs can reuse exact prompts
                meta = {
                    "filename": o,
                    "source": fn,
                    "phase": "refine",
                    "refine_steps": args.refine_steps,
                    "refine_cfg": args.refine_cfg,
                    "refine_denoise": args.refine_denoise,
                    "sampler": args.refine_sampler,
                    "scheduler": args.refine_scheduler,
                    "positive": pos,
                    "negative": neg,
                }
                write_prompt_sidecar(o, meta)
        if refined:
            working_images = refined
            produced.extend(refined)

    # Upscale
    if args.upscale_model:
        upscaled: List[str] = []
        model_resolved = resolve_model_name(client, args.upscale_model)
        for fn in working_images:
            ensure_in_input(fn)
            wf = build_upscale_workflow(fn, model_resolved)
            outs = queue_and_wait(client, wf, timeout=args.timeout)
            for o in outs:
                upscaled.append(o)
                client.copy_to_staging(o)
        if upscaled:
            working_images = upscaled
            produced.extend(upscaled)

    # Downscale
    toned_inputs: List[Path] = []
    if args.downscale:
        for fn in working_images:
            src_file = COMFYUI_OUTPUT / fn
            if src_file.exists():
                out = downscale_write(src_file, width=args.downscale_width, unsharp=True)
                toned_inputs.append(out)
                print("Downscaled:", out.name)
    else:
        # Use originals for tone step
        toned_inputs = [COMFYUI_OUTPUT / fn for fn in working_images if (COMFYUI_OUTPUT / fn).exists()]

    # Post stack: tone → micro-contrast
    final_paths: List[Path] = list(toned_inputs)
    if args.tone and final_paths:
        new_paths: List[Path] = []
        for path in final_paths:
            tout = apply_tone_curve_write(path, exposure=args.tone_exposure, contrast=args.tone_contrast, gamma=args.tone_gamma)
            print("Toned:", tout.name)
            new_paths.append(tout)
        final_paths = new_paths

    if args.microcontrast and final_paths:
        new_paths2: List[Path] = []
        for path in final_paths:
            mout = apply_microcontrast_write(path, radius=args.micro_radius, percent=args.micro_percent, threshold=args.micro_threshold)
            print("Micro-contrast:", mout.name)
            new_paths2.append(mout)
        final_paths = new_paths2

    # Refresh gallery index
    try:
        from build_review_index import main as build_index
        build_index()
    except Exception:
        pass

    print("Base images:", base_images)
    print("Produced (post steps):", produced)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
