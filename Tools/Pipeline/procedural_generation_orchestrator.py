#!/usr/bin/env python3
"""
Terminal Grounds Procedural Generation Orchestrator
Enterprise-grade automated pipeline connecting UE5, ComfyUI, and Territorial Systems

Author: DevOps Engineer
Version: 1.0.0
"""

import asyncio
import json
import logging
import sqlite3
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import queue
import websockets
import sys
import traceback

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procedural_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProceduralOrchestrator")

# Pipeline Configuration
class Config:
    """Centralized configuration for the pipeline"""
    
    # Service endpoints
    COMFYUI_HOST = "127.0.0.1"
    COMFYUI_PORT = 8188
    WEBSOCKET_HOST = "127.0.0.1"
    WEBSOCKET_PORT = 8765
    
    # Database paths
    TERRITORIAL_DB = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
    PIPELINE_DB = Path("C:/Users/Zachg/Terminal-Grounds/Database/pipeline_state.db")
    
    # Asset paths
    OUTPUT_DIR = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
    PROCEDURAL_DIR = OUTPUT_DIR / "procedural"
    
    # Generation parameters (100% success rate proven)
    PROVEN_PARAMS = {
        "sampler": "heun",
        "scheduler": "normal",
        "cfg": 3.2,
        "steps": 25,
        "width": 1536,
        "height": 864
    }
    
    # Performance tuning
    MAX_CONCURRENT_GENERATIONS = 3
    GENERATION_TIMEOUT = 600  # 10 minutes
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5
    HEALTH_CHECK_INTERVAL = 30
    
    # Queue management
    MAX_QUEUE_SIZE = 100
    BATCH_SIZE = 10
    BATCH_DELAY = 2

class GenerationType(Enum):
    """Types of procedural generation"""
    ENVIRONMENT = "environment"
    BUILDING = "building"
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    CHARACTER = "character"
    EMBLEM = "emblem"
    UI_ELEMENT = "ui_element"
    TERRITORIAL_MARKER = "territorial_marker"

