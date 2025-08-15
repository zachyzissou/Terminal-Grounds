#!/usr/bin/env python3
"""
Upscale a single image using a selected UpscaleModelLoader model via ComfyUI API.
Saves with prefix UPSCALE_<Model>_ and copies result to staging.
"""
import argparse
import json
import urllib.request
import urllib.error
from pathlib import Path
import shutil
from comfyui_api_client import ComfyUIAPIClient

ROOT = Path(__file__).resolve().parents[2]
COMFY_OUT = Path.home() / "Documents" / "ComfyUI" / "output"
COMFY_IN = Path.home() / "Documents" / "ComfyUI" / "input"
COMFY_IN_ALT = Path("C:/ComfyUI/input")


def build_upscale_workflow(image_name: str, model_name: str):
    return {
        "1": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": model_name}},
        "2": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "3": {"class_type": "ImageUpscaleWithModel", "inputs": {"image": ["2", 0], "upscale_model": ["1", 0]}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": f"UPSCALE_{model_name.replace('/', '_').replace('\\', '_')}"}},
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
            print("HTTP 400:", json.dumps(body, indent=2))
        except Exception:
            print("HTTP error:", e)
        return []
    pid = body.get("prompt_id", "")
    if not pid:
        return []
    return client.wait_for_completion(pid, timeout=timeout)


def discover_upscaler_choices(base_url: str) -> list[str]:
    try:
        with urllib.request.urlopen(f"{base_url}/object_info", timeout=5) as r:
            obj = json.loads(r.read().decode("utf-8", errors="ignore"))
        info = obj.get("nodes", {}).get("UpscaleModelLoader", {}).get("inputs", {})
        model = info.get("model_name")
        if isinstance(model, list) and model and isinstance(model[0], list):
            return model[0]
    except Exception:
        pass
    return []


def resolve_model_name(client: ComfyUIAPIClient, requested: str) -> str:
    choices = discover_upscaler_choices(client.base_url)
    if not choices:
        return requested
    # Exact match
    if requested in choices:
        return requested
    # Try with/without extension
    stem = Path(requested).name
    if stem in choices:
        return stem
    stem_no_ext = Path(requested).stem
    for c in choices:
        if Path(c).stem == stem_no_ext:
            return c
    return requested


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="Filename in ComfyUI/output")
    ap.add_argument("--model", required=True, help="Upscale model name as listed in UpscaleModelLoader choices")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2

    # Ensure image exists in ComfyUI/input for LoadImage
    src = COMFY_OUT / args.image
    dst = COMFY_IN / args.image
    try:
        # Primary input dir
        COMFY_IN.mkdir(parents=True, exist_ok=True)
        if src.exists():
            if (not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime):
                shutil.copy2(src, dst)
        # Alternate input dir (portable installs)
        if COMFY_IN_ALT:
            COMFY_IN_ALT.mkdir(parents=True, exist_ok=True)
            dst2 = COMFY_IN_ALT / args.image
            if src.exists():
                if (not dst2.exists() or src.stat().st_mtime > dst2.stat().st_mtime):
                    shutil.copy2(src, dst2)
    except Exception:
        pass

    model_name = resolve_model_name(client, args.model)
    wf = build_upscale_workflow(args.image, model_name)
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
