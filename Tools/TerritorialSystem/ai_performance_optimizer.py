#!/usr/bin/env python3
"""
AI Performance Optimizer for Terminal Grounds Territorial System
Performance Engineer Implementation - Optimizing AI behavior for 100+ concurrent players

Manages AI processing load, coordinates with WebSocket server, and ensures smooth gameplay
performance while running sophisticated adaptive AI faction behavior systems.
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
import statistics
import psutil
import gc

@dataclass
class PerformanceConstraints:
    """Performance constraints for AI processing"""
    max_ai_processing_time: float = 0.016  # 16ms per frame (60 FPS target)
    max_concurrent_ai_threads: int = 4
    max_database_queries_per_second: int = 200  # Under 1ms per query
    target_websocket_latency: float = 0.050  # 50ms target
    memory_usage_limit_mb: int = 2048  # 2GB limit for AI processing
    cache_hit_ratio_target: float = 0.85  # 85% cache hit ratio

@dataclass
class SystemMetrics:
    """Real-time system performance metrics"""
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    ai_processing_time: float = 0.0
    database_query_time: float = 0.0
    websocket_latency: float = 0.0
    active_connections: int = 0
    ai_decisions_per_second: float = 0.0
    cache_hit_ratio: float = 0.0
    frame_time_ms: float = 0.0
    
@dataclass
class LoadBalancingConfig:
    """AI load balancing configuration"""
    ai_processing_interval: float = 1.0  # Base AI processing interval
    dynamic_scaling_enabled: bool = True
    load_threshold_high: float = 0.8  # 80% system load
    load_threshold_low: float = 0.3   # 30% system load
    scaling_factor: float = 1.2       # Scale factor for dynamic adjustments

class AIProcessingQueue:
    """High-performance queue for AI processing tasks"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.processing_times = deque(maxlen=100)
        self.completed_tasks = 0
        self.failed_tasks = 0
        
    async def enqueue_ai_task(self, faction_id: int, priority: int = 1) -> bool:
        """Enqueue AI processing task with priority"""
        try:
            task = {
                'faction_id': faction_id,
                'priority': priority,
                'timestamp': time.time(),
                'attempts': 0
            }
            await self.queue.put(task)
            return True
        except asyncio.QueueFull:
            return False
            
    async def dequeue_ai_task(self) -> Optional[Dict]:
        """Dequeue AI processing task"""
        try:
            task = await asyncio.wait_for(self.queue.get(), timeout=0.1)
            return task
        except asyncio.TimeoutError:
            return None
            
    def record_task_completion(self, processing_time: float, success: bool):
        """Record task completion metrics"""
        self.processing_times.append(processing_time)
        if success:
            self.completed_tasks += 1
        else:
            self.failed_tasks += 1
            
    def get_avg_processing_time(self) -> float:
        """Get average processing time"""
        return statistics.mean(self.processing_times) if self.processing_times else 0.0
        
    def get_success_rate(self) -> float:
        """Get task success rate"""
        total_tasks = self.completed_tasks + self.failed_tasks
        return self.completed_tasks / max(total_tasks, 1)

