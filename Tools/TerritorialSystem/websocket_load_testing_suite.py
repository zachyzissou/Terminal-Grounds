#!/usr/bin/env python3
"""
WebSocket Load Testing Suite for Integrated Territorial Warfare System
Performance Engineer Implementation - 120+ concurrent player load validation

Tests WebSocket server integration under realistic multiplayer load conditions
with comprehensive performance monitoring and bottleneck identification.
"""

import asyncio
import json
import time
import random
import statistics
import websockets
import threading
import psutil
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import concurrent.futures
import logging
from datetime import datetime, timedelta
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WebSocketLoadTestConfig:
    """Configuration for WebSocket load testing"""
    server_uri: str = "ws://127.0.0.1:8765"
    max_concurrent_connections: int = 120
    test_duration_seconds: int = 300  # 5 minutes
    message_rate_per_client: float = 2.0  # Messages per second per client
    connection_ramp_up_seconds: int = 30  # Gradual connection establishment
    performance_sample_rate: float = 10.0  # Samples per second
    target_response_time_ms: float = 50.0  # <50ms response time target
    target_connection_success_rate: float = 0.95  # 95% success rate
    
@dataclass
class ClientPerformanceMetrics:
    """Performance metrics for individual client"""
    client_id: int
    connection_established: bool
    messages_sent: int
    messages_received: int
    average_response_time_ms: float
    max_response_time_ms: float
    connection_errors: int
    message_errors: int
    bytes_sent: int
    bytes_received: int
    connection_duration: float

@dataclass
class WebSocketLoadTestResult:
    """Results from WebSocket load test"""
    test_name: str
    start_time: datetime
    end_time: datetime
    target_connections: int
    successful_connections: int
    connection_success_rate: float
    total_messages_sent: int
    total_messages_received: int
    average_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    max_response_time_ms: float
    messages_per_second: float
    bytes_per_second: float
    server_resource_usage: Dict[str, float]
    performance_violations: List[str]
    success: bool

