#!/usr/bin/env python3
"""
Terminal Grounds UE5 Integration for Procedural Pipeline
Connects UE5 procedural subsystem with automated generation pipeline

Author: DevOps Engineer
Version: 1.0.0
"""

import asyncio
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import subprocess
import shutil

from procedural_generation_orchestrator import (
    GenerationRequest, 
    GenerationType, 
    PipelineOrchestrator,
    Config
)

logger = logging.getLogger("UE5Integration")

@dataclass
class UE5AssetRequest:
    """Request from UE5 subsystem"""
    territory_id: int
    territory_type: str  # Region, District, ControlPoint
    faction_id: str
    generation_type: str  # Landscape, Buildings, Details, Vegetation, All
    center_location: Dict[str, float]  # X, Y, Z
    generation_radius: float
    random_seed: int
    metadata: Dict[str, Any]

class UE5ProceduralBridge:
    """Bridge between UE5 subsystem and generation pipeline"""
    
    def __init__(self, orchestrator: PipelineOrchestrator):
        self.orchestrator = orchestrator
        self.ue5_requests_db = Path("C:/Users/Zachg/Terminal-Grounds/Database/ue5_requests.db")
        self.asset_output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Content/Generated")
        self.ue5_import_dir = Path("C:/Users/Zachg/Terminal-Grounds/Content/Generated/Import")
        
        self._init_database()
        self._ensure_directories()
    
    def _init_database(self):
        """Initialize UE5 requests database"""
        conn = sqlite3.connect(str(self.ue5_requests_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ue5_requests (
                request_id TEXT PRIMARY KEY,
                territory_id INTEGER,
                territory_type TEXT,
                faction_id TEXT,
                generation_type TEXT,
                center_location TEXT,
                generation_radius REAL,
                random_seed INTEGER,
                metadata TEXT,
                status TEXT,
                pipeline_requests TEXT,
                created_at TEXT,
                completed_at TEXT,
                asset_paths TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _ensure_directories(self):
        """Ensure output directories exist"""
        self.asset_output_dir.mkdir(parents=True, exist_ok=True)
        self.ue5_import_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories by type
        for gen_type in GenerationType:
            type_dir = self.asset_output_dir / gen_type.value
            type_dir.mkdir(exist_ok=True)
    
    async def handle_ue5_request(self, ue5_request: UE5AssetRequest) -> str:
        """Handle request from UE5 subsystem"""
        request_id = f"ue5_{ue5_request.territory_id}_{int(time.time())}"
        
        logger.info(f"Processing UE5 request: {request_id}")
        
        # Store request in database
        self._store_ue5_request(request_id, ue5_request)
        
        # Convert to pipeline requests
        pipeline_requests = await self._convert_to_pipeline_requests(
            request_id, ue5_request
        )
        
        # Submit to pipeline
        pipeline_request_ids = []
        for req in pipeline_requests:
            await self.orchestrator.submit_request(req)
            pipeline_request_ids.append(req.request_id)
        
        # Update database with pipeline request IDs
        self._update_pipeline_requests(request_id, pipeline_request_ids)
        
        logger.info(f"Submitted {len(pipeline_requests)} pipeline requests for {request_id}")
        
        return request_id
    
    def _store_ue5_request(self, request_id: str, ue5_request: UE5AssetRequest):
        """Store UE5 request in database"""
        conn = sqlite3.connect(str(self.ue5_requests_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ue5_requests (
                request_id, territory_id, territory_type, faction_id,
                generation_type, center_location, generation_radius,
                random_seed, metadata, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id,
            ue5_request.territory_id,
            ue5_request.territory_type,
            ue5_request.faction_id,
            ue5_request.generation_type,
            json.dumps(ue5_request.center_location),
            ue5_request.generation_radius,
            ue5_request.random_seed,
            json.dumps(ue5_request.metadata),
            "processing",
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _convert_to_pipeline_requests(
        self, 
        ue5_request_id: str, 
        ue5_request: UE5AssetRequest
    ) -> List[GenerationRequest]:
        """Convert UE5 request to pipeline generation requests"""
        
        requests = []
        
        # Map UE5 generation types to pipeline types
        generation_mapping = {
            "Landscape": [GenerationType.ENVIRONMENT],
            "Buildings": [GenerationType.BUILDING, GenerationType.TERRITORIAL_MARKER],
            "Details": [GenerationType.WEAPON, GenerationType.UI_ELEMENT],
            "Vegetation": [GenerationType.ENVIRONMENT],
            "All": [
                GenerationType.ENVIRONMENT,
                GenerationType.BUILDING,
                GenerationType.VEHICLE,
                GenerationType.WEAPON,
                GenerationType.EMBLEM,
                GenerationType.TERRITORIAL_MARKER
            ]
        }
        
        generation_types = generation_mapping.get(
            ue5_request.generation_type, 
            [GenerationType.ENVIRONMENT]
        )
        
        # Create requests for each type
        for gen_type in generation_types:
            # Determine priority based on type and territory
            priority = self._calculate_priority(gen_type, ue5_request)
            
            # Build prompt data from UE5 context
            prompt_data = self._build_prompt_data(gen_type, ue5_request)
            
            # Create metadata
            metadata = {
                "ue5_request_id": ue5_request_id,
                "territory_id": ue5_request.territory_id,
                "territory_type": ue5_request.territory_type,
                "center_location": ue5_request.center_location,
                "generation_radius": ue5_request.generation_radius,
                "seed": ue5_request.random_seed,
                "source": "ue5_subsystem"
            }
            metadata.update(ue5_request.metadata)
            
            request = GenerationRequest(
                request_id=f"{ue5_request_id}_{gen_type.value}_{uuid.uuid4().hex[:8]}",
                generation_type=gen_type,
                faction_id=ue5_request.faction_id,
                territory_id=ue5_request.territory_id,
                prompt_data=prompt_data,
                metadata=metadata,
                priority=priority
            )
            
            requests.append(request)
        
        return requests
    
    def _calculate_priority(self, gen_type: GenerationType, ue5_request: UE5AssetRequest) -> int:
        """Calculate request priority based on context"""
        base_priority = 5
        
        # Higher priority for smaller territories (more immediate)
        if ue5_request.territory_type == "ControlPoint":
            base_priority += 3
        elif ue5_request.territory_type == "District":
            base_priority += 1
        
        # Higher priority for buildings and markers (gameplay critical)
        if gen_type in [GenerationType.BUILDING, GenerationType.TERRITORIAL_MARKER]:
            base_priority += 2
        
        # Immediate priority for real-time generation
        if ue5_request.metadata.get("immediate", False):
            base_priority = 10
        
        return min(base_priority, 10)
    
    def _build_prompt_data(self, gen_type: GenerationType, ue5_request: UE5AssetRequest) -> Dict[str, Any]:
        """Build prompt data from UE5 context"""
        prompt_data = {}
        
        # Territory-specific prompts
        territory_descriptions = {
            "Region": "large scale regional environment",
            "District": "urban district facility",
            "ControlPoint": "strategic control point structure"
        }
        
        prompt_data["territory_context"] = territory_descriptions.get(
            ue5_request.territory_type, 
            "territorial location"
        )
        
        # Generation type specific prompts
        type_contexts = {
            GenerationType.ENVIRONMENT: f"{prompt_data['territory_context']}, environmental storytelling",
            GenerationType.BUILDING: f"faction {ue5_request.faction_id} {prompt_data['territory_context']}",
            GenerationType.VEHICLE: f"{ue5_request.faction_id} territorial patrol vehicle",
            GenerationType.WEAPON: f"{ue5_request.faction_id} faction weapon cache",
            GenerationType.EMBLEM: f"{ue5_request.faction_id} territorial control marker",
            GenerationType.TERRITORIAL_MARKER: f"{ue5_request.faction_id} zone boundary marker"
        }
        
        prompt_data["additional_prompt"] = type_contexts.get(gen_type, "")
        
        # Add radius-based scale context
        if ue5_request.generation_radius > 50000:  # Large area
            prompt_data["scale_context"] = "wide area view, strategic overview"
        elif ue5_request.generation_radius > 20000:  # Medium area  
            prompt_data["scale_context"] = "tactical zone, operational area"
        else:  # Small area
            prompt_data["scale_context"] = "close quarters, detailed structures"
        
        return prompt_data
    
    def _update_pipeline_requests(self, ue5_request_id: str, pipeline_request_ids: List[str]):
        """Update UE5 request with pipeline request IDs"""
        conn = sqlite3.connect(str(self.ue5_requests_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ue5_requests 
            SET pipeline_requests = ? 
            WHERE request_id = ?
        """, (json.dumps(pipeline_request_ids), ue5_request_id))
        
        conn.commit()
        conn.close()
    
    async def check_completion(self, ue5_request_id: str) -> Dict[str, Any]:
        """Check completion status of UE5 request"""
        conn = sqlite3.connect(str(self.ue5_requests_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ue5_requests WHERE request_id = ?
        """, (ue5_request_id,))
        
        ue5_request = cursor.fetchone()
        conn.close()
        
        if not ue5_request:
            return {"status": "not_found"}
        
        # Get pipeline request statuses
        pipeline_request_ids = json.loads(ue5_request["pipeline_requests"] or "[]")
        
        if not pipeline_request_ids:
            return {"status": "no_pipeline_requests"}
        
        pipeline_statuses = self._get_pipeline_statuses(pipeline_request_ids)
        
        # Determine overall status
        completed_count = sum(1 for s in pipeline_statuses if s["status"] == "completed")
        failed_count = sum(1 for s in pipeline_statuses if s["status"] == "failed")
        total_count = len(pipeline_statuses)
        
        if completed_count == total_count:
            status = "completed"
            # Collect asset paths
            asset_paths = [s["output_path"] for s in pipeline_statuses if s["output_path"]]
            await self._process_completed_assets(ue5_request_id, asset_paths)
        elif failed_count > 0:
            status = "partial_failure"
        else:
            status = "processing"
        
        return {
            "status": status,
            "completed": completed_count,
            "failed": failed_count,
            "total": total_count,
            "pipeline_requests": pipeline_statuses
        }
    
    def _get_pipeline_statuses(self, pipeline_request_ids: List[str]) -> List[Dict[str, Any]]:
        """Get statuses of pipeline requests"""
        if not Config.PIPELINE_DB.exists():
            return []
        
        conn = sqlite3.connect(str(Config.PIPELINE_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        statuses = []
        for request_id in pipeline_request_ids:
            cursor.execute("""
                SELECT request_id, status, output_path, error_message
                FROM generation_requests 
                WHERE request_id = ?
            """, (request_id,))
            
            result = cursor.fetchone()
            if result:
                statuses.append(dict(result))
            else:
                statuses.append({
                    "request_id": request_id,
                    "status": "unknown",
                    "output_path": None,
                    "error_message": "Request not found"
                })
        
        conn.close()
        return statuses
    
    async def _process_completed_assets(self, ue5_request_id: str, asset_paths: List[str]):
        """Process completed assets for UE5 import"""
        # Copy assets to UE5 import directory
        ue5_assets = []
        
        for asset_path in asset_paths:
            if not asset_path:
                continue
            
            source_path = Path(asset_path)
            if not source_path.exists():
                logger.warning(f"Asset not found: {asset_path}")
                continue
            
            # Determine asset type from generation request
            asset_type = self._determine_asset_type(source_path.name)
            
            # Create target directory
            target_dir = self.ue5_import_dir / asset_type
            target_dir.mkdir(exist_ok=True)
            
            # Generate UE5-friendly filename
            target_filename = f"{ue5_request_id}_{asset_type}_{source_path.stem}.png"
            target_path = target_dir / target_filename
            
            # Copy asset
            try:
                shutil.copy2(source_path, target_path)
                ue5_assets.append(str(target_path))
                logger.info(f"Copied asset to UE5 import: {target_path}")
            except Exception as e:
                logger.error(f"Failed to copy asset {source_path}: {e}")
        
        # Update database with asset paths
        self._update_ue5_assets(ue5_request_id, ue5_assets)
        
        # Generate UE5 import manifest
        await self._generate_import_manifest(ue5_request_id, ue5_assets)
    
    def _determine_asset_type(self, filename: str) -> str:
        """Determine asset type from filename"""
        if "environment" in filename.lower():
            return "Environments"
        elif "building" in filename.lower():
            return "Buildings"
        elif "vehicle" in filename.lower():
            return "Vehicles"
        elif "weapon" in filename.lower():
            return "Weapons"
        elif "emblem" in filename.lower():
            return "Emblems"
        elif "territorial" in filename.lower():
            return "TerritorialMarkers"
        else:
            return "Miscellaneous"
    
    def _update_ue5_assets(self, ue5_request_id: str, asset_paths: List[str]):
        """Update UE5 request with final asset paths"""
        conn = sqlite3.connect(str(self.ue5_requests_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ue5_requests 
            SET status = 'completed', 
                completed_at = ?,
                asset_paths = ?
            WHERE request_id = ?
        """, (
            datetime.now().isoformat(),
            json.dumps(asset_paths),
            ue5_request_id
        ))
        
        conn.commit()
        conn.close()
    
    async def _generate_import_manifest(self, ue5_request_id: str, asset_paths: List[str]):
        """Generate UE5 import manifest"""
        manifest = {
            "request_id": ue5_request_id,
            "generated_at": datetime.now().isoformat(),
            "assets": []
        }
        
        for asset_path in asset_paths:
            asset_info = {
                "path": asset_path,
                "type": self._determine_asset_type(Path(asset_path).name),
                "import_settings": self._get_import_settings(asset_path)
            }
            manifest["assets"].append(asset_info)
        
        # Save manifest
        manifest_path = self.ue5_import_dir / f"{ue5_request_id}_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Generated import manifest: {manifest_path}")
    
    def _get_import_settings(self, asset_path: str) -> Dict[str, Any]:
        """Get UE5 import settings based on asset type"""
        asset_type = self._determine_asset_type(Path(asset_path).name)
        
        settings = {
            "Environments": {
                "texture_group": "World",
                "compression": "BC7",
                "mip_gen": True,
                "sRGB": True
            },
            "Buildings": {
                "texture_group": "WorldNormalMap", 
                "compression": "BC7",
                "mip_gen": True,
                "sRGB": True
            },
            "Vehicles": {
                "texture_group": "Vehicle",
                "compression": "BC7", 
                "mip_gen": True,
                "sRGB": True
            },
            "Weapons": {
                "texture_group": "Weapon",
                "compression": "BC7",
                "mip_gen": True,
                "sRGB": True
            },
            "Emblems": {
                "texture_group": "UI",
                "compression": "BC7",
                "mip_gen": False,
                "sRGB": True,
                "alpha": True
            },
            "TerritorialMarkers": {
                "texture_group": "Effects",
                "compression": "BC7",
                "mip_gen": True,
                "sRGB": True,
                "alpha": True
            }
        }
        
        return settings.get(asset_type, settings["Environments"])

class UE5RequestProcessor:
    """Process incoming requests from UE5"""
    
    def __init__(self, bridge: UE5ProceduralBridge):
        self.bridge = bridge
        self.request_file = Path("C:/Users/Zachg/Terminal-Grounds/Temp/ue5_requests.json")
        self.response_file = Path("C:/Users/Zachg/Terminal-Grounds/Temp/ue5_responses.json")
        
        # Ensure temp directory exists
        self.request_file.parent.mkdir(parents=True, exist_ok=True)
    
    async def process_file_based_requests(self):
        """Process requests from file (for UE5 integration)"""
        while True:
            try:
                if self.request_file.exists():
                    with open(self.request_file, 'r') as f:
                        data = json.load(f)
                    
                    if data.get("requests"):
                        responses = []
                        
                        for req_data in data["requests"]:
                            ue5_request = UE5AssetRequest(**req_data)
                            request_id = await self.bridge.handle_ue5_request(ue5_request)
                            
                            responses.append({
                                "original_request": req_data,
                                "request_id": request_id,
                                "status": "processing"
                            })
                        
                        # Write responses
                        response_data = {
                            "timestamp": datetime.now().isoformat(),
                            "responses": responses
                        }
                        
                        with open(self.response_file, 'w') as f:
                            json.dump(response_data, f, indent=2)
                        
                        # Remove processed request file
                        self.request_file.unlink()
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing file requests: {e}")
                await asyncio.sleep(5)

async def main():
    """Test the UE5 integration"""
    from procedural_generation_orchestrator import PipelineOrchestrator
    
    # Create orchestrator
    orchestrator = PipelineOrchestrator()
    await orchestrator.initialize()
    
    # Create bridge
    bridge = UE5ProceduralBridge(orchestrator)
    
    # Create processor
    processor = UE5RequestProcessor(bridge)
    
    # Test request
    test_request = UE5AssetRequest(
        territory_id=1,
        territory_type="ControlPoint",
        faction_id="Directorate",
        generation_type="Buildings",
        center_location={"X": 1000.0, "Y": 2000.0, "Z": 100.0},
        generation_radius=5000.0,
        random_seed=12345,
        metadata={"test": True}
    )
    
    request_id = await bridge.handle_ue5_request(test_request)
    print(f"Created test request: {request_id}")
    
    # Monitor completion
    while True:
        status = await bridge.check_completion(request_id)
        print(f"Status: {status}")
        
        if status["status"] in ["completed", "partial_failure"]:
            break
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())