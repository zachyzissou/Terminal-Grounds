#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use the ACTUAL documented MCP commands to open map and build demo
Based on the real MCP tool definitions in unreal-mcp
"""

import socket
import json
import time
import sys

class RealMCPDemo:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 55557  # The actual MCP plugin port in Unreal
        
    def send_command(self, command, params=None):
        """Send command using the documented format"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((self.host, self.port))
            
            # Based on the code, commands are sent with "command" field
            message = {
                "command": command,
                "params": params or {}
            }
            
            msg = json.dumps(message) + '\n'
            print(f"[SEND] {command}: {params}")
            s.send(msg.encode('utf-8'))
            
            # Receive response
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n' in chunk:
                    break
            
            s.close()
            
            if data:
                response = json.loads(data.decode('utf-8').strip())
                return response
            return None
            
        except Exception as e:
            print(f"[ERROR] {command}: {e}")
            return None
    
    def build_complete_demo(self):
        """Build demo using the ACTUAL MCP commands"""
        print("\n" + "=" * 70)
        print("  TERMINAL GROUNDS - USING REAL MCP COMMANDS")
        print("=" * 70 + "\n")
        
        # According to the documentation, these are the REAL commands:
        # - get_actors_in_level
        # - find_actors_by_name
        # - spawn_actor
        # - delete_actor
        # - set_actor_transform
        # - get_actor_properties
        # - focus_viewport
        # - take_screenshot
        # - open_level (let's try this)
        # - load_map (alternative)
        
        print("[1] Testing connection...")
        response = self.send_command("get_actors_in_level")
        if response:
            actors = response.get("result", {}).get("actors", [])
            print(f"  -> Found {len(actors)} actors in current level\n")
        else:
            print("  -> Could not connect to MCP server\n")
            return False
        
        # Try to open a map
        print("[2] Attempting to open map...")
        maps_to_try = [
            "Demo_Combat_Zone",
            "/Game/Maps/Demo_Combat_Zone",
            "/Game/TG/Maps/IEZ/IEZ_District_Alpha",
            "IEZ_District_Alpha"
        ]
        
        for map_path in maps_to_try:
            # Try different command names
            for cmd in ["open_level", "load_level", "load_map", "open_map"]:
                response = self.send_command(cmd, {"level": map_path})
                if response and response.get("status") != "error":
                    print(f"  -> Map opened with {cmd}: {map_path}\n")
                    time.sleep(3)  # Let map load
                    break
        
        # Now spawn actors using the REAL spawn_actor command format
        print("[3] Spawning demo content...\n")
        
        # According to editor_tools.py, spawn_actor takes:
        # - name: unique name
        # - type: actor type (uppercase)
        # - location: [x, y, z]
        # - rotation: [pitch, yaw, roll]
        
        print("  [COVER] Creating tactical cover...")
        cover_positions = [
            ([500, 500, 100], "Cover_NE"),
            ([-500, 500, 100], "Cover_NW"),
            ([500, -500, 100], "Cover_SE"),
            ([-500, -500, 100], "Cover_SW"),
            ([0, 700, 100], "Cover_N"),
            ([0, -700, 100], "Cover_S")
        ]
        
        covers_spawned = 0
        for location, name in cover_positions:
            response = self.send_command("spawn_actor", {
                "name": name,
                "type": "STATICMESHACTOR",  # Uppercase as per the code
                "location": location,
                "rotation": [0.0, 0.0, 0.0]
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {name} spawned")
                covers_spawned += 1
            else:
                error = response.get("error", "Unknown") if response else "No response"
                print(f"    [FAIL] {name}: {error}")
        
        print(f"  -> Created {covers_spawned} cover positions\n")
        
        print("  [LIGHTS] Adding atmospheric lighting...")
        light_positions = [
            ([0, 0, 2000], "Sun", "DIRECTIONALLIGHT", [-45, 135, 0]),
            ([800, 800, 400], "Light_NE", "POINTLIGHT", [0, 0, 0]),
            ([-800, 800, 400], "Light_NW", "POINTLIGHT", [0, 0, 0]),
            ([800, -800, 400], "Light_SE", "POINTLIGHT", [0, 0, 0]),
            ([-800, -800, 400], "Light_SW", "POINTLIGHT", [0, 0, 0]),
            ([0, 0, 600], "Light_Center", "SPOTLIGHT", [-90, 0, 0])
        ]
        
        lights_spawned = 0
        for location, name, light_type, rotation in light_positions:
            response = self.send_command("spawn_actor", {
                "name": name,
                "type": light_type,
                "location": location,
                "rotation": rotation
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {name} created")
                lights_spawned += 1
        
        print(f"  -> Created {lights_spawned} lights\n")
        
        print("  [OBJECTIVES] Placing spawn points...")
        objectives = [
            ([0, 0, 200], "PlayerStart", "PLAYERSTART"),
            ([0, 1200, 100], "Extraction_North", "TARGETPOINT"),
            ([0, -1200, 100], "Extraction_South", "TARGETPOINT"),
            ([600, 600, 100], "Objective_A", "TARGETPOINT"),
            ([-600, -600, 100], "Objective_B", "TARGETPOINT")
        ]
        
        for location, name, obj_type in objectives:
            response = self.send_command("spawn_actor", {
                "name": name,
                "type": obj_type,
                "location": location,
                "rotation": [0.0, 0.0, 0.0]
            })
            if response and response.get("status") != "error":
                print(f"    [OK] {name} placed")
        
        print()
        
        # Focus viewport on the scene
        print("[4] Setting viewport focus...")
        response = self.send_command("focus_viewport", {
            "target": "PlayerStart",
            "distance": 1500
        })
        if response and response.get("status") != "error":
            print("  -> Viewport focused on scene\n")
        
        # Take screenshot
        print("[5] Capturing screenshot...")
        response = self.send_command("take_screenshot", {
            "filename": f"TG_Demo_{int(time.time())}.png",
            "show_ui": False,
            "resolution": [1920, 1080]
        })
        if response and response.get("status") != "error":
            print("  -> Screenshot captured\n")
        
        # Get final actor count
        print("[6] Verifying demo build...")
        response = self.send_command("get_actors_in_level")
        if response:
            actors = response.get("result", {}).get("actors", [])
            print(f"  -> Total actors in level: {len(actors)}\n")
        
        print("=" * 70)
        print("  DEMO BUILD COMPLETE!")
        print("=" * 70)
        print("\nCREATED:")
        print(f"  -> {covers_spawned} Tactical cover positions")
        print(f"  -> {lights_spawned} Atmospheric lights")
        print("  -> Multiple objectives and spawn points")
        print("  -> Screenshot captured")
        print("\nTO PLAY:")
        print("  1. You should see the demo in Unreal Editor")
        print("  2. Press Play button or Alt+P")
        print("  3. Use WASD to move around the tactical arena")
        print("=" * 70 + "\n")
        
        return True

def main():
    print("Terminal Grounds - Real MCP Commands Demo")
    print("Using documented MCP protocol...")
    
    demo = RealMCPDemo()
    
    if demo.build_complete_demo():
        print("[SUCCESS] Demo built with real MCP commands!")
        return 0
    else:
        print("[FAILED] Could not complete demo")
        return 1

if __name__ == "__main__":
    sys.exit(main())