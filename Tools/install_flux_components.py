#!/usr/bin/env python3
"""
Install FLUX Model Components for ComfyUI
==========================================
Downloads the required FLUX model files that were missing after restart.
This recreates the working FLUX setup from yesterday.
"""

import urllib.request
import os
from pathlib import Path

# ComfyUI paths
COMFYUI_BASE = Path("C:/Users/Zachg/Documents/ComfyUI")
MODELS_DIR = COMFYUI_BASE / "models"

# Required FLUX components
FLUX_COMPONENTS = {
    "vae/ae.safetensors": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors",
    "clip/clip_l.safetensors": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors", 
    "clip/t5xxl_fp16.safetensors": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors"
}

def download_file(url: str, filepath: Path):
    """Download file with progress"""
    print(f"Downloading {filepath.name}...")
    
    # Create directory if needed
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded * 100) // total_size)
            print(f"\r  Progress: {percent}%", end="", flush=True)
    
    try:
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print(f"\n  Downloaded {filepath.name}")
        return True
    except Exception as e:
        print(f"\n  Failed: {e}")
        return False

def check_existing_files():
    """Check which FLUX components are already present"""
    print("Checking existing FLUX components...")
    
    missing = []
    for rel_path in FLUX_COMPONENTS.keys():
        full_path = MODELS_DIR / rel_path
        if full_path.exists():
            size_mb = full_path.stat().st_size // (1024 * 1024)
            print(f"  OK: {rel_path} ({size_mb} MB)")
        else:
            print(f"  Missing: {rel_path}")
            missing.append(rel_path)
    
    return missing

def main():
    print("=" * 60)
    print("FLUX Model Components Installer")
    print("=" * 60)
    print()
    
    if not COMFYUI_BASE.exists():
        print(f"Error: ComfyUI not found at {COMFYUI_BASE}")
        print("Please check your ComfyUI installation path.")
        return 1
    
    # Check what's missing
    missing = check_existing_files()
    
    if not missing:
        print("\nAll FLUX components are already installed!")
        print("If generation is still failing, restart ComfyUI.")
        return 0
    
    print(f"\nNeed to download {len(missing)} components...")
    
    # Download missing components
    success_count = 0
    for rel_path in missing:
        url = FLUX_COMPONENTS[rel_path]
        filepath = MODELS_DIR / rel_path
        
        if download_file(url, filepath):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Downloaded {success_count}/{len(missing)} components")
    
    if success_count == len(missing):
        print("\nFLUX setup complete!")
        print("\nNext steps:")
        print("  1. Restart ComfyUI completely")
        print("  2. Test FLUX generation:")
        print("     python Tools/ArtGen/flux_generator.py")
    else:
        print("\nSome downloads failed. Check your internet connection.")
    
    return 0

if __name__ == "__main__":
    exit(main())