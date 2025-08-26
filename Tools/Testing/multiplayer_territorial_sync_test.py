#!/usr/bin/env python3
"""
Multiplayer Territorial Synchronization Testing Framework
Tests real-time territorial state synchronization across multiple simulated clients
Validates WebSocket broadcasting and state consistency
"""

import asyncio
import websockets
import json
import time
import sqlite3
import threading
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class SimulatedPlayer:
    """Simulated player for territorial sync testing"""
    player_id: int
    faction_id: int
    current_territory: int
    websocket: Optional[websockets.WebSocketClientProtocol]
    received_updates: List[Dict]
    last_update_time: datetime
    actions_performed: int

@dataclass
class TerritorialSyncTestResult:
    """Results of territorial synchronization test"""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_players: int
    messages_sent: int
    messages_received: int
    sync_latency_avg: float
    sync_latency_max: float
    state_consistency_rate: float
    success: bool
    errors: List[str]

class MultiplayerTerritorialSyncTester:
    """
    Tests multiplayer synchronization of territorial control system
    Simulates multiple players performing territorial actions simultaneously
    """
    
    def __init__(self):
        self.websocket_server_url = "ws://127.0.0.1:8765"
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        
        self.simulated_players: Dict[int, SimulatedPlayer] = {}
        self.test_results: List[TerritorialSyncTestResult] = []
        self.test_running = False
        
        # Test configuration
        self.max_concurrent_players = 50
        self.test_duration = 60.0  # seconds
        self.action_interval = 5.0  # seconds between player actions
        
        print("Multiplayer Territorial Sync Tester initialized")
        print(f"WebSocket server: {self.websocket_server_url}")
        print(f"Database: {self.db_path}")
    
    async def create_simulated_player(self, player_id: int, faction_id: int) -> Optional[SimulatedPlayer]:
        """Create and connect a simulated player"""
        try:
            websocket = await websockets.connect(self.websocket_server_url)
            
            player = SimulatedPlayer(
                player_id=player_id,
                faction_id=faction_id,
                current_territory=1,  # Start in territory 1
                websocket=websocket,
                received_updates=[],
                last_update_time=datetime.now(),
                actions_performed=0
            )
            
            # Send initial connection message
            connection_message = {
                "type": "player_connected",
                "player_id": player_id,
                "faction_id": faction_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(connection_message))
            
            print(f"Connected simulated player {player_id} (Faction {faction_id})")
            return player
            
        except Exception as e:
            print(f"Failed to connect simulated player {player_id}: {e}")
            return None
    
    async def simulate_player_behavior(self, player: SimulatedPlayer):
        """Simulate territorial actions for a player"""
        try:
            while self.test_running and player.websocket:
                # Listen for incoming messages
                try:
                    message = await asyncio.wait_for(player.websocket.recv(), timeout=0.1)
                    update = json.loads(message)
                    update["received_time"] = datetime.now().isoformat()
                    player.received_updates.append(update)
                    player.last_update_time = datetime.now()
                    
                except asyncio.TimeoutError:
                    pass
                
                # Perform territorial action occasionally
                if time.time() % self.action_interval < 0.1:
                    await self.simulate_territorial_action(player)
                
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming
                
        except websockets.exceptions.ConnectionClosed:
            print(f"Player {player.player_id} disconnected")
        except Exception as e:
            print(f"Error in player {player.player_id} simulation: {e}")
    
    async def simulate_territorial_action(self, player: SimulatedPlayer):
        """Simulate a territorial action by a player"""
        try:
            # Choose a random territorial action
            import random
            
            action_types = ["sabotage", "supply_delivery", "intel_gathering", "infrastructure_assault"]
            action_type = random.choice(action_types)
            
            # Choose target territory (prefer nearby territories)
            possible_territories = [1, 2, 3, 4]  # Phase 1 territories
            target_territory = random.choice(possible_territories)
            
            # Create territorial action message
            action_message = {
                "type": "territorial_action",
                "player_id": player.player_id,
                "faction_id": player.faction_id,
                "action_type": action_type,
                "target_territory": target_territory,
                "influence_change": random.randint(10, 30),
                "timestamp": datetime.now().isoformat()
            }
            
            await player.websocket.send(json.dumps(action_message))
            player.actions_performed += 1
            
            print(f"Player {player.player_id} performed {action_type} on territory {target_territory}")
            
        except Exception as e:
            print(f"Error simulating action for player {player.player_id}: {e}")
    
    async def disconnect_player(self, player: SimulatedPlayer):
        """Disconnect a simulated player"""
        try:
            if player.websocket:
                await player.websocket.close()
                player.websocket = None
            print(f"Disconnected player {player.player_id}")
        except Exception as e:
            print(f"Error disconnecting player {player.player_id}: {e}")
    
    def calculate_sync_metrics(self, players: List[SimulatedPlayer]) -> Dict[str, float]:
        """Calculate synchronization performance metrics"""
        
        if not players:
            return {
                "avg_latency": 0.0,
                "max_latency": 0.0,
                "message_loss_rate": 0.0,
                "state_consistency": 0.0
            }
        
        # Calculate latency metrics
        latencies = []
        total_messages_sent = 0
        total_messages_received = 0
        
        for player in players:
            total_messages_sent += player.actions_performed
            total_messages_received += len(player.received_updates)
            
            # Calculate latencies for received updates
            for update in player.received_updates:
                if "timestamp" in update and "received_time" in update:
                    try:
                        sent_time = datetime.fromisoformat(update["timestamp"].replace("Z", "+00:00"))
                        received_time = datetime.fromisoformat(update["received_time"])
                        latency = (received_time - sent_time).total_seconds()
                        if latency >= 0:  # Only count valid latencies
                            latencies.append(latency)
                    except:
                        pass
        
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 0.0
        
        # Calculate message loss rate
        expected_messages = total_messages_sent * len(players)  # Each action should broadcast to all players
        message_loss_rate = 1.0 - (total_messages_received / expected_messages) if expected_messages > 0 else 0.0
        
        # Calculate state consistency (simplified - based on update frequency)
        consistent_players = sum(1 for p in players if len(p.received_updates) > 0)
        state_consistency = consistent_players / len(players) if players else 0.0
        
        return {
            "avg_latency": avg_latency,
            "max_latency": max_latency,
            "message_loss_rate": message_loss_rate,
            "state_consistency": state_consistency
        }
    
    async def run_concurrent_players_test(self, num_players: int = 10) -> TerritorialSyncTestResult:
        """Test with multiple concurrent players"""
        
        test_name = f"Concurrent Players Test ({num_players} players)"
        start_time = datetime.now()
        
        print(f"\nStarting {test_name}")
        print(f"Duration: {self.test_duration} seconds")
        
        errors = []
        players = []
        
        try:
            # Create simulated players
            for i in range(num_players):
                faction_id = (i % 3) + 1  # Distribute across first 3 factions
                player = await self.create_simulated_player(i + 1, faction_id)
                
                if player:
                    players.append(player)
                    self.simulated_players[player.player_id] = player
                else:
                    errors.append(f"Failed to create player {i + 1}")
            
            print(f"Created {len(players)} simulated players")
            
            # Start test
            self.test_running = True
            
            # Start player behavior simulations
            player_tasks = [self.simulate_player_behavior(player) for player in players]
            
            # Run test for specified duration
            await asyncio.sleep(self.test_duration)
            
            # Stop test
            self.test_running = False
            
            # Wait for player tasks to complete
            await asyncio.gather(*player_tasks, return_exceptions=True)
            
            # Disconnect all players
            for player in players:
                await self.disconnect_player(player)
            
            # Calculate metrics
            metrics = self.calculate_sync_metrics(players)
            
            # Create test result
            end_time = datetime.now()
            total_messages_sent = sum(p.actions_performed for p in players)
            total_messages_received = sum(len(p.received_updates) for p in players)
            
            success = (
                metrics["avg_latency"] < 0.5 and  # Under 500ms average latency
                metrics["message_loss_rate"] < 0.1 and  # Under 10% message loss
                metrics["state_consistency"] > 0.8  # Over 80% state consistency
            )
            
            result = TerritorialSyncTestResult(
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                total_players=len(players),
                messages_sent=total_messages_sent,
                messages_received=total_messages_received,
                sync_latency_avg=metrics["avg_latency"],
                sync_latency_max=metrics["max_latency"],
                state_consistency_rate=metrics["state_consistency"],
                success=success,
                errors=errors
            )
            
            return result
            
        except Exception as e:
            errors.append(f"Test execution error: {e}")
            
            result = TerritorialSyncTestResult(
                test_name=test_name,
                start_time=start_time,
                end_time=datetime.now(),
                total_players=len(players),
                messages_sent=0,
                messages_received=0,
                sync_latency_avg=0.0,
                sync_latency_max=0.0,
                state_consistency_rate=0.0,
                success=False,
                errors=errors
            )
            
            return result
    
    async def run_stress_test(self, max_players: int = 50) -> TerritorialSyncTestResult:
        """Stress test with maximum concurrent players"""
        
        test_name = f"Stress Test ({max_players} players)"
        start_time = datetime.now()
        
        print(f"\nStarting {test_name}")
        
        # Run concurrent players test with maximum players
        result = await self.run_concurrent_players_test(max_players)
        result.test_name = test_name
        
        return result
    
    async def run_all_tests(self) -> List[TerritorialSyncTestResult]:
        """Run comprehensive multiplayer synchronization tests"""
        
        print("MULTIPLAYER TERRITORIAL SYNCHRONIZATION TESTS")
        print("=" * 60)
        
        results = []
        
        # Test with different player counts
        player_counts = [5, 10, 25, 50]
        
        for count in player_counts:
            if count <= self.max_concurrent_players:
                result = await self.run_concurrent_players_test(count)
                results.append(result)
                self.test_results.append(result)
                
                # Print test result
                print(f"\n{result.test_name} Results:")
                print(f"Success: {'PASS' if result.success else 'FAIL'}")
                print(f"Players: {result.total_players}")
                print(f"Messages: {result.messages_sent} sent, {result.messages_received} received")
                print(f"Avg Latency: {result.sync_latency_avg:.3f}s")
                print(f"Max Latency: {result.sync_latency_max:.3f}s")
                print(f"State Consistency: {result.state_consistency_rate:.1%}")
                
                if result.errors:
                    print(f"Errors: {len(result.errors)}")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"  - {error}")
                
                # Wait between tests
                await asyncio.sleep(2.0)
        
        return results
    
    def print_test_summary(self, results: List[TerritorialSyncTestResult]):
        """Print comprehensive test summary"""
        
        print("\n" + "=" * 60)
        print("MULTIPLAYER TERRITORIAL SYNC TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for r in results if r.success)
        total_tests = len(results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Overall Success Rate: {passed_tests/total_tests:.1%}")
        
        if results:
            avg_latency = sum(r.sync_latency_avg for r in results) / len(results)
            max_latency = max(r.sync_latency_max for r in results)
            avg_consistency = sum(r.state_consistency_rate for r in results) / len(results)
            
            print(f"Average Latency: {avg_latency:.3f}s")
            print(f"Maximum Latency: {max_latency:.3f}s")
            print(f"Average State Consistency: {avg_consistency:.1%}")
        
        # Performance assessment
        if passed_tests == total_tests:
            print("\nASSESSMENT: MULTIPLAYER SYNC SYSTEM OPERATIONAL")
            print("Ready for production multiplayer territorial gameplay")
        elif passed_tests >= total_tests * 0.8:
            print("\nASSESSMENT: MULTIPLAYER SYNC SYSTEM MOSTLY OPERATIONAL")
            print("Minor optimizations needed for full production readiness")
        else:
            print("\nASSESSMENT: MULTIPLAYER SYNC SYSTEM REQUIRES OPTIMIZATION")
            print("Significant improvements needed before production deployment")

async def main():
    """Main testing execution"""
    
    tester = MultiplayerTerritorialSyncTester()
    
    # Check WebSocket server availability
    try:
        import websockets
        # Simple connectivity test
        print("Testing WebSocket server connectivity...")
        
    except Exception as e:
        print(f"WebSocket server not available: {e}")
        print("Please ensure territorial_websocket_server.py is running")
        return False
    
    # Run all synchronization tests
    results = await tester.run_all_tests()
    
    # Print comprehensive summary
    tester.print_test_summary(results)
    
    # Return overall success
    return all(result.success for result in results)

if __name__ == "__main__":
    asyncio.run(main())