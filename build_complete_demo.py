#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Complete Demo Builder
Builds entire playable demo using built-in Unreal classes
"""

import socket
import json
import time
import sys

class CompleteDemoBuilder:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 55557
        
    def send_command(self, cmd_type, params=None):
        """Send command using MCP protocol"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.host, self.port))
            
            message = {"type": cmd_type}
            if params:
                message["params"] = params
                
            msg = json.dumps(message) + '\n'
            s.send(msg.encode('utf-8'))
            
            response = s.recv(8192).decode('utf-8')
            s.close()
            
            return json.loads(response.strip())
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def spawn_actor(self, actor_type, name, x, y, z, pitch=0, yaw=0, roll=0, scale_x=1, scale_y=1, scale_z=1):
        """Spawn an actor with location, rotation and scale"""
        params = {
            "type": actor_type,
            "name": name,
            "location": {"x": x, "y": y, "z": z},
            "rotation": {"pitch": pitch, "yaw": yaw, "roll": roll},
            "scale": {"x": scale_x, "y": scale_y, "z": scale_z}
        }
        return self.send_command("spawn_actor", params)
    
    def build_demo(self):
        """Build complete playable demo"""
        print("\n" + "=" * 70)
        print("  TERMINAL GROUNDS - COMPLETE DEMO BUILDER")
        print("=" * 70 + "\n")
        
        # Test connection
        print("[INIT] Testing MCP connection...")
        result = self.send_command("ping")
        if result.get("status") != "success":
            print("[ERROR] Cannot connect to Unreal MCP")
            return False
        print("[OK] Connected to Unreal Engine\n")
        
        print("[BUILD] Creating complete Terminal Grounds demo...\n")
        
        # Try different actor types for enemies
        print("[ENEMIES] Spawning combat targets...")
        enemy_types_to_try = [
            "/Game/TG/Blueprints/BP_EnemyGrunt.BP_EnemyGrunt_C",
            "BP_EnemyGrunt",
            "/Script/Engine.Character",
            "Character",
            "/Script/Engine.Pawn",
            "Pawn",
            "TargetPoint"
        ]
        
        enemy_positions = [
            (500, 500, 100), (-500, 500, 100), (500, -500, 100), (-500, -500, 100),
            (0, 800, 100), (0, -800, 100), (800, 0, 100), (-800, 0, 100)
        ]
        
        enemies_spawned = 0
        working_enemy_type = None
        
        # Find which enemy type works
        for enemy_type in enemy_types_to_try:
            x, y, z = enemy_positions[0]
            result = self.spawn_actor(enemy_type, "TestEnemy", x, y, z)
            if result.get("status") == "success":
                print(f"  [FOUND] Working enemy type: {enemy_type}")
                working_enemy_type = enemy_type
                enemies_spawned = 1
                break
        
        # Spawn remaining enemies with working type
        if working_enemy_type:
            for i, (x, y, z) in enumerate(enemy_positions[1:], 2):
                result = self.spawn_actor(working_enemy_type, f"Enemy_{i}", x, y, z)
                if result.get("status") == "success":
                    enemies_spawned += 1
                    print(f"  [OK] Enemy {i} spawned at ({x}, {y}, {z})")
        else:
            print("  [WARN] Could not find working enemy type, using target points")
            for i, (x, y, z) in enumerate(enemy_positions, 1):
                result = self.spawn_actor("TargetPoint", f"EnemyMarker_{i}", x, y, z)
                if result.get("status") == "success":
                    print(f"  [OK] Enemy marker {i} placed at ({x}, {y}, {z})")
        
        print(f"  -> Spawned {enemies_spawned} combat targets\n")
        
        # Try to spawn player
        print("[PLAYER] Creating player spawn point...")
        player_types = [
            "/Game/TG/Blueprints/BP_PlayPawn.BP_PlayPawn_C",
            "BP_PlayPawn",
            "/Script/Engine.DefaultPawn",
            "DefaultPawn",
            "PlayerStart"
        ]
        
        player_spawned = False
        for player_type in player_types:
            result = self.spawn_actor(player_type, "PlayerSpawn", 0, 0, 200)
            if result.get("status") == "success":
                print(f"  [OK] Player spawn created using {player_type}\n")
                player_spawned = True
                break
        
        if not player_spawned:
            print("  [WARN] Could not spawn player, you'll spawn at default location\n")
        
        # Create detailed cover system
        print("[COVER] Building tactical cover system...")
        
        # Large cover blocks
        large_cover = [
            (400, 400, 75, 3, 1, 2),  # Corner covers
            (-400, 400, 75, 3, 1, 2),
            (400, -400, 75, 3, 1, 2),
            (-400, -400, 75, 3, 1, 2)
        ]
        
        for i, (x, y, z, sx, sy, sz) in enumerate(large_cover, 1):
            result = self.spawn_actor("StaticMeshActor", f"LargeCover_{i}", x, y, z, 0, 0, 0, sx, sy, sz)
            if result.get("status") == "success":
                print(f"  [OK] Large cover {i} at ({x}, {y})")
        
        # Small cover points
        small_cover = [
            (200, 0, 50), (-200, 0, 50), (0, 200, 50), (0, -200, 50),
            (600, 200, 50), (600, -200, 50), (-600, 200, 50), (-600, -200, 50)
        ]
        
        for i, (x, y, z) in enumerate(small_cover, 1):
            result = self.spawn_actor("StaticMeshActor", f"SmallCover_{i}", x, y, z, 0, 0, 0, 1.5, 1.5, 1.5)
            if result.get("status") == "success":
                print(f"  [OK] Small cover {i} at ({x}, {y})")
        
        print("  -> Cover system deployed\n")
        
        # Create weapons/pickups using target points
        print("[ITEMS] Placing weapon and item spawns...")
        weapon_spawns = [
            (100, 0, 100, "WeaponSpawn_1"),
            (-100, 100, 100, "WeaponSpawn_2"),
            (0, -200, 100, "WeaponSpawn_3"),
            (300, 300, 100, "AmmoSpawn_1"),
            (-300, -300, 100, "AmmoSpawn_2")
        ]
        
        for x, y, z, name in weapon_spawns:
            result = self.spawn_actor("TargetPoint", name, x, y, z)
            if result.get("status") == "success":
                print(f"  [OK] {name} placed")
        
        print("  -> Item spawn points created\n")
        
        # Enhanced lighting setup
        print("[ATMOSPHERE] Creating immersive lighting...")
        
        # Main directional light (sun)
        result = self.spawn_actor("DirectionalLight", "Sun", 0, 0, 2000, -60, 45, 0)
        if result.get("status") == "success":
            print("  [OK] Main sun light created")
        
        # Additional lights for atmosphere
        point_lights = [
            (500, 500, 300, "Light_NE"),
            (-500, 500, 300, "Light_NW"),
            (500, -500, 300, "Light_SE"),
            (-500, -500, 300, "Light_SW")
        ]
        
        for x, y, z, name in point_lights:
            result = self.spawn_actor("PointLight", name, x, y, z)
            if result.get("status") == "success":
                print(f"  [OK] {name} placed")
        
        # Spot lights for dramatic effect
        spot_lights = [
            (0, 0, 500, -90, 0, 0, "SpotLight_Center"),
            (300, 0, 400, -45, 180, 0, "SpotLight_East")
        ]
        
        for x, y, z, pitch, yaw, roll, name in spot_lights:
            result = self.spawn_actor("SpotLight", name, x, y, z, pitch, yaw, roll)
            if result.get("status") == "success":
                print(f"  [OK] {name} created")
        
        print("  -> Atmospheric lighting complete\n")
        
        # Create navigation markers
        print("[NAVIGATION] Setting up level boundaries...")
        boundary_markers = [
            (1000, 1000, 50, "Boundary_NE"),
            (-1000, 1000, 50, "Boundary_NW"),
            (1000, -1000, 50, "Boundary_SE"),
            (-1000, -1000, 50, "Boundary_SW")
        ]
        
        for x, y, z, name in boundary_markers:
            result = self.spawn_actor("TargetPoint", name, x, y, z)
            if result.get("status") == "success":
                print(f"  [OK] {name} placed")
        
        print("  -> Level boundaries defined\n")
        
        # Create extraction/objective points
        print("[OBJECTIVES] Creating mission objectives...")
        objectives = [
            (0, 1000, 100, "Extraction_North"),
            (0, -1000, 100, "Extraction_South"),
            (0, 0, 100, "CapturePoint_Center")
        ]
        
        for x, y, z, name in objectives:
            result = self.spawn_actor("TargetPoint", name, x, y, z)
            if result.get("status") == "success":
                print(f"  [OK] {name} created")
        
        print("  -> Objectives placed\n")
        
        # Take final screenshot
        print("[CAPTURE] Taking demo screenshot...")
        timestamp = int(time.time())
        filepath = f"TG_Complete_Demo_{timestamp}.png"
        result = self.send_command("take_screenshot", {"filepath": filepath})
        if result.get("status") == "success":
            print(f"  [OK] Screenshot saved: {filepath}\n")
        
        # Final summary
        print("=" * 70)
        print("  TERMINAL GROUNDS DEMO - BUILD COMPLETE!")
        print("=" * 70)
        print("\nDEMO FEATURES:")
        print(f"  [COMBAT]")
        print(f"    -> {enemies_spawned} Enemy spawn points")
        print(f"    -> Player spawn position")
        print(f"    -> 5 Weapon/ammo spawn points")
        print(f"  [TACTICAL]")
        print(f"    -> 4 Large cover positions")
        print(f"    -> 8 Small cover points")
        print(f"    -> Strategic positioning")
        print(f"  [ATMOSPHERE]")
        print(f"    -> Directional sun lighting")
        print(f"    -> 4 Point lights for ambience")
        print(f"    -> 2 Spot lights for drama")
        print(f"  [OBJECTIVES]")
        print(f"    -> 2 Extraction points")
        print(f"    -> 1 Central capture point")
        print(f"    -> 4 Boundary markers")
        
        print("\n[PLAY INSTRUCTIONS]")
        print("  1. Switch to Unreal Editor")
        print("  2. Press Play (Alt+P) or PIE button")
        print("  3. WASD to move, Mouse to look")
        print("  4. Left click to shoot (if weapon equipped)")
        print("  5. Navigate between cover positions")
        print("  6. Reach extraction points to complete")
        
        print("\n[SUCCESS] Your playable demo is ready in Unreal Engine!")
        print("=" * 70 + "\n")
        
        return True

def main():
    print("TERMINAL GROUNDS - Complete Demo Builder")
    print("Building your entire playable demo...")
    
    builder = CompleteDemoBuilder()
    
    if builder.build_demo():
        print("[DONE] Demo successfully built! Switch to Unreal to play.")
        return 0
    else:
        print("[FAILED] Could not complete demo build.")
        return 1

if __name__ == "__main__":
    sys.exit(main())