class GenerationStatus(Enum):
    """Status of generation requests"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class GenerationRequest:
    """Structured generation request"""
    request_id: str
    generation_type: GenerationType
    faction_id: Optional[str]
    region_id: Optional[str]
    territory_id: Optional[int]
    prompt_data: Dict[str, Any]
    metadata: Dict[str, Any]
    priority: int = 5
    status: GenerationStatus = GenerationStatus.PENDING
    attempts: int = 0
    created_at: str = ""
    completed_at: Optional[str] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class ServiceHealthMonitor:
    """Monitor health of all connected services"""
    
    def __init__(self):
        self.services = {
            "comfyui": False,
            "websocket": False,
            "database": False
        }
        self.last_check = {}
        self.error_counts = {}
        
    async def check_comfyui(self) -> bool:
        """Check ComfyUI service health"""
        try:
            url = f"http://{Config.COMFYUI_HOST}:{Config.COMFYUI_PORT}/system_stats"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    self.services["comfyui"] = True
                    self.error_counts["comfyui"] = 0
                    return True
        except Exception as e:
            self.error_counts["comfyui"] = self.error_counts.get("comfyui", 0) + 1
            logger.error(f"ComfyUI health check failed: {e}")
            self.services["comfyui"] = False
        return False
    
    async def check_websocket(self) -> bool:
        """Check WebSocket server health"""
        try:
            uri = f"ws://{Config.WEBSOCKET_HOST}:{Config.WEBSOCKET_PORT}"
            async with websockets.connect(uri, timeout=5) as websocket:
                await websocket.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                if data.get("type") == "pong":
                    self.services["websocket"] = True
                    self.error_counts["websocket"] = 0
                    return True
        except Exception as e:
            self.error_counts["websocket"] = self.error_counts.get("websocket", 0) + 1
            logger.warning(f"WebSocket health check failed: {e}")
            self.services["websocket"] = False
        return False
    
    def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            conn = sqlite3.connect(str(Config.TERRITORIAL_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM territories")
            cursor.fetchone()
            conn.close()
            self.services["database"] = True
            self.error_counts["database"] = 0
            return True
        except Exception as e:
            self.error_counts["database"] = self.error_counts.get("database", 0) + 1
            logger.error(f"Database health check failed: {e}")
            self.services["database"] = False
        return False
    
    async def run_health_checks(self):
        """Run all health checks"""
        await self.check_comfyui()
        await self.check_websocket()
        self.check_database()
        
        self.last_check = {
            service: datetime.now().isoformat()
            for service in self.services
        }
        
        return all(self.services.values())
    
    def get_status_report(self) -> Dict:
        """Get detailed health status report"""
        return {
            "services": self.services,
            "last_check": self.last_check,
            "error_counts": self.error_counts,
            "healthy": all(self.services.values())
        }

class ComfyUIGenerator:
    """Handle ComfyUI asset generation with proven parameters"""
    
    def __init__(self):
        self.base_url = f"http://{Config.COMFYUI_HOST}:{Config.COMFYUI_PORT}"
        self.active_generations = {}
        self.completion_queue = queue.Queue()
        
    def create_workflow(self, request: GenerationRequest) -> Dict:
        """Create ComfyUI workflow from request using proven parameters"""
        
        # Base workflow structure (proven 100% success)
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": self._get_model_for_type(request.generation_type)
                }
            }
        }
        
        # Build prompt based on type
        positive_prompt = self._build_positive_prompt(request)
        negative_prompt = self._build_negative_prompt(request.generation_type)
        
        # Add text encoding nodes
        workflow["2"] = {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive_prompt,
                "clip": ["1", 1]
            }
        }
        
        workflow["3"] = {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": ["1", 1]
            }
        }
        
        # Determine resolution based on type
        width, height = self._get_resolution_for_type(request.generation_type)
        
        # Add sampler with proven parameters
        workflow["4"] = {
            "class_type": "KSampler",
            "inputs": {
                "seed": request.metadata.get("seed", int(time.time() * 1000) % 2**32),
                "steps": Config.PROVEN_PARAMS["steps"],
                "cfg": Config.PROVEN_PARAMS["cfg"],
                "sampler_name": Config.PROVEN_PARAMS["sampler"],
                "scheduler": Config.PROVEN_PARAMS["scheduler"],
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["5", 0]
            }
        }
        
        # Add latent image
        workflow["5"] = {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        }
        
        # Add VAE decode
        workflow["6"] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["4", 0],
                "vae": ["1", 2]
            }
        }
        
        # Add save node
        filename_prefix = f"TG_{request.generation_type.value}_{request.request_id}"
        workflow["7"] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": filename_prefix
            }
        }
        
        return {"prompt": workflow}
    
    def _get_model_for_type(self, gen_type: GenerationType) -> str:
        """Select appropriate model based on generation type"""
        models = {
            GenerationType.ENVIRONMENT: "FLUX1-dev-fp8.safetensors",
            GenerationType.BUILDING: "FLUX1-dev-fp8.safetensors",
            GenerationType.VEHICLE: "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            GenerationType.WEAPON: "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            GenerationType.CHARACTER: "FLUX1-dev-fp8.safetensors",
            GenerationType.EMBLEM: "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            GenerationType.UI_ELEMENT: "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            GenerationType.TERRITORIAL_MARKER: "FLUX1-dev-fp8.safetensors"
        }
        return models.get(gen_type, "FLUX1-dev-fp8.safetensors")
    
    def _get_resolution_for_type(self, gen_type: GenerationType) -> Tuple[int, int]:
        """Get optimal resolution for generation type"""
        resolutions = {
            GenerationType.ENVIRONMENT: (1536, 864),
            GenerationType.BUILDING: (1024, 1024),
            GenerationType.VEHICLE: (1024, 1024),
            GenerationType.WEAPON: (1024, 1024),
            GenerationType.CHARACTER: (768, 1024),
            GenerationType.EMBLEM: (1024, 1024),
            GenerationType.UI_ELEMENT: (1920, 1080),
            GenerationType.TERRITORIAL_MARKER: (512, 512)
        }
        return resolutions.get(gen_type, (1024, 1024))
    
    def _build_positive_prompt(self, request: GenerationRequest) -> str:
        """Build positive prompt from request data"""
        base_prompts = {
            GenerationType.ENVIRONMENT: "Terminal Grounds environment, post-apocalyptic industrial facility, weathered concrete structures, rusted metal machinery",
            GenerationType.BUILDING: "Terminal Grounds faction building, fortified structure, post-apocalyptic architecture, defensive position",
            GenerationType.VEHICLE: "military vehicle concept art, Terminal Grounds faction vehicle, post-apocalyptic combat transport, weathered armored vehicle",
            GenerationType.WEAPON: "weapon concept art, Terminal Grounds weapon design, post-apocalyptic firearm, weathered military equipment",
            GenerationType.CHARACTER: "Terminal Grounds operator, faction soldier, post-apocalyptic survivor, tactical gear",
            GenerationType.EMBLEM: "military faction emblem, Terminal Grounds faction logo, minimalist tactical insignia, clean vector design",
            GenerationType.UI_ELEMENT: "Terminal Grounds HUD element, tactical interface, military UI design, clean futuristic display",
            GenerationType.TERRITORIAL_MARKER: "territorial control marker, faction flag, zone boundary indicator, strategic position marker"
        }
        
        base = base_prompts.get(request.generation_type, "Terminal Grounds concept art")
        
        # Add faction-specific elements
        if request.faction_id:
            base += f", {request.faction_id} faction aesthetic"
        
        # Add region-specific elements
        if request.region_id:
            base += f", {request.region_id} environment characteristics"
        
        # Add custom prompt data
        if request.prompt_data.get("additional_prompt"):
            base += f", {request.prompt_data['additional_prompt']}"
        
        # Add quality modifiers
        base += ", sharp focus, high detail, professional concept art, game asset quality"
        
        return base
    
    def _build_negative_prompt(self, gen_type: GenerationType) -> str:
        """Build negative prompt for generation type"""
        base = "blurry, soft focus, low quality, amateur, placeholder art"
        
        # Type-specific negatives
        if gen_type in [GenerationType.VEHICLE, GenerationType.UI_ELEMENT]:
            # Critical fix for text corruption
            base += ", text, letters, numbers, symbols, writing, inscriptions, labels, signage, gibberish text, scrambled letters, unreadable markings"
        
        if gen_type == GenerationType.UI_ELEMENT:
            # Copyright protection
            base += ", call of duty, apex legends, battlefield, warzone, fortnite, destiny, halo, overwatch, copyrighted UI"
        
        return base
    
    async def submit_generation(self, request: GenerationRequest) -> bool:
        """Submit generation request to ComfyUI"""
        try:
            workflow = self.create_workflow(request)
            
            # Submit to ComfyUI
            url = f"{self.base_url}/prompt"
            data = json.dumps(workflow).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    result = json.loads(response.read())
                    prompt_id = result.get('prompt_id')
                    
                    if prompt_id:
                        self.active_generations[prompt_id] = request
                        logger.info(f"Submitted generation {request.request_id} -> ComfyUI {prompt_id}")
                        return True
                    
        except Exception as e:
            logger.error(f"Failed to submit generation {request.request_id}: {e}")
            
        return False
    
    async def check_completion(self, prompt_id: str) -> Optional[str]:
        """Check if generation is complete and return output path"""
        try:
            url = f"{self.base_url}/history/{prompt_id}"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read())
                    
                    if prompt_id in data:
                        outputs = data[prompt_id].get('outputs', {})
                        
                        # Find saved image
                        for node_id, output in outputs.items():
                            if 'images' in output:
                                for image in output['images']:
                                    filename = image.get('filename')
                                    if filename:
                                        return str(Config.OUTPUT_DIR / filename)
                                        
        except urllib.error.HTTPError as e:
            if e.code != 404:  # 404 means not ready yet
                logger.error(f"Error checking completion for {prompt_id}: {e}")
        except Exception as e:
            logger.error(f"Error checking completion for {prompt_id}: {e}")
            
        return None
    
    async def monitor_generations(self):
        """Monitor active generations for completion"""
        while True:
            completed = []
            
            for prompt_id, request in list(self.active_generations.items()):
                output_path = await self.check_completion(prompt_id)
                
                if output_path:
                    request.output_path = output_path
                    request.status = GenerationStatus.COMPLETED
                    request.completed_at = datetime.now().isoformat()
                    
                    self.completion_queue.put(request)
                    completed.append(prompt_id)
                    
                    logger.info(f"Generation completed: {request.request_id} -> {output_path}")
            
            # Remove completed generations
            for prompt_id in completed:
                del self.active_generations[prompt_id]
            
            await asyncio.sleep(2)

class TerritorialIntegration:
    """Integration with territorial control system"""
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to territorial WebSocket server"""
        try:
            uri = f"ws://{Config.WEBSOCKET_HOST}:{Config.WEBSOCKET_PORT}"
            self.websocket = await websockets.connect(uri)
            self.connected = True
            logger.info("Connected to territorial WebSocket server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to territorial server: {e}")
            self.connected = False
            return False
    
    async def listen_for_events(self, callback):
        """Listen for territorial events and trigger generation"""
        if not self.connected:
            await self.connect()
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                event_type = data.get('type')
                
                if event_type == 'territory_control_changed':
                    # Territory control changed - generate new assets
                    await callback(data)
                elif event_type == 'territorial_contest':
                    # Territory being contested - might need battle assets
                    await callback(data)
                    
        except Exception as e:
            logger.error(f"Error listening to territorial events: {e}")
            self.connected = False
    
    async def notify_generation_complete(self, request: GenerationRequest):
        """Notify territorial system of completed asset generation"""
        if not self.connected:
            return
        
        try:
            notification = {
                "type": "asset_generated",
                "request_id": request.request_id,
                "territory_id": request.territory_id,
                "faction_id": request.faction_id,
                "asset_type": request.generation_type.value,
                "output_path": request.output_path,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(notification))
            
        except Exception as e:
            logger.error(f"Failed to notify territorial system: {e}")

