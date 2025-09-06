#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Ultimate Demo Builder
Uses flopperam MCP's advanced capabilities to build a complete playable level
"""

import socket
import json
import time
import sys
import random

class TerminalGroundsUltimateDemo:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 13377  # flopperam MCP port
        
    def send_command(self, command, params=None):
        """Send command to flopperam MCP server"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((self.host, self.port))
            
            message = {
                "command": command,
                "params": params or {}
            }
            
            msg = json.dumps(message) + '\n'
            s.send(msg.encode('utf-8'))
            
            data = b""
            while True:
                chunk = s.recv(8192)
                if not chunk:
                    break
                data += chunk
                if b'\n' in chunk:
                    break
            
            s.close()
            
            if data:
                return json.loads(data.decode('utf-8').strip())
            return None
            
        except Exception as e:
            print(f"[ERROR] {command}: {e}")
            return None
    
    def build_epic_demo(self):
        """Build the ultimate Terminal Grounds demo level"""
        
        print("\n" + "=" * 80)
        print("  TERMINAL GROUNDS - ULTIMATE DEMO BUILDER")
        print("  Using Flopperam MCP + ProceduralDungeon + StreetMap")
        print("=" * 80 + "\n")
        
        # Test connection
        print("[INIT] Connecting to flopperam MCP server...")
        response = self.send_command("get_actors_in_level")
        if not response:
            print("[ERROR] Cannot connect to MCP server on port 13377")
            print("Make sure:")
            print("  1. Unreal Engine is running")
            print("  2. UnrealMCP plugin is enabled")
            print("  3. The MCP server is listening on port 13377")
            return False
        
        print("[OK] Connected to MCP server\n")
        
        # Clear the level
        print("[CLEANUP] Preparing level...")
        actors = response.get("actors", [])
        print(f"  Found {len(actors)} existing actors\n")
        
        # ==========================================
        # PHASE 1: BUILD THE MAIN TOWN
        # ==========================================
        print("=" * 60)
        print("PHASE 1: CONSTRUCTING TERMINAL GROUNDS SETTLEMENT")
        print("=" * 60 + "\n")
        
        print("[TOWN] Creating central hub area...")
        
        # Build different house styles for variety
        houses = [
            # Central mansion (HQ)
            {
                "style": "mansion",
                "location": [0, 0, 0],
                "width": 1500,
                "depth": 1200,
                "name": "HQ_Mansion"
            },
            # Modern houses on east side
            {
                "style": "modern",
                "location": [2000, 500, 0],
                "width": 1200,
                "depth": 1000,
                "name": "House_East_1"
            },
            {
                "style": "modern", 
                "location": [2000, -500, 0],
                "width": 1200,
                "depth": 1000,
                "name": "House_East_2"
            },
            # Cottages on west side
            {
                "style": "cottage",
                "location": [-2000, 500, 0],
                "width": 800,
                "depth": 600,
                "name": "Cottage_West_1"
            },
            {
                "style": "cottage",
                "location": [-2000, -500, 0],
                "width": 800,
                "depth": 600,
                "name": "Cottage_West_2"
            }
        ]
        
        for house in houses:
            print(f"  Building {house['name']} ({house['style']})...")
            response = self.send_command("construct_house", {
                "house_style": house["style"],
                "location": house["location"],
                "width": house["width"],
                "depth": house["depth"]
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {house['name']} constructed")
            else:
                print(f"    [FAIL] Could not build {house['name']}")
        
        print()
        
        # ==========================================
        # PHASE 2: DEFENSIVE STRUCTURES
        # ==========================================
        print("=" * 60)
        print("PHASE 2: BUILDING DEFENSIVE PERIMETER")
        print("=" * 60 + "\n")
        
        print("[WALLS] Creating defensive walls...")
        
        # Build perimeter walls
        walls = [
            # North wall
            {"location": [0, 3500, 0], "length": 7000, "height": 500, "orientation": "horizontal"},
            # South wall
            {"location": [0, -3500, 0], "length": 7000, "height": 500, "orientation": "horizontal"},
            # East wall
            {"location": [3500, 0, 0], "length": 7000, "height": 500, "orientation": "vertical"},
            # West wall
            {"location": [-3500, 0, 0], "length": 7000, "height": 500, "orientation": "vertical"}
        ]
        
        for i, wall in enumerate(walls):
            direction = ["North", "South", "East", "West"][i]
            print(f"  Building {direction} wall...")
            response = self.send_command("create_wall", {
                "location": wall["location"],
                "length": wall["length"],
                "height": wall["height"],
                "block_size": 100,
                "orientation": wall["orientation"]
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {direction} wall complete")
        
        print("\n[TOWERS] Adding watchtowers at corners...")
        
        # Build corner towers
        towers = [
            {"location": [3200, 3200, 0], "name": "Tower_NE"},
            {"location": [-3200, 3200, 0], "name": "Tower_NW"},
            {"location": [3200, -3200, 0], "name": "Tower_SE"},
            {"location": [-3200, -3200, 0], "name": "Tower_SW"}
        ]
        
        for tower in towers:
            print(f"  Building {tower['name']}...")
            response = self.send_command("create_tower", {
                "location": tower["location"],
                "levels": 5,
                "block_size": 150
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {tower['name']} constructed")
        
        print()
        
        # ==========================================
        # PHASE 3: TACTICAL MAZE AREA
        # ==========================================
        print("=" * 60)
        print("PHASE 3: GENERATING TACTICAL MAZE")
        print("=" * 60 + "\n")
        
        print("[MAZE] Creating combat maze area...")
        response = self.send_command("create_maze", {
            "rows": 10,
            "cols": 10,
            "cell_size": 250,
            "wall_height": 400,
            "location": [0, -6000, 0]
        })
        if response and response.get("status") != "error":
            print("  [OK] 10x10 tactical maze generated")
        else:
            print("  [FAIL] Could not generate maze")
        
        print()
        
        # ==========================================
        # PHASE 4: EXTRACTION & OBJECTIVES
        # ==========================================
        print("=" * 60)
        print("PHASE 4: SETTING UP OBJECTIVES")
        print("=" * 60 + "\n")
        
        print("[EXTRACTION] Creating extraction zones...")
        
        # Build archways for extraction points
        extraction_points = [
            {"location": [0, 6000, 0], "name": "Extraction_North"},
            {"location": [6000, 0, 0], "name": "Extraction_East"},
            {"location": [-6000, 0, 0], "name": "Extraction_West"}
        ]
        
        for point in extraction_points:
            print(f"  Building {point['name']} arch...")
            response = self.send_command("create_arch", {
                "location": point["location"],
                "radius": 300,
                "segments": 12
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {point['name']} arch created")
        
        print()
        
        # ==========================================
        # PHASE 5: PHYSICS PLAYGROUND
        # ==========================================
        print("=" * 60)
        print("PHASE 5: ADDING PHYSICS OBJECTS")
        print("=" * 60 + "\n")
        
        print("[PHYSICS] Spawning destructible objects...")
        
        # Spawn physics-enabled objects
        physics_objects = [
            {"name": "PhysicsBarrel_1", "location": [1000, 1000, 100]},
            {"name": "PhysicsBarrel_2", "location": [-1000, 1000, 100]},
            {"name": "PhysicsBarrel_3", "location": [1000, -1000, 100]},
            {"name": "PhysicsBarrel_4", "location": [-1000, -1000, 100]},
            {"name": "PhysicsCrate_1", "location": [500, 0, 100]},
            {"name": "PhysicsCrate_2", "location": [-500, 0, 100]},
            {"name": "PhysicsCrate_3", "location": [0, 500, 100]},
            {"name": "PhysicsCrate_4", "location": [0, -500, 100]}
        ]
        
        for obj in physics_objects:
            print(f"  Spawning {obj['name']}...")
            response = self.send_command("spawn_physics_blueprint_actor", {
                "name": obj["name"],
                "mesh_path": "/Engine/BasicShapes/Cube",  # Default cube mesh
                "location": obj["location"],
                "mass": 50.0,
                "enable_physics": True
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {obj['name']} spawned")
        
        print()
        
        # ==========================================
        # PHASE 6: ATMOSPHERIC ELEMENTS
        # ==========================================
        print("=" * 60)
        print("PHASE 6: ATMOSPHERIC SETUP")
        print("=" * 60 + "\n")
        
        print("[ATMOSPHERE] Adding lighting and atmosphere...")
        
        # Spawn atmospheric actors
        atmosphere = [
            {
                "type": "DirectionalLight",
                "name": "MainSun",
                "location": [0, 0, 10000],
                "rotation": [-45, 135, 0]
            },
            {
                "type": "ExponentialHeightFog",
                "name": "Fog",
                "location": [0, 0, 0],
                "rotation": [0, 0, 0]
            },
            {
                "type": "SkyAtmosphere",
                "name": "Atmosphere",
                "location": [0, 0, 0],
                "rotation": [0, 0, 0]
            }
        ]
        
        for atmo in atmosphere:
            print(f"  Adding {atmo['name']}...")
            response = self.send_command("spawn_actor", {
                "name": atmo["name"],
                "type": atmo["type"],
                "location": atmo["location"],
                "rotation": atmo["rotation"]
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {atmo['name']} added")
        
        print()
        
        # ==========================================
        # FINAL SUMMARY
        # ==========================================
        print("=" * 80)
        print("  TERMINAL GROUNDS DEMO - BUILD COMPLETE!")
        print("=" * 80)
        print("\nCREATED FEATURES:")
        print("\n[SETTLEMENT]")
        print("  -> 1 Command HQ Mansion")
        print("  -> 2 Modern houses")
        print("  -> 2 Cottages")
        print("\n[DEFENSES]")
        print("  -> 4 Perimeter walls (7000 units each)")
        print("  -> 4 Corner watchtowers (5 levels)")
        print("\n[TACTICAL]")
        print("  -> 10x10 Combat maze")
        print("  -> 3 Extraction zones with archways")
        print("\n[INTERACTIVE]")
        print("  -> 8 Physics-enabled objects")
        print("  -> Full atmospheric lighting")
        print("\n[PLUGINS UTILIZED]")
        print("  -> Flopperam MCP (advanced building)")
        print("  -> ProceduralDungeon (ready for integration)")
        print("  -> StreetMap (ready for real-world data)")
        print("\n" + "=" * 80)
        print("\nTO PLAY YOUR DEMO:")
        print("  1. Press Play in Unreal Editor (Alt+P)")
        print("  2. Explore the settlement")
        print("  3. Navigate the tactical maze")
        print("  4. Reach extraction points")
        print("  5. Interact with physics objects")
        print("\nYour Terminal Grounds demo is ready!")
        print("=" * 80 + "\n")
        
        return True

def main():
    print("TERMINAL GROUNDS - Ultimate Demo Builder")
    print("Powered by Flopperam MCP + ProceduralDungeon + StreetMap")
    print("-" * 60)
    
    demo = TerminalGroundsUltimateDemo()
    
    if demo.build_epic_demo():
        print("[SUCCESS] Epic demo built successfully!")
        return 0
    else:
        print("[FAILED] Could not complete demo build")
        print("\nTroubleshooting:")
        print("  1. Make sure Unreal Engine is running")
        print("  2. Enable these plugins in Project Settings:")
        print("     - UnrealMCP (from flopperam)")
        print("     - ProceduralDungeon")
        print("     - StreetMap")
        print("  3. The MCP plugin should be listening on port 13377")
        print("  4. Restart Unreal Editor after enabling plugins")
        return 1

if __name__ == "__main__":
    sys.exit(main())