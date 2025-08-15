#!/usr/bin/env python3
"""
Run an A/B upscale comparison on the most recent ComfyUI output image
(or a specific file) using two different models. Copies to staging.

Fixes:
- Ensure the source image is copied into ComfyUI/input so LoadImage can find it
- Resolve model names to valid UpscaleModelLoader choices
"""
import argparse
from pathlib import Path
from comfyui_api_client import ComfyUIAPIClient, COMFYUI_OUTPUT
from upscale_image_once import (
    build_upscale_workflow,
    queue_and_wait,
    resolve_model_name,
    COMFY_IN,
    COMFY_IN_ALT,
    COMFY_OUT,
)
import shutil


def find_latest(folder: Path) -> str | None:
    imgs = sorted([p for p in folder.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}], key=lambda p: p.stat().st_mtime, reverse=True)
    return imgs[0].name if imgs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", default="", help="Image filename in ComfyUI/output; if empty, use latest")
    ap.add_argument("--a", required=True, help="Upscaler A model name")
    ap.add_argument("--b", required=True, help="Upscaler B model name")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2

    image_name = args.image or find_latest(COMFYUI_OUTPUT)
    if not image_name:
        print("No input image found")
        return 3

    # Make sure the image exists in ComfyUI/input for LoadImage
    src = (COMFY_OUT / image_name) if (COMFY_OUT / image_name).exists() else (COMFYUI_OUTPUT / image_name)
    if not src.exists():
        print("Input image not found in ComfyUI/output:", image_name)
        return 4

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
    except Exception as e:
        print("Warning: couldn't copy to input:", e)

    print("Input:", image_name)
    for model in (args.a, args.b):
        model_resolved = resolve_model_name(client, model)
        if model_resolved != model:
            print(f"Resolved model '{model}' -> '{model_resolved}'")
        wf = build_upscale_workflow(image_name, model_resolved)
        imgs = queue_and_wait(client, wf, timeout=args.timeout)
        if not imgs:
            print("No output for", model)
        else:
            print("OK:", model, "->", imgs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
