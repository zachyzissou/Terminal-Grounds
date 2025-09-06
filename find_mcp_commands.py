#!/usr/bin/env python3
"""Find valid MCP commands"""

import socket
import json

def send_command(cmd_type, params=None):
    """Send a command with type field"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 55557))
        
        message = {"type": cmd_type}
        if params:
            message["params"] = params
            
        msg = json.dumps(message) + '\n'
        s.send(msg.encode('utf-8'))
        
        response = s.recv(4096).decode('utf-8')
        s.close()
        
        return json.loads(response.strip())
    except Exception as e:
        return {"error": str(e)}

print("Testing potential MCP commands...")
print("=" * 60)

# Try various command names
commands = [
    "help",
    "list",
    "GetCommands",
    "ListCommands",
    "GetTools",
    "spawn",
    "SpawnActor",
    "spawn_actor",
    "screenshot",
    "TakeScreenshot",
    "take_screenshot",
    "GetActors",
    "get_actors",
    "version",
    "GetVersion",
    "get_version",
    "ping",
    "echo",
    "status",
    "info"
]

found_commands = []

for cmd in commands:
    result = send_command(cmd)
    status = result.get("status", "timeout")
    
    if status != "error" or "Unknown command" not in result.get("error", ""):
        print(f"[FOUND] '{cmd}': {status}")
        found_commands.append(cmd)
        print(f"  Response: {result}")
    else:
        print(f"[INVALID] '{cmd}'")

print("\n" + "=" * 60)
if found_commands:
    print(f"Found {len(found_commands)} valid commands:")
    for cmd in found_commands:
        print(f"  -> {cmd}")
else:
    print("No valid commands found with simple names.")
    print("The MCP plugin may use different command naming.")