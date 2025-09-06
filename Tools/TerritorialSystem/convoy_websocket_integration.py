#!/usr/bin/env python3
"""
Terminal Grounds Convoy WebSocket Integration
Performance Engineer Implementation - Real-time Convoy Route Updates

Integrates with existing territorial_websocket_server.py to broadcast convoy route changes
Optimized for 100+ concurrent players with route update batching and performance monitoring
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
logger = logging.getLogger("ConvoyWebSocketIntegration")

@dataclass
class ConvoyRouteUpdate:
    """Convoy route update message structure"""
    type: str  # "route_generated", "route_invalidated", "routes_updated"
    faction_id: int
    route_id: Optional[str]
    route_data: Optional[Dict[str, Any]]
    security_rating: Optional[float]
    profitability_score: Optional[float]
    territorial_path: Optional[List[int]]
    timestamp: str
    performance_metrics: Dict[str, float]

class ConvoyWebSocketIntegration:
    """
    High-performance WebSocket integration for convoy route updates
    Coordinates with territorial system for real-time route adaptation
    """
    
    def __init__(self, territorial_server_host="127.0.0.1", territorial_server_port=8765):
        self.territorial_server_host = territorial_server_host
        self.territorial_server_port = territorial_server_port
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        self.running = False
        
        # Performance monitoring
        self.route_updates_sent = 0
        self.batch_updates_processed = 0
        self.average_update_latency = 0.0
        self.start_time = time.time()
        
        # Route update batching for performance
        self.pending_route_updates = []
        self.update_batch_size = 10  # Routes per batch
        self.update_batch_interval = 1.0  # Seconds between batch sends
        self.last_batch_send = time.time()
        
        # Connection to territorial WebSocket server
        self.territorial_websocket = None
        self.connection_retry_count = 0
        self.max_retry_attempts = 5
        
        logger.info("Convoy WebSocket Integration initialized")
        logger.info(f"Target territorial server: {territorial_server_host}:{territorial_server_port}")
        logger.info(f"Database: {self.db_path}")
    
    async def connect_to_territorial_server(self):
        """Establish connection to territorial WebSocket server"""
        retry_delay = 2.0
        
        while self.connection_retry_count < self.max_retry_attempts:
            try:
                uri = f"ws://{self.territorial_server_host}:{self.territorial_server_port}"
                logger.info(f"Attempting to connect to territorial server: {uri}")
                
                self.territorial_websocket = await websockets.connect(uri)
                logger.info("Successfully connected to territorial WebSocket server")
                self.connection_retry_count = 0
                return True
                
            except Exception as e:
                self.connection_retry_count += 1
                logger.error(f"Failed to connect (attempt {self.connection_retry_count}/{self.max_retry_attempts}): {e}")
                
                if self.connection_retry_count < self.max_retry_attempts:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
        
        logger.error("Max retry attempts reached. Could not connect to territorial server.")
        return False
    
    async def send_route_update(self, update: ConvoyRouteUpdate):
        """Send individual route update with performance tracking"""
        start_time = time.time()
        
        try:
            if not self.territorial_websocket:
                if not await self.connect_to_territorial_server():
                    logger.error("Cannot send route update - no connection to territorial server")
                    return False
            
            # Add convoy route update type identifier
            message = {
                "message_type": "convoy_route_update",
                "update_data": asdict(update)
            }
            
            await self.territorial_websocket.send(json.dumps(message))
            
            # Update performance metrics
            latency = (time.time() - start_time) * 1000  # Convert to ms
            self.average_update_latency = (self.average_update_latency * self.route_updates_sent + latency) / (self.route_updates_sent + 1)
            self.route_updates_sent += 1
            
            logger.debug(f"Sent convoy route update: {update.type} for faction {update.faction_id} (latency: {latency:.2f}ms)")
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Territorial server connection closed. Attempting to reconnect...")
            self.territorial_websocket = None
            return await self.send_route_update(update)  # Retry once
            
        except Exception as e:
            logger.error(f"Error sending route update: {e}")
            return False
    
    async def send_batch_route_updates(self, updates: List[ConvoyRouteUpdate]):
        """Send multiple route updates in batched format for performance"""
        start_time = time.time()
        
        try:
            if not self.territorial_websocket:
                if not await self.connect_to_territorial_server():
                    logger.error("Cannot send batch route updates - no connection to territorial server")
                    return False
            
            # Create batched update message
            batch_message = {
                "message_type": "convoy_route_batch_update",
                "batch_size": len(updates),
                "updates": [asdict(update) for update in updates],
                "timestamp": datetime.now().isoformat(),
                "performance_info": {
                    "batch_id": self.batch_updates_processed + 1,
                    "total_routes_in_batch": len(updates)
                }
            }
            
            await self.territorial_websocket.send(json.dumps(batch_message))
            
            # Update performance metrics
            batch_latency = (time.time() - start_time) * 1000
            self.batch_updates_processed += 1
            self.route_updates_sent += len(updates)
            
            logger.info(f"Sent batch route update: {len(updates)} routes (latency: {batch_latency:.2f}ms, avg: {self.average_update_latency:.2f}ms)")
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Territorial server connection closed during batch send. Attempting to reconnect...")
            self.territorial_websocket = None
            return await self.send_batch_route_updates(updates)  # Retry once
            
        except Exception as e:
            logger.error(f"Error sending batch route updates: {e}")
            return False
    
    def queue_route_update(self, update: ConvoyRouteUpdate):
        """Queue route update for batched sending (thread-safe)"""
        self.pending_route_updates.append(update)
        
        # If batch is full or enough time has passed, process immediately
        current_time = time.time()
        if (len(self.pending_route_updates) >= self.update_batch_size or 
            current_time - self.last_batch_send >= self.update_batch_interval):
            
            # Schedule batch processing on event loop
            if self.running:
                asyncio.create_task(self.process_pending_updates())
    
    async def process_pending_updates(self):
        """Process queued route updates in batches"""
        if not self.pending_route_updates:
            return
        
        # Extract current batch
        current_batch = self.pending_route_updates.copy()
        self.pending_route_updates.clear()
        self.last_batch_send = time.time()
        
        # Send batch update
        success = await self.send_batch_route_updates(current_batch)
        
        if not success:
            logger.warning(f"Failed to send batch of {len(current_batch)} route updates")
            # Could implement retry queue here if needed
    
    def monitor_convoy_database_changes(self):
        """Monitor database for convoy route changes and trigger updates"""
        logger.info("Starting convoy database change monitor")
        
        last_check_time = time.time()
        
        while self.running:
            try:
                connection = sqlite3.connect(str(self.db_path))
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                
                # Check for recent convoy-related territorial events that might affect routes
                cursor.execute("""
                    SELECT te.*, t.territory_name
                    FROM territorial_events te
                    JOIN territories t ON te.territory_id = t.id
                    WHERE te.started_at > datetime('now', '-10 seconds')
                    AND te.event_type IN ('capture', 'contest', 'abandon')
                """)
                
                recent_events = cursor.fetchall()
                
                for event in recent_events:
                    # Create convoy route invalidation update for affected territory
                    update = ConvoyRouteUpdate(
                        type="routes_invalidated_by_territory",
                        faction_id=event.get("initiating_faction_id", 0),
                        route_id=None,
                        route_data=None,
                        security_rating=None,
                        profitability_score=None,
                        territorial_path=[event["territory_id"]],
                        timestamp=event["started_at"],
                        performance_metrics={
                            "detection_latency": time.time() - last_check_time,
                            "event_type": event["event_type"]
                        }
                    )
                    
                    self.queue_route_update(update)
                
                connection.close()
                last_check_time = time.time()
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in convoy database monitor: {e}")
                time.sleep(5)  # Wait longer on error
    
    async def start_integration(self):
        """Start the convoy WebSocket integration service"""
        logger.info("Starting Convoy WebSocket Integration Service")
        
        self.running = True
        
        # Connect to territorial server
        if not await self.connect_to_territorial_server():
            logger.error("Failed to connect to territorial server. Convoy integration cannot start.")
            return
        
        # Start database monitoring in separate thread
        monitor_thread = threading.Thread(target=self.monitor_convoy_database_changes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start periodic batch processing
        async def periodic_batch_processor():
            while self.running:
                await asyncio.sleep(self.update_batch_interval)
                if self.pending_route_updates:
                    await self.process_pending_updates()
        
        batch_processor_task = asyncio.create_task(periodic_batch_processor())
        
        logger.info("Convoy WebSocket Integration Service started successfully")
        logger.info(f"Monitoring territorial database for convoy route impacts")
        logger.info(f"Batch processing: {self.update_batch_size} routes per batch, {self.update_batch_interval}s interval")
        
        # Keep service running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Convoy integration stopped by user")
        finally:
            self.running = False
            batch_processor_task.cancel()
            if self.territorial_websocket:
                await self.territorial_websocket.close()
    
    def stop_integration(self):
        """Stop the integration service"""
        logger.info("Stopping Convoy WebSocket Integration Service")
        self.running = False
        
        # Print performance statistics
        uptime = time.time() - self.start_time
        logger.info(f"Integration Statistics:")
        logger.info(f"  Uptime: {uptime:.1f} seconds")
        logger.info(f"  Route updates sent: {self.route_updates_sent}")
        logger.info(f"  Batch updates processed: {self.batch_updates_processed}")
        logger.info(f"  Average update latency: {self.average_update_latency:.2f}ms")
        logger.info(f"  Updates per second: {self.route_updates_sent / uptime:.1f}")
    
    # API for UE5 Integration
    def notify_route_generated(self, faction_id: int, route_id: str, route_data: Dict[str, Any]):
        """API call from UE5 when a new route is generated"""
        update = ConvoyRouteUpdate(
            type="route_generated",
            faction_id=faction_id,
            route_id=route_id,
            route_data=route_data,
            security_rating=route_data.get("security_rating", 0.0),
            profitability_score=route_data.get("profitability_score", 0.0),
            territorial_path=route_data.get("territorial_path", []),
            timestamp=datetime.now().isoformat(),
            performance_metrics={
                "generation_time": route_data.get("generation_time_ms", 0.0)
            }
        )
        
        self.queue_route_update(update)
        logger.debug(f"Queued route generation notification: {route_id} for faction {faction_id}")
    
    def notify_route_invalidated(self, faction_id: int, route_id: str, reason: str):
        """API call from UE5 when a route is invalidated"""
        update = ConvoyRouteUpdate(
            type="route_invalidated",
            faction_id=faction_id,
            route_id=route_id,
            route_data={"invalidation_reason": reason},
            security_rating=None,
            profitability_score=None,
            territorial_path=None,
            timestamp=datetime.now().isoformat(),
            performance_metrics={}
        )
        
        self.queue_route_update(update)
        logger.debug(f"Queued route invalidation notification: {route_id} for faction {faction_id} (reason: {reason})")
    
    def notify_faction_routes_updated(self, faction_id: int, active_route_count: int, total_profitability: float):
        """API call from UE5 when faction routes are bulk updated"""
        update = ConvoyRouteUpdate(
            type="faction_routes_updated",
            faction_id=faction_id,
            route_id=None,
            route_data={
                "active_route_count": active_route_count,
                "total_profitability": total_profitability
            },
            security_rating=None,
            profitability_score=total_profitability,
            territorial_path=None,
            timestamp=datetime.now().isoformat(),
            performance_metrics={}
        )
        
        self.queue_route_update(update)
        logger.info(f"Queued faction route update: {active_route_count} routes, {total_profitability:.2f} profit for faction {faction_id}")

async def main():
    """Main entry point for standalone convoy WebSocket integration"""
    integration = ConvoyWebSocketIntegration()
    
    try:
        await integration.start_integration()
    except KeyboardInterrupt:
        logger.info("Integration stopped by user")
    except Exception as e:
        logger.error(f"Integration error: {e}")
    finally:
        integration.stop_integration()

if __name__ == "__main__":
    print("CONVOY WEBSOCKET INTEGRATION - Performance Engineer Implementation")
    print("Real-time convoy route updates for 100+ concurrent players")
    print("Integrates with territorial WebSocket server for optimal performance")
    print("Press Ctrl+C to stop integration")
    print()
    
    asyncio.run(main())