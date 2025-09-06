#!/usr/bin/env python3
"""
Procedural-AI Asset Pipeline Bridge
==================================

Bridges the gap between procedural level generation and AI asset creation:
1. Monitors TGProceduralArena for generation events
2. Analyzes generated layouts for asset needs
3. Triggers AI asset generation for specific locations
4. Imports generated assets back into Unreal Engine
5. Integrates with territorial system for faction-specific assets

This creates a feedback loop where procedural generation drives AI asset creation,
which then enhances the procedural content with high-quality AI-generated elements.
"""

import asyncio
import json
import socket
import time
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetType(Enum):
    """Types of assets that can be generated."""
    FACTION_EMBLEM = "faction_emblem"
    ENVIRONMENTAL_PROP = "environmental_prop"
    ARCHITECTURAL_ELEMENT = "architectural_element"
    TERRITORIAL_MARKER = "territorial_marker"
    EXTRACTION_BEACON = "extraction_beacon"
    CAPTURE_NODE_BASE = "capture_node_base"

@dataclass
class AssetRequest:
    """Request for AI-generated asset."""
    asset_type: AssetType
    location: Tuple[float, float, float]  # World coordinates
    faction_id: Optional[str] = None
    style_params: Optional[Dict] = None
    priority: int = 1  # 1=high, 2=medium, 3=low
    context: Optional[str] = None  # Additional context for generation
    
@dataclass
class GeneratedAsset:
    """Information about a generated asset."""
    asset_id: str
    asset_type: AssetType
    file_path: Path
    faction_id: Optional[str]
    world_location: Tuple[float, float, float]
    status: str  # 'generated', 'imported', 'placed'

