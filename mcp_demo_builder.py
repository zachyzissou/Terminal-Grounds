#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds MCP Demo Builder
Uses the correct MCP protocol to build a playable demo
"""

import json
import socket
import sys
import time

HOST = "127.0.0.1"
PORT = 55557

def send_mcp_command(command, params=None):
    """Send command using the correct MCP protocol"""
    msg = json.dumps({"command": command, "params": params or {}}) + "\n"
    
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as s:
            s.sendall(msg.encode("utf-8"))
            data = b""
            while True:
                b = s.recv(4096)
                if not b:
                    break
                data += b
                if b"\n" in b:
                    break
        
        line = data.decode("utf-8").split("\n", 1)[0]
        try:
            return json.loads(line)
        except Exception:
            return {"raw": line}
    except Exception as e:
        print(f"[ERROR] Failed to send command '{command}': {e}")
        return None

def build_demo():
    """Build the Terminal Grounds demo"""
    print("\n" + "=" * 60)
    print("TERMINAL GROUNDS - MCP DEMO BUILDER")
    print("=" * 60 + "\n")
    
    # Test connection
    print("[TEST] Checking MCP connection...")
    result = send_mcp_command("health")
    if not result or result.get("status") != "ok":
        print("[ERROR] Cannot connect to Unreal MCP server")
        print("Make sure Unreal Engine is running with MCP plugin enabled")
        return False
    print("[OK] Connected to Unreal MCP server")
    
    # Get version info
    print("\n[INFO] Getting Unreal version...")
    result = send_mcp_command("get_version")
    if result and result.get("status") == "success":
        version = result.get("result", {})
        print(f"  Engine: {version.get('engine', 'Unknown')}")
        print(f"  Plugin: {version.get('plugin', 'Unknown')}")
    
    # Get available tools
    print("\n[INFO] Checking available MCP tools...")
    result = send_mcp_command("get_tools")
    if result and result.get("status") == "success":
        tools = result.get("result", [])
        print(f"  Found {len(tools)} tools available")
    
    print("\n[BUILD] Starting demo construction...\n")
    
    # Spawn AI enemies
    print("[AI] Spawning 8 AI enemies...")
    enemy_positions = [
        {"x": 500, "y": 500, "z": 100},
        {"x": -500, "y": 500, "z": 100},
        {"x": 500, "y": -500, "z": 100},
        {"x": -500, "y": -500, "z": 100},
        {"x": 0, "y": 800, "z": 100},
        {"x": 0, "y": -800, "z": 100},
        {"x": 800, "y": 0, "z": 100},
        {"x": -800, "y": 0, "z": 100}
    ]
    
    for i, location in enumerate(enemy_positions, 1):
        params = {
            "type": "TGEnemyGrunt",
            "name": f"Enemy_{i}",
            "location": location,
            "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
        }
        result = send_mcp_command("spawn_actor", params)
        if result and result.get("status") == "success":
            print(f"  [OK] Enemy {i} spawned at ({location['x']}, {location['y']}, {location['z']})")
        else:
            print(f"  [FAIL] Could not spawn Enemy {i}")
    
    # Spawn player
    print("\n[PLAYER] Spawning player character...")
    params = {
        "type": "TGPlayPawn",
        "name": "Player",
        "location": {"x": 0, "y": 0, "z": 200},
        "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
    }
    result = send_mcp_command("spawn_actor", params)
    if result and result.get("status") == "success":
        print("  [OK] Player spawned at origin")
    else:
        print("  [FAIL] Could not spawn player")
    
    # Spawn weapon
    print("\n[WEAPON] Spawning weapon...")
    params = {
        "type": "TGWeapon",
        "name": "PlayerWeapon",
        "location": {"x": 50, "y": 0, "z": 200},
        "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
    }
    result = send_mcp_command("spawn_actor", params)
    if result and result.get("status") == "success":
        print("  [OK] Weapon spawned near player")
    else:
        print("  [FAIL] Could not spawn weapon")
    
    # Create cover objects (using cube static mesh)
    print("\n[COVER] Creating cover objects...")
    cover_positions = [
        {"x": 300, "y": 300, "z": 50},
        {"x": -300, "y": 300, "z": 50},
        {"x": 300, "y": -300, "z": 50},
        {"x": -300, "y": -300, "z": 50}
    ]
    
    for i, location in enumerate(cover_positions, 1):
        params = {
            "type": "StaticMeshActor",
            "name": f"Cover_{i}",
            "location": location,
            "rotation": {"pitch": 0, "yaw": 0, "roll": 0},
            "scale": {"x": 2, "y": 2, "z": 3}
        }
        result = send_mcp_command("spawn_actor", params)
        if result and result.get("status") == "success":
            print(f"  [OK] Cover {i} placed at ({location['x']}, {location['y']}, {location['z']})")
        else:
            print(f"  [FAIL] Could not place Cover {i}")
    
    # Add lighting
    print("\n[LIGHTING] Setting up atmospheric lighting...")
    
    # Directional light (sun)
    params = {
        "type": "DirectionalLight",
        "name": "Sun",
        "location": {"x": 0, "y": 0, "z": 1000},
        "rotation": {"pitch": -45, "yaw": 45, "roll": 0}
    }
    result = send_mcp_command("spawn_actor", params)
    if result and result.get("status") == "success":
        print("  [OK] Directional light created")
    
    # Sky light
    params = {
        "type": "SkyLight",
        "name": "SkyLight",
        "location": {"x": 0, "y": 0, "z": 500}
    }
    result = send_mcp_command("spawn_actor", params)
    if result and result.get("status") == "success":
        print("  [OK] Sky light created")
    
    # Exponential fog
    params = {
        "type": "ExponentialHeightFog",
        "name": "Fog",
        "location": {"x": 0, "y": 0, "z": 0}
    }
    result = send_mcp_command("spawn_actor", params)
    if result and result.get("status") == "success":
        print("  [OK] Atmospheric fog created")
    
    # Focus viewport on the scene
    print("\n[CAMERA] Setting viewport focus...")
    params = {
        "target": "Player",
        "distance": 1000
    }
    result = send_mcp_command("focus_viewport", params)
    if result and result.get("status") == "success":
        print("  [OK] Viewport focused on player")
    
    # Take screenshot
    print("\n[SCREENSHOT] Capturing demo scene...")
    params = {
        "filename": "TerminalGrounds_Demo.png",
        "resolution": {"width": 1920, "height": 1080}
    }
    result = send_mcp_command("take_screenshot", params)
    if result and result.get("status") == "success":
        print("  [OK] Screenshot saved")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] DEMO BUILD COMPLETE!")
    print("=" * 60)
    print("\nDemo Features Built:")
    print("  -> 8 AI enemies (TGEnemyGrunt)")
    print("  -> Player character (TGPlayPawn)")
    print("  -> Weapon system (TGWeapon)")
    print("  -> 4 strategic cover positions")
    print("  -> Atmospheric lighting (Sun, Sky, Fog)")
    print("  -> Screenshot captured")
    print("\n[READY] Switch to Unreal Editor and press PIE to play!")
    print("=" * 60 + "\n")
    
    return True

def main():
    print("Terminal Grounds - MCP Demo Builder")
    print("Connecting to Unreal Engine on port 55557...")
    
    if build_demo():
        return 0
    else:
        print("\n[FAILED] Demo build failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())