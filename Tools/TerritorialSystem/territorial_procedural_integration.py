#!/usr/bin/env python3
"""
Territorial Procedural Integration System
Real-time integration between territorial control and procedural map generation

Connects UTGTerritorialProceduralSystem with production asset generation pipeline
Handles WebSocket events and triggers appropriate procedural modifications
Maintains competitive balance while enabling faction-specific environmental storytelling
"""

import asyncio
import websockets
import json
import sqlite3
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerritorialProcedural")

class TerritorialModificationType(Enum):
    NONE = "none"
    COSMETIC = "cosmetic"
    ASSET_PLACEMENT = "asset_placement"
    STRUCTURAL_CHANGE = "structural_change"

class FactionArchitecturalStyle(Enum):
    NEUTRAL = "neutral"
    CORPORATE_HEGEMONY = "corporate_hegemony"
    FREE77 = "free77"
    IRON_SCAVENGERS = "iron_scavengers"
    NOMAD_CLANS = "nomad_clans"
    ARCHIVE_KEEPERS = "archive_keepers"
    CIVIC_WARDENS = "civic_wardens"

@dataclass
class TerritorialProceduralRequest:
    """Request for territorial procedural modification"""
    territory_id: int
    faction_id: int
    modification_type: TerritorialModificationType
    architectural_style: FactionArchitecturalStyle
    strategic_value: int
    contested: bool
    priority: int  # 1=highest, 5=lowest

@dataclass
class AssetGenerationJob:
    """Asset generation job for territorial modification"""
    territory_id: int
    faction_id: int
    asset_type: str
    prompt_data: Dict
    output_path: str
    priority: int

