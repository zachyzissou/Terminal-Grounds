"""
ComfyUI HTTP Client for Terminal Grounds
Minimal client for interacting with ComfyUI API at http://127.0.0.1:8000
"""
import json
import time
import os
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid
import base64

class ComfyClient:
    def __init__(self, base_url: str = None):
        self.base = base_url or os.environ.get("COMFY_BASE", "http://127.0.0.1:8000")
        self.base = self.base.rstrip('/')
        self.session = requests.Session()
        
    def queue_prompt(self, workflow: Dict[str, Any], client_id: str = None) -> Dict[str, Any]:
        """Queue a workflow prompt for execution"""
        if client_id is None:
            client_id = str(uuid.uuid4())
            
        payload = {
            "prompt": workflow,
            "client_id": client_id
        }
        
        try:
            response = self.session.post(
                f"{self.base}/prompt",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error queuing prompt: {e}")
            return None
    
    def get_history(self, prompt_id: str = None) -> Dict[str, Any]:
        """Get execution history, optionally for specific prompt"""
        url = f"{self.base}/history"
        if prompt_id:
            url = f"{url}/{prompt_id}"
            
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting history: {e}")
            return {}
    
    def wait_for_result(self, prompt_id: str, timeout: int = 600, poll_interval: float = 1.0) -> Optional[Dict]:
        """Wait for prompt execution to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            
            if prompt_id in history:
                status = history[prompt_id].get('status', {})
                if status.get('status_str') == 'success' and status.get('completed', False):
                    return history[prompt_id]
                elif status.get('status_str') == 'error':
                    print(f"Prompt failed with error: {status.get('messages', [])}")
                    return None
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Prompt {prompt_id} timed out after {timeout} seconds")
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Download generated image from ComfyUI"""
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        
        try:
            response = self.session.get(
                f"{self.base}/view",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            return None
    
    def upload_image(self, image_path: str, overwrite: bool = True) -> Optional[Dict]:
        """Upload an image to ComfyUI input folder"""
        path = Path(image_path)
        if not path.exists():
            print(f"Image not found: {image_path}")
            return None
        
        with open(path, 'rb') as f:
            files = {
                'image': (path.name, f, 'image/png')
            }
            data = {
                'overwrite': str(overwrite).lower()
            }
            
            try:
                response = self.session.post(
                    f"{self.base}/upload/image",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error uploading image: {e}")
                return None
    
    def interrupt(self) -> bool:
        """Interrupt current generation"""
        try:
            response = self.session.post(f"{self.base}/interrupt", timeout=5)
            response.raise_for_status()
            return True
        except:
            return False
    
    def get_queue(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            response = self.session.get(f"{self.base}/queue", timeout=5)
            response.raise_for_status()
            return response.json()
        except:
            return {"queue_running": [], "queue_pending": []}
    
    def clear_queue(self) -> bool:
        """Clear pending queue"""
        try:
            response = self.session.post(
                f"{self.base}/queue",
                json={"clear": True},
                timeout=5
            )
            response.raise_for_status()
            return True
        except:
            return False
    
    def get_models(self, model_type: str = "checkpoints") -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get(
                f"{self.base}/object_info",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract checkpoint models from the CheckpointLoaderSimple node
            if "CheckpointLoaderSimple" in data:
                loader_info = data["CheckpointLoaderSimple"]
                if "input" in loader_info and "required" in loader_info["input"]:
                    ckpt_info = loader_info["input"]["required"].get("ckpt_name", [])
                    if ckpt_info and len(ckpt_info) > 0:
                        return ckpt_info[0]
            
            return []
        except:
            return []
    
    def test_connection(self) -> bool:
        """Test if ComfyUI server is reachable"""
        try:
            response = self.session.get(f"{self.base}/system_stats", timeout=2)
            return response.status_code == 200
        except:
            return False


# Simple test function
def test_client():
    client = ComfyClient()
    
    print(f"Testing connection to {client.base}...")
    if client.test_connection():
        print("✅ ComfyUI server is running")
        
        # Get available models
        models = client.get_models()
        if models:
            print(f"\n📦 Available models: {', '.join(models[:5])}")
        
        # Check queue
        queue = client.get_queue()
        print(f"\n📊 Queue status:")
        print(f"  Running: {len(queue.get('queue_running', []))}")
        print(f"  Pending: {len(queue.get('queue_pending', []))}")
    else:
        print("❌ ComfyUI server is not reachable")
        print("Please ensure ComfyUI is running at http://127.0.0.1:8000")


if __name__ == "__main__":
    test_client()
