#!/usr/bin/env python3
"""
Terminal Grounds Lore Branch Generator
Uses the perfect parameters from today's first generation to create a complete lore branch
"""
import json
import urllib.request
import time
import uuid
import subprocess
from pathlib import Path

# Perfect parameters from today's successful generation
PERFECT_PARAMS = {
    "seed_base": 94887,
    "sampler": "heun", 
    "scheduler": "normal",
    "cfg": 3.2,
    "steps": 25,
    "width": 1536,
    "height": 864
}

def generate_lore_prompts(location, style):
    """Generate lore-accurate prompts using your existing system"""
    try:
        cmd = [
            "python", 
            "Tools/ArtGen/build_lore_prompt.py",
            "--location", location,
            "--style", style,
            "--extra", "professional AAA game art, sharp focus, fine detail, architectural visualization quality"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="C:/Users/Zachg/Terminal-Grounds")
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            positive = ""
            negative = ""
            reading_positive = False
            reading_negative = False
            
            for line in output_lines:
                if line.startswith("POSITIVE:"):
                    reading_positive = True
                    reading_negative = False
                    continue
                elif line.startswith("NEGATIVE:"):
                    reading_positive = False
                    reading_negative = True
                    continue
                
                if reading_positive and line.strip():
                    positive = line.strip()
                elif reading_negative and line.strip():
                    negative = line.strip()
            
            return positive, negative
        else:
            return None, None
            
    except Exception as e:
        print(f"Error generating lore prompts: {e}")
        return None, None

def create_lore_workflow(location, style, seed_offset=0):
    """Create workflow using perfect parameters and lore-accurate prompts"""
    
    # Generate lore-based prompts
    positive, negative = generate_lore_prompts(location, style)
    
    if not positive:
        # Fallback to high-quality generic prompts
        positive = f"Terminal Grounds {location}, {style} aesthetic, professional AAA game art, sharp focus, fine detail, architectural visualization quality, clean industrial design, precise geometry, atmospheric lighting"
        negative = "text, words, letters, UI elements, blurry, low quality, abstract, watermark, signature, overexposed"
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive,
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": PERFECT_PARAMS["width"],
                "height": PERFECT_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": PERFECT_PARAMS["seed_base"] + seed_offset,
                "steps": PERFECT_PARAMS["steps"],
                "cfg": PERFECT_PARAMS["cfg"],
                "sampler_name": PERFECT_PARAMS["sampler"],
                "scheduler": PERFECT_PARAMS["scheduler"],
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
                "images": ["6", 0],
                "filename_prefix": f"TG_LORE_{location}_{style}_Perfect"
            }
        }
    }
    
    return workflow

def submit_lore_generation(workflow, location, style):
    """Submit workflow to ComfyUI"""
    client_id = str(uuid.uuid4())
    prompt_data = {
        "prompt": workflow,
        "client_id": client_id
    }
    
    data = json.dumps(prompt_data).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:8188/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            prompt_id = result.get('prompt_id')
            
        if prompt_id:
            print(f"✓ Queued {location} ({style}): {prompt_id}")
            return prompt_id
        else:
            print(f"✗ Failed to queue {location} ({style})")
            return None
            
    except Exception as e:
        print(f"Error submitting {location}: {e}")
        return None

def generate_complete_lore_branch():
    """Generate a complete lore branch using perfect parameters"""
    
    print("TERMINAL GROUNDS - COMPLETE LORE BRANCH GENERATION")
    print("=" * 70)
    print("Using perfect parameters from today's successful generation:")
    print(f"  Seed Base: {PERFECT_PARAMS['seed_base']}")
    print(f"  Sampler: {PERFECT_PARAMS['sampler']} / {PERFECT_PARAMS['scheduler']}")
    print(f"  CFG: {PERFECT_PARAMS['cfg']}, Steps: {PERFECT_PARAMS['steps']}")
    print(f"  Resolution: {PERFECT_PARAMS['width']}x{PERFECT_PARAMS['height']}")
    print()
    
    # Define complete lore branch locations and styles
    locations = [
        "Metro_Maintenance_Corridor",
        "IEZ_Facility_Interior", 
        "Tech_Wastes_Exterior",
        "Corporate_Plaza",
        "Underground_Bunker",
        "Security_Checkpoint",
        "Industrial_Platform",
        "Research_Laboratory"
    ]
    
    styles = [
        "Clean_SciFi",
        "Gritty_Realism"
    ]
    
    queued_count = 0
    total_combinations = len(locations) * len(styles)
    
    print(f"Generating {total_combinations} lore-accurate assets...")
    print()
    
    for i, location in enumerate(locations):
        for j, style in enumerate(styles):
            seed_offset = (i * len(styles)) + j
            
            print(f"[{queued_count + 1}/{total_combinations}] {location} - {style}")
            
            # Create lore-accurate workflow
            workflow = create_lore_workflow(location, style, seed_offset)
            
            # Submit generation
            prompt_id = submit_lore_generation(workflow, location, style)
            
            if prompt_id:
                queued_count += 1
                
            # Brief pause to avoid overwhelming the queue
            time.sleep(1)
    
    print()
    print("=" * 70)
    print(f"LORE BRANCH GENERATION COMPLETE!")
    print(f"Successfully queued: {queued_count}/{total_combinations} assets")
    print()
    print("Expected outputs:")
    print("• Clean sci-fi environments with precision and authority")
    print("• Gritty realistic locations with believable wear")  
    print("• All using the perfect parameters for consistent quality")
    print("• Lore-accurate prompts from your faction documentation")
    print()
    print("Output location: C:/Users/Zachg/Documents/ComfyUI/output/")
    print("Filename pattern: TG_LORE_[Location]_[Style]_Perfect_*.png")
    print()
    print("Estimated completion time: ~6-8 minutes per asset")
    print(f"Total estimated time: ~{(queued_count * 7)//60} hours {(queued_count * 7)%60} minutes")

if __name__ == "__main__":
    generate_complete_lore_branch()