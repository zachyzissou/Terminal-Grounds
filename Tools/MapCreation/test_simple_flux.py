#!/usr/bin/env python3
"""
Test simple FLUX workflow to debug the 400 errors
"""

import requests
import json
import uuid

def test_simple_flux():
    comfyui_url = "http://127.0.0.1:8188"

    # Very simple FLUX workflow
    workflow = {
        "1": {
            "inputs": {
                "clip_name1": "t5\\t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "t5\\t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader",
            "_meta": {"title": "Load CLIP"}
        },
        "2": {
            "inputs": {
                "text": "test prompt",
                "clip": ["1", 0]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Encode Text"}
        }
    }

    print("Testing simple FLUX workflow...")
    print(json.dumps(workflow, indent=2))

    try:
        response = requests.post(f"{comfyui_url}/prompt",
                               json={"prompt": workflow, "client_id": str(uuid.uuid4())})

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_flux()
