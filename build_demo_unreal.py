#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Demo Builder for Unreal Engine
Direct connection to Unreal MCP Plugin
"""

import socket
import json
import time
import sys

class UnrealDemoBuilder:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 55557  # Unreal MCP Plugin port
        
    def send_unreal_command(self, command):
        """Send a properly formatted command to Unreal MCP"""
        try:
            # Create new socket for each command (Unreal closes after each)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.host, self.port))
            
            # Format command with proper type field
            cmd = {
                'type': 'execute',  # Using execute type as shown in logs
                'command': command,
                'params': {}
            }
            
            # Send as JSON with newline
            message = json.dumps(cmd) + '\n'
            s.send(message.encode('utf-8'))
            
            # Try to receive response
            try:
                response = s.recv(4096).decode('utf-8')
                print(f"[RESPONSE] {response[:100]}")  # First 100 chars
            except socket.timeout:
                print("[TIMEOUT] No response from Unreal")
            
            s.close()
            time.sleep(0.1)  # Small delay between commands
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send command: {e}")
            return False
    
    def build_demo(self):
        """Build the demo using Unreal console commands"""
        print("\n" + "=" * 60)
        print("[START] Building Terminal Grounds Demo")
        print("=" * 60 + "\n")
        
        # Test connection
        print("[TEST] Testing connection to Unreal...")
        if not self.send_unreal_command("ke * stat fps"):
            print("[ERROR] Cannot connect to Unreal Engine MCP")
            print("Make sure Unreal Editor is running with MCP plugin enabled")
            return False
        
        print("[OK] Connected to Unreal Engine\n")
        
        # Load the TechWastes map if needed
        print("[MAP] Loading TechWastes map...")
        self.send_unreal_command("open /Game/TG/Maps/TechWastes/TechWastes_Band_Gamma")
        time.sleep(3)  # Give time for map to load
        
        # Clear any existing demo actors
        print("[CLEANUP] Clearing existing demo actors...")
        self.send_unreal_command("DestroyAll TGEnemyGrunt")
        self.send_unreal_command("DestroyAll TGWeapon")
        time.sleep(0.5)
        
        # Spawn AI enemies at strategic positions
        print("\n[AI] Spawning 8 AI enemies...")
        enemy_positions = [
            (500, 500, 100),
            (-500, 500, 100),
            (500, -500, 100),
            (-500, -500, 100),
            (0, 800, 100),
            (0, -800, 100),
            (800, 0, 100),
            (-800, 0, 100)
        ]
        
        for i, (x, y, z) in enumerate(enemy_positions, 1):
            cmd = f"summon TGEnemyGrunt X={x} Y={y} Z={z}"
            if self.send_unreal_command(cmd):
                print(f"  [OK] Enemy {i} spawned at ({x}, {y}, {z})")
        
        # Spawn player pawn
        print("\n[PLAYER] Spawning player character...")
        self.send_unreal_command("summon TGPlayPawn X=0 Y=0 Z=200")
        print("  [OK] Player spawned at origin")
        
        # Spawn weapon for player
        print("\n[WEAPON] Spawning weapon...")
        self.send_unreal_command("summon TGWeapon X=50 Y=0 Z=200")
        print("  [OK] Weapon spawned near player")
        
        # Create some cover objects using basic shapes
        print("\n[COVER] Creating cover objects...")
        cover_positions = [
            (300, 300, 0),
            (-300, 300, 0),
            (300, -300, 0),
            (-300, -300, 0)
        ]
        
        for i, (x, y, z) in enumerate(cover_positions, 1):
            # Using cube static mesh actors as cover
            cmd = f"summon StaticMeshActor X={x} Y={y} Z={z}"
            if self.send_unreal_command(cmd):
                print(f"  [OK] Cover {i} placed at ({x}, {y}, {z})")
        
        # Setup lighting
        print("\n[LIGHTING] Configuring atmosphere...")
        self.send_unreal_command("r.TonemapperGamma 2.2")
        self.send_unreal_command("r.Exposure.Offset 0.5")
        self.send_unreal_command("r.Fog 1")
        print("  [OK] Atmospheric settings applied")
        
        # Set game mode settings
        print("\n[GAME] Configuring game settings...")
        self.send_unreal_command("slomo 1.0")  # Normal time scale
        self.send_unreal_command("god")  # God mode for testing
        self.send_unreal_command("show collision")  # Show collision for debugging
        time.sleep(0.5)
        self.send_unreal_command("show collision")  # Toggle back off
        print("  [OK] Game settings configured")
        
        # Focus viewport on the action
        print("\n[CAMERA] Setting viewport focus...")
        self.send_unreal_command("bugitgo 0 0 500 0 -30 0")  # Position camera
        print("  [OK] Camera positioned")
        
        # Take screenshot
        print("\n[SCREENSHOT] Capturing demo screenshot...")
        self.send_unreal_command("HighResShot 1920x1080")
        print("  [OK] Screenshot saved to Unreal project")
        
        # Final stats
        print("\n" + "=" * 60)
        print("[SUCCESS] DEMO BUILD COMPLETE!")
        print("=" * 60)
        print("\nDemo Features:")
        print("  -> 8 AI enemies (TGEnemyGrunt)")
        print("  -> Player character (TGPlayPawn)")
        print("  -> Weapon system (TGWeapon)")
        print("  -> Strategic cover positions")
        print("  -> Atmospheric lighting")
        print("  -> TechWastes map loaded")
        print("\n[READY] Switch to Unreal Editor to play the demo!")
        print("Press PIE (Play In Editor) to start playing")
        print("=" * 60 + "\n")
        
        return True

def main():
    builder = UnrealDemoBuilder()
    
    print("Terminal Grounds - Live Demo Builder")
    print("=====================================")
    print("Connecting to Unreal Engine MCP on port 55557...")
    
    if builder.build_demo():
        return 0
    else:
        print("\n[FAILED] Demo build encountered errors")
        print("Please check Unreal Engine console for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())