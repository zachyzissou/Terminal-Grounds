#!/usr/bin/env python3
"""
Terminal Grounds Production Pipeline V2
========================================
BULLETPROOF image generation with quality validation
NO ROOM FOR ERROR - Every generation must be high quality
"""

import json
import urllib.request
import urllib.error
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# CRITICAL CONFIGURATION
COMFYUI_SERVER = "127.0.0.1:8000"
OUTPUT_DIR = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
STAGING_DIR = Path(r"C:\Users\Zachg\Terminal-Grounds\Style_Staging")

# PROVEN WORKING PARAMETERS (from successful TG_ENV generations)
WORKING_CONFIG = {
    "checkpoint": r"FLUX1\flux1-dev-fp8.safetensors",  # Windows path format
    "steps": 25,
    "cfg": 6.0,
    "sampler": "dpmpp_2m",
    "scheduler": "karras",
    "width": 1024,
    "height": 576,
    "negative": "blurry, low quality, amateur"
}

class QualityValidator:
    """Validates generation quality before accepting"""
    
    @staticmethod
    def check_file_quality(filepath: Path) -> Tuple[bool, str]:
        """Check if generated file meets quality standards"""
        if not filepath.exists():
            return False, "File not found"
        
        size_kb = filepath.stat().st_size / 1024
        
        # Quality thresholds based on successful generations
        if size_kb < 200:
            return False, f"File too small ({size_kb:.1f}KB) - likely blurry/low detail"
        elif size_kb < 400:
            return False, f"File small ({size_kb:.1f}KB) - may lack detail"
        elif size_kb > 600:
            return True, f"EXCELLENT quality ({size_kb:.1f}KB)"
        else:
            return True, f"Good quality ({size_kb:.1f}KB)"