class PipelineOrchestrator:
    """Main orchestrator for the procedural generation pipeline"""
    
    def __init__(self):
        self.health_monitor = ServiceHealthMonitor()
        self.generator = ComfyUIGenerator()
        self.territorial = TerritorialIntegration()
        
        self.request_queue = asyncio.Queue(maxsize=Config.MAX_QUEUE_SIZE)
        self.retry_queue = asyncio.Queue()
        self.completion_handlers = []
        
        self.stats = {
            "total_requests": 0,
            "completed": 0,
            "failed": 0,
            "retried": 0,
            "average_time": 0
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize all pipeline components"""
        logger.info("Initializing Procedural Generation Pipeline...")
        
        # Ensure directories exist
        Config.PROCEDURAL_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Check service health
        healthy = await self.health_monitor.run_health_checks()
        
        if not healthy:
            logger.warning("Some services are not healthy:")
            logger.warning(json.dumps(self.health_monitor.get_status_report(), indent=2))
            
            # Allow pipeline to run with degraded functionality
            if not self.health_monitor.services["comfyui"]:
                raise Exception("ComfyUI is required for pipeline operation")
        
        # Connect to territorial system if available
        if self.health_monitor.services["websocket"]:
            await self.territorial.connect()
        
        logger.info("Pipeline initialized successfully")
        return True
    
    def _init_database(self):
        """Initialize pipeline state database"""
        conn = sqlite3.connect(str(Config.PIPELINE_DB))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_requests (
                request_id TEXT PRIMARY KEY,
                generation_type TEXT,
                faction_id TEXT,
                region_id TEXT,
                territory_id INTEGER,
                prompt_data TEXT,
                metadata TEXT,
                priority INTEGER,
                status TEXT,
                attempts INTEGER,
                created_at TEXT,
                completed_at TEXT,
                output_path TEXT,
                error_message TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_stats (
                stat_name TEXT PRIMARY KEY,
                stat_value REAL,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def submit_request(self, request: GenerationRequest):
        """Submit a new generation request"""
        request.status = GenerationStatus.QUEUED
        
        # Store in database
        self._store_request(request)
        
        # Add to queue
        await self.request_queue.put(request)
        
        self.stats["total_requests"] += 1
        
        logger.info(f"Request {request.request_id} queued (priority: {request.priority})")
    
    def _store_request(self, request: GenerationRequest):
        """Store request in database"""
        conn = sqlite3.connect(str(Config.PIPELINE_DB))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO generation_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.request_id,
            request.generation_type.value,
            request.faction_id,
            request.region_id,
            request.territory_id,
            json.dumps(request.prompt_data),
            json.dumps(request.metadata),
            request.priority,
            request.status.value,
            request.attempts,
            request.created_at,
            request.completed_at,
            request.output_path,
            request.error_message
        ))
        
        conn.commit()
        conn.close()
    
    async def process_queue(self):
        """Process generation requests from queue"""
        active_generations = 0
        
        while self.running:
            try:
                # Check if we can process more
                if active_generations >= Config.MAX_CONCURRENT_GENERATIONS:
                    await asyncio.sleep(1)
                    continue
                
                # Get next request
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )
                
                request.status = GenerationStatus.PROCESSING
                request.attempts += 1
                
                # Submit to ComfyUI
                success = await self.generator.submit_generation(request)
                
                if success:
                    active_generations += 1
                    self._store_request(request)
                else:
                    await self._handle_generation_failure(request)
                
            except asyncio.TimeoutError:
                # No requests in queue
                pass
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                
            # Check for completions
            try:
                while not self.generator.completion_queue.empty():
                    completed = self.generator.completion_queue.get_nowait()
                    active_generations -= 1
                    await self._handle_completion(completed)
            except queue.Empty:
                pass
    
    async def _handle_generation_failure(self, request: GenerationRequest):
        """Handle failed generation with retry logic"""
        if request.attempts < Config.RETRY_ATTEMPTS:
            request.status = GenerationStatus.RETRYING
            self.stats["retried"] += 1
            
            # Exponential backoff
            delay = Config.RETRY_DELAY * (2 ** (request.attempts - 1))
            await asyncio.sleep(delay)
            
            # Re-queue for retry
            await self.retry_queue.put(request)
            
            logger.warning(f"Retrying request {request.request_id} (attempt {request.attempts}/{Config.RETRY_ATTEMPTS})")
        else:
            request.status = GenerationStatus.FAILED
            request.error_message = f"Failed after {Config.RETRY_ATTEMPTS} attempts"
            self.stats["failed"] += 1
            
            self._store_request(request)
            
            logger.error(f"Request {request.request_id} failed permanently")
    
    async def _handle_completion(self, request: GenerationRequest):
        """Handle completed generation"""
        self.stats["completed"] += 1
        
        # Update database
        self._store_request(request)
        
        # Notify territorial system
        if self.territorial.connected:
            await self.territorial.notify_generation_complete(request)
        
        # Call completion handlers
        for handler in self.completion_handlers:
            try:
                await handler(request)
            except Exception as e:
                logger.error(f"Error in completion handler: {e}")
        
        logger.info(f"Generation complete: {request.request_id} -> {request.output_path}")
    
    async def handle_territorial_event(self, event_data: Dict):
        """Handle territorial control events"""
        event_type = event_data.get('type')
        territory_id = event_data.get('territory_id')
        faction_id = event_data.get('controller_faction_id')
        
        logger.info(f"Territorial event: {event_type} for territory {territory_id}")
        
        # Generate appropriate assets based on event
        if event_type == 'territory_control_changed':
            # Generate new territorial markers
            marker_request = GenerationRequest(
                request_id=f"territorial_marker_{territory_id}_{int(time.time())}",
                generation_type=GenerationType.TERRITORIAL_MARKER,
                faction_id=faction_id,
                territory_id=territory_id,
                prompt_data={
                    "additional_prompt": f"territorial control marker for {faction_id}"
                },
                metadata={
                    "event_type": event_type,
                    "triggered_by": "territorial_system"
                },
                priority=8  # High priority for real-time events
            )
            
            await self.submit_request(marker_request)
            
            # Generate faction building
            building_request = GenerationRequest(
                request_id=f"faction_building_{territory_id}_{int(time.time())}",
                generation_type=GenerationType.BUILDING,
                faction_id=faction_id,
                territory_id=territory_id,
                prompt_data={
                    "additional_prompt": f"{faction_id} command post"
                },
                metadata={
                    "event_type": event_type,
                    "triggered_by": "territorial_system"
                },
                priority=7
            )
            
            await self.submit_request(building_request)
    
    async def process_retry_queue(self):
        """Process retry queue with backoff"""
        while self.running:
            try:
                request = await asyncio.wait_for(
                    self.retry_queue.get(),
                    timeout=1.0
                )
                
                # Re-submit to main queue
                await self.request_queue.put(request)
                
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                logger.error(f"Error processing retry queue: {e}")
    
    async def health_check_loop(self):
        """Periodic health checking"""
        while self.running:
            await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)
            
            await self.health_monitor.run_health_checks()
            
            # Log health status
            status = self.health_monitor.get_status_report()
            if not status["healthy"]:
                logger.warning(f"Health check warning: {json.dumps(status, indent=2)}")
                
                # Attempt recovery
                if not self.health_monitor.services["websocket"] and self.territorial.connected:
                    logger.info("Attempting to reconnect to territorial server...")
                    await self.territorial.connect()
    
    async def run(self):
        """Main pipeline execution loop"""
        self.running = True
        
        logger.info("Starting Procedural Generation Pipeline")
        
        # Start all async tasks
        tasks = [
            asyncio.create_task(self.process_queue()),
            asyncio.create_task(self.process_retry_queue()),
            asyncio.create_task(self.generator.monitor_generations()),
            asyncio.create_task(self.health_check_loop())
        ]
        
        # Start territorial listener if connected
        if self.territorial.connected:
            tasks.append(
                asyncio.create_task(
                    self.territorial.listen_for_events(self.handle_territorial_event)
                )
            )
        
        # Run until stopped
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            traceback.print_exc()
        finally:
            self.running = False
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            
            # Save final stats
            self._save_stats()
    
    def _save_stats(self):
        """Save pipeline statistics"""
        conn = sqlite3.connect(str(Config.PIPELINE_DB))
        cursor = conn.cursor()
        
        for stat_name, stat_value in self.stats.items():
            cursor.execute("""
                INSERT OR REPLACE INTO pipeline_stats VALUES (?, ?, ?)
            """, (stat_name, stat_value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Pipeline Statistics: {json.dumps(self.stats, indent=2)}")
    
    def get_status(self) -> Dict:
        """Get current pipeline status"""
        return {
            "running": self.running,
            "health": self.health_monitor.get_status_report(),
            "stats": self.stats,
            "queue_size": self.request_queue.qsize(),
            "retry_queue_size": self.retry_queue.qsize(),
            "active_generations": len(self.generator.active_generations)
        }

# Example usage and API
class PipelineAPI:
    """Simple API for interacting with the pipeline"""
    
    def __init__(self, orchestrator: PipelineOrchestrator):
        self.orchestrator = orchestrator
    
    async def generate_faction_assets(self, faction_id: str, count: int = 5):
        """Generate a set of assets for a faction"""
        requests = []
        
        # Generate various asset types
        asset_types = [
            GenerationType.BUILDING,
            GenerationType.VEHICLE,
            GenerationType.WEAPON,
            GenerationType.EMBLEM,
            GenerationType.CHARACTER
        ]
        
        for i in range(count):
            asset_type = asset_types[i % len(asset_types)]
            
            request = GenerationRequest(
                request_id=f"{faction_id}_{asset_type.value}_{int(time.time())}_{i}",
                generation_type=asset_type,
                faction_id=faction_id,
                prompt_data={},
                metadata={"batch": True, "index": i}
            )
            
            requests.append(request)
            await self.orchestrator.submit_request(request)
        
        return [r.request_id for r in requests]
    
    async def generate_territorial_batch(self, territory_data: List[Dict]):
        """Generate assets for multiple territories"""
        requests = []
        
        for territory in territory_data:
            request = GenerationRequest(
                request_id=f"territory_{territory['id']}_{int(time.time())}",
                generation_type=GenerationType.ENVIRONMENT,
                territory_id=territory['id'],
                faction_id=territory.get('faction_id'),
                region_id=territory.get('region_id'),
                prompt_data={
                    "additional_prompt": territory.get('description', '')
                },
                metadata=territory
            )
            
            requests.append(request)
            await self.orchestrator.submit_request(request)
        
        return [r.request_id for r in requests]

async def main():
    """Main entry point"""
    
    # Create orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Initialize
    if not await orchestrator.initialize():
        logger.error("Failed to initialize pipeline")
        return
    
    # Create API
    api = PipelineAPI(orchestrator)
    
    # Example: Generate faction assets
    print("Generating test assets for Directorate faction...")
    request_ids = await api.generate_faction_assets("Directorate", count=3)
    print(f"Submitted {len(request_ids)} generation requests")
    
    # Run pipeline
    await orchestrator.run()

if __name__ == "__main__":
    print("TERMINAL GROUNDS PROCEDURAL GENERATION PIPELINE")
    print("Enterprise-grade automated asset generation")
    print("Press Ctrl+C to stop")
    print()
    
    asyncio.run(main())