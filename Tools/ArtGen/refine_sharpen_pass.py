#!/usr/bin/env python3
"""
Low-denoise refine pass to improve focus and micro-contrast using the same prompt.
Pipeline: LoadImage -> VAEEncode -> KSampler(denoise~0.18) -> VAEDecode -> SaveImage
This avoids re-composing the scene and tightens edges without hallucinating.
"""
import argparse
import json
from pathlib import Path
import urllib.request
import urllib.error
from comfyui_api_client import ComfyUIAPIClient, COMFYUI_OUTPUT
from upscale_image_once import COMFY_IN, COMFY_IN_ALT, COMFY_OUT
import shutil

ANTI_BLUR = (
    "tack sharp focus, crisp edges, high microcontrast, clean detail"
)
NEG_BLOCK = (
    "soft focus, motion blur, gaussian blur, depth of field, bokeh, dreamy glow, foggy veil, smeared, low contrast, underexposed"
)


def build_refine_workflow(
    image_name: str,
    prompt_text: str,
    negative_text: str | None = None,
    steps: int = 14,
    cfg: float = 4.2,
    denoise: float = 0.18,
    ckpt_name: str | None = None,
    filename_prefix: str = "REFINE_SHARP"
):
    ckpt = ckpt_name or "FLUX1\\flux1-dev-fp8.safetensors"
    neg = (negative_text + ", " + NEG_BLOCK) if negative_text else NEG_BLOCK
    pos = prompt_text + ", " + ANTI_BLUR
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "5": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}},
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 94887,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoise,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["5", 0]
            }
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix}},
    }


def queue_and_wait(client: ComfyUIAPIClient, wf, timeout: int = 600):
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{client.base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", errors="ignore"))
            print("HTTP 400:", body)
        except Exception:
            print("HTTP error:", e)
        return []
    pid = body.get("prompt_id", "")
    if not pid:
        return []
    return client.wait_for_completion(pid, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="Filename in ComfyUI/output")
    ap.add_argument("--prompt", required=True, help="Positive prompt text (will be augmented)")
    ap.add_argument("--negative", default="", help="Negative prompt text (will be augmented)")
    ap.add_argument("--steps", type=int, default=14)
    ap.add_argument("--cfg", type=float, default=4.2)
    ap.add_argument("--denoise", type=float, default=0.18)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2

    # Ensure the image exists in ComfyUI/input for LoadImage
    src = (COMFY_OUT / args.image) if (COMFY_OUT / args.image).exists() else (COMFYUI_OUTPUT / args.image)
    if not src.exists():
        print("Input image not found in ComfyUI/output:", args.image)
        return 3
    try:
        COMFY_IN.mkdir(parents=True, exist_ok=True)
        dst = COMFY_IN / args.image
        if (not dst.exists()) or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(src, dst)
        if COMFY_IN_ALT:
            COMFY_IN_ALT.mkdir(parents=True, exist_ok=True)
            dst2 = COMFY_IN_ALT / args.image
            if (not dst2.exists()) or src.stat().st_mtime > dst2.stat().st_mtime:
                shutil.copy2(src, dst2)
    except Exception as e:
        print("Warning: couldn't copy to input:", e)

    wf = build_refine_workflow(
        image_name=args.image,
        prompt_text=args.prompt,
        negative_text=args.negative or None,
        steps=args.steps,
        cfg=args.cfg,
        denoise=args.denoise,
    )
    imgs = queue_and_wait(client, wf, timeout=args.timeout)
    if imgs:
        for fn in imgs:
            client.copy_to_staging(fn)
            print("OK:", fn)
    else:
        print("No output (timeout/failure)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