class ProceduralAIBridge:
    """Main bridge class connecting procedural generation with AI asset creation."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.asset_queue: List[AssetRequest] = []
        self.generated_assets: List[GeneratedAsset] = []
        self.comfyui_url = "http://127.0.0.1:8188"
        self.unreal_tcp_port = 55557
        self.territorial_ws_url = "ws://127.0.0.1:8765"
        
        # Asset generation parameters (proven successful)
        self.generation_params = {
            "seed": 94887,
            "sampler": "heun",
            "scheduler": "normal", 
            "cfg": 3.2,
            "steps": 25,
            "width": 1536,
            "height": 864
        }
        
    async def check_services(self) -> Dict[str, bool]:
        """Check if required services are available."""
        services = {}
        
        # Check ComfyUI
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats", timeout=2)
            services['comfyui'] = response.status_code == 200
        except:
            services['comfyui'] = False
        
        # Check Unreal TCP bridge
        try:
            sock = socket.create_connection(('127.0.0.1', self.unreal_tcp_port), timeout=2)
            sock.close()
            services['unreal'] = True
        except:
            services['unreal'] = False
        
        # Check territorial server
        try:
            # Simple socket check since WebSocket requires more setup
            sock = socket.create_connection(('127.0.0.1', 8765), timeout=2)
            sock.close()
            services['territorial'] = True
        except:
            services['territorial'] = False
        
        return services
    
    def analyze_procedural_layout(self, arena_data: Dict) -> List[AssetRequest]:
        """Analyze a procedural arena layout and determine what assets to generate."""
        asset_requests = []
        
        # Extract key locations from arena data
        capture_nodes = arena_data.get('capture_nodes', [])
        extraction_pads = arena_data.get('extraction_pads', []) 
        faction_territories = arena_data.get('faction_territories', [])
        
        # Generate faction emblems for each territory
        for territory in faction_territories:
            faction_id = territory.get('faction_id')
            location = territory.get('center_location', (0, 0, 0))
            
            if faction_id:
                asset_requests.append(AssetRequest(
                    asset_type=AssetType.FACTION_EMBLEM,
                    location=location,
                    faction_id=faction_id,
                    priority=1,
                    context=f"Territorial control marker for {faction_id}"
                ))
        
        # Generate capture node bases
        for node in capture_nodes:
            location = node.get('location', (0, 0, 0))
            controlling_faction = node.get('controlling_faction')
            
            asset_requests.append(AssetRequest(
                asset_type=AssetType.CAPTURE_NODE_BASE,
                location=location,
                faction_id=controlling_faction,
                priority=2,
                context="Capture node structural base"
            ))
        
        # Generate extraction beacons
        for pad in extraction_pads:
            location = pad.get('location', (0, 0, 0))
            
            asset_requests.append(AssetRequest(
                asset_type=AssetType.EXTRACTION_BEACON,
                location=location,
                priority=1,
                context="High-visibility extraction point marker"
            ))
        
        logger.info(f"Analyzed layout: {len(asset_requests)} assets identified")
        return asset_requests
    
    async def generate_asset(self, request: AssetRequest) -> Optional[GeneratedAsset]:
        """Generate a single asset using ComfyUI."""
        if not await self.check_services().get('comfyui', False):
            logger.error("ComfyUI not available for asset generation")
            return None
        
        # Build generation prompt based on asset type and faction
        prompt = self.build_generation_prompt(request)
        
        # Prepare ComfyUI workflow
        workflow = self.build_comfyui_workflow(prompt, request)
        
        try:
            # Submit to ComfyUI
            response = requests.post(f"{self.comfyui_url}/prompt", json={
                "prompt": workflow,
                "client_id": str(uuid.uuid4())
            })
            
            if response.status_code == 200:
                prompt_id = response.json().get('prompt_id')
                
                # Wait for generation to complete
                asset_path = await self.wait_for_generation(prompt_id)
                
                if asset_path:
                    asset = GeneratedAsset(
                        asset_id=str(uuid.uuid4()),
                        asset_type=request.asset_type,
                        file_path=asset_path,
                        faction_id=request.faction_id,
                        world_location=request.location,
                        status='generated'
                    )
                    
                    self.generated_assets.append(asset)
                    logger.info(f"Generated asset: {asset.asset_type.value} at {asset_path}")
                    return asset
            
        except Exception as e:
            logger.error(f"Asset generation failed: {e}")
        
        return None
    
    def build_generation_prompt(self, request: AssetRequest) -> str:
        """Build a generation prompt based on asset type and context."""
        base_style = "Terminal Grounds aesthetic, industrial sci-fi, weathered metal"
        
        if request.asset_type == AssetType.FACTION_EMBLEM:
            faction_styles = {
                'directorate': 'clean corporate blue, geometric patterns, authority symbols',
                'free77': 'military yellow warnings, tactical markings, resistance symbols',
                'iron_scavengers': 'orange rust, improvised metal, salvage aesthetic',
                'nomad_clans': 'green natural, adaptive camouflage, survival gear'
            }
            
            faction_style = faction_styles.get(request.faction_id, 'neutral gray, generic industrial')
            
            return f"faction emblem, {faction_style}, {base_style}, logo design, clean readable text, professional signage"
        
        elif request.asset_type == AssetType.CAPTURE_NODE_BASE:
            return f"capture control terminal, tactical computer interface, {base_style}, glowing holographic display, tactical readouts"
        
        elif request.asset_type == AssetType.EXTRACTION_BEACON:
            return f"extraction beacon, bright emergency lighting, {base_style}, landing pad markers, high-visibility safety stripes"
        
        elif request.asset_type == AssetType.TERRITORIAL_MARKER:
            return f"territorial boundary marker, faction control beacon, {base_style}, warning lights, defensive positioning"
        
        else:
            return f"industrial prop, {base_style}, functional design, environmental storytelling"
    
    def build_comfyui_workflow(self, prompt: str, request: AssetRequest) -> Dict:
        """Build a ComfyUI workflow for the asset generation."""
        # This is a simplified workflow structure
        # In practice, you'd load from your proven workflow templates
        
        workflow = {
            "1": {
                "inputs": {
                    "text": prompt,
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "text": "blurry, low quality, distorted text, gibberish, watermark",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "seed": self.generation_params["seed"],
                    "steps": self.generation_params["steps"],
                    "cfg": self.generation_params["cfg"],
                    "sampler_name": self.generation_params["sampler"],
                    "scheduler": self.generation_params["scheduler"],
                    "denoise": 1.0,
                    "model": ["11", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["4", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "width": self.generation_params["width"],
                    "height": self.generation_params["height"],
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "5": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["11", 2]
                },
                "class_type": "VAEDecode"
            },
            "6": {
                "inputs": {
                    "filename_prefix": f"TG_{request.asset_type.value}_{int(time.time())}",
                    "images": ["5", 0]
                },
                "class_type": "SaveImage"
            },
            "11": {
                "inputs": {
                    "ckpt_name": "flux1-dev-fp8.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            }
        }
        
        return workflow
    
    async def wait_for_generation(self, prompt_id: str, timeout: int = 300) -> Optional[Path]:
        """Wait for ComfyUI generation to complete and return the output path."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check generation status
                response = requests.get(f"{self.comfyui_url}/history/{prompt_id}")
                
                if response.status_code == 200:
                    history = response.json()
                    
                    if prompt_id in history:
                        outputs = history[prompt_id].get('outputs', {})
                        
                        # Look for saved images
                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                for image_info in node_output['images']:
                                    filename = image_info.get('filename')
                                    if filename:
                                        # ComfyUI saves to output directory
                                        output_path = Path(self.project_root / "Tools" / "Comfy" / "ComfyUI-API" / "output" / filename)
                                        if output_path.exists():
                                            return output_path
                
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error checking generation status: {e}")
                await asyncio.sleep(5)
        
        logger.error(f"Generation timeout for prompt {prompt_id}")
        return None
    
    async def import_to_unreal(self, asset: GeneratedAsset) -> bool:
        """Import generated asset into Unreal Engine."""
        if not await self.check_services().get('unreal', False):
            logger.error("Unreal Engine not available for asset import")
            return False
        
        try:
            # Prepare import command
            import_command = {
                "type": "import_asset",
                "params": {
                    "source_path": str(asset.file_path),
                    "destination_path": f"/Game/Generated/{asset.asset_type.value}s/",
                    "asset_name": f"{asset.asset_type.value}_{asset.asset_id[:8]}",
                    "reimport": True
                }
            }
            
            # Send to Unreal via TCP
            with socket.create_connection(('127.0.0.1', self.unreal_tcp_port), timeout=10) as sock:
                sock.sendall(json.dumps(import_command).encode('utf-8'))
                response = sock.recv(4096).decode('utf-8')
                
                response_data = json.loads(response)
                if response_data.get('success'):
                    asset.status = 'imported'
                    logger.info(f"Imported asset to Unreal: {asset.asset_id}")
                    return True
                else:
                    logger.error(f"Import failed: {response_data.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Unreal import error: {e}")
        
        return False
    
    async def process_asset_queue(self):
        """Process the asset generation queue."""
        logger.info(f"Processing {len(self.asset_queue)} queued assets...")
        
        # Sort by priority
        self.asset_queue.sort(key=lambda x: x.priority)
        
        for request in self.asset_queue:
            logger.info(f"Generating {request.asset_type.value} for faction {request.faction_id}")
            
            asset = await self.generate_asset(request)
            if asset:
                # Attempt to import to Unreal
                if await self.import_to_unreal(asset):
                    logger.info(f"Successfully processed asset: {asset.asset_id}")
                else:
                    logger.warning(f"Generated but failed to import: {asset.asset_id}")
            
            # Brief delay between generations to avoid overwhelming ComfyUI
            await asyncio.sleep(2)
        
        # Clear processed queue
        self.asset_queue.clear()
    
    async def monitor_procedural_events(self):
        """Monitor for procedural generation events that trigger asset creation."""
        logger.info("Monitoring for procedural generation events...")
        
        # This would connect to Unreal Engine to listen for arena generation events
        # For now, we'll simulate with a periodic check
        
        while True:
            try:
                # Check if new procedural content has been generated
                # In a real implementation, this would listen for UE5 events
                
                # Simulate finding new procedural layout
                if len(self.asset_queue) == 0:  # Only add if queue is empty
                    # Example procedural layout data
                    mock_arena_data = {
                        "capture_nodes": [
                            {"location": (1000, 500, 0), "controlling_faction": "directorate"},
                            {"location": (-800, -200, 0), "controlling_faction": "free77"},
                            {"location": (200, -1000, 0), "controlling_faction": None}
                        ],
                        "extraction_pads": [
                            {"location": (0, 0, 200)}
                        ],
                        "faction_territories": [
                            {"faction_id": "directorate", "center_location": (800, 400, 0)},
                            {"faction_id": "free77", "center_location": (-600, -400, 0)}
                        ]
                    }
                    
                    # Analyze and queue assets
                    new_requests = self.analyze_procedural_layout(mock_arena_data)
                    self.asset_queue.extend(new_requests)
                    
                    if new_requests:
                        logger.info(f"Queued {len(new_requests)} assets from procedural analysis")
                        await self.process_asset_queue()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in procedural monitoring: {e}")
                await asyncio.sleep(10)

async def main():
    """Main entry point for the bridge."""
    bridge = ProceduralAIBridge()
    
    # Check service availability
    services = await bridge.check_services()
    logger.info("Service Status:")
    for service, available in services.items():
        status = "✅ ONLINE" if available else "❌ OFFLINE"
        logger.info(f"  {service}: {status}")
    
    if not any(services.values()):
        logger.error("No services available. Start automation with: python start_tg_automation.py")
        return
    
    try:
        # Start monitoring for procedural events
        await bridge.monitor_procedural_events()
    except KeyboardInterrupt:
        logger.info("Bridge shutdown by user")

if __name__ == "__main__":
    asyncio.run(main())