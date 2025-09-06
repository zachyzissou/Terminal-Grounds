#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force open a map in Unreal Editor RIGHT NOW
"""

import socket
import json
import time

def send_command(cmd_type, params=None):
    """Send command to MCP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(('127.0.0.1', 55557))
        
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

print("FORCING MAP OPEN IN UNREAL EDITOR")
print("=" * 50)

# Test connection
result = send_command("ping")
if result.get("status") == "success":
    print("[OK] Connected to Unreal MCP")
else:
    print("[ERROR] Cannot connect to Unreal")
    exit(1)

# Try EVERY possible way to open a map
print("\n[ATTEMPTING] Opening Demo_Combat_Zone map...\n")

# All possible command variations to try
map_commands = [
    # Console command variations
    ("execute_console_command", {"command": "open Demo_Combat_Zone"}),
    ("execute_console_command", {"command": "open /Game/Maps/Demo_Combat_Zone"}),
    ("console_command", {"command": "open Demo_Combat_Zone"}),
    ("exec", {"command": "open Demo_Combat_Zone"}),
    
    # Editor specific commands
    ("editor_command", {"command": "open Demo_Combat_Zone"}),
    ("editor.load_map", {"map": "/Game/Maps/Demo_Combat_Zone"}),
    ("editor.open", {"asset": "/Game/Maps/Demo_Combat_Zone"}),
    
    # Direct execute variations
    ("execute", {"command": "open /Game/Maps/Demo_Combat_Zone"}),
    ("execute", {"command": "LoadLevel Demo_Combat_Zone"}),
    ("execute", {"command": "OpenLevel Demo_Combat_Zone"}),
    
    # Travel command (sometimes works in editor)
    ("execute", {"command": "travel Demo_Combat_Zone"}),
    ("execute", {"command": "servertravel Demo_Combat_Zone"}),
    
    # Blueprint/asset loading
    ("load_asset", {"path": "/Game/Maps/Demo_Combat_Zone"}),
    ("open_asset", {"asset": "/Game/Maps/Demo_Combat_Zone.Demo_Combat_Zone"}),
]

success = False
for cmd_type, params in map_commands:
    print(f"[TRY] {cmd_type}: {params.get('command', params.get('map', params.get('asset', '')))}")
    result = send_command(cmd_type, params)
    
    if result.get("status") == "success":
        print(f"  -> SUCCESS! Map should be opening!")
        success = True
        break
    elif "Unknown command" not in str(result.get("error", "")):
        # If it's not "Unknown command", it might have worked
        print(f"  -> Response: {result}")
        if "error" not in str(result).lower():
            success = True
            break

if not success:
    print("\n[FALLBACK] Trying IEZ_District_Alpha instead...\n")
    
    # Try with IEZ map
    alternate_commands = [
        ("execute", {"command": "open /Game/TG/Maps/IEZ/IEZ_District_Alpha"}),
        ("execute_console_command", {"command": "open IEZ_District_Alpha"}),
        ("console_command", {"command": "open /Game/TG/Maps/IEZ/IEZ_District_Alpha"}),
    ]
    
    for cmd_type, params in alternate_commands:
        print(f"[TRY] {cmd_type}: {params.get('command', '')}")
        result = send_command(cmd_type, params)
        
        if result.get("status") == "success":
            print(f"  -> SUCCESS! IEZ map should be opening!")
            success = True
            break

print("\n" + "=" * 50)
if success:
    print("[SUCCESS] Map open command sent!")
    print("\nThe map should be loading in Unreal Editor now.")
    print("Wait a moment for it to load, then you'll see the level.")
else:
    print("[INFO] Could not open map via MCP commands.")
    print("\nMANUAL STEPS TO OPEN MAP:")
    print("1. In Unreal Editor, click File -> Open Level")
    print("2. Navigate to: Content/Maps/Demo_Combat_Zone")
    print("3. Or navigate to: Content/TG/Maps/IEZ/IEZ_District_Alpha")
    print("4. Double-click the map to open it")
    print("\nThen run the demo builder script again!")

print("=" * 50)