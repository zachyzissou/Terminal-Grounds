#!/usr/bin/env python3
"""
Terminal Grounds Territorial WebSocket Server
CTO Phase 1 Implementation - Real-time Territorial Updates

Provides real-time territorial state synchronization for 100+ concurrent players
Integrates with SQLite territorial database and broadcasts updates via WebSocket
"""

import asyncio
import websockets
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerritorialWebSocket")

@dataclass
class TerritorialUpdate:
    """Territorial update message structure"""
    type: str  # "territory_control_changed", "influence_updated", "territory_contested"
    territory_id: int
    territory_name: str
    controller_faction_id: Optional[int]
    controller_name: Optional[str]
    contested: bool
    timestamp: str
    influence_changes: List[Dict[str, Any]]
    strategic_value: int

class TerritorialWebSocketServer:
    """
    WebSocket server for real-time territorial updates
    Handles 100+ concurrent connections with efficient broadcasting
    """
    
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        self.server = None
        self.running = False
        self.update_thread = None
        
        # Performance monitoring
        self.message_count = 0
        self.client_count = 0
        self.start_time = time.time()
        
        logger.info("Territorial WebSocket Server initialized")
        logger.info(f"Database: {self.db_path}")
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register new client connection"""
        self.clients.add(websocket)
        self.client_count = len(self.clients)
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_info} (Total: {self.client_count})")
        
        # Send initial territorial state to new client
        await self.send_initial_state(websocket)
        
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister client connection"""
        self.clients.discard(websocket)
        self.client_count = len(self.clients)
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client disconnected: {client_info} (Total: {self.client_count})")
        
    async def send_initial_state(self, websocket: websockets.WebSocketServerProtocol):
        """Send current territorial state to newly connected client"""
        try:
            territorial_state = self.get_territorial_state()
            
            message = {
                "type": "initial_state",
                "territories": territorial_state,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(message))
            logger.info(f"Sent initial state to client: {len(territorial_state)} territories")
            
        except Exception as e:
            logger.error(f"Error sending initial state: {e}")
            
    def get_territorial_state(self) -> List[Dict[str, Any]]:
        """Get current territorial state from database"""
        try:
            connection = sqlite3.connect(str(self.db_path))
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM territorial_control_summary")
            territories = [dict(row) for row in cursor.fetchall()]
            
            connection.close()
            return territories
            
        except Exception as e:
            logger.error(f"Error getting territorial state: {e}")
            return []
            
    async def broadcast_update(self, update: TerritorialUpdate):
        """Broadcast territorial update to all connected clients"""
        if not self.clients:
            return
            
        message = json.dumps(asdict(update))
        
        # Send to all clients concurrently
        disconnected_clients = set()
        
        async def send_to_client(client):
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        # Send to all clients in parallel
        await asyncio.gather(
            *[send_to_client(client) for client in self.clients],
            return_exceptions=True
        )
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.discard(client)
            
        self.message_count += len(self.clients)
        self.client_count = len(self.clients)
        
        logger.info(f"Broadcasted update to {len(self.clients)} clients: {update.type}")
        
    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await websocket.send(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
                
            elif message_type == "request_update":
                # Client requesting specific territorial update
                territory_id = data.get("territory_id")
                if territory_id:
                    await self.send_territory_update(websocket, territory_id)
                    
            elif message_type == "influence_action":
                # Client reporting influence change action
                await self.process_influence_action(data)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            
    async def send_territory_update(self, websocket: websockets.WebSocketServerProtocol, territory_id: int):
        """Send specific territory update to client"""
        try:
            connection = sqlite3.connect(str(self.db_path))
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM territorial_control_summary WHERE territory_id = ?", (territory_id,))
            territory = cursor.fetchone()
            
            if territory:
                message = {
                    "type": "territory_update", 
                    "territory": dict(territory),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(message))
                
            connection.close()
            
        except Exception as e:
            logger.error(f"Error sending territory update: {e}")
            
    async def process_influence_action(self, data: Dict[str, Any]):
        """Process influence action and broadcast if significant"""
        try:
            territory_id = data.get("territory_id")
            faction_id = data.get("faction_id")
            influence_change = data.get("influence_change", 0)
            
            if not all([territory_id, faction_id]):
                return
                
            # Update database
            connection = sqlite3.connect(str(self.db_path))
            cursor = connection.cursor()
            
            # Update faction influence
            cursor.execute("""
                UPDATE faction_territorial_influence 
                SET influence_level = MAX(0, MIN(100, influence_level + ?)),
                    last_action_at = CURRENT_TIMESTAMP
                WHERE territory_id = ? AND faction_id = ?
            """, (influence_change, territory_id, faction_id))
            
            # Check if control changed
            cursor.execute("""
                SELECT territory_name, current_controller_faction_id 
                FROM territories WHERE id = ?
            """, (territory_id,))
            territory_info = cursor.fetchone()
            
            if territory_info:
                territory_name, old_controller = territory_info
                
                # Get highest influence faction
                cursor.execute("""
                    SELECT faction_id, influence_level FROM faction_territorial_influence 
                    WHERE territory_id = ? ORDER BY influence_level DESC LIMIT 1
                """, (territory_id,))
                
                top_influence = cursor.fetchone()
                if top_influence and top_influence[1] > 50:  # Control threshold
                    new_controller = top_influence[0]
                    
                    if new_controller != old_controller:
                        # Control changed - update database
                        cursor.execute("""
                            UPDATE territories SET current_controller_faction_id = ? 
                            WHERE id = ?
                        """, (new_controller, territory_id))
                        
                        # Get faction name
                        cursor.execute("SELECT faction_name FROM factions WHERE id = ?", (new_controller,))
                        faction_result = cursor.fetchone()
                        controller_name = faction_result[0] if faction_result else "Unknown"
                        
                        # Create and broadcast update
                        update = TerritorialUpdate(
                            type="territory_control_changed",
                            territory_id=territory_id,
                            territory_name=territory_name,
                            controller_faction_id=new_controller,
                            controller_name=controller_name,
                            contested=False,
                            timestamp=datetime.now().isoformat(),
                            influence_changes=[{
                                "faction_id": faction_id,
                                "new_influence": top_influence[1]
                            }],
                            strategic_value=data.get("strategic_value", 1)
                        )
                        
                        await self.broadcast_update(update)
                        
            connection.commit()
            connection.close()
            
        except Exception as e:
            logger.error(f"Error processing influence action: {e}")
            
    async def client_handler(self, websocket):
        """Handle individual client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            await self.unregister_client(websocket)
            
    def database_change_monitor(self):
        """Monitor database for changes and trigger updates"""
        logger.info("Database change monitor started")
        
        last_update_time = time.time()
        
        while self.running:
            try:
                # Check for recent territorial events
                connection = sqlite3.connect(str(self.db_path))
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                
                # Check for events in last 5 seconds
                cursor.execute("""
                    SELECT te.*, t.territory_name, f.faction_name
                    FROM territorial_events te
                    JOIN territories t ON te.territory_id = t.id
                    LEFT JOIN factions f ON te.initiating_faction_id = f.id
                    WHERE te.started_at > datetime('now', '-5 seconds')
                """)
                
                recent_events = cursor.fetchall()
                
                for event in recent_events:
                    # Create update for each recent event
                    update = TerritorialUpdate(
                        type=f"territorial_{event['event_type']}",
                        territory_id=event["territory_id"],
                        territory_name=event["territory_name"],
                        controller_faction_id=event.get("initiating_faction_id"),
                        controller_name=event.get("faction_name"),
                        contested=event["event_type"] == "contest",
                        timestamp=event["started_at"],
                        influence_changes=[],
                        strategic_value=1
                    )
                    
                    # Schedule broadcast
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_update(update),
                        asyncio.get_event_loop()
                    )
                
                connection.close()
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in database monitor: {e}")
                time.sleep(5)
                
    async def start_server(self, host="127.0.0.1", port=8765):
        """Start the WebSocket server"""
        logger.info(f"Starting Territorial WebSocket Server on {host}:{port}")
        
        self.running = True
        
        # Start database monitoring thread
        self.update_thread = threading.Thread(target=self.database_change_monitor)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Start WebSocket server
        self.server = await websockets.serve(
            self.client_handler,
            host,
            port,
            ping_interval=30,
            ping_timeout=10,
            max_size=1024*1024  # 1MB max message size
        )
        
        logger.info("Territorial WebSocket Server started successfully")
        logger.info("Monitoring territorial database for real-time updates")
        
        # Keep server running
        await self.server.wait_closed()
        
    def stop_server(self):
        """Stop the WebSocket server"""
        logger.info("Stopping Territorial WebSocket Server")
        self.running = False
        
        if self.server:
            self.server.close()
            
        # Print statistics
        uptime = time.time() - self.start_time
        logger.info(f"Server Statistics:")
        logger.info(f"  Uptime: {uptime:.1f} seconds")
        logger.info(f"  Messages sent: {self.message_count}")
        logger.info(f"  Peak concurrent clients: {self.client_count}")
        logger.info(f"  Messages per second: {self.message_count / uptime:.1f}")

async def main():
    """Main entry point"""
    server = TerritorialWebSocketServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.stop_server()

if __name__ == "__main__":
    print("TERRITORIAL WEBSOCKET SERVER - CTO Phase 1 Implementation")
    print("Real-time territorial updates for 100+ concurrent players")
    print("Press Ctrl+C to stop server")
    print()
    
    asyncio.run(main())