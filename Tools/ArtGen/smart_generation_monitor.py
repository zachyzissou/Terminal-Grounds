#!/usr/bin/env python3
"""
Smart Generation Monitor
========================
Monitors ComfyUI API for generation completion and provides real-time status
"""

import time
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

class GenerationMonitor:
    """Monitors ComfyUI generation progress with smart completion detection"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8188"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def check_api_health(self) -> bool:
        """Check if ComfyUI API is responding"""
        try:
            response = self.session.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            response = self.session.get(f"{self.base_url}/queue")
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def get_generation_status(self, prompt_id: str) -> Dict[str, Any]:
        """Get status of specific generation"""
        try:
            response = self.session.get(f"{self.base_url}/history/{prompt_id}")
            if response.status_code == 200:
                data = response.json()
                if prompt_id in data:
                    return data[prompt_id]
            return {}
        except:
            return {}
    
    def wait_for_completion(
        self, 
        prompt_id: str, 
        timeout: int = 600,
        check_interval: float = 2.0,
        output_dir: Optional[Path] = None,
        expected_prefix: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Wait for generation to complete with multiple detection methods
        
        Returns:
            Dict with keys: success, completed, elapsed_time, status, output_files
        """
        
        start_time = time.time()
        last_file_count = 0
        
        print(f"🎨 Monitoring generation {prompt_id[:8]}...")
        
        while True:
            elapsed = time.time() - start_time
            
            # Check timeout
            if elapsed > timeout:
                return {
                    "success": False,
                    "completed": False,
                    "elapsed_time": elapsed,
                    "status": "timeout",
                    "output_files": []
                }
            
            # Method 1: Check API history
            status = self.get_generation_status(prompt_id)
            if status and "status" in status:
                api_status = status["status"]
                if "completed" in api_status and api_status["completed"]:
                    print(f"✅ Generation completed via API (elapsed: {elapsed:.1f}s)")
                    return {
                        "success": True,
                        "completed": True,
                        "elapsed_time": elapsed,
                        "status": "completed_api",
                        "output_files": self._find_output_files(output_dir, expected_prefix)
                    }
            
            # Method 2: Check output directory for new files
            if output_dir and expected_prefix:
                output_files = self._find_output_files(output_dir, expected_prefix)
                if len(output_files) > last_file_count:
                    # New file appeared, wait a moment for completion
                    time.sleep(1.0)
                    final_files = self._find_output_files(output_dir, expected_prefix)
                    if len(final_files) == len(output_files):  # No more new files
                        print(f"✅ Generation completed via file detection (elapsed: {elapsed:.1f}s)")
                        return {
                            "success": True,
                            "completed": True,
                            "elapsed_time": elapsed,
                            "status": "completed_file",
                            "output_files": final_files
                        }
                    last_file_count = len(final_files)
            
            # Method 3: Check queue status
            queue = self.get_queue_status()
            if queue:
                running = queue.get("queue_running", [])
                pending = queue.get("queue_pending", [])
                
                # Check if our prompt is no longer in queue
                our_prompt_in_queue = any(
                    item.get("prompt_id") == prompt_id 
                    for item in running + pending
                )
                
                if not our_prompt_in_queue and elapsed > 5:  # Give it time to start
                    # Not in queue anymore, likely completed
                    time.sleep(2.0)  # Wait for file write
                    output_files = self._find_output_files(output_dir, expected_prefix) if output_dir else []
                    if output_files or not output_dir:
                        print(f"✅ Generation completed via queue status (elapsed: {elapsed:.1f}s)")
                        return {
                            "success": True,
                            "completed": True,
                            "elapsed_time": elapsed,
                            "status": "completed_queue",
                            "output_files": output_files
                        }
            
            # Progress indicator
            if int(elapsed) % 10 == 0 and elapsed > 0:
                print(f"⏳ Still generating... ({elapsed:.0f}s elapsed)")
            
            time.sleep(check_interval)
    
    def _find_output_files(self, output_dir: Path, prefix: str) -> list:
        """Find output files matching the expected pattern"""
        if not output_dir or not prefix:
            return []
        
        try:
            pattern = f"{prefix}*.png"
            files = list(output_dir.glob(pattern))
            # Sort by modification time, newest first
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return [str(f) for f in files]
        except:
            return []

def main():
    parser = argparse.ArgumentParser(description="Monitor ComfyUI generation")
    parser.add_argument("prompt_id", help="Prompt ID to monitor")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    parser.add_argument("--output-dir", type=Path, help="Output directory to monitor")
    parser.add_argument("--prefix", help="Expected file prefix")
    parser.add_argument("--url", default="http://127.0.0.1:8188", help="ComfyUI API URL")
    
    args = parser.parse_args()
    
    monitor = GenerationMonitor(args.url)
    
    # Check API health
    if not monitor.check_api_health():
        print("❌ ComfyUI API not responding")
        return 1
    
    # Monitor generation
    result = monitor.wait_for_completion(
        args.prompt_id,
        timeout=args.timeout,
        output_dir=args.output_dir,
        expected_prefix=args.prefix
    )
    
    if result["success"]:
        print(f"🎉 Generation successful!")
        print(f"   Method: {result['status']}")
        print(f"   Time: {result['elapsed_time']:.1f}s")
        if result["output_files"]:
            print(f"   Files: {len(result['output_files'])} generated")
            for f in result["output_files"][:3]:  # Show first 3
                print(f"     - {Path(f).name}")
        return 0
    else:
        print(f"❌ Generation failed: {result['status']}")
        print(f"   Time: {result['elapsed_time']:.1f}s")
        return 1

if __name__ == "__main__":
    exit(main())