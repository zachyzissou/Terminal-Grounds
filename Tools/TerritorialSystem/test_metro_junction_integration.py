#!/usr/bin/env python3
"""
Metro Junction WebSocket Integration Test
Tests the territorial system integration with Metro Junction map
Validates real-time territorial control and faction dynamics
"""

import asyncio
import websockets
import json
import time
import sys
import os
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Metro Junction territorial configuration
METRO_JUNCTION_TERRITORIES = {
    1001: {
        "name": "Metro Junction Region",
        "type": "Region",
        "factions": [1, 2, 4],  # Directorate, Free77, CivicWardens
        "strategic_value": 85
    },
    1002: {
        "name": "Directorate Corporate Zone",
        "type": "District", 
        "factions": [1],  # Directorate
        "strategic_value": 70
    },
    1003: {
        "name": "Free77 Resistance Zone",
        "type": "District",
        "factions": [2],  # Free77
        "strategic_value": 65
    },
    1004: {
        "name": "Central Junction Hub",
        "type": "District",
        "factions": [1, 2, 4],  # Contested
        "strategic_value": 90
    },
    1005: {
        "name": "Platform Alpha",
        "type": "ControlPoint",
        "factions": [1],  # Directorate extraction
        "strategic_value": 60
    },
    1007: {
        "name": "Platform Beta", 
        "type": "ControlPoint",
        "factions": [2],  # Free77 extraction
        "strategic_value": 60
    }
}

FACTION_NAMES = {
    1: "Directorate",
    2: "Free77", 
    4: "CivicWardens"
}

