#!/usr/bin/env python3
"""
Procedural Generation Bridge for Terminal Grounds

Connects UE5 Procedural Subsystem to ComfyUI generation pipeline
Handles real-time territorial events and asset generation requests

Author: Terminal Grounds Development Team
"""

import asyncio
import websockets
import json
import sqlite3
import requests
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    """Structure for generation requests from UE5"""
    request_id: str
    territory_id: int
    territory_type: str
    dominant_faction: str
    generation_type: str
    center_location: Dict[str, float]
    generation_radius: float
    random_seed: int
    metadata: Dict[str, Any]

@dataclass 
class GenerationResult:
    """Structure for generation results"""
    request_id: str
    success: bool
    asset_paths: List[str]
    metadata: Dict[str, Any]
    generation_time: float
    error_message: Optional[str] = None

class ProceduralGenerationBridge:
    """Main bridge service connecting all procedural components"""
    
    def __init__(self, 
                 websocket_port: int = 8766,
                 comfyui_port: int = 8188,
                 territorial_port: int = 8765,
                 database_path: str = "Database/territorial_system.db"):
        
        self.websocket_port = websocket_port
        self.comfyui_port = comfyui_port  
        self.territorial_port = territorial_port
        self.database_path = Path(database_path)
        
        # Service connections
        self.connected_clients = set()
        self.generation_queue = asyncio.Queue()
        self.active_generations = {}
        
        # Configuration
        self.proven_params = {
            "sampler": "heun",
            "scheduler": "normal", 
            "cfg": 3.2,
            "steps": 25,
            "resolution": [1536, 864]
        }
        
        # Asset cache
        self.asset_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("Procedural Generation Bridge initialized")

    async def start_services(self):
        """Start all bridge services"""
        logger.info("Starting Procedural Generation Bridge services...")
        
        # Validate prerequisites
        await self.validate_prerequisites()
        
        # Start WebSocket server for UE5 communication
        websocket_server = websockets.serve(
            self.handle_ue5_connection,
            "127.0.0.1", 
            self.websocket_port
        )
        
        # Start generation worker
        generation_worker = asyncio.create_task(self.process_generation_queue())
        
        # Start territorial event listener
        territorial_listener = asyncio.create_task(self.listen_territorial_events())
        
        logger.info(f"✓ WebSocket server running on port {self.websocket_port}")
        logger.info(f"✓ Generation worker started")
        logger.info(f"✓ Territorial listener started")
        
        # Run all services
        await asyncio.gather(
            websocket_server,
            generation_worker,
            territorial_listener
        )
    
    async def validate_prerequisites(self):
        """Validate all required services are available"""
        logger.info("Validating prerequisites...")
        
        # Check ComfyUI availability
        try:
            response = requests.get(f"http://127.0.0.1:{self.comfyui_port}/system_stats", timeout=5)
            if response.status_code == 200:
                logger.info("✓ ComfyUI is running")
            else:
                raise Exception(f"ComfyUI returned status {response.status_code}")
        except Exception as e:
            logger.error(f"✗ ComfyUI not available: {e}")
            raise
            
        # Check territorial database
        if not self.database_path.exists():
            logger.error(f"✗ Territorial database not found: {self.database_path}")
            raise FileNotFoundError(f"Database not found: {self.database_path}")
        
        logger.info("✓ Territorial database accessible")
        
        # Check procedural prompt engine
        prompt_engine_path = Path("Tools/Comfy/ComfyUI-API/procedural_prompt_engine.py")
        if not prompt_engine_path.exists():
            logger.error(f"✗ Procedural prompt engine not found: {prompt_engine_path}")
            raise FileNotFoundError(f"Prompt engine not found: {prompt_engine_path}")
            
        logger.info("✓ Procedural prompt engine available")
        
        # Create output directory if needed
        output_dir = Path("Tools/Comfy/ComfyUI-API/output/procedural")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("✓ Output directory ready")

    async def handle_ue5_connection(self, websocket, path):
        """Handle WebSocket connections from UE5"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.connected_clients.add(websocket)
        logger.info(f"UE5 client connected: {client_id}")
        
        try:
            async for message in websocket:
                await self.handle_ue5_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"UE5 client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling UE5 connection {client_id}: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def handle_ue5_message(self, websocket, message):
        """Process messages from UE5 Procedural Subsystem"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "generation_request":
                await self.handle_generation_request(websocket, data)
            elif message_type == "cache_query":
                await self.handle_cache_query(websocket, data)  
            elif message_type == "status_request":
                await self.handle_status_request(websocket, data)
            else:
                logger.warning(f"Unknown message type from UE5: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from UE5: {e}")
            await websocket.send(json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing UE5 message: {e}")
            await websocket.send(json.dumps({"error": str(e)}))

    async def handle_generation_request(self, websocket, data):
        """Handle procedural generation request from UE5"""
        try:
            # Parse generation request
            request = GenerationRequest(
                request_id=data["request_id"],
                territory_id=data["territory_id"],
                territory_type=data["territory_type"], 
                dominant_faction=data["dominant_faction"],
                generation_type=data["generation_type"],
                center_location=data["center_location"],
                generation_radius=data["generation_radius"],
                random_seed=data["random_seed"],
                metadata=data.get("metadata", {})
            )
            
            logger.info(f"Received generation request: {request.request_id} for territory {request.territory_id}")
            
            # Check cache first
            cache_key = self.build_cache_key(request)
            if cache_key in self.asset_cache:
                logger.info(f"Cache hit for request {request.request_id}")
                self.cache_hits += 1
                cached_result = self.asset_cache[cache_key]
                await websocket.send(json.dumps({
                    "type": "generation_complete",
                    "request_id": request.request_id,
                    "result": cached_result,
                    "cached": True
                }))
                return
            
            self.cache_misses += 1
            
            # Add to generation queue
            await self.generation_queue.put((websocket, request))
            self.active_generations[request.request_id] = {
                "status": "queued",
                "request": request,
                "websocket": websocket,
                "start_time": time.time()
            }
            
            # Send acknowledgment
            await websocket.send(json.dumps({
                "type": "generation_queued", 
                "request_id": request.request_id,
                "queue_position": self.generation_queue.qsize()
            }))
            
        except KeyError as e:
            logger.error(f"Missing required field in generation request: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Missing required field: {e}"
            }))
        except Exception as e:
            logger.error(f"Error handling generation request: {e}")
            await websocket.send(json.dumps({
                "type": "error", 
                "message": str(e)
            }))

    def build_cache_key(self, request: GenerationRequest) -> str:
        """Build cache key for asset reuse"""
        return f"{request.territory_type}_{request.dominant_faction}_{request.generation_type}_{request.random_seed}"

    async def handle_cache_query(self, websocket, data):
        """Handle cache availability query from UE5"""
        cache_key = data.get("cache_key")
        available = cache_key in self.asset_cache if cache_key else False
        
        await websocket.send(json.dumps({
            "type": "cache_response",
            "cache_key": cache_key,
            "available": available,
            "cache_stats": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "entries": len(self.asset_cache)
            }
        }))

    async def handle_status_request(self, websocket, data):
        """Handle status request from UE5"""
        request_id = data.get("request_id")
        
        if request_id in self.active_generations:
            status = self.active_generations[request_id]["status"]
            elapsed = time.time() - self.active_generations[request_id]["start_time"]
            
            await websocket.send(json.dumps({
                "type": "status_response",
                "request_id": request_id,
                "status": status,
                "elapsed_time": elapsed,
                "queue_size": self.generation_queue.qsize()
            }))
        else:
            await websocket.send(json.dumps({
                "type": "status_response", 
                "request_id": request_id,
                "status": "not_found"
            }))

    async def process_generation_queue(self):
        """Worker process for handling generation requests"""
        logger.info("Generation queue worker started")
        
        while True:
            try:
                # Get next request from queue
                websocket, request = await self.generation_queue.get()
                
                logger.info(f"Processing generation request: {request.request_id}")
                
                # Update status
                if request.request_id in self.active_generations:
                    self.active_generations[request.request_id]["status"] = "generating"
                
                # Generate assets
                result = await self.generate_procedural_assets(request)
                
                # Cache result if successful
                if result.success:
                    cache_key = self.build_cache_key(request)
                    self.asset_cache[cache_key] = result
                    logger.info(f"Cached result for key: {cache_key}")
                
                # Send result to UE5
                try:
                    await websocket.send(json.dumps({
                        "type": "generation_complete",
                        "request_id": request.request_id,
                        "result": {
                            "success": result.success,
                            "asset_paths": result.asset_paths,
                            "metadata": result.metadata,
                            "generation_time": result.generation_time,
                            "error_message": result.error_message
                        },
                        "cached": False
                    }))
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"UE5 connection closed before sending result for {request.request_id}")
                
                # Clean up active generation tracking
                if request.request_id in self.active_generations:
                    del self.active_generations[request.request_id]
                    
            except Exception as e:
                logger.error(f"Error in generation queue worker: {e}")
                
            # Mark task done
            self.generation_queue.task_done()

    async def generate_procedural_assets(self, request: GenerationRequest) -> GenerationResult:
        """Generate procedural assets using ComfyUI"""
        start_time = time.time()
        
        try:
            logger.info(f"Generating assets for territory {request.territory_id}, faction {request.dominant_faction}")
            
            # Get territorial context from database
            territorial_context = await self.get_territorial_context(request.territory_id)
            
            # Generate contextual prompt using procedural prompt engine
            prompt_data = await self.generate_contextual_prompt(request, territorial_context)
            
            # Create ComfyUI workflow
            workflow = await self.create_comfyui_workflow(prompt_data, request)
            
            # Submit to ComfyUI
            asset_paths = await self.submit_to_comfyui(workflow, request)
            
            generation_time = time.time() - start_time
            
            return GenerationResult(
                request_id=request.request_id,
                success=True,
                asset_paths=asset_paths,
                metadata={
                    "territorial_context": territorial_context,
                    "prompt_data": prompt_data,
                    "generation_params": self.proven_params
                },
                generation_time=generation_time
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"Asset generation failed for {request.request_id}: {e}")
            
            return GenerationResult(
                request_id=request.request_id,
                success=False,
                asset_paths=[],
                metadata={},
                generation_time=generation_time,
                error_message=str(e)
            )

    async def get_territorial_context(self, territory_id: int) -> Dict[str, Any]:
        """Get territorial context from database"""
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query territorial data
            cursor.execute("""
                SELECT * FROM territories 
                WHERE territory_id = ?
            """, (territory_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            else:
                logger.warning(f"No territorial data found for territory {territory_id}")
                return {"territory_id": territory_id}
                
        except Exception as e:
            logger.error(f"Error getting territorial context: {e}")
            return {"territory_id": territory_id, "error": str(e)}

    async def generate_contextual_prompt(self, request: GenerationRequest, territorial_context: Dict) -> Dict[str, Any]:
        """Generate contextual prompt using procedural prompt engine"""
        try:
            # Build command for procedural prompt engine
            cmd = [
                "python", "Tools/Comfy/ComfyUI-API/procedural_prompt_engine.py",
                "--faction", request.dominant_faction,
                "--subject", self.get_generation_subject(request.generation_type),
                "--complexity", "4"
            ]
            
            # Add region if available in territorial context
            if "region_id" in territorial_context:
                cmd.extend(["--region", territorial_context["region_id"]])
                
            # Add action based on generation type
            action = self.get_generation_action(request.generation_type)
            if action:
                cmd.extend(["--action", action])
            
            # Execute prompt generation
            logger.info(f"Running prompt generation: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                # Parse output (simplified - would need actual parsing logic)
                return {
                    "prompt": result.stdout.split("PROMPT:")[1].split("CONTEXT:")[0].strip() if "PROMPT:" in result.stdout else "procedural environment",
                    "context": territorial_context,
                    "generation_params": self.proven_params
                }
            else:
                logger.error(f"Prompt generation failed: {result.stderr}")
                return {
                    "prompt": f"procedural {request.generation_type} for {request.dominant_faction}",
                    "context": territorial_context,
                    "generation_params": self.proven_params
                }
                
        except Exception as e:
            logger.error(f"Error generating contextual prompt: {e}")
            return {
                "prompt": f"procedural {request.generation_type} for {request.dominant_faction}",
                "context": territorial_context,
                "generation_params": self.proven_params
            }

    def get_generation_subject(self, generation_type: str) -> str:
        """Map generation type to subject for prompt engine"""
        subjects = {
            "Buildings": "faction building",
            "Landscape": "territorial environment", 
            "Details": "environmental details",
            "Vegetation": "procedural vegetation",
            "All": "complete territorial environment"
        }
        return subjects.get(generation_type, "procedural environment")

    def get_generation_action(self, generation_type: str) -> Optional[str]:
        """Map generation type to action for prompt engine"""
        actions = {
            "Buildings": "constructing structures",
            "Landscape": "terraforming landscape",
            "Details": "placing environmental details",
            "Vegetation": "growing vegetation"
        }
        return actions.get(generation_type)

    async def create_comfyui_workflow(self, prompt_data: Dict, request: GenerationRequest) -> Dict:
        """Create ComfyUI workflow with proven parameters"""
        
        # Base workflow structure using proven parameters
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "FLUX1-dev-fp8.safetensors"
                }
            },
            "2": {
                "class_type": "CLIPTextEncode", 
                "inputs": {
                    "clip": ["1", 1],
                    "text": prompt_data["prompt"]
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["1", 1], 
                    "text": "blurry, low quality, text, watermark"
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": self.proven_params["resolution"][0],
                    "height": self.proven_params["resolution"][1],
                    "batch_size": 1
                }
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0], 
                    "latent_image": ["4", 0],
                    "seed": request.random_seed,
                    "steps": self.proven_params["steps"],
                    "cfg": self.proven_params["cfg"],
                    "sampler_name": self.proven_params["sampler"],
                    "scheduler": self.proven_params["scheduler"],
                    "denoise": 1.0
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
                    "filename_prefix": f"TG_Procedural_{request.territory_id}_{request.generation_type}_{request.request_id}"
                }
            }
        }
        
        return workflow

    async def submit_to_comfyui(self, workflow: Dict, request: GenerationRequest) -> List[str]:
        """Submit workflow to ComfyUI and wait for completion"""
        try:
            # Submit workflow
            response = requests.post(
                f"http://127.0.0.1:{self.comfyui_port}/prompt",
                json={"prompt": workflow},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"ComfyUI submission failed: {response.status_code}")
            
            result_data = response.json()
            prompt_id = result_data["prompt_id"]
            
            logger.info(f"Submitted to ComfyUI with prompt_id: {prompt_id}")
            
            # Wait for completion (simplified polling)
            max_wait = 300  # 5 minutes
            wait_time = 0
            
            while wait_time < max_wait:
                await asyncio.sleep(2)
                wait_time += 2
                
                # Check if generation is complete
                history_response = requests.get(f"http://127.0.0.1:{self.comfyui_port}/history/{prompt_id}")
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    
                    if prompt_id in history_data:
                        # Generation complete, find output files
                        output_files = self.extract_output_files(history_data[prompt_id])
                        logger.info(f"Generation complete: {len(output_files)} files")
                        return output_files
            
            raise Exception("Generation timeout - ComfyUI did not complete in time")
            
        except Exception as e:
            logger.error(f"Error submitting to ComfyUI: {e}")
            raise

    def extract_output_files(self, history_entry: Dict) -> List[str]:
        """Extract output file paths from ComfyUI history"""
        output_files = []
        
        try:
            outputs = history_entry.get("outputs", {})
            for node_id, node_outputs in outputs.items():
                if "images" in node_outputs:
                    for image_data in node_outputs["images"]:
                        filename = image_data.get("filename", "")
                        if filename:
                            # Build full path to output file
                            output_path = Path("Tools/Comfy/ComfyUI-API/output") / filename
                            output_files.append(str(output_path))
            
        except Exception as e:
            logger.error(f"Error extracting output files: {e}")
            
        return output_files

    async def listen_territorial_events(self):
        """Listen to territorial system events and trigger regeneration"""
        logger.info("Starting territorial event listener...")
        
        while True:
            try:
                # Connect to territorial WebSocket server
                uri = f"ws://127.0.0.1:{self.territorial_port}"
                
                async with websockets.connect(uri) as websocket:
                    logger.info("✓ Connected to territorial event system")
                    
                    # Subscribe to territorial change events
                    await websocket.send(json.dumps({
                        "type": "subscribe",
                        "events": ["territorial_influence_changed", "control_point_captured"]
                    }))
                    
                    async for message in websocket:
                        await self.handle_territorial_event(message)
                        
            except websockets.exceptions.ConnectionRefused:
                logger.warning("Territorial WebSocket server not available, retrying in 30s...")
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error in territorial event listener: {e}")
                await asyncio.sleep(10)

    async def handle_territorial_event(self, message: str):
        """Handle territorial change events"""
        try:
            event = json.loads(message)
            event_type = event.get("type")
            
            if event_type == "territorial_influence_changed":
                territory_id = event.get("territory_id")
                new_faction = event.get("dominant_faction")
                
                logger.info(f"Territorial change: Territory {territory_id} now controlled by {new_faction}")
                
                # Invalidate cache for this territory
                self.invalidate_territorial_cache(territory_id)
                
                # Notify connected UE5 clients
                await self.broadcast_territorial_change(event)
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in territorial event: {e}")
        except Exception as e:
            logger.error(f"Error handling territorial event: {e}")

    def invalidate_territorial_cache(self, territory_id: int):
        """Invalidate cached assets for a territory"""
        keys_to_remove = []
        
        for key in self.asset_cache:
            if key.startswith(f"territory_{territory_id}_"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.asset_cache[key]
            
        if keys_to_remove:
            logger.info(f"Invalidated {len(keys_to_remove)} cached assets for territory {territory_id}")

    async def broadcast_territorial_change(self, event: Dict):
        """Broadcast territorial change to connected UE5 clients"""
        message = json.dumps({
            "type": "territorial_change_notification",
            "event": event
        })
        
        disconnected = []
        for websocket in self.connected_clients:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.connected_clients.discard(websocket)

async def main():
    """Main entry point"""
    logger.info("Starting Terminal Grounds Procedural Generation Bridge")
    
    bridge = ProceduralGenerationBridge()
    
    try:
        await bridge.start_services()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())