#!/usr/bin/env python3
"""Test different MCP command formats to find what works"""

import socket
import json
import time

def test_format(description, message, host='127.0.0.1', port=55557):
    """Test a specific message format"""
    print(f"\n[TEST] {description}")
    print(f"  Sending: {message}")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, port))
        
        # Send message
        if isinstance(message, dict):
            msg = json.dumps(message)
        else:
            msg = message
            
        if not msg.endswith('\n'):
            msg += '\n'
            
        s.send(msg.encode('utf-8'))
        
        # Try to receive response
        try:
            response = s.recv(4096).decode('utf-8')
            print(f"  Response: {response[:200]}")
            return True
        except socket.timeout:
            print("  Response: TIMEOUT")
            return False
        finally:
            s.close()
            
    except Exception as e:
        print(f"  Error: {e}")
        return False

print("Testing different MCP command formats...")
print("=" * 60)

# Test 1: Format from smoke_bridge.py
test_format(
    "Format 1: command + params (smoke_bridge style)",
    {"command": "health", "params": {}}
)

time.sleep(0.5)

# Test 2: Format with type field
test_format(
    "Format 2: type + params (as Unreal expects 'type')",
    {"type": "health", "params": {}}
)

time.sleep(0.5)

# Test 3: Simple command string
test_format(
    "Format 3: Plain command string",
    "health"
)

time.sleep(0.5)

# Test 4: Execute wrapper
test_format(
    "Format 4: execute command wrapper",
    {"type": "execute", "command": "health", "params": {}}
)

time.sleep(0.5)

# Test 5: Direct console command
test_format(
    "Format 5: Console command format",
    {"type": "console", "command": "stat fps"}
)

time.sleep(0.5)

# Test 6: GetVersion command
test_format(
    "Format 6: GetVersion (different command)",
    {"command": "GetVersion", "params": {}}
)

print("\n" + "=" * 60)
print("Test complete. Check which formats got responses.")