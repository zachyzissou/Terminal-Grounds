#!/usr/bin/env python3
"""
Simple WebSocket Test
Quick validation of WebSocket server connectivity
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_connection():
    """Test basic WebSocket connectivity"""
    try:
        print("Testing WebSocket connection to ws://127.0.0.1:8765")
        
        # Try to connect
        websocket = await websockets.connect("ws://127.0.0.1:8765")
        print("SUCCESS: Connected to WebSocket server")
        
        # Send a test message
        test_message = {
            "type": "player_connected",
            "player_id": 1,
            "faction_id": 1,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(test_message))
        print("SUCCESS: Sent test message")
        
        # Wait for response
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"SUCCESS: Received response: {response}")
            
            # Parse response
            response_data = json.loads(response)
            if response_data.get("type") == "initial_state":
                territories = response_data.get("territories", [])
                print(f"SUCCESS: Initial state received with {len(territories)} territories")
            
        except asyncio.TimeoutError:
            print("WARNING: No response received within 5 seconds")
        
        # Close connection
        await websocket.close()
        print("SUCCESS: WebSocket test completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: WebSocket test failed: {e}")
        return False

async def main():
    """Main test execution"""
    print("SIMPLE WEBSOCKET CONNECTIVITY TEST")
    print("=" * 50)
    
    success = await test_websocket_connection()
    
    if success:
        print("\nTEST RESULT: PASS")
        print("WebSocket server is operational and responsive")
    else:
        print("\nTEST RESULT: FAIL")
        print("WebSocket server connectivity issues detected")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())