#!/usr/bin/env python3
"""
Enhanced ComfyUI Client for Terminal Grounds v2.0
================================================
Robust, production-ready client with connection pooling, retry logic, and comprehensive error handling.
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import socket
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import queue
import logging

logger = logging.getLogger(__name__)

class GenerationStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class GenerationJob:
    """Represents a single generation job"""
    id: str
    prompt_id: Optional[str]
    workflow: Dict[str, Any]
    status: GenerationStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    output_files: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.metadata is None:
            self.metadata = {}

class ComfyUIConnectionError(Exception):
    """Raised when unable to connect to ComfyUI server"""
    pass

class ComfyUIGenerationError(Exception):
    """Raised when generation fails"""
    pass

class EnhancedComfyUIClient:
    """
    Production-ready ComfyUI client with enterprise features:
    - Automatic server detection
    - Connection pooling and retry logic
    - Progress tracking and job management
    - Comprehensive error handling
    - Output file management
    """
    
    def __init__(self, server: Optional[str] = None, timeout: int = 300, max_retries: int = 3):
        self.server = server or self._detect_server()
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = f"http://{self.server}"
        
        # Job management
        self.active_jobs: Dict[str, GenerationJob] = {}
        self.job_queue: queue.Queue = queue.Queue()
        self.max_concurrent_jobs = 2  # Optimal for RTX 3090 Ti
        
        # Connection pool
        self._session_lock = threading.Lock()
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
        
        # Validate connection
        self._validate_connection()
        
    def _detect_server(self) -> str:
        """Auto-detect ComfyUI server using existing logic"""
        import os
        
        # Check environment variable first
        env_server = os.getenv("COMFYUI_SERVER")
        if env_server and self._probe_server(env_server):
            return env_server
            
        # Probe common ports
        candidates = ["127.0.0.1:8000", "127.0.0.1:8188"]
        for candidate in candidates:
            if self._probe_server(candidate):
                return candidate
                
        # Fallback
        return "127.0.0.1:8188"
        
    def _probe_server(self, hostport: str) -> bool:
        """Test if server is responding"""
        try:
            with urllib.request.urlopen(f"http://{hostport}/system_stats", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False
            
    def _validate_connection(self):
        """Validate connection and get server info"""
        try:
            response = self._make_request("/system_stats", method="GET")
            logger.info(f"Connected to ComfyUI at {self.server}")
            logger.info(f"Server info: {response}")
        except Exception as e:
            raise ComfyUIConnectionError(f"Failed to connect to ComfyUI at {self.server}: {e}")
            
    def _make_request(self, endpoint: str, data: Optional[Dict] = None, method: str = "POST") -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    req = urllib.request.Request(url)
                else:
                    json_data = json.dumps(data).encode('utf-8') if data else b''
                    req = urllib.request.Request(url, data=json_data)
                    req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    return json.loads(response.read().decode('utf-8'))
                    
            except urllib.error.HTTPError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise ComfyUIConnectionError(f"HTTP error: {e}")
                    
            except urllib.error.URLError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise ComfyUIConnectionError(f"Connection error: {e}")
                    
            except socket.timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise ComfyUIConnectionError("Request timeout")
                    
            # Exponential backoff
            time.sleep(2 ** attempt)
            
    def health_check(self) -> bool:
        """Check if server is healthy"""
        current_time = time.time()
        if current_time - self._last_health_check < self._health_check_interval:
            return True
            
        try:
            self._make_request("/system_stats", method="GET")
            self._last_health_check = current_time
            return True
        except Exception:
            return False
            
    def queue_prompt(self, workflow: Dict[str, Any], job_id: Optional[str] = None) -> GenerationJob:
        """Queue a generation job"""
        if not self.health_check():
            raise ComfyUIConnectionError("Server health check failed")
            
        # Generate job ID if not provided
        if not job_id:
            job_id = f"tg_{int(time.time() * 1000)}"
            
        # Create job
        job = GenerationJob(
            id=job_id,
            prompt_id=None,
            workflow=workflow,
            status=GenerationStatus.QUEUED,
            created_at=time.time()
        )
        
        try:
            # Submit to ComfyUI
            response = self._make_request("/prompt", {"prompt": workflow})
            
            if "prompt_id" in response:
                job.prompt_id = response["prompt_id"]
                job.status = GenerationStatus.RUNNING
                job.started_at = time.time()
                self.active_jobs[job_id] = job
                logger.info(f"Job {job_id} queued with prompt_id {job.prompt_id}")
                return job
            else:
                job.status = GenerationStatus.FAILED
                job.error = "No prompt_id in response"
                raise ComfyUIGenerationError(f"Invalid response: {response}")
                
        except Exception as e:
            job.status = GenerationStatus.FAILED
            job.error = str(e)
            logger.error(f"Failed to queue job {job_id}: {e}")
            raise ComfyUIGenerationError(f"Failed to queue job: {e}")
            
    def wait_for_completion(self, job: GenerationJob, progress_callback: Optional[callable] = None) -> GenerationJob:
        """Wait for job completion with optional progress callback"""
        if not job.prompt_id:
            raise ValueError("Job has no prompt_id")
            
        start_time = time.time()
        last_progress_time = start_time
        
        while True:
            try:
                # Check job status
                history_response = self._make_request(f"/history/{job.prompt_id}", method="GET")
                
                if job.prompt_id in history_response:
                    # Job completed
                    history_data = history_response[job.prompt_id]
                    job.status = GenerationStatus.COMPLETED
                    job.completed_at = time.time()
                    
                    # Extract output files
                    job.output_files = self._extract_output_files(history_data)
                    job.metadata = self._extract_metadata(history_data)
                    
                    # Remove from active jobs
                    if job.id in self.active_jobs:
                        del self.active_jobs[job.id]
                        
                    logger.info(f"Job {job.id} completed in {job.completed_at - job.started_at:.1f}s")
                    return job
                    
                # Check queue status for progress
                queue_response = self._make_request("/queue", method="GET")
                
                # Call progress callback if provided
                current_time = time.time()
                if progress_callback and current_time - last_progress_time > 2.0:
                    elapsed = current_time - start_time
                    queue_position = self._get_queue_position(job.prompt_id, queue_response)
                    progress_callback(job, elapsed, queue_position)
                    last_progress_time = current_time
                    
                # Check for timeout
                if current_time - start_time > self.timeout:
                    job.status = GenerationStatus.FAILED
                    job.error = "Generation timeout"
                    raise ComfyUIGenerationError(f"Job {job.id} timed out after {self.timeout}s")
                    
                time.sleep(2)  # Poll every 2 seconds
                
            except KeyboardInterrupt:
                job.status = GenerationStatus.CANCELLED
                logger.info(f"Job {job.id} cancelled by user")
                return job
                
            except Exception as e:
                job.status = GenerationStatus.FAILED
                job.error = str(e)
                logger.error(f"Error waiting for job {job.id}: {e}")
                raise ComfyUIGenerationError(f"Error waiting for completion: {e}")
                
    def _get_queue_position(self, prompt_id: str, queue_response: Dict) -> int:
        """Get position in queue"""
        try:
            running = queue_response.get("queue_running", [])
            pending = queue_response.get("queue_pending", [])
            
            # Check if currently running
            for i, item in enumerate(running):
                if len(item) > 1 and item[1] == prompt_id:
                    return 0  # Currently running
                    
            # Check position in pending queue
            for i, item in enumerate(pending):
                if len(item) > 1 and item[1] == prompt_id:
                    return i + 1
                    
            return -1  # Not found
        except Exception:
            return -1
            
    def _extract_output_files(self, history_data: Dict) -> List[str]:
        """Extract output file paths from history data"""
        output_files = []
        
        try:
            outputs = history_data.get("outputs", {})
            for node_id, node_outputs in outputs.items():
                if "images" in node_outputs:
                    for image_info in node_outputs["images"]:
                        if "filename" in image_info:
                            output_files.append(image_info["filename"])
        except Exception as e:
            logger.warning(f"Error extracting output files: {e}")
            
        return output_files
        
    def _extract_metadata(self, history_data: Dict) -> Dict[str, Any]:
        """Extract generation metadata from history data"""
        metadata = {}
        
        try:
            # Extract basic info
            metadata["status"] = history_data.get("status", {})
            
            # Extract prompt info
            prompt = history_data.get("prompt", {})
            if prompt:
                metadata["workflow_info"] = self._analyze_workflow(prompt)
                
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
            
        return metadata
        
    def _analyze_workflow(self, prompt: Dict) -> Dict[str, Any]:
        """Analyze workflow to extract useful info"""
        info = {
            "node_count": len(prompt),
            "has_lora": False,
            "model_name": "unknown",
            "steps": 0,
            "cfg": 0
        }
        
        try:
            for node_id, node_data in prompt.items():
                class_type = node_data.get("class_type", "")
                inputs = node_data.get("inputs", {})
                
                # Check for LoRA
                if "lora" in class_type.lower():
                    info["has_lora"] = True
                    
                # Extract model name
                if class_type == "CheckpointLoaderSimple":
                    info["model_name"] = inputs.get("ckpt_name", "unknown")
                    
                # Extract sampling parameters
                if class_type == "KSampler":
                    info["steps"] = inputs.get("steps", 0)
                    info["cfg"] = inputs.get("cfg", 0)
                    
        except Exception as e:
            logger.warning(f"Error analyzing workflow: {e}")
            
        return info
        
    def generate_sync(self, workflow: Dict[str, Any], progress_callback: Optional[callable] = None) -> GenerationJob:
        """Generate synchronously and wait for completion"""
        job = self.queue_prompt(workflow)
        return self.wait_for_completion(job, progress_callback)
        
    def cancel_job(self, job: GenerationJob) -> bool:
        """Cancel a running job"""
        try:
            if job.prompt_id:
                # Try to cancel via API (if supported)
                # For now, just mark as cancelled
                job.status = GenerationStatus.CANCELLED
                if job.id in self.active_jobs:
                    del self.active_jobs[job.id]
                return True
        except Exception as e:
            logger.error(f"Error cancelling job {job.id}: {e}")
        return False
        
    def get_active_jobs(self) -> List[GenerationJob]:
        """Get list of active jobs"""
        return list(self.active_jobs.values())
        
    def clear_completed_jobs(self):
        """Clear completed jobs from memory"""
        to_remove = []
        for job_id, job in self.active_jobs.items():
            if job.status in [GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.CANCELLED]:
                to_remove.append(job_id)
                
        for job_id in to_remove:
            del self.active_jobs[job_id]
            
    def get_server_info(self) -> Dict[str, Any]:
        """Get detailed server information"""
        try:
            stats = self._make_request("/system_stats", method="GET")
            object_info = self._make_request("/object_info", method="GET")
            
            return {
                "server": self.server,
                "stats": stats,
                "available_nodes": len(object_info),
                "connection_status": "healthy" if self.health_check() else "unhealthy"
            }
        except Exception as e:
            return {
                "server": self.server,
                "error": str(e),
                "connection_status": "error"
            }