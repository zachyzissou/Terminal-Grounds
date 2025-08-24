#!/usr/bin/env python3
"""
Use the advanced Terminal Grounds lore-based generation system
"""
import json
import subprocess
import urllib.request
import uuid
from pathlib import Path

def generate_lore_based_prompt(location="Metro_Maintenance_Corridor", style="Clean_SciFi"):
    """Generate a lore-accurate prompt using the build_lore_prompt system"""
    
    try:
        # Use the existing lore system
        cmd = [
            "python", 
            "Tools/ArtGen/build_lore_prompt.py",
            "--location", location,
            "--style", style,
            "--extra", "professional AAA game art, sharp focus, fine detail"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="C:/Users/Zachg/Terminal-Grounds")
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            
            # Parse the output
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
            print(f"Error generating lore prompt: {result.stderr}")
            return None, None
            
    except Exception as e:
        print(f"Failed to generate lore prompt: {e}")
        return None, None

def create_advanced_workflow(location, style, positive_prompt, negative_prompt):
    """Create an advanced workflow using lore-based prompts"""
    
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
                "text": positive_prompt,
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1536,
                "height": 864,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42042,  # Different seed for variety
                "steps": 25,
                "cfg": 3.2,
                "sampler_name": "heun",
                "scheduler": "normal",
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
                "filename_prefix": f"TG_Advanced_{location}_{style}"
            }
        }
    }
    
    return workflow

def submit_advanced_generation():
    """Submit an advanced lore-based generation"""
    
    print("TERMINAL GROUNDS ADVANCED LORE-BASED GENERATOR")
    print("=" * 60)
    
    # Generate lore-accurate prompts
    print("Generating lore-based prompts...")
    location = "Metro_Maintenance_Corridor"
    style = "Clean_SciFi"
    
    positive, negative = generate_lore_based_prompt(location, style)
    
    if not positive:
        print("Failed to generate lore-based prompts")
        return False
    
    print(f"\nLocation: {location}")
    print(f"Style: {style}")
    print(f"Positive: {positive[:100]}...")
    print(f"Negative: {negative[:100]}...")
    
    # Create advanced workflow
    workflow = create_advanced_workflow(location, style, positive, negative)
    
    # Submit to API
    print("\nSubmitting advanced workflow...")
    
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
            print(f"✓ Advanced generation queued: {prompt_id}")
            print("✓ Using lore-accurate prompts with sophisticated workflow")
            print("✓ Output will have prefix: TG_Advanced_Metro_Maintenance_Corridor_Clean_SciFi")
            return True
        else:
            print("Failed to queue advanced generation")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    submit_advanced_generation()