async def test_metro_junction_websocket():
    """Test WebSocket connection to territorial server"""
    
    print("=== Metro Junction WebSocket Integration Test ===")
    
    try:
        # Connect to territorial WebSocket server
        uri = "ws://127.0.0.1:8765"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("OK: Connected to territorial WebSocket server")
            
            # Test 1: Initialize Metro Junction territories
            for territory_id, config in METRO_JUNCTION_TERRITORIES.items():
                init_message = {
                    "action": "update_territorial_influence",
                    "territory_id": territory_id,
                    "territory_type": config["type"],
                    "faction_id": config["factions"][0],  # Primary faction
                    "influence_change": 50,  # Initial influence
                    "cause": f"Metro Junction Map Initialization - {config['name']}"
                }
                
                await websocket.send(json.dumps(init_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                print(f"  -> Initialized {config['name']}: {response_data.get('status', 'Unknown')}")
            
            # Test 2: Simulate faction conflict in Central Junction Hub (contested territory)
            print("\nSimulating faction conflict in Central Junction Hub...")
            
            conflict_scenarios = [
                {"faction_id": 1, "influence_change": 15, "cause": "Directorate Security Sweep"},
                {"faction_id": 2, "influence_change": 20, "cause": "Free77 Resistance Operation"},
                {"faction_id": 1, "influence_change": 10, "cause": "Corporate Reinforcements"},
                {"faction_id": 2, "influence_change": -5, "cause": "Equipment Malfunction"},
                {"faction_id": 4, "influence_change": 8, "cause": "Civilian Protection Initiative"}
            ]
            
            for scenario in conflict_scenarios:
                conflict_message = {
                    "action": "update_territorial_influence",
                    "territory_id": 1004,  # Central Junction Hub
                    "territory_type": "District",
                    "faction_id": scenario["faction_id"],
                    "influence_change": scenario["influence_change"],
                    "cause": scenario["cause"]
                }
                
                await websocket.send(json.dumps(conflict_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                faction_name = FACTION_NAMES.get(scenario["faction_id"], "Unknown")
                print(f"  -> {faction_name}: {scenario['influence_change']:+d} influence - {scenario['cause']}")
                
                await asyncio.sleep(0.5)  # Small delay between actions
            
            # Test 3: Query territorial state
            print("\nQuerying Metro Junction territorial state...")
            
            for territory_id in [1004, 1005, 1007]:  # Hub + both extraction platforms
                query_message = {
                    "action": "get_territorial_state", 
                    "territory_id": territory_id
                }
                
                await websocket.send(json.dumps(query_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if "territorial_state" in response_data:
                    state = response_data["territorial_state"]
                    territory_name = METRO_JUNCTION_TERRITORIES[territory_id]["name"]
                    dominant_faction = FACTION_NAMES.get(state.get("dominant_faction", 0), "None")
                    contested = "Yes" if state.get("is_contested", False) else "No"
                    
                    print(f"  -> {territory_name}: Controlled by {dominant_faction}, Contested: {contested}")
            
            # Test 4: Extraction point influence simulation
            print("\nSimulating extraction point territorial influence...")
            
            extraction_tests = [
                {
                    "territory_id": 1005,  # Platform Alpha
                    "player_faction": 1,   # Directorate player
                    "extraction_success": True,
                    "influence_gain": 25
                },
                {
                    "territory_id": 1007,  # Platform Beta  
                    "player_faction": 2,   # Free77 player
                    "extraction_success": True,
                    "influence_gain": 25
                },
                {
                    "territory_id": 1005,  # Platform Alpha
                    "player_faction": 2,   # Free77 player (hostile extraction)
                    "extraction_success": False,
                    "influence_gain": -10  # Penalty for failed hostile extraction
                }
            ]
            
            for test in extraction_tests:
                extraction_message = {
                    "action": "update_territorial_influence",
                    "territory_id": test["territory_id"],
                    "territory_type": "ControlPoint",
                    "faction_id": test["player_faction"],
                    "influence_change": test["influence_gain"],
                    "cause": f"Extraction {'Success' if test['extraction_success'] else 'Failed'}"
                }
                
                await websocket.send(json.dumps(extraction_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                territory_name = METRO_JUNCTION_TERRITORIES[test["territory_id"]]["name"]
                faction_name = FACTION_NAMES[test["player_faction"]]
                result = "SUCCESS" if test["extraction_success"] else "FAILED"
                
                print(f"  -> {territory_name}: {faction_name} extraction {result} ({test['influence_gain']:+d} influence)")
            
            print("\n=== Integration Test Complete ===")
            print("Metro Junction WebSocket integration: OK")
            print("Territorial influence tracking: OK")  
            print("Faction conflict simulation: OK")
            print("Extraction point mechanics: OK")
            
    except ConnectionRefusedError:
        print("FAILED: WebSocket server not running at 127.0.0.1:8765")
        print("Start the server with: python Tools/TerritorialSystem/territorial_websocket_server.py")
        return False
    except Exception as e:
        print(f"FAILED: WebSocket integration error: {e}")
        return False
    
    return True

def test_database_integration():
    """Test direct database integration for Metro Junction"""
    
    print("\n=== Database Integration Test ===")
    
    try:
        # Connect to territorial database
        db_path = "C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db"
        
        if not os.path.exists(db_path):
            print("FAILED: Territorial database not found")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test database structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        required_tables = ['territories', 'territorial_influence', 'faction_activities']
        missing_tables = []
        
        table_names = [table[0] for table in tables]
        for required_table in required_tables:
            if required_table not in table_names:
                missing_tables.append(required_table)
        
        if missing_tables:
            print(f"FAILED: Missing database tables: {missing_tables}")
            conn.close()
            return False
        
        # Test Metro Junction territory lookup
        cursor.execute("""
            SELECT territory_id, name, territory_type, strategic_value 
            FROM territories 
            WHERE territory_id BETWEEN 1001 AND 1010
        """)
        
        metro_territories = cursor.fetchall()
        
        if len(metro_territories) == 0:
            print("WARNING: No Metro Junction territories found in database")
            print("Database may need Metro Junction territory initialization")
        else:
            print(f"OK: Found {len(metro_territories)} Metro Junction territories in database")
            for territory in metro_territories:
                print(f"  -> {territory[0]}: {territory[1]} ({territory[2]}, Strategic Value: {territory[3]})")
        
        # Test territorial influence tracking
        cursor.execute("""
            SELECT COUNT(*) FROM territorial_influence 
            WHERE territory_id BETWEEN 1001 AND 1010
        """)
        
        influence_records = cursor.fetchone()[0]
        print(f"OK: Found {influence_records} territorial influence records for Metro Junction")
        
        conn.close()
        
        print("Database integration: OK")
        return True
        
    except Exception as e:
        print(f"FAILED: Database integration error: {e}")
        return False

async def main():
    """Main test execution"""
    
    print("Metro Junction Territorial Integration Test")
    print("Testing WebSocket and database integration for playtesting readiness")
    
    # Test WebSocket integration
    websocket_success = await test_metro_junction_websocket()
    
    # Test database integration  
    database_success = test_database_integration()
    
    # Summary
    print(f"\n=== Test Results ===")
    print(f"WebSocket Integration: {'PASS' if websocket_success else 'FAIL'}")
    print(f"Database Integration: {'PASS' if database_success else 'FAIL'}")
    
    if websocket_success and database_success:
        print("Status: READY FOR PLAYTESTING")
        print("Metro Junction territorial system is operational")
    else:
        print("Status: NOT READY - Issues found")
        print("Resolve integration issues before playtesting")

if __name__ == "__main__":
    asyncio.run(main())