class TerritorialProceduralIntegration:
    """
    Integration system between territorial control and procedural generation
    Connects WebSocket territorial updates with asset generation pipeline
    """
    
    def __init__(self):
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        self.asset_generator_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/ArtGen/production_territorial_pipeline.py")
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
        
        # Faction data
        self.faction_styles = {
            1: {  # Corporate Hegemony
                "name": "Corporate Hegemony",
                "style": FactionArchitecturalStyle.CORPORATE_HEGEMONY,
                "colors": {"primary": "#00C2FF", "secondary": "#0C0F12"},
                "architectural_elements": [
                    "clean geometric lines", "blue corporate lighting", 
                    "polished metal surfaces", "advanced security systems"
                ]
            },
            2: {  # The Seventy-Seven
                "name": "The Seventy-Seven", 
                "style": FactionArchitecturalStyle.FREE77,
                "colors": {"primary": "#BDC3C7", "secondary": "#34495E"},
                "architectural_elements": [
                    "military tactical design", "yellow warning markers",
                    "modular fortifications", "tactical positioning advantages"
                ]
            },
            3: {  # Iron Scavengers
                "name": "Iron Scavengers",
                "style": FactionArchitecturalStyle.IRON_SCAVENGERS,
                "colors": {"primary": "#D35400", "secondary": "#7F8C8D"},
                "architectural_elements": [
                    "improvised salvage construction", "orange industrial markings",
                    "repurposed materials", "environmental adaptation"
                ]
            },
            4: {  # Nomad Clans
                "name": "Nomad Clans",
                "style": FactionArchitecturalStyle.NOMAD_CLANS,
                "colors": {"primary": "#AF601A", "secondary": "#6E2C00"},
                "architectural_elements": [
                    "mobile adaptable structures", "green camouflage integration",
                    "weather-resistant design", "natural material blending"
                ]
            },
            5: {  # Archive Keepers
                "name": "Archive Keepers",
                "style": FactionArchitecturalStyle.ARCHIVE_KEEPERS,
                "colors": {"primary": "#8E44AD", "secondary": "#2C3E50"},
                "architectural_elements": [
                    "information security design", "purple data streams",
                    "secure knowledge storage", "information control points"
                ]
            },
            6: {  # Civic Wardens
                "name": "Civic Wardens",
                "style": FactionArchitecturalStyle.CIVIC_WARDENS,
                "colors": {"primary": "#27AE60", "secondary": "#145A32"},
                "architectural_elements": [
                    "community protection focus", "green safety indicators",
                    "defensive positioning", "civilian safety integration"
                ]
            }
        }
        
        # Asset generation queues
        self.high_priority_queue = []
        self.standard_priority_queue = []
        self.processing_jobs = set()
        
        logger.info("Territorial Procedural Integration initialized")
        
    async def start_integration_server(self, host="127.0.0.1", port=8766):
        """Start integration server to handle UE5 requests"""
        logger.info(f"Starting Territorial Procedural Integration Server on {host}:{port}")
        
        # Start asset generation processing
        asyncio.create_task(self.process_asset_generation_queue())
        
        # Start WebSocket server
        server = await websockets.serve(
            self.handle_ue5_connection,
            host,
            port,
            ping_interval=30,
            ping_timeout=10
        )
        
        logger.info("Integration server started - listening for UE5 territorial requests")
        await server.wait_closed()
        
    async def handle_ue5_connection(self, websocket, path):
        """Handle WebSocket connection from UE5 Territorial Procedural System"""
        logger.info(f"UE5 Territorial System connected from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.process_ue5_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("UE5 connection closed")
        except Exception as e:
            logger.error(f"Error handling UE5 connection: {e}")
            
    async def process_ue5_message(self, websocket, message):
        """Process message from UE5 Territorial Procedural System"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "territorial_change_request":
                await self.handle_territorial_change_request(websocket, data)
            elif message_type == "asset_generation_request":
                await self.handle_asset_generation_request(websocket, data)
            elif message_type == "validation_request":
                await self.handle_validation_request(websocket, data)
            elif message_type == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": time.time()}))
            else:
                logger.warning(f"Unknown message type from UE5: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from UE5: {message}")
        except Exception as e:
            logger.error(f"Error processing UE5 message: {e}")
            
    async def handle_territorial_change_request(self, websocket, data):
        """Handle territorial control change request from UE5"""
        territory_id = data.get("territory_id")
        old_faction_id = data.get("old_faction_id", 0)
        new_faction_id = data.get("new_faction_id", 0)
        
        logger.info(f"Processing territorial change: Territory {territory_id} from Faction {old_faction_id} to {new_faction_id}")
        
        # Get territory data from database
        territory_data = self.get_territory_data(territory_id)
        if not territory_data:
            await self.send_error_response(websocket, f"Territory {territory_id} not found")
            return
            
        # Determine modification type based on strategic value
        mod_type = self.determine_modification_type(territory_data["strategic_value"])
        
        # Create procedural request
        request = TerritorialProceduralRequest(
            territory_id=territory_id,
            faction_id=new_faction_id,
            modification_type=mod_type,
            architectural_style=self.get_faction_style(new_faction_id),
            strategic_value=territory_data["strategic_value"],
            contested=territory_data.get("contested", False),
            priority=self.calculate_priority(territory_data)
        )
        
        # Generate assets for the territorial change
        success = await self.generate_territorial_assets(request)
        
        # Send response back to UE5
        response = {
            "type": "territorial_change_response",
            "territory_id": territory_id,
            "success": success,
            "modification_type": mod_type.value,
            "estimated_completion_time": 300 if success else 0  # 5 minutes estimate
        }
        
        await websocket.send(json.dumps(response))
        
    async def handle_asset_generation_request(self, websocket, data):
        """Handle direct asset generation request from UE5"""
        territory_id = data.get("territory_id")
        faction_id = data.get("faction_id")
        asset_type = data.get("asset_type", "territorial_general")
        
        logger.info(f"Asset generation request: Territory {territory_id}, Faction {faction_id}, Type {asset_type}")
        
        # Create asset generation job
        job = AssetGenerationJob(
            territory_id=territory_id,
            faction_id=faction_id,
            asset_type=asset_type,
            prompt_data=self.create_asset_prompt_data(territory_id, faction_id, asset_type),
            output_path=str(self.output_dir / f"TERRITORIAL_{asset_type}_{territory_id}_{faction_id}"),
            priority=data.get("priority", 3)
        )
        
        # Add to appropriate queue
        if job.priority <= 2:
            self.high_priority_queue.append(job)
        else:
            self.standard_priority_queue.append(job)
            
        response = {
            "type": "asset_generation_queued",
            "territory_id": territory_id,
            "faction_id": faction_id,
            "queue_position": len(self.high_priority_queue) + len(self.standard_priority_queue)
        }
        
        await websocket.send(json.dumps(response))
        
    async def handle_validation_request(self, websocket, data):
        """Handle validation request for territorial modifications"""
        territory_id = data.get("territory_id")
        proposed_locations = data.get("proposed_locations", [])
        modification_type = data.get("modification_type")
        
        # Validate proposed asset locations
        validation_result = self.validate_asset_locations(territory_id, proposed_locations, modification_type)
        
        response = {
            "type": "validation_response",
            "territory_id": territory_id,
            "valid": validation_result["valid"],
            "valid_locations": validation_result["valid_locations"],
            "invalid_reasons": validation_result["invalid_reasons"]
        }
        
        await websocket.send(json.dumps(response))
        
    def get_territory_data(self, territory_id):
        """Get territory data from database"""
        try:
            connection = sqlite3.connect(str(self.db_path))
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM territories WHERE id = ?", (territory_id,))
            territory = cursor.fetchone()
            
            if territory:
                result = dict(territory)
                connection.close()
                return result
            else:
                connection.close()
                return None
                
        except Exception as e:
            logger.error(f"Error getting territory data: {e}")
            return None
            
    def determine_modification_type(self, strategic_value):
        """Determine modification type based on strategic value"""
        if strategic_value >= 8:
            return TerritorialModificationType.STRUCTURAL_CHANGE
        elif strategic_value >= 5:
            return TerritorialModificationType.ASSET_PLACEMENT
        elif strategic_value >= 2:
            return TerritorialModificationType.COSMETIC
        else:
            return TerritorialModificationType.NONE
            
    def get_faction_style(self, faction_id):
        """Get architectural style for faction"""
        if faction_id in self.faction_styles:
            return self.faction_styles[faction_id]["style"]
        return FactionArchitecturalStyle.NEUTRAL
        
    def calculate_priority(self, territory_data):
        """Calculate priority based on territory characteristics"""
        priority = 5  # Default low priority
        
        strategic_value = territory_data.get("strategic_value", 1)
        contested = territory_data.get("contested", False)
        
        if strategic_value >= 8:
            priority = 1  # Highest priority
        elif strategic_value >= 6:
            priority = 2  # High priority
        elif strategic_value >= 4:
            priority = 3  # Medium priority
        else:
            priority = 4  # Low priority
            
        # Contested territories get higher priority
        if contested:
            priority = max(1, priority - 1)
            
        return priority
        
    async def generate_territorial_assets(self, request: TerritorialProceduralRequest):
        """Generate territorial assets for procedural modification"""
        try:
            faction_data = self.faction_styles.get(request.faction_id, {})
            
            # Create asset generation job
            job = AssetGenerationJob(
                territory_id=request.territory_id,
                faction_id=request.faction_id,
                asset_type=request.modification_type.value,
                prompt_data=self.create_faction_prompt_data(request, faction_data),
                output_path=str(self.output_dir / f"TERRITORIAL_{request.modification_type.value}_{request.territory_id}_{request.faction_id}"),
                priority=request.priority
            )
            
            # Add to queue based on priority
            if request.priority <= 2:
                self.high_priority_queue.append(job)
            else:
                self.standard_priority_queue.append(job)
                
            logger.info(f"Queued territorial asset generation: Territory {request.territory_id}, Priority {request.priority}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating territorial assets: {e}")
            return False
            
    def create_faction_prompt_data(self, request: TerritorialProceduralRequest, faction_data: Dict):
        """Create faction-specific prompt data for asset generation"""
        base_prompt = f"masterpiece quality Terminal Grounds territorial {request.modification_type.value}"
        
        faction_name = faction_data.get("name", "Unknown Faction")
        colors = faction_data.get("colors", {"primary": "#FFFFFF", "secondary": "#000000"})
        elements = faction_data.get("architectural_elements", ["generic faction design"])
        
        # Build faction-specific prompt
        faction_prompt = f"{base_prompt}, {faction_name} faction control marker"
        
        # Add architectural elements
        style_elements = ", ".join(elements)
        faction_prompt += f", {style_elements}"
        
        # Add color scheme
        faction_prompt += f", faction colors {colors['primary']} and {colors['secondary']}"
        
        # Add territorial status
        if request.contested:
            faction_prompt += ", battle-worn with recent conflict damage, contested territory markers"
        else:
            faction_prompt += ", well-maintained showing established control, secure territory indicators"
            
        # Add strategic value indicators
        if request.strategic_value >= 8:
            faction_prompt += ", high-value strategic location, reinforced construction"
        elif request.strategic_value >= 5:
            faction_prompt += ", moderate strategic importance"
        else:
            faction_prompt += ", outpost-level territorial marker"
            
        faction_prompt += ", Terminal Grounds aesthetic, photorealistic detail"
        
        return {
            "positive_prompt": faction_prompt,
            "negative_prompt": "blurry, low quality, text, watermark, poor composition, generic design",
            "faction_colors": colors,
            "architectural_style": request.architectural_style.value,
            "modification_type": request.modification_type.value
        }
        
    def create_asset_prompt_data(self, territory_id, faction_id, asset_type):
        """Create prompt data for specific asset generation request"""
        territory_data = self.get_territory_data(territory_id)
        if not territory_data:
            return {}
            
        faction_data = self.faction_styles.get(faction_id, {})
        
        request = TerritorialProceduralRequest(
            territory_id=territory_id,
            faction_id=faction_id,
            modification_type=TerritorialModificationType(asset_type.replace("territorial_", "")),
            architectural_style=self.get_faction_style(faction_id),
            strategic_value=territory_data.get("strategic_value", 1),
            contested=territory_data.get("contested", False),
            priority=self.calculate_priority(territory_data)
        )
        
        return self.create_faction_prompt_data(request, faction_data)
        
    async def process_asset_generation_queue(self):
        """Process queued asset generation jobs"""
        logger.info("Starting asset generation queue processor")
        
        while True:
            try:
                # Process high priority queue first
                if self.high_priority_queue:
                    job = self.high_priority_queue.pop(0)
                    await self.execute_asset_generation_job(job)
                elif self.standard_priority_queue:
                    job = self.standard_priority_queue.pop(0)
                    await self.execute_asset_generation_job(job)
                else:
                    # No jobs in queue, wait
                    await asyncio.sleep(1.0)
                    
            except Exception as e:
                logger.error(f"Error in asset generation queue processor: {e}")
                await asyncio.sleep(5.0)
                
    async def execute_asset_generation_job(self, job: AssetGenerationJob):
        """Execute single asset generation job"""
        logger.info(f"Executing asset generation: Territory {job.territory_id}, Type {job.asset_type}")
        
        # Add to processing set
        job_id = f"{job.territory_id}_{job.faction_id}_{job.asset_type}"
        if job_id in self.processing_jobs:
            logger.warning(f"Job {job_id} already processing, skipping")
            return
            
        self.processing_jobs.add(job_id)
        
        try:
            # Call production territorial pipeline with job parameters
            success = await self.call_asset_generation_pipeline(job)
            
            if success:
                logger.info(f"Asset generation successful: {job_id}")
                # TODO: Notify UE5 of completion
            else:
                logger.error(f"Asset generation failed: {job_id}")
                
        except Exception as e:
            logger.error(f"Error executing asset generation job {job_id}: {e}")
        finally:
            self.processing_jobs.discard(job_id)
            
    async def call_asset_generation_pipeline(self, job: AssetGenerationJob):
        """Call production asset generation pipeline"""
        try:
            # Create temporary prompt file with faction data
            prompt_file = self.output_dir / f"temp_prompt_{job.territory_id}_{job.faction_id}.json"
            with open(prompt_file, 'w') as f:
                json.dump(job.prompt_data, f, indent=2)
                
            # Call production territorial pipeline
            cmd = [
                "python",
                str(self.asset_generator_path),
                "--territory-id", str(job.territory_id),
                "--faction-id", str(job.faction_id),
                "--asset-type", job.asset_type,
                "--prompt-file", str(prompt_file),
                "--output-prefix", job.output_path
            ]
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)  # 10 minute timeout
            
            # Clean up temporary file
            prompt_file.unlink(missing_ok=True)
            
            if process.returncode == 0:
                logger.info(f"Asset generation pipeline completed successfully")
                return True
            else:
                logger.error(f"Asset generation pipeline failed: {stderr.decode()}")
                return False
                
        except asyncio.TimeoutError:
            logger.error(f"Asset generation timed out for job {job.territory_id}")
            return False
        except Exception as e:
            logger.error(f"Error calling asset generation pipeline: {e}")
            return False
            
    def validate_asset_locations(self, territory_id, proposed_locations, modification_type):
        """Validate proposed asset placement locations"""
        valid_locations = []
        invalid_reasons = []
        
        # Get territory boundaries and protected areas
        territory_data = self.get_territory_data(territory_id)
        if not territory_data:
            return {"valid": False, "valid_locations": [], "invalid_reasons": ["Territory not found"]}
            
        # Validate each proposed location
        for i, location in enumerate(proposed_locations):
            x, y, z = location.get("x", 0), location.get("y", 0), location.get("z", 0)
            
            # Check if location is within territory bounds (simplified)
            if self.is_location_in_territory(territory_id, x, y):
                valid_locations.append(location)
            else:
                invalid_reasons.append(f"Location {i} outside territory bounds")
                
        return {
            "valid": len(valid_locations) > 0,
            "valid_locations": valid_locations,
            "invalid_reasons": invalid_reasons
        }
        
    def is_location_in_territory(self, territory_id, x, y):
        """Check if location is within territory bounds (simplified implementation)"""
        # In production, this would use proper spatial queries
        return True
        
    async def send_error_response(self, websocket, error_message):
        """Send error response to UE5"""
        response = {
            "type": "error",
            "message": error_message,
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(response))

async def main():
    """Main entry point"""
    integration = TerritorialProceduralIntegration()
    
    try:
        await integration.start_integration_server()
    except KeyboardInterrupt:
        logger.info("Integration server stopped by user")
    except Exception as e:
        logger.error(f"Integration server error: {e}")

if __name__ == "__main__":
    print("TERRITORIAL PROCEDURAL INTEGRATION SYSTEM")
    print("Real-time integration between territorial control and procedural generation")
    print("Connects UE5 Territorial System with Asset Generation Pipeline")
    print("Press Ctrl+C to stop")
    print()
    
    asyncio.run(main())