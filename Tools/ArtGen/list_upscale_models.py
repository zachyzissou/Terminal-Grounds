#!/usr/bin/env python3
"""
List available ComfyUI upscale models by querying /object_info
and inspecting UpscaleModelLoader's model_name choices.
Falls back to a validation probe if /object_info is unavailable.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path
from comfyui_api_client import ComfyUIAPIClient


def from_object_info(base_url: str):
    try:
        with urllib.request.urlopen(f"{base_url}/object_info", timeout=5) as r:
            obj = json.loads(r.read().decode("utf-8", errors="ignore"))
        nodes = obj.get("nodes", {})
        info = nodes.get("UpscaleModelLoader", {})
        inputs = info.get("inputs", {})
        model = inputs.get("model_name")
        if isinstance(model, list) and model:
            # Newer Comfy formats: [choices, {tooltip: ...}]
            if isinstance(model[0], list):
                return model[0]
        return []
    except Exception:
        return []


def from_validation_probe(base_url: str):
    # Build a tiny prompt with UpscaleModelLoader and a bogus name to force a choices list
    prompt = {
        "1": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "__invalid__"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": "__invalid__.png"}},
        "3": {"class_type": "ImageUpscaleWithModel", "inputs": {"image": ["2", 0], "upscale_model": ["1", 0]}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "_probe_"}},
    }
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            _ = r.read()
            return []
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
            j = json.loads(body)
            ne = j.get("node_errors", {})
            for node_id, detail in ne.items():
                for err in detail.get("errors", []):
                    if err.get("type") == "value_not_in_list" and "model_name" in err.get("details", ""):
                        info = err.get("extra_info", {}).get("input_config")
                        if isinstance(info, list) and info and isinstance(info[0], list):
                            return info[0]
        except Exception:
            pass
    except Exception:
        pass
    return []


def from_filesystem() -> list[str]:
    candidates = []
    paths = [
        Path.home() / "Documents" / "ComfyUI" / "models" / "upscale_models",
        Path("C:/ComfyUI/models/upscale_models"),
    ]
    seen = set()
    for p in paths:
        try:
            if p.exists():
                for f in p.iterdir():
                    if f.is_file() and f.suffix.lower() in {".pth", ".onnx", ".safetensors"}:
                        name = f.name  # keep extension; Comfy often lists full filenames
                        if name not in seen:
                            candidates.append(name)
                            seen.add(name)
        except Exception:
            pass
    return candidates


def main():
    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2
    choices = from_object_info(client.base_url)
    if not choices:
        choices = from_validation_probe(client.base_url)
    fs = from_filesystem()
    print("UPSCALE MODELS:")
    for c in choices or []:
        print("-", c)
    if fs:
        print("\nFILESYSTEM CANDIDATES:")
        for n in fs:
            print("-", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