class DatabaseConnectionPool:
    """High-performance database connection pool"""
    
    def __init__(self, db_path: str, pool_size: int = 8):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.available_connections = asyncio.Queue(maxsize=pool_size)
        self.connection_usage = defaultdict(int)
        self.query_times = deque(maxlen=1000)
        
    async def initialize_pool(self):
        """Initialize connection pool"""
        import sqlite3
        
        for i in range(self.pool_size):
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connections.append(conn)
                await self.available_connections.put(conn)
            except Exception as e:
                print(f"Error creating database connection {i}: {e}")
                
    async def get_connection(self):
        """Get database connection from pool"""
        try:
            conn = await asyncio.wait_for(self.available_connections.get(), timeout=1.0)
            self.connection_usage[id(conn)] += 1
            return conn
        except asyncio.TimeoutError:
            print("Warning: Database connection pool exhausted")
            return None
            
    async def return_connection(self, conn):
        """Return connection to pool"""
        if conn:
            await self.available_connections.put(conn)
            
    async def execute_query_optimized(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute optimized database query"""
        start_time = time.time()
        conn = await self.get_connection()
        
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            query_time = time.time() - start_time
            self.query_times.append(query_time)
            
            return results
            
        except Exception as e:
            print(f"Database query error: {e}")
            return []
        finally:
            await self.return_connection(conn)
            
    def get_avg_query_time(self) -> float:
        """Get average query time"""
        return statistics.mean(self.query_times) if self.query_times else 0.0
        
    def cleanup_pool(self):
        """Cleanup connection pool"""
        for conn in self.connections:
            conn.close()

class AIPerformanceOptimizer:
    """
    Performance optimizer for AI faction behavior in multiplayer territorial warfare
    Ensures smooth gameplay performance for 100+ concurrent players
    """
    
    def __init__(self, adaptive_ai_system, websocket_server=None):
        self.ai_system = adaptive_ai_system
        self.websocket_server = websocket_server
        
        # Performance components
        self.constraints = PerformanceConstraints()
        self.metrics = SystemMetrics()
        self.load_config = LoadBalancingConfig()
        
        # Processing systems
        self.ai_queue = AIProcessingQueue()
        self.db_pool = None
        self.executor = ThreadPoolExecutor(max_workers=self.constraints.max_concurrent_ai_threads)
        
        # Performance monitoring
        self.performance_history = deque(maxlen=1000)
        self.load_measurements = deque(maxlen=60)  # 60 seconds of measurements
        self.optimization_active = False
        
        # Frame timing for 60 FPS coordination
        self.frame_start_time = 0.0
        self.frame_budget_remaining = 0.0
        
        print("AI Performance Optimizer initialized")
        print(f"Target performance: 60 FPS ({self.constraints.max_ai_processing_time*1000:.1f}ms AI budget per frame)")
        
    async def initialize_optimizer(self):
        """Initialize performance optimization systems"""
        # Initialize database connection pool
        self.db_pool = DatabaseConnectionPool(
            str(self.ai_system.db_path), 
            pool_size=self.constraints.max_concurrent_ai_threads * 2
        )
        await self.db_pool.initialize_pool()
        
        # Start monitoring systems
        self.optimization_active = True
        asyncio.create_task(self._performance_monitor_loop())
        asyncio.create_task(self._ai_processing_loop())
        asyncio.create_task(self._load_balancing_loop())
        
        print("Performance optimization systems active")
        
    async def _performance_monitor_loop(self):
        """Continuous performance monitoring"""
        while self.optimization_active:
            try:
                # Collect system metrics
                self.metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
                self.metrics.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
                
                # AI system metrics
                if hasattr(self.ai_system, 'performance_metrics'):
                    ai_perf = self.ai_system.performance_metrics
                    self.metrics.ai_processing_time = ai_perf.avg_decision_time
                    self.metrics.database_query_time = ai_perf.database_query_time
                    self.metrics.cache_hit_ratio = ai_perf.cache_hit_ratio
                    
                # Database metrics
                if self.db_pool:
                    self.metrics.database_query_time = self.db_pool.get_avg_query_time()
                    
                # WebSocket metrics
                if self.websocket_server and hasattr(self.websocket_server, 'client_count'):
                    self.metrics.active_connections = self.websocket_server.client_count
                    
                # AI processing metrics
                self.metrics.ai_decisions_per_second = self.ai_queue.completed_tasks / max(time.time() - self.frame_start_time, 1)
                
                # Record performance snapshot
                self.performance_history.append({
                    'timestamp': time.time(),
                    'cpu_usage': self.metrics.cpu_usage,
                    'memory_usage_mb': self.metrics.memory_usage_mb,
                    'ai_processing_time': self.metrics.ai_processing_time,
                    'active_connections': self.metrics.active_connections,
                    'frame_time_ms': self.metrics.frame_time_ms
                })
                
                # Performance warnings
                if self.metrics.ai_processing_time > self.constraints.max_ai_processing_time:
                    print(f"WARNING: AI processing time {self.metrics.ai_processing_time*1000:.1f}ms exceeds {self.constraints.max_ai_processing_time*1000:.1f}ms budget")
                    
                if self.metrics.memory_usage_mb > self.constraints.memory_usage_limit_mb:
                    print(f"WARNING: Memory usage {self.metrics.memory_usage_mb:.1f}MB exceeds {self.constraints.memory_usage_limit_mb}MB limit")
                    await self._trigger_memory_optimization()
                    
                await asyncio.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                print(f"Error in performance monitor: {e}")
                await asyncio.sleep(1.0)
                
    async def _ai_processing_loop(self):
        """Main AI processing loop with performance optimization"""
        while self.optimization_active:
            try:
                frame_start = time.time()
                self.frame_start_time = frame_start
                self.frame_budget_remaining = self.constraints.max_ai_processing_time
                
                # Process AI tasks within frame budget
                processed_tasks = 0
                while self.frame_budget_remaining > 0.001:  # 1ms minimum remaining
                    task = await self.ai_queue.dequeue_ai_task()
                    if not task:
                        break
                        
                    # Process AI decision with timing
                    task_start = time.time()
                    success = await self._process_ai_task_optimized(task)
                    task_time = time.time() - task_start
                    
                    # Record task completion
                    self.ai_queue.record_task_completion(task_time, success)
                    processed_tasks += 1
                    
                    # Update remaining frame budget
                    self.frame_budget_remaining -= task_time
                    
                    # Safety break if we're taking too long
                    if task_time > self.constraints.max_ai_processing_time * 0.5:
                        break
                        
                # Calculate frame metrics
                frame_time = time.time() - frame_start
                self.metrics.frame_time_ms = frame_time * 1000
                
                # Dynamic interval adjustment based on load
                if self.load_config.dynamic_scaling_enabled:
                    interval = self._calculate_dynamic_interval()
                else:
                    interval = self.load_config.ai_processing_interval
                    
                # Wait for next frame
                sleep_time = max(0.001, interval - frame_time)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                print(f"Error in AI processing loop: {e}")
                await asyncio.sleep(0.1)
                
    async def _process_ai_task_optimized(self, task: Dict) -> bool:
        """Process individual AI task with optimization"""
        try:
            faction_id = task['faction_id']
            
            # Use cached state if available
            state = await self.ai_system.load_territorial_state_cached()
            
            # Generate decision with timeout
            decision_coro = self.ai_system._generate_single_faction_decision(faction_id, state)
            decision = await asyncio.wait_for(decision_coro, timeout=0.05)  # 50ms timeout
            
            if decision:
                # Queue decision for batch processing
                await self._queue_decision_for_batch_update(decision)
                return True
                
            return False
            
        except asyncio.TimeoutError:
            print(f"AI decision timeout for faction {task['faction_id']}")
            return False
        except Exception as e:
            print(f"Error processing AI task: {e}")
            return False
            
    async def _queue_decision_for_batch_update(self, decision):
        """Queue decision for batch database update"""
        # Add to AI system's batch queue
        if hasattr(self.ai_system, 'batch_update_queue'):
            with self.ai_system.update_lock:
                self.ai_system.batch_update_queue.append(decision)
                
    def _calculate_dynamic_interval(self) -> float:
        """Calculate dynamic processing interval based on system load"""
        base_interval = self.load_config.ai_processing_interval
        
        # CPU-based scaling
        cpu_load_factor = 1.0
        if self.metrics.cpu_usage > self.load_config.load_threshold_high * 100:
            cpu_load_factor = self.load_config.scaling_factor
        elif self.metrics.cpu_usage < self.load_config.load_threshold_low * 100:
            cpu_load_factor = 1.0 / self.load_config.scaling_factor
            
        # Connection-based scaling
        connection_factor = 1.0
        if self.metrics.active_connections > 80:  # High connection load
            connection_factor = 1.3
        elif self.metrics.active_connections < 20:  # Low connection load
            connection_factor = 0.8
            
        # Memory-based scaling
        memory_factor = 1.0
        memory_usage_ratio = self.metrics.memory_usage_mb / self.constraints.memory_usage_limit_mb
        if memory_usage_ratio > 0.8:
            memory_factor = 1.5
            
        # Combine factors
        total_factor = cpu_load_factor * connection_factor * memory_factor
        adjusted_interval = base_interval * total_factor
        
        # Clamp to reasonable bounds
        return max(0.1, min(5.0, adjusted_interval))
        
    async def _load_balancing_loop(self):
        """Load balancing and optimization loop"""
        while self.optimization_active:
            try:
                # Collect load measurements
                current_load = {
                    'cpu': self.metrics.cpu_usage / 100.0,
                    'memory': self.metrics.memory_usage_mb / self.constraints.memory_usage_limit_mb,
                    'ai_time': self.metrics.ai_processing_time / self.constraints.max_ai_processing_time,
                    'connections': self.metrics.active_connections / 100.0  # Assume 100 max for calculation
                }
                
                overall_load = statistics.mean(current_load.values())
                self.load_measurements.append(overall_load)
                
                # Trigger optimizations based on load
                if overall_load > self.load_config.load_threshold_high:
                    await self._trigger_performance_optimization()
                elif overall_load < self.load_config.load_threshold_low:
                    await self._trigger_performance_enhancement()
                    
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in load balancing: {e}")
                await asyncio.sleep(5.0)
                
    async def _trigger_performance_optimization(self):
        """Trigger performance optimization measures"""
        print("Triggering performance optimization due to high system load")
        
        # Reduce AI processing frequency
        self.load_config.ai_processing_interval *= 1.2
        
        # Trigger garbage collection
        gc.collect()
        
        # Clear old cache entries
        if hasattr(self.ai_system, 'state_cache'):
            # Force cache refresh to free memory
            self.ai_system.state_cache._territorial_state = None
            
        # Reduce cache durations
        for profile in self.ai_system.behavior_profiles.values():
            profile.cache_duration *= 0.8
            
        print(f"Performance optimization applied - new AI interval: {self.load_config.ai_processing_interval:.2f}s")
        
    async def _trigger_performance_enhancement(self):
        """Trigger performance enhancement measures"""
        # System is under low load - can increase AI processing frequency
        self.load_config.ai_processing_interval *= 0.9
        
        # Increase cache durations for better performance
        for profile in self.ai_system.behavior_profiles.values():
            profile.cache_duration = min(60.0, profile.cache_duration * 1.1)
            
    async def _trigger_memory_optimization(self):
        """Trigger memory optimization measures"""
        print("Triggering memory optimization")
        
        # Force garbage collection
        gc.collect()
        
        # Clear performance history
        self.performance_history.clear()
        
        # Clear AI decision history
        if hasattr(self.ai_system, 'decision_history'):
            self.ai_system.decision_history.clear()
            
        # Clear adaptation records (keep only recent)
        if hasattr(self.ai_system, 'adaptation_records'):
            self.ai_system.adaptation_records = self.ai_system.adaptation_records[-100:]
            
        # Clear success patterns (keep only recent)
        for pattern_key in self.ai_system.success_patterns:
            self.ai_system.success_patterns[pattern_key] = self.ai_system.success_patterns[pattern_key][-50:]
            
    async def enqueue_faction_ai_processing(self, faction_ids: List[int], priority: int = 1) -> bool:
        """Enqueue AI processing for factions with performance consideration"""
        # Check if we can handle more AI processing
        if self.metrics.ai_processing_time > self.constraints.max_ai_processing_time * 0.8:
            return False  # Too busy
            
        # Enqueue tasks
        success = True
        for faction_id in faction_ids:
            if not await self.ai_queue.enqueue_ai_task(faction_id, priority):
                success = False
                
        return success
        
    async def coordinate_with_websocket_server(self, server):
        """Coordinate AI processing with WebSocket server load"""
        self.websocket_server = server
        
        # Monitor WebSocket server performance
        if hasattr(server, 'client_count'):
            connection_count = server.client_count
            
            # Adjust AI processing based on connection load
            if connection_count > 80:
                # High connection load - reduce AI processing frequency
                self.load_config.ai_processing_interval = max(2.0, self.load_config.ai_processing_interval * 1.2)
            elif connection_count < 20:
                # Low connection load - can increase AI processing
                self.load_config.ai_processing_interval = max(0.5, self.load_config.ai_processing_interval * 0.9)
                
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        if not self.performance_history:
            return {'error': 'No performance data available'}
            
        recent_measurements = list(self.performance_history)[-60:]  # Last 60 seconds
        
        report = {
            'current_metrics': {
                'cpu_usage_percent': self.metrics.cpu_usage,
                'memory_usage_mb': self.metrics.memory_usage_mb,
                'ai_processing_time_ms': self.metrics.ai_processing_time * 1000,
                'database_query_time_ms': self.metrics.database_query_time * 1000,
                'active_connections': self.metrics.active_connections,
                'frame_time_ms': self.metrics.frame_time_ms,
                'cache_hit_ratio': self.metrics.cache_hit_ratio
            },
            'performance_targets': {
                'ai_processing_time_target_ms': self.constraints.max_ai_processing_time * 1000,
                'websocket_latency_target_ms': self.constraints.target_websocket_latency * 1000,
                'database_query_target_ms': 1.0,  # 1ms target
                'cache_hit_ratio_target': self.constraints.cache_hit_ratio_target,
                'memory_limit_mb': self.constraints.memory_usage_limit_mb
            },
            'ai_processing_stats': {
                'avg_processing_time_ms': self.ai_queue.get_avg_processing_time() * 1000,
                'completed_tasks': self.ai_queue.completed_tasks,
                'failed_tasks': self.ai_queue.failed_tasks,
                'success_rate': self.ai_queue.get_success_rate(),
                'current_interval_s': self.load_config.ai_processing_interval
            },
            'recent_performance': {
                'avg_cpu_usage': statistics.mean([m['cpu_usage'] for m in recent_measurements]),
                'avg_memory_mb': statistics.mean([m['memory_usage_mb'] for m in recent_measurements]),
                'avg_frame_time_ms': statistics.mean([m['frame_time_ms'] for m in recent_measurements]),
                'load_trend': 'stable' if len(self.load_measurements) < 2 else 
                             ('increasing' if self.load_measurements[-1] > self.load_measurements[-5] else 'decreasing')
            },
            'optimization_status': {
                'optimization_active': self.optimization_active,
                'dynamic_scaling_enabled': self.load_config.dynamic_scaling_enabled,
                'database_pool_size': self.db_pool.pool_size if self.db_pool else 0,
                'concurrent_ai_threads': self.constraints.max_concurrent_ai_threads
            }
        }
        
        return report
        
    def shutdown_optimizer(self):
        """Shutdown performance optimizer"""
        print("Shutting down AI performance optimizer...")
        self.optimization_active = False
        
        if self.db_pool:
            self.db_pool.cleanup_pool()
            
        self.executor.shutdown(wait=True)
        print("AI performance optimizer shutdown complete")

# Integration function for existing systems
async def integrate_ai_performance_optimization(adaptive_ai_system, websocket_server=None):
    """
    Integration function to add performance optimization to existing AI system
    """
    optimizer = AIPerformanceOptimizer(adaptive_ai_system, websocket_server)
    await optimizer.initialize_optimizer()
    
    # Replace AI system's processing method with optimized version
    original_process_turn = adaptive_ai_system.process_ai_turn_adaptive
    
    async def optimized_process_turn():
        """Optimized AI turn processing"""
        # Enqueue all factions for processing
        faction_ids = list(adaptive_ai_system.behavior_profiles.keys())
        success = await optimizer.enqueue_faction_ai_processing(faction_ids)
        
        if not success:
            print("Warning: AI processing queue at capacity")
            
        # Return empty list as actual processing happens in background
        return []
        
    # Patch the AI system
    adaptive_ai_system.process_ai_turn_adaptive = optimized_process_turn
    adaptive_ai_system.performance_optimizer = optimizer
    
    return optimizer

if __name__ == "__main__":
    print("AI Performance Optimizer - Standalone Testing")
    print("For integration testing, use integrate_ai_performance_optimization()")