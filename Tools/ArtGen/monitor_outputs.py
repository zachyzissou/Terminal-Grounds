#!/usr/bin/env python3
"""
Simple output monitor - just copy new files every few seconds
"""

import time
import os
from pathlib import Path
import shutil
from datetime import datetime

COMFYUI_OUTPUT = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
STAGING_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds\Style_Staging")

def monitor_and_copy():
    """Monitor for new ComfyUI outputs and copy them"""
    
    staging_folder = STAGING_ROOT / "_Recent_Generations"
    staging_folder.mkdir(parents=True, exist_ok=True)
    
    if not COMFYUI_OUTPUT.exists():
        print(f"ComfyUI output folder not found: {COMFYUI_OUTPUT}")
        return
    
    print(f"Monitoring: {COMFYUI_OUTPUT}")
    print(f"Copying to: {staging_folder}")
    print("Press Ctrl+C to stop")
    
    seen_files = set()
    
    # Get initial file list
    if COMFYUI_OUTPUT.exists():
        for file_path in COMFYUI_OUTPUT.glob("*.png"):
            seen_files.add(file_path.name)
    
    try:
        while True:
            if COMFYUI_OUTPUT.exists():
                for file_path in COMFYUI_OUTPUT.glob("*.png"):
                    if file_path.name not in seen_files:
                        # New file found
                        dest_path = staging_folder / file_path.name
                        try:
                            shutil.copy2(file_path, dest_path)
                            print(f"NEW: {file_path.name}")
                            seen_files.add(file_path.name)
                        except Exception as e:
                            print(f"Error copying {file_path.name}: {e}")
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

if __name__ == "__main__":
    monitor_and_copy()