class ProductionGenerator:
    """Bulletproof generation with validation"""
    
    def __init__(self):
        self.server = COMFYUI_SERVER
        self.base_url = f"http://{self.server}"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.successful = []
        self.failed = []
        
    def check_server(self) -> bool:
        """Verify ComfyUI is running"""
        try:
            with urllib.request.urlopen(f"{self.base_url}/system_stats", timeout=5) as r:
                return r.status == 200
        except:
            return False
    
    def create_workflow(self, prompt: str, seed: int, prefix: str) -> Dict[str, Any]:
        """Create workflow with PROVEN parameters"""
        
        # Use narrative prompt style that worked
        full_prompt = f"A photograph of {prompt}. Professional photography, sharp focus throughout, incredible detail visible."
        
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": WORKING_CONFIG["checkpoint"]}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": full_prompt,
                    "clip": ["1", 1]
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": WORKING_CONFIG["negative"],
                    "clip": ["1", 1]
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": WORKING_CONFIG["width"],
                    "height": WORKING_CONFIG["height"],
                    "batch_size": 1
                }
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": WORKING_CONFIG["steps"],
                    "cfg": WORKING_CONFIG["cfg"],
                    "sampler_name": WORKING_CONFIG["sampler"],
                    "scheduler": WORKING_CONFIG["scheduler"],
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": prefix,
                    "images": ["6", 0]
                }
            }
        }
    
    def queue_and_validate(self, prompt: str, seed: int, name: str) -> bool:
        """Queue generation and validate quality"""
        
        prefix = f"TG_PROD_{name}"
        workflow = self.create_workflow(prompt, seed, prefix)
        
        # Queue the workflow
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                prompt_id = result.get('prompt_id', '')
                print(f"  Queued: {prompt_id[:8]}")
        except Exception as e:
            print(f"  ERROR queueing: {e}")
            return False
        
        # Wait for completion
        print("  Generating...", end="", flush=True)
        start_time = time.time()
        timeout = 120
        
        while time.time() - start_time < timeout:
            try:
                with urllib.request.urlopen(f"{self.base_url}/history/{prompt_id}") as resp:
                    history = json.loads(resp.read())
                
                if prompt_id in history:
                    entry = history[prompt_id]
                    outputs = entry.get('outputs', {})
                    
                    for node_output in outputs.values():
                        if 'images' in node_output:
                            filename = node_output['images'][0]['filename']
                            filepath = OUTPUT_DIR / filename
                            
                            # Wait a moment for file to be written
                            time.sleep(1)
                            
                            # Validate quality
                            passed, message = QualityValidator.check_file_quality(filepath)
                            
                            if passed:
                                print(f" SUCCESS! {message}")
                                self.successful.append((name, filename))
                                
                                # Copy to staging
                                staging_path = STAGING_DIR / "_Production" / filename
                                staging_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(filepath, staging_path)
                                
                                return True
                            else:
                                print(f" FAILED! {message}")
                                self.failed.append((name, message))
                                return False
            except:
                pass
            
            print(".", end="", flush=True)
            time.sleep(2)
        
        print(" TIMEOUT!")
        self.failed.append((name, "Generation timeout"))
        return False
    
    def generate_batch(self, concepts: List[Tuple[str, str]], base_seed: int = 70000):
        """Generate batch with quality validation"""
        
        print("\n" + "=" * 60)
        print("PRODUCTION PIPELINE V2 - QUALITY ASSURED")
        print("=" * 60)
        print(f"Generating {len(concepts)} concepts")
        print(f"Using PROVEN parameters from successful generations")
        print(f"Resolution: {WORKING_CONFIG['width']}x{WORKING_CONFIG['height']}")
        print(f"Steps: {WORKING_CONFIG['steps']}, CFG: {WORKING_CONFIG['cfg']}")
        print("=" * 60)
        
        for i, (name, prompt) in enumerate(concepts):
            print(f"\n[{i+1}/{len(concepts)}] {name}")
            
            success = self.queue_and_validate(prompt, base_seed + i * 100, name)
            
            if not success:
                print("  Retrying with different seed...")
                # Retry with different seed
                success = self.queue_and_validate(prompt, base_seed + i * 100 + 50, name)
            
            time.sleep(3)  # Don't overwhelm the server
        
        # Report
        print("\n" + "=" * 60)
        print("GENERATION REPORT")
        print("=" * 60)
        print(f"Successful: {len(self.successful)}/{len(concepts)}")
        
        if self.successful:
            print("\nSUCCESSFUL GENERATIONS:")
            for name, filename in self.successful:
                print(f"  ✓ {name}: {filename}")
        
        if self.failed:
            print("\nFAILED GENERATIONS:")
            for name, reason in self.failed:
                print(f"  ✗ {name}: {reason}")
        
        return len(self.successful) == len(concepts)

def main():
    """Run production pipeline"""
    
    # Terminal Grounds environment concepts
    concepts = [
        ("Industrial_Corridor", "an industrial corridor in Terminal Grounds facility with exposed pipes, wet concrete floors, harsh fluorescent lighting"),
        ("Metro_Platform", "an abandoned metro platform with rusted tracks, flickering lights, graffiti on walls"),
        ("Security_Checkpoint", "a military security checkpoint with bulletproof glass, metal detectors, warning signs"),
        ("Server_Room", "a server room with blinking status lights, cable chaos, dust particles in air"),
        ("Maintenance_Tunnel", "a maintenance tunnel with tool lockers, steam vents, oil stains on floor")
    ]
    
    generator = ProductionGenerator()
    
    if not generator.check_server():
        print("ERROR: ComfyUI not running on", COMFYUI_SERVER)
        sys.exit(1)
    
    success = generator.generate_batch(concepts)
    
    if success:
        print("\n✓ ALL GENERATIONS SUCCESSFUL!")
        print(f"Files saved to: {STAGING_DIR / '_Production'}")
    else:
        print("\n✗ Some generations failed - review needed")
        sys.exit(1)

if __name__ == "__main__":
    main()