class MockTerritorialClient:
    """Mock client simulating territorial warfare player interactions"""
    
    def __init__(self, client_id: int, server_uri: str, message_rate: float):
        self.client_id = client_id
        self.server_uri = server_uri
        self.message_rate = message_rate
        self.websocket = None
        self.running = False
        
        # Performance tracking
        self.messages_sent = 0
        self.messages_received = 0
        self.response_times = deque(maxlen=1000)
        self.connection_errors = 0
        self.message_errors = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.connection_start_time = 0
        self.connection_established = False
        
        # Message tracking for response time calculation
        self.pending_messages = {}  # message_id -> timestamp
        
    async def connect_and_simulate(self, duration: float):
        """Connect and simulate territorial warfare client behavior"""
        self.connection_start_time = time.time()
        
        try:
            self.websocket = await websockets.connect(self.server_uri)
            self.connection_established = True
            self.running = True
            
            logger.info(f"Client {self.client_id} connected successfully")
            
            # Start message sending and receiving tasks
            send_task = asyncio.create_task(self._send_messages_loop(duration))
            receive_task = asyncio.create_task(self._receive_messages_loop())
            
            # Wait for test duration
            await asyncio.sleep(duration)
            self.running = False
            
            # Wait for tasks to complete
            await asyncio.gather(send_task, receive_task, return_exceptions=True)
            
        except websockets.exceptions.ConnectionClosed as e:
            self.connection_errors += 1
            logger.warning(f"Client {self.client_id} connection closed: {e}")
        except Exception as e:
            self.connection_errors += 1
            logger.error(f"Client {self.client_id} error: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
                
    async def _send_messages_loop(self, duration: float):
        """Send territorial warfare messages at specified rate"""
        end_time = time.time() + duration
        message_interval = 1.0 / self.message_rate if self.message_rate > 0 else 1.0
        
        while self.running and time.time() < end_time:
            try:
                message = self._generate_territorial_message()
                message_bytes = json.dumps(message).encode('utf-8')
                
                await self.websocket.send(message_bytes)
                
                self.messages_sent += 1
                self.bytes_sent += len(message_bytes)
                
                # Track message for response time measurement
                if 'message_id' in message:
                    self.pending_messages[message['message_id']] = time.time()
                    
                # Maintain message rate
                await asyncio.sleep(message_interval)
                
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                self.message_errors += 1
                logger.error(f"Client {self.client_id} send error: {e}")
                
    async def _receive_messages_loop(self):
        """Receive and process messages from server"""
        while self.running:
            try:
                message_bytes = await self.websocket.recv()
                self.bytes_received += len(message_bytes)
                
                message = json.loads(message_bytes.decode('utf-8'))
                self.messages_received += 1
                
                # Calculate response time if this is a response to our message
                if 'response_to' in message:
                    message_id = message['response_to']
                    if message_id in self.pending_messages:
                        response_time = (time.time() - self.pending_messages[message_id]) * 1000  # ms
                        self.response_times.append(response_time)
                        del self.pending_messages[message_id]
                        
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                self.message_errors += 1
                logger.error(f"Client {self.client_id} receive error: {e}")
                
    def _generate_territorial_message(self) -> Dict[str, Any]:
        """Generate realistic territorial warfare message"""
        message_types = [
            'territorial_update',
            'influence_change', 
            'extraction_action',
            'convoy_movement',
            'diplomatic_action',
            'ai_decision_request',
            'resource_transfer',
            'alliance_proposal'
        ]
        
        message_type = random.choice(message_types)
        message_id = f"{self.client_id}_{self.messages_sent}_{int(time.time() * 1000)}"
        
        base_message = {
            'type': message_type,
            'message_id': message_id,
            'client_id': self.client_id,
            'timestamp': time.time()
        }
        
        # Add type-specific data
        if message_type == 'territorial_update':
            base_message.update({
                'territory_id': random.randint(1, 20),
                'faction_id': random.randint(1, 7),
                'influence_delta': random.randint(-100, 100)
            })
        elif message_type == 'influence_change':
            base_message.update({
                'territory_id': random.randint(1, 20),
                'faction_id': random.randint(1, 7),
                'influence_change': random.randint(-50, 50)
            })
        elif message_type == 'extraction_action':
            base_message.update({
                'extraction_point_id': random.randint(1, 10),
                'faction_id': random.randint(1, 7),
                'extraction_amount': random.randint(10, 100)
            })
        elif message_type == 'convoy_movement':
            base_message.update({
                'convoy_id': random.randint(1, 15),
                'from_territory': random.randint(1, 20),
                'to_territory': random.randint(1, 20),
                'cargo_value': random.randint(100, 1000)
            })
        elif message_type == 'diplomatic_action':
            base_message.update({
                'from_faction': random.randint(1, 7),
                'to_faction': random.randint(1, 7),
                'action_type': random.choice(['alliance', 'trade', 'cease_fire', 'declare_war']),
                'terms': {'duration': random.randint(60, 3600)}
            })
        elif message_type == 'ai_decision_request':
            base_message.update({
                'faction_id': random.randint(1, 7),
                'decision_context': {
                    'controlled_territories': random.randint(1, 10),
                    'threat_level': random.choice(['low', 'medium', 'high']),
                    'resources': random.randint(100, 1000)
                }
            })
        elif message_type == 'resource_transfer':
            base_message.update({
                'from_territory': random.randint(1, 20),
                'to_territory': random.randint(1, 20),
                'resource_type': random.choice(['industrial', 'military', 'research', 'economic']),
                'amount': random.randint(10, 200)
            })
        elif message_type == 'alliance_proposal':
            base_message.update({
                'proposing_faction': random.randint(1, 7),
                'target_faction': random.randint(1, 7),
                'proposal_type': random.choice(['mutual_defense', 'resource_sharing', 'territory_agreement']),
                'duration_hours': random.randint(24, 168)  # 1 day to 1 week
            })
            
        return base_message
        
    def get_performance_metrics(self) -> ClientPerformanceMetrics:
        """Get client performance metrics"""
        connection_duration = time.time() - self.connection_start_time if self.connection_start_time > 0 else 0
        avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
        max_response_time = max(self.response_times) if self.response_times else 0
        
        return ClientPerformanceMetrics(
            client_id=self.client_id,
            connection_established=self.connection_established,
            messages_sent=self.messages_sent,
            messages_received=self.messages_received,
            average_response_time_ms=avg_response_time,
            max_response_time_ms=max_response_time,
            connection_errors=self.connection_errors,
            message_errors=self.message_errors,
            bytes_sent=self.bytes_sent,
            bytes_received=self.bytes_received,
            connection_duration=connection_duration
        )

class SystemResourceMonitor:
    """Monitor system resource usage during WebSocket load testing"""
    
    def __init__(self, sample_rate: float = 10.0):
        self.sample_rate = sample_rate
        self.monitoring = False
        self.resource_history = deque(maxlen=10000)
        
    async def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        asyncio.create_task(self._monitoring_loop())
        logger.info("System resource monitoring started")
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        logger.info("System resource monitoring stopped")
        
    async def _monitoring_loop(self):
        """Resource monitoring loop"""
        while self.monitoring:
            try:
                # CPU and memory metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                
                # Network metrics
                network_io = psutil.net_io_counters()
                
                # Process-specific metrics
                process = psutil.Process()
                process_memory = process.memory_info()
                
                metrics = {
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_info.percent,
                    'memory_used_mb': memory_info.used / 1024 / 1024,
                    'memory_available_mb': memory_info.available / 1024 / 1024,
                    'process_memory_mb': process_memory.rss / 1024 / 1024,
                    'network_bytes_sent': network_io.bytes_sent,
                    'network_bytes_recv': network_io.bytes_recv,
                    'active_threads': threading.active_count()
                }
                
                self.resource_history.append(metrics)
                
                await asyncio.sleep(1.0 / self.sample_rate)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(1.0)
                
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary"""
        if not self.resource_history:
            return {}
            
        # Extract metric arrays
        cpu_values = [m['cpu_percent'] for m in self.resource_history]
        memory_values = [m['memory_percent'] for m in self.resource_history]
        process_memory_values = [m['process_memory_mb'] for m in self.resource_history]
        
        return {
            'cpu_usage': {
                'mean': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'p95': sorted(cpu_values)[int(len(cpu_values) * 0.95)]
            },
            'memory_usage': {
                'mean': statistics.mean(memory_values),
                'max': max(memory_values),
                'p95': sorted(memory_values)[int(len(memory_values) * 0.95)]
            },
            'process_memory_mb': {
                'mean': statistics.mean(process_memory_values),
                'max': max(process_memory_values),
                'p95': sorted(process_memory_values)[int(len(process_memory_values) * 0.95)]
            },
            'samples_collected': len(self.resource_history)
        }

class WebSocketLoadTester:
    """
    Comprehensive WebSocket load testing for territorial warfare system
    Tests server performance under 120+ concurrent connections with realistic traffic
    """
    
    def __init__(self, config: WebSocketLoadTestConfig):
        self.config = config
        self.resource_monitor = SystemResourceMonitor(config.performance_sample_rate)
        self.clients: List[MockTerritorialClient] = []
        
        logger.info(f"WebSocket Load Tester initialized for {config.max_concurrent_connections} connections")
        
    async def run_load_test(self) -> WebSocketLoadTestResult:
        """Run comprehensive WebSocket load test"""
        logger.info("STARTING WEBSOCKET LOAD TEST")
        logger.info(f"Target connections: {self.config.max_concurrent_connections}")
        logger.info(f"Test duration: {self.config.test_duration_seconds} seconds")
        logger.info(f"Server URI: {self.config.server_uri}")
        
        start_time = datetime.now()
        
        # Start resource monitoring
        await self.resource_monitor.start_monitoring()
        
        try:
            # Create client instances
            self.clients = [
                MockTerritorialClient(
                    client_id=i,
                    server_uri=self.config.server_uri,
                    message_rate=self.config.message_rate_per_client
                ) for i in range(self.config.max_concurrent_connections)
            ]
            
            # Execute load test with gradual ramp-up
            await self._execute_load_test_with_ramp_up()
            
            # Collect results
            end_time = datetime.now()
            test_result = self._analyze_test_results(start_time, end_time)
            
            return test_result
            
        except Exception as e:
            logger.error(f"Load test execution error: {e}")
            end_time = datetime.now()
            return self._create_error_result(start_time, end_time, str(e))
        finally:
            # Stop monitoring and cleanup
            self.resource_monitor.stop_monitoring()
            
    async def _execute_load_test_with_ramp_up(self):
        """Execute load test with gradual connection ramp-up"""
        logger.info("Starting gradual connection ramp-up...")
        
        # Calculate ramp-up timing
        connections_per_second = self.config.max_concurrent_connections / self.config.connection_ramp_up_seconds
        
        # Start clients in batches
        client_tasks = []
        for i, client in enumerate(self.clients):
            # Delay each client based on ramp-up schedule
            delay = i / connections_per_second
            
            task = asyncio.create_task(
                self._start_client_with_delay(client, delay, self.config.test_duration_seconds)
            )
            client_tasks.append(task)
            
        logger.info(f"All {len(client_tasks)} client tasks created, waiting for completion...")
        
        # Wait for all clients to complete
        await asyncio.gather(*client_tasks, return_exceptions=True)
        
        logger.info("All client tasks completed")
        
    async def _start_client_with_delay(self, client: MockTerritorialClient, delay: float, duration: float):
        """Start individual client with specified delay"""
        await asyncio.sleep(delay)
        await client.connect_and_simulate(duration)
        
    def _analyze_test_results(self, start_time: datetime, end_time: datetime) -> WebSocketLoadTestResult:
        """Analyze test results and generate comprehensive report"""
        logger.info("Analyzing load test results...")
        
        # Collect client metrics
        client_metrics = [client.get_performance_metrics() for client in self.clients]
        
        # Calculate aggregate metrics
        successful_connections = sum(1 for m in client_metrics if m.connection_established)
        connection_success_rate = successful_connections / len(client_metrics) if client_metrics else 0
        
        total_messages_sent = sum(m.messages_sent for m in client_metrics)
        total_messages_received = sum(m.messages_received for m in client_metrics)
        
        # Response time statistics
        all_response_times = []
        for client in self.clients:
            if client.response_times:
                all_response_times.extend(client.response_times)
                
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        p95_response_time = sorted(all_response_times)[int(len(all_response_times) * 0.95)] if all_response_times else 0
        p99_response_time = sorted(all_response_times)[int(len(all_response_times) * 0.99)] if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        
        # Throughput calculations
        test_duration_seconds = (end_time - start_time).total_seconds()
        messages_per_second = total_messages_sent / test_duration_seconds if test_duration_seconds > 0 else 0
        
        total_bytes = sum(m.bytes_sent + m.bytes_received for m in client_metrics)
        bytes_per_second = total_bytes / test_duration_seconds if test_duration_seconds > 0 else 0
        
        # Resource usage summary
        resource_summary = self.resource_monitor.get_resource_summary()
        
        # Performance violations
        violations = self._identify_performance_violations(
            connection_success_rate, avg_response_time, p95_response_time, resource_summary
        )
        
        # Overall success determination
        success = (
            connection_success_rate >= self.config.target_connection_success_rate and
            avg_response_time <= self.config.target_response_time_ms and
            len(violations) == 0
        )
        
        return WebSocketLoadTestResult(
            test_name=f"WebSocket Load Test - {self.config.max_concurrent_connections} connections",
            start_time=start_time,
            end_time=end_time,
            target_connections=self.config.max_concurrent_connections,
            successful_connections=successful_connections,
            connection_success_rate=connection_success_rate,
            total_messages_sent=total_messages_sent,
            total_messages_received=total_messages_received,
            average_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            max_response_time_ms=max_response_time,
            messages_per_second=messages_per_second,
            bytes_per_second=bytes_per_second,
            server_resource_usage=resource_summary,
            performance_violations=violations,
            success=success
        )
        
    def _identify_performance_violations(self, connection_success_rate: float, 
                                       avg_response_time: float, p95_response_time: float,
                                       resource_summary: Dict[str, Any]) -> List[str]:
        """Identify performance violations"""
        violations = []
        
        # Connection success rate violations
        if connection_success_rate < self.config.target_connection_success_rate:
            violations.append(f"Connection success rate {connection_success_rate:.2%} below target {self.config.target_connection_success_rate:.2%}")
            
        # Response time violations
        if avg_response_time > self.config.target_response_time_ms:
            violations.append(f"Average response time {avg_response_time:.1f}ms exceeds target {self.config.target_response_time_ms}ms")
            
        if p95_response_time > self.config.target_response_time_ms * 2:  # Allow 2x target for P95
            violations.append(f"P95 response time {p95_response_time:.1f}ms exceeds threshold")
            
        # Resource usage violations
        cpu_stats = resource_summary.get('cpu_usage', {})
        if cpu_stats.get('p95', 0) > 90:
            violations.append(f"CPU usage P95 {cpu_stats['p95']:.1f}% exceeds 90% threshold")
            
        memory_stats = resource_summary.get('memory_usage', {})
        if memory_stats.get('p95', 0) > 85:
            violations.append(f"Memory usage P95 {memory_stats['p95']:.1f}% exceeds 85% threshold")
            
        return violations
        
    def _create_error_result(self, start_time: datetime, end_time: datetime, error: str) -> WebSocketLoadTestResult:
        """Create error result when test fails"""
        return WebSocketLoadTestResult(
            test_name=f"WebSocket Load Test - ERROR",
            start_time=start_time,
            end_time=end_time,
            target_connections=self.config.max_concurrent_connections,
            successful_connections=0,
            connection_success_rate=0.0,
            total_messages_sent=0,
            total_messages_received=0,
            average_response_time_ms=0.0,
            p95_response_time_ms=0.0,
            p99_response_time_ms=0.0,
            max_response_time_ms=0.0,
            messages_per_second=0.0,
            bytes_per_second=0.0,
            server_resource_usage={},
            performance_violations=[f"Test execution error: {error}"],
            success=False
        )
        
    def generate_load_test_report(self, result: WebSocketLoadTestResult) -> str:
        """Generate comprehensive load test report"""
        report_lines = [
            "=" * 80,
            "WEBSOCKET LOAD TEST REPORT",
            "=" * 80,
            f"Test: {result.test_name}",
            f"Duration: {(result.end_time - result.start_time).total_seconds():.1f} seconds",
            f"Target Connections: {result.target_connections}",
            "",
            "CONNECTION RESULTS:",
            f"  Successful Connections: {result.successful_connections}",
            f"  Connection Success Rate: {result.connection_success_rate:.2%}",
            f"  Target Success Rate: {self.config.target_connection_success_rate:.2%}",
            "",
            "PERFORMANCE METRICS:",
            f"  Total Messages Sent: {result.total_messages_sent:,}",
            f"  Total Messages Received: {result.total_messages_received:,}",
            f"  Messages per Second: {result.messages_per_second:.1f}",
            f"  Throughput: {result.bytes_per_second / 1024:.1f} KB/s",
            "",
            "RESPONSE TIME ANALYSIS:",
            f"  Average Response Time: {result.average_response_time_ms:.1f} ms",
            f"  P95 Response Time: {result.p95_response_time_ms:.1f} ms",
            f"  P99 Response Time: {result.p99_response_time_ms:.1f} ms",
            f"  Maximum Response Time: {result.max_response_time_ms:.1f} ms",
            f"  Target Response Time: {self.config.target_response_time_ms:.1f} ms",
            ""
        ]
        
        # Resource usage
        if result.server_resource_usage:
            report_lines.extend([
                "RESOURCE USAGE:",
                f"  CPU Usage (Mean/Max/P95): {result.server_resource_usage.get('cpu_usage', {}).get('mean', 0):.1f}% / {result.server_resource_usage.get('cpu_usage', {}).get('max', 0):.1f}% / {result.server_resource_usage.get('cpu_usage', {}).get('p95', 0):.1f}%",
                f"  Memory Usage (Mean/Max/P95): {result.server_resource_usage.get('memory_usage', {}).get('mean', 0):.1f}% / {result.server_resource_usage.get('memory_usage', {}).get('max', 0):.1f}% / {result.server_resource_usage.get('memory_usage', {}).get('p95', 0):.1f}%",
                f"  Process Memory (Mean/Max/P95): {result.server_resource_usage.get('process_memory_mb', {}).get('mean', 0):.1f} MB / {result.server_resource_usage.get('process_memory_mb', {}).get('max', 0):.1f} MB / {result.server_resource_usage.get('process_memory_mb', {}).get('p95', 0):.1f} MB",
                ""
            ])
            
        # Performance violations
        if result.performance_violations:
            report_lines.extend([
                "PERFORMANCE VIOLATIONS:",
            ] + [f"  - {violation}" for violation in result.performance_violations] + [""])
            
        # Final result
        report_lines.extend([
            f"OVERALL RESULT: {'PASSED' if result.success else 'FAILED'}",
            "=" * 80
        ])
        
        return "\n".join(report_lines)

async def run_websocket_load_test_suite():
    """Run comprehensive WebSocket load testing suite"""
    logger.info("WEBSOCKET LOAD TESTING SUITE FOR TERRITORIAL WARFARE SYSTEM")
    logger.info("Performance Engineer Implementation - 120+ Concurrent Player Validation")
    
    # Test configurations - escalating load
    test_configs = [
        WebSocketLoadTestConfig(
            max_concurrent_connections=25,
            test_duration_seconds=120,
            message_rate_per_client=1.0
        ),
        WebSocketLoadTestConfig(
            max_concurrent_connections=50,
            test_duration_seconds=180,
            message_rate_per_client=1.5
        ),
        WebSocketLoadTestConfig(
            max_concurrent_connections=100,
            test_duration_seconds=300,
            message_rate_per_client=2.0
        ),
        WebSocketLoadTestConfig(
            max_concurrent_connections=120,
            test_duration_seconds=300,
            message_rate_per_client=2.0
        ),
        WebSocketLoadTestConfig(
            max_concurrent_connections=150,
            test_duration_seconds=180,
            message_rate_per_client=2.5
        )
    ]
    
    overall_success = True
    test_results = []
    
    for i, config in enumerate(test_configs, 1):
        logger.info(f"\n--- Running Load Test {i}/{len(test_configs)} ---")
        logger.info(f"Connections: {config.max_concurrent_connections}, Duration: {config.test_duration_seconds}s")
        
        tester = WebSocketLoadTester(config)
        
        try:
            result = await tester.run_load_test()
            test_results.append(result)
            
            # Generate and display report
            report = tester.generate_load_test_report(result)
            print(report)
            
            if not result.success:
                overall_success = False
                logger.error(f"Load test {i} FAILED")
            else:
                logger.info(f"Load test {i} PASSED")
                
            # Recovery pause between tests
            if i < len(test_configs):
                logger.info("Pausing for system recovery...")
                await asyncio.sleep(15)
                
        except Exception as e:
            logger.error(f"Load test {i} execution error: {e}")
            overall_success = False
            
    # Generate summary report
    logger.info("\n" + "=" * 80)
    logger.info("WEBSOCKET LOAD TESTING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Overall Result: {'PASSED' if overall_success else 'FAILED'}")
    logger.info(f"Tests Executed: {len(test_results)}")
    logger.info(f"Tests Passed: {sum(1 for r in test_results if r.success)}")
    logger.info(f"Tests Failed: {sum(1 for r in test_results if not r.success)}")
    
    if overall_success:
        logger.info("✅ WebSocket server validated for 120+ concurrent territorial warfare connections")
        logger.info("System ready for production deployment with comprehensive load handling")
    else:
        logger.info("❌ WebSocket server requires optimization before handling target load")
        logger.info("Review individual test reports for specific optimization recommendations")
        
    # Export detailed results
    results_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/TerritorialSystem/websocket_load_test_results.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(result) for result in test_results], f, indent=2, default=str)
        
    logger.info(f"Detailed test results exported to: {results_path}")
    
    return overall_success

async def main():
    """Main execution function"""
    try:
        success = await run_websocket_load_test_suite()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("Load testing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Load testing error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)