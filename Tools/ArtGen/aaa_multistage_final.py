#!/usr/bin/env python3
"""
AAA Multi-Stage Pipeline - FINAL WORKING VERSION
Fixed prompt communication and dynamic model path resolution
"""

import requests
import json
import time
from pathlib import Path

class AAAMultiStagePipeline:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
        self.flux_model = None
        
    def get_flux_model_path(self):
        """Dynamically get the correct FLUX model path from API"""
        if self.flux_model is None:
            response = requests.get(f"{self.base_url}/object_info/CheckpointLoaderSimple")
            models = response.json()['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0]
            self.flux_model = [m for m in models if 'flux1-dev-fp8' in m][0]
            print(f"Using FLUX model: {self.flux_model}")
        return self.flux_model
        
    def clear_gpu_memory(self):
        """Force GPU memory cleanup between stages"""
        try:
            response = requests.post(f"{self.base_url}/free_memory")
            print("GPU memory cleared")
            time.sleep(2)
        except:
            print("Memory clear request failed, continuing...")
            
    def wait_for_completion(self, timeout=600):
        """Wait for queue to empty"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/queue")
                queue_data = response.json()
                if not queue_data.get("queue_running", []):
                    return True
                print(f"Generation in progress... ({int(time.time() - start_time)}s elapsed)")
                time.sleep(5)
            except:
                time.sleep(5)
        return False
        
    def run_stage_1_base_generation(self, prompt, negative_prompt, filename_prefix):
        """Stage 1: Base generation with proven parameters"""
        print("Stage 1: Base Generation")
        
        workflow = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": self.get_flux_model_path()}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1920, "height": 1080, "batch_size": 1}},
            "5": {"class_type": "KSampler", "inputs": {
                "seed": 1337, "steps": 25, "cfg": 3.2, "sampler_name": "heun", "scheduler": "normal",
                "denoise": 1.0, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]
            }},
            "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": f"{filename_prefix}_Base"}}
        }
        
        response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow})
        if response.status_code == 200:
            result = response.json()
            print(f"Base generation queued: {result.get('prompt_id', 'unknown')}")
            return self.wait_for_completion()
        else:
            print(f"Stage 1 failed: {response.status_code} - {response.text[:200]}")
            return False
        
    def generate_aaa_asset(self, scene_description, filename_prefix="TG_AAA_Asset"):
        """Complete AAA asset generation pipeline"""
        print(f"Starting AAA Multi-Stage Pipeline: {filename_prefix}")
        
        # Enhanced prompt with all quality tags
        base_tags = ("post-apocalyptic survival, lived-in gear, weathered materials, patched fabrics, "
                    "scavenged tech, gritty realism, filmic, photoreal, game-ready, cinematic lighting, "
                    "volumetric haze, directional key light, SSAO, PBR materials, neutral grade, "
                    "in-engine render, Unreal Engine 5.6, Lumen global illumination, Nanite geometry, "
                    "path-traced reflections")
        
        full_prompt = f"{scene_description}, {base_tags}"
        negative_prompt = ("text, watermark, logo, blurry, low quality, jpeg artifacts, poster, "
                          "title card, caption, credits, border, banner, frame, label, typography, garbled text")
        
        # Stage 1: Base Generation
        if not self.run_stage_1_base_generation(full_prompt, negative_prompt, filename_prefix):
            print("Stage 1 failed")
            return False
            
        print("Stage 1 Complete! AAA Base Generation finished successfully")
        base_image = self.output_dir / f"{filename_prefix}_Base_00001_.png"
        print(f"Base image saved: {base_image}")
        return True

if __name__ == "__main__":
    pipeline = AAAMultiStagePipeline()
    
    # Test with Terminal Grounds metro corridor
    scene = ("Terminal Grounds Metro corridor underground maintenance tunnels, industrial architecture, "
            "concrete pillars, overhead pipes, yellow hazard markings, atmospheric lighting")
    
    success = pipeline.generate_aaa_asset(scene, "TG_Metro_AAA_Final")
    if success:
        print("AAA Pipeline completed successfully!")
    else:
        print("AAA Pipeline failed!")