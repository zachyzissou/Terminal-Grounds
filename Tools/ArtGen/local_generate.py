#!/usr/bin/env python
"""
Local image generator using Hugging Face Diffusers with optional LoRA adapters.

- Default output dir: C:\\Users\\Zachg\\Terminal-Grounds-Generations
- Supports SDXL models and multiple LoRAs with per-adapter weights
- Deterministic seeds, simple CLI

Example:
  python Tools/ArtGen/local_generate.py \
    --prompt "Terminal Grounds: stylized icon of a rugged sci-fi backpack" \
    --negative "blurry, text, watermark" \
    --width 1024 --height 1024 --steps 25 --cfg 7.0 --seed 1234 \
    --model-id stabilityai/stable-diffusion-xl-base-1.0 \
    --loras '[{"repo_id":"TheMistoAI/mistoLineArtXL_lora","adapter_name":"line","scale":0.8}]'
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Optional

try:
    import torch
    from diffusers import (
        StableDiffusionXLPipeline,
        EulerAncestralDiscreteScheduler,
    )
    from PIL import Image, PngImagePlugin
except Exception as e:
    print("[local_generate] Missing dependencies. Install from Tools/ArtGen/requirements_local.txt")
    raise


def parse_loras(loras_arg: Optional[str]):
    if not loras_arg:
        return []
    # Accept JSON string or path to JSON
    if os.path.isfile(loras_arg):
        with open(loras_arg, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(loras_arg)


def ensure_output_dir(path: str):
    os.makedirs(path, exist_ok=True)


def sanitize_filename(text: str, max_len: int = 50) -> str:
    safe = "".join(c for c in text if c.isalnum() or c in ("-", "_", " "))
    safe = "_".join(safe.split())
    return safe[:max_len] if safe else "image"


def save_png(image: Image.Image, out_dir: str, base_name: str, meta: dict) -> str:
    ensure_output_dir(out_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{base_name}_{ts}.png"
    path = os.path.join(out_dir, fname)
    pnginfo = PngImagePlugin.PngInfo()
    try:
        pnginfo.add_text("generation_metadata", json.dumps(meta, ensure_ascii=False))
    except Exception:
        pass
    image.save(path, format="PNG", pnginfo=pnginfo)
    return path


def main():
    parser = argparse.ArgumentParser(description="Local Diffusers generator with LoRA support")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--negative", default="")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--model-id", default="stabilityai/stable-diffusion-xl-base-1.0")
    parser.add_argument("--loras", default=None, help="JSON string or path: [{repo_id, weight_name?, adapter_name?, scale?}]")
    parser.add_argument("--output-dir", default=os.environ.get("TG_GENERATIONS_DIR", r"C:\\Users\\Zachg\\Terminal-Grounds-Generations"))
    parser.add_argument("--dtype", default=None, choices=["auto", "fp16", "bf16", "fp32"], help="Override dtype")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if args.dtype in (None, "auto"):
        if device == "cuda":
            dtype = torch.float16
        elif torch.cuda.is_bf16_supported() if hasattr(torch, "cuda") else False:
            dtype = torch.bfloat16
        else:
            dtype = torch.float32
    else:
        dtype = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}[args.dtype]

    print(f"[local_generate] device={device} dtype={dtype}")

    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(
        args.model_id,
        torch_dtype=dtype,
        use_safetensors=True,
        variant="fp16" if dtype == torch.float16 else None,
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

    # Try to use CUDA if available
    if device == "cuda":
        pipe = pipe.to("cuda")
        try:
            pipe.enable_model_cpu_offload()  # harmless if already on cuda
        except Exception:
            pass

    # Load LoRAs if provided
    loras = parse_loras(args.loras)
    adapter_names: List[str] = []
    adapter_scales: List[float] = []
    for i, entry in enumerate(loras):
        repo_id = entry.get("repo_id") or entry.get("path")
        if not repo_id:
            print(f"[local_generate] Skipping LoRA at index {i}: missing repo_id/path")
            continue
        weight_name = entry.get("weight_name")  # optional (for repos with multiple weight files)
        adapter_name = entry.get("adapter_name") or f"lora_{i}"
        scale = float(entry.get("scale", 1.0))
        print(f"[local_generate] Loading LoRA: {repo_id} (weight={weight_name}, adapter={adapter_name}, scale={scale})")
        pipe.load_lora_weights(repo_id, weight_name=weight_name, adapter_name=adapter_name)
        adapter_names.append(adapter_name)
        adapter_scales.append(scale)

    if adapter_names:
        try:
            # Newer diffusers API for multiple adapters
            pipe.set_adapters(adapter_names, adapter_weights=adapter_scales)
        except Exception:
            # Fallback: set the last adapter only
            pipe.set_adapter(adapter_names[-1])
            print("[local_generate] Using last adapter only; update diffusers to support multiple adapters.")

    generator = None
    if args.seed is not None:
        generator = torch.Generator(device=device)
        generator = generator.manual_seed(int(args.seed))

    print("[local_generate] Generating...")
    result = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative or None,
        width=args.width,
        height=args.height,
        num_inference_steps=args.steps,
        guidance_scale=args.cfg,
        generator=generator,
    )
    image = result.images[0]

    meta = {
        "prompt": args.prompt,
        "negative": args.negative,
        "width": args.width,
        "height": args.height,
        "steps": args.steps,
        "cfg": args.cfg,
        "seed": args.seed,
        "model_id": args.model_id,
        "loras": loras,
        "device": device,
        "dtype": str(dtype),
        "elapsed_sec": round(time.time() - t0, 2),
    }

    base_name = sanitize_filename(args.prompt)
    out_path = save_png(image, args.output_dir, base_name, meta)
    print(f"[local_generate] Saved: {out_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
