#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 50 Comprehensive Assets for Terminal Grounds
Using the complete procedural generation pipeline

Asset Distribution:
- 14 Vehicles (2 per faction)
- 14 Weapons (2 per faction) 
- 14 UI Elements (2 per faction)
- 7 Emblems (1 per faction)
- 1 Complete environment set

Author: Terminal Grounds Procedural Pipeline
"""

import asyncio
import subprocess
import time
import json
from pathlib import Path

# Faction list
FACTIONS = [
    "directorate", "free77", "civicwardens", "nomadclans", 
    "ironscavengers", "corporatehegemony", "archivekeepers"
]

# Vehicle types for variety
VEHICLE_TYPES = [
    "transport", "patrol", "heavy", "recon", "support", "command", "assault"
]

# Weapon types for variety  
WEAPON_TYPES = [
    "rifle", "pistol", "smg", "sniper", "shotgun", "mg", "carbine"
]

# UI element types
UI_TYPES = [
    "hud_overlay", "status_display", "radar_interface", "weapon_ui", 
    "health_monitor", "comm_panel", "tactical_display"
]

class ComprehensiveAssetGenerator:
    """Generate 50 diverse assets using all procedural systems"""
    
    def __init__(self):
        self.root_path = Path("C:/Users/Zachg/Terminal-Grounds")
        self.generated_count = 0
        self.successful_count = 0
        self.failed_count = 0
        self.generation_log = []
        
    def log_generation(self, asset_type, faction, details, success=True):
        """Log generation attempt"""
        self.generated_count += 1
        if success:
            self.successful_count += 1
        else:
            self.failed_count += 1
            
        entry = {
            "id": self.generated_count,
            "type": asset_type,
            "faction": faction,
            "details": details,
            "success": success,
            "timestamp": time.time()
        }
        self.generation_log.append(entry)
        
        status = "SUCCESS" if success else "FAILED"
        print(f"[{self.generated_count:2d}/50] {asset_type:12s} | {faction:15s} | {details:20s} | {status}")

    async def generate_vehicles(self):
        """Generate 14 vehicles (2 per faction)"""
        print("\n=== GENERATING VEHICLES (14) ===")
        
        for i, faction in enumerate(FACTIONS):
            for j in range(2):  # 2 vehicles per faction
                vehicle_type = VEHICLE_TYPES[j % len(VEHICLE_TYPES)]
                
                try:
                    # Use FIXED vehicle generation (100% success rate)
                    cmd = [
                        "python", "Tools/ArtGen/FIXED_faction_vehicle_concepts.py",
                        "--faction", faction,
                        "--vehicle-type", vehicle_type,
                        "--count", "1",
                        "--seed", str(1000 + i * 100 + j * 10)
                    ]
                    
                    process = await asyncio.create_subprocess_exec(
                        *cmd, 
                        cwd=self.root_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    success = process.returncode == 0
                    self.log_generation("Vehicle", faction, vehicle_type, success)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.log_generation("Vehicle", faction, f"{vehicle_type} (ERROR)", False)

    async def generate_weapons(self):
        """Generate 14 weapons (2 per faction)"""
        print("\n=== GENERATING WEAPONS (14) ===")
        
        for i, faction in enumerate(FACTIONS):
            for j in range(2):  # 2 weapons per faction
                weapon_type = WEAPON_TYPES[j % len(WEAPON_TYPES)]
                
                try:
                    # Use terminal grounds pipeline for weapons
                    cmd = [
                        "python", "Tools/ArtGen/terminal_grounds_pipeline.py",
                        "generate", "weapon", weapon_type,
                        "--faction", faction
                    ]
                    
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        cwd=self.root_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    success = process.returncode == 0
                    self.log_generation("Weapon", faction, weapon_type, success)
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.log_generation("Weapon", faction, f"{weapon_type} (ERROR)", False)

    async def generate_ui_elements(self):
        """Generate 14 UI elements (2 per faction)"""
        print("\n=== GENERATING UI ELEMENTS (14) ===")
        
        for i, faction in enumerate(FACTIONS):
            for j in range(2):  # 2 UI elements per faction
                ui_type = UI_TYPES[j % len(UI_TYPES)]
                
                try:
                    # Use FIXED UI generation (100% success rate, copyright-safe)
                    cmd = [
                        "python", "Tools/ArtGen/FIXED_faction_ui_hud_concepts.py",
                        "--faction", faction,
                        "--element-type", ui_type,
                        "--count", "1"
                    ]
                    
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        cwd=self.root_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    success = process.returncode == 0
                    self.log_generation("UI Element", faction, ui_type, success)
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.log_generation("UI Element", faction, f"{ui_type} (ERROR)", False)

    async def generate_emblems(self):
        """Generate 7 emblems (1 per faction)"""
        print("\n=== GENERATING EMBLEMS (7) ===")
        
        for faction in FACTIONS:
            try:
                # Use faction emblem generation
                cmd = [
                    "python", "Tools/ArtGen/faction_emblem_fixes.py",
                    "--faction", faction,
                    "--count", "1"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=self.root_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                success = process.returncode == 0
                self.log_generation("Emblem", faction, "faction_logo", success)
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.log_generation("Emblem", faction, "faction_logo (ERROR)", False)

    async def generate_environments(self):
        """Generate 1 environment set"""
        print("\n=== GENERATING ENVIRONMENT SET (1) ===")
        
        try:
            # Use proven environment generation (92% success rate)
            cmd = [
                "python", "Tools/ArtGen/terminal_grounds_generator.py",
                "--count", "1",
                "--location", "comprehensive_showcase"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.root_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            success = process.returncode == 0
            self.log_generation("Environment", "neutral", "showcase_scene", success)
            
        except Exception as e:
            self.log_generation("Environment", "neutral", "showcase_scene (ERROR)", False)

    async def generate_all_assets(self):
        """Generate all 50 assets"""
        print("COMPREHENSIVE ASSET GENERATION: 50 ASSETS")
        print("=" * 60)
        print("Distribution:")
        print("  - 14 Vehicles (2 per faction)")
        print("  - 14 Weapons (2 per faction)")  
        print("  - 14 UI Elements (2 per faction)")
        print("  - 7 Emblems (1 per faction)")
        print("  - 1 Environment set")
        print("=" * 60)
        
        start_time = time.time()
        
        # Generate all asset types
        await self.generate_vehicles()
        await self.generate_weapons() 
        await self.generate_ui_elements()
        await self.generate_emblems()
        await self.generate_environments()
        
        # Calculate statistics
        total_time = time.time() - start_time
        success_rate = (self.successful_count / self.generated_count * 100) if self.generated_count > 0 else 0
        
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE!")
        print("=" * 60)
        print(f"Total Assets: {self.generated_count}")
        print(f"Successful: {self.successful_count}")
        print(f"Failed: {self.failed_count}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.1f} seconds")
        print(f"Average Time: {total_time/self.generated_count:.1f}s per asset")
        
        # Show breakdown by type
        print("\nBreakdown by Asset Type:")
        type_counts = {}
        type_success = {}
        for entry in self.generation_log:
            asset_type = entry['type']
            type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
            if entry['success']:
                type_success[asset_type] = type_success.get(asset_type, 0) + 1
        
        for asset_type in type_counts:
            success = type_success.get(asset_type, 0)
            total = type_counts[asset_type]
            rate = (success / total * 100) if total > 0 else 0
            print(f"  - {asset_type:12s}: {success:2d}/{total:2d} ({rate:4.1f}%)")
        
        print(f"\nOutput Directory: Tools/Comfy/ComfyUI-API/output/")
        print(f"Look for files: TG_FIXED_*, TG_CLEAN_*, TG_PERFECT_*")
        
        # Save generation report
        report = {
            "timestamp": time.time(),
            "total_assets": self.generated_count,
            "successful": self.successful_count,
            "failed": self.failed_count,
            "success_rate": success_rate,
            "total_time": total_time,
            "generation_log": self.generation_log
        }
        
        report_path = self.root_path / "generation_report_50_assets.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved: {report_path}")

async def main():
    """Main execution"""
    generator = ComprehensiveAssetGenerator()
    await generator.generate_all_assets()

if __name__ == "__main__":
    asyncio.run(main())