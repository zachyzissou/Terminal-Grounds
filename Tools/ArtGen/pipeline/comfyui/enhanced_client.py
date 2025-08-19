"""
Enhanced ComfyUI Client
======================

An improved version of the ComfyUI client with better error handling,
retry logic, connection pooling, and advanced features.
"""

from __future__ import annotations

import json
import pathlib
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..utils.logger import setup_logger


class ComfyUIError(Exception):
    """Base exception for ComfyUI-related errors."""
    pass


class ConnectionError(ComfyUIError):
    """ComfyUI connection error."""
    pass


class WorkflowError(ComfyUIError):
    """ComfyUI workflow execution error."""
    pass


class TimeoutError(ComfyUIError):
    """ComfyUI timeout error."""
    pass


class EnhancedComfyClient:
    """
    Enhanced ComfyUI API client with robust error handling and advanced features.
    
    Features:
    - Connection pooling and retry logic
    - Progress monitoring and cancellation
    - Queue management
    - Better error handling and logging
    - Concurrent job management
    """
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8188",
        timeout: float = 300.0,
        max_retries: int = 3,
        log_level: str = "INFO"
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = setup_logger("EnhancedComfyClient", log_level)
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Track active jobs
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info(f"Enhanced ComfyUI client initialized: {self.base_url}")
    
    def test_connection(self) -> bool:
        """Test connection to ComfyUI server."""
        try:
            response = self.session.get(
                f"{self.base_url}/system_stats",
                timeout=10
            )
            response.raise_for_status()
            self.logger.debug("ComfyUI connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"ComfyUI connection test failed: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get ComfyUI system statistics."""
        try:
            response = self.session.get(f"{self.base_url}/system_stats", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            raise ConnectionError(f"Unable to get system stats: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        try:
            response = self.session.get(f"{self.base_url}/queue", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get queue status: {e}")
            raise ConnectionError(f"Unable to get queue status: {e}")
    
    def queue_workflow(
        self,
        workflow: Dict[str, Any],
        client_id: Optional[str] = None
    ) -> str:
        """
        Queue a workflow for execution.
        
        Args:
            workflow: ComfyUI workflow specification
            client_id: Optional client identifier
            
        Returns:
            Prompt/job identifier
        """
        if not client_id:
            client_id = str(uuid.uuid4())
        
        payload = {
            "prompt": workflow,
            "client_id": client_id
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            prompt_id = result.get("prompt_id") or result.get("node_id")
            
            if not prompt_id:
                raise WorkflowError(f"No prompt_id in response: {result}")
            
            # Track the job
            self.active_jobs[prompt_id] = {
                "client_id": client_id,
                "queued_at": time.time(),
                "workflow": workflow,
                "status": "queued"
            }
            
            self.logger.info(f"Workflow queued successfully: {prompt_id}")
            return prompt_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to queue workflow: {e}")
            raise WorkflowError(f"Failed to queue workflow: {e}")
    
    def wait_for_images(
        self,
        prompt_id: str,
        output_dir: pathlib.Path,
        poll_interval: float = 2.0,
        timeout: float = 600.0,
        progress_callback: Optional[callable] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Wait for workflow completion and download generated images.
        
        Args:
            prompt_id: Job identifier
            output_dir: Output directory for images
            poll_interval: Polling interval in seconds
            timeout: Maximum wait time in seconds
            progress_callback: Optional progress callback function
            
        Returns:
            Tuple of (image_list, history_data)
        """
        self.logger.info(f"Waiting for workflow completion: {prompt_id}")
        
        start_time = time.time()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Update job status
        if prompt_id in self.active_jobs:
            self.active_jobs[prompt_id]["status"] = "waiting"
        
        while time.time() - start_time < timeout:
            try:
                # Check history for completion
                history_response = self.session.get(
                    f"{self.base_url}/history/{prompt_id}",
                    timeout=30
                )
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    
                    if history_data and prompt_id in history_data:
                        job_data = history_data[prompt_id]
                        
                        # Check if job completed
                        if job_data.get("status", {}).get("completed", False):
                            # Extract images from history
                            images = self._extract_images_from_history(job_data)
                            
                            if images:
                                # Download images
                                downloaded_images = self._download_images(images, output_dir)
                                
                                # Update job status
                                if prompt_id in self.active_jobs:
                                    self.active_jobs[prompt_id]["status"] = "completed"
                                    self.active_jobs[prompt_id]["completed_at"] = time.time()
                                
                                self.logger.info(
                                    f"Workflow completed: {len(downloaded_images)} images downloaded"
                                )
                                
                                return downloaded_images, history_data
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_info = self._extract_progress_info(job_data)
                            progress_callback(prompt_id, progress_info)
                
                # Check queue status for more detailed progress
                queue_status = self.get_queue_status()
                self._update_job_progress(prompt_id, queue_status)
                
            except Exception as e:
                self.logger.warning(f"Error checking workflow status: {e}")
            
            time.sleep(poll_interval)
        
        # Timeout reached
        if prompt_id in self.active_jobs:
            self.active_jobs[prompt_id]["status"] = "timeout"
        
        raise TimeoutError(f"Workflow {prompt_id} timed out after {timeout} seconds")
    
    def _extract_images_from_history(self, history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract image information from ComfyUI history data."""
        images = []
        
        outputs = history_data.get("outputs", {})
        for node_id, node_outputs in outputs.items():
            if isinstance(node_outputs, dict):
                node_images = node_outputs.get("images", [])
                for img in node_images:
                    if isinstance(img, dict) and "filename" in img:
                        images.append(img)
        
        return images
    
    def _download_images(
        self,
        images: List[Dict[str, Any]],
        output_dir: pathlib.Path
    ) -> List[Dict[str, Any]]:
        """Download images from ComfyUI server."""
        downloaded_images = []
        
        for img_info in images:
            try:
                filename = img_info["filename"]
                subfolder = img_info.get("subfolder", "")
                img_type = img_info.get("type", "output")
                
                # Construct download URL
                url = f"{self.base_url}/view"
                params = {
                    "filename": filename,
                    "type": img_type
                }
                if subfolder:
                    params["subfolder"] = subfolder
                
                # Download image
                response = self.session.get(url, params=params, timeout=60)
                response.raise_for_status()
                
                # Save to output directory
                output_path = output_dir / filename
                output_path.write_bytes(response.content)
                
                # Add local path info
                img_info["local_path"] = str(output_path)
                downloaded_images.append(img_info)
                
                self.logger.debug(f"Downloaded image: {filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to download image {img_info}: {e}")
        
        return downloaded_images
    
    def _extract_progress_info(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract progress information from job data."""
        # This is a simplified progress extraction
        # Real implementation would parse ComfyUI's progress format
        return {
            "status": job_data.get("status", {}),
            "current_node": job_data.get("current_node"),
            "progress_percent": 0  # Would calculate based on completed nodes
        }
    
    def _update_job_progress(self, prompt_id: str, queue_status: Dict[str, Any]):
        """Update job progress based on queue status."""
        if prompt_id not in self.active_jobs:
            return
        
        # Check if job is in running queue
        running = queue_status.get("queue_running", [])
        pending = queue_status.get("queue_pending", [])
        
        for job_info in running:
            if isinstance(job_info, list) and len(job_info) > 1:
                if job_info[1] == prompt_id:
                    self.active_jobs[prompt_id]["status"] = "running"
                    return
        
        for job_info in pending:
            if isinstance(job_info, list) and len(job_info) > 1:
                if job_info[1] == prompt_id:
                    self.active_jobs[prompt_id]["status"] = "pending"
                    return
    
    def cancel_job(self, prompt_id: str) -> bool:
        """Cancel a queued or running job."""
        try:
            payload = {"delete": [prompt_id]}
            response = self.session.post(
                f"{self.base_url}/queue",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            if prompt_id in self.active_jobs:
                self.active_jobs[prompt_id]["status"] = "cancelled"
            
            self.logger.info(f"Job cancelled: {prompt_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel job {prompt_id}: {e}")
            return False
    
    def get_job_status(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        return self.active_jobs.get(prompt_id)
    
    def clear_queue(self) -> bool:
        """Clear all pending jobs from the queue."""
        try:
            payload = {"clear": True}
            response = self.session.post(
                f"{self.base_url}/queue",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Mark all pending jobs as cancelled
            for job_id, job_info in self.active_jobs.items():
                if job_info["status"] in ["queued", "pending"]:
                    job_info["status"] = "cancelled"
            
            self.logger.info("Queue cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear queue: {e}")
            return False
    
    def interrupt_current(self) -> bool:
        """Interrupt the currently running job."""
        try:
            response = self.session.post(f"{self.base_url}/interrupt", timeout=30)
            response.raise_for_status()
            
            self.logger.info("Current job interrupted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to interrupt current job: {e}")
            return False
    
    def get_models(self) -> Dict[str, List[str]]:
        """Get available models from ComfyUI."""
        try:
            response = self.session.get(f"{self.base_url}/object_info", timeout=30)
            response.raise_for_status()
            
            object_info = response.json()
            models = {}
            
            # Extract model information
            if "CheckpointLoaderSimple" in object_info:
                checkpoint_info = object_info["CheckpointLoaderSimple"]
                if "input" in checkpoint_info and "required" in checkpoint_info["input"]:
                    ckpt_names = checkpoint_info["input"]["required"].get("ckpt_name", [])
                    if isinstance(ckpt_names, list) and len(ckpt_names) > 0:
                        models["checkpoints"] = ckpt_names[0] if isinstance(ckpt_names[0], list) else []
            
            return models
            
        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")
            return {}
    
    def shutdown(self):
        """Shutdown the client and cleanup resources."""
        self.logger.info("Shutting down Enhanced ComfyUI Client")
        
        # Cancel any active jobs
        for prompt_id in list(self.active_jobs.keys()):
            if self.active_jobs[prompt_id]["status"] in ["queued", "pending", "running"]:
                self.cancel_job(prompt_id)
        
        # Close session
        self.session.close()
        
        self.logger.info("Enhanced ComfyUI Client shutdown complete")


# Convenience function for simple workflow execution
def execute_simple_workflow(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 28,
    cfg: float = 6.5,
    model: str = "flux.1-dev",
    output_dir: pathlib.Path = None
) -> List[str]:
    """Execute a simple text-to-image workflow."""
    from .workflow_manager import create_simple_workflow
    
    client = EnhancedComfyClient()
    
    # Create simple workflow
    workflow = create_simple_workflow(model, steps, cfg)
    
    # Inject parameters
    for node in workflow.values():
        if node.get("class_type") == "CLIPTextEncode":
            if "text" in node["inputs"] and node["inputs"]["text"] == "":
                # First empty text node gets positive prompt
                node["inputs"]["text"] = prompt
                # Find negative prompt node
                for other_node in workflow.values():
                    if (other_node.get("class_type") == "CLIPTextEncode" and 
                        other_node != node and 
                        other_node["inputs"]["text"] == ""):
                        other_node["inputs"]["text"] = negative_prompt
                        break
                break
        elif node.get("class_type") == "EmptyLatentImage":
            node["inputs"]["width"] = width
            node["inputs"]["height"] = height
    
    # Execute workflow
    if not output_dir:
        output_dir = pathlib.Path.cwd() / "outputs"
    
    prompt_id = client.queue_workflow(workflow)
    images, _ = client.wait_for_images(prompt_id, output_dir)
    
    return [img["local_path"] for img in images]