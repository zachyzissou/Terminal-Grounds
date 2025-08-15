#!/usr/bin/env python3
"""
Minimal ComfyUI workflow smoke test.
Posts a tiny graph and reports detailed errors.
"""
import json
import sys
import os
import urllib.request
import urllib.error
from comfyui_api_client import ComfyUIAPIClient

def build_smoke_workflow():
    ckpt_name = os.getenv("TG_CKPT", "FLUX1\\flux1-dev-fp8.safetensors")
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "terminal grounds smoke test", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "text, watermark, low quality", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"seed": 12345, "steps": 6, "cfg": 4.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "TG_Smoke"}}
    }

def main():
    client = ComfyUIAPIClient()
    print("Server:", client.base_url)
    if not client.check_server():
        print("Server not reachable; start ComfyUI first.")
        return 2

    wf = build_smoke_workflow()
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{client.base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            print("Queued OK:", body)
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code)
        try:
            print(e.read().decode("utf-8", errors="ignore"))
        except Exception:
            pass
        return 3
    except Exception as e:
        print("Error queueing:", e)
        return 4

    return 0

if __name__ == "__main__":
    sys.exit(main())
