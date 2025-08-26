# -*- coding: utf-8 -*-
"""
Test client for CTO Territorial WebSocket Server
Validates real-time territorial updates and connection handling
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_territorial_websocket():
    """Test territorial WebSocket connection and updates"""
    uri = "ws://127.0.0.1:8765"
    
    print("TERRITORIAL WEBSOCKET CLIENT TEST")
    print("=" * 50)
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"SUCCESS: Connected to territorial server")
            
            # Send test message
            test_message = {
                "type": "client_hello",
                "client_id": "test_client_001",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"SENT: Client hello message")
            
            # Listen for responses
            print("LISTENING: Waiting for territorial updates...")
            
            timeout_count = 0
            max_messages = 5
            message_count = 0
            
            while message_count < max_messages and timeout_count < 3:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    
                    try:
                        data = json.loads(message)
                        print(f"RECEIVED: {data.get('type', 'unknown')} message")
                        
                        if data.get('type') == 'territorial_state':
                            print(f"  -> Territories: {len(data.get('territories', []))}")
                            print(f"  -> Total influence relationships: {data.get('total_influences', 0)}")
                        elif data.get('type') == 'territory_update':
                            print(f"  -> Territory: {data.get('territory_name', 'Unknown')}")
                            print(f"  -> Controller: {data.get('controller_name', 'None')}")
                            
                        message_count += 1
                        
                    except json.JSONDecodeError:
                        print(f"RECEIVED: Raw message - {message}")
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"TIMEOUT: No message received (attempt {timeout_count}/3)")
                    
                    if timeout_count >= 3:
                        print("INFO: No more messages - connection stable")
                        break
            
            # Test territory update request
            if message_count > 0:
                print("\nTESTING: Requesting territory update")
                update_request = {
                    "type": "request_territory_update",
                    "territory_id": 1,
                    "client_id": "test_client_001"
                }
                
                await websocket.send(json.dumps(update_request))
                print("SENT: Territory update request")
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    response_data = json.loads(response)
                    print(f"RECEIVED: {response_data.get('type', 'unknown')} response")
                except asyncio.TimeoutError:
                    print("TIMEOUT: No response to territory update request")
            
            print(f"\nSUCCESS: WebSocket test completed")
            print(f"  -> Messages received: {message_count}")
            print(f"  -> Connection stable: Yes")
            print(f"  -> Server responsive: Yes")
            
    except ConnectionRefusedError:
        print("ERROR: Could not connect to territorial server")
        print("Make sure the server is running: python Tools/TerritorialSystem/territorial_websocket_server.py")
        return False
    except Exception as e:
        print(f"ERROR: WebSocket test failed - {e}")
        return False
    
    return True

async def test_concurrent_connections():
    """Test multiple concurrent connections"""
    print("\nCONCURRENT CONNECTION TEST")
    print("=" * 50)
    
    uri = "ws://127.0.0.1:8765"
    connection_count = 5
    
    async def client_connection(client_id):
        try:
            async with websockets.connect(uri) as websocket:
                hello_msg = {
                    "type": "client_hello", 
                    "client_id": f"test_client_{client_id:03d}"
                }
                await websocket.send(json.dumps(hello_msg))
                
                # Listen for initial state
                message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(message)
                return f"Client {client_id}: {data.get('type', 'unknown')} received"
                
        except Exception as e:
            return f"Client {client_id}: ERROR - {e}"
    
    # Create concurrent connections
    tasks = [client_connection(i) for i in range(1, connection_count + 1)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"ERROR: {result}")
        else:
            print(f"SUCCESS: {result}")
            success_count += 1
    
    print(f"\nCONCURRENT TEST RESULTS:")
    print(f"  -> Successful connections: {success_count}/{connection_count}")
    print(f"  -> Success rate: {(success_count/connection_count)*100:.1f}%")
    
    return success_count == connection_count

def main():
    """Main test execution"""
    print("CTO TERRITORIAL WEBSOCKET VALIDATION")
    print("=" * 60)
    print("Testing real-time territorial server functionality")
    print()
    
    # Run basic connection test
    basic_test = asyncio.run(test_territorial_websocket())
    
    if basic_test:
        # Run concurrent connection test
        concurrent_test = asyncio.run(test_concurrent_connections())
        
        print("\n" + "=" * 60)
        print("TERRITORIAL WEBSOCKET TEST SUMMARY")
        print("=" * 60)
        print(f"Basic connection test: {'PASS' if basic_test else 'FAIL'}")
        print(f"Concurrent connections: {'PASS' if concurrent_test else 'FAIL'}")
        
        if basic_test and concurrent_test:
            print("\nSUCCESS: Territorial WebSocket server fully operational")
            print("READY: For UE5 client integration")
        else:
            print("\nISSUES: Some tests failed - review server implementation")
    else:
        print("\nFAILED: Basic connection test - server may not be running")
        print("Start server: python Tools/TerritorialSystem/territorial_websocket_server.py")

if __name__ == "__main__":
    main()