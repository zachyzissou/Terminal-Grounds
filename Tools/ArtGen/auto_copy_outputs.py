#!/usr/bin/env python3
"""
Terminal Grounds - Auto Copy ComfyUI Outputs
===========================================
Automatically copies ComfyUI outputs to Style_Staging for analysis.
Monitors the ComfyUI output folder and copies new files immediately.
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
COMFYUI_OUTPUT = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
STAGING_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds\Style_Staging")
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")

class ComfyUIOutputHandler(FileSystemEventHandler):
    """Handles new files in ComfyUI output directory"""
    
    def __init__(self):
        self.staging_root = STAGING_ROOT
        self.staging_root.mkdir(exist_ok=True)
        
        # Create analysis folder
        self.analysis_folder = self.staging_root / "_Recent_Generations"
        self.analysis_folder.mkdir(exist_ok=True)
        
    def on_created(self, event):
        """Copy new files to staging immediately"""
        if event.is_directory:
            return
            
        source_path = Path(event.src_path)
        
        # Only copy image files
        if source_path.suffix.lower() not in ['.png', '.jpg', '.jpeg']:
            return
            
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        try:
            # Create timestamped copy
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_name = f"{timestamp}_{source_path.name}"
            dest_path = self.analysis_folder / dest_name
            
            shutil.copy2(source_path, dest_path)
            print(f"✓ Copied: {source_path.name} → {dest_name}")
            
            # Also keep original name for easy access
            latest_path = self.analysis_folder / source_path.name
            shutil.copy2(source_path, latest_path)
            
        except Exception as e:
            print(f"✗ Failed to copy {source_path.name}: {e}")

def setup_auto_copy():
    """Set up automatic copying of ComfyUI outputs"""
    
    if not COMFYUI_OUTPUT.exists():
        print(f"ComfyUI output folder not found: {COMFYUI_OUTPUT}")
        print("Please update COMFYUI_OUTPUT path in this script")
        return False
        
    print(f"Monitoring: {COMFYUI_OUTPUT}")
    print(f"Copying to: {STAGING_ROOT / '_Recent_Generations'}")
    
    event_handler = ComfyUIOutputHandler()
    observer = Observer()
    observer.schedule(event_handler, str(COMFYUI_OUTPUT), recursive=False)
    
    try:
        observer.start()
        print("✓ Auto-copy monitoring started. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        observer.stop()
        print("\n✓ Auto-copy monitoring stopped.")
        
    observer.join()
    return True

def copy_existing_outputs():
    """Copy any existing outputs from today"""
    
    if not COMFYUI_OUTPUT.exists():
        print(f"ComfyUI output folder not found: {COMFYUI_OUTPUT}")
        return
        
    analysis_folder = STAGING_ROOT / "_Recent_Generations"
    analysis_folder.mkdir(exist_ok=True)
    
    today = datetime.now().date()
    copied_count = 0
    
    for file_path in COMFYUI_OUTPUT.glob("*.png"):
        # Check if file was created today
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        if file_time.date() == today:
            dest_path = analysis_folder / file_path.name
            if not dest_path.exists():
                shutil.copy2(file_path, dest_path)
                copied_count += 1
                print(f"✓ Copied existing: {file_path.name}")
    
    print(f"✓ Copied {copied_count} existing files from today")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-copy ComfyUI outputs to staging")
    parser.add_argument("--copy-existing", action="store_true", 
                       help="Copy existing outputs from today")
    parser.add_argument("--monitor", action="store_true", default=True,
                       help="Start monitoring for new outputs")
    
    args = parser.parse_args()
    
    if args.copy_existing:
        copy_existing_outputs()
    
    if args.monitor:
        setup_auto_copy()